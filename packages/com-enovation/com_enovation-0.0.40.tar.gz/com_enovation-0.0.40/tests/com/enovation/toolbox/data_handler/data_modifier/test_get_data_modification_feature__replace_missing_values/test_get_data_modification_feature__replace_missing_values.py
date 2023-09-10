import os
import unittest
from pathlib import Path
from logging import Logger, getLogger
from inspect import stack
from pandas import DataFrame, read_excel
from pandas.testing import assert_frame_equal

from com_enovation.toolbox.data_handler.data_modifier.data_modification_feature_factory \
    import DataModificationFeatureFactory


class TestDataModificationFeatureFactory_ReplaceMissingValues(unittest.TestCase):
    _logger: Logger = getLogger(__name__)

    def test_replace_missing_values(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the data extract
        df_data_extract: DataFrame = read_excel(Path(os.path.join(os.path.dirname(__file__),
                                                                  '01.data_extract.xlsx')))

        # Run 1: no missing value in the column, therefore no modification
        df_the_modified_dataframe: DataFrame = DataModificationFeatureFactory(). \
            get_data_modification_feature__replace_missing_values(
            dict_columns={
                "Jsg - ID": "ABC",
            },
            b_copy=True
        )(df_data_extract)

        assert_frame_equal(
            left=df_data_extract,
            right=df_the_modified_dataframe,
            check_exact=True,
            obj="Run 1 - We did not modify any missing value..."
        )

        # Run 2: missing values are defaulted
        df_the_modified_dataframe: DataFrame = DataModificationFeatureFactory(). \
            get_data_modification_feature__replace_missing_values(
            dict_columns={
                "Jsg - ID": "ABC",
                "Jsg - Null Values A": "defaulted missing value",
                "Jsg - Null Values B": 7.321
            },
            b_copy=True
        )(df_data_extract)

        self.assertEqual(
            first=len(
                df_the_modified_dataframe[
                    df_the_modified_dataframe["Jsg - Null Values A"] == "defaulted missing value"
                ].index
            ),
            second=5,
            msg="Run 2, check 1 - We expect 5 lines to be modified in column A..."
        )

        self.assertEqual(
            first=len(
                df_the_modified_dataframe[
                    df_the_modified_dataframe["Jsg - Null Values B"] == 7.321
                ].index
            ),
            second=1,
            msg="Run 2, check 2 - We expect 3 lines to be modified in column B..."
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
