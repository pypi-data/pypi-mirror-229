import os
from inspect import stack
from unittest import TestCase
from logging import Logger, getLogger

from pandas import DataFrame

from com_enovation.helper.excel_loader import ExcelLoaderBean, ExcelLoader
from com_enovation.helper.pandas_dataframe_typer import PandasDataframeTyper
from com_enovation.toolbox.backlog.bck_compare.bck_comparer import BacklogComparer


class TestFunctionCompare(TestCase):

    _logger: Logger = getLogger(__name__)

    def test_01(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the test data
        _bean_test_data: ExcelLoaderBean = ExcelLoader().load_tables(
            str_path=os.path.join(os.path.dirname(__file__), 'TC01.SimpleSourceTargetAndExpectedResults.xlsx')
        )

        df_the_delta: DataFrame = BacklogComparer().compare(
            df_src=_bean_test_data.dict_tables["src"],
            df_tgt=_bean_test_data.dict_tables["tgt"],
            dict_columns={
                "key columns": {
                    "key 1": {
                        "type": PandasDataframeTyper.str__type__str,
                    },
                    "key 2": {
                        "type": PandasDataframeTyper.str__type__str,
                    },
                },
                "compared columns": {
                    "col 1": {
                        "type": PandasDataframeTyper.str__type__int,
                        #"compare logic": "",
                        #"delta type": ""
                    },
                    "col 2": {
                        "type": PandasDataframeTyper.str__type__str,
                        #"compare logic": "",
                        #"delta type": ""
                    },
                    "col 4": {
                        "type": PandasDataframeTyper.str__type__str,
                        "compare logic": "src.str.len() == tgt.str.len() ",
                        #"delta type": ""
                    },
                }
            }
        )

        df_the_delta: DataFrame = BacklogComparer().compare_into_excel(
            df_src=_bean_test_data.dict_tables["src"],
            df_tgt=_bean_test_data.dict_tables["tgt"],
            dict_columns={
                "key columns": {
                    "key 1": {
                        "type": PandasDataframeTyper.str__type__str,
                    },
                    "key 2": {
                        "type": PandasDataframeTyper.str__type__str,
                    },
                },
                "compared columns": {
                    "col 1": {
                        "type": PandasDataframeTyper.str__type__int,
                        # "compare logic": "",
                        # "delta type": ""
                    },
                    "col 2": {
                        "type": PandasDataframeTyper.str__type__str,
                        # "compare logic": "",
                        # "delta type": ""
                    },
                    "col 4": {
                        "type": PandasDataframeTyper.str__type__str,
                        "compare logic": "src.str.len() == tgt.str.len() ",
                        # "delta type": ""
                    },
                }
            },
            str_path=os.path.join(os.path.dirname(__file__), 'TC01.outputs.xlsx')
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
