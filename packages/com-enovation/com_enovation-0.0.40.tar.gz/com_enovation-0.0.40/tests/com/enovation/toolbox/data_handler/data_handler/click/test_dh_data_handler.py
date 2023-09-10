import os
from inspect import stack
from logging import getLogger, Logger
from unittest import TestCase
import click
from click.testing import CliRunner
from pandas import DataFrame

from com_enovation.enov import enov


class TestClickDhDataHandler(TestCase):

    _logger: Logger = getLogger(__name__)

    def test_01(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        runner = CliRunner()

        enov.add_command(check)

        # noinspection PyTypeChecker
        result = runner.invoke(
            cli=enov,
            args=[
                # To get all the logs...
                '--verbose',

                # We load the data handler configuration
                'dict-load-json',
                os.path.join(os.path.dirname(__file__), '../01.config.json'),
                'enov_config',

                # We load the excel file
                'df-load-xls',
                os.path.join(os.path.dirname(__file__), '../02.data_to_handle.xlsx'),
                'enov_data',

                'dh-sequence',
                'enov_data',
                'enov_config',
                'first sequence',
                'enov_first_output',

                'dh-sequences',
                'enov_data',
                'enov_config',
                '[\"first sequence\", \"second sequence\"]',
                'enov_second_output',

                'check'
            ]
        )

        self.assertEqual(
            first=0,
            second=result.exit_code,
            msg=str(result.exception)
        )


@click.command('check')
@click.pass_context
def check(ctx_context):
    # We get the outputs from both tests
    _df_the_first_output: DataFrame = ctx_context.obj["enov_first_output"]
    _df_the_second_output: DataFrame = ctx_context.obj["enov_second_output"]

    # We check the number of rows and columns
    TestCase().assertEqual(
        first=len(_df_the_first_output.index), second=34,
        msg="First Output: wrong number of rows"
    )

    # We check the number of rows and columns
    TestCase().assertEqual(
        first=len(_df_the_first_output.columns), second=18,
        msg="First Output: wrong number of columns"
    )

    # We check the number of rows and columns
    TestCase().assertEqual(
        first=len(_df_the_second_output.index), second=34,
        msg="Second Output: wrong number of rows"
    )

    # We check the number of rows and columns
    TestCase().assertEqual(
        first=len(_df_the_second_output.columns), second=19,
        msg="Second Output: wrong number of columns"
    )
