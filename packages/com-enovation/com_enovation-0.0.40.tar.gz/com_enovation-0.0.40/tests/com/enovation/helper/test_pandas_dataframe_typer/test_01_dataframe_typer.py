import os
from inspect import stack
from unittest import TestCase
from logging import Logger, getLogger

from pandas import DataFrame, read_excel

from com_enovation.helper.pandas_dataframe_typer import PandasDataframeTyper


class Test01DataframeTyper(TestCase):

    _logger: Logger = getLogger(__name__)

    def test_01_dataframe_typer(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        _df_TC1_to_type: DataFrame = read_excel(
            io=os.path.join(os.path.dirname(__file__), 'TC_A_00.DataframeToType.xls'),
            dtype="object",
        )

        self.assertTrue(
            expr=(_df_TC1_to_type.dtypes == "object").all(),
            msg="We expect dataframe to type containing only 'object' columns."
        )

        _df_TC1_typed: DataFrame = PandasDataframeTyper.type(
            df_to_type=_df_TC1_to_type,
            dict_columns_to_type={
                "col1_str": PandasDataframeTyper.str__type__str,
                "col3_date": PandasDataframeTyper.str__type__date,
                "col4_float": PandasDataframeTyper.str__type__float,
                "col5_int": PandasDataframeTyper.str__type__int,
            }
        )

        self.assertListEqual(
            list1=_df_TC1_typed.dtypes.tolist(),
            list2=[
                "string",
                "object",
                "datetime64[ns]",
                "Float64",
                "Int64",
                "object"
            ],
            msg="We expect dataframe to be properly retyped."
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")

    def test_02_unexpected_type(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        with self.assertRaisesRegex(
                Exception,
                f"We don't know how to handle transco into 'jsg_unexpected_type'."
        ):
            PandasDataframeTyper.type(
                df_to_type=DataFrame(columns=['col1', 'col2']),
                dict_columns_to_type={
                    "col1": PandasDataframeTyper.str__type__str,
                    "col2": "jsg_unexpected_type",
                }
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")

    def test_03_unexpected_column(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        # First call: we do not want to be strict --> no exception raised
        PandasDataframeTyper.type(
            df_to_type=DataFrame(columns=['col1', 'col2']),
            dict_columns_to_type={
                "col1": PandasDataframeTyper.str__type__str,
                "col3": PandasDataframeTyper.str__type__int,
            },
            b_strict=False
        )

        # Second call: we want to be strict --> we raise an exception
        with self.assertRaisesRegex(
                Exception,
                f"When requesting to type a dataframe, we discovered the following discrepancies:"
                f"\n\t- Columns in dataframe, but missing in  dictionary: 'col2'"
                f"\n\t- Columns in dictionary, but missing in dataframe: 'col3'."
        ):
            PandasDataframeTyper.type(
                df_to_type=DataFrame(columns=['col1', 'col2']),
                dict_columns_to_type={
                    "col1": PandasDataframeTyper.str__type__str,
                    "col3": PandasDataframeTyper.str__type__int,
                },
                b_strict=True
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")
