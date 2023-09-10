from inspect import stack
from logging import Logger, getLogger
from unittest import TestCase

from jsonschema import ValidationError

from com_enovation.toolbox.excel_dashboard.config_checker import ConfigChecker


class TestWorksheetAddTable(TestCase):

    _logger: Logger = getLogger(__name__)

    _dict_a_full_format: dict = {

        # to turn on or off the autofilter in the header row. It is on by default
        "autofilter": False,

        # to turn on or off the header row in the table. It is on by default
        "header_row": True,

        # to create columns of alternating color in the table. It is on by default
        "banded_columns": False,

        # to create rows of alternating color in the table. It is on by default
        "banded_rows": True,

        # to highlight the first column of the table. The type of highlighting will depend on the style of the table.
        # It may be bold text or a different color. It is off by default
        "first_column": True,

        # to highlight the last column of the table. The type of highlighting will depend on the style of the table.
        # It may be bold text or a different color. It is off by default
        "last_column": True,

        # to set the style of the table. Standard Excel table format names should be used (with matching capitalization)
        "style": "Table Style Medium 15",

        # to turn on the total row in the last row of a table. It is distinguished from the other rows by a different
        # formatting and also with dropdown SUBTOTAL functions
        "total_row": True,

        # default tables are named Table1, Table2, etc. The name parameter can be used to set the name of the table
        "name": "table_name",

        # to set properties for columns within the table
        "columns": [
            {
                # the column header
                "header": "the header",

                # the format for the column header
                "header_format": {
                    "font_name": "Times New Roman",
                    "font_size": 15,
                },

                # column formulas applied using the column formula property
                "formula": "=today()",

                # total captions are specified via the columns property and the total_string sub properties
                "total_string": "total",

                # total functions are specified via the columns property and the total_function sub properties
                # total_function is a string among: average, count_nums, count, max, min, std_dev, sum, var
                "total_function": "average",

                # to set a calculated value for the total_function using the total_value sub property. Only necessary
                # when creating workbooks for applications that cannot calculate the value of formulas automatically.
                # This is similar to setting the value optional property in write_formula()
                "total_value": 15,

                # "the format for the column"
                "format": {
                    "font_name": "Times New Roman",
                    "font_size": 15,
                }

            }
        ]
    }

    def test_01_successful(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/add_table/options",
            lst_widgets_json_schemas=[]
        )

        _the_config_checker.validate(
            dict_to_validate=self._dict_a_full_format
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_02_unexpected_tag(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/add_table/options",
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
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/add_table/options",
            lst_widgets_json_schemas=[]
        )

        _the_config_checker.validate(
            dict_to_validate={}
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_04_incorrect_format(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/add_table/options",
            lst_widgets_json_schemas=[]
        )

        _the_altered_dict: dict = dict(self._dict_a_full_format)
        _the_altered_dict["columns"] = [{
            # the column header
            "header": "the header",

            # the format for the column header
            "header_format": {
                "font_name": "Times New Roman",
                "font_size": 15,
                "jsg": "bou"
            },

            # column formulas applied using the column formula property
            "formula": "=today()",

            # total captions are specified via the columns property and the total_string sub properties
            "total_string": "total",

            # total functions are specified via the columns property and the total_function sub properties
            # total_function is a string among: average, count_nums, count, max, min, std_dev, sum, var
            "total_function": "average",

            # to set a calculated value for the total_function using the total_value sub property. Only necessary
            # when creating workbooks for applications that cannot calculate the value of formulas automatically.
            # This is similar to setting the value optional property in write_formula()
            "total_value": 15,

            # "the format for the column"
            "format": {
                "font_name": "Times New Roman",
                "font_size": 15,
            }

        }]

        with self.assertRaisesRegex(
                ValidationError,
                f"Additional properties are not allowed \\('jsg' was unexpected\\)"
        ):
            _the_config_checker.validate(
                dict_to_validate=_the_altered_dict
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
