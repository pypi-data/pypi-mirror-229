import json
import os
import unittest
from inspect import stack
from logging import Logger, getLogger
from pathlib import Path

from com_enovation.toolbox.data_broadcaster.data_broadcaster import DataBroadcaster


class TestDataBroadcaster(unittest.TestCase):
    """
    In this test, we will do execute the following logic:
    - We load the various data (data prepared ahead of calling the broadcaster)
    - We then broadcast these data into several dashboards, after having filtered (and possibly refreshed) the data
    """
    _logger: Logger = getLogger(__name__)

    def test_data_broadcaster(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the config
        with open(Path(os.path.join(os.path.dirname(__file__), 'IN_test_data/BroadcasterConfiguration.json')), 'r') \
                as json_file:
            dict_config: dict = json.load(json_file)

        # From this distribution configuration, we adjust the paths to the Excel dashboards configurations
        for k_dashboard_config, v_dashboard_config in \
                dict_config[DataBroadcaster._const_str__config_tag__dashboards_cfgs__as_dict].items():
            v_dashboard_config[DataBroadcaster._const_str__config_tag__dashboard_cfg__path__as_path] = Path(
                os.path.join(
                    os.path.dirname(__file__),
                    "IN_test_data",
                    v_dashboard_config[DataBroadcaster._const_str__config_tag__dashboard_cfg__path__as_path]
                )
            )

        _obj_the_broadcaster: DataBroadcaster = DataBroadcaster(
            dict_config=dict_config
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
