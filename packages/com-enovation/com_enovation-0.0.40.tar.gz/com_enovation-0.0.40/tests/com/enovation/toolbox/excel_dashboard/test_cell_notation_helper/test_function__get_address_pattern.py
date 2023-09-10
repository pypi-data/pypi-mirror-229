import unittest
from inspect import stack
from logging import getLogger, Logger

from com_enovation.toolbox.excel_dashboard.cell_notation_helper import CellNotationHelper


class test_function__get_address_pattern(unittest.TestCase):

    _logger: Logger = getLogger(__name__)

    def test_function(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _dict_the_test_data: dict = {

            # Pattern 1, cells
            "D3": "--A--1",

            "@D3": "@-A--1",
            "@$D3": "@$A--1",
            "$D3": "-$A--1",

            "D@3": "--A@-1",
            "D@$3": "--A@$1",
            "D$3": "--A-$1",

            "@$D@$3": "@$A@$1",

            # Pattern 2, range
            "C2:C3": "--A--1:--A--1",
            "C@2:C$3": "--A@-1:--A-$1",

            # Pattern 3, column
            "C:C": "--A:--A",
            "@C:@$C": "@-A:@$A",

            # Pattern 4, row
            "@$3:$3": "@$1:-$1"

        }

        for k, v in _dict_the_test_data.items():
            self.assertEqual(
                v,
                CellNotationHelper.get_address_pattern(
                    str_address=k
                ),
                msg=f"Error when trying to get pattern for '{k}'."
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_exception(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _dict_the_test_data: list[str] = [
            " D3",
            "32D"
        ]

        for i_address in _dict_the_test_data:

            with self.assertRaisesRegex(
                    Exception,
                    f"The address '{i_address}' is not recognized as an address, and its pattern could not "
                    f"be determined."
            ):
                CellNotationHelper.get_address_pattern(
                    str_address=i_address
                ),

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
