import os
import signal
import unittest
from time import sleep
# import json

from click.testing import CliRunner
from logging import Logger, getLogger
from inspect import stack
from com_enovation.enov import enov


class TestDatePredictability(unittest.TestCase):

    import logging.config

    logging.basicConfig(
        format='%(levelname)s [%(asctime)s]: %(message)s',
        level=logging.DEBUG
    )

    logging.info('com.enovation: tests logging initialized')

    _logger: Logger = getLogger(__name__)

    def test_bubbles(self):
        """
        Note: When calling function 'CliRunner.invoke', we add a tag "# noinspection PyTypeChecker" not to raise a
        warning due to function "invoke" expecting function that we call to be a "BaseCommand", which does not seem to
        be the case...

        python3 ./src/enov.py --verbose df-load-xls ./tests/test_enov/test_dash/test_bubbles/01_input_file.xlsx df_raw
        dict-set-json "{\"properties\": {\"title\":\"JSG\"},\"sheets\": {\"sheet abc\": {\"properties\": {},
        \"widgets\":[{\"id\":\"https://enovation.com/dash_application/bubbles\",\"properties\":{\"data\":\"df_raw\"}
        }]}}}" config ds-dash config


        :return:
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        the_runner = CliRunner()

        # ###############################################################
        # 3. We launch the ds_dash
        if hasattr(os, 'fork'):
            int_childpid: int = os.fork()

            if int_childpid == 0:
                # noinspection PyTypeChecker
                the_runner.invoke(
                        cli=enov,
                        args=[
                            '--verbose',

                            # We load the Excel file
                            'df-load-xls',
                            os.path.join(os.path.dirname(__file__), '01_input_file.xlsx'),
                            'df_raw',

                            # We set the widgets configuration
                            'dict-set-json',
                            '{'
                            '   "properties": {"title":"JSG"},'
                            '   "sheets": {'
                            '       "sheet abc": {'
                            '           "properties": {},'
                            '           "widgets": ['
                            '               {'
                            '                   "id": "https://enovation.com/dash_application/bubbles",'
                            '                   "properties": {'
                            '                       "data":"df_raw",'
                            '                       "px.scatter":{'
                            '                           "x":"Start Date",'
                            '                           "y":"Probability",'
                            '                           "animation_frame":"Timestamp",'
                            '                           "animation_group":"Project",'
                            '                           "size":"Effort",'
                            '                           "color":"Territory",'
                            '                           "hover_name":"Project",'
                            # '                           "log_x":True,'
                            # '                           "size_max":55,'
                            # '                           "range_x":[100, 100000],'
                            # '                           "range_y":[25, 90]'
                            '                       }'
                            '                   }'
                            '               }'
                            '           ]'
                            '       }'
                            '   }'
                            '}',
                            'config',

                            # We load the predictability bean
                            'ds-dash',
                            'config'
                            # os.path.join(os.path.dirname(__file__), '03_actual_results.xls'),
                            # 'df_predictability',
                            #
                            # # We graph
                            # 'dp-graph',
                            # 'df_predictability'
                        ],
                        catch_exceptions=True
                    )

            else:
                # in the parent
                sleep(60)
                os.kill(int_childpid, signal.SIGINT)

        else:
            self._logger.warning(f"You must be executing on Windows, as os.fork() could be executed...")

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
        raise Exception(f"Bubbles as div is effectively NOK, as it contains constants 'Sp - xxx' that might not be "
                        f"in the provided data... Bubbles widget is to be revisited!")
