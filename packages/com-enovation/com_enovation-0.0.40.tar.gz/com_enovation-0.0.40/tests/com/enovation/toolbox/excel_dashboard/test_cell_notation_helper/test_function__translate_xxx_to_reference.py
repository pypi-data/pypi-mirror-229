from inspect import stack
from logging import Logger, getLogger
from unittest import TestCase

from com_enovation.toolbox.excel_dashboard.cell_notation_helper import CellNotationHelper


class TestFunction_TranslateXxxToReference(TestCase):

    _logger: Logger = getLogger(__name__)

    _lst_test_data_exceptions: list[str] = [
        "abc",
        "D:C",
        "3:4",
    ]

    _dict_test_data__range: dict = {
        "A1:C5": "A1:C5",

        "@A1:C5": "B1:C5",
        "A@1:C5": "A3:C5",
        "A1:@C5": "A1:D5",
        "A1:C@5": "A1:C7",
        "@A@1:@C@5": "B3:D7",

        # With dollars
        "@A1:C$5": "B1:C$5",
        "A@1:$C5": "A3:$C5",
        "A$1:@C5": "A$1:D5",
        "$A1:C@5": "$A1:C7",
        "@$A@$1:@$C@$5": "$B$3:$D$7",
    }

    _dict_test_data__column: dict = {
        "B:C": "B:C",
        "B:@C": "B:D",
        "@B:@C": "C:D",

        # With dollars
        "$B:C": "$B:C",
        "B:@$C": "B:$D",
        "@$B:@$C": "$C:$D",
    }

    _dict_test_data__row: dict = {
        "3:5": "3:5",
        "3:@5": "3:7",
        "@3:@5": "5:7",

        # With dollars
        "$3:5": "$3:5",
        "3:@$5": "3:$7",
        "@$3:@$5": "$5:$7",
    }

    _dict_test_data__cell: dict = {
        "C5": "C5",
        "@C5": "D5",
        "C@5": "C7",

        # With dollars
        "$C5": "$C5",
        "@C$5": "D$5",
        "$C@$5": "$C$7",
    }

    _dict_test_data__column_ref: dict = {
        "C": "C",
        "@C": "D",

        # With dollars
        "$C": "$C",
        "@$C": "$D",
    }

    _dict_test_data__row_ref: dict = {
        "5": "5",
        "@5": "7",

        # With dollars
        "$5": "$5",
        "@$5": "$7",
    }

    def test_function__translate_address_to_reference(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for k, v in (
                self._dict_test_data__range
                | self._dict_test_data__cell
                | self._dict_test_data__column
                | self._dict_test_data__row
        ).items():
            _str_result: str = CellNotationHelper.translate_address_to_reference(
                str_address=k,
                str_reference_cell="B3"
            )
            self.assertEqual(
                first=v,
                second=_str_result,
                msg=f"Function CellNotationHelper.translate_address_to_reference(str_reference_cell='B3', "
                    f"str_address='{k}') returned '{_str_result}' while we expected '{v}'."
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__translate_range_to_reference(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for k, v in self._dict_test_data__range.items():
            _str_result: str = CellNotationHelper.translate_range_to_reference(
                str_range=k,
                str_reference_cell="B3"
            )
            self.assertEqual(
                first=v,
                second=_str_result,
                msg=f"Function CellNotationHelper.translate_range_to_reference(str_reference_address='B3', "
                    f"str_relative_address='{k}') returned '{_str_result}' while we expected '{v}'."
            )

        # We check exceptions for unexpected formats...
        for i_data in (
                self._dict_test_data__cell
                | self. _dict_test_data__column_ref
                | self. _dict_test_data__row_ref
                | self._dict_test_data__column
                | self._dict_test_data__row
        ):

            with self.assertRaises(Exception):
                CellNotationHelper.translate_range_to_reference(
                    str_range=i_data,
                    str_reference_cell="B3"
                )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__translate_column_to_reference(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for k, v in self._dict_test_data__column.items():
            _str_result: str = CellNotationHelper.translate_column_to_reference(
                str_column=k,
                str_reference_cell="B3"
            )
            self.assertEqual(
                first=v,
                second=_str_result,
                msg=f"Function CellNotationHelper.translate_column_to_reference(str_reference_address='B3', "
                    f"str_column='{k}') returned '{_str_result}' while we expected '{v}'."
            )

        # We check exceptions for unexpected formats...
        for i_data in (
                self._dict_test_data__cell
                | self. _dict_test_data__column_ref
                | self. _dict_test_data__row_ref
                | self._dict_test_data__row
        ):

            with self.assertRaises(Exception):
                CellNotationHelper.translate_column_to_reference(
                    str_column=i_data,
                    str_reference_cell="B3"
                )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__translate_row_to_reference(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for k, v in self._dict_test_data__row.items():
            _str_result: str = CellNotationHelper.translate_row_to_reference(
                str_row=k,
                str_reference_cell="B3"
            )
            self.assertEqual(
                first=v,
                second=_str_result,
                msg=f"Function CellNotationHelper.translate_row_to_reference(str_reference_address='B3', "
                    f"str_row='{k}') returned '{_str_result}' while we expected '{v}'."
            )

        # We check exceptions for unexpected formats...
        for i_data in (
                self._dict_test_data__cell
                | self. _dict_test_data__column_ref
                | self. _dict_test_data__row_ref
                | self._dict_test_data__column
        ):

            with self.assertRaises(Exception):
                CellNotationHelper.translate_row_to_reference(
                    str_row=i_data,
                    str_reference_cell="B3"
                )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__translate_cell_to_reference(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for k, v in self._dict_test_data__cell.items():
            _str_result: str = CellNotationHelper.translate_cell_to_reference(
                str_cell=k,
                str_reference_cell="B3"
            )
            self.assertEqual(
                first=v,
                second=_str_result,
                msg=f"Function CellNotationHelper.translate_cell_to_reference(str_reference_address='B3', "
                    f"str_relative_address='{k}') returned '{_str_result}' while we expected '{v}'."
            )

        # We check exceptions for unexpected formats...
        for i_data in (
                self._dict_test_data__range
                | self. _dict_test_data__column_ref
                | self. _dict_test_data__row_ref
                | self._dict_test_data__column
                | self._dict_test_data__row
        ):

            with self.assertRaises(Exception):
                CellNotationHelper.translate_cell_to_reference(
                    str_cell=i_data,
                    str_reference_cell="B3"
                )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__translate_column_ref_to_reference(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for k, v in self._dict_test_data__column_ref.items():
            _str_result: str = CellNotationHelper.translate_column_ref_to_reference(
                str_column_ref=k,
                str_reference_cell="B3"
            )
            self.assertEqual(
                first=v,
                second=_str_result,
                msg=f"Function CellNotationHelper.translate_cell_to_reference(str_reference_address='B3', "
                    f"str_relative_address='{k}') returned '{_str_result}' while we expected '{v}'."
            )

        # We check exceptions for unexpected formats...
        for i_data in (
                self._dict_test_data__range
                | self. _dict_test_data__cell
                | self. _dict_test_data__row_ref
                | self._dict_test_data__column
                | self._dict_test_data__row
        ):

            with self.assertRaises(Exception):
                CellNotationHelper.translate_column_ref_to_reference(
                    str_column_ref=i_data,
                    str_reference_cell="B3"
                )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__translate_row_ref_to_reference(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for k, v in self._dict_test_data__row_ref.items():
            _str_result: str = CellNotationHelper.translate_row_ref_to_reference(
                str_row_ref=k,
                str_reference_cell="B3"
            )
            self.assertEqual(
                first=v,
                second=_str_result,
                msg=f"Function CellNotationHelper.translate_row_ref_to_reference(str_reference_address='B3', "
                    f"str_relative_address='{k}') returned '{_str_result}' while we expected '{v}'."
            )

        # We check exceptions for unexpected formats...
        for i_data in (
                self._dict_test_data__range
                | self. _dict_test_data__cell
                | self. _dict_test_data__column_ref
                | self._dict_test_data__column
                | self._dict_test_data__row
        ):

            with self.assertRaises(Exception):
                CellNotationHelper.translate_row_ref_to_reference(
                    str_row_ref=i_data,
                    str_reference_cell="B3"
                )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_exceptions(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # ############################################################################################################ #
        # 1. For all incorrect addresses                                                                               #
        # ############################################################################################################ #

        for i_data in self._lst_test_data_exceptions:

            with self.assertRaises(Exception):
                CellNotationHelper.translate_range_to_reference(
                    str_range=i_data,
                    str_reference_cell="B3"
                )

            with self.assertRaises(Exception):
                CellNotationHelper.translate_cell_to_reference(
                    str_cell=i_data,
                    str_reference_cell="B3"
                )

            with self.assertRaises(Exception):
                CellNotationHelper.translate_column_ref_to_reference(
                    str_column_ref=i_data,
                    str_reference_cell="B3"
                )

            with self.assertRaises(Exception):
                CellNotationHelper.translate_row_ref_to_reference(
                    str_row_ref=i_data,
                    str_reference_cell="B3"
                )

        # ############################################################################################################ #
        # 2. Incorrect reference cell                                                                                  #
        # ############################################################################################################ #

        with self.assertRaisesRegex(Exception, f"The address 'JSG' is not recognized as an address, and its pattern "
                                               f"could not be determined."):
            CellNotationHelper.translate_range_to_reference(
                str_range="J3",
                str_reference_cell="JSG"
            )

        with self.assertRaisesRegex(Exception, f"The address 'JSG' is not recognized as an address, and its pattern "
                                               f"could not be determined."):
            CellNotationHelper.translate_cell_to_reference(
                str_cell="J3",
                str_reference_cell="JSG"
            )

        with self.assertRaisesRegex(Exception, f"The address 'JSG' is not recognized as an address, and its pattern "
                                               f"could not be determined."):
            CellNotationHelper.translate_column_ref_to_reference(
                str_column_ref="J3",
                str_reference_cell="JSG"
            )

        with self.assertRaisesRegex(Exception, f"The address 'JSG' is not recognized as an address, and its pattern "
                                               f"could not be determined."):
            CellNotationHelper.translate_row_ref_to_reference(
                str_row_ref="J3",
                str_reference_cell="JSG"
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
