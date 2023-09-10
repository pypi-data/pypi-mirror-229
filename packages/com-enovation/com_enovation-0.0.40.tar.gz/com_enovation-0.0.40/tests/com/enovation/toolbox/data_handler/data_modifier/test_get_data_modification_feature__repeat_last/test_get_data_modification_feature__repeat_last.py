import os
import unittest
from pathlib import Path
from logging import Logger, getLogger
from inspect import stack

from pandas import DataFrame, read_excel
from pandas.testing import assert_frame_equal

from com_enovation.toolbox.data_handler.data_modifier.data_modification_feature_factory \
    import DataModificationFeatureFactory


class TestDataModificationFeatureFactory_RepeatLast(unittest.TestCase):
    _logger: Logger = getLogger(__name__)

    def test_repeat_last__vanilla(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the data extract
        df_data_extract: DataFrame = read_excel(
            Path(os.path.join(os.path.dirname(__file__), '01.test_data.xlsx'))
        )

        # We type the data extract...
        df_data_extract = DataModificationFeatureFactory(). \
            get_data_modification_feature__type_columns(
            dict_columns={
                "Key": "str",
                "Date": "date",
                "Measure": "int"
            }
        )(df_data_extract)

        df_the_modified_dataframe: DataFrame = DataModificationFeatureFactory(). \
            get_data_modification_feature__repeat_last(
                s_column_to_repeat="Measure",
                s_column_repeat="Last Measure",
                lst_key_columns=["Key"],
                b_copy=True
            )(df_data_extract[["Key", "Date", "Measure"]])

        assert_frame_equal(
            left=df_data_extract,
            right=df_the_modified_dataframe,
            check_dtype=False
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
