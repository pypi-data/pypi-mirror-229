import os
import shutil
import unittest
from inspect import stack
from logging import getLogger, Logger
from sys import platform
from unittest import TestCase

import click
from click.testing import CliRunner

from com_enovation.enov import enov

from com_enovation.helper.excel_loader import ExcelLoader, ExcelLoaderBean
from pandas import DataFrame

from pandas.testing import assert_frame_equal


@unittest.skipUnless(platform.startswith("win"), f"CLASS - Do run on Windows only, and not on {platform}")
class TestClick_XlsConnectionsToDf(TestCase):

    _logger: Logger = getLogger(__name__)

    @unittest.skipUnless(platform.startswith("win"), f"FN - Do run on Windows only, and not on {platform}")
    def test_01_no_persist(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        try:
            os.remove(os.path.join(os.path.dirname(__file__), "./02.ConnectedData.persisted.xlsx"))
        except FileNotFoundError:
            pass

        runner = CliRunner()

        enov.add_command(check_data)

        # noinspection PyTypeChecker
        result = runner.invoke(
            cli=enov,
            args=[
                # To get all the logs...
                '--verbose',

                'xls-connection-to-df',
                '--no-persist',
                os.path.join(os.path.dirname(__file__), "./02.ConnectedData.xlsx"),
                "JSG",

                'check_data',
                'TEST 01. no persist'
            ]
        )

        self.assertEqual(
            first=0,
            second=result.exit_code,
            msg="TEST 01: " + str(result.exception)
        )

    @unittest.skipUnless(platform.startswith("win"), f"FN - Do run on Windows only, and not on {platform}")
    def test_02_persist(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        try:
            os.remove(os.path.join(os.path.dirname(__file__), "./02.ConnectedData.persisted.xlsx"))
        except FileNotFoundError:
            pass

        runner = CliRunner()

        enov.add_command(check_data)

        # We need to copy the file that will be refreshed, as it will be persisted!
        shutil.copyfile(
            src=os.path.join(os.path.dirname(__file__), "./02.ConnectedData.xlsx"),
            dst=os.path.join(os.path.dirname(__file__), "./02.ConnectedData.persisted.xlsx")
        )

        # noinspection PyTypeChecker
        result = runner.invoke(
            cli=enov,
            args=[
                # To get all the logs...
                '--verbose',

                'xls-connection-to-df',
                # '--persist',
                os.path.join(os.path.dirname(__file__), "./02.ConnectedData.persisted.xlsx"),
                "JSG",

                'check_data',
                'TEST 02. persist'
            ]
        )

        self.assertEqual(
            first=0,
            second=result.exit_code,
            msg="TEST 02: " + str(result.exception)
        )


@unittest.skipUnless(platform.startswith("win"), f"FN - Do run on Windows only, and not on {platform}")
@click.command('check_data')
@click.argument('step', type=str)
@click.pass_context
def check_data(ctx_context, step):
    """
    Function that checks data were effectively loaded...
    """

    # We get source data was to later reconcile
    _excel_source_tables: ExcelLoaderBean = ExcelLoader().load_tables(
        str_path=os.path.join(os.path.dirname(__file__), "./01.SourceData.xlsx")
    )

    # We check data was not persisted in 02.ConnectedData
    _excel_connected_tables: ExcelLoaderBean = ExcelLoader().load_tables(
        str_path=os.path.join(os.path.dirname(__file__), "./02.ConnectedData.xlsx")
    )
    for i_table in ["JSG_TABLE_1", "BCH_TABLE_1", "BCH_TABLE_2"]:
        if len(_excel_connected_tables.dict_tables[i_table+"query"].index) != 1:
            raise Exception(f"Table {i_table} has {len(_excel_connected_tables.dict_tables[i_table+'query'].index)}, "
                            f"while only one is expected.")

    # We check data loaded in context
    # Note: we only import the dependency here, as this import can only work on Windows!
    from com_enovation.helper.excel.xls_data_connection_to_df import ExcelTables
    _obj_excel_tables: ExcelTables = ctx_context.obj["JSG"]

    for i_table in ["JSG_TABLE_1", "BCH_TABLE_1", "BCH_TABLE_2"]:

        _src: DataFrame = _excel_source_tables.dict_tables[i_table]
        _refreshed: DataFrame = _obj_excel_tables.dict_tables[i_table+'query']

        assert_frame_equal(
            left=_src,
            right=_refreshed,
            obj=f"{i_table} not reconciling",
            check_dtype=False
        )

    if step == 'TEST 02. persist':

        # We check data from 02.ConnectedData
        _excel_tables: ExcelLoaderBean = ExcelLoader().load_tables(
            str_path=os.path.join(os.path.dirname(__file__), "./02.ConnectedData.persisted.xlsx")
        )
        for i_table in ["JSG_TABLE_1", "BCH_TABLE_1", "BCH_TABLE_2"]:

            _src: DataFrame = _excel_source_tables.dict_tables[i_table]
            _refreshed: DataFrame = _excel_tables.dict_tables[i_table+'query']

            assert_frame_equal(
                left=_src,
                right=_refreshed,
                obj=f"{i_table} not reconciling",
                check_dtype=False
            )
