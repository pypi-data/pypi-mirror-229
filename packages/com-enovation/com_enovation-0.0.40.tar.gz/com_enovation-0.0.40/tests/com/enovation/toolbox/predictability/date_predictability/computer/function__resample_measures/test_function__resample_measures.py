from inspect import stack
from unittest import TestCase
from logging import Logger, getLogger

from pandas import DataFrame

from com_enovation.helper.pandas_dataframe_typer import PandasDataframeTyper
from com_enovation.toolbox.predictability.dp_date_predictability.dp_computer import DatePredictabilityComputer


class TestFunctionResampleMeasures(TestCase):

    _logger: Logger = getLogger(__name__)

    def test_vanilla(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        the_df_dataset: DataFrame = DataFrame(
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
                ["abc", "2021-5-28", "2021-5-27"],
                ["abc", "2021-5-29", "2021-5-20"],
                ["abc", "2021-6-6", "2021-5-19"],

                ["bcd", "2021-6-6", "2021-5-19"],

                ["def", "2019-6-6", "2020-5-19"],
                ["def", "2021-6-6", "2021-5-19"],
            ]
        )

        # We type the columns
        the_df_dataset = PandasDataframeTyper.type(
            df_to_type=the_df_dataset,
            dict_columns_to_type={
                DatePredictabilityComputer.str__input__column_label__date: PandasDataframeTyper.str__type__date,
                DatePredictabilityComputer.str__input__column_label__measure: PandasDataframeTyper.str__type__date,
            },
            b_strict=False
        )

        the_df_resampled_measures: DataFrame = DatePredictabilityComputer()._resample_measures(
            df_measures=the_df_dataset
        )

        self.assertEqual(
            first=(775, 3),
            second=the_df_resampled_measures.shape,
            msg="unexpected shape"
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
