import os
import unittest
from pathlib import Path
from logging import Logger, getLogger
from inspect import stack
from pandas import DataFrame, read_excel
from com_enovation.toolbox.data_handler.data_modifier.data_modification_feature_factory \
    import DataModificationFeatureFactory


class TestDataModificationFeatureFactory_TypeColumns(unittest.TestCase):
    _logger: Logger = getLogger(__name__)

    def test_type_columns__all_column(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the data extract
        df_data_extract: DataFrame = read_excel(
            Path(os.path.join(os.path.dirname(__file__),
                              '01.data_extract.xlsx')),
            dtype="object"
        )

        # Run 1: we type each and every column
        df_the_modified_dataframe: DataFrame = DataModificationFeatureFactory(). \
            get_data_modification_feature__type_columns(
            dict_columns={
                "Jsg - ID": "str",
                "Jsg - Snapshot": "str",
                "Jsg - Label": "str",
                "Jsg - Type": "str",
                "Jsg - Solution": "str",
                "Jsg - Created On": "datetime",
                "Jsg - Updated On": "date",
                "Jsg - Status": "str",
                "Jsg - Stage": "str",
                "Jsg - Conf Lvl": "float",
                "Jsg - Close Date": "datetime",
                "Jsg - Manager": "str",
                "Jsg - Director": "str",
                "Jsg - Costs": "int",
                "Jsg - Revenues": "int",
                "Jsg - Null Values A": "str",
                "Jsg - Null Values B": "str",
            }
        )(df_data_extract)

        self.assertEqual(
            first=str(df_the_modified_dataframe.dtypes),
            second="""Jsg - ID                       object
Jsg - Snapshot                 object
Jsg - Label                    object
Jsg - Type                     object
Jsg - Solution                 object
Jsg - Created On       datetime64[ns]
Jsg - Updated On               object
Jsg - Status                   object
Jsg - Stage                    object
Jsg - Conf Lvl                float32
Jsg - Close Date       datetime64[ns]
Jsg - Manager                  object
Jsg - Director                 object
Jsg - Costs                     int16
Jsg - Revenues                float64
Jsg - Null Values A            object
Jsg - Null Values B            object
dtype: object""",
            msg="Error when checking typed dataframe"
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
