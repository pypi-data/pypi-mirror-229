import os
import signal
import unittest
from pathlib import Path
from time import sleep

from click.testing import CliRunner, Result
from logging import Logger, getLogger
from inspect import stack

from pandas.testing import assert_frame_equal

from com_enovation.toolbox.predictability.dp_date_predictability.dp_computer import PredictabilityBean
from com_enovation.toolbox.predictability.dp_date_predictability.dp_persister import DatePredictabilityPersister
from com_enovation.enov import enov


class TestDatePredictability(unittest.TestCase):

    _logger: Logger = getLogger(__name__)

    def test_date_predictability(self):
        """
        Note: When calling function 'CliRunner.invoke', we add a tag "# noinspection PyTypeChecker" not to raise a
        warning due to function "invoke" expecting function that we call to be a "BaseCommand", which does not seem to
        be the case...
        :return:
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # First, we cleanse the output file from previous run
        if Path(os.path.join(os.path.dirname(__file__), '03_actual_results.xlsx')).exists():
            os.remove(os.path.join(os.path.dirname(__file__), '03_actual_results.xlsx'))
        self.assertFalse(
            Path(os.path.join(os.path.dirname(__file__), '03_actual_results.xlsx')).exists(),
            f"We still have a file '{os.path.join(os.path.dirname(__file__), '03_actual_results.xlsx')}', that will "
            f"generate issue while executing the test..."
        )

        the_runner = CliRunner()

        # ###############################################################
        # Step 1: we compute date predictability, and we persist the bean
        # noinspection PyTypeChecker
        the_result: Result = the_runner.invoke(
            cli=enov,
            args=[
                # 'enov-warm-up',
                '--verbose',

                # We load the Excel file
                'df-load-xls',
                '-c', '["id","timestamp","kick_off_date"]',
                os.path.join(os.path.dirname(__file__), '01_input_file.xlsx'),
                'df_raw',

                # We rename the columns
                'df-rename-columns',
                '-o', 'df_renamed',
                'df_raw',
                '{"id":"key","timestamp":"date","kick_off_date":"measure"}',

                # We cleanse null values
                'df-cleanse-null',
                '-o', 'df_cleansed',
                '-c', '["measure"]',
                'df_renamed',
                
                # # We compute date predictability
                'dp-compute',
                '--resample',
                'df_cleansed',
                'df_predictability',

                # # We persist the predictability bean
                'dp-persist',
                'df_predictability',
                os.path.join(os.path.dirname(__file__), '03_actual_results.xlsx'),
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
                os.path.join(os.path.dirname(__file__), '03_actual_results.xlsx')
            ),
            f"File '03_actual_results.xlsx' was not persisted..., with stdout: {the_result.stdout}"
        )

        # ###############################################################
        # Step 2: we reconcile the persisted bean
        obj_the_expected_results: PredictabilityBean = DatePredictabilityPersister().load(
            p_file_path=Path(os.path.join(os.path.dirname(__file__), '02_expected_results.xlsx')),
        )
        obj_the_actual_results: PredictabilityBean = DatePredictabilityPersister().load(
            p_file_path=Path(os.path.join(os.path.dirname(__file__), '03_actual_results.xlsx')),
        )
        assert_frame_equal(
            left=obj_the_expected_results.df_by_key,
            right=obj_the_actual_results._df_by_key,
            obj=f"The sheet {DatePredictabilityPersister.str_sheet_name__by_key} does not reconcile.",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )
        assert_frame_equal(
            left=obj_the_expected_results.df_by_measure,
            right=obj_the_actual_results.df_by_measure,
            obj=f"The sheet {DatePredictabilityPersister.str_sheet_name__by_measure} does not reconcile.",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )
        assert_frame_equal(
            left=obj_the_expected_results.df_historical,
            right=obj_the_actual_results.df_historical,
            obj=f"The sheet {DatePredictabilityPersister.str_sheet_name__historical} does not reconcile.",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        # ###############################################################
        # 3. We launch the dp_grapher
        if hasattr(os, 'fork'):
            childpid = os.fork()

            if childpid == 0:
                # noinspection PyTypeChecker
                CliRunner().invoke(
                        cli=enov,
                        args=[
                            '--verbose',

                            # We load the predictability bean
                            'dp-load',
                            os.path.join(os.path.dirname(__file__), '03_actual_results.xlsx'),
                            'df_predictability',

                            # We graph
                            'dp-graph',
                            'df_predictability'
                        ],
                        catch_exceptions=True
                    )

            else:
                # in the parent
                sleep(10)
                os.kill(childpid, signal.SIGINT)

        else:
            self._logger.warning(f"You must be executing on Windows, as os.fork() could be executed...")

        self.assertEqual(
            0,
            the_result.exit_code,
            f"Unexpected exit_code, with stdout: {the_result.stdout}"
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
