import os
import unittest
from pathlib import Path
from logging import Logger, getLogger
from inspect import stack

from pandas import DataFrame, read_excel

from com_enovation.toolbox.data_handler.data_modifier.data_modification_feature_factory \
    import DataModificationFeatureFactory


class TestDataModificationFeatureFactory_AddEvalColumn(unittest.TestCase):
    _logger: Logger = getLogger(__name__)

    def test_add_eval_column__vanilla(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the data extract
        df_data_extract: DataFrame = read_excel(
            Path(os.path.join(os.path.dirname(__file__), '01.data_extract_for_data_quality_checks.xlsx'))
        )

        # We type the data extract...
        df_data_extract = DataModificationFeatureFactory(). \
            get_data_modification_feature__type_columns(
            dict_columns={
                "StatusA": "str",
                "StatusB": "str"
            }
        )(df_data_extract)

        _lst_authorized: list[str] = [
            "OpenOpen",
            "OpenInactive",
            "InactiveOpen",
            "InactiveInactive",
            "ClosedClosed"
        ]

        df_the_modified_dataframe: DataFrame = DataModificationFeatureFactory(). \
            get_data_modification_feature__add_eval_columns(
            str_expressions=f"""
                DQ_01=StatusA+StatusB=={[
                "OpenOpen",
                "OpenInactive",
                "InactiveOpen",
                "InactiveInactive",
                "ClosedClosed"
            ]}
                DQ_02=StatusA=='Open'
                """,
            b_copy=True
        )(df_data_extract)

        self.assertEqual(
            first=df_the_modified_dataframe.to_string(),
            second=f"    StatusA   StatusB  DQ_01  DQ_02\n"
                   f"0      Open      Open   True   True\n"
                   f"1      Open  Inactive   True   True\n"
                   f"2      Open    Closed  False   True\n"
                   f"3  Inactive      Open   True  False\n"
                   f"4  Inactive  Inactive   True  False\n"
                   f"5  Inactive    Closed  False  False\n"
                   f"6    Closed      Open  False  False\n"
                   f"7    Closed  Inactive  False  False\n"
                   f"8    Closed    Closed   True  False",
            msg=""
        )
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
