import os
import unittest
from pathlib import Path
from logging import Logger, getLogger
from inspect import stack
from pandas import DataFrame, read_excel, Series, MultiIndex, Index
from pandas.testing import assert_series_equal

from com_enovation.toolbox.data_handler.data_checker.data_check_feature_factory import DataCheckFeatureFactory


class TestDataCheckFeatureFactory_CheckDuplicate(unittest.TestCase):
    _logger: Logger = getLogger(__name__)

    def test_check_duplicate__1_column(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the data extract
        df_data_extract: DataFrame = \
            read_excel(Path(os.path.join(os.path.dirname(__file__), '01.data_extract.xlsx')))

        # Run 1: duplicates found, as data extract contains 3 snapshots, so most id will be duplicated
        s_the_return: Series = DataCheckFeatureFactory().get_data_check_feature__check_duplicate(
            columns="Jsg - ID"
        )(df_data_extract)

        assert_series_equal(
            left=s_the_return.sort_index(),
            right=Series(
                data=[3, 3, 3, 3, 3],
                index=Index(
                    data=["JSG1384", "JSG1371", "JSG1365", "JSG1302", "JSG1338"],
                    name="Jsg - ID"
                ),
                name=DataCheckFeatureFactory.const_fn_data_extract_checker__count
            ).sort_index(),
            obj="Check 1: most opp_id are duplicated. We expect 5 duplicates.",
            check_exact=True
        )

        # Run 2: no duplicate found, because if we only select one snapshot, then we do not expect any duplicate
        s_the_return: Series = DataCheckFeatureFactory().get_data_check_feature__check_duplicate(
            columns="Jsg - ID"
        )(df_data_extract[df_data_extract["Jsg - Snapshot"] == 1])

        self.assertIsNone(
            obj=s_the_return,
            msg="Check 2: no duplicate, we expect a null value!"
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_check_duplicate__2_columns(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the data extract
        df_data_extract: DataFrame = \
            read_excel(Path(os.path.join(os.path.dirname(__file__), '01.data_extract.xlsx')))

        # Run 1: no duplicate found, as no duplicate in the source file across id and snapshot
        s_the_return: Series = DataCheckFeatureFactory().get_data_check_feature__check_duplicate(
            columns=["Jsg - ID", "Jsg - Snapshot"],
        )(df_data_extract)

        self.assertIsNone(
            obj=s_the_return,
            msg="Check 1: no duplicate, we expect a null value!"
        )

        # Run 2: duplicates found after altering the data extract
        df_data_extract.at[1, "Jsg - Snapshot"] = 1
        df_data_extract.at[2, "Jsg - Snapshot"] = 1

        df_data_extract.at[3, "Jsg - Snapshot"] = 2
        df_data_extract.at[4, "Jsg - Snapshot"] = 2
        df_data_extract.at[5, "Jsg - Snapshot"] = 2
        df_data_extract.at[6, "Jsg - Snapshot"] = 2
        df_data_extract.at[7, "Jsg - Snapshot"] = 2

        s_the_return: Series = DataCheckFeatureFactory().get_data_check_feature__check_duplicate(
            columns=["Jsg - ID", "Jsg - Snapshot"],
        )(df_data_extract)

        assert_series_equal(
            left=s_the_return.sort_index(),
            right=Series(
                data=[3, 3, 2],
                index=MultiIndex.from_arrays(
                    [["JSG1384", "JSG1371", "JSG1365"], [1, 2, 2]],
                    names=("Jsg - ID", "Jsg - Snapshot")
                ),
                name=DataCheckFeatureFactory.const_fn_data_extract_checker__count
            ).sort_index(),
            obj="Check 2: duplicates, we expect one combination duplicated 3 times!",
            check_exact=True
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_check_duplicate__exception(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the data extract
        df_data_extract: DataFrame = \
            read_excel(Path(os.path.join(os.path.dirname(__file__), '01.data_extract.xlsx')))

        # Exception 1: single column does not exist in extract
        with self.assertRaisesRegex(
                Exception,
                f"Column 'Jsg - not defined' is missing from the data extract to check."
        ):
            DataCheckFeatureFactory().get_data_check_feature__check_duplicate(
                columns="Jsg - not defined"
            )(df_data_extract)

        # Exception 2: multiple column does not exist in extract
        with self.assertRaisesRegex(
                Exception,
                f"Column 'Jsg - not defined' is missing from the data extract to check."
        ):
            DataCheckFeatureFactory().get_data_check_feature__check_duplicate(
                columns=["Jsg - not defined", "Jsg - and a second one"]
            )(df_data_extract)

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
