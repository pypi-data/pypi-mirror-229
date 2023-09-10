import json
import os
import unittest
from inspect import stack
from logging import Logger, getLogger
from pathlib import Path

from com_enovation.toolbox.data_broadcaster.data_broadcaster import DataBroadcaster
from com_enovation.toolbox.data_handler.data_handler import DataHandler


class TestFunction_InstantiateDataHandlers(unittest.TestCase):
    """
    Test the translation:
    - From the Data Broadcaster configuration, isolating the configurations for the Data Handlers
    - To the relevant Data Handlers, properly configured.
    """
    _logger: Logger = getLogger(__name__)

    def test_function_instantiate_data_handler(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the config
        with open(Path(os.path.join(os.path.dirname(__file__), 'IN_test_data/BroadcasterConfiguration.json')), 'r') \
                as json_file:
            dict_config: dict = json.load(json_file)

        # We load the expected result
        with open(Path(os.path.join(os.path.dirname(__file__), 'IN_test_data/ExpectedDataHandlerConfig.json')), 'r') \
                as json_file:
            dict_expected: dict = json.load(json_file)

        _dict_the_dhs: dict[str, DataHandler] = DataBroadcaster._instantiate_data_handlers(
            dict_distributions_configurations=dict_config[
                DataBroadcaster._const_str__config_tag__distributions_cfgs__as_dict
            ]
        )

        for k_dataset, v_dh in _dict_the_dhs.items():

            _dict_the_expected: dict = dict_expected[k_dataset]
            _dict_the_actual: dict = v_dh.dict_configuration

            self.assertDictEqual(
                d1=_dict_the_expected,
                d2=_dict_the_actual,
                msg="D1 (expected) is not equal to D2 (actual)."
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
