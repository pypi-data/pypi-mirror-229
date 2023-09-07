"""This module implements a multivariate Gaussian distribution of a random vector
and extends the scipy.stats implementations by including Bayesian learning.

*** Classes:
GaussianRV: a trainable Gaussian distribution of a random vector with INDEPENDENT elements,
    defined by a Gaussian mu array, and gamma-distributed precision parameters.

GaussianGivenPrecision: class for the random mu vector of a Gaussian vector,
    with either CORRELATED OR UNCORRELATED elements.


*** Version History:
* Version 1.0.0: new module within ItemResponseCalc, modified from EmaCalc
"""
import numpy as np
import logging
# from scipy.special import gammaln  # , psi

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # *** TEST


# -------------------------------------------
class GaussianRV:  # *** need subclass for vectors with CORRELATION ? ***
    """Gaussian distribution of a random 1D (row) array with UNCORRELATED elements.
    The probability density function is
    p(x | mu, Lambda) propto prod_d Lambda_d^0.5 exp(- 0.5 (x_d - mu_d)^2 Lambda_d ), where
    mu = (..., mu_d, ...) is the mu array, and
    Lambda=(..., Lambda_d, ...) is the vector of precision values,
        = inverse variance
        = inverse diagonal of covariance matrix.

    To allow Bayesian learning, mu and Lambda are random variables, with
    p(mu, Lambda) = p(pop_theta | Lambda) p(Lambda), where
    p(mu | Lambda) is implemented by a GaussianGivenPrecision instance, and
    p(Lambda) is implemented by either a GammaRV or a WishartRV instance.
    """
    log_2_pi = np.log(2 * np.pi)  # class constant for mean_logpdf calc

    def __init__(self, mu, prec):
        """
        :param mu: GaussianGivenPrecision instance
        :param prec: precision object, either a 1D GammaRV or a 2D WishartRV instance
        """
        self.mu = mu
        self.prec = prec

#     @classmethod
#     def initialize(cls,
#                    loc,
#                    prec_a, prec_b,
#                    learned_weight=0.001):
#         """Create cls instance with default structure
#         :param loc: 1D array-like location vector = mean of mu attribute
#         :param prec_a: scalar or 1D array-like precision gamma shape parameter
#         :param prec_b: 1D array-like precision gamma inverse-scale parameter
#             len(prec_b) == len(loc)
#         :param learned_weight: (optional) scalar effective number of observations
#             learned_weight = 0. gives a non-informative improper global_pop density
#         """
#         prec = PrecisionRV(a=prec_a, b=prec_b)
#         mu = GaussianGivenPrecision(loc, learned_weight, prec)
#         return cls(mu, prec)
#
    def __repr__(self):
        property_sep = ',\n\t'
        return (self.__class__.__name__ + '(\n\t'
                + property_sep.join(f'{k}={repr(v)}'
                                    for (k, v) in vars(self).items())
                + ')')

    @property
    def loc(self):
        return self.mu.loc

    @property
    def size(self):
        return len(self.loc)

    def _prec_mean_log(self):
        """Mean log det(full precision matrix),
        needed for log normalization constant.
        Simplified version for uncorrelated case.
        :return: scalar
        """
        return np.sum(self.prec.mean_log)

    # *********** separate mean_loglikelihood + log_normalization
    # to save computation during sampling that only needs loglikelihood part.

    def mean_logpdf(self, x):
        """E{ ln pdf( x | self ) }, expectation across all parameters of self
        :param x: 1-dim OR M-dim array or array-like list of sample vectors assumed drawn from self
            x[..., :] = ...-th sample row vector
        :return: scalar or array LL, with
            LL[...] = E{ ln pdf( x[..., :] | self ) }  INCL. log normalization constant
            LL.shape == x.shape[:-1]
        """
        x = np.asarray(x)
        if self.mu.learned_weight <= 0.:
            return np.full(x.shape[:-1], -np.inf)
        # z2 = np.dot((x - self.loc) ** 2, self.prec.mu)
        z2 = _square_mahanalobis(x - self.loc, self.prec.mean)
        # = Mahanalobis distance, z2.shape == x.shape[:-1]
        return (- z2 - self.size / self.mu.learned_weight
                + np.sum(self.prec.mean_log) - self.size * self.log_2_pi  # np.log(2 * np.pi)
                ) / 2

    def d_mean_logpdf(self, x):
        """First derivative of self.mean_logpdf(x) w.r.t x
        :param x: 1-dim OR M-dim array or array-like list of sample vectors assumed drawn from self
            x[..., :] = ...-th sample row vector
        :return: array dLL, with
            dLL[..., i] = d E{ ln pdf( x[..., :] | self ) } / d x[..., i]
            dLL.shape == x.shape
        """
        d = np.asarray(x) - self.loc
        return - d * self.prec.mean

    def relative_entropy(self, othr):
        """Kullback-Leibler divergence between self and othr
        :param othr: single instance of same class as self
        :return: scalar KLdiv(q || p) = E_q{ln q(x) / p(x)},
            where q = self and p = othr
        """
        return (self.mu.relative_entropy(othr.mu, self.prec) +
                self.prec.relative_entropy(othr.prec))

    # def predictive(self, rng=None):  # *****************************
    #     """Predictive distribution of random vector, integrated over parameters.
    #     :param rng: (optional) random.Generator object
    #     :return: rv = single StudentRV instance with independent elements
    #
    #     Scalar Student pdf(x) propto (1 + (1/df) (x-m)^2 / scale^2 )^(- (df + 1) / 2)
    #     where scale = sqrt{ (1+beta) self.prec.inv_scale / (beta self.prec.shape)
    #     and Student df = 2* self.prec.shape
    #     See Leijon EmaCalc report Appendix, or Leijon JASA PairedComp paper appendix
    #     """
    #     beta = self.mu.learned_weight
    #     return StudentRV(loc=self.loc,
    #                      scale=np.sqrt(self.prec.b * (1. + beta) / (beta * self.prec.a)),
    #                      df=2 * self.prec.a,
    #                      rng=rng)


# ----------------------------------------------------------------------
class GaussianGivenPrecision:
    """Conditional Gaussian distribution of the mean of a Gaussian random vector,
    given a 1D precision array representing a diagonal precision matrix,
    OR with correlated elements, given a full 2D precision matrix.

    The probability density function is
    p(mu | Lambda) propto  det(beta Lambda)^0.5 exp(- 0.5 Mahanalobis(mu - m, beta Lambda)^2)
    where
    Mahanalobis(x, L)^2 = the square Mahanalobis distance x*T L x
    mu=(..., mu_d, ...)  is a row vector, sample of random vector self
    m=(..., m_d, ...) is the location of self,
    beta is the scalar learned_weight property
    Lambda = (..., Lambda_ij, ....) = 2D square symmetric positive definite precision matrix,
    OR, in case of UNCORRELATED vector,
    Lambda=(..., Lambda_d, ...) is the 1D diagonal of the full matrix
    defined externally in either case.

    Module function _square_mahanalobis(...) handles both cases.
    """
    def __init__(self, loc, learned_weight):
        """Conditional Gaussian vector, given precision matrix
        Associated precision supplied as argument when needed.
        :param loc: location vector
        :param learned_weight: scalar effective number of learning data
        """
        assert np.isscalar(learned_weight), 'learned_weight must be scalar'
        self.loc = np.asarray(loc)
        self.learned_weight = learned_weight

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                '\n\t'.join(f'{k}= {repr(v)},'
                            for (k, v) in self.__dict__.items()) +
                '\n\t)')

    @property
    def size(self):
        return len(self.loc)

    @property
    def mean(self):
        return self.loc

    # def adapt(self, x, w, prior):  # *** overridden not needed in ItemResponseCalc
    #     """Update distribution parameters using observed data and global_pop.
    #     :param x: 2D array or array-like list of sample vectors assumed drawn from self
    #     :param prior: global_pop conjugate distribution, same class as self
    #     :param prior: global_pop conjugate distribution, same class as self
    #     :return: None
    #     Result: updated internal parameters of self
    #     """
    #     m = self.loc  # for debug only
    #     self.learned_weight = prior.learned_weight + np.sum(w)
    #     sx = prior.learned_weight * prior.loc + np.dot(w, x)
    #     self.loc = sx / self.learned_weight
    #     d = self.loc - m  # update change in location
    #     if self.learned_weight > 0.5:
    #         logger.debug('comp loc change: '
    #                      + np.array_str(d, precision=3))

    def relative_entropy(self, othr, prec):
        """Kullback-Leibler divergence between self and othr, given precision
        :param othr: single instance of same class as self
        :param prec: single instance of external precision of self,
            either 1D or 2D array
        :return: scalar KLdiv[q || p] = E_q{ln q(x) / p(x)},
            where q = self and p = othr
        """
        d = len(self.loc)
        md = self.loc - othr.loc
        beta_pq_ratio = othr.learned_weight / self.learned_weight
        return (othr.learned_weight * _square_mahanalobis(md, prec.mean)
                + d * (beta_pq_ratio - np.log(beta_pq_ratio) - 1.)
                ) / 2


    # def predictive(self, rng=None):
    #     """Predictive distribution of self, integrated over self.prec
    #     p(pop_theta) = integral p(pop_theta | prec) p(prec) d_prec, where
    #     p(prec) is represented by the PrecisionRV instance self.prec
    #     :param rng: (optional) random.Generator object
    #     :return: rv = single StudentRV instance
    #
    #     Method: see JASA PairedComp paper Appendix
    #     see also Leijon EmaCalc doc report,
    #     re-checked 2022-01-01
    #     """
    #     beta = self.learned_weight
    #     return StudentRV(loc=self.loc,
    #                      scale=np.sqrt(self.prec.b / (self.prec.a * beta)),
    #                      df=2 * self.prec.a,
    #                      rng=rng)


# --------------------------------------- Module help functions
def _square_mahanalobis(d, mean_prec):  # ***** -> static method ?
    """Precision-weighted square of given distance vector(s)
    for a Gaussian vector with either dependent or independent elements.
    :param d: array-like with difference vector(s)
        d[..., :] = ...-sample assumed drawn from a Gaussian distribution
    :param mean_prec: mean precision
        = 2D symmetric array or 1D array with diagonal precision values
        mean_prec.shape[-1] == d.shape[-1]
    :return: z2 = scalar or array
        z2.shape == d.shape[:-1]
    """
    if mean_prec.ndim == 1:  # diagonal precision, no correlations
        return np.dot(d**2, mean_prec)
    else:  # full symmetric precision matrix, with correlation
        return np.einsum('...i, ij, ...j',
                         d, mean_prec, d)


# ------------------------------------------------- TEST
if __name__ == '__main__':
    from ItemResponseCalc.gamma import GammaRV
    from ItemResponseCalc.wishart import WishartRV
    import copy
    from scipy.optimize import approx_fprime, check_grad

    # --------------------------- Test GaussGivenPrecision
    nx = 3
    m = np.zeros(nx)
    mean_prec1 = np.array(np.arange(1, nx + 1))
    mean_prec2 = np.diag(mean_prec1)

    prec1 = GammaRV(a=1., b=1./mean_prec1)
    prec2 = WishartRV(df=1, scale=mean_prec2)

    mu = GaussianGivenPrecision(loc=m + 1., learned_weight=10)
    mu_prior = GaussianGivenPrecision(loc=m, learned_weight=0.1)
    kl_div1= mu.relative_entropy(mu_prior, prec1)
    print('1D prec: kldiv = ', kl_div1)
    kl_div2= mu.relative_entropy(mu_prior, prec2)
    print('2D prec: kldiv = ', kl_div2)

    # --------------------------- Test d_logpdf
    gx = GaussianRV(mu=mu, prec=prec1)  # a Gauss-gamma RV, 1D prec
    test_x = gx.loc + 2.

    def fun(x):
        return gx.mean_logpdf(x)

    def jac(x):
        return gx.d_mean_logpdf(x)

    print('approx gradient = ', approx_fprime(test_x, fun, epsilon=1e-6))
    print('exact  gradient = ', jac(test_x))
    err = check_grad(fun, jac, test_x, epsilon=1e-6)
    print('check_grad err = ', err)


