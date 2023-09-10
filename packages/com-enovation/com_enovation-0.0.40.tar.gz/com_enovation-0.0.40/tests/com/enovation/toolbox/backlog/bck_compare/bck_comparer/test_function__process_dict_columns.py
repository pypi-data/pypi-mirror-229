from inspect import stack
from unittest import TestCase
from logging import Logger, getLogger


from com_enovation.helper.pandas_dataframe_typer import PandasDataframeTyper
from com_enovation.toolbox.backlog.bck_compare.bck_comparer import BacklogComparer


class TestFunctionProcessDictColumns(TestCase):
    _logger: Logger = getLogger(__name__)

    def test_001(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # From the dict_columns, we prepare the various sub-dictionaries/ lists
        dict_the_columns_types: dict[str]   # A dictionary to properly type the dataframes (both key and comparable col)
        lst_the_compared_columns: list[str] # A list of the columns' labels to compare
        lst_the_key_columns: list[str]      # A list of the key columns' labels to merge dataframes
        dict_the_columns_comparison_logics: dict    # A dictionary to properly associate comparison functions to columns

        # First, we process the dict_columns, and raise an exception should its format be incorrect
        dict_columns_types, lst_compared_columns, lst_key_columns, dict_the_columns_comparison_logics = \
            BacklogComparer()._process_dict_columns(
                dict_columns={
                    BacklogComparer.str__dict_columns__json_tag__key_columns: {
                        "key1": {
                            BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                        }
                    },
                    BacklogComparer.str__dict_columns__json_tag__compared_columns: {
                        "col1": {
                            BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                        }
                    }
                }
            )

        self.assertDictEqual(
            d1={
                "key1": PandasDataframeTyper.str__type__str,
                "col1": PandasDataframeTyper.str__type__str
            },
            d2=dict_columns_types,
            msg=f"dict_columns_types not equal. D1 as expected results"
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
