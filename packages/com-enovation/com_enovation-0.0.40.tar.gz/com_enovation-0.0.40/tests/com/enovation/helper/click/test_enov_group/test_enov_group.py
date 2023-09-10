import os
import unittest

import click
from click.testing import CliRunner, Result
from logging import Logger, getLogger
from inspect import stack

from com_enovation.helper.click.enov_group import EnovGroup


@click.command("set-jsg")
@click.option('--option-test/--no-option-test', type=bool)
@click.argument('arg-test', type=bool)
@click.pass_context
def set_jsg(ctx_context, option_test, arg_test):

    getLogger(__name__).debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

    ctx_context.obj["option_test"] = option_test
    ctx_context.obj["arg_test"] = arg_test

    getLogger(__name__).debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")


@click.command("get-nina")
@click.option('--option-test/--no-option-test', type=bool)
@click.argument('arg-test', type=bool)
@click.pass_context
def get_nina(ctx_context, option_test, arg_test):

    getLogger(__name__).debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

    if "option_test" not in ctx_context.obj:
        raise Exception(f"'option_test' not in ctx_context.obj")

    if ctx_context.obj["option_test"] == option_test:
        raise Exception(f"ctx_context.obj['option_test'] == option_test, while we expect the opposite"
                        f"\n\t- ctx_context.obj['option_test']: '{ctx_context.obj['option_test']}'"
                        f"\n\t- option_test: '{option_test}'")

    if "arg_test" not in ctx_context.obj:
        raise Exception(f"'arg_test' not in ctx_context.obj")

    if ctx_context.obj["arg_test"] == arg_test:
        raise Exception(f"ctx_context.obj['arg_test'] == arg_test, while we expect the opposite"
                        f"\n\t- ctx_context.obj['arg_test']: '{ctx_context.obj['arg_test']}'"
                        f"\n\t- arg_test: '{arg_test}'")

    if "loaded-csv" not in ctx_context.obj:
        raise Exception(f"'loaded-csv' not in ctx_context.obj")

    if len(ctx_context.obj["loaded-csv"].index) != 2:
        raise Exception(f"ctx_context.obj['loaded-csv'] has '{len(ctx_context.obj['loaded-csv'].index)}' rows, while 2 "
                        f"are expected.")

    getLogger(__name__).debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")


nina = EnovGroup(
    str_name="nina",
    lst_commands=[set_jsg, get_nina]
)


class TestExtendedEnov(unittest.TestCase):
    _logger: Logger = getLogger(__name__)

    def test_01_extending_enov_group(self):

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        the_runner = CliRunner()

        # First call, all correct
        the_result: Result = the_runner.invoke(
            cli=nina,
            args=[
                '--verbose',

                'set-jsg',
                '--option-test',
                'True',

                'df-load-csv',
                os.path.join(os.path.dirname(__file__), 'test.csv'),
                'loaded-csv',

                'get-nina',
                '--no-option-test',
                'False'
            ],
            catch_exceptions=False,
        )

        self.assertEqual(
            0,
            the_result.exit_code,
            f"Call 1, unexpected exit_code, with stdout: {the_result.stdout}"
        )
