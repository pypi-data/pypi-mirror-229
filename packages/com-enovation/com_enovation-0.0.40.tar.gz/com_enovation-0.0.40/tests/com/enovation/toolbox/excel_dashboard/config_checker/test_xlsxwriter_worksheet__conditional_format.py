from datetime import datetime
from inspect import stack
from logging import Logger, getLogger
from unittest import TestCase

from jsonschema import ValidationError

from com_enovation.toolbox.excel_dashboard.config_checker import ConfigChecker


class TestWorksheetConditionalFormat(TestCase):

    _logger: Logger = getLogger(__name__)

    _dict_a_full_format_cell_equal: dict = {
        # most common conditional formatting type. It is used when a format is applied to a cell based on a
        # simple criterion
        "type": "cell",

        # to set the criteria by which the cell data will be evaluated. It has no default value. The most
        # common criteria as applied to {'type': 'cell'} are:
        # - between
        # - not between
        # - equal to
        # - not equal to
        # - greater than
        # - less than
        # - greater than or equal to
        # - less than or equal to
        "criteria": "equal to",

        # generally used along with the criteria parameter to set the rule by which the cell data will be
        # evaluated. If the type is cell and the value is a string then it should be double quoted, as
        # required by Excel
        "value": '"Failed"',

        # to specify the format that will be applied to the cell when the conditional formatting criterion is met
        "format": {'bold': True, 'font_color': 'red'},

        # to set the “stop if true” feature of a conditional formatting rule when more than one rule is
        # applied to a cell or a range of cells. When this parameter is set then subsequent rules are not
        # evaluated if the current rule is true:
        "stop_if_true": True,

        # The multi_range option is used to extend a conditional format over non-contiguous ranges.
        # It is possible to apply the conditional format to different cell ranges in a worksheet using multiple
        # calls to conditional_format(). However, as a minor optimization it is also possible in Excel to apply
        # the same conditional format to different non-contiguous cell ranges.
        # This is replicated in conditional_format() using the multi_range option. The range must contain the
        # primary range for the conditional format and any others separated by spaces.
        "multi_range": "A1:A2 B3:B4 D15"
    }

    _dict_a_full_format_cell_between: dict = {
        # most common conditional formatting type. It is used when a format is applied to a cell based on a
        # simple criterion
        "type": "cell",

        # to set the criteria by which the cell data will be evaluated. It has no default value. The most
        # common criteria as applied to {'type': 'cell'} are:
        # - between
        # - not between
        # - equal to
        # - not equal to
        # - greater than
        # - less than
        # - greater than or equal to
        # - less than or equal to
        "criteria": "between",

        # generally used along with the criteria parameter to set the rule by which the cell data will be
        # evaluated. If the type is cell and the value is a string then it should be double quoted, as
        # required by Excel
        # "value": '"Failed"',

        # to set the lower limiting value when the criteria is either 'between' or 'not between'
        "minimum": 2,

        # to set the upper limiting value when the criteria is either 'between' or 'not between'
        "maximum": 5,

        # to specify the format that will be applied to the cell when the conditional formatting criterion is met
        "format": {'bold': True, 'font_color': 'red'},

        # to set the “stop if true” feature of a conditional formatting rule when more than one rule is
        # applied to a cell or a range of cells. When this parameter is set then subsequent rules are not
        # evaluated if the current rule is true:
        "stop_if_true": True,

        # The multi_range option is used to extend a conditional format over non-contiguous ranges.
        # It is possible to apply the conditional format to different cell ranges in a worksheet using multiple
        # calls to conditional_format(). However, as a minor optimization it is also possible in Excel to apply
        # the same conditional format to different non-contiguous cell ranges.
        # This is replicated in conditional_format() using the multi_range option. The range must contain the
        # primary range for the conditional format and any others separated by spaces.
        "multi_range": "A1:A2 B3:B4"
    }

    _dict_a_full_format_date_equal: dict = {
        # date type is similar the cell type and uses the same criteria and values. However, the value, minimum
        # and maximum properties are specified as a datetime object
        "type": "date",

        # criteria is the same as {'type': 'date'}
        "criteria": "equal to",

        # the value, minimum and maximum properties are specified as a datetime object
        "value": f"{datetime.strptime('2011-01-01', '%Y-%m-%d')}",

        # format, stop_if_true and multi_range are the same as {'type': 'date'}
        "format": {'bold': True, 'font_color': 'red'},
        "stop_if_true": True,
        "multi_range": "A1:A2 B3:B4"
    }

    _dict_a_full_format_date_between: dict = {
        # date type is similar the cell type and uses the same criteria and values. However, the value, minimum
        # and maximum properties are specified as a datetime object
        "type": "date",

        # criteria is the same as {'type': 'date'}
        "criteria": "between",

        # the value, minimum and maximum properties are specified as a datetime object
        "minimum": f"{datetime.strptime('2011-01-01', '%Y-%m-%d')}",
        "maximum": f"{datetime.strptime('2011-01-01', '%Y-%m-%d')}",

        # format, stop_if_true and multi_range are the same as {'type': 'date'}
        "format": {'bold': True, 'font_color': 'red'},
        "stop_if_true": True,
        "multi_range": "A1:A2 B3:B4"
    }

    _dict_a_full_format_text: dict = {
        # to specify Excel’s “Specific Text” style conditional format. It is used to do simple string matching
        # using the criteria and value parameters:
        "type": "text",

        # the criteria can have one of the following values:
        # - containing
        # - not containing
        # - begins with
        # - ends with
        "criteria": "containing",

        # The value parameter should be a string or single character
        "value": "jsg",

        # format, stop_if_true and multi_range are the same as {'type': 'date'}
        "format": {'bold': True, 'font_color': 'red'},
        "stop_if_true": True,
        "multi_range": "A1:A2 B3:B4"
    }

    _dict_a_full_format_formula: dict = {
        # to specify a conditional format based on a user defined formula
        "type": "formula",

        # formula is specified in the criteria, written with the US style separator/range operator which is a
        # comma (not semi-colon) and should follow the same rules as write_formula().
        # See Non US Excel functions and syntax for a full explanation:
        # https://xlsxwriter.readthedocs.io/working_with_formulas.html
        "criteria": "=today()",

        # format, stop_if_true and multi_range are the same as {'type': 'date'}
        "format": {'bold': True, 'font_color': 'red'},
        "stop_if_true": True,
        "multi_range": "A1:A2 B3:B4"
    }

    def test_111_cell_equal_successful(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/conditional_format/options",
            lst_widgets_json_schemas=[]
        )

        _the_config_checker.validate(
            dict_to_validate=self._dict_a_full_format_cell_equal
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_112_cell_equal_unexpected_tag(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/conditional_format/options",
            lst_widgets_json_schemas=[]
        )

        _the_altered_dict: dict = dict(self._dict_a_full_format_cell_equal)
        _the_altered_dict["jsg"] = "bouh"

        with self.assertRaisesRegex(
                ValidationError,
                "{'type': 'cell', 'criteria': 'equal to', 'value': '\"Failed\"', 'format': {'bold': True, "
                "'font_color': 'red'}, 'stop_if_true': True, 'multi_range': 'A1:A2 B3:B4 D15', 'jsg': 'bouh'} is not valid "
                "under any of the given schemas"
        ):
            _the_config_checker.validate(
                dict_to_validate=_the_altered_dict
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_121_cell_between_successful(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/conditional_format/options",
            lst_widgets_json_schemas=[]
        )

        _the_config_checker.validate(
            dict_to_validate=self._dict_a_full_format_cell_between
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_122_cell_between_unexpected_tag(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/conditional_format/options",
            lst_widgets_json_schemas=[]
        )

        _the_altered_dict: dict = dict(self._dict_a_full_format_cell_between)
        _the_altered_dict["jsg"] = "bouh"

        with self.assertRaisesRegex(
                ValidationError,
                "{'type': 'cell', 'criteria': 'between', 'minimum': 2, 'maximum': 5, 'format': {'bold': True, "
                "'font_color': 'red'}, 'stop_if_true': True, 'multi_range': 'A1:A2 B3:B4', 'jsg': 'bouh'} is not valid "
                "under any of the given schemas"
        ):
            _the_config_checker.validate(
                dict_to_validate=_the_altered_dict
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_211_date_equal_successful(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/conditional_format/options",
            lst_widgets_json_schemas=[]
        )

        _the_config_checker.validate(
            dict_to_validate=self._dict_a_full_format_date_equal
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_212_date_equal_unexpected_tag(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/conditional_format/options",
            lst_widgets_json_schemas=[]
        )

        _the_altered_dict: dict = dict(self._dict_a_full_format_date_equal)
        _the_altered_dict["jsg"] = "bouh"

        with self.assertRaisesRegex(
                ValidationError,
                "{'type': 'date', 'criteria': 'equal to', 'value': '2011-01-01 00:00:00', 'format': {'bold': True, "
                "'font_color': 'red'}, 'stop_if_true': True, 'multi_range': 'A1:A2 B3:B4', 'jsg': 'bouh'} is not valid "
                "under any of the given schemas"
        ):
            _the_config_checker.validate(
                dict_to_validate=_the_altered_dict
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_221_date_between_successful(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/conditional_format/options",
            lst_widgets_json_schemas=[]
        )

        _the_config_checker.validate(
            dict_to_validate=self._dict_a_full_format_date_between
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_222_date_between_unexpected_tag(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/conditional_format/options",
            lst_widgets_json_schemas=[]
        )

        _the_altered_dict: dict = dict(self._dict_a_full_format_date_between)
        _the_altered_dict["jsg"] = "bouh"

        with self.assertRaisesRegex(
                ValidationError,
                "{'type': 'date', 'criteria': 'between', 'minimum': '2011-01-01 00:00:00', 'maximum': "
                "'2011-01-01 00:00:00', 'format': {'bold': True, 'font_color': 'red'}, 'stop_if_true': True, "
                "'multi_range': 'A1:A2 B3:B4', 'jsg': 'bouh'} is not valid under any of the given schemas"
        ):
            _the_config_checker.validate(
                dict_to_validate=_the_altered_dict
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_311_formula_successful(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/conditional_format/options",
            lst_widgets_json_schemas=[]
        )

        _the_config_checker.validate(
            dict_to_validate=self._dict_a_full_format_formula
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_312_formula_unexpected_tag(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/conditional_format/options",
            lst_widgets_json_schemas=[]
        )

        _the_altered_dict: dict = dict(self._dict_a_full_format_formula)
        _the_altered_dict["jsg"] = "bouh"

        with self.assertRaisesRegex(
                ValidationError,
                "{'type': 'formula', 'criteria': '=today\\(\\)', 'format': {'bold': True, 'font_color': 'red'}, "
                "'stop_if_true': True, 'multi_range': 'A1:A2 B3:B4', 'jsg': 'bouh'} is not valid under any of the "
                "given schemas"
        ):
            _the_config_checker.validate(
                dict_to_validate=_the_altered_dict
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_411_text_successful(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/conditional_format/options",
            lst_widgets_json_schemas=[]
        )

        _the_config_checker.validate(
            dict_to_validate=self._dict_a_full_format_text
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_412_text_unexpected_tag(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/conditional_format/options",
            lst_widgets_json_schemas=[]
        )

        _the_altered_dict: dict = dict(self._dict_a_full_format_text)
        _the_altered_dict["jsg"] = "bouh"

        with self.assertRaisesRegex(
                ValidationError,
                "{'type': 'text', 'criteria': 'containing', 'value': 'jsg', 'format': {'bold': True, 'font_color': "
                "'red'}, 'stop_if_true': True, 'multi_range': 'A1:A2 B3:B4', 'jsg': 'bouh'} is not valid under any of "
                "the given schemas"
        ):
            _the_config_checker.validate(
                dict_to_validate=_the_altered_dict
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_511_empty(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/conditional_format/options",
            lst_widgets_json_schemas=[]
        )

        with self.assertRaisesRegex(
                ValidationError,
                "{} does not have enough properties"
        ):
            _the_config_checker.validate(
                dict_to_validate={}
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_04_incorrect_format(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/worksheet/conditional_format/options",
            lst_widgets_json_schemas=[]
        )

        _the_altered_dict: dict = dict(self._dict_a_full_format_cell_equal)
        _the_altered_dict["format"] = {
            "font_name": "Times New Roman",
            "font_size": "15",
        }

        with self.assertRaisesRegex(
                ValidationError,
                f"'15' is not of type 'integer'"
        ):
            _the_config_checker.validate(
                dict_to_validate=_the_altered_dict
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
