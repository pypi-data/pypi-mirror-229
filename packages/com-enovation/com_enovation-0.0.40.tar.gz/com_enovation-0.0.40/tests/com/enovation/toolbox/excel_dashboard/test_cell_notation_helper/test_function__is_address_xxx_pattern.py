import unittest
from inspect import stack
from logging import getLogger, Logger

from com_enovation.toolbox.excel_dashboard.cell_notation_helper import CellNotationHelper


class TestFunction__IsAddressXxx(unittest.TestCase):

    _logger: Logger = getLogger(__name__)

    _list_the_incorrect_addresses: list[str] = [
        " D3",
        "32D",
        "3D",
        "A02"
    ]

    _list_the_cell_addresses: list[str] = [
        "C5",

        "@C5",
        "@$C5",
        "$C5",

        "C@5",
        "C@$5",
        "C$5",

        "@$C@$5",
        "@C$5",
        "$C@5",
    ]

    _list_the_range_addresses: list[str] = [
        "C5:@CA61",

        "@C5:@$CA61",
        "@$C5:$CA61",
        "$C5:CA@61",

        "C@5:CA@$61",
        "C@$5:CA$61",
        "C$5:@$CA@$61",

        "@$C@$5:@CA$61",
        "@C$5:$CA@61",
        "$C@5:CA61",
    ]

    _list_the_column_addresses: list[str] = [
        "C:CA",

        "@C:CA",
        "@$C:CA",
        "$C:CA",

        "C:@CA",
        "C:@$CA",
        "C:$CA",

        "@$C:@$CA",
        "$C:@CA",
    ]

    _list_the_row_addresses: list[str] = [
        "5:63",

        "@5:63",
        "@$5:63",
        "$5:63",

        "5:@63",
        "5:@$63",
        "5:$63",

        "@5:@$63",
        "$5:@63",
    ]

    def test_function__is_address_cell_pattern(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_str_address in self._list_the_cell_addresses:
            self.assertTrue(
                CellNotationHelper.is_address_cell_pattern(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be OK."
            )

        for i_str_address in \
                self._list_the_range_addresses + \
                self._list_the_column_addresses + \
                self._list_the_row_addresses:
            self.assertFalse(
                CellNotationHelper.is_address_cell_pattern(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be NOK."
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__is_address_range_pattern(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_str_address in self._list_the_range_addresses:
            self.assertTrue(
                CellNotationHelper.is_address_range_pattern(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be OK."
            )

        for i_str_address in \
                self._list_the_cell_addresses + \
                self._list_the_column_addresses + \
                self._list_the_row_addresses:
            self.assertFalse(
                CellNotationHelper.is_address_range_pattern(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be NOK."
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__is_address_column_pattern(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_str_address in self._list_the_column_addresses:
            self.assertTrue(
                CellNotationHelper.is_address_column_pattern(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be OK."
            )

        for i_str_address in \
                self._list_the_cell_addresses + \
                self._list_the_range_addresses + \
                self._list_the_row_addresses:
            self.assertFalse(
                CellNotationHelper.is_address_column_pattern(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be NOK."
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__is_address_row_pattern(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_str_address in self._list_the_row_addresses:
            self.assertTrue(
                CellNotationHelper.is_address_row_pattern(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be OK."
            )

        for i_str_address in \
                self._list_the_cell_addresses + \
                self._list_the_range_addresses + \
                self._list_the_column_addresses:
            self.assertFalse(
                CellNotationHelper.is_address_row_pattern(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be NOK."
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__is_address_pattern_correct(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_str_address in \
                self._list_the_cell_addresses + \
                self._list_the_range_addresses + \
                self._list_the_column_addresses + \
                self._list_the_row_addresses:
            self.assertTrue(
                CellNotationHelper.is_address_pattern_correct(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be OK."
            )

        for i_str_address in self._list_the_incorrect_addresses:
            self.assertFalse(
                CellNotationHelper.is_address_pattern_correct(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be NOK."
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_exception(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_str_address in self._list_the_incorrect_addresses:
            with self.assertRaisesRegex(Exception, f"The address '{i_str_address}' is not recognized as an address, "
                                                   f"and its pattern could not be determined."):
                CellNotationHelper.is_address_cell_pattern(str_address=i_str_address),

            with self.assertRaisesRegex(Exception, f"The address '{i_str_address}' is not recognized as an address, "
                                                   f"and its pattern could not be determined."):
                CellNotationHelper.is_address_range_pattern(str_address=i_str_address),

            with self.assertRaisesRegex(Exception, f"The address '{i_str_address}' is not recognized as an address, "
                                                   f"and its pattern could not be determined."):
                CellNotationHelper.is_address_column_pattern(str_address=i_str_address),

            with self.assertRaisesRegex(Exception, f"The address '{i_str_address}' is not recognized as an address, "
                                                   f"and its pattern could not be determined."):
                CellNotationHelper.is_address_row_pattern(str_address=i_str_address),

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
