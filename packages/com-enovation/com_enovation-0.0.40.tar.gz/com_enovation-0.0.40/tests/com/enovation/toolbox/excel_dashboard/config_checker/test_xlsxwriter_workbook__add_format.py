from inspect import stack
from logging import Logger, getLogger
from unittest import TestCase

from jsonschema import ValidationError

from com_enovation.toolbox.excel_dashboard.config_checker import ConfigChecker


class TestWorkbookAddFormat(TestCase):

    _logger: Logger = getLogger(__name__)

    _dict_a_full_format: dict = {
        # Category Font. Font used in the cell. Excel can only display fonts that are installed on the system
        # that it is running on. Therefore it is best to use the fonts that come as standard such as
        # ‘Calibri’, ‘Times New Roman’ and ‘Courier New’. The default font for an unformatted cell in Excel
        # 2007+ is ‘Calibri’.
        "font_name": "Times New Roman",

        # Category Font. Size of the font used in the cell. Excel adjusts the height of a row to accommodate
        # the largest font size in the row.
        "font_size": 15,

        # Category Font. Color of the font used in the cell. Color can be a Html style #RRGGBB string or a
        # limited number of named colors. See website for further details:
        # https://xlsxwriter.readthedocs.io/format.html.
        "font_color": "red",

        # Category Font. To turn on bold for the format font.
        "bold": False,

        # Category Font. To turn on italic for the format font.
        "italic": True,

        # Category Font. To turn on underline for the format. The available underline styles are: 1 = Single
        # underline (the default), 2 = Double underline, 33 = Single accounting underline and 34 = Double
        # accounting underline.
        "underline": 2,

        # Category Font. To set the strikeout property of the font.
        "font_strikeout": True,

        # Category Font. To set the superscript/subscript property of the font. The available options are: 1
        # = Superscript and 2 = Subscript
        "font_script": 1,

        # Category Number. Set the number format for a cell. It controls whether a number is displayed as an
        # integer, a floating point number, a date, a currency value or some other user defined format. The
        # numerical format of a cell can be specified by using a format string or an index to one of Excel’s
        # built-in formats: 'd mmm yyyy' = Format string or '0x0F' = Format index. See website for indices to
        # Excel's built-in formats: https://xlsxwriter.readthedocs.io/format.html
        "num_format": "dd-mùm-yyyy",

        # Category Protection. To set the cell locked state. This property can be used to prevent
        # modification of a cell’s contents. Following Excel’s convention, cell locking is turned on by
        # default. However, it only has an effect if the worksheet has been protected using the worksheet
        # protect() method.
        "locked": True,

        # Category Protection. To hide formulas in a cell. This property is used to hide a formula while
        # still displaying its result. This is generally used to hide complex calculations from end users who
        # are only interested in the result. It only has an effect if the worksheet has been protected using
        # the worksheet protect() method.
        "hidden": False,

        # Category Alignment. To set the horizontal alignment for data in the cell: left, center, right,
        # fill, justify, center_across or distributed
        "align": "right",

        # Category Alignment. To set the vertical alignment for data in the cell: top, vcenter, bottom,
        # vjustify or vdistributed
        "valign": "top",

        # Category Alignment. To set the rotation of the text in a cell. Rotation angle is in the range -90
        # to 90 and 270. The angle 270 indicates text where the letters run from top to bottom.
        "rotation": 90,

        # Category Alignment. To turn text wrapping on for text in a cell.
        "text_wrap": True,

        # Category Alignment. To set the reading order for the text in a cell. This is useful when creating
        # Arabic, Hebrew or other near or far eastern worksheets. It can be used in conjunction with the
        # Worksheet right_to_left() method to also change the direction of the worksheet.
        "reading_order": True,

        # Category Alignment. To turn on the justify last text property. Only applies to Far Eastern versions
        # of Excel.
        "text_justlast": True,

        # Category Alignment. To center text across adjacent cells. Text can be aligned across two or more
        # adjacent cells. This is an alias for align='center_across'). Only the leftmost cell should contain
        # the text. The other cells in the range should be blank but should include the formatting.
        "center_across": True,

        # Category Alignment. To set the cell text indentation level, as an integer.
        "indent": 4,

        # Category Alignment. To turn on the text 'shrink to fit' for a cell.
        "shrink": True,

        # Category Pattern. To set the background pattern of a cell. The most common pattern is 1 which is a
        # solid fill of the background color. Pattern ranges from 0 to 18
        "pattern": 5,

        # Category Pattern. To set the color of the background pattern in a cell. If a pattern has not been
        # defined then a solid fill pattern is used as the default. The color can be a Html style #RRGGBB
        # string or a limited number of named colors.
        "bg_color": "black",

        # Category Pattern. To set the color of the foreground pattern in a cell. The color can be a Html
        # style #RRGGBB string or a limited number of named colors.
        "fg_color": "#FFFFFF",

        # Category Border. To set the cell border style. A cell border is comprised of a border on the
        # bottom, top, left and right. These can be set to the same value or individually using the relevant
        # properties. The following shows the border styles sorted by XlsxWriter index number: 0 = None,
        # 1 = Continuous weight 1, 2 = Continuous weight 2, 3 = Dash weight 1, 4 = Dot weight 1,
        # 5 = Continuous weight 3, 6 = Double weight 3, 7 = Continuous weight 0, 8 = Dash weight 2,
        # 9 = Dash Dot weight 1, 10 = Dash Dot weight 2, 11 = Dash Dot Dot weight, 12 = Dash Dot Dot weight
        # 2, 13 = SlantDash Dot weight 2
        "border": 0,

        # Category Border. To set the cell bottom border style.
        "bottom": 6,

        # Category Border. To set the cell top border style.
        "top": 5,

        # Category Border. To set the cell left border style.
        "left": 6,

        # "Category Border. To set the cell right border style."
        "right": 7,

        # Category Border. To set the color of the cell border. A cell border is comprised of a border on the
        # bottom, top, left and right. These can be set to the same value or individually using the relevant
        # properties. The color can be a Html style #RRGGBB string or a limited number of named colors.
        "border_color": "black",

        # Category Border. To set the color of the bottom cell border.
        "bottom_color": "black",

        # Category Border. To set the color of the top cell border.
        "top_color": "black",

        # Category Border. To set the color of the left cell border.
        "left_color": "green",

        # Category Border. To set the color of the right cell border.
        "right_color": "gray"
    }

    def test_01_successful(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/workbook/add_format/properties",
            lst_widgets_json_schemas=[]
        )

        _the_config_checker.validate(
            dict_to_validate=self._dict_a_full_format
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_02_unexpected_tag(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/workbook/add_format/properties",
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
            str_base_json_schema_id="https://enovation.com/xlsxwriter/workbook/add_format/properties",
            lst_widgets_json_schemas=[]
        )

        with self.assertRaisesRegex(
                ValidationError,
                f"does not have enough properties"
        ):
            _the_config_checker.validate(
                dict_to_validate={}
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_04_incorrect_color(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker = ConfigChecker(
            str_base_json_schema_id="https://enovation.com/xlsxwriter/workbook/add_format/properties",
            lst_widgets_json_schemas=[]
        )

        _the_altered_dict: dict = dict(self._dict_a_full_format)
        _the_altered_dict["font_color"] = "bouh"

        with self.assertRaisesRegex(
                ValidationError,
                f"'bouh' is not valid under any of the given schemas"
        ):
            _the_config_checker.validate(
                dict_to_validate=_the_altered_dict
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
