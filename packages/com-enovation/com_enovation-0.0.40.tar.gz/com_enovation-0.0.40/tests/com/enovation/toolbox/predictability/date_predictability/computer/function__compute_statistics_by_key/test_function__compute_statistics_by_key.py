from inspect import stack
from unittest import TestCase
from logging import Logger, getLogger

from pandas import DataFrame
from pandas.testing import assert_frame_equal

from com_enovation.helper.pandas_dataframe_typer import PandasDataframeTyper
from com_enovation.toolbox.predictability.dp_date_predictability.dp_computer import DatePredictabilityComputer

class TestFunctionComputeStatisticsByKey(TestCase):

    _logger: Logger = getLogger(__name__)

    def test_one(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        """
        ["abc", "26-Apr-2021", "22-May-2021"],
        ["abc", "27-Apr-2021", "05-Jun-2021"],
        ["abc", "30-Apr-2021", "03-Jun-2021"],
        ["abc", "01-May-2021", "04-Jun-2021"],
        ["abc", "06-May-2021", "29-May-2021"],
        ["abc", "07-May-2021", "25-May-2021"],
        ["abc", "09-May-2021", "21-May-2021"],
        ["abc", "11-May-2021", "19-May-2021"],
        ["abc", "13-May-2021", "16-May-2021"],
        ["abc", "16-May-2021", "17-May-2021"],
        ["abc", "18-May-2021", "21-May-2021"],
        ["abc", "23-May-2021", "14-May-2021"],
        ["abc", "25-May-2021", "27-May-2021"],
        ["abc", "29-May-2021", "20-May-2021"],
        ["abc", "06-Jun-2021", "19-May-2021"],

        ["bcd", "06-Jun-2021", "19-May-2021"],

        ["def", "26-Apr-2021", "22-May-2021"],
        ["def", "27-Apr-2021", "05-Jun-2021"],
        ["def", "30-Apr-2021", "03-Jun-2021"],
        ["def", "01-May-2021", "04-Jun-2021"],
        ["def", "06-May-2021", "29-May-2021"],
        ["def", "07-May-2021", "25-May-2021"],
        ["def", "09-May-2021", "21-May-2021"],
        ["def", "11-May-2021", "19-May-2021"],
        """
        the_df_by_measure: DataFrame = PandasDataframeTyper.type(
            df_to_type=DataFrame(
                columns=[
                    DatePredictabilityComputer.str__input__column_label__key,
                    DatePredictabilityComputer.str__input__column_label__date,
                    DatePredictabilityComputer.str__input__column_label__measure,
                ],
                data=[
                    ["abc", "2021-4-26", "2021-5-22"],
                    ["abc", "2021-4-27", "2021-6-5"],
                    ["abc", "2021-4-30", "2021-6-3"],
                    ["abc", "2021-5-1", "2021-6-4"],
                    ["abc", "2021-5-6", "2021-5-29"],
                    ["abc", "2021-5-7", "2021-5-25"],
                    ["abc", "2021-5-9", "2021-5-21"],
                    ["abc", "2021-5-11", "2021-5-19"],
                    ["abc", "2021-5-13", "2021-5-16"],
                    ["abc", "2021-5-16", "2021-5-17"],
                    ["abc", "2021-5-18", "2021-5-21"],
                    ["abc", "2021-5-23", "2021-5-14"],
                    ["abc", "2021-5-25", "2021-5-27"],
                    ["abc", "2021-5-29", "2021-5-20"],
                    ["abc", "2021-6-6", "2021-5-19"],

                    ["bcd", "2021-6-6", "2021-5-19"],

                    ["def", "2021-4-26", "2021-5-22"],
                    ["def", "2021-4-27", "2021-6-5"],
                    ["def", "2021-4-30", "2021-6-3"],
                    ["def", "2021-5-1", "2021-6-4"],
                    ["def", "2021-5-6", "2021-5-29"],
                    ["def", "2021-5-7", "2021-5-25"],
                    ["def", "2021-5-9", "2021-5-21"],
                    ["def", "2021-5-11", "2021-5-19"]
                ]
            ),
            dict_columns_to_type={
                DatePredictabilityComputer.str__input__column_label__date: PandasDataframeTyper.str__type__date,
                DatePredictabilityComputer.str__input__column_label__measure: PandasDataframeTyper.str__type__date,
            },
            b_strict=False
        )

        the_df_historical: DataFrame = PandasDataframeTyper.type(
            df_to_type=DataFrame(
                columns=[
                    DatePredictabilityComputer.str__input__column_label__key,
                    DatePredictabilityComputer.str__input__column_label__date,
                    DatePredictabilityComputer.str__input__column_label__measure,

                    # expected result
                    DatePredictabilityComputer.str__output__column_label__predictability,
                ],
                data=[
                    ['abc', '2021-4-26', '2021-5-22', 1.0],                     # Checked through excel spreadsheet
                    ['abc', '2021-4-27', '2021-6-5', 0.825],                    # Checked
                    ['abc', '2021-4-28', '2021-6-5', 0.883333333333333],        # Checked
                    ['abc', '2021-4-29', '2021-6-5', 0.9125],                   # Checked
                    ['abc', '2021-4-30', '2021-6-3', 0.903491611912665],        # Checked
                    ['abc', '2021-5-1', '2021-6-4', 0.926162440636125],
                    ['abc', '2021-5-2', '2021-6-4', 0.9367106634023928],
                    ['abc', '2021-5-3', '2021-6-4', 0.9446218304770937],
                    ['abc', '2021-5-4', '2021-6-4', 0.9507749604240833],
                    ['abc', '2021-5-5', '2021-6-4', 0.9556974643816749],
                    ['abc', '2021-5-6', '2021-5-29', 0.798208912959267],        # Checked
                    ['abc', '2021-5-7', '2021-5-25', 0.6517082274090612],
                    ['abc', '2021-5-8', '2021-5-25', 0.6784999022237488],
                    ['abc', '2021-5-9', '2021-5-21', 0.4530050760389395],
                    ['abc', '2021-5-10', '2021-5-21', 0.4894714043030102],
                    ['abc', '2021-5-11', '2021-5-19', 0.3488042221590647],
                    ['abc', '2021-5-12', '2021-5-19', 0.38710985614970794],
                    ['abc', '2021-5-13', '2021-5-16', 0.155687830687831],       # Checked
                    ['abc', '2021-5-14', '2021-5-16', 0.200125313283208],
                    ['abc', '2021-5-15', '2021-5-16', 0.24011904761904762],
                    ['abc', '2021-5-16', '2021-5-17', 0.2969009826152683],
                    ['abc', '2021-5-17', '2021-5-17', 0.32886002886002885],
                    ['abc', '2021-5-18', '2021-5-21', 0.47596651281321234],
                    ['abc', '2021-5-19', '2021-5-21', 0.49780124144599514],
                    ['abc', '2021-5-20', '2021-5-21', 0.5178891917881553],
                    ['abc', '2021-5-21', '2021-5-21', 0.536431915180919],       # Checked
                    ['abc', '2021-5-22', '2021-5-21', 0.5536011035075512],
                    ['abc', '2021-5-23', '2021-5-14', 0.06001984126984127],
                    ['abc', '2021-5-24', '2021-5-14', 0.09243295019157087],
                    ['abc', '2021-5-25', '2021-5-27', 0.47412148666071574],
                    ['abc', '2021-5-26', '2021-5-27', 0.4910853096716604],
                    ['abc', '2021-5-27', '2021-5-27', 0.506988893744421],
                    ['abc', '2021-5-28', '2021-5-27', 0.5219286242370144],
                    ['abc', '2021-5-29', '2021-5-20', 0.3251447767823873],
                    ['abc', '2021-5-30', '2021-5-20', 0.3444263545886048],
                    ['abc', '2021-5-31', '2021-5-20', 0.36263673362781],        # Checked
                    ['abc', '2021-6-1', '2021-5-20', 0.3798627678540856],
                    ['abc', '2021-6-2', '2021-5-20', 0.39618216870003076],
                    ['abc', '2021-6-3', '2021-5-20', 0.41166467719490174],
                    ['abc', '2021-6-4', '2021-5-20', 0.4263730602650292],
                    ['abc', '2021-6-5', '2021-5-20', 0.4403639612341748],
                    ['abc', '2021-6-6', '2021-5-19', 0.4023347872297693],       # Checked

                    ["bcd", "2021-6-6", "2021-5-19", 1.0], # ["bcd", "06-Jun-2021", "19-May-2021", 1.0],

                    ['def', '2021-4-26', '2021-5-22', 1.0],                     # Checked through excel spreadsheet
                    ['def', '2021-4-27', '2021-6-5', 0.825],                    # Checked
                    ['def', '2021-4-28', '2021-6-5', 0.883333333333333],        # Checked
                    ['def', '2021-4-29', '2021-6-5', 0.9125],                   # Checked
                    ['def', '2021-4-30', '2021-6-3', 0.903491611912665],        # Checked
                    ['def', '2021-5-1', '2021-6-4', 0.926162440636125],
                    ['def', '2021-5-2', '2021-6-4', 0.9367106634023928],
                    ['def', '2021-5-3', '2021-6-4', 0.9446218304770937],
                    ['def', '2021-5-4', '2021-6-4', 0.9507749604240833],
                    ['def', '2021-5-5', '2021-6-4', 0.9556974643816749],
                    ['def', '2021-5-6', '2021-5-29', 0.798208912959267],        # Checked
                    ['def', '2021-5-7', '2021-5-25', 0.6517082274090612],
                    ['def', '2021-5-8', '2021-5-25', 0.6784999022237488],
                    ['def', '2021-5-9', '2021-5-21', 0.4530050760389395],
                    ['def', '2021-5-10', '2021-5-21', 0.4894714043030102],
                    ['def', '2021-5-11', '2021-5-19', 0.3488042221590647],
                ]
            ),
            dict_columns_to_type={
                DatePredictabilityComputer.str__input__column_label__date: PandasDataframeTyper.str__type__date,
                DatePredictabilityComputer.str__input__column_label__measure: PandasDataframeTyper.str__type__date,
            },
            b_strict=False
        )

        the_df_by_key: DataFrame = PandasDataframeTyper.type(
            df_to_type=DataFrame(
                columns=[
                    DatePredictabilityComputer.str__input__column_label__key,
                    DatePredictabilityComputer.str__statistics__column_label__measure_count,
                    DatePredictabilityComputer.str__statistics__column_label__date_first,
                    DatePredictabilityComputer.str__statistics__column_label__date_last,
                    DatePredictabilityComputer.str__statistics__column_label__measure_first,
                    DatePredictabilityComputer.str__statistics__column_label__measure_last,
                    DatePredictabilityComputer.str__statistics__column_label__measure_min,
                    DatePredictabilityComputer.str__statistics__column_label__measure_max,
                    DatePredictabilityComputer.str__statistics__column_label__predictability_last
                ],
                data=[
                    # key   #   date min     date max    measure 1s    measure lst  measure min  measure max
                    ["abc", 15, '2021-4-26', '2021-6-6', '2021-5-22',  '2021-5-19', '2021-5-14', '2021-6-5',
                     0.4023347872297693],
                    ["bcd", 1,  '2021-6-6',  '2021-6-6', '2021-5-19',  '2021-5-19', '2021-5-19', '2021-5-19', 1.0],
                    ["def", 8,  '2021-4-26', '2021-5-11', '2021-5-22', '2021-5-19', '2021-5-19', '2021-6-5',
                     0.3488042221590647],
                ]
            ),
            dict_columns_to_type={
                DatePredictabilityComputer.str__statistics__column_label__date_first:
                    PandasDataframeTyper.str__type__date,
                DatePredictabilityComputer.str__statistics__column_label__date_last:
                    PandasDataframeTyper.str__type__date,
                DatePredictabilityComputer.str__statistics__column_label__measure_first:
                    PandasDataframeTyper.str__type__date,
                DatePredictabilityComputer.str__statistics__column_label__measure_last:
                    PandasDataframeTyper.str__type__date,
                DatePredictabilityComputer.str__statistics__column_label__measure_min:
                    PandasDataframeTyper.str__type__date,
                DatePredictabilityComputer.str__statistics__column_label__measure_max:
                    PandasDataframeTyper.str__type__date,
            },
            b_strict=False
        )

        df_the_return: DataFrame = DatePredictabilityComputer().compute_statistics_by_key(
            df_measures=the_df_by_measure,
            df_historical_predictability=the_df_historical,
        )

        assert_frame_equal(
            left=the_df_by_key,
            right=df_the_return,
            obj=f"The computation did not return expected results",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
