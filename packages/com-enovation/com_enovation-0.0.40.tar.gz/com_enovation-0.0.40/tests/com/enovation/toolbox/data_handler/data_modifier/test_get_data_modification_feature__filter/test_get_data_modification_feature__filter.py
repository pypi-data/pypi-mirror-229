import os
import unittest
from pathlib import Path
from logging import Logger, getLogger
from inspect import stack
from pandas import DataFrame, read_excel

from com_enovation.toolbox.data_handler.data_modifier.data_modification_feature_factory \
    import DataModificationFeatureFactory


class TestDataModificationFeatureFactory_Filter(unittest.TestCase):
    _logger: Logger = getLogger(__name__)

    def test_filter(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the data extract
        df_data_extract: DataFrame = read_excel(
            Path(os.path.join(os.path.dirname(__file__),
                              '01.data_extract.xlsx'))
        )

        df_the_modified_dataframe: DataFrame = DataModificationFeatureFactory(). \
            get_data_modification_feature__filter(
            str_expressions=f"""
                StatusA+StatusB=={[
                "OpenOpen",
                "OpenInactive",
                "InactiveOpen",
                "InactiveInactive",
                "ClosedClosed"
            ]}
                """,
            b_copy=True
        )(df_data_extract)

        self.assertEqual(
            first=df_the_modified_dataframe.to_string(),
            second="""    StatusA   StatusB
0      Open      Open
1      Open  Inactive
3  Inactive      Open
4  Inactive  Inactive
8    Closed    Closed""",
            msg=""
        )
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
