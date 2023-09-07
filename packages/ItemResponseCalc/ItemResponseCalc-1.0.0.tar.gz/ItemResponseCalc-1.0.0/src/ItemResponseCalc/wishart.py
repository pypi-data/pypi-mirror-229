"""This module implements a random matrix with Wishart distribution
suitable to represent the precision matrix of a Gaussian random vector
with correlated elements.

This version is used as part of ItemResponseCalc package.

*** Main Classes:

WishartRV -- a random symmetric matrix with Wishart distribution.

Similar to a frozen scipy.stats.wishart distribution object,
but extends functionality by allowing the objects to adapt to observed data.

*** Version History:
* Version 1.0.0: New module in this version of ItemResponseCalc
"""
import numpy as np
from scipy.special import multigammaln, psi
from scipy.stats import wishart


# ---------------------------------------------------------------------------
class WishartRV:
    """A symmetric precision matrix (called Lambda in doc) modelled as a random variable,
    with a probability density function
    p(Lambda) = (1/C) | Lambda|**((nu - p - 1)/2) exp(- trace(inv(V) Lambda)/2),
    where
        V = symmetric positive definite scale matrix,
        p = length of associated Gaussian vector
        nu = degree of freedom parameter > p - 1,
        Lambda.shape == V.shape == (p, p)
        C = |V|**(nu/2) 2**(nu * p / 2) Gamma_p(nu/2) = the normalization factor
        Gamma_p = multivariate gamma function
    The distribution is proper for nu > p - 1.
    """
    def __init__(self, scale, df):
        """
        :param scale: 2D array or array-like symmetric scale matrix, called V in doc
        :param df: scalar degrees of freedom, called nu in doc
        """
        # *** store scale or inv_scale internally? ***
        self.scale = np.asarray(scale)
        self.df = df

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                '\n\t'.join(f'{k}= {repr(v)},'
                            for (k, v) in self.__dict__.items()) +
                '\n\t)')

    @property
    def shape(self):
        return self.scale.shape

    @property
    def inv_scale(self):
        return np.linalg.inv(self.scale)

    @property
    def mean(self):
        """E{self}"""
        return self.df * self.scale

    @property
    def mean_inv(self):
        """E{ inv(self) },
        inv(self) = a random matrix with inverse-Wishart distribution
        """
        d = self.shape[0]
        if self.df > d + 1:
            return self.inv_scale / (self.df - d - 1)
        else:  # mean_inv is undefined
            return np.full_like(self.scale, np.nan)

    def mode_inv(self):
        """Mode of inv(self) = most likely corresponding covariance matrix
        when self is the precision matrix of a Gaussian random vector.
        """
        return self.inv_scale / (self.df + self.scale.shape[0] + 1)

    @property
    def mean_log_det(self):
        """E{ ln |self| }
        (self is positive definite, so sign of determinant is always = 1.)
        Needed for mean_logpdf of multivariate Gaussian random variable.
        """
        d = self.scale.shape[0]
        (s, log_det_scale) = np.linalg.slogdet(self.scale)
        if s <= 0:
            raise RuntimeError('Wishart scale matrix must be positive definite')
        return multi_psi(self.df / 2, d) + d * np.log(2) +  log_det_scale

    def logpdf(self, x):  # not needed in ItemResponseCalc, only for test
        """ln pdf(x | self), using scipy.stats.wishart
        :param x: 2D or 3D array or array-like list
        :return: lp = scalar lp = ln pdf(x | self)
            lp.shape == x.shape[:-2],
            i.e., == () if x is 2D, == x.shape[0] if x is 3D.

        NOTE: scipy.stats.wishart can only calculate logpdf for matrices stacked along 3rd axis,
            NOT first axis, like samples from rvs
        """
        # ***** first transpose in case 3D ? ***************
        # ***** OR implement explicitly, using np stacking convention ?
        return wishart.logpdf(x, scale=self.scale, df=self.df)

    def rvs(self, size=1):
        """Samples from Wishart distribution
        :param size: scalar integer number of sample matrices
        :return: S = 3D array
            S[..., :, :] = ...-th random precision matrix
            S.shape == (*size, *self.scale.shape)
        """
        # *** numpy.random can not yet sample a Wishart distribution
        # scipy.wishart.rvs may generate singular samples if self.df < self.shape[0]
        return wishart.rvs(size=size, scale=self.scale, df=self.df)

    # ------------------------------------------- VI update:
    # def adapt(self, groups, global_theta, prior):  # non needed, over-ridden anyway
    #     """Update distribution parameters using trait data from all groups and global distributions.
    #     :param groups: iterable of ir_group.ItemResponseGroup instances
    #     :param global_theta: ir_global.GlobalTheta instance
    #     :param prior: object of same class as self
    #     :return: - KLdiv(self || prior)
    #     Result: updated internal parameters of self
    #
    #     Method: doc sec:PosteriorLambda, eqs eq:PosteriorNu, eq:PosteriorV
    #     """
    #     n_s = 0     # total number of respondents
    #     cov = np.zeros(self.scale.shape)  # sum inter-individual covariance
    #     for g in groups:
    #         n_s += g.n_subjects
    #         cov += g.sum_theta_theta()
    #         mean_theta_g = g.theta_pop.mu.loc
    #         cov -= g.mu.learned_weight * mean_theta_g[:, None] * mean_theta_g   # eq:PosteriorV
    #     cov -= global_theta.mu.sum_square_mean()  # eq:PosteriorV
    #     self.scale = np.linalg.inv(prior.inv_scale + cov)   # eq:PosteriorV
    #     self.df = prior.df + n_s    # eqs eq:PosteriorNu
    #     return - self.relative_entropy(prior)

    def relative_entropy(self, othr):
        """Kullback-Leibler divergence between self and othr
        :param othr: single instance of same class as self
        :return: scalar KLdiv(q || p) = E_q{ln q(x) / p(x)},
            where q = self and p = othr

        Method: Using notation D = self.shape[0], V = self.scale,
        KLdiv = (q.df - p.df) * E{log_det(self)} / 2
            - (q.df - p.df) * ln(2) * D / 2
            + (p.df * log_det(p.V) - q.df * log_det(q.V)) / 2
            + trace[(inv(p.V) - inv(q.V)) * E{self}] / 2
            + gammaln_D(p.df/2) - gammaln_D(q.df/2)
        where
            E{log_det(self)} = psi_D(q.df/2) + D * ln(2) + log_det(q.V)
            E{self} = q.df * q.V
        = (q.df - p.df) * psi_D(q.df/2) / 2
            + p.df * (log_det(p.V) - log_det(q.V)) / 2
            + trace[(inv(p.V) - inv(q.V)) q.V] * q.df / 2
            + gammaln_D(p.df/2) - gammaln_D(q.df/2)
        """
        d = self.scale.shape[0]
        # Vpinv_Vq_dot = np.dot(othr.inv_scale, self.scale)
        Vpinv_Vq = np.linalg.solve(othr.scale, self.scale)
        (s, log_det_VV) = np.linalg.slogdet(Vpinv_Vq)
        return (0.5 * ((self.df - othr.df) * multi_psi(self.df/2, d)
                       - othr.df * s * log_det_VV
                       + (np.trace(Vpinv_Vq) - d) * self.df
                       )
                + multigammaln(othr.df/2, d) - multigammaln(self.df/2, d)
                )


# ------------------------------------------------ help function:
def multi_psi(a, d):
    """Multivariate psi function
    = first derivative of scipy.special.multigammaln(a, d) w.r.t a
    :param a: scalar ONLY
    :param d: scalar dimensionality
    :return: scalar
        = sum( psi( a + (1-j)/2) for j = 1,...,d ) (Wikipedia)
        = sum( psi( a - (j-1)/2) for j = 1,...,d )
        = sum( psi( a - j/2) for j = 0,...,d-1 )
    """
    return np.sum(psi(a - np.arange(d) / 2))


# ------------------------------------------------------------- Module TEST:

if __name__ == '__main__':

    # --------------------------- Testing WishartRV:
    nx = 3
    m = np.zeros(nx)
    mean_prec1 = np.array(np.arange(1, nx + 1))
    mean_prec2 = np.diag(mean_prec1)

    prec2 = WishartRV(df=nx + 1, scale=mean_prec2 + 1.)
    prec2_prior = WishartRV(df=nx - 1 + 0.1, scale=mean_prec2)
    print('KLdiv = ', prec2.relative_entropy(prec2_prior))

    x = prec2.rvs(size=5)
    print('x = prec2.rvs(3) = ', x)
    # *** NOTE: MUST transpose for scipy.wishart.logpdf to work
    x_t = x.transpose((1, 2, 0))
    print('logpdf(x) = ', prec2.logpdf(x_t))


