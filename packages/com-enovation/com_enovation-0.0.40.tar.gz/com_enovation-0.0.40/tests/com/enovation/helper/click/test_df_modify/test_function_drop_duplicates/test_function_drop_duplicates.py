from unittest import TestCase

import click
from click.testing import CliRunner, Result
from logging import Logger, getLogger
from inspect import stack

from pandas import DataFrame
from pandas.testing import assert_frame_equal

from com_enovation.helper.click.df_modify import df_compress


@click.group(chain=True)
@click.pass_context
def test_click(ctx_context):

    # Ensure that ctx_context.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    # This is effectively the context, that is shared across commands
    ctx_context.ensure_object(dict)

    # We set the test data for alias "jsg"
    # Same data set as in:
    # - file "tests/com/enovation/helper/test_pandas_dataframe_sampler/test_01_dataframe_sampler.py"
    # - test function "test_06_full_example_reordered_keep_last"
    ctx_context.obj["jsg"] = DataFrame(
        columns=[
            "key 1", "key 2", "order 1", "order 2", "val 1", "val 2"
        ],
        data=[
            # Universe 1
            ["k1a", "k2a", "o1b", "o2a", "v1b", "v2a"],   # 3 - in
            ["k1a", "k2a", "o1b", "o2c", "v1a", "v2a"],  # 5 - out
            ["k1a", "k2a", "o1a", "o2a", "v1a", "v2a"],   # 1 - in
            ["k1a", "k2a", "o1c", "o2b", "v1a", "v2a"],   # 6 - in
            ["k1a", "k2a", "o1c", "o2a", "v1a", "v2a"],  # 5 - out
            ["k1a", "k2a", "o1a", "o2b", "v1a", "v2a"],  # 2 - out
            ["k1a", "k2a", "o1b", "o2b", "v1a", "v2a"],   # 4 - in
        ]
    )


@click.command('test-check-click')
@click.pass_context
def test_check_click(ctx_context):
    df_expected: DataFrame = DataFrame(
        columns=[
            "key 1", "key 2", "order 1", "order 2", "val 1", "val 2", "expected result"
        ],
        data=[
            # Universe 1
            ["k1a", "k2a", "o1b", "o2a", "v1b", "v2a", 2],   # 3 - in
            ["k1a", "k2a", "o1b", "o2c", "v1a", "v2a", -1],  # 5 - out
            ["k1a", "k2a", "o1a", "o2a", "v1a", "v2a", 1],   # 1 - in
            ["k1a", "k2a", "o1c", "o2b", "v1a", "v2a", 4],   # 6 - in
            ["k1a", "k2a", "o1c", "o2a", "v1a", "v2a", -1],  # 5 - out
            ["k1a", "k2a", "o1a", "o2b", "v1a", "v2a", -1],  # 2 - out
            ["k1a", "k2a", "o1b", "o2b", "v1a", "v2a", 3],   # 4 - in
        ]
    )

    assert_frame_equal(
        left=df_expected[
            df_expected["expected result"] > 0
            ].sort_values(by="expected result")[ctx_context.obj["jsg"].columns].reset_index(drop=True),
        right=ctx_context.obj["jsg"].reset_index(drop=True),
        obj=f"Call 1",
        atol=0.00001,
        check_like=True  # To exclude index, and not to care about column ordering
    )


# We add the click command we want to test
# noinspection PyTypeChecker
test_click.add_command(df_compress)
test_click.add_command(test_check_click)


class TestFunctionDropDuplicates(TestCase):

    _logger: Logger = getLogger(__name__)

    def test_01_full_example_reordered_keep_last(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        """
        Note: When calling function CliRunner.invoke, we add a tag "# noinspection PyTypeChecker" not to raise a
        warning due to function "invoke" expecting function that we call to be a "BaseCommand", which does not seem to
        be the case...
        :return:
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        the_runner = CliRunner()

        # The click line is in 3 steps:
        # - First, the group "test_click", to instantiate the dataframe into the context
        # - Second, call the command drop_duplicates
        # - Third, call a test command to reconcile expected results
        the_result: Result = the_runner.invoke(
            cli=test_click,
            args=[
                'df-compress',
                '-k', '["key 1", "key 2"]',
                '-r', '["order 1", "order 2"]',
                '-v', '["val 1", "val 2"]',
                '--keep-last',
                'jsg',
                'test-check-click'
            ],
            catch_exceptions=False
        )
        self.assertEqual(
            0,
            the_result.exit_code,
            f"Unexpected exit_code, with stdout: {the_result.stdout}"
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")
