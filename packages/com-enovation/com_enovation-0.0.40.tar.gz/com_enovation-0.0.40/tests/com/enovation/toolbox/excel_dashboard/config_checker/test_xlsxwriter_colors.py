from inspect import stack
from logging import Logger, getLogger
from unittest import TestCase

from jsonschema import ValidationError

from com_enovation.toolbox.excel_dashboard.config_checker import ConfigChecker


class TestColors(TestCase):

    _logger: Logger = getLogger(__name__)

    def test_01_validated(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/colors",
            lst_widgets_json_schemas=[]
        )

        for i_color in [
            "red",
            "black",
            "#012345",
            "#A1D2B1"
        ]:
            # noinspection PyTypeChecker
            _the_config_checker.validate(dict_to_validate=i_color)

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_02_not_validated(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/colors",
            lst_widgets_json_schemas=[]
        )

        for i_color in [
            "redx",
            "#01234G"
        ]:
            with self.assertRaisesRegex(
                    ValidationError,
                    f"is not valid under any of the given schemas"
            ):
                # noinspection PyTypeChecker
                _the_config_checker.validate(dict_to_validate=i_color)

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
