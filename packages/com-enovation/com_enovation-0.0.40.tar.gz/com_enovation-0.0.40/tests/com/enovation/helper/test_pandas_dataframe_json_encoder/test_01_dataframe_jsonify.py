import json
import os
from inspect import stack
from logging import Logger, getLogger
from unittest import TestCase

from pandas import DataFrame, read_excel

from com_enovation.helper.json_encoder import JSONEncoder


class Test01DataframeJsonifyer(TestCase):

    _logger: Logger = getLogger(__name__)

    def test_01_dataframe_jsonifyer(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        df_the_dataframe: DataFrame = read_excel(
            io=os.path.join(os.path.dirname(__file__), 'TC_A_00.DataframeToJsonify.xls'),
            dtype="object",
        )

        str_the_json: str = json.dumps(
            obj=df_the_dataframe,
            cls=JSONEncoder
        )

        self.assertEqual(
            first='{"col1_str": {"0": "aaa", "1": "bbb", "2": "ccc", "3": "ddd", "4": "eee", "5": NaN}, "col2_obj": {"0'
                  '": "aaa", "1": "2021-03-12T00:00:00", "2": 13.2, "3": 13, "4": NaN, "5": "qdsf"}, "col3_date": {"0":'
                  ' 44217, "1": 44248, "2": 44276, "3": 44307, "4": 44337, "5": NaN}, "col4_float": {"0": 1.1, "1": 1.2'
                  ', "2": 1.3333333, "3": 1, "4": 3.51, "5": NaN}, "col5_int": {"0": 1, "1": 2, "2": 3, "3": 3, "4": 4,'
                  ' "5": NaN}, "Col 6 int": {"0": 1, "1": 2, "2": "3,5", "3": 4.4, "4": "dd", "5": NaN}}',
            second=str_the_json,
            msg="Unexpected json..."
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")
