from datetime import datetime
from inspect import stack
from logging import Logger, getLogger
from unittest import TestCase

from jsonschema import ValidationError

from com_enovation.toolbox.excel_dashboard.config_checker import ConfigChecker


class TestWorkbookSetProperties(TestCase):

    _logger: Logger = getLogger(__name__)

    _dict_a_full_format: dict = {
        "title": "a title to test",
        "subject": "a subject to test",
        "author": "an author to test",
        "manager": "a manager to test",
        "company": "a company to test",
        "category": "a category to test",
        "keywords": "a, keyword, to, test",
        "created": datetime(2018, 1, 1).strftime("yyyy-mm-dd"),
        "comments": "a comment to test",
        "status":  "a status to test",
        "hyperlink_base":  "a hyperlink_base to test"
    }

    def test_01_successful(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/workbook/set_properties/properties",
            lst_widgets_json_schemas=[]
        )

        _the_config_checker.validate(
            dict_to_validate=self._dict_a_full_format
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_02_unexpected_tag(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/workbook/set_properties/properties",
            lst_widgets_json_schemas=[]
        )

        _the_altered_dict: dict = dict(self._dict_a_full_format)
        _the_altered_dict["jsg"] = "bouh"

        with self.assertRaisesRegex(
                ValidationError,
                f"Additional properties are not allowed \\('jsg' was unexpected\\)"
        ):
            _the_config_checker.validate(
                dict_to_validate=_the_altered_dict
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_03_empty(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/workbook/set_properties/properties",
            lst_widgets_json_schemas=[]
        )

        _the_config_checker.validate(
            dict_to_validate={}
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
