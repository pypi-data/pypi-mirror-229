import unittest
from inspect import stack
from logging import getLogger, Logger

from com_enovation.toolbox.excel_dashboard.cell_notation_helper import CellNotationHelper


class TestFunction__IsAddressXxx(unittest.TestCase):

    _logger: Logger = getLogger(__name__)

    def test_function__transform_column_into_range_or_cell(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # 1. Correct columns: pattern and value
        for k, v in {
            "A:B": "A5:B15",
            "A:A": "A5:A15",
            "D:BC": "D5:BC15",

            # With @
            "@A:B": "@A5:B15",
            "D:@BC": "D5:@BC15",

            # With $
            "$A:B": "$A5:B15",
            "D:$BC": "D5:$BC15",
        }.items():
            self.assertEqual(
                first=v,
                second=CellNotationHelper.transform_column_into_range_or_cell(
                    str_column=k,
                    int_first_row=5,
                    int_last_row=15,
                    b_check_correct=True
                ),
                msg=f"Error when process address '{k}'."
            )
            self.assertEqual(
                first=v,
                second=CellNotationHelper.transform_column_into_range_or_cell(
                    str_column=k,
                    int_first_row=5,
                    int_last_row=15,
                    b_check_correct=False
                ),
                msg=f"Error when process address '{k}'."
            )

        # 2. Correct pattern, but not correct columns
        for k, v in {
            "B:A": "B5:A15",
            "BC:D": "BC5:D15",

            # With @
            "@B:A": "@B5:A15",
            "BC:@D": "BC5:@D15",

            # With $
            "$B:A": "$B5:A15",
            "BC:$D": "BC5:$D15",
        }.items():
            # self.assertEqual(
            #     first=v,
            #     second=CellNotationHelper.transform_column_into_range_or_cell(
            #         str_column=k,
            #         int_first_row=5,
            #         int_last_row=15,
            #         b_check_correct=True
            #     ),
            #     msg=f"Error when process address '{k}'."
            # )
            self.assertEqual(
                first=v,
                second=CellNotationHelper.transform_column_into_range_or_cell(
                    str_column=k,
                    int_first_row=5,
                    int_last_row=15,
                    b_check_correct=False
                ),
                msg=f"Error when process address '{k}'."
            )

        # 3. Returning a cell, not a range
        for k, v in {
            "A:A": "A5",

            # With @
            "@A:@A": "@A5",

            # With $
            "$A:$A": "$A5"
        }.items():
            self.assertEqual(
                first=v,
                second=CellNotationHelper.transform_column_into_range_or_cell(
                    str_column=k,
                    int_first_row=5,
                    int_last_row=5,
                    b_check_correct=True
                ),
                msg=f"Error when process address '{k}'."
            )
            self.assertEqual(
                first=v,
                second=CellNotationHelper.transform_column_into_range_or_cell(
                    str_column=k,
                    int_first_row=5,
                    int_last_row=5,
                    b_check_correct=False
                ),
                msg=f"Error when process address '{k}'."
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__transform_column_into_range__exceptions(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # 1. Crazy values
        for i_str_address in [
            "abc",
            " A3",
        ]:
            with self.assertRaisesRegex(Exception, f"The address '{i_str_address}' is not recognized as an address, "
                                                   f"and its pattern could not be determined."):
                CellNotationHelper.transform_column_into_range_or_cell(
                    str_column=i_str_address,
                    int_first_row=5,
                    int_last_row=15,
                    b_check_correct=True
                )
            with self.assertRaisesRegex(Exception, f"The address '{i_str_address}' is not recognized as an address, "
                                                   f"and its pattern could not be determined."):
                CellNotationHelper.transform_column_into_range_or_cell(
                    str_column=i_str_address,
                    int_first_row=5,
                    int_last_row=15,
                    b_check_correct=False
                )

        # 2. Not columns
        for i_str_address in [
            "A3",
            "A1:B2",
            "1:3"
        ]:
            with self.assertRaisesRegex(Exception,
                                        f"The parameter str_address '{i_str_address}' is not a column."):
                CellNotationHelper.transform_column_into_range_or_cell(
                    str_column=i_str_address,
                    int_first_row=5,
                    int_last_row=15,
                    b_check_correct=True
                )
            with self.assertRaisesRegex(Exception,
                                        f"The parameter str_address '{i_str_address}' is not a column."):
                CellNotationHelper.transform_column_into_range_or_cell(
                    str_column=i_str_address,
                    int_first_row=5,
                    int_last_row=15,
                    b_check_correct=False
                )

        # 3. Correct pattern, but not correct columns
        for k, v in {
            "B:A": "B5:A15",
            "BC:D": "BC5:D15",

            # With @
            "@B:A": "@B5:A15",
            "BC:@D": "BC5:@D15",

            # With $
            "$B:A": "$B5:A15",
            "BC:$D": "BC5:$D15",
        }.items():

            with self.assertRaisesRegex(Exception,
                                        f"The parameter str_address .* is not a correct column."):
                CellNotationHelper.transform_column_into_range_or_cell(
                    str_column=k,
                    int_first_row=5,
                    int_last_row=15,
                    b_check_correct=True
                )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__transform_columns_intersect_rows_into_range_or_cell(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_test in [
            {
                "label": "TC 01 - Vanilla use case",
                "col": "A:B", "row": "1:2",  # "check": True,
                "expected": "A1:B2"
            },
            {
                "label": "TC 02 - Returning a cell, not a range",
                "col": "A:A", "row": "3:3",  # "check": True,
                "expected": "A3"
            },
            {
                "label": "TC 03 - With @",
                "col": "@A:B", "row": "1:2", "check": False,
                "expected": "@A1:B2"
            },
            {
                "label": "TC 04 - A range, not a cell, due to the @",
                "col": "@A:A", "row": "3:3", "check": False,
                "expected": "@A3:A3"
            },
            {
                "label": "TC 05 - With $",
                "col": "A:$B", "row": "$1:2",  # "check": True,
                "expected": "A$1:$B2"
            },
            {
                "label": "TC 06 - Returning a cell, not a range",
                "col": "$A:$A", "row": "3:3",  # "check": True,
                "expected": "$A3"
            },
            {
                "label": "TC 07 - With @ and $",
                "col": "@$A:$B", "row": "1:$2", "check": False,
                "expected": "@$A1:$B$2"
            },
            {
                "label": "TC 08 - A range, not a cell, due to the $",
                "col": "$A:A", "row": "3:3",  # "check": True,
                "expected": "$A3:A3"
            },
        ]:
            if i_test.get("check", True) is True:
                self.assertEqual(
                    first=i_test["expected"],
                    second=CellNotationHelper.transform_columns_intersect_rows_into_range_or_cell(
                        str_columns=i_test["col"],
                        str_rows=i_test["row"],
                        b_check_correct=True
                    ),
                    msg=f"Error when process address test with label '{i_test['label']}', b_check_correct is True."
                )
            if i_test.get("check", False) is False:
                self.assertEqual(
                    first=i_test["expected"],
                    second=CellNotationHelper.transform_columns_intersect_rows_into_range_or_cell(
                        str_columns=i_test["col"],
                        str_rows=i_test["row"],
                        b_check_correct=False
                    ),
                    msg=f"Error when process address test with label '{i_test['label']}', b_check_correct is False."
                )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__transform_columns_intersect_rows_into_range__exceptions(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_test in [
            {
                "label": "TC 01 - totally wrong column",
                "col": "abc", "row": "1:2",  # "check": True,
                "exception": "The address 'abc' is not recognized as an address, and its pattern could not be "
                             "determined."
            },
            {
                "label": "TC 02 - totally wrong row",
                "col": "C:D", "row": "12",  # "check": True,
                "exception": "The address '12' is not recognized as an address, and its pattern could not be "
                             "determined."
            },
            {
                "label": "TC 03 - wrong column",
                "col": "D:C", "row": "1:2", "check": True,
                "exception": "The parameter str_columns 'D:C' is not a correct set of columns."
            },
            {
                "label": "TC 04 - wrong row",
                "col": "C:D", "row": "2:1", "check": True,
                "exception": "The parameter str_rows '2:1' is not a correct set of rows."
            },
        ]:
            if i_test.get("check", True) is True:
                with self.assertRaisesRegex(Exception, i_test["exception"]):
                    CellNotationHelper.transform_columns_intersect_rows_into_range_or_cell(
                        str_columns=i_test["col"],
                        str_rows=i_test["row"],
                        b_check_correct=True
                    )
            if i_test.get("check", False) is False:
                with self.assertRaisesRegex(Exception, i_test["exception"]):

                    CellNotationHelper.transform_columns_intersect_rows_into_range_or_cell(
                        str_columns=i_test["col"],
                        str_rows=i_test["row"],
                        b_check_correct=False
                    )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__transform_address_into_relative_and_absolute_address(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_test in [
            {
                "label": "TC 01",
                "parameters": {
                    "str_address": "A1:B2",
                    "b_first_col_at": True, "b_first_col_doll": True,
                    "b_last_col_at": True, "b_last_col_doll": True,
                    "b_first_row_at": True, "b_first_row_doll": True,
                    "b_last_row_at": True, "b_last_row_doll": True,
                },
                "result": "@$A@$1:@$B@$2"
                # "exception": "The address 'abc' is not recognized as an address, and its pattern could not be "
                #             "determined."
            },
            {
                "label": "TC 02",
                "parameters": {
                    "str_address": "A1:B2",
                    "b_first_col_at": True, "b_first_col_doll": False,
                    "b_last_col_at": False, "b_last_col_doll": True,
                    "b_first_row_at": False, "b_first_row_doll": True,
                    "b_last_row_at": True, "b_last_row_doll": False,
                },
                "result": "@A$1:$B@2"
                # "exception": "The address 'abc' is not recognized as an address, and its pattern could not be "
                #             "determined."
            },
            {
                "label": "TC 03 - set of columns",
                "parameters": {
                    "str_address": "A:B",
                    "b_first_col_at": False, "b_first_col_doll": True,
                    "b_last_col_at": True, "b_last_col_doll": False,
                    # "b_first_row_at": True, "b_first_row_doll": True,
                    # "b_last_row_at": True, "b_last_row_doll": True,
                },
                "result": "$A:@B"
                # "exception": "The address 'abc' is not recognized as an address, and its pattern could not be "
                #             "determined."
            },
            {
                "label": "TC 04 - set of rows",
                "parameters": {
                    "str_address": "1:3",
                    # "b_first_col_at": False, "b_first_col_doll": True,
                    # "b_last_col_at": True, "b_last_col_doll": False,
                    "b_first_row_at": False, "b_first_row_doll": True,
                    "b_last_row_at": True, "b_last_row_doll": False,
                },
                "result": "$1:@3"
                # "exception": "The address 'abc' is not recognized as an address, and its pattern could not be "
                #             "determined."
            },
            {
                "label": "TC 05 - cell",
                "parameters": {
                    "str_address": "A1",
                    "b_first_col_at": False, "b_first_col_doll": True,
                    # "b_last_col_at": True, "b_last_col_doll": False,
                    "b_first_row_at": True, "b_first_row_doll": False,
                    # "b_last_row_at": True, "b_last_row_doll": False,
                },
                "result": "$A@1"
                # "exception": "The address 'abc' is not recognized as an address, and its pattern could not be "
                #             "determined."
            },
            {
                "label": "TC 06 - no impact",
                "parameters": {
                    "str_address": "A1:B2",
                    # "b_first_col_at": True, "b_first_col_doll": True,
                    # "b_last_col_at": True, "b_last_col_doll": True,
                    # "b_first_row_at": True, "b_first_row_doll": True,
                    # "b_last_row_at": True, "b_last_row_doll": True,
                },
                "result": "A1:B2"
                # "exception": "The address 'abc' is not recognized as an address, and its pattern could not be "
                #             "determined."
            },
            {
                "label": "TC 07 - unset",
                "parameters": {
                    "str_address": "@$A@$1:@$B@$2",
                    "b_first_col_at": False,
                    # "b_first_col_doll": False,
                    # "b_last_col_at": False,
                    "b_last_col_doll": False,
                    "b_first_row_at": False,
                    # "b_first_row_doll": False,
                    # "b_last_row_at": False,
                    # "b_last_row_doll": False,
                },
                "result": "$A$1:@B@$2"
                # "exception": "The address 'abc' is not recognized as an address, and its pattern could not be "
                #             "determined."
            },
            {
                "label": "TC 0A - unexpected address",
                "parameters": {
                    "str_address": " A1",
                    "b_first_col_at": False, "b_first_col_doll": True,
                    # "b_last_col_at": True, "b_last_col_doll": False,
                    "b_first_row_at": True, "b_first_row_doll": False,
                    # "b_last_row_at": True, "b_last_row_doll": False,
                },
                # "result": "$A@1"
                "exception": "The address ' A1' is not recognized as an address, and it cannot be tokenized."
            },
            {
                "label": "TC 0B - unexpected change",
                "parameters": {
                    "str_address": "A1",
                    "b_first_col_at": False, "b_first_col_doll": True,
                    "b_last_col_at": True, "b_last_col_doll": False,
                    "b_first_row_at": True, "b_first_row_doll": False,
                    # "b_last_row_at": True, "b_last_row_doll": False,
                },
                # "result": "$A@1"
                "exception": "Trying to set last_col_at='True' for address 'A1', impossible."
            },
        ]:
            # No exception expected, but a result expected
            if "result" in i_test:

                self.assertEqual(
                    first=i_test["result"],
                    second=CellNotationHelper.transform_address_into_relative_and_absolute_address(
                        **i_test["parameters"]
                    ),
                    msg=f"Error when process test with label '{i_test['label']}'."
                )

            # Exception expected
            else:

                with self.assertRaisesRegex(Exception, i_test["exception"]):

                    CellNotationHelper.transform_address_into_relative_and_absolute_address(
                        **i_test["parameters"]
                    )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function__transform_address_into_tokens__transform_tokens_into_address(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_test in [
            {
                "label": "TC 01",
                "str_address": "A1:B2",
                "result": {
                    "first_col": "A", "first_col_at": False, "first_col_doll": False,
                    "first_row": "1", "first_row_at": False, "first_row_doll": False,
                    "last_col": "B", "last_col_at": False, "last_col_doll": False,
                    "last_row": "2", "last_row_at": False, "last_row_doll": False,
                },
                # "exception": "The address 'abc' is not recognized as an address, and its pattern could not be "
                #             "determined."
            },
            {
                "label": "TC 02",
                "str_address": "@A$1:$B@$2",
                "result": {
                    "first_col": "A", "first_col_at": True, "first_col_doll": False,
                    "first_row": "1", "first_row_at": False, "first_row_doll": True,
                    "last_col": "B", "last_col_at": False, "last_col_doll": True,
                    "last_row": "2", "last_row_at": True, "last_row_doll": True,
                },
                # "exception": "The address 'abc' is not recognized as an address, and its pattern could not be "
                #             "determined."
            },
            {
                "label": "TC 03 - columns",
                "str_address": "@A:@$B",
                "result": {
                    "first_col": "A", "first_col_at": True, "first_col_doll": False,
                    "first_row": None, "first_row_at": None, "first_row_doll": None,
                    "last_col": "B", "last_col_at": True, "last_col_doll": True,
                    "last_row": None, "last_row_at": None, "last_row_doll": None,
                },
                # "exception": "The address 'abc' is not recognized as an address, and its pattern could not be "
                #             "determined."
            },
            {
                "label": "TC 04 - rows",
                "str_address": "$1:@$2",
                "result": {
                    "first_col": None, "first_col_at": None, "first_col_doll": None,
                    "first_row": "1", "first_row_at": False, "first_row_doll": True,
                    "last_col": None, "last_col_at": None, "last_col_doll": None,
                    "last_row": "2", "last_row_at": True, "last_row_doll": True,
                },
                # "exception": "The address 'abc' is not recognized as an address, and its pattern could not be "
                #             "determined."
            },
            {
                "label": "TC 05 - exception",
                "str_address": " @A$1:$B@$2",
                # "result": {
                #     "first_col": "A", "first_col_at": True, "first_col_doll": False,
                #     "first_row": "1", "first_row_at": False, "first_row_doll": True,
                #     "last_col": "B", "last_col_at": False, "last_col_doll": True,
                #     "last_row": "2", "last_row_at": True, "last_row_doll": True,
                # },
                "exception": "The address ' \\@A\\$1:\\$B\\@\\$2' is not recognized as an address, and it cannot be "
                             "tokenized."
            },
        ]:
            # No exception expected, but a result expected
            if "result" in i_test:

                _dict_tokens: dict = CellNotationHelper.transform_address_into_tokens(
                    str_address=i_test["str_address"]
                )

                # We check the tokenization
                self.assertDictEqual(
                    d1=i_test["result"],
                    d2=_dict_tokens,
                    msg=f"Error when tokenizing test with label '{i_test['label']}'."
                )

                # We check the de-tokenization
                self.assertEqual(
                    first=i_test["str_address"],
                    second=CellNotationHelper.transform_tokens_into_address(
                        dict_tokens=_dict_tokens
                    ),
                    msg=f"Error when process test with label '{i_test['label']}'."
                )

            # Exception expected
            else:

                with self.assertRaisesRegex(Exception, i_test["exception"]):

                    CellNotationHelper.transform_address_into_tokens(
                        str_address=i_test["str_address"]
                    )

        # Eventually, we check exception when de-tokenizing an incorrect dictionary
        with self.assertRaisesRegex(Exception, "Unexpected keys in the parameters dict_tokens.keys\\(\\)='first_col, "
                                               "first_col_at, first_col_doll, first_row, first_row_at, first_row_doll, "
                                               "last_col, last_col_at, last_col_doll, last_row, last_row_at, "
                                               "last_row_doll, jsg'."):
            CellNotationHelper.transform_tokens_into_address(
                dict_tokens={
                    "first_col": None, "first_col_at": None, "first_col_doll": None,
                    "first_row": "1", "first_row_at": False, "first_row_doll": True,
                    "last_col": None, "last_col_at": None, "last_col_doll": None,
                    "last_row": "2", "last_row_at": True, "last_row_doll": True,
                    "jsg": 3
                }
            )

        with self.assertRaisesRegex(Exception, "Unexpected keys in the parameters dict_tokens.keys\\(\\)='first_col, "
                                               "first_col_at, first_col_doll, first_row, first_row_at, first_row_doll, "
                                               "last_col, last_col_at, last_col_doll'."):
            CellNotationHelper.transform_tokens_into_address(
                dict_tokens={
                    "first_col": None, "first_col_at": None, "first_col_doll": None,
                    "first_row": "1", "first_row_at": False, "first_row_doll": True,
                    "last_col": None, "last_col_at": None, "last_col_doll": None,
                    # "last_row": "2", "last_row_at": True, "last_row_doll": True,
                }
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
