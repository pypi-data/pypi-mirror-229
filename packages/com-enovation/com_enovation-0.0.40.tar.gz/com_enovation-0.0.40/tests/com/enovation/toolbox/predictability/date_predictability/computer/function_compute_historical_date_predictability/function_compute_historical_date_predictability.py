from datetime import datetime
from inspect import stack
from unittest import TestCase
from logging import Logger, getLogger

from pandas import DataFrame
from pandas._testing import assert_frame_equal

from com_enovation.toolbox import PredictabilityBean
from com_enovation.toolbox.predictability.dp_date_predictability.dp_computer import DatePredictabilityComputer


class TestFunctionComputeHistoricalDatePredictability(TestCase):
    """
    Test public fonctions that compute historical date predictability, with or without resampling
    """

    _logger: Logger = getLogger(__name__)

    df_the_test_date: DataFrame = DataFrame(
        columns=[
            DatePredictabilityComputer.str__input__column_label__key,
            DatePredictabilityComputer.str__input__column_label__date,
            DatePredictabilityComputer.str__input__column_label__measure,
            DatePredictabilityComputer.str__output__column_label__predictability,
        ],
        data=[
            ['abc', '2021-4-26', '2021-5-22', 1],
            ['abc', '2021-4-27', '2021-6-5', 0.65],
            ['abc', '2021-4-30', '2021-6-3', 0.879364514890831],
            ['abc', '2021-5-1', '2021-6-4', 0.91139492876335],
            ['abc', '2021-5-6', '2021-5-29', 0.778029804255193],
            ['abc', '2021-5-7', '2021-5-25', 0.620045338991703],
            ['abc', '2021-5-9', '2021-5-21', 0.41092854342655],
            ['abc', '2021-5-11', '2021-5-19', 0.305391170303002],
            ['abc', '2021-5-13', '2021-5-16', 0.106022408963585],
            ['abc', '2021-5-16', '2021-5-17', 0.261746031746032],
            ['abc', '2021-5-18', '2021-5-21', 0.452146808850176],
            ['abc', '2021-5-23', '2021-5-14', 0.0252057613168724],
            ['abc', '2021-5-25', '2021-5-27', 0.45598774482143],
            ['abc', '2021-5-29', '2021-5-20', 0.304694618503066],
            ['abc', '2021-6-6', '2021-5-19', 0.3877575869183],
        ]
    )

    df_the_expected_stats: DataFrame = DataFrame(
        columns=[
            DatePredictabilityComputer.str__input__column_label__key,
            DatePredictabilityComputer.str__statistics__column_label__measure_count,
            DatePredictabilityComputer.str__statistics__column_label__date_first,
            DatePredictabilityComputer.str__statistics__column_label__date_last,
            DatePredictabilityComputer.str__statistics__column_label__measure_min,
            DatePredictabilityComputer.str__statistics__column_label__measure_max,
            DatePredictabilityComputer.str__statistics__column_label__measure_first,
            DatePredictabilityComputer.str__statistics__column_label__measure_last,
            DatePredictabilityComputer.str__statistics__column_label__predictability_last
        ],
        data=[[
            'abc',                  # key
            15,                     # measure_count
            datetime(2021, 4, 26),  # date_first
            datetime(2021, 6, 6),   # date_last
            datetime(2021, 5, 14),  # measure_min
            datetime(2021, 6, 5),   # measure_max
            datetime(2021, 5, 22),  # measure_first
            datetime(2021, 5, 19),  # measure_last
            0.3877575869183         # predictability_last
        ]]
    )

    def test_01_resampling(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # 1. We call the function
        the_bean: PredictabilityBean = DatePredictabilityComputer().compute_historical_date_predictability(
            df_measures=self.df_the_test_date[[
                DatePredictabilityComputer.str__input__column_label__key,
                DatePredictabilityComputer.str__input__column_label__date,
                DatePredictabilityComputer.str__input__column_label__measure,
            ]],
            b_resample=True
        )

        # 2. We check the historical data frame
        df_the_historical: DataFrame = the_bean.df_historical

        for t_i_row in self.df_the_test_date.itertuples():
            str_the_key: str = getattr(t_i_row, DatePredictabilityComputer.str__input__column_label__key)
            dt_the_date: datetime = getattr(t_i_row, DatePredictabilityComputer.str__input__column_label__date)

            f_the_expected_predictability: float = getattr(
                t_i_row,
                DatePredictabilityComputer.str__output__column_label__predictability
            )

            f_the_computed_predictability: float = df_the_historical[
                (df_the_historical[DatePredictabilityComputer.str__input__column_label__key] == str_the_key)
                & (df_the_historical[DatePredictabilityComputer.str__input__column_label__date] == dt_the_date)
            ][DatePredictabilityComputer.str__output__column_label__predictability].iloc[0]

            self.assertAlmostEqual(
                first=f_the_expected_predictability,
                second=f_the_computed_predictability,
                msg=f"Incorrect computation '{f_the_computed_predictability}' vs expected "
                    f"'{f_the_expected_predictability}' for record:"
                    f"\n\t- key: '{str_the_key}'"
                    f"\n\t- date: '{dt_the_date}'"
            )

        # 3. We check the statistics
        assert_frame_equal(
            left=self.df_the_expected_stats,
            right=the_bean.df_by_key,
            obj=f"The computation did not return expected statistics",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_02_no_resampling(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # 1. We call the function
        the_bean: PredictabilityBean = DatePredictabilityComputer().compute_historical_date_predictability(
            df_measures=self.df_the_test_date[[
                DatePredictabilityComputer.str__input__column_label__key,
                DatePredictabilityComputer.str__input__column_label__date,
                DatePredictabilityComputer.str__input__column_label__measure,
            ]],
            b_resample=False
        )

        # 2. We check the historical data frame
        df_the_historical: DataFrame = the_bean.df_historical

        for t_i_row in self.df_the_test_date.itertuples():
            str_the_key: str = getattr(t_i_row, DatePredictabilityComputer.str__input__column_label__key)
            dt_the_date: datetime = getattr(t_i_row, DatePredictabilityComputer.str__input__column_label__date)

            f_the_expected_predictability: float = getattr(
                t_i_row,
                DatePredictabilityComputer.str__output__column_label__predictability
            )

            f_the_computed_predictability: float = df_the_historical[
                (df_the_historical[DatePredictabilityComputer.str__input__column_label__key] == str_the_key)
                & (df_the_historical[DatePredictabilityComputer.str__input__column_label__date] == dt_the_date)
            ][DatePredictabilityComputer.str__output__column_label__predictability].iloc[0]

            self.assertAlmostEqual(
                first=f_the_expected_predictability,
                second=f_the_computed_predictability,
                msg=f"Incorrect computation '{f_the_computed_predictability}' vs expected "
                    f"'{f_the_expected_predictability}' for record:"
                    f"\n\t- key: '{str_the_key}'"
                    f"\n\t- date: '{dt_the_date}'"
            )

        # 3. We check the statistics
        assert_frame_equal(
            left=self.df_the_expected_stats,
            right=the_bean.df_by_key,
            obj=f"The computation did not return expected statistics",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
