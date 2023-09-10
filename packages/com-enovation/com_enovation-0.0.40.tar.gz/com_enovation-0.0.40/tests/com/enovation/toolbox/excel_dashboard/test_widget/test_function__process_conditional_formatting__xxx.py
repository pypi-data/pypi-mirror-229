from inspect import stack
from logging import getLogger, Logger
from unittest import TestCase
from com_enovation.toolbox.excel_dashboard.widgets.widget import Widget


class TestWidget_FunctionProcessConditionalFormatting(TestCase):

    _logger: Logger = getLogger(__name__)

    _str_reference: str = "B3"
    _str_column_range_limit: str = "A:C"
    _str_row_range_limit = "2:5"

    _test_data__a_process_conditional_formatting__range: list = [
        {
            "label": "TC01 - Vanilla test case.",
            "str_range": "A@2:C@5",
            "result": "A4:C7"
        },
        {
            "label": "TC02 - Vanilla test case.",
            "str_range": "@A@1:B10",
            "result": "B3:B10"
        },
        {
            "label": "TC03 - Column range.",
            "str_range": "A:@B",
            "result": "A4:C7"
        },
        {
            "label": "TC04 - Row range.",
            "str_range": "1:@5",
            "result": "B1:D7"
        },
        {
            "label": "TC51 - dollars are forbidden.",
            "str_range": "$A5:B10",
            "exception": "There is '\\$' in the parameter str_range='\\$A5:B10', which is not expected\\."
        },
    ]

    def test_a_process_conditional_formatting__range(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        for i_test_case in self._test_data__a_process_conditional_formatting__range:

            # if test case expected NOT to raise an exception
            if "result" in i_test_case:
                self.assertEqual(
                    first=i_test_case["result"],
                    second=Widget._process_conditional_formatting__range(
                        str_range=i_test_case["str_range"],
                        str_reference_address=self._str_reference,
                        str_column_range_limit=self._str_column_range_limit,
                        str_row_range_limit=self._str_row_range_limit
                    ),
                    msg=i_test_case["label"]
                )

            # Else, test case expected to raise an exception
            else:

                with self.assertRaisesRegex(
                        Exception,
                        i_test_case["exception"]
                ):
                    Widget._process_conditional_formatting__range(
                        str_range=i_test_case["str_range"],
                        str_reference_address=self._str_reference,
                        str_column_range_limit=self._str_column_range_limit,
                        str_row_range_limit=self._str_row_range_limit
                    )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_a_process_conditional_formatting__multi_range(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _lst_correct_test_case__input: list[str] = [
            i_test_case["str_range"]
            for i_test_case in self._test_data__a_process_conditional_formatting__range
            if "result" in i_test_case
        ]

        _lst_correct_test_case__result: list[str] = [
            i_test_case["result"]
            for i_test_case in self._test_data__a_process_conditional_formatting__range
            if "result" in i_test_case
        ]

        _lst_incorrect_test_case__input: list[str] = [
            i_test_case["str_range"]
            for i_test_case in self._test_data__a_process_conditional_formatting__range
            if "exception" in i_test_case
        ]

        # We first test the successful concatenation
        self.assertEqual(
            first=" ".join(_lst_correct_test_case__result),
            second=Widget._process_conditional_formatting__multi_range(
                str_multi_range=" ".join(_lst_correct_test_case__input),
                str_reference_address=self._str_reference,
                str_column_range_limit=self._str_column_range_limit,
                str_row_range_limit=self._str_row_range_limit
            ),
            msg=f"Successful..."
        )

        # We go through each and every incorrect test case
        for i_test_case in _lst_incorrect_test_case__input:

            with self.assertRaisesRegex(
                    Exception,
                    ""
            ):
                Widget._process_conditional_formatting__multi_range(
                    str_multi_range=" ".join(_lst_correct_test_case__input+[i_test_case]),
                    str_reference_address=self._str_reference,
                    str_column_range_limit=self._str_column_range_limit,
                    str_row_range_limit=self._str_row_range_limit
                )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
