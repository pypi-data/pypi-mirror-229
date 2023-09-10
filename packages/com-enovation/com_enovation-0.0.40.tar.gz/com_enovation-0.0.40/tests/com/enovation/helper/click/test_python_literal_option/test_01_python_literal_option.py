import json
import unittest

import click
from click.testing import CliRunner, Result
from logging import Logger, getLogger
from inspect import stack

from com_enovation.helper.click.python_literal_argument_and_option import PythonLiteralOption


@click.command('my-test')
@click.option('--a-list', cls=PythonLiteralOption, type=list, default=[])
@click.option('--a-dict', cls=PythonLiteralOption, type=dict, default={})
def my_test(a_list, a_dict):

    # 1. We check the list
    if isinstance(a_list, list):
        if a_list != ["o11", "o12", "o13"]:
            raise Exception(f"Parameter a_list is not as expected, but is '{a_list}'.")
    else:
        raise Exception(f"Option a_list is not a list, but a '{type(a_list)}'.")

    # We check the dictionary
    if isinstance(a_dict, dict):
        dict_expected: dict = {"k1": "v1", "k2": "v2"}
        if len(a_dict) != len(dict_expected):
            raise Exception(f"Option a_dict has '{len(a_dict)}' records, while '{len(dict_expected)}' is expected.")

        dict_diff: dict = {
            key: value for (key, value) in a_dict.items() if (
                (key not in dict_expected.keys()) | (dict_expected[key] != value)
            )
        }
        if len(dict_diff) > 0:
            raise Exception(f"Option a_dict is not as expected, but has the following items in difference: "
                            f"'{json.dumps(dict_diff)}'")
    else:
        raise Exception(f"Option a_dict is not a dict, but a '{type(a_dict)}'.")


class TestPythonLiteralOption(unittest.TestCase):
    _logger: Logger = getLogger(__name__)

    def test_date_predictability(self):

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        the_runner = CliRunner()

        the_result: Result = the_runner.invoke(
            cli=my_test,
            args=[
                '--a-list', '["o11", "o12", "o13"]',
                '--a-dict', '{"k1": "v1", "k2": "v2"}',
            ],
            catch_exceptions=False,
        )

        self.assertEqual(
            0,
            the_result.exit_code,
            f"Unexpected exit_code, with stdout: {the_result.stdout}"
        )
