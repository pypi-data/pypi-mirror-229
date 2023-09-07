"""This module implements a multivariate Student distribution of a random vector
with possibly DEPENDENT (correlated) vector elements,
or with INDEPENDENT vector elements,
and extends the scipy.stats implementations by including Bayesian learning.

This distribution is a predictive distribution for a multivariate Bayesian GaussianRV model.
The multivariate Student is obtained by integrating out the random variations of the precision of the Gaussian.

*** Reference:
M. Roth. On the multivariate t distribution.
Technical Report LiTH-ISY-R-3059, Linköping University, 2013.

*** Classes:
MultiStudentRV: a multivariate Student-t distribution allowing correlations between vector elements.
    NOTE: Even if elements are uncorrelated, i.e., the covariance matrix is diagonal,
    the elements are NOT independent, i.e.,
    the density function is NOT a product of scalar Student-t densities.

StudentRV: Student-t distribution for a vector with INDEPENDENT elements.

*** Version History:
* Version 1.0.0: new module within ItemResponseCalc
"""
import numpy as np
import logging
from scipy.special import gammaln  # , psi

RNG = np.random.default_rng()  # default random generator
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # *** TEST


# ---------------------------------------------------------------------------
class MultiStudentRV:
    """Multivariate Student distribution of 1D random ROW vector
    with inter-dependent elements.
    The density function is (Roth, 2013; Wikipedia)
    f(x) = C [1 + (x - m)^T Sigma^{-1} (x - m) / df ]^{(df + D) / 2}
        where x and m are COLUMN vectors, D = len(x),
        df is degrees-of-freedom parameter,
        Sigma is symmetric positive-definite square matrix.
        (Covariance == Sigma * df / (df - 2), defined only for df > 2.)
        The normalization factor is
        C = Gamma((df + D) / 2) det(Sigma)^{-1/2) / Gamma(df / 2) df^{D/2) pi^{D/2)
    """
    def __init__(self, df,
                 loc=np.array(0.).reshape((1,)),
                 sigma=np.array(1.).reshape((1, 1))):
        """
        :param df: scalar degrees of freedom, MUST be > 0
        :param loc: 1D array or array-like list of location elements
        :param sigma: 2D symmetric positive semi-definite matrix
            (called shape matrix in scipy, scale matrix in Wikipedia)
            sigma.shape == (len(loc), len(loc))
        *** OR save only the scale (square root) matrix, s.t., sigma = scale @ scale.T ***
        """
        self.df = df
        self.loc = np.asarray(loc)
        self.sigma = np.asarray(sigma)

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                '\n\t'.join(f'{k}= {repr(v)},'
                            for (k, v) in self.__dict__.items()) +
                '\n\t)')

    @property
    def shape(self):
        return self.loc.shape

    @property
    def size(self):
        return self.loc.size

    @property
    def mean(self):
        if self.df > 1.:
            return self.loc
        else:
            return np.full_like(self.loc, np.nan)

    @property
    def cov(self):
        """Covariance matrix"""
        if self.df > 2:
            return self.sigma * self.df / (self.df - 2.)
        else:
            return np.full_like(self.sigma, np.nan)

    def logpdf(self, x):
        """ln pdf(x | self)
        :param x: array or array-like list of sample vectors
            must be broadcast-compatible with self.loc
        :return: lp = scalar or array of logpdf values
            lp[...] = ln pdf[x[..., :] | self)
            lp.shape == x.shape[:-1]
        """
        raise NotImplementedError

    # def rvs_scipy(self, size=None, rng=RNG):
    #     """Generate array of random variates drawn from self
    #     :param size: integer or tuple with number of desired samples,
    #         where each sample.shape == self.shape
    #     :param rng: (optional) instance of np.random.Generator or subclass
    #     :return: x = array of samples
    #         x.shape == (*size, *self.shape)
    #     """
    #     # **** use np.random instead, with Gauss-gamma method (Roth, 2013)
    #     if size is None:
    #         result_shape = self.shape
    #     elif np.ndim(size) == 0:
    #         result_shape = (size,) + self.shape
    #     else:
    #         result_shape = size + self.shape
    #     x = multivariate_t.rvs(size=size,
    #                            df=self.df,
    #                            loc=self.loc,
    #                            shape=self.sigma)
    #     # multivariate_t squeezes result if loc.shape == (1,)
    #     if self.size == 1:  # must Un-sqeeze if x.shape != result_size
    #         x = x.reshape(result_shape)  # temp fix
    #     return x

    def rvs(self, size=None, rng=RNG):
        """Generate array of random variates drawn from self
        :param size: integer or tuple with number of desired sample vectors,
            where each sample.shape == self.shape
        :param rng: (optional) instance of np.random.Generator or subclass
        :return: x = array of samples
            x.shape == (*size, *self.shape)

        Method: Roth (2013) eq. 2.1
        """
        if size is None:
            result_shape = self.shape
        elif np.ndim(size) == 0:
            result_shape = (size,) + self.shape
        else:
            result_shape = size + self.shape
        (eigval, eigvec) = np.linalg.eigh(self.sigma)
        # eigval = 1D array of eigenvalues, eigvec = 2D array with COLUMN eigenvectors
        y = rng.standard_normal(size=result_shape)
        y *= np.sqrt(eigval)
        y = y @ eigvec.T
        # = samples of Gaussian with mean == 0 and cov = inv(self.sigma)
        v = rng.gamma(size=y.shape[:-1], shape=self.df / 2, scale=2 / self.df)
        # = samples of gamma-distributed V with mean == 1., ONE for each vector in y
        return self.loc + y / np.sqrt(v[..., None])

class MultiStudentGivenMean(MultiStudentRV):
    """Variant with mean conditionally depending on an external random variable
    self.mean = self.loc + self.mean_factor * offset
    Needed for predictive model of population mean trait in ir_group.
    """
    def __init__(self, mean_factor=1., **kwargs):
        """
        :param mean_factor: scalar factor to be applied to external offset array
        :param kwargs: arguments to superclass
        """
        super().__init__(**kwargs)
        self.mean_factor = mean_factor

    def rvs(self, mu_rvs=np.asarray(0.), size=None, rng=RNG):
        """Generate array of random variates drawn from self
        :param size: integer or tuple with number of desired samples,
            where each sample.shape == self.shape
        :param rng: (optional) instance of np.random.Generator or subclass
        :param mu_rvs: (optional) array of externally generated random vectors
            such that conditional self.mean = self.loc + self.mean_factor * mu_rvs
        :return: x = array of samples
            x.shape == (*size, *self.shape)
        """
        if size != mu_rvs.shape[:-1] and size is not None:
            logger.warning(f'Changed to size = {mu_rvs.shape[:-1]} like given mu_rvs.')
        size = mu_rvs.shape[:-1]
        x = super().rvs(size=size, rng=rng)
        return x + self.mean_factor * mu_rvs


class StudentRV:
    """Frozen Student distribution of 1D random vector with INDEPENDENT elements,
    i.e., with density function as a product of scalar Student-t densities.
    """
    def __init__(self, df,
                 loc=np.array(0.).reshape((1,)),
                 scale=np.array(1.).reshape((1,)),
                 rng=None):
        """
        :param df: scalar or 1D array-like, degrees of freedom
        :param loc: 1D array or array-like list of location elements
        :param scale: scalar or 1D array or array-like list of scale parameter(s)
            df, loc, and scale must have broadcast-compatible shapes
        :param rng: (optional) random.Generator object
        """
        self.df = np.asarray(df)
        self.loc = np.asarray(loc)
        self.scale = np.asarray(scale)
        if rng is None:
            self.rng = np.random.default_rng()
        else:
            self.rng = rng

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                '\n\t'.join(f'{k}= {repr(v)},'
                            for (k, v) in self.__dict__.items()) +
                '\n\t)')

    @property
    def size(self):
        return self.loc.size  # len(self.loc)

    @property
    def mean(self):
        if self.df.ndim > 0:
            m = self.loc + 0.  # copy
            m[self.df <= 1.] = np.nan
            return m
        elif self.df > 1.:
            return self.loc
        else:
            return np.full_like(self.loc, np.nan)

    @property
    def var(self):
        """Variance array
        (all correlations == 0.)
        """
        if self.df.ndim > 0:
            v = self.scale ** 2 * self.df / np.maximum(self.df - 2., np.finfo(float).eps)
            v[self.df <= 2.] = np.inf
            v[self.df <= 1.] = np.nan
            return v
        elif self.df > 2:
            return self.scale ** 2 * self.df / (self.df - 2.)
        elif self.df > 1:
            return np.full_like(self.loc, np.inf)
        else:
            return np.full_like(self.loc, np.nan)

    def logpdf(self, x):
        """ln pdf(x | self)
        :param x: array or array-like list of sample vectors
            must be broadcast-compatible with self.loc
        :return: lp = scalar or array of logpdf values
            lp[...] = ln pdf[x[..., :] | self)
            lp.shape == x.shape[:-1]
        Arne Leijon, 2018-07-08, **** checked by comparison to scipy.stats.t
        """
        d = (x - self.loc) / self.scale
        return np.sum(- np.log1p(d**2 / self.df) * (self.df + 1) / 2
                      - np.log(self.scale)
                      + gammaln((self.df + 1) / 2) - gammaln(self.df / 2)
                      - 0.5 * np.log(np.pi * self.df),
                      axis=-1)

    def rvs(self, size=None):
        """Random vectors drawn from self.
        :param size: scalar or tuple with number of sample vectors
        :return: x = array of samples
            x.shape == (*size, self.size)
        """
        if size is None:
            s = self.size
        elif np.isscalar(size):
            s = (size, self.size)
        else:
            s = (*size, self.size)
        # z_sc = scipy_t.rvs(df=self.df, size=s)
        z = self.rng.standard_t(df=self.df, size=s)
        # = standardized samples
        return self.loc + self.scale * z


# ------------------------------------------------- TEST
if __name__ == '__main__':
    from scipy.stats import multivariate_t

    # --------------------------- Test MultiStudentRV
    d = 1
    nx = 1000000
    m = 1. + np.arange(d)  # np.array([1., 2., 3.])  # np.zeros(d)
    s = 1. + np.arange(d)[::-1]  # np.array([3., 2., 1.])
    sigma = RNG.uniform(size=(d, d), low=-0.9, high=0.9)  # correlations
    sigma = (sigma + sigma.T) / 2.
    sigma[range(d), range(d)] = 1.
    sigma *= s[:, None] * s  # covariance
    (eigval, eigvec) = np.linalg.eigh(sigma)  # must be symmetric and positive semi-definite
    print(f'sigma eigval = {eigval}')
    for df in np.array([1.5, 2.5, 3., 10., 30.]):
        st = MultiStudentRV(df=df, loc=m, sigma=sigma)
        print(f'\n*** Testing {st}')
        print(f'st.meam= {st.mean}')
        print(f'st.cov=\n' + np.array_str(st.cov,
                                                 precision=3, suppress_small=True))

        scipy_x = multivariate_t.rvs(size=nx,
                                     df=df,
                                     loc=m,
                                     shape=sigma)
        if d == 1:
            scipy_x = scipy_x.reshape((nx, d))

        print(f'mean(rvs_scipy)= {np.mean(scipy_x, axis=0)}')
        print(f'cov(rvs_scipy)=\n' + np.array_str(np.cov(scipy_x, rowvar=False),
                                                 precision=3, suppress_small=True))

        print(f'MultiStudentRV.rvs() = {st.rvs()}')
        x = st.rvs(size=nx)
        print(f'mean(x)= {np.mean(x, axis=0)}')
        print(f'cov(x)=\n' + np.array_str(np.cov(x, rowvar=False),
                                         precision=3, suppress_small=True))
