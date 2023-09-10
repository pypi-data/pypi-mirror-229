from datetime import datetime
from inspect import stack
from unittest import TestCase
from logging import Logger, getLogger

from pandas import DataFrame
from scipy.special import psi

from com_enovation.helper.pandas_dataframe_typer import PandasDataframeTyper
from com_enovation.toolbox.predictability.dp_date_predictability.dp_computer import DatePredictabilityComputer


class TestFunctionComputeSpotPredictabilityForAGivenKey(TestCase):
    """
    We test all the combinations when calling the function _compute_spot_predictability_for_a_given_key_no_resample.

    Each test function executes 3 test cases:
    - For given start and end date that will be the same across 3 test cases
    - We first compute predictability with a measure (22-May) > last measure (19-May)
    - We then compute predictability with a measure spot§on (aka 19-May), expected to be 1
    - We eventually conpute predictability with a measure (16-May) < last measure (19-May).

    In addition to call function _compute_spot_predictability_for_a_given_key_no_resample, we call the psi special
    function. This can be useful to debug in case of any issue.
    """

    _logger: Logger = getLogger(__name__)

    def function_to_test(
            self,
            s_test_case: str,
            dt_start: datetime,
            dt_end: datetime,
            f_aggregated_predictability: float,
            i_a_west: int = None,
            i_b_west: int = None,
            i_m_west: int = None,
            f_psi_result_west: float = None,
            i_a_east: int = None,
            i_b_east: int = None,
            i_m_east: int = None,
            f_psi_result_east: float = None
    ):
        """
        Helper function to easily execute the various combinations:
        - The effective call to the function compute spot predictability, in north, south and spot-on (aka when
          measure = last measure)
        - And the calls to the psi function, both in the western and eastern cones.
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We instantiate the dataframes
        the_df_dataset_north: DataFrame = DataFrame(
            columns=[
                DatePredictabilityComputer.str__input__column_label__date,
                DatePredictabilityComputer.str__input__column_label__measure,
                "date_end",
                DatePredictabilityComputer.str__output__column_label__duration
            ],
            data=[
                [dt_start, datetime(2021, 5, 22), dt_end, (dt_end-dt_start).days],
                [dt_end,  datetime(2021, 5, 19), dt_end, 0],
            ]
        )
        the_df_dataset_spot_on: DataFrame = DataFrame(
            columns=[
                DatePredictabilityComputer.str__input__column_label__date,
                DatePredictabilityComputer.str__input__column_label__measure,
                "date_end",
                DatePredictabilityComputer.str__output__column_label__duration
            ],
            data=[
                [dt_start, datetime(2021, 5, 19), dt_end, (dt_end-dt_start).days],
                [dt_end,  datetime(2021, 5, 19), dt_end, 0],
            ]
        )
        the_df_dataset_south: DataFrame = DataFrame(
            columns=[
                DatePredictabilityComputer.str__input__column_label__date,
                DatePredictabilityComputer.str__input__column_label__measure,
                "date_end",
                DatePredictabilityComputer.str__output__column_label__duration
            ],
            data=[
                [dt_start, datetime(2021, 5, 16), dt_end, (dt_end-dt_start).days],
                [dt_end,  datetime(2021, 5, 19), dt_end, 0],
            ]
        )

        # We call the function 3 times
        f_the_computed_aggregated_predictability_north: float = \
            DatePredictabilityComputer()._compute_date_predictability_for_a_given_key_not_resampled(
                df_measures=the_df_dataset_north
            )
        f_the_computed_aggregated_predictability_spot_on: float = \
            DatePredictabilityComputer()._compute_date_predictability_for_a_given_key_not_resampled(
                df_measures=the_df_dataset_spot_on
            )
        f_the_computed_aggregated_predictability_south: float = \
            DatePredictabilityComputer()._compute_date_predictability_for_a_given_key_not_resampled(
                df_measures=the_df_dataset_south
            )

        # We test the psi function
        if f_psi_result_west:
            self.assertAlmostEqual(
                f_psi_result_west,
                (i_b_west-i_a_west)*(psi(i_b_west)-psi(i_b_west+i_m_west))+i_m_west,
                msg=f"Test Case '{s_test_case}': the psi function does not return expected results for parameters:"
                    f"\n\t-i_a_west='{i_a_west}'"
                    f"\n\t-i_b_west='{i_b_west}'"
                    f"\n\t-i_m_west='{i_m_west}'",
            )
        if f_psi_result_east:
            self.assertAlmostEqual(
                f_psi_result_east,
                (i_b_east-i_a_east)*(psi(i_b_east)-psi(i_b_east+i_m_east))+i_m_east,
                msg=f"Test Case '{s_test_case}': the psi function does not return expected results for parameters:"
                    f"\n\t-i_a_east='{i_a_east}'"
                    f"\n\t-i_b_east='{i_b_east}'"
                    f"\n\t-i_m_east='{i_m_east}'",
            )

        # We test the function results
        self.assertAlmostEqual(
            f_aggregated_predictability,
            f_the_computed_aggregated_predictability_north,
            msg=f"Test Case '{s_test_case}': the function does not return expected results in North (measure > last "
                f"measure)."
        )

        # We test the function results
        self.assertAlmostEqual(
            f_aggregated_predictability,
            f_the_computed_aggregated_predictability_south,
            msg=f"Test Case '{s_test_case}': the function does not return expected results in South (measure < last"
                f"measure"
        )

        # We test the function results
        self.assertAlmostEqual(
            1,
            f_the_computed_aggregated_predictability_spot_on,
            msg=f"Test Case '{s_test_case}': the function does not return expected results when measure is spot on."
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_01_WxW_WxW(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="01. WNW to WNW, WSW to WSW, W to W",
            dt_start=datetime(2021, 4, 26),
            dt_end=datetime(2021, 4, 28),
            f_aggregated_predictability=0.8666007905138338,
            i_a_west=19,
            i_b_west=22,
            i_m_west=2,
            f_psi_result_west=1.7332015810276675,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_02_WxW_to_xW(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="02. WNW to NW (decreasing cone), WSW to SW (increasing cone), W to W",
            dt_start=datetime(2021, 4, 26),
            dt_end=datetime(2021, 5, 16),
            f_aggregated_predictability=0.7148562733369739,
            i_a_west=1,
            i_b_west=4,
            i_m_west=20,
            f_psi_result_west=14.297125466739478,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_03_WxW_to_xxW(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="03. WNW to NNW, WSW to SSW, W to W",
            dt_start=datetime(2021, 4, 26),
            dt_end=datetime(2021, 5, 18),
            f_aggregated_predictability=0.649869339397249,
            i_a_west=1,
            i_b_west=4,
            i_m_west=20,
            f_psi_result_west=14.297125466739478,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_04_WxW_to_last_measure(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="04. WNW to last measure, WSW to last measure, W to last measure",
            dt_start=datetime(2021, 4, 26),
            dt_end=datetime(2021, 5, 19),
            f_aggregated_predictability=0.6216141507278035,
            i_a_west=1,
            i_b_west=4,
            i_m_west=20,
            f_psi_result_west=14.297125466739478,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_05_WxW_to_xxE(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="05. WNW to NNE, WSW to SSE, W to E",
            dt_start=datetime(2021, 4, 26),
            dt_end=datetime(2021, 5, 20),
            f_aggregated_predictability=0.595713561114145,
            i_a_west=1,
            i_b_west=4,
            i_m_west=20,
            f_psi_result_west=14.297125466739478,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_06_WxW_to_xE(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="06. WNW to NE (increasing cone), WSW to SE (decreasing cone), W to E",
            dt_start=datetime(2021, 4, 26),
            dt_end=datetime(2021, 5, 22),
            f_aggregated_predictability=0.5498894410284415,
            i_a_west=1,
            i_b_west=4,
            i_m_west=20,
            f_psi_result_west=14.297125466739478,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_07_WxW_to_ExE(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="07. WNW to ENE, WSW to ESE, W to E",
            dt_start=datetime(2021, 4, 26),
            dt_end=datetime(2021, 5, 25),
            f_aggregated_predictability=0.5154181195427406,
            i_a_west=1,
            i_b_west=4,
            i_m_west=20,
            f_psi_result_west=14.297125466739478,
            i_a_east=1,
            i_b_east=4,
            i_m_east=2,
            f_psi_result_east=0.6499999999999995,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_08_xW_to_ExE(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="08. NW (decreasing cone) to ENE, SW (increasing cone) to ESE, W to E",
            dt_start=datetime(2021, 5, 16),
            dt_end=datetime(2021, 5, 25),
            f_aggregated_predictability=0.6499999999999995/9,
            i_a_east=1,
            i_b_east=4,
            i_m_east=2,
            f_psi_result_east=0.6499999999999995,
        )

    def test_09_xxE_to_ExE(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="09. NNE to ENE, SSE to ESE, E to E",
            dt_start=datetime(2021, 5, 20),
            dt_end=datetime(2021, 5, 25),
            f_aggregated_predictability=0.6499999999999995/5,
            i_a_east=1,
            i_b_east=4,
            i_m_east=2,
            f_psi_result_east=0.6499999999999995,
        )

    def test_10_xE_to_ExE(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="10. NE (increasing cone) to ENE, SE (decreasing cone) to ESE, E to E",
            dt_start=datetime(2021, 5, 22),
            dt_end=datetime(2021, 5, 25),
            f_aggregated_predictability=0.6499999999999995/3,
            i_a_east=1,
            i_b_east=4,
            i_m_east=2,
            f_psi_result_east=0.6499999999999995,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_11_ExE_to_ExE(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="11. ENE to ENE, ESE to ESE, E to E",
            dt_start=datetime(2021, 5, 23),
            dt_end=datetime(2021, 5, 25),
            f_aggregated_predictability=0.32499999999999973,
            i_a_east=1,
            i_b_east=4,
            i_m_east=2,
            f_psi_result_east=0.6499999999999995,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_12_xW_to_xxW(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="12. NW (decreasing cone) to NNW, SW (increasing cone) to SSW, W to W",
            dt_start=datetime(2021, 5, 16),
            dt_end=datetime(2021, 5, 18),
            f_aggregated_predictability=0.0,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_13_xW_to_last_measure_north(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="13. NW (decreasing cone) to last measure, SW (increasing cone) to last measure, W to last "
                        "measure",
            dt_start=datetime(2021, 5, 16),
            dt_end=datetime(2021, 5, 19),
            f_aggregated_predictability=0.0,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_14_xW_to_xxE(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="14. NW (decreasing cone) to NNE, SW (increasing cone) to SSE, W to E",
            dt_start=datetime(2021, 5, 16),
            dt_end=datetime(2021, 5, 21),
            f_aggregated_predictability=0.0,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_15_xW_to_xE(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="15. NW (decreasing cone) to NE (increasing cone), SW (decreasing cone) to SE (increasing "
                        "cone), W to E",
            dt_start=datetime(2021, 5, 16),
            dt_end=datetime(2021, 5, 22),
            f_aggregated_predictability=0.0,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_16_xxW_to_xxW(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="16. NNW to NNW, SSW to SSW, W to W",
            dt_start=datetime(2021, 5, 17),
            dt_end=datetime(2021, 5, 18),
            f_aggregated_predictability=0.0,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_17_xxW_to_last_measure(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="17. NNW to last measure, SSW to last measure, W to last measure",
            dt_start=datetime(2021, 5, 17),
            dt_end=datetime(2021, 5, 19),
            f_aggregated_predictability=0.0,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_18_xxW_to_xxE(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="18. NNW to NNE, SSW to SSE, W to E",
            dt_start=datetime(2021, 5, 17),
            dt_end=datetime(2021, 5, 20),
            f_aggregated_predictability=0.0,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_19_xxW_to_xE(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="19. NNW to NE (increasing cone), SSW to SE (decreasing cone), W to E",
            dt_start=datetime(2021, 5, 17),
            dt_end=datetime(2021, 5, 22),
            f_aggregated_predictability=0.0,
        )

    def test_20_last_measure_to_xxE(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="20. Last measure to NNE, last measure to SSE, last measure to E",
            dt_start=datetime(2021, 5, 19),
            dt_end=datetime(2021, 5, 21),
            f_aggregated_predictability=0.0,
        )

    def test_21_last_measure_to_xE(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="21. Last measure to NE (increasing cone), last measure to SE (decreasing cone), last measure "
                        "to E",
            dt_start=datetime(2021, 5, 19),
            dt_end=datetime(2021, 5, 22),
            f_aggregated_predictability=0.0,
        )

    def test_22_xxE_to_xxE(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="22. NNE to NNE, SSE to SSE, E to E",
            dt_start=datetime(2021, 5, 20),
            dt_end=datetime(2021, 5, 21),
            f_aggregated_predictability=0.0,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_23_xxE_to_xE(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self.function_to_test(
            s_test_case="23. NNE to NE (increasing cone), SSE to SE (decreasing cone), E to E",
            dt_start=datetime(2021, 5, 20),
            dt_end=datetime(2021, 5, 22),
            f_aggregated_predictability=0.0,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    # Je suis ici.
    # Je dois faire les tests unitaires lorsque je suis spot on
    # Et les tests au sud.

    def todo_test_full(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        the_df_dataset: DataFrame = DataFrame(
            columns=[
                DatePredictabilityComputer.str__input__column_label__key,
                DatePredictabilityComputer.str__input__column_label__date,
                DatePredictabilityComputer.str__input__column_label__measure,
                "date_end",
                DatePredictabilityComputer.str__output__column_label__duration
            ],
            data=[
                ['abc', '2021-4-26', '2021-5-22', '2021-4-27', 1],
                ['abc', '2021-4-27', '2021-6-5', '2021-4-30', 3],
                ['abc', '2021-4-30', '2021-6-3', '2021-5-1', 1],
                ['abc', '2021-5-1', '2021-6-4', '2021-5-6', 5],
                ['abc', '2021-5-6', '2021-5-29', '2021-5-7', 1],
                ['abc', '2021-5-7', '2021-5-25', '2021-5-9', 2],
                ['abc', '2021-5-9', '2021-5-21', '2021-5-11', 2],
                ['abc', '2021-5-11', '2021-5-19', '2021-5-13', 2],
                ['abc', '2021-5-13', '2021-5-16', '2021-5-16', 3],
                ['abc', '2021-5-16', '2021-5-17', '2021-5-18', 2],
                ['abc', '2021-5-18', '2021-5-21', '2021-5-23', 5],
                ['abc', '2021-5-23', '2021-5-14', '2021-5-25', 2],
                ['abc', '2021-5-25', '2021-5-27', '2021-5-29', 4],
                ['abc', '2021-5-29', '2021-5-20', '2021-6-6', 8],
                ['abc', '2021-6-6', '2021-5-19', '2021-6-6', 0],
            ]
        )

        # We type the columns
        the_df_dataset = PandasDataframeTyper.type(
            df_to_type=the_df_dataset,
            dict_columns_to_type={
                DatePredictabilityComputer.str__input__column_label__date: PandasDataframeTyper.str__type__date,
                DatePredictabilityComputer.str__input__column_label__measure: PandasDataframeTyper.str__type__date,
                "date_end": PandasDataframeTyper.str__type__date,
            },
            b_strict=False
        )

        f_the_aggregated_predictability: float = \
            DatePredictabilityComputer()._compute_date_predictability_for_a_given_key_not_resampled(
                df_measures=the_df_dataset[[
                    DatePredictabilityComputer.str__input__column_label__key,
                    DatePredictabilityComputer.str__input__column_label__date,
                    DatePredictabilityComputer.str__input__column_label__measure,
                    "date_end",
                    DatePredictabilityComputer.str__output__column_label__duration
                ]]
            )

        self.assertEqual(
            0.4023347872297693,
            f_the_aggregated_predictability,
            msg=f"The computation did not return expected results",
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
