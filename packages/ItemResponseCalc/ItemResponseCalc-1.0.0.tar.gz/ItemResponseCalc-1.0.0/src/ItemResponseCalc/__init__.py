"""Package ItemResponseCalc implements Bayesian analysis of
subjective responses to items in a questionnaire,
using Item Response Theory (IRT) applied with
the Graded Response Model (Samejima, 1997; Fox, 2010).

This package is only intended for the analysis of data with ORDINAL responses,
e.g., the IOI-HA questionnaire for users' satisfaction with their hearing aids.

The IRT Graded Response Model treats subjects' responses
as determined by the outcome of a latent individual trait variable,
i.e., similar to the latent internal "sensation"
variable assumed to determine responses in psycho-physical experiments.
This package uses a logistic distribution for the latent variables.

Each questionnaire item corresponds to exactly ONE individual trait variable,
but each trait variable may determine the subject's responses to several items.

Therefore, for a questionnaire with I separate items,
the model can learn D <= I trait variables, based on the observed responses.
The model automatically learns how many
different trait variables are needed to 'explain' the recorded data.

NOTE: In most modules of this package,
the ordinal response to the i-th item is encoded as
an integer in {0, 1,..., L_i-1},
where L_i = the number of ordinal response levels for the i-th item.
Any value outside this range is interpreted as a missing response.

However, in data files with recorded responses,
the recorded responses are sometimes encoded as integers in {1, 2,..., L_i},
with missing values encoded as zero.
Other response files may instead store the actual text labels
on the response alternatives in the questionnaire.

Therefore, the package user must specify the response encoding
separately for each input data source.

*** Usage

Copy the template script `run_irt.py` to your working directory, rename it, and
edit the copy as suggested in the template, to specify
    - your experimental layout,
    - your input data file(s),
    - a directory where all output result files will be stored.

*** Main Modules

ir_base:
    General help methods to access sampled data

item_response_data:
    Interface to one or several data sets containing individual responses
    from respondents recruited from one or more separate population(s).
    See this module for information about input files and data formats.

ir_model:
    The core of the Bayesian IRT model adapted to all observed data.

ir_global:
    global parameter distributions, common for all included populations.

ir_graded_response_prob:
    Calculates response probabilities with the Graded Response Model

ir_group:
    Classes representing individual- and population-specific models
    defining trait distributions for each individual in ONE group of respondents,
    and response thresholds for the population represented by the group.

ir_display:
    Functions and classes to display all analysis results as figures and tables.
    
ir_source:
    Implements access methods for input data in several source types,
    e.g., Excel or CSV files, or SQL database,
    using reader functions available in package Pandas,
    or a similar user-defined reader function.

ir_thresholds:
    Mapping response thresholds from internal model parameters

Analysis results are saved as figures and tables in the selected result directory.
After running an analysis, the logging output briefly explains
the analysis results presented in figures and tables.

*** References
* For Version >=1.0:
A. Leijon: Analysis of Ordinal Response Data using Bayesian Item Response Theory package ItemResponseCalc.
    Documentation report with all math details for the new model structure

* For Version <= 0.6:
A. Leijon, H. Dillon, L. Hickson, M. Kinkel, S. E. Kramer, and P. Nordqvist.
    Analysis of data from the international outcome inventory for hearing aids (IOI-HA)
    using Bayesian item response theory. Int J Audiol 60(2):81–88, 2020.
    doi: 10.1080/14992027.2020.1813338
J.-P. Fox (2010). *Bayesian Item Response Modeling: Theory and Applications*.
    Statistics for Social and Behavioral Sciences. Springer.
G. N. Masters (1982). A Rasch model for partial credit scoring.
    *Psychometrika*, 47(2):149–174.
F. Samejima (1997). Graded response model.
    In W. J. v. D. Linden and R. K. Hambleton, eds.,
    *Handbook of Modern Item Response Theory*, p. 85–100. Springer, New York.


*** Version History
* Version 1.0.0: New model structure. Item response thresholds are separate for each group.
    Thus, differing response patterns between included groups can be "explained"
    partly by their different interpretations of response categories,
    rather than by real perceptual differences between populations.
    This is a reasonable assumption, in particular, if respondents from different populations
    have used different language versions of the questionnaire items.

* Version 0.6.0:
2023-07-07, using package pandas to access input data files, and for tabulated results.

* Version 0.5:
2020-06-xx, prepare to allow different item response probability models-
2020-06-08, first version uploaded to PyPi, tested with several IOI-HA data sets.
2019-08-24, first functional version with automatic selection of trait dimensionality.
"""

__name__ = 'ItemResponseCalc'
__version__ = '1.0.0'
__all__ = ['__version__', 'run_irt']


