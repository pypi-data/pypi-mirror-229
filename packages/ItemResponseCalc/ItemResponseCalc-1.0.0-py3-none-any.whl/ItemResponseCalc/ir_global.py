"""This module defines global model parameters,
common for all groups / populations in an ir_model.OrdinalItemResponseModel,
used as hierarchical priors for all group-specific model parameters.

*** Main Classes:
ItemResponseGlobal: container for all threshold and trait parameter distributions,
    for a global population, possibly including several separate (sub)populations,
    each represented by a group of respondents recruited from that (sub)population.
    The global parameter distribution is prior for all (sub)populations.

GlobalTheta:    container for trait-related parameters
GlobalEta:      container for threshold-related parameters

ThetaMean:  conditional Gaussian distribution of global mean theta,
            given average inter-individual precision matrix within groups.
ThetaMeanFixed:  fixed global mean theta = 0.

EtaMean:    conditional Gaussian distribution of global mean eta, given precision array

PrecFactorGroup:    Precision factor for group means re. global mean, called B in doc.
PrecFactorGroup:    Precision factor for global mean, called C in doc.

ThetaPrecision:     Wishart distribution of inter-individual precision matrix,
                    for individual trait vectors.

EtaPrecisionAmongGroups:    gamma distribution of diagonal precision
                            for eta variations between groups.


*** Version History:
* Version 1.0.0: new module for this version
"""
import numpy as np
from scipy.stats import norm
import logging

from .gauss import GaussianRV, GaussianGivenPrecision
from .student import MultiStudentRV
from .gamma import GammaRV
from .wishart import WishartRV

# ------------------------------- Prior hyperparameters
PROB_PSEUDO_COUNT = 0.5
# = Jeffreys prior for Dirichlet-distributed prob-mass estimated from observed counts

THETA_PSEUDO_COUNT = 0.001
# non-informative for ThetaMean prec_factor_group (B in doc) and prec_factor_global (C in doc)

THETA_PRECISION_DELTA = 0.001
# Prior df of within-group Wishart distribution is set at df = D - 1 + THETA_PRECISION_DELTA,
# where df = approximate weight of prior precision re. one individual respondent.
# Wishart distribution is proper only for df > D - 1,
THETA_SCALE_WITHIN = 1.
# = approximate scale of inter-individual theta variations within groups

ETA_PSEUDO_COUNT = 0.01  # called kappa' in doc. slightly informative for EtaMean distribution
# ETA_A_AMONG  # called f' in doc; = pseudo_groups / 2, specified by user, via ir_model.initialize()
ETA_B_AMONG = 0.01  # called g' in doc
# = prior parameters for global eta distribution
# The prior var[eta_gk] between groups is g' / (f' - 1) = g' with f' = 2.
# The prior variance of global mean eta_k between categories is g' / (f' - 1) kappa'
# ----------------------------------------------------------

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)  # test


# ----------------------------------------------------------
class ItemResponseGlobal:
    """Container for global (theta, eta) distributions,
    used as priors for all group-specific parameters.
    All model parameters are implemented as random variables.
    """
    def __init__(self, theta, eta):
        """
        :param theta: GlobalTheta instance for all trait-related model parameters
        :param eta: GlobalEta instance with Gaussian distribution of group-specific threshold parameters
        """
        self.theta = theta
        self.eta = eta

    @classmethod
    def initialize(cls, n_eta, n_traits, restrict_traits, pseudo_groups):
        """Create weakly informative distribution of global parameters,
        to be used as constant top prior for the data-trained global parameter distributions,
        which are in turn used as prior distribution for all group-specific model parameters.
        :param n_eta: scalar integer total number of threshold-defining parameters for all items
        :param n_traits: D = scalar integer number of trait parameters
        :param restrict_traits: boolean switch
        :param pseudo_groups: scalar number of prior "groups"
            with all threshold-parameters forced EQUAL TO global mean.
            Larger value -> smaller between-population variations of thresholds.
        :return: a cls instance
        """
        theta_prec = ThetaPrecision.initialize(n_traits)
        if restrict_traits:
            theta_mean = ThetaMeanFixed.initialize(n_traits)
            prec_factor_global = None  # not used, infinite precision of theta_mean
        else:
            theta_mean = ThetaMean.initialize(n_traits, learned_weight=THETA_PSEUDO_COUNT)
            prec_factor_global = PrecFactorGlobal(a=THETA_PSEUDO_COUNT, b=THETA_PSEUDO_COUNT)
        prec_factor_group = PrecFactorGroup(a=THETA_PSEUDO_COUNT, b=THETA_PSEUDO_COUNT)
        theta_param = GlobalTheta(theta_mean,
                                  theta_prec,
                                  prec_factor_global,
                                  prec_factor_group)
        eta_prec = EtaPrecisionAmongGroups.initialize(n_eta, pseudo_groups)
        eta_param = GlobalEta(EtaMean.initialize(n_eta), eta_prec)
        logger.debug(f'Initializing Global Prior with'
                     +f'\n\tPROB_PSEUDO_COUNT={PROB_PSEUDO_COUNT}'
                     +f'\n\tTHETA_PSEUDO_COUNT={THETA_PSEUDO_COUNT}'
                     +f'\n\tTHETA_SCALE_WITHIN={THETA_SCALE_WITHIN}'
                     +f'\n\tETA_PSEUDO_COUNT={ETA_PSEUDO_COUNT}'
                     +f"\n\tpseudo_groups={pseudo_groups}; f'={pseudo_groups / 2}"
                     +f'\n\tETA_B_AMONG={ETA_B_AMONG}'
                     )
        return cls(theta_param, eta_param)

    def set_start(self, item_response_count, base, trait_scale):
        """Initialize self based on total item response counts,
        defining typical response thresholds,
        to be used for initialization of individual traits in all groups.
        Needed BEFORE the start of iterative VI learning procedure.
        :param item_response_count: list of total response counts, sum across all groups
        :param base: ir_base.ItemResponseBase object, already initialized
        :param trait_scale: scalar initial scale of individual trait locations
        :return: None
        Result: updated self.mu.loc, other params left at their prior values
        """
        self.eta.mu.set_initial_loc(item_response_count, base, trait_scale)

    def adapt(self, groups, prior):
        """Adapt global distributions to current group / (sub)populations
        :param groups: list of ir_group.RespondentGroup instances
        :param prior: object of same class as self, with prior distributions
        :return: LL = scalar = - KLdiv(self || prior)
        """
        return self.eta.adapt(groups, prior.eta) + self.theta.adapt(groups, prior.theta)

    def prune(self, keep):
        """Prune away un-necessary trait dimensions
        :param keep: 1D boolean array indicating traits to keep
        :return: None
        """
        self.theta.prune(keep)
        # self.eta.prune(keep)  # nothing theta-related there

    # def standardize(self, s):
    #     """Standardize by scaling for unity trait variance, as estimated externally
    #     :param s: 1D array with down-scale factors, one for each trait
    #     :return: None
    #     """
    #     self.theta.standardize(s)
    #     self.eta.standardize(s)


class GlobalTheta:
    """Global distributions of all trait-related parameters
    """
    def __init__(self, mu, prec, prec_factor_global, prec_factor_group):
        """
        :param mu: ThetaMean instance; Gaussian global mean of group-specific mean theta, if freely variable
            OR ThetaMeanFixed instance with loc = 0., in case restricted_trait
        :param prec: ThetaPrecision instance,
            = Wishart-distributed inter-individual trait precision within groups
        :param prec_factor_global: scalar gamma-distributed ratio factor, called C in doc report, such that
            precision of mu = prec_factor_global * prec, IFF theta_mean is free random variable
        :param prec_factor_group: scalar gamma-distributed ratio factor, called B in doc report, such that
            precision of group-specific mean = prec_factor_group * prec
        """
        self.mu = mu
        self.prec = prec
        self.prec_factor_global = prec_factor_global
        self.prec_factor_group = prec_factor_group

    def adapt(self, groups, prior):
        """
        :param groups: list of ir_group.RespondentGroup instances
        :param prior: object of same class as self, with prior distribution
        :return: LL = scalar = - KLdiv(self || prior)
        """
        ll_prec = self.prec.adapt(groups, self, prior.prec)
        logger.debug(f'Global Theta.prec.mean_inv = {np.diag(self.prec.mean_inv)}')
        g_pop_mu = [g.pop_theta.mu for g in groups]
        if self.prec_factor_global is None:  # and self.mu is a ThetaMeanFixed object
            ll_mu = 0.
            ll_factor_c = 0.
        else:
            ll_mu = self.mu.adapt(g_pop_mu, self, prior.mu)
            logger.debug(f'Global Theta.mu.mean = {self.mu.mean}')
            ll_factor_c = self.prec_factor_global.adapt(self, prior.prec_factor_global)
            logger.debug(f'Global <C> = {self.prec_factor_global.mean}')
        ll_factor_b = self.prec_factor_group.adapt(g_pop_mu, self, prior.prec_factor_group)
        logger.debug(f'Global <B> = {self.prec_factor_group.mean}')
        return ll_prec + ll_mu + ll_factor_b + ll_factor_c

    def prune(self, keep):
        """Prune away un-necessary trait dimensions
        :param keep: 1D boolean array indicating traits to keep
        :return: None
        """
        self.mu.prune(keep)
        self.prec.prune(keep)

    def predictive_mean(self):
        return self.mu.predictive(self.prec)

    def entropy(self):  # **** check! over-estimation ?
        """Mean entropy of the global distribution of trait vector theta
        for a random individual in any included population.
        Expectation is across the variability of learned self.prec
        :return: scalar h = E{ - ln p(theta | self) }

        Method: doc sec:MI eq:entropyGlobalTheta
        """
        d = self.mu.size
        return (d * np.log(2 * np.pi)  + d - self.prec.mean_log_det) / 2


# -------------------------------------- internal parameter classes
class ThetaMean(GaussianGivenPrecision):
    """Implements conditional Gaussian mean of trait locations,
    for the global population, represented by ALL included groups,
    given a precision matrix supplied as argument when needed.
    """
    @classmethod
    def initialize(cls, n_traits, learned_weight):
        """
        :param n_traits: number of traits in model
        :param learned_weight: weight for external precision object
            = effective number of observed data used for learning
        :return: a cls instance
        """
        return cls(loc=np.zeros(n_traits), learned_weight=learned_weight)

    def prune(self, keep):
        """Prune away un-necessary trait dimensions
        :param keep: 1D boolean array indicating traits to keep
        :return: None
        """
        self.loc = self.loc[keep]

    def weighted_mean_mean(self):
        """weigted outer product matrix of self.loc,
        needed for global prec adapt
        :return: m2 = gamma * self.mean(as column) * self.mean(as row)
            self.mean is written \bar m in doc
        """
        return self.learned_weight * self.loc[:, None] * self.loc

    def adapt(self, g_pop_mu, global_theta, prior):
        """VI update
        :param g_pop_mu: list of ir_group.PopulationMeanTheta instances, one for each group
        :param global_theta: a GlobalTheta instance containing self and associated objects
        :param prior: object of same class as self
        :return: ll = - KLdiv(self || prior) after update

        Method: doc sec:PosteriorTheta eq:PosteriorGlobalMuGamma eq:PosteriorGlobalMuMean
        """
        mean_b = global_theta.prec_factor_group.mean  # = <B> in doc
        self.learned_weight = (global_theta.prec_factor_global.mean  #  <C>
                               + mean_b  # <B>
                               * sum(1. - g_mu.global_weight for g_mu in g_pop_mu)
                               )
        self.loc = (prior.loc   # == 0.
                    + sum(g_mu.loc for g_mu in g_pop_mu)
                    * mean_b / self.learned_weight)
        return - self.relative_entropy(prior, global_theta.prec)

    def predictive(self, prec):
        """Predictive distribution, by integrating out prec
        :param prec: precision matrix implemented by a WishartRV instance
        :return: a MultiStudentRV instance that can generate samples
        """
        nu = prec.df
        df = nu + 1 - self.size
        gamma = self.learned_weight
        return MultiStudentRV(df=df,
                              loc=self.loc,
                              sigma=prec.inv_scale / df / gamma)


class ThetaMeanFixed:
    """Implements a Fixed prior mean of trait locations == 0
    """
    learned_weight = np.inf

    def __init__(self, loc):
        self.loc = loc

    @classmethod
    def initialize(cls, n_traits):
        """
        :param n_traits: number of traits in model
        :return: a cls instance
        """
        return cls(np.zeros(n_traits))

    @property
    def size(self):
        return len(self.loc)

    @property
    def mean(self):
        return self.loc

    def weighted_mean_mean(self):
        """mean_square matrix needed for global prec adapt
        """
        d = len(self.loc)
        return np.zeros((d, d))

    def prune(self, keep):
        """Prune away un-necessary trait dimensions
        :param keep: 1D boolean array indicating traits to keep
        :return: None
        """
        self.loc = self.loc[keep]

    # def adapt(self, group_pop_mu, global_theta, prior):  # *** should never be called ! *****

    def predictive(self, *args, **kwargs):
        """Fake random variable fixed at self.loc = all zero
        """
        return self

    def rvs(self, size, **kwargs):
        """
        :param size: number of fake sample vectors, all == 0.
        :param kwargs: not used
        :return: array with all-zero samples
        """
        return np.zeros((size, len(self.loc)))



# ------------------------------------- Global threshold-defining parameters
class GlobalEta(GaussianRV):
    """Global Gaussian distribution of threshold-defining parameters eta across groups
    with INDEPENDENT elements.
    """
    # def __init__(self, mu, prec):  # *** superclass

    def adapt(self, groups, prior):
        """
        :param groups: list of ir_group.RespondentGroup instances
        :param prior: object of same class as self, with prior distribution
        :return: LL = scalar = - KLdiv(self || prior)

        Method: doc sec:PosteriorEtaPsiGlobal
        """
        # ***** use superclass adapt jointly for mu and prec ? ******************
        eta_samples = [g.eta for g in groups]
        self.mu.adapt([np.mean(eta_g, axis=0)  # mean across samples
                       for eta_g in eta_samples], prior.mu)
        # logger.debug(f'Global eta.mu.mean = {self.mu.mean}')
        self.prec.adapt([np.mean(eta_g**2, axis=0)
                         for eta_g in eta_samples], prior.prec,
                        self.mu, prior.mu)
        # logger.debug(f'Global eta.prec.mean_inv = {self.prec.mean_inv}')
        return - self.relative_entropy(prior)

    # def relative_entropy(self, othr):   # -> superclass
    #     """Kullback-Leibler divergence KLdiv(self || othr)
    #     :param othr: instance of same class as self
    #     :return: E_self{ln pdf(x | self) / pdf(x | othr) }
    #     """
    #     return (self.mu.relative_entropy(othr.mu, self.prec)
    #             + self.prec.relative_entropy(othr.prec))


class EtaMean(GaussianGivenPrecision):
    """Implements conditional Gaussian distribution of group-specific threshold-defining parameters,
    given external precision.
    """
    # def __init__() by superclass

    @classmethod
    def initialize(cls, n_eta):
        """Create weakly informative prior distribution of
        threshold-defining eta parameters for all items.
        :return: a cls instance
        """
        return cls(loc=np.zeros(n_eta), learned_weight=ETA_PSEUDO_COUNT)

    def set_initial_loc(self, ir_count, base, trait_scale):
        """
        :param ir_count: list of 1D arrays with response counts
            ir_count[i][l] = total number of l-th ordinal response to i-th item, across all groups
        :param base: ir_base.ItemResponseBase instance defining eta -> threshold mapping
        :param trait_scale: presumed st.-dev. of inter-individual trait variations
        :return: a cls instance
        """
        def estim_eta(item_count, scale):
            """Estimate threshold values that might yield observed response count,
            assuming that individual latent variables are Gaussian with known scale.
            :param item_count: 1D count array for ONE item
            :param scale: inter-individual scale of latent variable Y
            :return: eta = 1D array of threshold-defining parameters
            """
            f = np.cumsum(item_count + PROB_PSEUDO_COUNT)
            p_cum = f/ f[-1]
            # = cumulative probabilities for latent variable to fall in each response interval
            # p_cum[l] = P(tau[l] < Y <= tau[l+1])
            tau = norm.ppf(p_cum[:-1], scale=scale)
            # EXCL. extreme thresholds -inf, +inf
            eta = base.thr.tau_inv(tau)
            # such that base.thr.tau(eta) = tau, with required restriction
            return eta
        # ---------------------------------------------------------------
        total_scale = np.sqrt(trait_scale**2 + base.rm_class.latent_scale()**2)
        # = presumed inter-individual st.dev. of latent variable
        eta_all = np.concatenate([estim_eta(item_count, total_scale)
                   for item_count in ir_count])
        self.loc = eta_all

    def adapt(self, eta, prior):  # *** use superclass ?
        """
        :param eta: array-like with observed data:
            eta[g] = 1D array with mean of current eta distribution for g-th group
        :param prior: object of same class as self, with prior distribution
        :return: None

        Method: doc sec:PosteriorEtaPsiGlobal
        """
        self.learned_weight = prior.learned_weight + len(eta)
        prior_eta = prior.learned_weight * prior.loc
        self.loc = (prior_eta + np.sum(eta, axis=0)) / self.learned_weight


# --------------------------------------------------- Global Precision Factors
class PrecFactorGroup(GammaRV):
    """Distribution of ratio factor, called B in doc,
    for the precision of group-specific mean trait vectors,
    relative to the global mean.
    """
    # def __init__(self, a, b):  by superclass

    def adapt(self, group_pop_mu, global_theta, prior):
        """
        :param group_pop_mu: iterable with one ir_group.PopulationMeanTheta instance for each group
            representing the mean trait in the population represented by the group
        :param global_theta: owner of self = ir_global.GlobalTheta instance
        :param prior: object with same class as self
        :return: ll = - KLdiv(self || prior)

        Method: doc sec:PosteriorB
        """
        d2 = [g_mu.mean_sq_dev(global_theta.mu, global_theta.prec)
              for g_mu in group_pop_mu]
        # d2[g] = mean square deviation of g-th group mean from global mean
        d = global_theta.mu.size
        self.a = prior.a + len(d2) * d / 2
        self.b = prior.b + sum(d2) / 2
        return - self.relative_entropy(prior)


class PrecFactorGlobal(GammaRV):
    """Distribution of precision factor, called C in doc,
    for the precision of the global mean trait vector,
    implemented by ir_global.GlobalTheta.mu,
    in case this is an object of class ir_global.ThetaMean
    """
    # def __init__(self, a, b):  by superclass

    def adapt(self, global_theta, prior):
        """
        :param global_theta: owner of self, ir_global.GlobalTheta instance
        :param prior: object with same class as self
        :return: ll = - KLdiv(self || prior)

        Method: doc sec:PosteriorC
        """
        d = len(global_theta.mu.loc)
        self.a = prior.a + d / 2
        gamma = global_theta.mu.learned_weight
        m = global_theta.mu.mean
        mean_prec = global_theta.prec.mean   # <Lambda>
        self.b = prior.b + (d / gamma + m @ mean_prec @ m) / 2
        return - self.relative_entropy(prior)  # superclass method


# ---------------------------------------------------- Precision parameters:
class ThetaPrecision(WishartRV):
    """Wishart-distributed Lambda = global inter-individual precision of trait vectors.
    The probability density function is
    p(Lambda) = (1/C) | Lambda|**((nu - p - 1)/2) exp(- trace(inv(V) Lambda)/2), where
        V = symmetric scale matrix,
        p = length of corresponding Gaussian vector
        nu = degree of freedom parameter >= p,
        Lambda.shape == V.shape == (p, p)
        C = |V|**(nu/2) 2**(nu p / 2) Gamma_p(nu/2) is the normalization factor
    """
    @classmethod
    def initialize(cls, n_traits):
        """Create a weakly informative prior distribution
        for the global precision of inter-individual trait vectors,
        common for all groups / populations
        :param n_traits: number of trait elements for each individual
        :return: a cls instance
        """
        nu = n_traits - 1 + THETA_PRECISION_DELTA
        # = minimal degrees-of-freedom to make the distribution just barely proper
        # We need a PROPER prior to be able to calculate relative entropy
        # between posterior and prior models.
        return cls(df=nu, scale=np.eye(n_traits) * THETA_SCALE_WITHIN / nu)

    # def __init__(self, scale, df):  # superclass

    def adapt(self, groups, global_theta, prior):
        """Update distribution parameters using trait data from all groups and global distributions.
        :param groups: iterable of ir_group.ItemResponseGroup instances
        :param global_theta: ir_global.GlobalTheta instance containing self and other related objects
        :param prior: object of same class as self
        :return: - KLdiv(self || prior)
        Result: updated internal parameters of self

        Method: doc sec:PosteriorLambda, eqs eq:PosteriorNu, eq:PosteriorV
        """
        n_s = 0     # accumulator for number of respondents
        cov = np.zeros(self.scale.shape)  # sum inter-individual covariance
        for g in groups:
            n_s += g.n_subjects
            cov += g.sum_theta_theta()
            mean_theta_g = g.pop_theta.mu.loc
            cov -= g.pop_theta.mu.learned_weight * mean_theta_g[:, None] * mean_theta_g   # eq:PosteriorV
        cov -= global_theta.mu.weighted_mean_mean()  # eq:PosteriorV
        self.scale = np.linalg.inv(prior.inv_scale + cov)   # eq:PosteriorV
        self.df = prior.df + n_s    # eqs eq:PosteriorNu
        return - self.relative_entropy(prior)

    def prune(self, keep):
        """Prune away un-necessary trait dimensions
        :param keep: 1D boolean array indicating traits to keep
        :return: None
        Result: self.scale reduced
        """
        self.scale = self.scale[keep, :][:, keep]


# -------------------------------------------------------------------------
class EtaPrecisionAmongGroups(GammaRV):
    """Array of independent gamma distributions for model parameter psi,
    representing diagonal precision matrix of the
    threshold-defining parameter vectors, called eta in doc,
    among different ItemResponseGroup instances
    """
    @classmethod
    def initialize(cls, n_eta, pseudo_groups):
        """Prior global distribution of precision of threshold-defining
        eta parameters across groups
        :param n_eta: total number of eta parameters for all items
        :param pseudo_groups: scalar number of prior "groups"
            with ZERO deviations from global mean eta parameters.
            Large value -> smaller threshold variations between real populations.
        :return: a cls instance
        """
        return cls(a=pseudo_groups / 2, b=ETA_B_AMONG * np.ones(n_eta))

    # def __init__(self, a=1., b=1.):  # ******* use superclass  ********

    def adapt(self, eta2, prior, prior_mu, eta_mu):
        """Adapt to given data
        :param eta2: 2D array-like with square observed mean_eta vectors
            eta2[g][k] = k-th mean squared eta value in g-th group
        :param prior: object of same class as self
        :param prior_mu: EtaMean object associated with prior
        :param eta_mu: EtaMean object associated with self
        :return: ll = KLdiv(self || global_pop) after adjustment

        Method: doc sec:PosteriorEtaPsiGlobal eq:PosteriorPsiShape eq:PosteriorPsiScale
        """
        self.a = prior.a + len(eta2) / 2    # eq:PosteriorPsiShape
        z2 = np.sum(eta2, axis=0) # sum across groups
        z2 += prior_mu.learned_weight * prior_mu.mean**2
        z2 -= eta_mu.learned_weight * eta_mu.mean**2
        self.b = prior.b + z2 / 2   # eq:PosteriorPsiScale
        return - self.relative_entropy(prior)

    def prune(self, keep):
        """Prune away un-necessary trait dimensions
        :param keep: 1D boolean array indicating traits to keep
        :return: None
        Result: self.b reduced, self.a is scalar, unchanged
        """
        self.b = self.b[keep]
