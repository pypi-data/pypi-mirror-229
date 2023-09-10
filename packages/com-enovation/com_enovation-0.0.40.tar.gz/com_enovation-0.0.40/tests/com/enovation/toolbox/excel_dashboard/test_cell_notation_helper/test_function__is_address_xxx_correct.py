import unittest
from inspect import stack
from logging import getLogger, Logger

from com_enovation.toolbox.excel_dashboard.cell_notation_helper import CellNotationHelper


class TestFunction__IsAddressXxx(unittest.TestCase):

    _logger: Logger = getLogger(__name__)

    # Raising exceptions
    _list_the_incorrect_addresses: list[str] = [
        " D3",
        "32D",
        "3D",
        "A02",
    ]

    # Raising exceptions
    _list_the_incorrect_addresses_at: list[str] = [
        # Cell with @
        "@C5",
        "@$C5",
        "C@5",
        "C@$5",
        "@$C@$5",
        "@C$5",
        "$C@5",

        # Range with @
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

    _list_the_cell_addresses: list[str] = [
        "C5",
        "$C5",
        "C$5",
    ]

    _list_the_range_addresses: list[str] = [
        "C5:C5",
        "C5:C6", "C5:C41", "C5:C61",
        "C5:D5", "C5:AB5", "C5:DA5",
        "C5:D6", "C5:AB41", "C5:DA61",

        # With dollars
        "$C5:C5",
        "C$5:C6", "C5:$C41", "C5:C$61",
        "$C5:D$5", "C$5:$AB5", "$C$5:$DA5",
        "C$5:$D6", "$C5:AB$41", "C$5:$DA$61",
    ]

    _list_the_range_addresses_incorrect: list[str] = [
        "C5:C4", "C41:C5",
        "C5:B5", "BA5:C5", "CA5:C5",
                           
        "AA41:C5",

        # With dollars
        "$C5:C4", "C$41:C5",
        "C5:$B5", "BA5:C$5", "$CA5:C$5",
        "AA$41:$C5",
    ]

    _list_the_column_addresses: list[str] = [
        "C:C",
        "C:D",
        "C:AB",

        # With dollars
        "$C:C",
        "C:$D",
        "$C:$AB",
    ]

    _list_the_column_addresses_incorrect: list[str] = [
        "CA:C",
        "D:C",
        "AB:C",

        # With dollars
        "$CA:C",
        "D:$C",
        "$AB:$C",
    ]

    _list_the_row_addresses: list[str] = [
        "5:5",
        "5:9",
        "5:45",

        # With dollars
        "$5:5",
        "5:$9",
        "$5:$45",
    ]

    _list_the_row_addresses_incorrect: list[str] = [
        "55:5",
        "6:5",
        "45:5",

        # With dollars
        "$55:5",
        "6:$5",
        "$45:$5",
    ]

    def test_function__is_address_cell_correct(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # Cell address - correct --> True
        for i_str_address in self._list_the_cell_addresses:
            self.assertTrue(
                CellNotationHelper.is_address_cell_correct(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be OK."
            )

        # Cell address - incorrect --> False
        # for i_str_address in \
        #         self._list_the_range_addresses + \
        #         self._list_the_range_addresses_incorrect + \
        #         self._list_the_column_addresses + \
        #         self._list_the_column_addresses_incorrect + \
        #         self._list_the_row_addresses + \
        #         self._list_the_row_addresses_incorrect:
        #     self.assertFalse(
        #         CellNotationHelper.is_address_cell_correct(str_address=i_str_address),
        #         msg=f"Error when process address '{i_str_address}', expected to be NOK."
        #     )

        # Address - incorrect --> exception
        for i_str_address in self._list_the_incorrect_addresses:
            with self.assertRaisesRegex(Exception, ""):
                CellNotationHelper.is_address_cell_correct(str_address=i_str_address),

        # Address - not cell --> exception
        for i_str_address in \
                self._list_the_range_addresses + \
                self._list_the_range_addresses_incorrect + \
                self._list_the_column_addresses + \
                self._list_the_column_addresses_incorrect + \
                self._list_the_row_addresses + \
                self._list_the_row_addresses_incorrect:
            with self.assertRaisesRegex(
                    Exception,
                    f"The parameter str_address .* is not a cell."):
                CellNotationHelper.is_address_cell_correct(str_address=i_str_address),

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__is_address_range_correct(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # Range address - correct --> True
        for i_str_address in self._list_the_range_addresses:
            self.assertTrue(
                CellNotationHelper.is_address_range_correct(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be OK."
            )

        # Range address - incorrect --> False
        for i_str_address in self._list_the_range_addresses_incorrect:
            self.assertFalse(
                CellNotationHelper.is_address_range_correct(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be NOK."
            )

        # Address - incorrect --> exception
        for i_str_address in self._list_the_incorrect_addresses:
            with self.assertRaisesRegex(Exception, ""):
                CellNotationHelper.is_address_range_correct(str_address=i_str_address),

        # Address - not range --> exception
        for i_str_address in \
                self._list_the_cell_addresses + \
                self._list_the_column_addresses + \
                self._list_the_column_addresses_incorrect + \
                self._list_the_row_addresses + \
                self._list_the_row_addresses_incorrect:
            with self.assertRaisesRegex(
                    Exception,
                    f"The parameter str_address .* is not a range."):
                CellNotationHelper.is_address_range_correct(str_address=i_str_address),

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__is_address_column_correct(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # Column address - correct --> True
        for i_str_address in self._list_the_column_addresses:
            self.assertTrue(
                CellNotationHelper.is_address_column_correct(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be OK."
            )

        # Column address - incorrect --> False
        for i_str_address in self._list_the_column_addresses_incorrect:
            self.assertFalse(
                CellNotationHelper.is_address_column_correct(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be NOK."
            )

        # Address - incorrect --> exception
        for i_str_address in self._list_the_incorrect_addresses:
            with self.assertRaisesRegex(Exception, ""):
                CellNotationHelper.is_address_column_correct(str_address=i_str_address),

        # Address - not column --> exception
        for i_str_address in \
                self._list_the_cell_addresses + \
                self._list_the_range_addresses + \
                self._list_the_range_addresses_incorrect + \
                self._list_the_row_addresses + \
                self._list_the_row_addresses_incorrect:
            with self.assertRaisesRegex(
                    Exception,
                    f"The parameter str_address .* is not a column."):
                CellNotationHelper.is_address_column_correct(str_address=i_str_address),

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__is_address_row_correct(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # Row address - correct --> True
        for i_str_address in self._list_the_row_addresses:
            self.assertTrue(
                CellNotationHelper.is_address_row_correct(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be OK."
            )

        # Row address - incorrect --> False
        for i_str_address in self._list_the_row_addresses_incorrect:
            self.assertFalse(
                CellNotationHelper.is_address_row_correct(str_address=i_str_address),
                msg=f"Error when process address '{i_str_address}', expected to be NOK."
            )

        # Address - incorrect --> exception
        for i_str_address in self._list_the_incorrect_addresses:
            with self.assertRaisesRegex(Exception, ""):
                CellNotationHelper.is_address_row_correct(str_address=i_str_address),

        # Address - not row --> exception
        for i_str_address in \
                self._list_the_cell_addresses + \
                self._list_the_range_addresses + \
                self._list_the_range_addresses_incorrect + \
                self._list_the_column_addresses + \
                self._list_the_column_addresses_incorrect:
            with self.assertRaisesRegex(
                    Exception,
                    f"The parameter str_address .* is not a row."):
                CellNotationHelper.is_address_row_correct(str_address=i_str_address),

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_exception(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_str_address in self._list_the_incorrect_addresses:
            with self.assertRaisesRegex(Exception, f"The address '{i_str_address}' is not recognized as an address, "
                                                   f"and its pattern could not be determined."):
                CellNotationHelper.is_address_cell_correct(str_address=i_str_address)

            with self.assertRaisesRegex(Exception, f"The address '{i_str_address}' is not recognized as an address, "
                                                   f"and its pattern could not be determined."):
                CellNotationHelper.is_address_range_correct(str_address=i_str_address)

            with self.assertRaisesRegex(Exception, f"The address '{i_str_address}' is not recognized as an address, "
                                                   f"and its pattern could not be determined."):
                CellNotationHelper.is_address_column_correct(str_address=i_str_address)

            with self.assertRaisesRegex(Exception, f"The address '{i_str_address}' is not recognized as an address, "
                                                   f"and its pattern could not be determined."):
                CellNotationHelper.is_address_row_correct(str_address=i_str_address)

        for i_str_address in self._list_the_incorrect_addresses_at:
            with self.assertRaisesRegex(Exception, ""):
                CellNotationHelper.is_address_cell_correct(str_address=i_str_address)

            with self.assertRaisesRegex(Exception, ""):
                CellNotationHelper.is_address_range_correct(str_address=i_str_address)

            with self.assertRaisesRegex(Exception, ""):
                CellNotationHelper.is_address_column_correct(str_address=i_str_address)

            with self.assertRaisesRegex(Exception, ""):
                CellNotationHelper.is_address_row_correct(str_address=i_str_address)

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
