"""Main template script to analyze ordinal response data using Item Response Theory.
This template should be copied and edited by the user for the desired application.

The model estimates the distribution of one or more latent traits
that determine the probability of response alternatives in a questionnaire,
for one or several populations, represented by groups of respondents.

The results show trait distributions within and between populations,
for an unseen RANDOM INDIVIDUAL in each population, and
for the POPULATION MEAN for each population,
and reveals jointly credible differences between population means.

Populations should preferably be represented by large groups of respondents,
recruited at random from the populations of interest.

Analysis results show inter-individual variance,
correlations between separate traits, if more than one,
the mapping between traits and items,
and estimated response thresholds for all items in all populations,
but individual trait values are not displayed.

The analysis script always includes three main steps:
1: Define and collect item response data from one or more sources,
    and specify a top directory for all results.
2: Learn an OrdinalItemResponseModel instance using the collected response data.
3: Display the main characteristics of the learned model.

*** Version History
* Version 1.0.0:
2023-08-04, no standardization of trait scales in the learned model
2023-07-21, changed signature of ir_model.OrdinalItemResponseModel.initialize

* Version 0.6.0
2023-07-11, cleanup this script template with examples using new ir_source module
2023-07-06, result file format choice moved from ItemResponseDisplaySet.show() -> .save()
2023-07-01, new module ir_source for pandas.read_xxx for input files
2022-09-15, use pandas.read_xxx functions to access input data files.
2020-06-06, first standalone version for ItemResponseCalc package
2020-05-30, template example based on IOI-HA data analysis
"""
# -------- __main__ check to prevent multiprocessor sub-tasks to re-run this script
if __name__ == '__main__':

    import numpy as np
    import pickle
    from pathlib import Path
    import datetime as dt
    import logging
    # from sqlalchemy import create_engine  # to read from SQL database

    from ItemResponseCalc import __version__
    from ItemResponseCalc import ir_logging
    from ItemResponseCalc.item_response_data import Questionnaire
    from ItemResponseCalc.item_response_data import ItemResponseDataSet
    from ItemResponseCalc.ir_source import item_response_table, Tables
    # Tables used to join data from two or more sources as one group
    from ItemResponseCalc.ir_model import OrdinalItemResponseModel
    from ItemResponseCalc.ir_display import ItemResponseDisplaySet
    # from ItemResponseCalc.ir_latent import LatentLogistic, LatentNormal

    # -------------------------------- ItemResponseModel parameters:
    max_n_traits = 4  # None
    # = max number of traits to explain total set of item responses
    # = 1, if the test instrument is known to measure a uni-dimensional trait

    n_samples = 50
    # = number of sampled trait vectors for each respondent
    # = number of sampled threshold-defining parameters for each population,

    TEST_DOWNSAMPLE = 1
    # -> no down-sampling -> all records included
    # TEST_DOWNSAMPLE = 10
    # -> smaller data subset only for faster initial test run

    # ----------------------------- STEP 1: Define input sources and result path:

    timestamp_result = True  # Prevent over-writing result files
    # timestamp_result = False  # Repeated runs will save results in same directory

    TOP_PATH = Path.home() / 'Documents/LeijonKTH/heartech/HA-QualityRegistry'
    TOP_PATH = TOP_PATH / 'IRT-IOI-HA'  # or whatever...
    # Change this example to top-dir for everything to be read or written

    ioiha_data_path = TOP_PATH / 'IOI-HA-data'  # or whatever...
    # path to directory containing item response data files

    result_dir = TOP_PATH / 'IOI-HA-results'  # or whatever...
    # path where results will be saved, for several runs if needed
    result_dir = Path('../../../ItemResponseCalc_test') / 'ioiha-result'  # author TEST

    questionnaire_file = ioiha_data_path / 'IOI-HA-English.txt'  # or whatever...
    # text file containing the questions and response alternatives
    # If not available, a Questionnaire object must be created manually
    # as suggested below.

    if timestamp_result:
        timefmt = '{0.year}-{0.month:02}-{0.day:02}-{0.hour:02}{0.minute:02}'
        result_run = timefmt.format(dt.datetime.now())
        # -> name of sub-folder in result_dir
        save_dir = result_dir / result_run
    else:
        save_dir = result_dir
    save_dir.mkdir(parents=True, exist_ok=True)
    # sub-path for results of this particular run

    model_file = 'irt-model.pkl'
    # = name of saved model in save_dir

    log_file = 'run_irt_log.txt'
    # = name of log file saved in save_dir
    ir_logging.setup(save_dir / log_file)
    logger = logging.getLogger(__name__)
    # logger.setLevel(logging.DEBUG)  # only for test

    logger.info('*** Using ItemResponseCalc v.' + __version__)
    if TEST_DOWNSAMPLE > 1:
        logger.info(f'*** Test with down-sampling {TEST_DOWNSAMPLE}')

    def accept_record(r):
        """User-defined inclusion criterion for accepting a response record,
        applied to responses recoded as integer with origin 0,
        and missing responses encoded as -1.
        :param r: list with integer-encoded responses in ONE record from a source
        :return: boolean == True if the record is acceptable
        """
        n_missing = sum(r_i < 0 for r_i in r)
        return n_missing <= 3
    # ----------------------------------------------------------

    # ------------------ 1A: Define questionnaire instrument:
    # create a Questionnaire object to specify
    # number of items and response alternatives

    # Example: load from text file, edit as needed:
    test_instrument = Questionnaire.load(questionnaire_file)

    # if the text file is not available, create test_instrument manually, e.g.:
    # Example: seven items, all with 5 response levels, like the IOI-HA:
    # r_levels = [5, 5, 5, 5, 5, 5, 5]
    # = list with number of response levels, one element for each item
    # test_instrument = Questionnaire(item_response_levels=r_levels)

    # ------------------ 1B: Define sources of data to be included in analysis:
    data_groups = dict()  # space for all included groups

    # Example: Include xlsx file(s) from Hickson, Australia:
    # Edit as needed:
    au1_file = ioiha_data_path / 'Hickson' / 'Short_Eartrak AUS.xlsx'
    au1 = item_response_table(source=au1_file,
                              items={f'Q0{item}': list(range(1, 6))
                                     for item in range(1, 8)},  # as encoded in the xlsx file
                              accept_fcn=accept_record,  # None -> no restriction
                              sample_factor=TEST_DOWNSAMPLE,
                              index_col=0    # with respondent ID, to avoid duplicate records
                              )
    # NOTE: items = a dict with column header and a sequence of allowed ordinal responses,
    #   as encoded in this input source, not necessarily == Questionnaire.responses.
    # If index_col is defined, only the LAST record from each respondent is included.

    logger.info(f'AU-H-10: Using {au1_file}')
    data_groups['AU-H-10'] = au1

    # # Example: second input source: Combine two csv files into one group:
    # nle1_file = ioiha_data_path / 'Kramer' / 'moeder_final - kopieforArne.csv'
    # logger.info(f'NL-02: Using {nle1_file}')
    #
    # nle1 = item_response_table(source=nle1_file,
    #                            items={f'ioi_v{item}': list(range(1, 6))
    #                                   for item in range(1, 8)},     # as encoded in the csv file
    #                            accept_fcn=accept_record,
    #                            sample_factor=TEST_DOWNSAMPLE)   # no respondent ID given
    #
    # nle2_file = ioiha_data_path / 'Kramer' / 'NLSH-Kramer-T2IOI-HA.csv'
    # logger.info(f'NL-16: Using {nle2_file}')
    #
    # kramer2_columns = {'T2IOIHA1': range(5),  # responses coded as 0,.., 4
    #                    'T2IOIHA2': range(1, 6),  # coded as 1,.., 5
    #                    'T2IOIHA3': range(1, 6),
    #                    'T2IOIHA4': range(5),  # coded as 0,.., 4
    #                    'T2IOIHA5': range(1, 6),
    #                    'T2IOIHA6': range(1, 6),
    #                    'T2IOIHA7': range(1, 6)}
    #
    # nle2 = item_response_table(source=nle2_file,
    #                            items=kramer2_columns,
    #                            accept_fcn=accept_record,
    #                            sample_factor=TEST_DOWNSAMPLE)
    # data_groups['NL-02-16'] = Tables(nle1, nle2)

    # SQL example: access data from a database:
    # engine = create_engine("sqlite+pysqlite:///" + str(sql_path / 'testDataBase.db'))
    # ir_sql = item_response_table(source=engine,
    #                              sql='ioiha',  # table name in database
    #                              index_col='EarRowId',
    #                              items={c: [str(i) for i in range(1, 6)]
    #                                     for c in column_names}
    #                              )  # NOTE: string-encoded responses in this DB
    # data_groups['test'] = ir_sql

    # ------------------ 1C: Collect all into ONE DataSet object:

    ids = ItemResponseDataSet(questionnaire=test_instrument,
                              groups=data_groups)
    # NOT YET reading any response data
    # In case of any input error, it will show here:
    logger.info('Item Response Data = \n' + repr(ids))

    # (Optional) Show response counts, to verify that input was OK
    r_counts = ids.response_counts()
    # = list with one TableRef object for each questionnaire item
    logger.info('Response Counts =\n'
                 + '\n\n'.join(item.question + '\n' + c_df.to_string()
                               for (item, c_df) in zip(ids.questionnaire.items,
                                                       r_counts)
                               )
                 )
    # ----- Optionally, save item count tables in separate files, too
    # item_counts = save_dir / 'data_counts'
    # item_counts.mkdir(parents=True, exist_ok=True)
    # for item_i in r_counts:
    #     item_i.save(item_counts, table_format='csv')    # for input to other package

    # ------------------ STEP 2: Learn ItemResponseModel from data:

    irm = OrdinalItemResponseModel.initialize(ids,
                                              # latent_class=LatentLogistic,    # default
                                              # n_traits=max_n_traits,  # default = n_items
                                              n_samples=n_samples,
                                              # restrict_traits=True,  # default
                                              # restrict_threshold=False,  # default
                                              # threshold_pseudo_factor=1.,   # default
                                              # trait_scale=3.,  # default
                                              )
    # restrict_traits = True -> Global mean trait fixed at zero.
    # restrict_threshold = True -> Middle response threshold fixed at zero for all items.
    # NOTE: Even with restrict_threshold = False,
    #   response thresholds must be rather similar across populations,
    #   although some variations are allowed. Therefore,
    #   the model includes a number of "pseudo_groups" = threshold_pseudo_factor * real n_groups,
    #   all with ZERO threshold deviations from the global mean.
    #   Larger threshold_pseudo_factor -> smaller threshold variations between populations.

    logger.info(f'Learning model with max {irm.n_traits} traits'
                 + f' for {irm.n_groups} groups'
                 + f' with {irm.n_subjects} included respondent records in total')
    logger.info(f'The model uses {n_samples} samples for each respondent group')

    LL = irm.learn(max_hours=0, max_minutes=30)
    # *** Might take hours, trying with shorter time limit first.
    # When learning is complete, it will finish before the time limit.

    logger.info(f'Learned model with {irm.n_groups} groups'
                 + f' with {irm.n_subjects} subjects in total')
    # logger.info('Log Likelihood: ' + np.array2string(np.array(LL), precision=1))

    # ------------------ Optionally, save model for later display generation
    with (save_dir / model_file).open('wb') as f:
        pickle.dump(irm, f)
    logger.info(f'Model saved in {save_dir}')
    logger.info('Learned model = \n' + repr(irm))

    irm.prune()  # keep only traits that were really needed to model the data

    # ------------------ STEP 3: Display Model Results:
    # mapping_item used to display trait scales by reference to ONE item
    ir_display = ItemResponseDisplaySet.show(irm,
                                             mapping_item=-1,  # last questionnaire item
                                             percentiles=[2.5, 50., 97.5],
                                             mpl_params={'figure.max_open_warning': 0,  # suppress warning
                                                         'figure.autolayout': True,  # -> tight layout
                                                         'axes.labelsize': 'x-large'},  # -> matplotlib.rcParam
                                             # mpl_style='my_style_sheet',
                                             # ... any other ema_display.FMT settings
                                             # ... any ema_display_format.FMT settings
                                             )
    ir_display.save(save_dir,
                    figure_format = 'pdf',  # any format that Matplotlib can handle
                    table_format = 'txt',   # any format that Pandas can handle
                    float_format = '%.2f')  # any other parameter(s) for pandas.write_xxx

    # --------------------------- (optionally) save in other format(s), too:
    # ir_display.save(save_dir,
    #          table_format='csv',  # only tables, for input to other package
    #          float_format='%.4f',
    #          )
    # ir_display.save(save_dir,
    #          figure_format='eps',  # only figures, for input to other package
    #          )

    logger.info(f'All results saved in {save_dir}')

    # ------------------------------ Instrument Reliability Measures:
    mi = irm.instrument_mutual_information()  # bits
    person_separation = 2.**mi
    logger.info(f'Instrument-trait information = {mi:.2f} bits. '
                + f'Separation ability: {person_separation:.1f} person categories.')
    rho = 1. - 2**(-2 * mi)
    logger.info(f'Equivalent Reliability Coefficient= {rho:.3f}')

    # ------------------ (Optional) PCA of inter-individual trait covariance within populations
    if irm.n_traits > 1:
        cov_within = irm.predictive_individual_cov()
        (eig_val, eig_vec) = np.linalg.eigh(cov_within)
        logger.debug('Cov eig_val= ' +
                      np.array2string(eig_val, precision=3))
        logger.debug('Cov eig_vec=\n' +
                      np.array2string(eig_vec, precision=3))
        eig_val_cum = np.cumsum(eig_val[::-1]) / np.sum(eig_val)
        logger.info(f'One, Two, etc Principal Trait Factors: ' +
                     ', '.join(f'{ev:.1%}'
                               for ev in eig_val_cum) +
                     ', of Variance within Populations')

    logging.shutdown()
