"""This module implements a Bayesian model of subjects' responses
to items in a questionnaire, using Item Response Theory (IRT).

The present version allows two variants of IRT models for ordinal data:
ir_graded_response_prob.GradedResponse(latent_class),
    with latent_class = either ir_latent.LatentLogistic (default) or .LatentNormal

A future version may implement the Partial Credits model as well.

NOTE: To make the model identifiable, some restriction is necessary.
The zero point on the trait and threshold scale is otherwise arbitrary,
if both latent-variable locations and response thresholds are freely variable.

This behavior is user-controlled by initialization arguments
restrict_trait and restrict_threshold.
The variance of response thresholds among groups is also restricted
by an informtive prior that may be user-controlled by
argument threshold_pseudo_factor to initialize method.

The model is also slightly restricted by a weakly informative global_pop_prior,
for numerical stability in case of extreme response patterns,
e.g., aLL ratings in the highest ordinal category.


*** Main Classes:

OrdinalItemResponseModel, defining a complete Bayesian model with all parameters
    adapted to a data set with individual responses to each item in a questionnaire.
    obtained from subjects in one or more different groups.

*** Usage Example: see template script run_irt.py

*** Reference:
* For Version 1.0.0:
Leijon: Analysis of Ordinal Response Data using Bayesian Item Response Theory package ItemResponseCalc.
Technical report, 2023.

* For Version <= 0.6:
Leijon, Kramer et al.:
Analysis of Data from the International Outcome Inventory for Hearing Aids (IOI-HA)
using Bayesian Item Response Theory. 2020, Int J Audiol.
doi: 10.1080/14992027.2020.1813338

** Version history:
* Version 1.0.0:  new model structure, joint distribution of thresholds and traits within each group
2023-08-30, minor cleanup, final testing
2023-08-12, first function version tested

* Version 0.6.0:
2023-07-12, predictive_individual_cov uses only precision_within if only one group
            (because precision_among is then undefined = NaN).

* Version 0.5.0:
2020-06-13, change internal names scales -> items for clarity
2020-06-15, internal changes to allow choice of response_prob models

2019-07-08, first functional version
2019-07-23, set Initial Trait Scale only here,
    for use by both item_scale and item_respondent initialization
2019-08-15, trying new initialization method, no boolean item_trait_map input
2019-08-16, max_hours limit for learn
2019-08-21, using Pool multiprocessing for learn
"""
# *** initialize with n_traits == n_items, then let learning concentrate TraitProb to fewer traits,
#   and prune when possible, during learning, OR after completed learning ?
#
# **** allow string item_id ? ***
# **** allow string trait_id ? ***
# **** allow tied thresholds across several items, like EmaCalc ??? ***

import numpy as np
import datetime as dt
from copy import deepcopy
from collections import Counter
import pandas as pd

from .ir_base import ItemResponseBase
from .ir_global import ItemResponseGlobal
from .ir_group import ResponseGroup
from .item_trait_selector import TraitProb, TraitSelector
from .ir_graded_response_prob import GradedResponse
from .ir_latent import LatentLogistic

# from .ir_group import logger as group_logger
# *** Does NOT work in multiprocessing.Pool child process

from multiprocessing.pool import Pool
import os

import logging

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # test

# ----------------------------------------------
__version__ = '2023-09-06'

INITIAL_TRAIT_SCALE = 3.  # larger?
# = crude assumed initial scale of model trait values
THRESHOLD_PSEUDO_FACTOR = 1.
# default: global pseudo_groups = THRESHOLD_PSEUDO_FACTOR * number of included groups
# controls prior between-population variability of threshold parameters
# ----------------------------------------------

usePool = True
# usePool = False # for TEST


def _pool_size(n):
    """Estimate number of Pool sub-processes
    :param n: total number of independent jobs to share between processes
    :return: n_processes
    """
    # NOTE: cpu_count() returns n of LOGICAL cpu cores.
    return min(os.cpu_count(), n)


# ---------------------------------------------- Main class:
class OrdinalItemResponseModel:
    """A Bayesian IRT model for discrete ORDINAL rating data,
    available as INDIVIDUAL results in a 2D array R with elements
    R[s, i] = ordinal integer-coded response by s-th subject to the i-th item.

    The number of response alternatives may differ among items.
    The i-th item has L_i ordinal response values.

    NOTE: In most modules of this package,
    the math notation assumes that R[s, i] is an integer in range(L_i),
    i.e., it can have integer values 0, 1,..., L_i-1.

    However, in some input data files,
    the recorded responses may be conventionally coded as values 1, 2,..., L_i,
    with missing values encoded as zero.

    All model parameters are treated as random variables.
    The main parameter distributions are represented by equally probable samples.

    This package uses the Graded Response Model (Samejima, 1969, 1997):
    Each rating R_si is determined by ONE latent random Trait variable
    Y_st = a real-valued random variable in the range (-inf, inf).
    There may be one or more separate trait variables,
    each determining the responses to one or more items.

    IFF the i-th item is associated with the t-th trait,
    the latent variable Y_st is assumed to determine the response R_si as
    tau_{i, l} < Y_st <= tau_{i, l+1} => R_si = l,
    where the response thresholds are defined in
    an array (tau_k0, ..., tau_kL) with strictly increasing elements, and
    tau_k0 = -inf; tau_kL = +inf

    The latent random variable Y_st has a logistic (or normal) distribution,
    with location theta_st = a subject-specific TRAIT variable,
    for the t-th trait of the s-th subject.

    The trait location theta_st is
    the individual performance measures to be estimated.

    The response thresholds are determined by a mapping function
    tau_i(eta_i), where eta_i is a 1D parameter vector for the i-th item.

    The thresholds may be either FREE, or RESTRICTED,
    as specified by boolean initialization argument restrict_threshold.
    If restrict_threshold == False, all (L_i - 1) finite thresholds are free parameters.
    If restrict_threshold == True, ONE middle threshold is fixed at zero,
    so there are only (L_i - 2) free threshold values.
    Thus, the parameter vector eta_i has either (L_i - 1) or (L_i - 2) elements.

    Each item response is modelled as determined by ONE trait variable,
    identified by an item_trait_selector.TraitSelector object.
    The association between traits and items is automatically
    estimated by the learning procedure.

    The model is implemented by main properties
    response_prob = an object defining core response probabilities,
        given item-specific and subject-specific sets of parameters.
        The present version allows only ONE response_prob class:
        ir_graded_response_prob.GradedResponse, (using logistic or normal distribution).
        (The Partial Credits response model may be added in a future version.)
    global_pop_prior = an ir_global.ItemResponseGlobal instance,
        kept constant during learning, used as prior for global_pop.
    global_pop = an ir_global.ItemResponseGlobal instance,
        defining learned overall distribution of parameters common for all groups.
    groups = a list with one item_respondents.RespondentGroup instance for each group of subjects.
        The group object includes all recorded responses for all respondents in that group,
        AND models the distribution of individual traits for those respondents,
        AND models the distribution of traits for a RANDOM INDIVIDUAL
            in the (sub)population from which the group respondents were recruited,
        AND models the distribution of MEAN traits in this (sub)population.
    item_trait_sel = a list of TraitSelector objects, one for each item,
        defining the association between the item and the individual traits
    trait_prob = an item_trait_selector.TraitProb object,
        representing the overall probability for each trait to be used for ANY item.
    """
    # --------------------------------------------------------------------
    def __init__(self, response_prob, questionnaire, base,
                 global_pop_prior, global_pop,
                 groups, item_trait_sel, trait_prob):
        """
        :param response_prob: object that calculates log probability for any response
        :param questionnaire: Questionnaire object with info about the items **** needed here ? ********
        :param base: ir_base.ItemResponseBase object defining indexing of model parameters
        :param global_pop_prior: ir_global.ItemResponseGlobal object used as prior for global_pop
        :param global_pop: ir_global.ItemResponseGlobal object defining global_pop model parameters,
            used as prior for distributions of group-specific parameters across groups
        :param groups: list with item_respondents.ResponseGroup elements
        :param item_trait_sel: list of item_trait_selector.TraitSelector instances, one for each item
        :param trait_prob: single TraitProb object, global_pop for all TraitSelector objects
        """
        self.version = __version__
        self.response_prob = response_prob
        self.questionnaire = questionnaire
        self.base = base
        self.global_pop_prior = global_pop_prior
        self.global_pop = global_pop
        self.groups = groups
        self.item_trait_sel = item_trait_sel
        self.trait_prob = trait_prob
        self.log_prob = []

    def __repr__(self):
        return (self.__class__.__name__
                + '(response_prob= ' + repr(self.response_prob) + ','
                + f'\n\t questionnaire= {self.questionnaire.__class__.__name__} '
                + f'object with {self.questionnaire.n_items} items,'
                + f'\n\t base= {self.base.__class__.__name__} '
                + f'\n\t global_pop_prior= {self.global_pop_prior.__class__.__name__} '
                + f'\n\t global_pop= {self.global_pop.__class__.__name__} '
                + '\n\t groups= [\n\t\t'
                + ',\n\t\t'.join(f'{g.__class__.__name__}(name={repr(g.name)}, with {g.n_subjects} respondents)'
                                 for g in self.groups) + '],'
                + f'\n\t item_trait_sel= [{len(self.item_trait_sel)} TraitSelector objects],'
                + f'mapping items to {self.n_traits} latent traits, '
                + f'\n\t trait_prob = {self.trait_prob.__class__.__name__} object, '
                + f'\n\t version= {self.version}'
                + ')')

    @classmethod
    def initialize(cls, data_set,
                   response_prob=None,
                   latent_class=LatentLogistic,
                   n_traits=None,
                   n_samples=50,
                   restrict_traits=True,
                   restrict_threshold=False,
                   trait_scale=INITIAL_TRAIT_SCALE,
                   threshold_pseudo_factor=THRESHOLD_PSEUDO_FACTOR):
        """Initialize a model crudely from given item response data.
        :param data_set: a single ItemResponseDataSet instance,
            including response data from one or more groups of subjects.
        :param response_prob: (optional) object to calculate response probabilities,
            either GradedResponse, (or PartialCredits **** future)
        :param latent_class: (optional) class of latent variable distribution,
            = ir_latent.LatentLogistic or .LatentNormal (only for GradedResponse)
        :param n_traits: (optional) scalar integer max number of effective latent traits
        :param n_samples: (optional) number of samples of parameters (eta, theta) for each group
        :param restrict_traits: (optional) boolean switch;
            True -> global_pop mean trait fixed at zero.
        :param restrict_threshold: (optional) boolean switch;
            True -> one mid threshold fixed at zero.
        :param trait_scale: (optional) scalar initially assumed scale of model trait values
        :param threshold_pseudo_factor: (optional) scalar to define
            pseudo_groups = threshold_pseudo_factor * n_groups
        :return: a cls instance, crudely initialized for given data_source
            to be refined later, by method learn

        Method:
        0: Initialize base = ir_base.ItemResponseBase with indexing scheme, depending on restrict_threshold
        1.1: Initialize global_pop_prior = weakly informative ir_global.ItemResponseGlobal object,
        1.2: Initialize global_pop = copy of global_pop_prior, EXCEPT threshold parameters
            adjusted to informative values, using total item response counts for all items
        2.1: Initialize all group models with individual response data, for traits == items, 
            with sampled individual theta, using initialized thresholds from global_pop.eta_mean
        2.2: Use PCA on these item-specific crude trait samples
        2.3: Transform all item-specific traits to a (sub)space with n_traits dimensions <= n_items.
        """
        n_groups = len(data_set.groups)
        assert n_groups > 0, 'Must have at least one group'
        if response_prob is None:
            response_prob = GradedResponse(latent_class)
        item_response_count = data_set.item_response_count()
        # item_response_count[i] = 1D array of response counts for i-th item, sum across all groups
        # len(item_response_count[i]) = L_i = number of ordinal response alternatives
        n_items = len(item_response_count)
        if n_traits is None:
            n_traits = n_items
        # ---- Create all model components:
        logger.info(f'Initializing model with restrict_traits={restrict_traits}, '
                    + f'restrict_threshold={restrict_threshold}, '
                    + f'threshold_pseudo_factor={threshold_pseudo_factor}.')
        base = ItemResponseBase.initialize(item_response_count, restrict_threshold, response_prob)
        # = object defining indexing scheme for (eta, theta), and some common logprob methods.
        global_pop_prior = ItemResponseGlobal.initialize(base.n_eta(),
                                                         n_traits,
                                                         restrict_traits,
                                                         pseudo_groups=threshold_pseudo_factor * n_groups)
        # = top hierarchical prior for global population model
        global_pop = deepcopy(global_pop_prior)
        # = global population model for (eta, theta) distributions,
        #   used as prior for all included (sub)populations / groups
        global_pop.set_start(item_response_count, base,
                             trait_scale=trait_scale)
        # = crudely modified, to be suitable to start the VI learning procedure
        trait_prob = TraitProb.initialize(n_traits)
        logger.debug(f'Prior TraitProb.alpha = {np.array2string(trait_prob.alpha, precision=4)}')
        trait_sel = [TraitSelector.initialize(n_traits) for _ in range(n_items)]
        # = objects defining item-trait mapping
        # *** put trait_prob and all trait_sel into ONE single class instance ? **********

        # ----------------------------------------- initialize groups with subjects
        groups = [ResponseGroup.initialize_by_item(responses=g_responses,
                                                   trait_scale=trait_scale,
                                                   base=base,
                                                   item_trait_sel=trait_sel,
                                                   global_pop=global_pop,
                                                   name=g_name,
                                                   n_samples=n_samples)
                  for (g_name, g_responses) in data_set.groups.items()]
        # groups[g] = object containing individual response data for each item,
        #   AND a trait-distribution model for the (sub)population represented by the group of respondents,
        #   initially with mapping ONE item <-> ONE trait, i.e., n_traits == n_items
        trait_cov = np.sum(g.cov_theta()
                           for g in groups)
        transform_matrix = _trait_rotation(trait_cov, n_traits)
        # to project trait locations to subspace with n_traits dimensions <= n_items
        # such that transformed traits are approximately uncorrelated.
        # *** Without transform_traits, the model never gets sparse, so each item <-> one trait. ***
        for g in groups:
            g.transform_traits(transform_matrix)
        # now all model components are ready to start VI learning
        # *** BUT this initial setting -> perhaps too hard initial item_trait_sel.prob
        # *** does not change during learning. Use a PCA model for traits instead?
        return cls(response_prob,
                   data_set.questionnaire,
                   base,
                   global_pop_prior,
                   global_pop,
                   groups,
                   trait_sel,
                   trait_prob)

    @property
    def n_groups(self):
        return len(self.groups)

    @property
    def n_subjects(self):
        return sum(g.n_subjects for g in self.groups)

    @property
    def n_items(self):
        return len(self.item_trait_sel)

    @property
    def n_traits(self):
        return len(self.trait_prob.mean)

    def item_labels(self):  # *** get from questionnaire if defined there ***
        return [f'Q{i+1}' for i in range(self.n_items)]

    # def trait_labels(self):  # ********* ?

    # ------------------------------------------ General VI learn algorithm:
    def learn(self,
              min_iter=10,
              min_step=0.01,
              max_iter=500,
              max_hours=1.,
              max_minutes=0.,
              callback=None):
        """Learn from all observed response data stored in self.groups,
        using Variational Inference (VI).

        This method adapts sampled distributions for all model parameters
        to maximize a lower bound to the total likelihood of the observed data.
        The resulting sequence of lower-bound values is theoretically guaranteed to be non-decreasing,
        but the sampling variability may cause small variations around the non-decreasing trend.
        :param min_iter: (optional) minimum number of learning iterations
        :param min_step: (optional) minimum data log-likelihood improvement,
                 over the latest min_iter iterations,
                 for learning iterations to continue.
        :param max_iter: (optional) maximum number of iterations, regardless of result.
        :param max_hours = (optional) maximal allowed running time, regardless of result.
        :param max_minutes = (optional) maximal allowed running time, regardless of result.
        :param callback: (optional) function to be called after each iteration step.
            If callable, called as callback(self, log_prob)
            where log_prob == scalar last achieved value of VI lower bound
        :return: log_prob = list of log-likelihood values, one for each iteration.
        Result: updated properties of self
        """
        if max_hours == 0. and max_minutes == 0.:
            max_minutes = 30.
        logger.info('Learning the model. Might take some time! '
                    + f'Max {max_hours:.0f} hours + {max_minutes:.0f} minutes.')
        min_iter = np.max([min_iter, 1])
        end_time = dt.datetime.now() + dt.timedelta(hours=max_hours)
        # last allowed time to start new VI iteration
        log_prob = []
        while (len(log_prob) <= min_iter
               or (log_prob[-1] - log_prob[-1 - min_iter] > min_step
                   and (len(log_prob) < max_iter)
                   and (dt.datetime.now() < end_time))):
            log_prob.append(self.adapt())
            if callable(callback):
                callback(self, log_prob[-1])
            logger.info(f'Done {len(log_prob)} iterations. LL={log_prob[-1]:.1f}')
        self.log_prob = np.array(log_prob)
        if dt.datetime.now() >= end_time:
            logger.warning('Learning stopped at time limit, possibly not yet converged')
        if len(log_prob) >= max_iter:
            logger.warning('Learning stopped at max iterations, possibly not yet converged')
        return self.log_prob

    def adapt(self):
        """One adaptation step for all parameters
        using all response data stored in self.groups.
        :return: ll = scalar lower bound to data log-likelihood,
            incl. negative contributions for KLdiv re priors
        """
        ll_items = self._adapt_items()
        ll_global = self.global_pop.adapt(self.groups, self.global_pop_prior)
        if logger.isEnabledFor(logging.DEBUG):
            global_eta_var = self.global_pop.eta.prec.mean_inv
            item_eta_var = [global_eta_var[i]
                            for i in self.base.eta_slices]
            logger.debug('\n' + '\n'.join(f'Item {i+1} tau_mean = '
                                          + np.array_str(tau_i[1:-1],
                                                         precision=3,
                                                         suppress_small=True)
                                          + f'; Item eta variance = '
                                          + np.array_str(eta_var_i,
                                                         precision=3,
                                                         suppress_small=True)
                                          for (i, (tau_i, eta_var_i)) in enumerate(zip(self.item_thresholds_global(),
                                                                                       item_eta_var))
                                          )
                         )
        ll_groups = self._adapt_groups()
        # *** should be done in this order,
        # because item_trait_sel are used in global_pop update
        # and global_pop and items are used in groups update.
        # All KLdiv calculations must use SAME distributions
        # i.e., the current value AFTER adaptations.
        logger.debug(f'll_items={ll_items}; ll_global={ll_global}; ll_groups={ll_groups}')
        return ll_items + ll_global + ll_groups

    def _adapt_items(self):
        """One adaptation step for all item parameters
        using all response data stored in self.groups.
        :return: ll = scalar lower bound to data log-likelihood
        """
        ll = 0.
        log_resp = np.sum(g.item_trait_logprob()
                          for g in self.groups)
        logger.debug('item_trait_sel log_resp=\n' + np.array_str(log_resp,
                                                             precision=3,
                                                             suppress_small=True))
        for (item_sel, lr) in zip(self.item_trait_sel, log_resp):
            ll += item_sel.adapt(lr, self.trait_prob)
        ll += self.trait_prob.adapt(self.item_trait_sel)
        i_t_prob = np.array([i.mean for i in self.item_trait_sel])
        logger.debug('item_trait_sel.mean=\n' + np.array_str(i_t_prob,
                                                             precision=3,
                                                             suppress_small=True))
        return ll

    def _adapt_groups(self):
        """One adaptation step for all parameters
        using all response data stored in self.groups.
        :return: ll = scalar lower bound to data log-likelihood
        """
        # logger.info(f'_adapt_groups: id(logger)={id(logger)}; id(group_logger)={id(group_logger)}')
        # adapt_args = (group_logger,)  # *** pass logger as arg to group.adapt? NO does not work!
        adapt_args = ()
        if usePool and self.n_groups > 1:
            n_pool = _pool_size(self.n_groups)
            ch_size = 1
            logger.debug(f'_adapt_groups Pool: n_pool= {n_pool}, ch_size= {ch_size}')
            with Pool(n_pool) as p:
                self.groups = list(p.imap(_adapt, ((g, adapt_args)
                                                   for g in self.groups),
                                          chunksize=ch_size))
        else:
            logger.debug(f'_adapt_groups map, NoPool')
            self.groups = list(map(_adapt, ((g, adapt_args)
                                            for g in self.groups)))
        for g in self.groups:
            logger.debug(f'group {repr(g.name)}: pop_theta.mu.loc= '
                         + np.array2string(g.pop_theta.mu.loc,
                                           precision=3, suppress_small=True)
                         + f'; ll={g.ll:.2f}')
            # ***** must restore all group refs to original base and global params after work in pool copies
            g.base = self.base
            g.global_pop = self.global_pop
            g.item_trait_sel = self.item_trait_sel
        return sum(g.ll for g in self.groups)

    # ------------------------------------------------------- Result Display Functions:
    def item_thresholds_global(self):
        """Global mean thresholds for all items
        :return: list with elements
            tau_i = 1D array of thresholds INCL. extremes at +-inf
        """
        return self.base.tau(self.global_pop.eta.mu.mean)

    def item_thresholds(self, item='Item', response='Response', sample='Sample'):
        """Response thresholds for all items and all groups
        :param item: index name for items in result
        :param response: index name for response category
        :param sample: index name for sample
        :return: pd.DataFrame with thresholds in one column for each group, and
            one row for each (item, sample, response)
            Thresholds are UPPER interval limits for each ordinal response
            EXCL. extremes at +-inf,
            i.e., number of thresholds = n_categories - 1 for each item.

            Sample values are RELATED across items and responses,
            but UNRELATED among groups.
        """
        def tau_group_item(t):
            """Make thresholds DataFrame for ONE item for ONE group
            :param t: 2D threshold array
                t[n, l] = n-th sample of l-th threshold for i-th item
            :return: pd.Series with index labels ('sample', 'Response')
            """
            ind = pd.MultiIndex.from_product([np.arange(t.shape[0]),
                                              np.arange(t.shape[1])],
                                             names=[sample, response])
            return pd.Series(t.reshape((-1,)), index=ind)
        # -----------------------------------------------------------------
        tau_g = {g.name: pd.concat([tau_group_item(tau_gi[:, 1:-1])
                                    for tau_gi in self.base.tau(g.xi)],
                                   keys=self.item_labels(),
                                   names=[item])
                 for g in self.groups}
        return pd.DataFrame.from_dict(tau_g)

    def item_trait_map(self):
        """Mapping with exactly ONE trait corresponding to each item
        :return: itp = 2D boolean array
            itp[i, t] == True <=> i-th item responses were most probably determined by t-th trait
        """
        return np.array([sc.bool for sc in self.item_trait_sel])

    def prune(self):
        """Reduce model complexity by deleting any latent trait variables
        that did not correspond to any item
        :return: None
        Result: modified internal model properties
        """
        it_map = self.item_trait_map()
        keep = np.any(it_map, axis=0)
        logger.info(f'Pruning model to {sum(keep)} active traits out of {len(keep)} initially allowed.')
        self.trait_prob.prune(keep)
        self.global_pop.prune(keep)
        for sc in self.item_trait_sel:
            sc.prune(keep)
        for g in self.groups:
            g.prune(keep)

    # ------------------------------------------------------ Raw Descriptive Data:
    def item_response_count(self):
        """Total frequency of responses at each ordinal level, for each item,
        by subjects in each included group.
        :return: dict with elements (group_key, g_count), where
            g_count is a list of collections.Counter objects,
            g_count[i][r] = number of responses == r for i-th item,
            with r==0 indicating missing response, and
            r = 1, ..., L_i are actual responses.
            *** change to origin-zero response indices ?
        """
        return {g.name: [Counter(sr_i)
                         for sr_i in g.subject_responses]
                for g in self.groups}

    # ------------------------------------------------------ Predictive Models:
    def theta_range(self):
        """Major range of learned theta values across all items and populations,
        suitable for result plots
        :return: tuple (theta_min, theta_max)
        """
        tau = self.item_thresholds_global()
        tau_min = min(tau_i[1] for tau_i in tau)
        tau_max = max(tau_i[-2] for tau_i in tau)
        latent_scale = self.base.rm_class.latent_class.scale
        return tau_min - latent_scale, tau_max + latent_scale

    def item_response_prob(self, th):
        """Prob of any response category as a function of latent trait
        :param th: 1D array with hypothetical trait values (to be used for plots)
        :return: p = list with estimated probability distributions,
            p[i] = 2D array with response probabilities
            p[i][n, l] = P{l-th response | t[n]} for i-th item
            *** return dict with (item_id, item_prob) instead ?
        """
        def response_prob(tau_i):
            """Response probability mass distributions for ONE item
            :param tau_i: 2D array with
                tau_i[n, l] = n-th sample of lower threshold for l-th response for i-th item
            :return: p_i = 2D array for this item
                p[t, l] = prob. of l-th response, given th[t]
            """
            return np.mean(self.base.rm_class.response_prob(tau_i, th),
                           axis=0)  # mean across samples
        # ----------------------------------------------------------------
        eta = np.concatenate([g.eta for g in self.groups], axis=0)
        # = samples of learned eta distribution for all groups / populations, all items
        return [response_prob(tau_i)
                for tau_i in self.base.tau(eta)]

    def item_fisher_information(self, th):
        """Fisher information for all items, as a function of trait values.
        Conventionally plotted as "Item Information Curves" in IRT / Rasch analysis,
        but it is less interesting in the Bayesian framework,
        that automatically generates a measure of the uncertainty.

        Cramer-Rao inequality:
        The variance of an unbiased POINT estimate of a trait  >= 1 / Fisher Information,
        possibly with equality in some simple cases.

        Fisher information is ADDITIVE across items, because
        item responses are assumed conditionally independent, given the latent trait.
        :param th: array of trait values
        :return: F = 2D array with estimated information functions,
            F[i] = 1D array with Fisher information values for given theta
            p[i, n] = Fisher info when th[n] is the TRUE latent trait value.
        """
        def fisher(tau_i):
            """Calculate Fisher info for ONE item
            :param tau_i: 2D array with
                tau_i[m, l] = m-th sample of lower threshold for l-th response for this item
            :return: F_i = 1D array with
                F_i[n] = Fisher info for this item given th[n]
            """
            p = self.base.rm_class.response_prob(tau_i, th)
            # p[m, n, l] = P{Response = l | tau_i[m], th[n]}
            d_lp_dth = self.base.rm_class.d_log_response_prob_d_theta(tau_i, th)
            # d_lp_dth[m, n, l] = partial derivative d ln p[m, n, l] / d th[n]
            return np.mean(np.sum(p * d_lp_dth**2, axis=-1),
                           axis=0)
        # ------------------------------------------------------------
        eta = np.concatenate([g.eta for g in self.groups], axis=0)
        # eta[m] = m-th sample of learned eta array for all groups / populations, all items
        return np.array([fisher(tau_i)
                         for tau_i in self.base.tau(eta)])

    def instrument_mutual_information(self):
        """Mutual Information I(R, Theta)
        between observed response(s) R and latent Trait(s) Theta,
        showing the average amount of information (in bits) about the trait(s) of a RANDOM INDIVIDUAL,
        that is gained from a single record of responses to the given Questionnaire Instrument.

        Quantifies the ability of the Instrument to classify an individual
        into one of several possible categories, i.e.,
        similar to the Person Separation Index (PSI) in the IRT / Rasch tradition.
        Also related to the conventional Reliability measure
        defined as True_population_variance / Total_measure_variance in range (0, 1.),
        where Total_measure_variance = True_population_variance + Error_variance.
        :return: scalar mutual information (in bits) for ONE response record from the instrument
            by ONE random individual from any population included in the model.
            I(R, Theta) = h(Theta) - h(Theta | R), where
            h(X) = - E{log_2 pdf(X)} is differential entropy of a continuous random variable X

        Method:
        h(Theta) estimated from global p(Theta | mu, Lambda)
        h(Theta | R) approximated by average across all individual q(theta_s | r_s),
            which is represented by a set of samples in the learned model.
        """
        n_pseudo = 0.5
        # representing hypothetical participant NOT included in any group
        h_theta = self.global_pop.theta.entropy()
        # = scalar entropy for theta distribution within any included population
        # NOT including the uncertainty of global mean, if freely variable.
        h_theta_group = sum(g.n_subjects * g.entropy_theta_group()
                            for g in self.groups)
        h_theta_group += n_pseudo * h_theta
        h_theta_group /= (self.n_subjects + n_pseudo)
        # = h(theta) estimated as sample average across all included participants in all groups
        logger.debug(f'Global h(theta)= {h_theta:.3f}. Sample-based h(theta)= {h_theta_group:.3f}. (nats)')
        h_theta_given_response = sum(sum(g.entropy_theta_individual())
                                     for g in self.groups)
        # = sum_s h(theta_s | r_s) over all subjects
        h_theta_given_response += n_pseudo * h_theta  # pseudo-participant not seen
        h_theta_given_response /= (self.n_subjects + n_pseudo)
        mi_sampled = h_theta_group - h_theta_given_response  # nats
        mi = h_theta - h_theta_given_response  # nats
        logger.debug(f'mi_sampled= {mi_sampled:.3f}. mi= {mi:.3f} (nats).')
        return mi / np.log(2.)  # bits

    def item_mean_ordinal(self, theta):
        """Expected value of ordinal responses for all items,
        as a function of trait values.
        :param theta: array of trait values
        :return: r = list with expected "responses" on continuous scale
            r[i][...] = sum_l l * P{response = l | theta[...]} for i-th item
            *** return as dict instead ? ***

        NOTE: Since the ordinal responses are NOT on a linear interval scale,
        it is formally MEANINGLESS to take the mean of ordinal responses.
        Therefore, this result should be used only for illustration purpose,
        with caution about the scale non-linearity.

        Nevertheless, the expectation of ordinal responses
        is sometimes used without hesitation in the Rasch research tradition,
        Ref, e.g.: Wright and Masters (1982), Eq. 5.4.1.
        The expected rating plotted vs individual trait value
        is sometimes called Item Characteristic Curve (ICC).
        """
        return [np.dot(p_r, np.arange(p_r.shape[-1]))
                for p_r in self.item_response_prob(theta)]

    # def predictive_individual_var(self):  # *** not needed
    #     return np.diag(self.predictive_individual_cov())

    def predictive_individual_cov(self):
        """Inter-individual Covariance of traits, re. group mean,
        for a RANDOM INDIVIDUAL from any of the included (sub)populations,
        :return: 2D array with mean covariance matrix

        Method: = doc E{inv(Lambda)},
            where Lambda is estimated inter-individual precision matrix
            for theta values in all included (sub)populations / groups
        """
        return self.global_pop.theta.prec.mean_inv


# ------------------------------ module-internal help functions
def _trait_rotation(c, n_traits):
    """Transformation matrix for trait vectors to (sub-)space
    defined by eigenvectors of cov matrix
    :param c: 2D array with covariance matrix for all initial item-defined traits
        summed across all subjects in all groups
        c.shape == (n_items, n_items)
    :return: proj: 2D projection matrix with orthogonal COLUMN vectors
        proj[:, t] = unit direction vector for t-th trait
        proj.shape == (n_items, n_traits)
        where n_traits <= n_items
        The vectors are scaled such that transformation preserves trait variance
        in the new coordinate system,
        so the initial item scale thresholds should still be reasonably valid.
    """
    (e_val, e_vec) = np.linalg.eigh(c)
    mean_var = np.mean(np.diag(c))
    s = np.sign(e_vec[np.argmax(np.abs(e_vec), axis=0), np.arange(e_vec.shape[1])])
    e_vec *= s
    # e_det = np.linalg.det(e_vec)
    proj = e_vec[:, ::-1][:, :n_traits]  # in decreasing e_val order
    new_var = e_val[::-1][:n_traits]  # in same order
    s = np.sqrt(mean_var / new_var)
    # = scale factor to preserve trait variance
    proj *= s  # *********** needed? *****
    # c_proj = proj.T @ c @ proj  # *** for test, should be diagonal
    return proj
# ---------------------------------------------------------------------


# ------------------------------ help function for Pool multitasking:
# used by map or Pool().imap:
def _adapt(task):
    """dispatch call to given object.adapt(...)
    :param task: arguments defining the task:
        task[0] = object whose adapt method is called
        task[1] = positional arguments for adapt method
    :return: returned object from the called adapt method,
        i.e., an updated copy of object task[0]
    """
    # obj = task[0]
    # arg = task[1]
    # logger.debug(f'{obj}.adapt({arg})')
    return task[0].adapt(*task[1])
