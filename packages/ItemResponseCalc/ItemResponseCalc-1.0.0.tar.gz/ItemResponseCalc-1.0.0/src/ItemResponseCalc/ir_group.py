"""Module defining a Bayesian IRT model for the responses of a group of subjects
to a questionnaire with several items.
Each item response is assumed to be determined by the outcome of a
latent random variable with a subject-specific location.

Each uni-dimensional subject trait may determine responses to one or several items.

*** Main Classes:

ResponseGroup:  model for a group of subjects for which
                response data are available for each item for each subject.

PopulationTheta:    distribution of individual traits for a RANDOM INDIVIDUAL
                    in the (sub)population represented by a group of respondents,
                    used as prior for traits of all respondents in this group
PopulationMeanTheta:    distribution of MEAN traits in this (sub)population

** Version history:
* Version 1.0.0: New model structure
2023-07-19, New ResponseGroup implements both eta and theta parameter distributions, jointly sampled.
            New PopulationMeanTheta is conditional on ir_global.ItemResponseGlobal

* Version 0.6.0:
2023-06-24, adapted for new ir_source, all responses already encoded with origin=0.

* Version 0.5.0 and earlier:
2019-07-08, first version
2019-07-23, cannot use SummaryResponseGroup!
2019-08-11, delete class SummaryResponseGroup
2019-08-11, use items.trait_sel.mean as item_trait_weight
2019-08-15, new initialize method, incl. theta randomization
2019-08-17, single ResponseGroup class, generalized for tied or non-tied prec_among
2019-08-20, ResponseGroup.adapt returns self, to allow multiprocessing
2020-06-15, internal changes to use external response_prob for core functions
"""
# *** with class PopulationMeanTheta for the mean of individual theta
#   and sampling method to get predictive RandomIndividual results?

import numpy as np
from scipy.stats import norm

from samppy import hamiltonian_sampler as ham
from samppy.sample_entropy import entropy_nn_approx as entropy
from ItemResponseCalc.gauss import GaussianGivenPrecision
from ItemResponseCalc.student import MultiStudentGivenMean

import multiprocessing
import logging
logger = logging.getLogger(__name__)

# NOTE: logger does NOT inherit parent handlers, when this module is running as child process
if multiprocessing.current_process().name != "MainProcess":
    # 2023-09-01: Tried to send parent logger as argument: does NOT work.
    # restore a formatter like ir_logging, but only for console output
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('{asctime} {name}: {message}',
                                           style='{',
                                           datefmt='%H:%M:%S'))
    logger.addHandler(console)
    logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)  # TEST

RNG = np.random.default_rng()
# = module-global random generator, Numpy 1.17

ham.VECTOR_AXIS = 1  # just in case default has changed...
# ham.logger.setLevel(logging.DEBUG)  # TEST

ETA_DITHER = 0.2    # scale of random dither for initial eta parameters

# ---------------------------------------------- Respondent Group Model:
class ResponseGroup:
    """Model representing individual distributions latent trait distributions
    and group-common response-thresholds, for ONE group of respondents,
    in an OrdinalItemResponseModel.
    Model is learned by adaptation to individual item responses for each respondent.

    An included population model specifies the distribution of traits
    in the (sub)population from which the respondents were recruited.
    This model is used as prior for individual trait distributions.

    An external global population model represents parameters common for all groups.

    Individual traits theta and group-common threshold-mapping parameters eta are sampled jointly.
    An array xi = self._sampler.x includes all samples of both kinds,
    with a predefined indexing scheme:
    Individual trait samples:
        theta = xi[:, self.base.theta_slice].reshape((n_samples, n_subjects, n_traits))
    Group-specific threshold parameters:
        eta = xi[:, self.base.eta_all_slice], with item-specific sub-arrays
        eta_i = eta[:, self.base.eta_slices[i]] for the i-th item.
    Actual thresholds are mapped by
    tau_i = self.base.thr.tau(eta_i)
    """
    def __init__(self, responses, xi, pop_theta, name, base, item_trait_sel, global_pop):
        """
        :param responses: 2D array-like list with response data
            response[i, s] = integer ordinal response index for i-th item by s-th subject
            encoded with origin=0 and missing response == -1,
        :param xi: 2D array with initial joint (eta, theta) samples, stored as
            xi = concatenated (eta, theta.reshape(...))
            where
            eta[n, :] = n-th sample of all threshold-defining parameters for this group
            theta[n, s, d] = n-th sample of d-th trait for s-th subject
        :param pop_theta: PopulationTheta instance representing current distribution of theta
            in the population represented by this group.
            Used as prior for individual theta distributions of respondents.
        :param name: string with arbitrary label for this object, for display purpose
        :param base: ref to common ItemResponseBase object defining indexing scheme for parameter subsets,
            same for all groups
        :param item_trait_sel: ref to common list of ItemSelector objects
        :param global_pop: ref to common ItemResponseGlobal object
            defining global distributions for all group-specific parameters.

        NOTE: Internal property
        responses = 2D array of individual response indices, with
            response[i, s] = integer index of response to i-th item,
            encoded with origin==0, and missing response encoded as -1.
        The corresponding external property
        subject_responses = responses + 1,
        with origin == 1 and missing response == 0,
        is needed only for some conventional external presentations.
        """
        self.responses = np.array(responses)
        self.n_traits = self.responses.shape[0]
        # NOTE: initially, each item <-> one trait; n_traits may be reduced later
        self.sampler = ham.HamiltonianSampler(fun=self.neg_logprob,
                                              jac=self.d_neg_logprob,
                                              x=xi,  # theta.reshape(n_samples, -1),
                                              epsilon=0.3,
                                              n_leapfrog_steps=10)
        # NOTE: xi = (eta, theta) is stored only as sampler.x
        # args for neg_logprob and d_neg_logprob are defined later, in each call to adapt
        self.pop_theta = pop_theta
        self.name = name
        self.ll = None  # log likelihood to be saved here by adapt step
        self.base = base
        self.item_trait_sel = item_trait_sel
        self.global_pop = global_pop

    def __repr__(self):
        return (self.__class__.__name__ + f'(name= {repr(self.name)},'
                + f'\n\t responses= array with responses to {len(self.responses)} items'
                + f' by {self.n_subjects} respondents,'
                + f'\n\t theta= array with shape= {self.theta.shape},'
                + '\n\t pop_theta= ' + self.pop_theta.__repr__()
                + ')')

    # ------------- initialization methods:
    @classmethod
    def initialize_by_item(cls, responses, trait_scale, base, global_pop, item_trait_sel, name, n_samples=50):
        """Initialize trait values by sampling, one trait for each item
        :param responses: iterable yielding subject responses as a list with
            responses[s][i] = integer index of response to i-th item,
            encoded with origin==0 for the first response alternative,
            and missing response encoded as -1.
        :param trait_scale: scalar initially assumed scale of trait values
        :param base: ItemResponseBase instance created by caller
        :param global_pop: ir_global.ItemResponseGlobal instance
            containing global priors for all group-specific parameters
        :param item_trait_sel: ref to common list of ItemSelector objects
        :param name: string identifying this group
        :param n_samples: number of samples of the intra-subject distribution of trait values
            and intra-group threshold-determining eta parameters
        :return: single cls instance
        """
        # collect all response data in one array
        s_responses = np.array([s_r for s_r in responses]).T  # *** copy needed?
        # s_responses[i, s] = response-level index for i-th item by s-th subject
        # with origin == 0, missing response == -1
        # n_items = len(s_responses)
        eta = np.tile(global_pop.eta.mu.loc, (n_samples, 1))
        eta += ETA_DITHER * RNG.standard_normal(size=eta.shape)
        tau = base.tau(eta)
        # = list of crude initial threshold arrays, INCL extremes in range [-inf, +inf]
        th = np.array([sample_latent(r_i, tau_i, trait_scale=trait_scale)
                       for (r_i, tau_i) in zip(s_responses, tau)])
        # th[i, s, m] = m-th sample for i-th item and s-th subject
        # th = (th + 9. * np.mean(th, axis=0)) / 10.  # *** blur traits across items  ***
        # *** 2023-08-16: did not help to automatically reduce n_traits ***
        th = th.transpose((2, 1, 0))
        # th[m, s, i] = m-th sample of i-th item for s-th subject
        xi = np.concatenate((eta, th.reshape((n_samples, -1))), axis=-1)
        pop_theta = PopulationTheta.initialize(th, global_pop.theta)
        logger.info(f'Initializing {repr(name)}'
                    + f' with {s_responses.shape[-1]} respondent records')
        logger.debug('Initial item pop_theta.loc= ' + np.array2string(pop_theta.mu.loc, precision=3))
        return cls(responses=s_responses,
                   xi=xi,
                   pop_theta=pop_theta,
                   item_trait_sel=item_trait_sel,
                   global_pop=global_pop,
                   name=name,
                   base=base)

    def cov_theta(self):
        """Covariance matrix across all samples, all subjects,
        used only to calculate initial transformation of trait coordinates,
        to be used by method transform_traits later.
        :return: c = 2D symmetric inter-individual covariance matrix
        """
        logger.debug('Initial cov without mean subtraction')
        x = self.theta.reshape((-1, self.theta.shape[-1]))
        c = np.cov(x, rowvar=False)
        return c

    def transform_traits(self, proj):
        """Transform initial item-traits to (sub-)space defined by external PCA
        :param proj: 2D projection matrix with orthonormal COLUMN vectors
            proj[:, d] = unit vector for d-th trait
        :return: None

        Result: self.theta and self.pop_theta transformed to proj coordinate system
        """
        th = np.dot(self.theta, proj)
        self.n_traits = th.shape[-1]
        self.xi = np.concatenate((self.eta, th.reshape((self.n_samples, -1))),
                                 axis=-1)
        self.pop_theta = PopulationTheta.initialize(th, self.global_pop.theta)
        logger.debug(f'Transformed group {repr(self.name)} self.pop_theta.mu.loc= '
                     + np.array2string(self.pop_theta.mu.loc, precision=3, suppress_small=True))

    # ----------------- Methods describing current model:
    @property
    def subject_responses(self):  # ***** needed ?
        """Subject responses as obtained from input files
        using the external encoding {1,..., L_i},
        with missing response == 0
        :return: r = 2D array with responses,
            r[s, i] = response by s-th subject to i-th item
        """
        return self.responses + 1

    @property
    def n_samples(self):
        return self.sampler.x.shape[0]

    @property
    def n_subjects(self):
        return self.responses.shape[-1]

    @property
    def xi(self):
        return self.sampler.x

    @xi.setter
    def xi(self, x):
        self.sampler.x = x

    @property
    def theta(self):
        """Sample representation of current distribution of trait values
        for all subjects in this group
        :return: theta = 3D array of samples
            theta[n, s, d] = n-th sample of d-th trait for s-th subject
        """
        return self.base.theta(self.xi, self.n_subjects)

    @property
    def eta(self):
        """Sample representation of current distribution of eta parameters
        :return: eta = 2D array of samples
            eta[n, k] = n-th sample of k-th eta value, indexed across all items
        """
        return self.base.eta_all(self.xi)

    def sum_theta_theta(self):
        """Sum mean outer product matrix of current theta distribution for each subject,
        averaged across samples, summed across respondents.
        :return: 2D array
            = sum_s E{ theta_s(as column) *  theta_s(as row) },
            with E{} calculated as mean across samples
        """
        th = self.theta
        return np.einsum('nsi, nsj -> ij',
                         th, th) / th.shape[0]

    def entropy_xi(self):
        """Entropy of current (eta, theta) distribution,
        estimated from samples by nearest-neighbor method
        :return: h_sum = scalar entropy
        """
        # h = entropy(self.xi)
        # h = single estimate using all subjects in one operation.
        # Results indicate this gets severely over-estimated ****
        # In previous versions, the distributions were independent among subjects,
        # and Singh et al. (2016) showed convergence is slower with increasing dimension,
        # so an average across all subjects, at low dimension for each subject,
        # might be closer to the true value.

        eta = self.eta
        th = self.theta
        h_eta = entropy(eta)
        h_theta = sum(entropy(th[:, s, :]) for s in range(th.shape[1]))
        # h_theta_test = sum(self.entropy_theta_individual())
        h_sum = h_eta + h_theta
        # as if eta and theta were independent
        # This is theoretically also an over-estimation, but much better than h = entropy(self.xi)
        # logger.debug(f'{self.name}: h_xi = {h}; h_eta= {h_eta}; h_theta= {h_theta}; h_sum= {h_sum}')

        # # *** Try dependent model: p(eta, theta) = p(eta) prod_s p(theta_s | eta):
        # h_eta_theta = sum(entropy(np.concatenate((eta, th[:, s, :]), axis=-1))
        #                   for s in range(th.shape[1]))
        # # = h(eta, theta) with same eta re-used n_subjects times
        # h_sum_xi = h_eta_theta - (self.n_subjects - 1) * h_eta
        # # = another estimate of h(xi) for comparison, *** NO GOOD: large random fluctuations!
        return h_sum

    def entropy_theta_individual(self):
        """Entropy for theta distribution given each participant's response vector
        :return: h_theta_ind = generator yielding
            scalar h(theta_s | r_s) for s-th participant
        """
        th = self.theta.transpose((1, 0, 2))
        # th[s, m, :] = m-th sample of trait vector for s-th subject
        return (entropy(th_s) for th_s in th)

    def entropy_theta_group(self):
        """Entropy for theta distribution among all participants in a group
        :return: scalar h(theta) estimated by ONE sample from each participant
        """
        th = self.theta[0]
        # th[s, :] = ONE random sample of trait vector for s-th subject
        return entropy(th)

    def item_trait_logprob(self):
        """Calculate log-responsibility used to update item-trait selectors
        based on current (eta, theta) distribution defined by self.xi
        :return: lr = 2D array with elements
            lr[i, d] = mean_n{ sum_s ln P(self.responses[i, s] | self.xi[n,:]) } for d-th trait
        """
        return np.mean(self.base.item_response_logprob(self.responses, self.eta, self.theta),
                       axis=1)

    # ----------------- learning methods:
    # def init_adapt(self):  # *** use scipy.minimize for a starting point ? ***

    def adapt(self):
        """One learning step for distribution of group theta values,
        and pop_theta property,
        using response data and current distribution of item scale parameters.
        :return: self, with updated contents, to allow multiprocessing

        Result:
        self.xi = updated set of samples of (eta, theta) for group respondents
        self.pop_theta.mu.loc updated to new self.xi and self.global_pop
        self.ll = E_self{ ln P(self.responses | self) }
                + E{ ln prior_pdf(eta | self.global_pop.eta) }
                + E{ ln prior_pdf(theta | self.pop_theta.mu, global_theta.prec)}
                + entropy(eta, theta) [using samples]
                - KLdiv(self.pop_theta.mu || prior.pop_theta_mu) [given global_theta]
        """
        _id = repr(self.name)  # used for logger output
        logger.debug(self.__class__.__name__ + f'[{_id}].adapt(...)')
        # ---------------------------------- adapt self.xi by Hamilton sampling
        weight = np.asarray([sel.mean for sel in self.item_trait_sel])
        self.sampler.args = (weight,)
        max_steps=20
        # adapt_check_grad(self, weight)  # **** OK. only for test **************
        try:
            self.sampler.safe_sample(min_steps=5, max_steps=max_steps)
            if self.sampler.n_steps >= max_steps:
                logger.warning(f'{_id}: Done {self.sampler.n_steps} = MAX allowed sampling steps')
            else:
                logger.debug(f'{_id}: Done {self.sampler.n_steps} sampling steps')
        except ham.AcceptanceError:  # raised by sampler, even after reducing epsilon
            # logger.debug(f'* AcceptanceError {self}.adapt()')
            # self.sampler.epsilon *= (0.7 + 0.2 * uniform.rvs())  # ************** SKIP
            logger.warning((f'{_id}: AcceptanceError: accept_rate= {self.sampler.accept_rate:.2f} ' +
                            f'of {self.sampler.n_trajectories}; ' +
                            f'epsilon reduced to {self.sampler.epsilon:.5f}'))
            # ****** keep going anyway ********
        else:
            logger.debug(f'{_id}: Sampler accept_rate = {self.sampler.accept_rate:.1%}')
            logger.debug(f'{_id}: Sampler epsilon = {self.sampler.epsilon}')
        # --------------------------------- DONE distribution of theta
        LL = - np.mean(self.sampler.U)
        LL += self.pop_theta.log_normalization(self.global_pop.theta) * self.n_subjects
        # because this log_normalization is not included in self.neg_logprob(...)
        LL += self.pop_theta.mu.adapt(np.mean(self.theta, axis=0), self.global_pop.theta)
        h = self.entropy_xi()
        logger.debug(f'{_id}: LL = {LL:.1f} + entropy={h:.1f}')
        self.ll = LL + h
        logger.debug(self.__class__.__name__ + f'[{_id}].adapt(...) finished')
        return self

    def neg_logprob(self, xi, weight):
        """Negative log-likelihood for any sample subject trait vector
        :param xi: 2D array of sample (eta, theta) values as stored in self.sampler.x
        :param weight: list of 1D arrays of item-trait mapping weights = doc <z_id>
            weight[i][d] = current prob that i-th item response determined by d-th trait
        :return: nlp = 1D vector of negative log-likelihood values
            nlp.shape == (xi.shape[0],) == (self.n_samples,)

        Method: doc eq:LogProbXi, section Respondent- and item-specific parameters
        """
        eta = self.base.eta_all(xi)
        th = self.base.theta(xi, self.n_subjects)
        return (- self.base.response_logprob(self.responses, eta, th, weight)
                - self.global_pop.eta.mean_logpdf(eta)  # INCL. log normalization
                - np.sum(self.pop_theta.mean_loglikelihood(th, self.global_pop.theta),
                         axis=-1)  # EXCL. log normalization
                )

    def d_neg_logprob(self, xi, weight):
        """Gradient of self.neg_logprob for any sample subject trait vector
        :param xi: 2D array of candidate samples (eta, theta) as stored in self.sampler.x
        :param weight: list of 1D arrays of item-trait mapping weights = doc <z_id>
            weight[i][d] = current prob that i-th item response determined by d-th trait
        :return: dnlp = 2D array of gradient values
            dnlp[n, k] = d self.neg_logprob(xi, ...)[n] / d xi[n, k]
            dnlp.shape == xi.shape
        """
        eta = self.base.eta_all(xi)
        th = self.base.theta(xi, self.n_subjects)
        dprior_d_eta = self.global_pop.eta.d_mean_logpdf(eta)
        dprior_d_theta = self.pop_theta.d_mean_loglikelihood(th, self.global_pop.theta)
        # n_samples = dprior_d_theta.shape[0]
        return (- self.base.d_response_logprob(self.responses, eta, th, weight)
                - np.concatenate((dprior_d_eta, dprior_d_theta.reshape(self.n_samples, -1)),
                                 axis=-1)
                )

    # -------------------------------------- Predictive Models for result displays:
    def prune(self, keep):
        """Prune away un-necessary trait dimensions
        :param keep: 1D boolean array indicating traits to keep
        :return: None
        Result: self.theta and self.pop_theta pruned
        """
        th = self.theta[..., keep]
        self.n_traits = np.sum(keep)
        self.xi = np.concatenate((self.eta, th.reshape(self.n_samples, -1)),
                                 axis=-1)
        self.pop_theta.mu.prune(keep)

    def predictive_mean(self):
        """Predictive distribution of MEAN IRT traits
        in the subpopulation for which the subject data in self are representative.
        :return: a student.MultiStudentGivenMean instance
        """
        return self.pop_theta.mu.predictive(self.global_pop.theta)

    def predictive_individual(self):
        """Predictive distribution of IRT traits for a RANDOM INDIVIDUAL
        in the subpopulation for which the respondent data in self are representative.
        :return: a student.MultiStudentGivenMean instance
        """
        return self.pop_theta.predictive(self.global_pop.theta)


# --------------------------------------------------------- help classes:
class PopulationTheta:  # (GaussianRVwithCorrelation):
    """Distribution of individual traits theta in the (sub)population
    from which ONE group of respondents has been recruited.
    Specified by a PopulationMeanTheta instance,
    AND an ir_global.GlobalTheta instance, supplied as argument whenever needed.

    This differs from a standard Bayesian Gaussian random vector,
    because its mean parameter mu is a linear function of the global mean,
    which is another Gaussian variable.
    """
    log_2_pi = np.log(2 * np.pi)  # class constant for mean_logpdf calc

    def __init__(self, mu):
        """
        :param mu: a PopulationMeanTheta instance
        """
        self.mu = mu

    @classmethod
    def initialize(cls, th, global_theta):
        """
        :param th: 3D array of theta samples
            th[n, s, :] = n-th sample of trait vector for s-th respondent
        :param global_theta: a GlobalTheta instance
        :return: a cls instance
        """
        return cls(PopulationMeanTheta(loc=np.mean(th, axis=(0, 1)),
                                       learned_weight=global_theta.prec_factor_group.mean,
                                       global_weight=1.)
                   )

    def mean_loglikelihood(self, th, global_theta):
        """mean log pdf(th | self.mu, global_theta), averaged across self.mu and global_theta,
        EXCL. log normalization constant that remains constant during samplng.
        :param th: array of trait vectors assumed drawn from self
            th[..., :] = ...-th trait vector sample for one or many respondents
        :param global_theta: an ir_global.GlobalTheta instance
        :return: lp = scalar or array
            lp[...] = E{log pdf(th[...] | self, global_theta)} - log(normalization)
            lp.shape == th.shape[:-1]

        Method: doc eq:LogProbXi, section Respondent- and item-specific parameters.
            th is assumed Gaussian, given self.mu and global_theta.prec.
            Result includes ONLY the exponent part, NOT the log det(prec) contribution,
            to save un-necessary computation during sampling.
        """
        th_dev = th - self.mu.conditional_mean(global_theta.mu.loc)
        d2 = np.einsum('...i, ij, ...j',
                       th_dev, global_theta.prec.mean, th_dev)
        # d2[...] = ...-th sample of mean square Mahanalobis distance
        beta_g = self.mu.learned_weight
        gamma = global_theta.mu.learned_weight  # might be inf if global_theta.mu is fixed.
        mean_b = global_theta.prec_factor_group.mean  # <B> in doc
        m2 = (1. + mean_b**2 / beta_g / gamma) * th.shape[-1] / beta_g
        # = contributions from variations in global_theta
        # m2 also constant during sampling, include later *** ?
        return - (d2 + m2) / 2

    def d_mean_loglikelihood(self, th, global_theta):
        """Gradient of mean_loglikelihood(self, th, global_theta) w.t.t. th.
        :param th: 1D or 2D or 3D array of trait vectors assumed drawn from self
            th[..., :] = ...-th sample of trait vector for one or many respondents
        :param global_theta: an ir_global.GlobalTheta instance
        :return: dlp = array
            dlp[..., d] = d logpdf(th, global_theta)[...] / d th[..., d]
            dlp.shape == th.shape
        """
        # th_dev = th - self.mu.conditional_mean(global_theta.mu.loc)
        return - np.dot(th - self.mu.conditional_mean(global_theta.mu.loc),
                        global_theta.prec.mean)

    def log_normalization(self, global_theta):  # **** -> GaussianRVwithCorrelation ? ****
        """log normalization constant, such that
        E{log pdf(th | self, global_theta) }
            = log_normalization(th,...) + log_likelihood(th,...)
            for ONE sample vector th.
        :param global_theta: an ir_global.GlobalTheta instance
        :return: scalar
        """
        return (global_theta.prec.mean_log_det - self.log_2_pi) / 2

    def predictive(self, global_theta):
        """Create a predictive model for the trait distribution
        of a RANDOM INDIVIDUAL in this (sub)population,
        by integrating out the precision.
        The result is conditional on the global_theta.mu,
        as defined by self.mu.conditional_mean(global_mu)
        :param global_theta: an ir_global.GlobalTheta instance
        :return: a MultiStudentGivenMean instance
            that can generate random samples from the predictive distribution
        """
        beta_g = self.mu.learned_weight
        nu = global_theta.prec.df
        df = nu + 1 - self.mu.size
        sigma = global_theta.prec.inv_scale * (beta_g + 1) / beta_g / df
        return MultiStudentGivenMean(mean_factor=self.mu.global_weight,
                                     df=df,
                                     loc=self.mu.loc,
                                     sigma=sigma)

class PopulationMeanTheta(GaussianGivenPrecision):
    """Gaussian conditional distribution of the mean trait vector mu_g
    in the population represented by the respondents in this ResponseGroup instance.
    Defined by super-class properties
        loc = location, part learned from sampled trait vectors theta of ONE group of subjects
        learned_weight = effective number of learning
        AND a scale factor global_weight, for the effect of the global theta mean
    """
    def __init__(self, loc, learned_weight, global_weight=0.):
        super().__init__(loc=loc, learned_weight=learned_weight)
        self.global_weight = global_weight

    @property
    def n_traits(self):  # **** needed ?
        return len(self.loc)

    def conditional_mean(self, global_mu):
        """Conditional mean, given any value of the global mean.
        :param global_mu: any sample value of ir_global.ThetaMean distribution
        :return: 1D array

        Method:
        E{mu_g | global_mu} = (<B> / beta) global_mu + average theta_gs
        doc eq:MuGroupGivenGlobal
        """
        return self.global_weight * global_mu + self.loc

    def mean_sq_dev(self, global_mu, global_prec):  # *** use global_theta as arg ? ***
        """Mean square Mahanalobis distance of self re global mean.
        Needed for VI update of global prec_factor_groups, called B in doc.
        :param global_mu: an ir_global.ThetaMean object
        :param global_prec: global Wishart-distributed precision matrix, called Lambda in doc.
        :return: scalar z2 = E{(mu_g - global_mu) @ Lambda @ (mu_g - global_mu)}
            where
            mu_g = group-specific mean theta represented by self,
            global_mu = global mean theta,
            Lambda = global inter-individual precision matrix

        Method: doc sec:PosteriorB
        """
        d = len(self.loc)
        beta = self.learned_weight
        gamma = global_mu.learned_weight
        # might be inf in case global_mean is fixed at zero
        global_m = global_mu.mean  # called \bar m in doc
        # might be zero in case global_mean is fixed at zero
        d_mean = self.conditional_mean(global_m) - global_m
        return d / beta + (1. + self.global_weight**2) * d / gamma + d_mean @ global_prec.mean @ d_mean

    def adapt(self, mean_theta, global_theta):
        """Adapt self to observed samples and global_pop
        :param mean_theta: 2D array of mean observed samples of subject traits
            mean_theta[s, d] = current mean of d-th trait for s-th subject in this group
        :param global_theta: ir_global.GlobalTheta object with global parameters
        :return: - KLdiv(self || prior)

        Method: doc Sec Population-specific and global trait parameters
            eq:MuGroupGivenGlobal eq:PosteriorBetaGroup eq:PosteriorMuGroup
        """
        mean_b = global_theta.prec_factor_group.mean  # called <B> in doc
        self.learned_weight = len(mean_theta) + mean_b
        self.global_weight = mean_b / self.learned_weight
        self.loc = np.sum(mean_theta, axis=0) / self.learned_weight
        return - self.relative_entropy_re_prior(global_theta)

    def relative_entropy_re_prior(self, global_theta):
        """Mean KLdiv( self.mu_g || prior.mu_g), where
        self.mu_g is Gaussian with
            mean = m(mu) = self.conditional_mean(global_theta.mu),
            prec = beta_g * Lambda = self.learned_weight * global_theta.prec
        prior.mu_g is Gaussian with
            mean = mu = global_theta.mu,
            prec = B * Lambda = global_theta.prec_factor_group * global_theta.prec
        :param global_theta: ir_global.GlobalTheta object with all global parameters
        :return: scalar KL_div = E{ ln pdf(mu_g | self) / pdf(mu_g | prior ) }_{self}

        Method:
        log pdf(mu_g | self) = [ln det(beta_g Lambda) - (mu_g - m(mu)).T beta_g Lambda (mu_g - m(mu)) ] / 2
            = Gaussian with
                mean = m(mu)
                cov = (beta_g Lambda)^{-1}
        log pdf(mu_g | prior)  = [ln det(B Lambda) - (mu_g - mu).T B Lambda (mu_g - mu) ] / 2
            = [ln det(B Lambda) - (mu_g - m(mu) + m(mu) - mu).T B Lambda (mu_g - m(mu) + m(mu) - mu) ] / 2
        m(mu) - mu is Gaussian with
            mean = self.loc + b_ratio * mu.mean - mu.mean
            cov = (1-b_ratio)^2 (gamma Lambda)^{-1}
        """
        d = len(self.loc)  # = self.size
        b_ratio = self.global_weight  # = <B> / beta_g
        b_ratio_m1 = b_ratio - 1.
        mu_mean = global_theta.mu.mean  # might be zero
        mu_dev = self.loc + b_ratio_m1 * mu_mean
        mean_b = global_theta.prec_factor_group.mean  # = <B>
        gamma = global_theta.mu.learned_weight  # might be inf
        return (- np.log(b_ratio)
                + b_ratio_m1
                + b_ratio_m1**2 * mean_b / gamma
                + mu_dev @ global_theta.prec.mean @ mu_dev
                ) * d / 2

    def prune(self, keep):
        """Prune away un-necessary trait dimensions
        :param keep: 1D boolean array indicating traits to keep
        :return: None
        """
        self.loc = self.loc[keep]

    def predictive(self, global_theta):
        """Create a predictive model for the MEAN trait distribution
        in this (sub)population,
        by integrating out the precision.
        The result is conditional on the global_theta.mu,
        as defined by self.conditional_mean(global_mu)
        :param global_theta: an ir_global.GlobalTheta instance
        :return: a MultiStudentGivenMean instance
            that can generate random samples from the predictive distribution
        """
        beta_g = self.learned_weight
        nu = global_theta.prec.df
        df = nu + 1 - self.size
        sigma = global_theta.prec.inv_scale / beta_g / df
        return MultiStudentGivenMean(mean_factor=self.global_weight,
                                     df=df,
                                     loc=self.loc,
                                     sigma=sigma)


# -------------------------------------------------------- module help functions
def sample_latent(r, tau, trait_scale):
    """Sample individual latent decision variable that might have caused
    observed individual response counts,
    for ONE given item
    :param r: 1D array of response, one from each respondent, for this given item.
        r[s] = response index in range(L_i) for s-th respondent
    :param tau: 2D array of response thresholds, -inf, ..., +inf,
        such that l-th response occurs IFF tau[l] < Y <= tau[l + 1]
        tau.shape[0] == n_samples to generate
    :param trait_scale: scale of inter-individual latent variable
        ***** prior mean of latent var is assumed = 0. *****
    :return: Y = 2D array of samples
        Y[s, n] = n-th sample for s-th respondent,
        random within response interval (tau[r_i[s]], tau[1 + r_i[s]])
    """
    def s_sample(r_s):
        """Sample in transformed (0, 1) range for ONE subject
        :param r_s: scalar integer response by this subject
        :return: 1D array th_s with uniform samples in allowed range
            len(th_s) == tau.shape[0]
        """
        if r_s < 0:
            return RNG.uniform(low=cdf_tau[:, 0], high=cdf_tau[:, -1])
        else:
            return RNG.uniform(low=cdf_tau[:, r_s], high=cdf_tau[:, r_s + 1])

    # ----------------------------------------------------------------------
    cdf_tau = norm.cdf(tau, scale=trait_scale)
    cdf_tau[:, 0] = np.finfo(float).tiny
    # tiny lowest limit, because RANDOM.uniform samples in [0, 1),
    # but we allow only samples in (0., 1)
    cdf_theta = [s_sample(r_s) for r_s in r]
    # cdf_theta[s, n] = n-th sample for s-th respondent
    return norm.ppf(np.array(cdf_theta), scale=trait_scale)


# -------------------------------------------------------- TEST grad:

def adapt_check_grad(gm, weight):  # ******** check eta, theta separately ********
    """Check ItemResponseGroup.d_neg_logprob
    :param gm: ResponseGroup instance
    :param weight: 2D array with item-trait weights
    :return: None
    """
    from scipy.optimize import check_grad, approx_fprime  # only for test

    def fun(x):
        # x = array like gm.xi[0]
        return gm.neg_logprob(gm.xi + x, weight)[0]

    def jac(x):
        # x = array like gm.xi[0]
        return gm.d_neg_logprob(gm.xi + x, weight)[0]

    test_x = np.zeros_like(gm.xi[0])  # like one row of xi
    print(f'*** adapt_check_grad: testing neg_logprob with test_x.shape = {test_x.shape}')
    print('fun =', fun(test_x))
    exact_d = jac(test_x)
    approx_d = approx_fprime(test_x,
                             fun,
                             epsilon=1e-6)
    print('exact jac = ', exact_d)
    err_diff = approx_d - exact_d
    print('approx_d - exact_d = ', err_diff)
    err = check_grad(fun, jac, test_x)
    print('check_grad err = ', err)


# -------------------------------------------------------- TEST:
# if __name__ == '__main__':
    # Testing some module functions OLD version. Replaced by adapt_check_grad
