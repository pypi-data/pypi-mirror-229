"""This module implements core functions of the
IRT Graded Response Model (Samejima, 1997).

These functions are collected in a separate module to simplify
selecting either this model, or any other model, in future versions.

*** Main Class: GradedResponse

*** References:
F. Samejima (1997). Graded response model.
In W. J. v. D. Linden and R. K. Hambleton, eds.,
*Handbook of Modern Item Response Theory*, p. 85–100. Springer, New York.

J.-P. Fox (2010). *Bayesian Item Response Modeling: Theory and Applications*.
Statistics for Social and Behavioral Sciences. Springer.

*** Version:
* Version 1.0.0:
2023-07-22, tested gradient function OK with scipy.check_grad
2023-07-21, modified methods for jointly sampled (eta, theta) parameters

2020-06-14, first version with methods copied from item_respondents
    to replace functions previously defined there.
2020-06-15, cleanup, tested
"""
import numpy as np

from ItemResponseCalc.ir_latent import LatentLogistic

import logging
logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------
class GradedResponse:
    """Implementing central methods to calculate
    log probability of observed responses, and corresponding gradients,
    given item and respondent parameters.
    """
    def __init__(self, latent_class=LatentLogistic, scale=None):
        """
        :param latent_class: class of latent variable that determines responses
        :param scale: (optional) 1D array of scale factors
            to get same response probabilities after external change of (eta, theta) scale
        """
        self.latent_class = latent_class
        self.scale = scale  # *** not needed not used in this version?

    def latent_scale(self):
        return self.latent_class.scale

    def log_response_prob(self, tau, theta):
        """Probability-mass distribution over all possible responses
        for given parameters.
        :param tau: 1D or 2D array of all response thresholds, INCL. extremes at -inf, +inf
            tau[..., m, l] = (..., m)-th sample of lower threshold for Response = l
        :param theta: 1D array with hypothetical latent-variable locations
        :return: p = 2D or 3D array with
            p[..., t, l] = prob{l-th response | ...-th tau vector, t-th theta value}
        """
        lp = np.array([self.latent_class.log_cdf_diff(tau[..., l, None] - theta,
                                                      tau[..., l + 1, None] - theta)
                       for l in range(tau.shape[-1] - 1)])
        return np.moveaxis(lp, 0, -1)

    def d_log_response_prob_d_theta(self, tau, theta):  # ******** not tested !
        """Partial derivative of log_response_prob(self, tau, theta) w.r.t. theta.
         :param tau: 1D or 2D array of all response thresholds, INCL. extremes at -inf, +inf
             tau[..., m, l] = (..., m)-th sample of lower threshold for Response = l
         :param theta: 1D array with hypothetical latent-variable locations
         :return: dlp = 2D or 3D array with
             dlp[..., t, l] = d ln P{response = l | tau[..., :], theta[t]} / d th[t]
         """
        dlp = np.array([-sum(self.latent_class.d_log_cdf_diff(tau[..., l, None] - theta,
                                                             tau[..., l + 1, None] - theta))
                        for l in range(tau.shape[-1] - 1)])
        return np.moveaxis(dlp, 0, -1)

    def response_prob(self, tau, theta):
        """Probability-mass distribution over all possible responses
        for given parameters.
        :param tau: 1D or 2D array of all response thresholds, INCL. extremes at -inf, +inf
        :param theta: 1D array with hypothetical latent-variable locations
        :return: p = 2D or 3D array with
            p[..., t, l] = prob{l-th response | ...-th tau vector, t-th theta value}
        """
        return np.exp(self.log_response_prob(tau, theta))

    # def item_response_logprob(self, r, tau, theta):  # *** not needed ?
    #     """Log Probability of responses to ONE item, given parameters, summed across respondents
    #     :param r: 1D array with r[s] = ordinal response by s-th respondent to this item
    #         valid responses in range(L_i), missing response = -1
    #         L_i = number of response categories
    #         len(r) == theta.shape[1]
    #     :param tau: tau[n, :] = n-th sample of response interval limits
    #         INCL. all elements in [-inf, +inf]
    #         tau.shape[-1] == L_i + 1
    #     :param theta: theta[n, s, d] = n-th sample of d-th trait for s-th subject
    #         theta.shape[0] == tau.shape[0] == number of joint samples
    #         theta.shape[1] == len(r)
    #     :return: lp = 3D array with elements
    #         lp[n, s, d] = ln P(r[s] | tau[n, :], theta[n, s, d])
    #     """
    #     tau_low, tau_high = _response_interval(tau, r)
    #     a = tau_low[..., None] - theta
    #     b = tau_high[..., None] - theta
    #     # a[n, s, d] = n-th sample, s-th respondent, d-th trait; b[n, s, d] same
    #     return self.latent_class.log_cdf_diff(a, b)

    def item_sum_response_logprob(self, r, tau, theta):
        """Log Probability of responses to ONE item, given parameters,
        summed across all respondents
        :param r: 1D array with r[s] = ordinal response by s-th subject to this item
            valid responses in range(L_i), missing response = -1
            L_i = number of response categories
            len(r) == theta.shape[1]
        :param tau: 2D array with tau[n, :] = n-th sample of response interval limits
            INCL. all elements in [-inf, +inf]
            tau.shape[-1] == L_i + 1
        :param theta: 3D array with theta[n, s, d] = n-th sample of d-th trait for s-th subject
            theta.shape[0] == tau.shape[0] == number of joint samples
            theta.shape[1] == len(r)
        :return: lp = 2D array with elements
            lp[n, d] = sum_s ln P(r[s] | tau[n, :], theta[n, s, d])
        """
        tau_low, tau_high = _response_interval(tau, r)
        a = tau_low[..., None] - theta
        b = tau_high[..., None] - theta
        # a[n, s, d] = n-th sample, s-th respondent, d-th trait
        # b[n, s, d] similar
        return np.sum(self.latent_class.log_cdf_diff(a, b),
                      axis=1)

    def d_item_sum_response_logprob(self, r, tau, theta):
        """Gradients of item_sum_response_logprob w.r.t tau and theta, for ONE item
        :param r: 1D array with r[s] = ordinal response by s-th subject to this item
            valid responses in range(L_i), missing response = -1
            L_i = number of response categories
            len(r) == theta.shape[1]
        :param tau: tau[n, :] = n-th sample of response interval limits
            INCL. all elements in [-inf, +inf]
            tau.shape[-1] == L_i + 1
        :param theta: theta[n, s, d] = n-th sample of d-th trait for s-th subject
            theta.shape[0] == tau.shape[0] == number of joint samples
            theta.shape[1] == len(r)
        :return: tuple (dlp_tau, dlp_theta), with elements
            dlp_tau[n, k, d] = sum_s d ln P(r[s] | tau[n, :], theta[n, s, d]) / d tau[n, k]
            dlp_theta[n, s, d] = d ln P(r[s] | tau[n, :], theta[n, s, d]) / d theta[n, s, d]
            NOTE: dlp_tau[:, 0, :] == dlp_tau[:, -1, :] == 0.
        """
        tau_low, tau_high = _response_interval(tau, r)
        a = tau_low[..., None] - theta
        b = tau_high[..., None] - theta
        # a[n, s, d] = n-th sample, s-th respondent, d-th trait; b[n, s, d] same
        dll_da, dll_db = self.latent_class.d_log_cdf_diff(a, b)
        # dll_da[n, s, d] = d log P(r[s] | tau[n, :], theta[n, s, d]) / d a[n, s, d]
        # dll_db[n, s, d] = d log P(r[s] | tau[n, :], theta[n, s, d]) / d b[n, s, d]
        dll_tau = np.zeros(tau.shape + theta.shape[-1:])
        for l in range(1, tau.shape[-1] - 1):  # each internal threshold
            dll_tau[:, l, :] += np.sum(dll_da[:, r == l, :], axis=1)
            dll_tau[:, l, :] += np.sum(dll_db[:, r + 1 == l, :], axis=1)
        dll_theta = - dll_da - dll_db
        return dll_tau, dll_theta


# -------------------------------- help functions
def _response_interval(tau, r):
    """Get response interval for given thresholds and responses for ONE item
    :param tau: 2D array with threshold samples, as
        tau[m, l] = m-th sample of LOWER limit of l-th response interval,
            INCL extreme limits -inf, +inf
        tau.shape[-1] == L + 1, with L = number of response levels
    :param r: 1D array of response indices, with missing response = -1
        r[s] = response index for s-th subject in range(L)
        r[s] + 1 <= tau.shape[-1]
        except r[s] = -1 in case of missing response
    :return: tuple (tau_low, tau_high) with
        tau_low[m, s] = m-th sample of lower interval limit for r[s]
        tau_high[m, s] = m-th sample of upper interval limit for r[s]
        tau_low.shape == tau_high.shape
    """
    r = np.asarray(r)
    tau_low = tau[:, np.maximum(0, r)]  # = -inf for r[s] == 0 OR r[s] == -1
    tau_high = tau[:, r + 1]
    tau_high[:, r < 0] = np.inf  # for r[s] == -1
    return tau_low, tau_high


# -------------------------------------------------------- TEST:
if __name__ == '__main__':
    # Testing some module functions
    from ItemResponseCalc.ir_thresholds import ThresholdsFree
    from scipy.optimize import check_grad, approx_fprime

    print('*** Testing _rating_thresholds ***')
    n_categories = 5
    n_samples = 2
    thr = ThresholdsFree()
    n_eta = n_categories - 1
    eta = np.zeros((n_samples, n_eta))
    tau = thr.tau(eta)
    print('tau=\n', np.array_str(tau, precision=3))
    r = list(range(n_categories)) + [-1, 0]
    r = np.array(r)
    tau_low, tau_high = _response_interval(tau, r)
    print('_response_intervals=')
    for (t0, t1) in zip(tau_low.T, tau_high.T):
        print(f'[{t0[0]:.3f}, {t1[0]:.3f}]')

    print('\n*** Check gradients d_item_sum_response_logprob: ')
    grm = GradedResponse()

    n_subjects = len(r)
    n_traits = 3
    test_subject = 0    # subject index for test
    test_theta = 0  # trait index for test
    test_tau = 3    # tau index for test

    theta = np.zeros((n_samples, n_subjects, 1)) + np.arange(n_traits)

    def test_logprob_theta(y):
        # len(y) == n_subjects
        th = theta + y[:, None]
        return grm.item_sum_response_logprob(r, tau, th)[0, test_theta]

    def test_d_logprob_theta(y):
        th = theta + y[:, None]
        dll_dth = grm.d_item_sum_response_logprob(r, tau, th)[1]
        # dll_dth[n, s, d] = d item_sum_response_logprob(...)[n, d] / d th[n, s, d] for all d
        # *** BUT test_logprob_theta returned only d == test_theta
        return dll_dth[0, :, test_theta]

    def test_logprob_tau(y):
        t = np.concatenate(([-np.inf], y, [np.inf]))
        t = np.tile(t, (n_samples, 1))
        return grm.item_sum_response_logprob(r, t, theta)[0, test_theta]

    def test_d_logprob_tau(y):
        t = np.concatenate(([-np.inf], y, [np.inf]))
        t = np.tile(t, (n_samples, 1))
        dll_dt = grm.d_item_sum_response_logprob(r, t, theta)[0]
        return dll_dt[0, 1:-1, test_theta]
    # ------------------------------------

    print('tau=\n', np.array_str(tau, precision=3))
    print('theta=\n', np.array_str(theta, precision=3))
    print('item_sum_response_logprob(r, tau, theta)=',
          grm.item_sum_response_logprob(r, tau, theta))

    theta_y = np.zeros(n_subjects)
    for test_theta in range(n_traits):
        print(f'\n*** Testing d_logprob_theta with theta_y={theta_y} at trait no. {test_theta}')
        print(f'\ntest_logprob_theta(test_y) = {test_logprob_theta(theta_y)}')

        err = check_grad(test_logprob_theta, test_d_logprob_theta, theta_y)
        print('test_d_logprob_theta =', test_d_logprob_theta(theta_y))
        print('approx_grad = ', approx_fprime(theta_y,
                                              test_logprob_theta,
                                              epsilon=1e-6))
        print('check_grad err = ', err)

    for test_tau in range(tau.shape[-1] - 2):
        # tau_y = 0.4  # test value to adjust tau[:, test_tau]
        tau_y = tau[0, 1:-1]  # only internal thresholds
        tau_y[test_tau] += 0.4
        print(f'\n*** Testing d_logprob_tau with tau_y={tau_y} at threshold no. {test_tau}:')
        print(f'\ntest_logprob_tau(tau_y) = {test_logprob_tau(tau_y)}')

        err = check_grad(test_logprob_tau, test_d_logprob_tau, tau_y)
        print('test_d_logprob_tau =', test_d_logprob_tau(tau_y))
        print('approx_grad = ', approx_fprime(tau_y,
                                              test_logprob_tau,
                                              epsilon=1e-6))
        print('check_grad err = ', err)
