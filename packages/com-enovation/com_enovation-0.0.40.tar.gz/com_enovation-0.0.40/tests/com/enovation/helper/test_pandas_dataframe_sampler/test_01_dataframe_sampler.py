from inspect import stack
from logging import Logger, getLogger
from unittest import TestCase

import numpy
import pandas
from pandas import DataFrame

from com_enovation.helper.pandas_dataframe_sampler import PandasDataframeSampler
from pandas.testing import assert_frame_equal

from com_enovation.helper.pandas_dataframe_typer import PandasDataframeTyper


class Test01DataframeSampler(TestCase):

    _logger: Logger = getLogger(__name__)

    def test_01_single_record_per_key(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        df_the_data: DataFrame = DataFrame(
            columns=[
                "col 1", "col 2", "col 3", "col 4"
            ],
            data=[
                ["aa_a", "bbb_b", "cccc_c", "dddd_d"],
                ["aa_a", "bbb_c", "cccc_d", "dddd_d"],
                ["aa_a", "bbb_d", "cccc_d", "dddd_e"],
                ["aa_a", "bbb_e", "cccc_d", "dddd_f"],

            ]
        )

        # Combination 1: 2 key columns, 2 value columns
        assert_frame_equal(
            left=df_the_data,
            right=PandasDataframeSampler.compress(
                df_measures=df_the_data,
                lst_key_columns=["col 1", "col 2"],
                lst_value_columns=["col 3", "col 4"],
                b_keep_last=True,
            ),
            obj=f"Call 1",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        # Combination 2: only one key column, 3 value columns
        assert_frame_equal(
            left=df_the_data,
            right=PandasDataframeSampler.compress(
                df_measures=df_the_data,
                lst_key_columns=["col 1"],
                lst_value_columns=["col 2", "col 3", "col 4"],
                b_keep_last=True,
            ),
            obj=f"Call 2",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        # Combination 3: no key column (empty list), only value columns
        assert_frame_equal(
            left=df_the_data,
            right=PandasDataframeSampler.compress(
                df_measures=df_the_data,
                lst_key_columns=[],
                lst_value_columns=["col 1", "col 2", "col 3", "col 4"],
                b_keep_last=True,
            ),
            obj=f"Call 3",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        # Combination 4: no key column (none value), only value columns
        assert_frame_equal(
            left=df_the_data,
            right=PandasDataframeSampler.compress(
                df_measures=df_the_data,
                lst_value_columns=["col 1", "col 2", "col 3", "col 4"],
                b_keep_last=True,
            ),
            obj=f"Call 4",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")

    def test_02_drop_last(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        df_the_data: DataFrame = DataFrame(
            columns=[
                "col 1", "col 2", "col 3", "col 4", "expected result"
            ],
            data=[
                ["aa_a", "bbb_b", "cccc_c", "dddd_d", "filter in"],

                ["aa_a", "bbb_c", "cccc_d", "dddd_d", "filter in"],

                ["aa_a", "bbb_d", "cccc_d", "dddd_e", "filter in"],
                ["aa_a", "bbb_d", "cccc_d", "dddd_e", "filter out"],
                ["aa_a", "bbb_d", "cccc_d", "dddd_e", "filter out"],
                ["aa_a", "bbb_d", "cccc_d", "dddd_e", "filter out"],

                ["aa_a", "bbb_e", "cccc_d", "dddd_f", "filter in"],
                ["aa_a", "bbb_e", "cccc_d", "dddd_f", "filter out"],
                ["aa_a", "bbb_e", "cccc_d", "dddd_f", "filter out"],
            ],
        )

        df_the_return: DataFrame = PandasDataframeSampler.compress(
            df_measures=df_the_data[[i_col for i_col in df_the_data.columns if i_col.startswith("col")]],
            lst_key_columns=["col 1", "col 2"],
            lst_value_columns=["col 3", "col 4"],
            b_keep_last=False,
        )

        assert_frame_equal(
            left=df_the_data[
                df_the_data["expected result"] == "filter in"
            ][df_the_return.columns].reset_index(drop=True),
            right=df_the_return.reset_index(drop=True),
            obj=f"Call 1",
            atol=0.00001,
            check_like=True,  # To exclude index, and not to care about column ordering
            check_names=False,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")

    def test_03_keep_last(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        df_the_data: DataFrame = DataFrame(
            columns=[
                "col 1", "col 2", "col 3", "col 4", "expected result"
            ],
            data=[
                ["aa_a", "bbb_b", "cccc_c", "dddd_d", "filter in"],

                ["aa_a", "bbb_c", "cccc_d", "dddd_d", "filter in"],

                ["aa_a", "bbb_d", "cccc_d", "dddd_e", "filter in"],
                ["aa_a", "bbb_d", "cccc_d", "dddd_e", "filter out"],
                ["aa_a", "bbb_d", "cccc_d", "dddd_e", "filter out"],
                ["aa_a", "bbb_d", "cccc_d", "dddd_e", "filter in"],

                ["aa_a", "bbb_e", "cccc_d", "dddd_f", "filter in"],
                ["aa_a", "bbb_e", "cccc_d", "dddd_f", "filter out"],
                ["aa_a", "bbb_e", "cccc_d", "dddd_f", "filter in"],

                ["aa_a", "bbb_f", "cccc_d", "dddd_g", "filter in"],
                ["aa_a", "bbb_f", "cccc_d", "dddd_g", "filter in"],
            ],
        )

        df_the_return: DataFrame = PandasDataframeSampler.compress(
            df_measures=df_the_data[[i_col for i_col in df_the_data.columns if i_col.startswith("col")]],
            lst_key_columns=["col 1", "col 2"],
            lst_value_columns=["col 3", "col 4"],
            b_keep_last=True,
        )

        assert_frame_equal(
            left=df_the_data[
                df_the_data["expected result"] == "filter in"
            ][df_the_return.columns].reset_index(drop=True),
            right=df_the_return.reset_index(drop=True),
            obj=f"Call 1",
            atol=0.00001,
            check_like=True,  # To exclude index, and not to care about column ordering
            check_names=False,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")

    def test_04_full_example_no_keep_last(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        df_the_data: DataFrame = DataFrame(
            columns=[
                "key 1", "key 2", "order 1", "order 2", "val 1", "val 2", "expected result"
            ],
            data=[
                # Universe 1
                ["k1a", "k2a", "o1a", "o2a", "v1a", "v2a", "filter in"],
                ["k1a", "k2a", "o1a", "o2b", "v1a", "v2a", "filter out"],
                ["k1a", "k2a", "o1b", "o2a", "v1b", "v2a", "filter in"],
                ["k1a", "k2a", "o1b", "o2b", "v1a", "v2a", "filter in"],
                ["k1a", "k2a", "o1b", "o2c", "v1a", "v2a", "filter out"],
                ["k1a", "k2a", "o1c", "o2a", "v1a", "v2a", "filter out"],
                ["k1a", "k2a", "o1c", "o2b", "v1a", "v2a", "filter out"],
            ]
        )

        df_the_return: DataFrame = PandasDataframeSampler.compress(
            df_measures=df_the_data[[i_col for i_col in df_the_data.columns if i_col != "expected result"]],
            lst_key_columns=["key 1", "key 2"],
            lst_ordering_columns=["order 1", "order 2"],
            lst_value_columns=["val 1", "val 2"],
            b_keep_last=False,
        )

        assert_frame_equal(
            left=df_the_data[
                df_the_data["expected result"] == "filter in"
            ][df_the_return.columns].reset_index(drop=True),
            right=df_the_return.reset_index(drop=True),
            obj=f"Call 1",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")

    def test_05_full_example_keep_last(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        df_the_data: DataFrame = DataFrame(
            columns=[
                "key 1", "key 2", "order 1", "order 2", "val 1", "val 2", "expected result"
            ],
            data=[
                # Universe 1
                ["k1a", "k2a", "o1a", "o2a", "v1a", "v2a", "filter in"],
                ["k1a", "k2a", "o1a", "o2b", "v1a", "v2a", "filter out"],
                ["k1a", "k2a", "o1b", "o2a", "v1b", "v2a", "filter in"],
                ["k1a", "k2a", "o1b", "o2b", "v1a", "v2a", "filter in"],
                ["k1a", "k2a", "o1b", "o2c", "v1a", "v2a", "filter out"],
                ["k1a", "k2a", "o1c", "o2a", "v1a", "v2a", "filter out"],
                ["k1a", "k2a", "o1c", "o2b", "v1a", "v2a", "filter in"],
            ]
        )

        df_the_return: DataFrame = PandasDataframeSampler.compress(
            df_measures=df_the_data[[i_col for i_col in df_the_data.columns if i_col != "expected result"]],
            lst_key_columns=["key 1", "key 2"],
            lst_ordering_columns=["order 1", "order 2"],
            lst_value_columns=["val 1", "val 2"],
            b_keep_last=True,
        )

        assert_frame_equal(
            left=df_the_data[
                df_the_data["expected result"] == "filter in"
            ][df_the_return.columns].reset_index(drop=True),
            right=df_the_return.reset_index(drop=True),
            obj=f"Call 1",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")

    def test_06_full_example_reordered_keep_last(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        # Same data set as previously...
        df_the_data: DataFrame = DataFrame(
            columns=[
                "key 1", "key 2", "order 1", "order 2", "val 1", "val 2", "expected result"
            ],
            data=[
                # Universe 1
                ["k1a", "k2a", "o1b", "o2a", "v1b", "v2a", 2],   # 3 - in
                ["k1a", "k2a", "o1b", "o2c", "v1a", "v2a", -1],  # 5 - out
                ["k1a", "k2a", "o1a", "o2a", "v1a", "v2a", 1],   # 1 - in
                ["k1a", "k2a", "o1c", "o2b", "v1a", "v2a", 4],   # 6 - in
                ["k1a", "k2a", "o1c", "o2a", "v1a", "v2a", -1],  # 5 - out
                ["k1a", "k2a", "o1a", "o2b", "v1a", "v2a", -1],  # 2 - out
                ["k1a", "k2a", "o1b", "o2b", "v1a", "v2a", 3],   # 4 - in
            ]
        )

        df_the_return: DataFrame = PandasDataframeSampler.compress(
            df_measures=df_the_data[[i_col for i_col in df_the_data.columns if i_col != "expected result"]],
            lst_key_columns=["key 1", "key 2"],
            lst_ordering_columns=["order 1", "order 2"],
            lst_value_columns=["val 1", "val 2"],
            b_keep_last=True,
        )

        assert_frame_equal(
            left=df_the_data[
                df_the_data["expected result"] > 0
            ].sort_values(by="expected result")[df_the_return.columns].reset_index(drop=True),
            right=df_the_return.reset_index(drop=True),
            obj=f"Call 1",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")

    def test_07_full_example_keep_last_with_null(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        df_the_data: DataFrame = DataFrame(
            columns=[
                "key 1", "key 2", "order 1", "order 2", "val 1", "val 2", "expected result"
            ],
            data=[
                # Universe 1
                ["k1a", "k2a", "o1a", "o2a", "v1a", '2021-1-15', "filter in"],
                ["k1a", "k2a", "o1a", "o2b", "v1a", '2021-1-15', "filter out"],
                ["k1a", "k2a", "o1b", "o2a", "v1b", '2021-1-15', "filter in"],
                ["k1a", "k2a", "o1b", "o2b", "v1a", pandas.NA, "filter in"],
                ["k1a", "k2a", "o1b", "o2c", "v1a", pandas.NaT, "filter out"],
                ["k1a", "k2a", "o1c", "o2a", "v1a", numpy.NAN, "filter out"],
                ["k1a", "k2a", "o1c", "o2b", "v1a", None, "filter in"],

                ["k2a", "k2a", "o1c", "o2b", "v1a", None, "filter in"],

            ]
        )
        df_the_data = PandasDataframeTyper.type(
            df_to_type=df_the_data,
            dict_columns_to_type={
                "val 2": PandasDataframeTyper.str__type__date
            }
        )

        df_the_return: DataFrame = PandasDataframeSampler.compress(
            df_measures=df_the_data[[i_col for i_col in df_the_data.columns if i_col != "expected result"]],
            lst_key_columns=["key 1", "key 2"],
            lst_ordering_columns=["order 1", "order 2"],
            lst_value_columns=["val 1", "val 2"],
            b_keep_last=True,
        )

        assert_frame_equal(
            left=df_the_data[
                df_the_data["expected result"] == "filter in"
            ][df_the_return.columns].reset_index(drop=True),
            right=df_the_return.reset_index(drop=True),
            obj=f"Call 1",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")
