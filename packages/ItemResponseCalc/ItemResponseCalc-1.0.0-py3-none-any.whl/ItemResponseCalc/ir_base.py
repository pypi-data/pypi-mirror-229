"""General utility classes and functions for internal use.

Defines class
ItemResponseBase --- container for common properties
    specifying the indexing of separate types of model parameters, and
    calculating logprob for observed data, given tentative model parameters.


*** Version history:
* Version 1.0.0: New module for this version. Modified after EmaCalc.ema_base.
"""
import numpy as np
# from itertools import chain
# from collections import namedtuple
# from scipy.special import logit, expit
# from scipy.special import logsumexp, softmax
import logging
# import pandas as pd

from .ir_thresholds import ThresholdsFree, ThresholdsMidFixed


# ------------------------------------------------------
__version__ = "2023-07-20"

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # *** TEST

PRIOR_PSEUDO_RESPONDENT = 0.5  # seems to work OK
# = hyperprior total pseudo-count re ONE real respondent
# = prior GaussianRV.mean.learned_weight.
# This value is NOT critical for Occam's Razor behavior.

PRIOR_PARAM_SCALE = 1.
# = main hyperprior scale of most Gaussian model parameters,
# defined in LatentNormal d-prime (probit) units for attribute parameters,
# rescaled if the LatentLogistic (logistic) model is used for latent variables.

PRIOR_PREC_A = PRIOR_PSEUDO_RESPONDENT / 2
# = GaussianRV precision shape for ALL parameters

PRIOR_PREC_B = PRIOR_PARAM_SCALE**2 / 2
# = GaussianRV precision inv_scale for MOST model parameters
# -> allows very small precision <=> large inter-individual variance
# -> mode of global_pop component-element variance = PRIOR_PREC_B /(PRIOR_PREC_A + 1) approx= PRIOR_PREC_B


# ------------------------------------------------------- Help classes
class Slicer:
    """Help class to create consecutive slices for parts of parameter vector
    """
    def __init__(self, start=0):
        self.start = start

    def slice(self, length):
        """Create a new slice object tight after previous slice
        :param length: desired slice size
        :return: a slice object
        """
        stop = self.start + length
        sl = slice(self.start, stop)
        self.start = stop  # for next call
        return sl


# ------------------------------------------------------------------
class ItemResponseBase:
    """Container for common properties and methods for OrdinalItemResponseModel and its parts.

    Each individual parameter distribution is represented by
    a large set of samples, stored as property ir_group.ResponseGroup.xi, with
    xi[n, :] = n-th sample of (eta, theta) parameters for ONE GROUP of respondents.

    All model classes share mapping properties defined here,
    for extracting parameter subsets for item thresholds and individual traits
    from a xi array of parameter vectors.
    Parameter types are stored consecutively in order (eta, theta)
    """
    def __init__(self, rm_class, thr, eta_slices):  #, restrict_threshold):
        """
        :param rm_class: response model class, e.g., ir_graded_response_prob.GradedResponse,
            calculating log probability of any response given model parameters
        :param thr: class defining threshold calculations, defined in module ir_thresholds,
        :param eta_slices: list of slice objects, such that
            eta_i = xi[:, eta_slices[i]] = array of thresholds for i-th item, by
            tau_i = self.thr.tau(eta_i)
        """
        self.rm_class = rm_class
        self.thr = thr
        self.eta_slices = eta_slices
        # self.restrict_threshold = restrict_threshold  # not needed ?

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                '\n\t'.join(f'{k}= {repr(v)},'
                            for (k, v) in self.__dict__.items()) +
                '\n\t)')

    @classmethod
    def initialize(cls, ir_count, restrict_threshold, rm_class):
        """Assign all parameter-extraction slices, and
        :param ir_count: list of 1D arrays with response counts
            ir_count[i][l] = number of l-th ordinal responses to i-th item
            *** need only sizes, not actual counts ***
        :param restrict_threshold: boolean switch
            to force restriction on response-threshold locations
        :param rm_class: response model class, e.g., ir_graded_response_prob.GradedResponse,
            calculating log probability of any response given model parameters
        :return: a cls instance

        Result: all properties initialized
        NOTE: xi parameter slices in order: all alpha, all beta, all eta
        """
        if restrict_threshold:
            thr = ThresholdsMidFixed
        else:
            thr = ThresholdsFree
        # Number of eta parameters depends on class thr

        slice_gen = Slicer()  # creating adjacent slice objects
        eta_slices = [slice_gen.slice(thr.n_param(len(count_i)))
                      for count_i in ir_count]
        # = list of slice objects, such that
        # eta_i = xi[:, eta_slices[i]] = array defining thresholds for i-th item, by
        # tau_i = self.thr.tau(eta_i)

        # **** allow tied thresholds for several items, like EmaCalc ??? ************
        # tied_scales = None
        # if len(attribute_slices) > len(unique_slices):
        #     attribute_keys = list(emf.attribute_scales.keys())
        #     tied_scales = [[attribute_keys.index(a_key) for a_key in a_keys]
        #                    for a_keys in emf.scale_attributes.values()]
        # tied_scales[s] = list of attribute indices a_i, such that
        # attribute_slices[a_i].eta_slice is eta_slices[s],
        # allowing same eta parameters to be used for more than one attribute

        return cls(rm_class,
                   thr,
                   eta_slices)

    @property
    def eta_all_slice(self):
        return slice(self.eta_slices[0].start, self.eta_slices[-1].stop)

    @property
    def theta_slice(self):
        """All remaining elements are theta
        """
        return slice(self.eta_slices[-1].stop, None)

    def n_eta(self):
        """Total number of eta parameters in model
        :return: scalar
        """
        return self.eta_slices[-1].stop

    def eta_all(self, xi):
        """Extract all threshold-defining parameters eta from given sample array
        :param xi: 2D array of (eta, theta) samples
        :return: 2D array of eta samples
        """
        return xi[:, self.eta_all_slice]

    def theta(self, xi, n_subjects):
        """Extract all theta parameters from given sample array
        :param xi: 2D array of (eta, theta) samples
        :param n_subjects: scalar number of respondents included in xi[:, self.theta_slice
        :return: 3D array of theta samples
            theta[n, s, d] = n-th sample of d-th trait for s-th respondent
        """
        n_samples = xi.shape[0]
        return xi[:, self.theta_slice].reshape((n_samples, n_subjects, -1))

    def tau(self, xi):
        """Extract threshold vectors for all items
        :param xi: 1D or 2D array of (eta, theta) samples
        :return: list of threshold samples tau_i, INCL extreme -inf, +inf
            tau_i[n, l] = n-th sample of l-th threshold for
        """
        return [self.thr.tau(xi[..., i])
                for i in self.eta_slices]

    # ---------------------- methods for logprob calculation:
    def item_response_logprob(self, r, eta, theta):
        """Rating logprob, given parameter values
        :param r: array of integer-coded responses
            r[i, s] = ordinal response to i-th item by s-th respondent
        :param eta: 2D array of tentative threshold-defining parameters, same for all respondents
            eta[n, self.eta_slice[i]] = n-th sample of eta for i-th item
        :param theta: 3D array of tentative trait values
            theta[n, s, d] = n-th sample of d-th trait for s-th respondent
            eta.shape[0] == theta.shape[0] == n_samples, joint for (eta, theta)
            theta.shape[1] == r.shape[1] == number of respondents
        :return: lp = 3D array, with elements
            lp[i, n, d] = sum_s log P(r[i, s] | eta_i[n, :], theta[n, s, d]
        """
        return np.array([self.rm_class.item_sum_response_logprob(r_i,
                                                                 self.thr.tau(eta[:, i]),
                                                                 theta)
                         for (i, r_i) in zip(self.eta_slices, r)])

    def response_logprob(self, r, eta, theta, weight):
        """Rating logprob given tentative parameter values, weighted by item-by-trait prob.
        Help method for group model learning.
        :param r: array of integer-coded responses
            r[i, s] = ordinal response to i-th item by s-th respondent
        :param eta: 2D array of tentative threshold-defining parameters for all items,
            eta[n, self.eta_slice[i]] = n-th sample of eta for i-th item
        :param theta: 3D array of tentative trait values
            theta[n, s, d] = n-th sample of d-th trait for s-th respondent
            eta.shape[0] == theta.shape[0] == n_samples (jointly sampled)
            theta.shape[1] == responses.shape[1]
        :param weight: array with item-trait mapping
            weight[i, d] = prob that response to i-th item is determined by d-th trait
        :return: ll = 1D array
            ll[n] = sum_{i, s} log P{r[i, s] | xi[n, :]}
            ll.shape == xi.shape[:-1]
        """
        return np.sum(self.item_response_logprob(r, eta, theta) * weight[:, None, :],
                      axis=(0, 2))

    def d_response_logprob(self, r, eta, theta, weight):
        """Gradients of rating_logprob(...)
        :param eta: 2D array of tentative threshold-defining parameters for all items,
            eta[n, self.eta_slice[i]] = n-th sample of eta for i-th item
        :param theta: 3D array of tentative trait values
            theta[n, s, d] = n-th sample of d-th trait for s-th respondent
            eta.shape[0] == theta.shape[0] == n_samples (joint)
        :param r: array of integer-coded responses
            r[i, s] = ordinal response to i-th item by s-th respondent
            theta.shape[1] == responses.shape[1]
        :param weight: array with item-trait mapping
            weight[i, d] = prob that response to i-th item determined by d-th trait
        :return: d_ll = 2D array with elements
            d_ll[n, k] = d response_logprob(r, eta, theta, weight)[n] / d xi[n, k]
            d_ll.shape == self.xi.shape
            such that
            d_ll[n, k] = d response_logprob(r, eta, theta, weight)[n] / d eta[n, k]; k in self.eta_slice_all
            d_ll[n, k] = d response_logprob(r, eta, theta, weight)[n] / d theta[n, sk]; sk in self.theta_slice_all
        """
        dll = [self.rm_class.d_item_sum_response_logprob(r_i, self.thr.tau(eta[:, i]), theta)
               for (i, r_i) in zip(self.eta_slices, r)]
        # dll[i][0][n, k, d] = d item_response_logprob(r_i, tau_i[n, k], theta[n,..., d)[n, d] / d tau_i[n, k]
        # dll[i][1][n, s, d] = d item_response_logprob(r_i, ...)[n, d] / d theta[n, s, d] )
        dll_tau = [np.dot(dll_i[0], w_i)
                   for (dll_i, w_i) in zip(dll, weight)]
        # dll_tau[i][n, l] = d response_logprob(r[i] | tau_i[n], theta[n]) / d tau_i[n, l]
        # dll_eta_test = [np.einsum('nl, nlj -> nj',
        #                           dll_i, self.thr.d_tau(eta[:, i]))
        #                 for (dll_i, i) in zip(dll_tau, self.eta_slices)]
        dll_eta = [np.sum(dll_i[..., None] * self.thr.d_tau(eta[:, i]), axis=1)
                   for (dll_i, i) in zip(dll_tau, self.eta_slices)]
        # dll_eta[i][n, k] = d response_logprob(r[i] | tau_i[n], theta[n]) / d eta[n, k]
        dll_theta = sum(dll_i[1] * w_i
                        for (dll_i, w_i) in zip(dll, weight))  # sum across items
        # dll_theta[n, s, d] = sum_i d item_response_logprob(r_i, tau_i, theta[n, s, d) / d theta[n, s, d] )
        n_samples = dll_theta.shape[0]
        return np.concatenate(dll_eta + [dll_theta.reshape((n_samples, -1))],
                              axis=-1)


# ------------------------------------------------- TEST:
