import os
import unittest
from datetime import datetime
from pathlib import Path
from logging import Logger, getLogger
from inspect import stack
from pandas import DataFrame, read_excel
from pandas.testing import assert_frame_equal

from com_enovation.toolbox.data_handler.data_modifier.data_modification_feature_factory \
    import DataModificationFeatureFactory


class TestDataModificationFeatureFactory_ReplaceValues(unittest.TestCase):
    _logger: Logger = getLogger(__name__)

    def test_replace_values(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the data extract
        df_data_extract: DataFrame = read_excel(Path(os.path.join(os.path.dirname(__file__),
                                                                  '01.data_extract.xlsx')))

        # Run 1: among the transco, no line is modified
        df_the_modified_dataframe: DataFrame = DataModificationFeatureFactory(). \
            get_data_modification_feature__replace_values(
                dict_columns={
                    "Jsg - ID": {"ABC": "DEF"},
                },
                b_copy=True
            )(df_data_extract)

        assert_frame_equal(
            left=df_data_extract,
            right=df_the_modified_dataframe,
            check_exact=True,
            obj="Run 1 - We did not modify any value..."
        )

        # Run 2: among the transco, some lines are modified
        df_the_modified_dataframe: DataFrame = DataModificationFeatureFactory(). \
            get_data_modification_feature__replace_values(
            dict_columns={
                "Jsg - ID": {"ABC": "DEF"},
                "Jsg - Created On": {datetime(2023, 1, 1, 0, 0): 13}
            },
            b_copy=True
        )(df_data_extract)

        self.assertEqual(
            first=len(df_the_modified_dataframe[df_the_modified_dataframe["Jsg - Created On"] == 13].index),
            second=3,
            msg="Run 2 - We expect 3 lines to be modified..."
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
