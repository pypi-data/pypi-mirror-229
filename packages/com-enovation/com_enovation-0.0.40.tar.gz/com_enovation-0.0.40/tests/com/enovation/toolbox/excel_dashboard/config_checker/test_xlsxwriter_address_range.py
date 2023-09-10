from inspect import stack
from logging import Logger, getLogger
from unittest import TestCase

from jsonschema import ValidationError

from com_enovation.toolbox.excel_dashboard.config_checker import ConfigChecker


class TestAddressRange(TestCase):

    _logger: Logger = getLogger(__name__)

    def test_01_validated(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/address/range",
            lst_widgets_json_schemas=[]
        )

        for i_range in [
            "A1",
            "$A$1",
            "A1 A2",
            "A1 B2:$D$34"
        ]:
            # noinspection PyTypeChecker
            _the_config_checker.validate(dict_to_validate=i_range)

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_02_not_validated(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/address/range",
            lst_widgets_json_schemas=[]
        )

        for i_range in [
            "A1q",
            "$A$1 ",
            "A1  A2",
            "A1 2:$D$34"
        ]:
            with self.assertRaisesRegex(
                    ValidationError,
                    f"does not match"
            ):
                # noinspection PyTypeChecker
                _the_config_checker.validate(dict_to_validate=i_range)

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
