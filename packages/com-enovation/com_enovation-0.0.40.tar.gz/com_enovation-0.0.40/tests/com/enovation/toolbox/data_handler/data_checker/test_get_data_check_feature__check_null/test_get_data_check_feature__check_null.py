import os
import unittest
from pathlib import Path
from logging import Logger, getLogger
from inspect import stack
from pandas import DataFrame, read_excel, Series, Index
from pandas.testing import assert_series_equal

from com_enovation.toolbox.data_handler.data_checker.data_check_feature_factory import DataCheckFeatureFactory


class TestDataCheckFeatureFactory_CheckNull(unittest.TestCase):
    _logger: Logger = getLogger(__name__)

    def test_check_null__1_column(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the data extract
        df_data_extract: DataFrame = \
            read_excel(Path(os.path.join(os.path.dirname(__file__), '01.data_extract.xlsx')))

        # Run 1: null values found in one column
        s_the_return: Series = DataCheckFeatureFactory().get_data_check_feature__check_null(
            columns="Jsg - Null Values A"
        )(df_data_extract)

        assert_series_equal(
            left=s_the_return.sort_index(),
            right=Series(
                data=[5],
                index=Index(
                    data=["Jsg - Null Values A"],
                    name=DataCheckFeatureFactory.const_fn_data_extract_checker__column_label
                ),
                name=DataCheckFeatureFactory.const_fn_data_extract_checker__count,
            ).sort_index(),
            obj="Check 1: null values found in one column.",
            check_exact=True
        )

        # Run 2: no null values...
        s_the_return: Series = DataCheckFeatureFactory().get_data_check_feature__check_null(
            columns="Jsg - ID"
        )(df_data_extract)

        self.assertIsNone(
            obj=s_the_return,
            msg="Run 2, no null value in column ID"
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_check_null__multiple_columns(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the data extract
        df_data_extract: DataFrame = \
            read_excel(Path(os.path.join(os.path.dirname(__file__), '01.data_extract.xlsx')))

        # Run 1: null values found in several columns
        s_the_return: Series = DataCheckFeatureFactory().get_data_check_feature__check_null(
            columns=["Jsg - Null Values A", "Jsg - Null Values B", "Jsg - ID"]
        )(df_data_extract)

        assert_series_equal(
            left=s_the_return.sort_index(),
            right=Series(
                data=[5, 1],
                index=Index(
                    data=["Jsg - Null Values A", "Jsg - Null Values B"],
                    name=DataCheckFeatureFactory.const_fn_data_extract_checker__column_label
                ),
                name=DataCheckFeatureFactory.const_fn_data_extract_checker__count
            ).sort_index(),
            obj="Check 1: null values found in 2 columns.",
            check_exact=True
        )

        # Run 2: no null values found across several columns
        s_the_return: Series = DataCheckFeatureFactory().get_data_check_feature__check_null(
            columns=["Jsg - ID", "Jsg - Snapshot"]
        )(df_data_extract)

        self.assertIsNone(
            obj=s_the_return,
            msg="Run 2, no null value in columns ID nor snapshot"
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
