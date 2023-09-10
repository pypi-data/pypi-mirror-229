import os
import unittest
from pathlib import Path

from click.testing import CliRunner, Result
from logging import Logger, getLogger
from inspect import stack
from com_enovation.enov import enov


class TestExcelDashboarder(unittest.TestCase):

    _logger: Logger = getLogger(__name__)

    def test_excel_dashboarder(self):
        """
        Note: When calling function 'CliRunner.invoke', we add a tag "# noinspection PyTypeChecker" not to raise a
        warning due to function "invoke" expecting function that we call to be a "BaseCommand", which does not seem to
        be the case...
        :return:
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # First, we cleanse the output file from previous run
        if Path(os.path.join(os.path.dirname(__file__), '02_actual_results.xls')).exists():
            os.remove(os.path.join(os.path.dirname(__file__), '02_actual_results.xls'))
        self.assertFalse(
            Path(os.path.join(os.path.dirname(__file__), '02_actual_results.xls')).exists(),
            f"We still have a file '{os.path.join(os.path.dirname(__file__), '02_actual_results.xls')}', that will "
            f"generate issue while executing the test..."
        )

        the_runner = CliRunner()

        # noinspection PyTypeChecker
        the_result: Result = the_runner.invoke(
            cli=enov,
            args=[
                # To get all the logs...
                '--verbose',

                # We load the Excel file
                'df-load-xls',
                '-c', '["Id", "Client", "Label", "Label Bis"]',
                os.path.join(os.path.dirname(__file__), '01_input_file.xls'),
                'df_data',

                # We load the config
                'dict-load-json',
                os.path.join(os.path.dirname(__file__), '01_config.json'),
                'dict_config',

                # We compute date predictability
                'dashboard',
                '--alias-parameters', '{"df_data": "df_data"}',
                '--parameters', '{"tokens": []}',
                'dict_config',
                os.path.join(os.path.dirname(__file__), '02_actual_results.xls')
            ],
            catch_exceptions=True
        )
        self.assertEqual(
            0,
            the_result.exit_code,
            f"Unexpected exit_code, with stdout: {the_result.stdout}"
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(os.path.dirname(__file__), '02_actual_results.xls')
            ),
            f"File '02_actual_results.xls' was not persisted..., with stdout: {the_result.stdout}"
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
