import unittest
from inspect import stack
from logging import getLogger, Logger

from com_enovation.toolbox.excel_dashboard.cell_notation_helper import CellNotationHelper


class TestFunction__IsPatternXxx(unittest.TestCase):

    _logger: Logger = getLogger(__name__)

    _list_the_incorrect_patterns: list[str] = [
        " D3",
        "32D"
    ]

    _list_the_cell_patterns: list[str] = [
        "--A--1",
        "@-A--1",
        "@$A--1",
        "-$A--1",
        "--A@-1",
        "--A@$1",
        "--A-$1",
        "@$A@$1"
    ]

    _list_the_range_patterns: list[str] = [
        "--A--1:@-A--1",
        "@-A--1:@$A--1",
        "@$A--1:-$A--1",
        "-$A--1:--A@-1",
        "--A@-1:--A@$1",
        "--A@$1:--A-$1",
        "--A-$1:@$A@$1",
        "@$A@$1:--A--1"
    ]

    _list_the_column_patterns: list[str] = [
        "--A:--A",
        "@-A:--A",
        "@$A:--A",
        "-$A:--A",
        "--A:@-A",
        "--A:@$A",
        "--A:-$A",
        "@$A:@$A"
    ]

    _list_the_row_patterns: list[str] = [
        "--1:--1",
        "@-1:--1",
        "@$1:--1",
        "-$1:--1",
        "--1:@-1",
        "--1:@$1",
        "--1:-$1",
        "@$1:@$1"
    ]

    def test_function__is_pattern_cell(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_str_pattern in self._list_the_cell_patterns:
            self.assertTrue(
                CellNotationHelper.is_pattern_cell(str_pattern=i_str_pattern),
                msg=f"Error when process pattern '{i_str_pattern}', expected to be OK."
            )

        for i_str_pattern in \
                self._list_the_range_patterns + \
                self._list_the_column_patterns + \
                self._list_the_row_patterns:
            self.assertFalse(
                CellNotationHelper.is_pattern_cell(str_pattern=i_str_pattern),
                msg=f"Error when process pattern '{i_str_pattern}', expected to be NOK."
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__is_pattern_range(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_str_pattern in self._list_the_range_patterns:
            self.assertTrue(
                CellNotationHelper.is_pattern_range(str_pattern=i_str_pattern),
                msg=f"Error when process pattern '{i_str_pattern}', expected to be OK."
            )

        for i_str_pattern in \
                self._list_the_cell_patterns + \
                self._list_the_column_patterns + \
                self._list_the_row_patterns:
            self.assertFalse(
                CellNotationHelper.is_pattern_range(str_pattern=i_str_pattern),
                msg=f"Error when process pattern '{i_str_pattern}', expected to be NOK."
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__is_pattern_column(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_str_pattern in self._list_the_column_patterns:
            self.assertTrue(
                CellNotationHelper.is_pattern_column(str_pattern=i_str_pattern),
                msg=f"Error when process pattern '{i_str_pattern}', expected to be OK."
            )

        for i_str_pattern in \
                self._list_the_cell_patterns + \
                self._list_the_range_patterns + \
                self._list_the_row_patterns:
            self.assertFalse(
                CellNotationHelper.is_pattern_column(str_pattern=i_str_pattern),
                msg=f"Error when process pattern '{i_str_pattern}', expected to be NOK."
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__is_pattern_row(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_str_pattern in self._list_the_row_patterns:
            self.assertTrue(
                CellNotationHelper.is_pattern_row(str_pattern=i_str_pattern),
                msg=f"Error when process pattern '{i_str_pattern}', expected to be OK."
            )

        for i_str_pattern in \
                self._list_the_cell_patterns + \
                self._list_the_range_patterns + \
                self._list_the_column_patterns:
            self.assertFalse(
                CellNotationHelper.is_pattern_row(str_pattern=i_str_pattern),
                msg=f"Error when process pattern '{i_str_pattern}', expected to be NOK."
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__is_pattern_correct(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_str_pattern in \
                self._list_the_cell_patterns + \
                self._list_the_range_patterns + \
                self._list_the_column_patterns + \
                self._list_the_row_patterns:
            self.assertTrue(
                CellNotationHelper.is_pattern_correct(str_pattern=i_str_pattern),
                msg=f"Error when process pattern '{i_str_pattern}', expected to be OK."
            )

        for i_str_pattern in self._list_the_incorrect_patterns:
            self.assertFalse(
                CellNotationHelper.is_pattern_correct(str_pattern=i_str_pattern),
                msg=f"Error when process pattern '{i_str_pattern}', expected to be NOK."
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_exception(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_pattern in self._list_the_incorrect_patterns:

            with self.assertRaisesRegex(Exception, f"Pattern '{i_pattern}' is incorrect, and not a cell!"):
                CellNotationHelper.is_pattern_cell(str_pattern=i_pattern),

            with self.assertRaisesRegex(Exception, f"Pattern '{i_pattern}' is incorrect, and not a range!"):
                CellNotationHelper.is_pattern_range(str_pattern=i_pattern),

            with self.assertRaisesRegex(Exception, f"Pattern '{i_pattern}' is incorrect, and not a column!"):
                CellNotationHelper.is_pattern_column(str_pattern=i_pattern),

            with self.assertRaisesRegex(Exception, f"Pattern '{i_pattern}' is incorrect, and not a row!"):
                CellNotationHelper.is_pattern_row(str_pattern=i_pattern),

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
