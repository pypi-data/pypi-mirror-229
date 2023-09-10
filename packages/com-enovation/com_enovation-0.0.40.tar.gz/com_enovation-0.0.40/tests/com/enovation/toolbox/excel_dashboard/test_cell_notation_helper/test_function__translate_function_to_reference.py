from inspect import stack
from logging import Logger, getLogger
from unittest import TestCase

from com_enovation.toolbox.excel_dashboard.cell_notation_helper import CellNotationHelper


class TestCellNotationHelper_TranslateFormulaToReference(TestCase):

    _logger: Logger = getLogger(__name__)

    def test__function__translate_formula_to_reference(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _dict_test_data: dict = {
            '=function("")': '=function("")',
            '=@C3': '=D3',
            '=@$C3': '=$D3',
            '=function("@B3")': '=function("@B3")',
            '=function(@C3)': '=function(D3)',
            '=function([@C3])': '=function([@C3])',
            '=function(C:@C)': '=function(C:D)',
            '=function(C@3:@C10)': '=function(C5:D10)',
            '=RIGHT(@C@3,1)="A"': '=RIGHT(D5,1)="A"'
        }

        for k, v in _dict_test_data.items():
            _str_result: str = CellNotationHelper.translate_formula_to_reference(
                str_reference_address="B3",
                str_formula=k
            )
            self.assertEqual(
                first=v,
                second=_str_result,
                msg=f"Function CellNotationHelper.get_absolute_from_relative_address(str_reference_address='B3', "
                    f"str_relative_address='{k}') returned '{_str_result}' while we expected '{v}'."
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test__function__translate_formula_to_reference__tokenize(self):

        _dict_test_data: dict = {
            '=function("")': ["=function(", r'""', ")"],
            '=""&function("")': ["=", r'""', "&function(", r'""', ")"],
            '="with an escaped "" double quote" &function("")': ["=", r'"with an escaped "" double quote"',
                                                                 " &function(", r'""', ")"],
        }

        for k_expression, v_expected_tokens in _dict_test_data.items():

            _lst_the_tokens: list[str] = CellNotationHelper._translate_formula_to_reference__tokenize(
                str_formula=k_expression
            )

            self.assertListEqual(
                list1=v_expected_tokens,
                list2=_lst_the_tokens,
                msg=f"Error when processing the expression '{k_expression}'."
            )

    def test__function__translate_formula_to_reference__pattern_a1(self):
        _dict_test_data: dict = {
            "C5": "C5",
            "@C@5": "D7",
            "=function(C5)": "=function(C5)",

            "[@C5]": "[@C5]",
        }

        for k_expression, v_expected_transformed in _dict_test_data.items():

            _str_the_transformed: str = CellNotationHelper._translate_formula_to_reference__pattern_a1(
                str_formula_token=k_expression,
                str_reference_address="B3"
            )

            self.assertEqual(
                first=v_expected_transformed,
                second=_str_the_transformed,
                msg=f"Error when processing the expression '{k_expression}'."
            )

    def test__function__translate_formula_to_reference__pattern_aa(self):

        _dict_test_data: dict = {
            "C5": "C5",
            "@C@5": "@C@5",
            "=function(C5)": "=function(C5)",
            "@C5": "@C5",

            "C:C": "C:C",
            "@C:D": "D:D",
            "=function(C:@C)": "=function(C:D)",

            "[@C[label]]": "[@C[label]]",
            "=function([@C[label])": "=function([@C[label])",
        }

        for k_expression, v_expected_transformed in _dict_test_data.items():

            _str_the_transformed: str = CellNotationHelper._translate_formula_to_reference__pattern_aa(
                str_formula_token=k_expression,
                str_reference_address="B3"
            )

            self.assertEqual(
                first=v_expected_transformed,
                second=_str_the_transformed,
                msg=f"Error when processing the expression '{k_expression}'."
            )

    def test__function__translate_formula_to_reference__pattern_11(self):

        _dict_test_data: dict = {
            "C5": "C5",
            "@C@5": "@C@5",
            "=function(C5)": "=function(C5)",
            "@C5": "@C5",

            "C:C": "C:C",
            "@C:C": "@C:C",
            "=function(C:@C)": "=function(C:@C)",

            "5:5": "5:5",
            "@5:7": "7:7",
            "=function(5:@5)": "=function(5:7)",
        }

        for k_expression, v_expected_transformed in _dict_test_data.items():

            _str_the_transformed: str = CellNotationHelper._translate_formula_to_reference__pattern_11(
                str_formula_token=k_expression,
                str_reference_address="B3"
            )

            self.assertEqual(
                first=v_expected_transformed,
                second=_str_the_transformed,
                msg=f"Error when processing the expression '{k_expression}'."
            )
