"""This module defines data structures and functions to display analysis results
given an OrdinalItemResponseModel instance,
learned from one or several data sets with ordinal responses to a questionnaire.

Results are shown as figures and tables.
Figures can be saved in pdf, eps, or other formats, as specified in ir_display_format.
Tables are saved in LaTeX tabular format OR in tab-delimited text files.
Thus, both figures and tables can be easily imported into a LaTeX document
or other word-processing document.

*** Main Class:

ItemResponseDisplaySet = a structured container for all display results
Each display element can be accessed and modified by the user, before saving.

*** Usage Example: see template script run_irt

*** Version History:
* Version 1.0.0:
2023-08-30, code cleanup
2023-08-13, adapted to modified ir_model, other minor updates

* Version 0.6:
2023-07-06: Table and figure names set when created. File formats defined in save methods.
2023-07-06: table results as pandas.DataFrame objects.

2020-06-04, first version for ItemResponseCalc standalone package
"""
# **** Allow scaling here, for unity inter-individual trait variance.
# **** display individual results ???

import numpy as np
from collections import Counter
from pathlib import Path

import logging

from samppy.credibility import cred_diff

from . import ir_display_format as fmt

# -------- module-global variables, that may be changed by user:
FMT = {'percentiles': [5., 50., 95.],
       'credibility_levels': [.99, .95, .9, .8, .7],  # MAX 5 values
       'population': 'Population',
       'trait': 'Trait',
       'mean': 'Mean',
       'random': 'Random',
       'individual': 'Individual',
       'equivalent': 'Equivalent',
       'item': 'Item',
       'response': 'Response',
       'thresholds': 'Thresholds',
       'probability': 'Prob.',
       'rating': 'Rating',
       'global': 'Global',
       'correlation': 'Correlation',
       'credibility': 'Credibility',
       'quantile': 'Quantile',
       # 'standardize': False,  # Future? True -> standardized trait scales in all displays
       }
# = dict with format parameters that may be changed by user
# Any other parameters are handled by module ir_display_format

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # test

DEFAULT_FIGURE_FORMAT = 'pdf'
DEFAULT_TABLE_FORMAT = 'txt'


# ------------------------------------------------------------
def set_format_param(**kwargs):
    """Set / modify format parameters for this module
    :param kwargs: dict with any formatting variables
    :return: None
    """
    other_fmt = dict()
    for (k, v) in kwargs.items():
        k = k.lower()
        if k in FMT:
            FMT[k] = v
        else:
            other_fmt[k] = v
    if len(FMT['credibility_levels']) > 5:
        FMT['credibility_levels'] = FMT['credibility_levels'][:5]
    fmt.set_format_param(**other_fmt)  # all remaining user-defined parameters


# ---------------------------------------------------------- Main Display Classes:
class ItemResponseDisplaySet:
    """Root container for all displays of predictive trait results and item properties,
    from one OrdinalItemResponseModel object.
    All display elements can be saved as files within a selected directory three.
    The complete instance can also be serialized and dumped to a single pickle file,
    then re-loaded and re-saved, if any display object needs to be edited.
    """
    def __init__(self,
                 log_likelihood,
                 instrument,
                 traits):
        """
        :param log_likelihood: fmt.FigureRef with log-likelihood plot
        :param instrument: ItemSetDisplay object, showing
            response thresholds, and response_prob plot for each item
            (containing only FigureRef displays)
        :param traits: TraitDisplay object with predicted trait distribution
            for population mean, and for random individual in population.
            Traits for individual respondents are NOT (yet) displayed.
            (containing both FigureRef and ResultTable instances)
        """
        self.log_likelihood = log_likelihood
        self.instrument = instrument
        self.traits = traits

    def __repr__(self):
        skip = '\n\t'
        return (self.__class__.__name__ + '(' + skip +
                (',' + skip).join(f'{key}={repr(v)}'
                                  for (key, v) in vars(self).items()) +
                skip + ')')

    def save(self, dir_top,
             figure_format=None,
             table_format=None,
             **kwargs):
        """Save all displays in a directory tree
        :param dir_top: Path or string with top directory for all displays
        :param figure_format: (optional) single figure-file format string
        :param table_format: (optional) single table-file format string
        :param kwargs: (optional) additional parameters passed to ResultTable.save() method.
            NOTE: NO extra kwargs allowed for FigureRef.save() method!
        :return: None
        """
        dir_top = Path(dir_top)  # just in case
        if figure_format is None and table_format is None:
            figure_format = DEFAULT_FIGURE_FORMAT
            table_format = DEFAULT_TABLE_FORMAT
        # One of them may be None -> only the other type of data are saved.
        dir_top.mkdir(parents=True, exist_ok=True)  # just in case
        self.log_likelihood.save(dir_top, figure_format=figure_format)
        if self.instrument is not None:
            self.instrument.save(dir_top,
                                 figure_format=figure_format,
                                 table_format=table_format)
        if self.traits is not None:
            self.traits.save(dir_top,
                             figure_format=figure_format,
                             table_format=table_format,
                             **kwargs)

    @classmethod
    def show(cls, irm, mapping_item=None, **kwargs):
        """Create displays for all results from learned model,
        and store all display elements in a single cls instance.
        :param irm: a single learned OrdinalItemResponseModel instance
        :param mapping_item: index of item to be used for
            mapping non-linear mean rating, given scale trait
        :param: kwargs: (optional) any display formatting parameters
        :return: a single cls instance
        """
        set_format_param(**kwargs)
        logger.info(f'Creating displays for {len(irm.groups)} population(s): ' +
                    ', '.join(g.name for g in irm.groups))
        logger.info(fig_comments())
        logger.info(table_comments())
        return cls(log_likelihood=fmt.fig_log_likelihood(irm.log_prob,
                                                         irm.n_subjects,
                                                         color='r',
                                                         name='LearnedLL'),
                   instrument=ItemSetDisplay.show(irm),
                   traits=TraitDisplay.show(irm, mapping_item))


class ItemSetDisplay:
    """Container for all displays of item-related properties
    """
    def __init__(self,
                 response_freq,
                 items,
                 thresholds=None,
                 fisher_info=None):
        """
        :param response_freq: FigureRef with relative response frequencies for all items
        :param items: dict with elements (item_id, item_display),
             where item_display = ItemDisplay object, containing FigureRef objects
        :param thresholds: TableRef with response thresholds for all items (and all groups)
        :param fisher_info: dict with elements (trait_id, fisher_fig)
            where fisher_fig is a FigureRef with Item Information Function plots
            for items related to the same trait.
        """
        self.response_freq = response_freq
        self.items = items
        self.thresholds = thresholds
        if fisher_info is None:
            fisher_info = dict()
        self.fisher_info = fisher_info

    def save(self, top_path, figure_format, table_format):
        """
        :param top_path: path where plots are saved
        :param figure_format: file format for saved figures
        :param table_format: file format for saved tables
        :return: None
        """
        items_path = top_path / 'items'
        items_path.mkdir(parents=True, exist_ok=True)
        if self.response_freq is not None:
            self.response_freq.save(items_path, figure_format)
        for item in self.items.values():
            item.save(items_path, figure_format)
        if self.thresholds is not None:
            self.thresholds.save(items_path, table_format)
        for f_info in self.fisher_info.values():
            f_info.save(items_path, figure_format)

    @classmethod
    def show(cls, irm):
        """
        :param irm: OrdinalItemResponseModel instance
        :return: a cls instance
        """
        (t_min, t_max) = irm.theta_range()
        t = np.linspace(t_min, t_max, 100)
        # same trait range across all items
        g_count = irm.item_response_count()
        # = dict with elements (group_key, g_count), where
        # g_count = list of Counter objects, one for each item
        total_count = [sum((g_c[i] for g_c in g_count.values()), Counter())
                       for i in range(irm.n_items)]
        # *** use item_id instead of item_index ********************
        response_prob = irm.item_response_prob(t)
        # = list with 1D response vectors, one for each item
        item_id = np.array(irm.item_labels())  # to allow boolean indexing
        thr = irm.item_thresholds(item=FMT['item'], response=FMT['response'])
        thr = thr.groupby([FMT['item'], FMT['response']]).quantile(np.array(FMT['percentiles']) / 100.)
        thr.index.set_names(FMT['quantile'], level=-1, inplace=True)  # ***** -> irm.item_thresholds_quantiles?
        # = pd.DataFrame with threshold quantiles for all items and all groups
        # with row MultiIndex (item, response, quantile), and one column for each group
        f_t = irm.item_fisher_information(t)
        item_trait_map = irm.item_trait_map()
        # ************** weighted average instead of hard selection ? ************************
        trait_labels = fmt.make_trait_labels(item_trait_map)  # *** -> irm ?
        fisher_figs = {trait_id: fmt.fig_fisher_information(t, f_t[trait_items, :],
                                                            item_labels=item_id[trait_items],
                                                            x_label=FMT['trait'],
                                                            y_label='Fisher Information',
                                                            name=trait_id+'-Fisher')
                       for (trait_id, trait_items) in zip(trait_labels,
                                                          item_trait_map.T)
                       }
        return cls(response_freq=fmt.fig_response_freq(total_count,
                                                       name='Response_freq'),
                   items={id_i: ItemDisplay.show(r_prob_i,
                                                 trait=t,
                                                 tau_global=tau_i[1:-1],
                                                 item_id=id_i,
                                                 tau_group=thr.loc[id_i])
                          for (r_prob_i, id_i, tau_i) in zip(response_prob,
                                                             item_id,
                                                             irm.item_thresholds_global())
                          },
                   thresholds=fmt.ResultTable(thr, name='ItemThresholds'),
                   fisher_info=fisher_figs
                   )


class ItemDisplay:
    """Container for all displays related to ONE item
    """
    def __init__(self,
                 response_freq=None,
                 response_prob=None,
                 mean_response=None,
                 thresholds=None):
        """
        :param response_freq: FigureRef with empirical response freq
        :param response_prob: FigureRef with predicted response probability vs. trait,
            like 'Category Characteristic Curves' in the Rasch tradition.
        :param mean_response: FigureRef with expected response vs. trait
            (*** and ? empirical response range vs trait ? *****)
            NOTE: NOT valid, as ordinal responses are NOT on interval scale
            *** SKIPPING this display variant for now...
        :param thresholds: FigureRef with threshold quartiles for all groups
        """
        self.response_freq = response_freq  # ****** NOT USED for now ***
        self.response_prob = response_prob
        self.mean_response = mean_response  # ****** NOT USED for now ***
        self.thresholds = thresholds

    def save(self, save_path, figure_format):
        """
        :param save_path: path where sub-objects are saved
        :param figure_format: file format of saved figures
        :return:
        """
        if figure_format is not None:
            if self.response_freq is not None:
                self.response_freq.save(save_path, figure_format)
            if self.response_prob is not None:
                self.response_prob.save(save_path, figure_format)
            if self.mean_response is not None:
                self.mean_response.save(save_path, figure_format)
            if self.thresholds is not None:
                self.thresholds.save(save_path, figure_format)

    @classmethod
    def show(cls, response_prob, trait, item_id, tau_global=None, tau_group=None):
        """Generate displays for given item
        :param response_prob: 2D array with response prob.mass
            response_prob[n, l] = prob.mass vector, for given trait[n] and l-th ordinal response
        :param trait: 1D array with dense trait values for plot
        :param item_id: string for plot lobel
        :param tau_global: 1D array with global mean thresholds for this item
            to be included in response-prob. plots
        :param tau_group: pd.DataFrame with threshold quantiles for this item
            separated by group, displayed in a separate figure
        :return: a cls instance
        """
        # r_mean = 1. + np.dot(ord_prob, np.arange(item_scale.n_response_levels))
        # response_freq=fmt.fig_response_freq(response_count),
        if tau_group.shape[-1] > 1:  # more than ONE population
            tau_fig = fmt.fig_thresholds(tau_group,
                                         name=item_id + FMT['thresholds'],
                                         x_label=FMT['population'],
                                         y_label=' '.join([FMT['response'],
                                                           FMT['thresholds']])
                                         )
        else:
            tau_fig = None
        return cls(response_prob=fmt.fig_response_prob(trait, response_prob,
                                                       name=item_id + FMT['probability'],
                                                       tau=tau_global,
                                                       x_label=FMT['trait'],
                                                       y_label=' '.join([FMT['response'],
                                                                         FMT['probability']])
                                                       ),
                   thresholds=tau_fig
                   )


class TraitDisplay:
    """Container for result displays of predicted trait values
    for all traits and groups,
    with layout depending on number of groups and traits.
    """
    def __init__(self, pop_mean, pop_ind,
                 corr_global=None,
                 corr_within=None,
                 group_diff=None):
        """
        :param pop_mean: FigureRef of population predictive mean traits
        :param pop_ind: FigureRef of population predictive traits for random individual
        :param corr_global: (optional) TableRef with global predictive trait correlations
        :param corr_within: (optional) TableRef with predictive trait correlations
            within populations, i.e., excl. variance between populations.
        :param group_diff: (optional) GroupDiffDisplay object,
            iff we have more than one group (population)
       """
        self.pop_mean = pop_mean
        self.pop_ind = pop_ind
        self.corr_global = corr_global  # *** not used in v. 1.0.0 ***
        self.corr_within = corr_within
        self.group_diff = group_diff

    def save(self, path, figure_format, table_format, **kwargs):
        """
        :param path: to directory where all display objects are saved
        :param figure_format: file format for saved figures
        :param table_format: file format for saved tables
        :param kwargs: (optional) additional parameters to table save method
        :return:
        """
        if figure_format is not None:
            if self.pop_mean is not None:
                self.pop_mean.save(path, figure_format)
            if self.pop_ind is not None:
                self.pop_ind.save(path, figure_format)
        if self.corr_global is not None:
            self.corr_global.save(path, table_format, **kwargs)
        if self.corr_within is not None:
            self.corr_within.save(path, table_format, **kwargs)
        if self.group_diff is not None:
            for (trait_id, trait_diff) in self.group_diff.items():
                trait_diff.save(path / 'group_diff',
                                figure_format=figure_format,
                                table_format=table_format,
                                **kwargs)

    @classmethod
    def show(cls, irm, mapping_item=None):
        """
        :param irm: OrdinalItemResponseModel instance
        :param mapping_item: index of item to be used for non-linear scale mapping
            *** identify by ID string instead ? ***
        :return: a cls instance
        """
        # *** show percentiles as table, too ? ***
        def _fig_percentiles(perc, g_labels, t_labels, y_label, name=None):
            """Plot trait percentiles vs groups and/or traits,
            in style depending on n_groups and n_traits
            :param perc: 3D array with percentile trait values
                perc[g, p, t] = p-th percentile of t-th trait in g-th population
            :param g_labels: list of group label strings
                len(g_labels) == perc.shape[0]
            :param t_labels: list of trait label strings
                len[t_labels] == perc.shape[2]
            :param y_label: string with y-axis label
            :param name: string with file name for the fiture
            :param mapping_item: index of irm.items to be used for mapping
            :return: FigureRef instance
            """
            (n_groups, n_perc, n_traits) = perc.shape
            if n_traits > 1:  # plot perc vs traits, with populations as subcases
                f = fmt.fig_percentiles(perc,
                                        x_label=FMT['trait'],
                                        x_ticklabels=t_labels,
                                        case_labels=g_labels,
                                        name=name,
                                        y_label=y_label,
                                        x_offset=0.07)
            else:  # plot perc vs groups, with traits as subcases
                f = fmt.fig_percentiles(perc.transpose(2, 1, 0),
                                        x_label=FMT['population'],
                                        x_ticklabels=g_labels,
                                        case_labels=t_labels,
                                        name=name,
                                        y_label=y_label,
                                        x_offset=0.07)
            (y_min, y_max) = f.ax.get_ylim()
            y_min -= 0.1  # **** fix to make more space for legend
            f.ax.set_ylim(y_min, y_max)
            if mapping_item is not None:
                # make second corresponding scale with expected response ratings
                y = np.linspace(y_min, y_max, 100)
                # use mapping_item and its item_id
                y_mapped = 1. + irm.item_mean_ordinal(y)[mapping_item]
                item_id = f'Q{1+mapping_item}'  # *** get mapping_item as ID string ?
                f.mapped_y_axis(y, y_mapped,
                                y_label=(FMT['equivalent'] + ' ' +
                                         item_id + ' ' + FMT['rating'])
                                )
            return f
        # -----------------------------------------------------------
        if mapping_item < 0:
            mapping_item = irm.n_items + mapping_item # ensure positive index
        item_trait_map = irm.item_trait_map()
        trait_sel = np.any(item_trait_map, axis=0)
        # = boolean trait index for display, just in case irm has NOT been pruned
        # *** should display the non-pruned model?
        # *** NO, because only traits[trait_sel] are effectively used in the model.
        n_traits = np.sum(trait_sel)
        trait_labels = fmt.make_trait_labels(item_trait_map[:, trait_sel])
        group_labels = [g.name for g in irm.groups]  # ********* irm.groups.keys()
        global_mu = irm.global_pop.theta.predictive_mean()
        global_mu_rvs = global_mu.rvs(size=10000)
        pop_mean_samples = np.array([g.predictive_mean().rvs(global_mu_rvs)[:, trait_sel]
                                     for g in irm.groups])
        # pop_mean_samples[g, n, t] = n-th sample of t-th trait in g-th population
        # all subpopulations conditional on global_mu
        pop_mean_perc = np.percentile(pop_mean_samples,
                                      FMT['percentiles'],
                                      axis=1)
        # pop_mean_perc[p, g, t] = p-th percentile for t-th trait in g-th population
        pop_mean_fig = _fig_percentiles(pop_mean_perc.transpose(1, 0, 2),
                                        group_labels,
                                        trait_labels,
                                        y_label=' '.join([FMT['population'],
                                                          FMT['mean'],
                                                          FMT['trait']]),
                                        name=' '.join([FMT['trait'],
                                                       FMT['mean']]))
        pop_ind_samples = np.array([g.predictive_individual().rvs(global_mu_rvs)[:, trait_sel]
                                    for g in irm.groups])
        pop_ind_perc = np.percentile(pop_ind_samples,
                                      FMT['percentiles'],
                                      axis=1)
        # pop_ind_perc[p, g, t] = p-th percentile for t-th trait in g-th population
        pop_ind_fig = _fig_percentiles(np.array(pop_ind_perc).transpose(1, 0, 2),
                                       group_labels,
                                       trait_labels,
                                       y_label=' '.join([FMT['random'],
                                                         FMT['individual'],
                                                         FMT['trait']]),
                                       name=' '.join([FMT['trait'],
                                                      FMT['individual']]))

        c_global = None
        c_within = None
        if n_traits > 1:
            c_global = fmt.tab_correlation_matrix(irm.predictive_individual_cov(), item_trait_map,
                                                  name='_'.join((FMT['trait'],
                                                                 FMT['correlation'],
                                                                 FMT['global'])
                                                                ))
        g_diff = None
        if irm.n_groups > 1:
            # show differences between population means:
            g_diff = {trait_id: GroupDiffDisplay.show(t_samples,
                                                      group_labels,
                                                      trait_label=trait_id)
                      for (trait_id, t_samples) in zip(trait_labels,
                                                       pop_mean_samples.transpose(2, 0, 1))
                      }
            if n_traits > 1:
                g_diff['Mean_Trait'] = GroupDiffDisplay.show(np.mean(pop_mean_samples,
                                                                     axis=-1),
                                                             group_labels,
                                                             trait_label='Mean_Trait')

        return cls(pop_mean=pop_mean_fig,
                   pop_ind=pop_ind_fig,
                   corr_global=c_global,
                   corr_within=c_within,
                   group_diff=g_diff)


class GroupDiffDisplay:
    """Container for displays showing predictive credible differences
    between populations, for ONE selected trait, or MEAN across traits.
    """
    def __init__(self, fig=None, tab=None):
        """
        :param fig: FigureRef object
        :param tab: TableRef object
        """
        self.fig = fig
        self.tab = tab

    def save(self, path,
             figure_format,
             table_format,
             **kwargs):
        """
        :param path: path to directory for saved plots and tables
        :param figure_format: file format of saved figures
        :param table_format: file format of saved table
        :param kwargs: (optional) additional arguments to Table.save method
        :return: None
        """
        if self.fig is not None:
            self.fig.save(path, figure_format=figure_format)
        if self.tab is not None:
            self.tab.save(path, table_format=table_format, **kwargs)

    @classmethod
    def show(cls, group_samples, group_labels, trait_label):
        """Display credible differences between groups,
        given samples of predictive distribution
        :param group_samples: 2D array with
            group_samples[g, n] = n-th sample of selected trait for g-th group
        :param group_labels: list of string-valued group labels
            len(group_labels) == group_samples.shape[0]
        :param trait_label: string identifying the difference to be shown
        :return: a cls instance
        """
        # **** Sort groups for decreasing median values
        s_ind = np.argsort(np.median(group_samples, axis=1))[::-1]
        g_samples = group_samples[s_ind, :]
        g_labels = [group_labels[i] for i in s_ind]
        diff = cred_diff(g_samples,
                         diff_axis=0, sample_axis=1,
                         p_lim=np.amin(FMT['credibility_levels']))
        fig = fmt.fig_credible_diff(diff,
                                    diff_label=trait_label,
                                    x_labels=g_labels,
                                    x_label=FMT['population'],
                                    cred_levels=FMT['credibility_levels'])
        tab = fmt.tab_credible_diff(diff, diff_name=trait_label,
                                    cred_header=FMT['credibility'],
                                    x_labels=g_labels, x_label=FMT['population'])
        return cls(fig, tab)


# ------------------------------------------------ Result explanations
def fig_comments():
    """Generate figure explanations.
    :return: comment string
    """
    p_min = np.amin(FMT['percentiles'])
    p_max = np.amax(FMT['percentiles'])
    c = f"""Figure Explanations:

Figure files with a name like Population_Indiv_Trait.xxx or Population_Mean_Trait.xxx
display user-requested percentiles (markers) and credible intervals (vertical bars)
for the estimated trait distribution for a random individual and for the population mean.
The vertical bars show the range between {p_min:.1f}- and {p_max:.1f}- percentiles.

The displayed ranges include all uncertainty
caused both by real inter-individual perceptual differences,
and by the limited number of items and discrete response categories,
and (possibly) between-population differences in questionnaire interpretations.

Item-specific figures show the model-estimated probability for each response category
as a function of the latent trait parameter.
These plots are sometimes called 'Category Characteristic Curves' in Rasch tradition.

If there is more than one population,
item-specific figures show estimated response thresholds for all populations,
as median and range between {p_min:.1f}- and {p_max:.1f}- percentiles.
"""
    return c


def table_comments():
    c = """Table Explanations:

Files with names like someTrait.txt or, *.csv, tabulate all pairs of populations
for which the trait difference is JOINTLY credibly different,
with the tabulated credibility value.

The credibility value in each table row is the JOINT probability
for the pairs in the same row and all rows above it.
Thus, the joint probability values already account for multiple comparisons,
so no further adjustments are needed.

The same information is also saved in figure files with similar names, like someTrait.pdf,
showing all population pairs with jointly credible trait differences.

If several latent traits are needed to model the response data, 
table files with names like Trait_Correlation_xxx.xxx 
show the estimated correlation between traits. 
"""
    return c
