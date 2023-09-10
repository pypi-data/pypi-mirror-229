import json
import os
import unittest
from pathlib import Path
from logging import Logger, getLogger
from inspect import stack
from pandas import DataFrame, read_excel

from com_enovation.toolbox.data_handler.data_handler import DataHandler


class TestDataHandler(unittest.TestCase):
    _logger: Logger = getLogger(__name__)

    def test_data_handler(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the config
        with open(Path(os.path.join(os.path.dirname(__file__), '01.config.json')), 'r') as json_file:
            dict_config: dict = json.load(json_file)

        # we instantiate the data handler
        _dh_the_data_handler: DataHandler = DataHandler(dict_config=dict_config)

        # We load the data to handle
        _df_the_data_extract: DataFrame = read_excel(
            Path(os.path.join(os.path.dirname(__file__), '02.data_to_handle.xlsx'))
        )

        # We handle the data: one single sequence
        _df_the_return: DataFrame = _dh_the_data_handler.handle_data(
            df_data=_df_the_data_extract,
            sequence_alias="first sequence"
        )

        # We handle the data: one single sequence, but as a list
        _df_the_return: DataFrame = _dh_the_data_handler.handle_data(
            df_data=_df_the_data_extract,
            sequence_alias=["first sequence", "second sequence"]
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
