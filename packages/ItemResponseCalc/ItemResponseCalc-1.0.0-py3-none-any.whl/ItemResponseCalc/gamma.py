"""This module implements a random variable with gamma distribution,
or an array of independent such variables.

Extends the scipy.stats implementation by including Bayesian learning.
"""
import numpy as np
from scipy.special import gammaln, psi

class GammaRV:
    """Implements a vector of INDEPENDENT gamma-distributed random variables.
    The probability density function is
    p(Lambda) = prod_d C_d Lambda_d^(a_d - 1) exp(- b_d Lambda_d), i.e., a gamma density,
        where
        a = scalar (or 1D array) shape parameters
        b = 1D array of inverse-scale parameters
        Lambda.shape == b.shape
        a and b must have broadcast-compatible shapes
        C_d = b_d^a / Gamma(a) is the normalization factor
    """
    def __init__(self, a=0., b=1.):
        """
        :param a: scalar or 1D array-like shape parameter(s)
        :param b: 1D array-like with inverse scale parameter(s)
        """
        # assert np.isscalar(a), 'shape parameter should be scalar for IRT usage'
        try:
            a = np.array(a)
            b = np.array(b)
            test = a / b
        except ValueError as e:
            raise RuntimeError('a and b parameters must be broadcast-compatible and > 0. ' + str(e))
        self.a = a
        self.b = b

    def __repr__(self):
        return self.__class__.__name__ + f'(a= {repr(self.a)}, b= {repr(self.b)})'

    @property
    def size(self):
        return self.mean.size

    @property
    def shape(self):
        return self.mean.shape

    @property
    def scale(self):
        return 1./self.b

    @property
    def inv_scale(self):
        return self.b

    @property
    def mean(self):
        """E{self}"""
        return self.a / self.b

    @property
    def mean_inv(self):
        """E{ inv(self) }, where
        inv(self) has an inverse-gamma distribution
        """
        if self.a.ndim > 0:
            m = self.b / np.maximum(self.a - 1, np.finfo(float).eps)
            m[self.a <= 1.] = np.nan
            return m
        elif self.a <= 1.:
            return np.full_like(self.b, np.nan)
        else:
            return self.b / (self.a - 1)

    def mode_inv(self):
        """mode{ inv(self) }, where
        inv(self) has an inverse-gamma distribution
        """
        return self.b / (self.a + 1.)

    @property
    def mean_log(self):
        """E{ ln self } element-wise"""
        return psi(self.a) - np.log(self.b)

    def logpdf(self, x):
        """ln pdf(x | self)
        :param x: array or array-like list
            x.shape[-1:] == self.mean.shape
        :return: lp = scalar or array, with
            lp[...] = ln pdf(x[..., :] | self)
            lp.shape == x.shape[:-1]
        """
        bx = self.b * np.asarray(x)
        return np.sum((self.a - 1.) * np.log(bx) - bx
                      + np.log(self.b) - gammaln(self.a),
                      axis=-1)

    # def adapt(self, x2, w, prior, new_mean_2):  # overridden anyway in ItemResponseCalc
    #     """Update distribution parameters using observed data and prior.
    #     :param x2: 2D array or array-like list of squared samples
    #         for vectors assumed drawn from distribution with precision == self.
    #     :param w: 1D array with sample weights
    #     :param prior: object of same class as self
    #     :param new_mean_2: weighted difference = nu * new_loc^2 - nu' * prior_loc**2
    #         where nu is the new sum-weight and nu' is the prior sum-weight
    #     :return: None
    #
    #     Result: updated internal parameters of self
    #     Method: Leijon EmaCalc report: sec:GaussGammaUpdate
    #     """
    #     self.a = prior.a + np.sum(w) / 2
    #     # eq:GammaUpdateA
    #     self.b = prior.b + (np.dot(w, x2) - new_mean_2) / 2
    #     # eq:GammaUpdateB

    def relative_entropy(q, p):
        """Kullback-Leibler divergence between PrecisionRV q and p,
        :param p: another instance of same class as self = q
        :return: scalar KLdiv( q || p ) = E{ ln q(x)/p(x) }_q

        Arne Leijon, 2018-07-07 copied from gamma.py 2015-10-16, checked 2023-07-25
        """
        pb_div_qb = p.b / q.b
        return np.sum(gammaln(p.a) - gammaln(q.a)
                      - p.a * np.log(pb_div_qb)
                      + (q.a - p.a) * psi(q.a)
                      - q.a * (1. - pb_div_qb)
                      )

