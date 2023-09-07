"""Functions and classes to display results from an OrdinalItemResponseModel object.
** Version history:

* Version 1.0.0:
2023-08-12, minor bugfix

* Version 0.6:
2023-07-07, rely mainly on matplotlib.rcParams for plot styles
2023-07-06, define name of FigureRef and ResultTable already when created
2023-07-05, new table result functions using Pandas for result tables

* Version 0.5: first published version
"""
import numpy as np
from itertools import cycle, product

import matplotlib.pyplot as plt
import logging

import pandas as pd

logger = logging.getLogger(__name__)

# --------------------------- Default format parameters:
FMT = {'colors': 'rbg',  # color cycle to separate results in plots
       'line_styles': ['solid', 'dashed', 'dashdot', 'dotted'],
       'markers': 'o^sDv',  # plot symbols, each repeated with each fillstyle
       'fillstyle': ['full', 'none'], # marker style
       'sum': 'Sum',
       }
# = module-global dict with default settings for display details
# that may be changed by user

# NOTE: FMT['colors'], FMT['linestyles'], FMT['markers'], and FMT['fillstyle']
#   override any corresponding properties in matplotlib.rcParams,
#   because rcParams.axes.prop_cycle allows only equal lengths of these property sequences.
#   Here, the UNEQUAL lengths of FMT default sequences will combine
#   into a sequence with many combinations, before the style repeats itself.


class FileWriteError(RuntimeError):
    """Any type of exception while attempting to write a pd.DataFrame table to a file
    """


def set_format_param(mpl_style=None, mpl_params=None, **kwargs):
    """Set / modify format parameters.
    Called before any displays are generated.
    :param mpl_style: (optional) matplotlib style sheet, or list of style sheets
    :param mpl_params: (optional) dict with matplotlib (k, v) rcParam settings
    :param kwargs: dict with any formatting variables to be stored in FMT
    :return: None
    """
    if mpl_style is not None:
        plt.style.use(mpl_style)
    if mpl_params is not None:
        plt.rcParams.update(mpl_params)
    other_fmt = dict()
    for (k, v) in kwargs.items():
        k = k.lower()
        if k in FMT:
            FMT[k] = v
        else:
            other_fmt[k] = v
    if len(other_fmt) > 0:
        logger.warning(f'Parameters {other_fmt} unknown, not used.')


# ---------------------------- Main Result Classes
class FigureRef:
    """Reference to a single graph instance
    """
    def __init__(self, ax, name=None):
        """
        :param ax: Axes instance containing the graph
        :param name: string name of figure
        """
        self.ax = ax
        self.name = name

    @property
    def fig(self):
        return self.ax.figure

    def save(self, path,
             figure_format):
        """Save figure to given path
        :param path: Path to directory where figure is saved
        :param figure_format: file format of saved figure
        :return: None
        """
        if figure_format is not None:
            name = _clean_file_name(self.name)
            path.mkdir(parents=True, exist_ok=True)
            f = (path / name).with_suffix('.' + figure_format)
            try:
                self.fig.savefig(f)
            except Exception as e:  # any error, just warn and continue
                logger.warning(f'Could not save plot to {f}. Error: {e}')

    def mapped_y_axis(self, y, y_mapped, y_label=''):
        """Add a second y_axis to self.ax with ticks placed at
        y values corresponding to uniform steps in y_mapped values
        but labelled by the y_mapped values
        :param y: long sequence of y_values along original y axis
        :param y_mapped: corresponding transformed y_values for new y_ticks
            len(y_mapped) == len(y)
            y and y_mapped monotonically increasing
        :param y_label: label of second y-axis
        :return: None
        """
        ax2 = self.ax.twinx()
        ax2.set_ylim(self.ax.get_ylim())
        ymap_ticks = _nice_ticks(np.amin(y_mapped), np.amax(y_mapped))
        # = uniform ticks in y_mapped scale
        ymap_ticklabels = [f'{tick:.1f}' for tick in ymap_ticks]
        y_ticks = np.interp(ymap_ticks, y_mapped, y)
        # = transformed to corresponding y scale positions
        ax2.set_yticks(y_ticks)
        ax2.set_yticklabels(ymap_ticklabels)
        ax2.set_ylabel(y_label)
        # self.fig.tight_layout()


# --------------------------------------------------
class Table(pd.DataFrame):
    """Subclass adding a general save method,
    automatically switching to desired file format.
    """
    def save(self, file_path,
             allow_over_write=True,
             write_fcn=None,
             **file_kwargs):
        """Save self to a table-style file.
        :param file_path: Path instance defining file location and full name incl. suffix.
        :param allow_over_write: (optional) boolean, if False, find new unused path stem.
        :param write_fcn: (optional) user-supplied function with signature
            write_fcn(table, path, **kwargs).
            If None, default pd.DataFrame method is used, determined by file_path.suffix
        :param file_kwargs: (optional) any additional arguments for the
            write function for the specific file format.
        :return: None
        """
        if not allow_over_write:
            file_path = safe_file_path(file_path)
        suffix = file_path.suffix
        try:
            # ******** file_path.parent.mkdir here? NO, done by container class
            if write_fcn is None:
                if suffix in ['.xlsx', '.xls', '.odf', '.ods', '.odt']:
                    self.to_excel(file_path, **file_kwargs)
                elif suffix in ['.csv']:
                    self.to_csv(file_path, **file_kwargs)
                elif suffix in ['.txt']:
                    self.to_string(file_path, **file_kwargs)
                elif suffix in ['.tex']:
                    # with warnings.catch_warnings():
                    #     # suppress Pandas FutureWarning about to_latex method
                    #     warnings.simplefilter('ignore')
                    #     self.to_latex(file_path, **file_kwargs)
                    self.to_latex(file_path, **file_kwargs)
                else:
                    raise FileWriteError(f'No DataFrame write method for file type {suffix}')
            else:
                write_fcn(self, file_path, **file_kwargs)
        except Exception as e:
            raise FileWriteError(f'Could not write to {file_path}. Error: {e}')

class ResultTable(Table):
    """A pd.DataFrame table subclass, with a name and special save method
    """
    def __init__(self, df, name):
        """
        :param df: a Table(pd.DataFrame) instance
        :param name: file name for saving the table
        """
        super().__init__(df)
        self.name = name

    def save(self, path,
             table_format=None,
             **kwargs):
        """Save table to file.
        :param path: Path to directory for saving self.
        :param table_format: table-format string code -> file-name suffix
        :param kwargs: (optional) any additional arguments to pandas writer function
        :return: None
        """
        if table_format is not None:
            name = _clean_file_name(self.name)
            f = (path / name).with_suffix('.' + table_format)
            try:
                super().save(f, **kwargs)
            except Exception as e:  # any error, just warn and continue
                logger.warning(f'Could not save result table. Error: {e}')


class DiffTable(ResultTable):
    """Special subclass suppressing index in save method
    """
    def save(self, path,
             **kwargs):
        """Save table to file.
        :param path: Path to directory for saving self.
        :param kwargs: (optional) any additional arguments to pandas writer function
        :return: None
        """
        if 'index' not in kwargs:
            kwargs['index'] = False  # override Pandas default = True
        super().save(path, **kwargs)


# ------------------------------------------------ plot routines

def fig_log_likelihood(learned_ll, n_users,
                       name,
                       title='',
                       **kwargs):
    """plot VI learning result
    :param learned_ll = list log-likelihood values from a learned ItemResponseModel
    :param n_users = scalar number of users included in the total log-likelihood
    :param name = figure name for file
    :param title = (optional) figure title
    :param kwargs = (optional) dict with any additional arguments for plot function
    :return: None
    """
    f_logprob, ax = plt.subplots()
    t1 = 1
    # for ll in learned_ll:
    t = [t1 + n for n in range(len(learned_ll))]
    # n_train = ham.n_training_users
    ax.plot(t, np.array(learned_ll) / n_users, **kwargs)
    # t1 = t[-1] + 1
    ax.set_xlim(0, t[-1]+1)
    ax.set_xlabel('Learning Iterations')
    ax.set_ylabel('Log-likelihood / N')
    if 0 < len(title):
        ax.set_title(title)
    return FigureRef(ax, name=name)


def fig_response_freq(count, name):
    """Generate a plot with relative frequencies of response counts for all items
    :param count: list of Counter objects  *** dict ?
        count[i][0] = number of missing responses for i-th item
        count[i][l] = number of responses in l-th ordinal level for i-th item
    :param name = string name of this figure
    :return: FigureRef object
    """
    fig, ax = plt.subplots()
    for (i, (c, col, (m, fill_style))) in enumerate(zip(count,  # total_count,
                                                        cycle(FMT['colors']),
                                                        cycle(product(FMT['markers'],
                                                                      FMT['fillstyle'])))):
        x_i = np.arange(1 + max(*c.keys()))  # key = 0 means missing data
        y_i = np.array([c[r] for r in x_i])
        y_i = y_i / np.sum(y_i)
        y_i *= 100  # in percent
        ax.plot(x_i, y_i, label = f'Q{i+1}', color=col,
                marker=m, fillstyle=fill_style)
    ax.set_xticks(np.arange(0, 6))
    ax.set_xticklabels(['Missing'] + [f'R={i+1}' for i in range(5)])
    ax.set_xlabel('Item Response')
    ax.set_ylabel('Rel. Frequency (%)')
    ax.legend(loc='best')
    return FigureRef(ax, name=name)


def fig_response_prob(t, p,
                      name,
                      tau=None,
                      x_label='',
                      y_label=''):
    """figure with response prob vs. trait for ONE item
    :param t: 1D array with trait values
    :param p: 2D array with response probabilities
        p[n, l] = P{l-th response | t[n]}
    :param name: string for plot file name
    :param tau: (optional) 1D array with trait thresholds
    :param x_label: string for x-axis label
    :param y_label: string for y-axis label
    :return: FigureRef object
    """
    fig, ax = plt.subplots()
    for (l, (p_l, c, ls)) in enumerate(zip(p.T,
                                           cycle(FMT['colors']),
                                           cycle(FMT['line_styles']))):
        ax.plot(t, p_l, color=c, linestyle=ls, label=f'R={1+l}')
    if tau is not None:
        # plot ticks at thresholds
        x = [tau, tau]
        y = [np.zeros(len(tau)), 0.1 * np.ones(len(tau))]
        ax.plot(x, y, color='k', linewidth=1., linestyle='solid')
    ax.set_ylim(0., 1.)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.legend(loc='best')
    return FigureRef(ax, name=name)


def fig_fisher_information(t, f, item_labels,
                           name,
                           x_label='',
                           y_label=''):
    """figure with response prob vs. trait for ONE item
    :param t: 1D array with hypothetical TRUE trait values
    :param f: 2D array with Fisher Information data
        f[i, n] = Fisher Information for i-th item given true trait=t[n]
    :param item_labels: list with string labels
        len(item_labels) == f.shape[0]
    :param name: string for plot file name
    :param tau: (optional) 1D array with trait thresholds
    :param x_label: string for x-axis label
    :param y_label: string for y-axis label
    :return: FigureRef object
    """
    fig, ax = plt.subplots()
    for (f_i, id_i, c, ls) in zip(f,
                                  item_labels,
                                  cycle(FMT['colors']),
                                  cycle(FMT['line_styles'])):
        ax.plot(t, f_i, color=c, linestyle=ls, label=id_i)
    if f.shape[0] > 1:  # plot sum, too
        ax.plot(t, np.sum(f, axis=0), color='k', linestyle='solid',
                linewidth=1.3*plt.rcParams['lines.linewidth'],
                label=FMT['sum'])
    # ax.set_ylim(0., 1.)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.legend(loc='best')
    return FigureRef(ax, name=name)


def fig_thresholds(tau_group,
                   name,
                   x_label='Population',
                   y_label='Thresholds'):
    """figure with threshold quartiles for ONE item and all groups
    :param tau_group: pd.DataFrame with one column for each group,
        and one MultiIndex row for each (Response, Quartile),
        with UPPER threshold for each ordinal response.
        Currently exactly THREE quantiles: first quartile, median, third quartile
    :param name: string label for the plot file
    :param x_label: (optional) string for x label
    :param y_label: (optional) string for y label
    :return: FigureRef instance
    """
    if tau_group is None:
        return None
    (fig, ax) = plt.subplots()
    responses = tau_group.index.levels[0]
    q = tau_group.index.levels[1]
    for r in responses:  # each response
        t = tau_group.loc[r].to_numpy()
        x = np.arange(t.shape[-1])
        ax.plot(np.tile(x, (2, 1)), t[[0, -1], :], 'r-')
        ax.plot(x[:, None], t[q==0.5, :].T, 'r-', marker='o', linewidth=0.5)
    ax.set_xticks(np.arange(tau_group.shape[-1]))
    ax.set_xticklabels(tau_group.columns.values)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    return FigureRef(ax, name=name)



def fig_percentiles(perc,
                    y_label,
                    x_ticklabels,
                    name,
                    case_labels=None,
                    x_label=None,
                    x_offset=0.1,
                    x_space=0.5,
                    **kwargs):
    """create a figure with trait percentile results
    :param perc: 3D (or 2D) array with trait percentiles
        perc[c, p, t] = p-th percentile of t-th variable for c-th case
        percentiles plotted vertically vs t-variables horizontally,
    :param y_label: string for y axis label
    :param x_label: string for x-axis label
    :param x_ticklabels: list of strings with labels for x_ticks,
        one for each value in rows perc[..., :]
        len(x_ticklabels) == perc.shape[-1] == number of traits
    :param name: string name of this figure
    :param case_labels: list of strings with labels for cases, if more than one
        len(case_labels) == perc.shape[0] if perc.ndim == 3
    :param x_offset: (optional) horizontal space between case plots for each x_tick
    :param x_space: (optional) min space outside min and max x_tick values
    :param kwargs: (optional) dict with any additional keyword arguments for plot commands.
    :return: None  # fig object with single plot axis with all results
    """
    fig, ax = plt.subplots()
    if perc.ndim == 2:
        perc = perc[np.newaxis,...]
        case_labels = [None]
    (n_cases, n_perc, n_xticks) = perc.shape
    x = np.arange(0., n_xticks) - x_offset * (n_cases - 1) / 2
    for (c_key, c_y, c, (m, fs)) in zip(case_labels, perc,
                                      cycle(FMT['colors']),
                                      cycle(product(FMT['markers'],
                                                    FMT['fillstyle']))):
        ax.plot(np.tile(x, (2, 1)), c_y[[0, 2], :],
                linestyle='solid', color=c, **kwargs)
        ax.plot(x, c_y[1, :], linestyle='', color=c,
                marker=m, fillstyle=fs,  # markeredgecolor=c,  # markerfacecolor='w',
                label=c_key, **kwargs)
        x += x_offset
    (x_min, x_max) = ax.get_xlim()
    x_min = min(x_min, -x_space)
    x_max = max(x_max, n_xticks - 1 + x_space)
    ax.set_xlim(x_min, x_max)
    ax.set_xticks(np.arange(n_xticks))
    ax.set_xticklabels(x_ticklabels)
    ax.set_ylabel(y_label)  # + ' (' + y_unit + ')')
    ax.set_xlabel(x_label)
    if n_cases > 1:
        # make space for legend
        (x_min, x_max) = ax.get_xlim()
        ax.set_xlim(x_min, x_max + 0.6)
        ax.legend(loc='best')
    if name is None:
        name = _clean_file_name(y_label)
    return FigureRef(ax, name=name)


def fig_credible_diff(c_diff,
                      diff_label,
                      x_labels,
                      x_label=None,
                      title=None,
                      cred_levels=None):
    """Nice color plot to show jointly credible differences
    :param c_diff: list of tuples ((i, j), p), indicating that
        x_labels[i] > x-labels[j] with joint credibility p
    :param diff_label: name for this display figure
    :param x_labels: list of labels of compared categories
    :param x_label: (optional) axis label
    :param title: (optional) string with plot title
    :param cred_levels: (optional) list of joint-credibility values, in DECREASING order
    :return:
    """
    if cred_levels is None:
        cred_levels = [.99, .95, .9, .8, .7]
    marker_sizes = [15, 12, 9, 6, 3]

    cred_levels = np.asarray(cred_levels)
    symbol_size = None  # use previous size to detect change

    # ------------------------------------------------
    def select_symbol(p, prev_size):
        """Determine symbol size and legend text
        """
        i_size = np.nonzero(cred_levels < p)[0][0]
        size = marker_sizes[i_size]
        if size != prev_size:
            return size, f'> {cred_levels[i_size]:.0%}'
        else:
            return size, None
    # ------------------------------------------------

    fig, ax = plt.subplots()
    for ((i, j), p) in c_diff:
        symbol_size, label = select_symbol(p, symbol_size)
        if symbol_size > 0:
            s, = ax.plot(i, len(x_labels) - 1 - j, 'sr', markersize=symbol_size)
            if label is not None:
                s.set_label(label)
    ax.set_xlim([-0.5, len(x_labels) - 0.5])
    ax.set_ylim([-0.5, len(x_labels) - 0.5])
    ax.set_xticks(np.arange(len(x_labels)))
    ax.set_yticks(np.arange(len(x_labels)))
    ax.set_xticklabels(x_labels,
                       **_x_tick_style(x_labels)
                       )
    ax.set_yticklabels(x_labels[::-1],  # reversed order
                       rotation='horizontal',
                       horizontalalignment='right'
                       )
    if x_label is not None:
        ax.set_xlabel(x_label)
        ax.set_ylabel(x_label)
    ax.set_title(title)
    if len(c_diff) > 0:
        ax.legend(loc='best')
    fig.tight_layout()
    return FigureRef(ax, name=diff_label)


# --------------------------------------- Table formatting functions
def tab_correlation_matrix(cov, item_trait_map, name='Corr', header='Trait'):
    """Normalized correlation matrix between IRT traits corresponding to items.
    :param cov: estimated, possibly un-normalized, covariance matrix,
        possibly including traits that have NO item correspondence
    :param item_trait_map: 2D boolean array mapping trait to item
        item_trait_map[i, t] == True <=> t-th trait determines i-th item response
    :param name: (optional) string name of this table
    :param header: (optional) name for row and column index
    :return: a ResultTable instance
    """
    trait_sel = np.any(item_trait_map, axis=0)
    c = cov[:, trait_sel][trait_sel, :]
    std = np.sqrt(np.diag(c))
    # Normalize covariance matrix
    c /= std
    c /= std[:, None]
    trait_labels = make_trait_labels(item_trait_map)
    # *** use externally defined trait labels? ******
    trait_index = pd.Index(trait_labels, name=header)
    df = pd.DataFrame(c, columns=trait_index, index=trait_index)
    return ResultTable(df, name=name)


def tab_credible_diff(diff,
                      diff_name,
                      x_labels,
                      cred_header='Cred.',
                      x_label='Population',
                      and_head=' ',
                      and_label='AND'):
    """Create table with credible trait differences between populations
    represented by included group data sets
    :param diff: list of tuples ((i, j), p), indicating that
        x_labels[i] > x-labels[j] with joint credibility p, meaning
        prob{ x_labels[i] > s_labels[j] } AND all previous pairs } == p
        in quantity = diff_name
    :param diff_name: string name identifying the difference shown
    :param x_labels: list of category labels of compared data
    :param x_label: string label of category for the difference
    :param cred_header: string header of credibility column
    :param and_head: name of column with AND labels
    :param and_label: label indicating AND condition
    :return: a ResultTable instance with header lines + one line for each credible difference,
    """
    if len(diff) == 0:
        return None
    col = {and_head: [''] + (len(diff) -1) * [and_label]}
    col |= {x_label + ' >': [x_labels[i]
                             for ((i, j), p) in diff]}  # category with larger value
    col |= {x_label: [x_labels[j]
                      for ((i, j), p) in diff]}  # category with smaller value
    col |= {cred_header: [p for ((i, j), p) in diff]}  # credibility value in (0, 1)
    df = pd.DataFrame(col)
    # df.items.name = diff_name  # suppressed anyway, by DiffTable.save()
    return DiffTable(df, name=diff_name)


# ------------------------------------------ internal help functions:
def _nice_ticks(y_min, y_max):
    """Make nice sequence of equally spaced ticks
    with at most one decimal
    :param y_min: scalar axis min
    :param y_max: scalar axis max
    :return: t = array with tick values
        all(y_min <= t <= y_max
    """
    d = y_max - y_min
    if d < 1.:
        step = 0.1
    elif d < 2.:
        step = 0.2
    elif d < 5.:
        step = 0.5
    else:
        step = 1.
    return np.arange(np.ceil(y_min / step), np.floor(y_max / step) + 1) * step


def _x_tick_style(labels):
    """Select xtick properties to avoid tick-label clutter
    :param labels: list of tick label strings
    :return: dict with keyword arguments for set_xticklabels
    """
    maxL = max(len(l) for l in labels)
    rotate_x_label = maxL * len(labels) > 60
    if rotate_x_label:
         style = dict(rotation=25, horizontalalignment='right')
    else:
        style = dict(rotation='horizontal', horizontalalignment='center')
    return style


def make_trait_labels(item_trait_map):  # ******** -> ir_model ?
    """Prepare trait labels for plots and tables
    :param item_trait_map: 2D boolean array mapping trait for each item
    :return: list of strings
    """
    # *** should be done externally, by ir_model.OrdinalResponseModel ? ***
    trait_sel = np.any(item_trait_map, axis=0)
    item_trait_map = item_trait_map[:, trait_sel]
    n_items = len(item_trait_map)
    t_items = [np.arange(1, n_items + 1, dtype=int)[t_i]
               for t_i in item_trait_map.T]
    return ['Q(' + ','.join(f'{i}' for i in t_i) + ')'
            for t_i in t_items]


def _clean_file_name(s):
    """Make a string that can be used as file name
    :param s: string
    :return: clean_s,
        with whitespace replaced by _,
        and not-allowed chars removed
    """
    clean_s = s.replace(' ', '_')
    return clean_s.translate({ord(c): None for c in '(),.*'})


# ------------------------------------------ help functions:
def safe_file_path(p):
    """Ensure previously non-existing file path, to avoid over-writing,
    by adding a sequence number to the path stem
    :param p: file path
    :return: p_safe = similar file path with modified name
    """
    f_stem = p.stem
    f_suffix = p.suffix
    i = 0
    while p.exists():
        i += 1
        p = p.with_name(f_stem + f'-{i}' + f_suffix)
    return p


# -----------------------------------------------------
if __name__ == '__main__':
    print(_clean_file_name('asd asdf. (asdf)*, asdf'))