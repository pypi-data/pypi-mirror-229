import os
from datetime import date
from inspect import stack
from logging import getLogger, Logger
from pathlib import Path
from unittest import TestCase

import xlsxwriter
from jsonschema import ValidationError
from pandas import DataFrame

from com_enovation.toolbox.excel_dashboard.config_checker import ConfigChecker
from com_enovation.toolbox.excel_dashboard.widgets.table_zoom.widget_table_zoom import WidgetTableZoom


class TestWidget(TestCase):

    _logger: Logger = getLogger(__name__)

    """
    We want to print a table of this kind
    
           |---------------------------------------------------------------|
           |- A ---------|- B ---------|- C ---------|- D ---------|- E ---|         
    -----                 -------------------------------------------------
    | 1 |    project ABC |  1-Jan-2022 |  1-Aug-2022 | 28-Aug-2022 | Trend |
    -----  --------------|-------------|-------------|-------------|-------|
    | 2 |  | weight      |     100 pts |     110 pts |     110 pts | Up    |
    -----  |-------------|-----------------------------------------|-------|
    | 3 |  | done        |      50 pts |      75 pts |      70 pts | Up    |
    -----  |-------------|-----------------------------------------|       |
    | 4 |  | progress    |         50% |         68% |         70% |       |
    -----  |-------------|-----------------------------------------|-------|
    | 5 |  | velocity    |              xxx pts/ mth | xxx pts/mth | Down  |
    -----  |-------------|-----------------------------------------|-------|
    | 6 |  | ***         | ***         | ***         | ***         | ***   |
    -----   ---------------------------------------------------------------
    """

    _test_data_by_pattern: list = [

        # Default values
        {"msg": "Default 1: default value", "test": {"value": 1.1}},
        {"msg": "Default 2: default parameter", "test": {"parameter": "Default 2"}},
        {
            "msg": "Default 3: EXCEPTION: both default value and default parameter",
            "test": {"value": 1.3, "parameter": "Default 3"},
            "exception": "We cannot have both default 'value' and default 'parameter' at the same time"
        },
        {
            "msg": "Default 4: EXCEPTION: empty",
            "test": {},
            "exception": "does not have enough properties"
        },

        # Pattern 1: one single cell, no list
        {
            "msg": "Pattern 1a: one single cell, no list - value",
            "test": {"C5": {"value": "Pattern 1a"}}
        },
        {
            "msg": "Pattern 1b: one single cell, no list - parameter",
            "test": {"C5": {"parameter": "Pattern 1b"}}
        },
        {
            "msg": "Pattern 1c: one single cell, no list - EXCEPTION: unexpected tag",
            "test": {"C5": {"format": {"bg_color": "black"}, "value": 1.3, "jsg": "Pattern 1c"}},
            "exception": "Additional properties are not allowed"
        },
        {
            "msg": "Pattern 1d: one single cell, no list - EXCEPTION: both value and parameter",
            "test": {"C5": {"format": {"bg_color": "black"}, "value": "Pattern 1d", "parameter": "Pattern 1d"}},
            "exception": "should not be valid under"
        },
        {
            "msg": "Pattern 1e: one single cell, no list - complex one",
            "test": {
                "format": {"bg_color": "gray", "fg_color": "white"},
                "parameter": "Pattern 1e",
                "conditional_formattings": [
                    {
                        "range": "@A@1:@A2",
                        "options": {
                            "type": "cell", "criteria": "equal to", "value": '"Failed"',
                            "format": {'bold': True, 'font_color': 'red'}
                        }
                    }
                ],
                "C5": {"format": {"bg_color": "black"}, "value": "Pattern 1e"}
            }
        },
        {
            "msg": "Pattern 1f: one single cell, no list - EXCEPTION: merge not allowed",
            "test": {"C5": {"format": {"bg_color": "black"}, "value": "Pattern 1d", "merged": True}},
            "exception": "should not be valid under"
        },
        {
            "msg": "Pattern 1g: one single cell, no list - one format only",
            "test": {"C5": {"format": {"bg_color": "black"}}},
        },
        {
            "msg": "Pattern 1h: one single cell, no list - EXCEPTION: empty cell",
            "test": {"C5": {}},
            "exception": "does not have enough properties"
        },

        # Pattern 2: range which replicates one cell
        {
            "msg": "Pattern 2a: range which replicates one cell - value",
            "test": {"C5:D@6": {"format": {"bg_color": "black"}, "value": "Pattern 2a"}}
        },
        {
            "msg": "Pattern 2b: range which replicates one cell - parameter",
            "test": {"C5:D@6": {"format": {"bg_color": "black"}, "parameter": "Pattern 2b"}}
        },
        {
            "msg": "Pattern 2c: range which replicates one cell - value, merged",
            "test": {"C5:D@6": {"format": {"bg_color": "black"}, "value": "Pattern 2c", "merged": True}}
        },
        {
            "msg": "Pattern 2d: range which replicates one cell - parameter, merged",
            "test": {"C5:D@6": {"format": {"bg_color": "black"}, "parameter": "Pattern 2d", "merged": True}}
        },
        {
            "msg": "Pattern 2e: range which replicates one cell - EXCEPTION: unexpected tag",
            "test": {"C5:D@6": {"format": {"bg_color": "black"}, "jsg": "Pattern 2e", "merged": True}},
            "exception": "is not valid under any of the given schemas"
        },
        {
            "msg": "Pattern 2f: range which replicates one cell - EXCEPTION: wrong parameter format",
            "test": {"C5:D@6": {"format": {"bg_color": "black"}, "parameter": 3.5, "merged": True}},
            "exception": "is not valid under any of the given schemas"
        },
        {
            "msg": "Pattern 2g: range which replicates one cell - EXCEPTION: empty cell",
            "test": {"C5:D@6": {}},
            "exception": "is not valid under any of the given schemas"
        },
        {
            "msg": "Pattern 2h: range which replicates one cell - only merge",
            "test": {"C5:D@6": {"merged": True}}
        },

        # Pattern 3: range as list of cells
        {
            "msg": "Pattern 3a: range as list of cells",
            "test": {"C5:D@6": [
                    {"format": {"border": 8, "border_color": "red"}, "value": "Pattern 3a"},
                    {"format": {"border": 8, "border_color": "red"}, "parameter": "Pattern 3a"}
            ]}
        },
        {
            "msg": "Pattern 3b: range as list of cells",
            "test": {"C5:D@6": [{"value": "Pattern 3b"}, {"parameter": "Pattern 3b"}]}
        },
        {
            "msg": "Pattern 3c: range as list of cells - EXCEPTION: empty list",
            "test": {"C5:D@6": []},
            "exception": "is not valid under any of the given schemas"
        },
        {
            "msg": "Pattern 3d: range as list of cells - EXCEPTION: empty cell in the list",
            "test": {"C5:D@6": [{}]},
            "exception": "is not valid under any of the given schemas"
        },
        {
            "msg": "Pattern 3e: range as list of cells - EXCEPTION: non cell in the list",
            "test": {"C5:D@6": [3, 2, 1]},
            "exception": "is not valid under any of the given schemas"
        },
        {
            "msg": "Pattern 3e: range as list of cells - EXCEPTION: merge not expected",
            "test": {"C5:D@6": [{"value": "Pattern 3e", "merged": True}]},
            "exception": "is not valid under any of the given schemas"
        },

        # Pattern 4: range with one value or parameter and a list of formats
        {
            "msg": "Pattern 4a: range with one value or parameter and a list of formats - one value only",
            "test": {"C5:D@6": {"value": "pattern 4a"}}
        },
        {
            "msg": "Pattern 4b: range with one value or parameter and a list of formats - one parameter only",
            "test": {"C5:D@6": {"parameter": "pattern 4b"}}
        },
        {
            "msg": "Pattern 4c: range with one value or parameter and a list of formats - list of formats only",
            "test": {"C5:D@6": {"format": [{"border": 8, "border_color": "red"}]}}
        },
        {
            "msg": "Pattern 4d: range with one value or parameter and a list of formats - one value & list of formats",
            "test": {"C5:D@6": {"value": 4.4, "format": [{"border": 8, "border_color": "red"}]}}
        },
        {
            "msg": "Pattern 4e: range with one value or parameter and a list of formats - one param & list of formats",
            "test": {"C5:D@6": {"parameter": "pattern 4e", "format": [{"border": 8, "border_color": "red"}]}}
        },
        {
            "msg": "Pattern 4f: range with one value or parameter and a list of formats - "
                   "EXCEPTION: empty list of formats",
            "test": {"C5:D@6": {"parameter": "pattern 4f", "format": []}},
            "exception": "is not valid under any of the given schemas"
        },
        {
            "msg": "Pattern 4g: range with one value or parameter and a list of formats - "
                   "EXCEPTION: list of formats containing a non format object",
            "test": {"C5:D@6": {"parameter": "pattern 4g", "format": [1, 2, 3]}},
            "exception": "is not valid under any of the given schemas"
        },
        {
            "msg": f"Pattern 4: range with format and value as: "
                   f"(i) Either one value to replicate (similar to pattern 2)"
                   f"(ii) Or list of values to apply (similar to patter 3)",
            "test": {
                "@B@1:@D@1": {
                    "format": {"border": 8, "border_color": "red"},
                    "value": ["date_1", "date_2", "date_3"]
                },
            }
        },

        # Pattern 5: range with list of values or parameters and a list of formats
        {
            "msg": "Pattern 5a: range with one value or parameter and a list of formats - list of values only",
            "test": {"C5:D@6": {"value": [5.1]}}
        },
        {
            "msg": "Pattern 5b: range with one value or parameter and a list of formats - list of parameters only",
            "test": {"C5:D@6": {"parameter": ["pattern 5b"]}}
        },
        {
            "msg": "Pattern 5c: range with one value or parameter and a list of formats - "
                   "list of values and list of formats",
            "test": {"C5:D@6": {"value": [5.3], "format":[{"border": 8, "border_color": "red"}]}}
        },
        {
            "msg": "Pattern 5d: range with one value or parameter and a list of formats - "
                   "list of parameters and list of formats",
            "test": {"C5:D@6": {"parameter": ["pattern 5d"], "format":[{"border": 8, "border_color": "red"}]}}
        },
        {
            "msg": "Pattern 5e: range with one value or parameter and a list of formats - "
                   "EXCEPTION: empty list of values",
            "test": {"C5:D@6": {"value": []}},
            "exception": "is not valid under any of the given schemas"
        },
        {
            "msg": "Pattern 5f: range with one value or parameter and a list of formats - "
                   "EXCEPTION: empty list of parameters",
            "test": {"C5:D@6": {"parameter": []}},
            "exception": "is not valid under any of the given schemas"
        },
        {
            "msg": "Pattern 5g: range with one value or parameter and a list of formats - "
                   "EXCEPTION: empty list of formats",
            "test": {"C5:D@6": {"format": []}},
            "exception": "is not valid under any of the given schemas"
        },
        {
            "msg": "Pattern 5h: range with one value or parameter and a list of formats - "
                   "EXCEPTION: weird value",
            "test": {"C5:D@6": {"value": [{"jsg": 3}]}},
            "exception": "is not valid under any of the given schemas"
        },
        {
            "msg": "Pattern 5i: range with one value or parameter and a list of formats - "
                   "EXCEPTION: weird parameter",
            "test": {"C5:D@6": {"parameter": [3.4]}},
            "exception": "is not valid under any of the given schemas"
        },
        {
            "msg": "Pattern 5j: range with one value or parameter and a list of formats - "
                   "EXCEPTION: weird format",
            "test": {"C5:D@6": {"format": [{"jsg": 3}]}},
            "exception": "is not valid under any of the given schemas"
        },

        # Pattern 6: range with list of values or list of parameters and one format
        {
            "msg": "Pattern 6a: range with list of values or list of parameters and one format -"
                   "List of values and one format",
            "test": {"C5:D@6": {"value": ["pattern 6a", 2, 3], "format": {"border": 8, "border_color": "red"}}}
        },
        {
            "msg": "Pattern 6b: range with list of values or list of parameters and one format -"
                   "List of parameters and one format",
            "test": {"C5:D@6": {"parameter": ["pattern", "6a", "3"], "format": {"border": 8, "border_color": "red"}}}
        },
        {
            "msg": "Pattern 6c: range with list of values or list of parameters and one format -"
                   "EXCEPTION: empty list of values",
            "test": {"C5:D@6": {"value": [], "format": {"border": 8, "border_color": "red"}}},
            "exception": "is not valid under any of the given schemas"
        },
        {
            "msg": "Pattern 6d: range with list of values or list of parameters and one format -"
                   "EXCEPTION: empty list of parameters",
            "test": {"C5:D@6": {"parameter": [], "format": {"border": 8, "border_color": "red"}}},
            "exception": "is not valid under any of the given schemas"
        },
        {
            "msg": "Pattern 6e: range with list of values or list of parameters and one format -"
                   "EXCEPTION: List of values, but empty format",
            "test": {"C5:D@6": {"value": ["pattern 6e", 2, 3], "format": {}}},
            "exception": "is not valid under any of the given schemas"
        },
    ]

    _zoom_config: dict = {
        "format": {
            "border": 7,
            "border_color": "grey"
        },
        "value": "--",
        "conditional_formattings": [
            {
                "range": "@A@1:@Z@9",
                "options": {
                    "type": "cell", "criteria": "equal to", "value": '"JSG"',
                    "format": {'bold': True, 'font_color': 'green'}
                }
            },
        ],
        # Pattern 1: single cell --> no list
        "@A@1": {
            "format": {"border": 8, "border_color": "red"},
            "value": "project ABC",
        },
        # Pattern 2: range which replicates one cell
        "@A@6:@E@6": {
            "format": {"border": 8, "border_color": "red"},
            "value": "***"
        },
        # Pattern 3: range as list of cells
        "@A@2:@A@5": [
            {
                "format": {"border": 8, "border_color": "red"},
                "value": "weight"
            },
            {
                "format": {"border": 8, "border_color": "red"},
                "value": "done"
            },
            {
                "format": {"border": 8, "border_color": "red"},
                "value": "progress"
            },
            {
                "format": {"border": 8, "border_color": "red"},
                "value": "velocity"
            },
        ],
        # Pattern 4: range with format and value as:
        # - Either one value to replicate (similar to pattern 2)
        # - Or list of values to apply (similar to patter 3)
        "@B@1:@D@1": {
            "format": {"border": 8, "border_color": "red"},
            "parameter": ["date_1", "date_2", "date_3"]
        },
        "@D@1:@D@1": {
            "format": [{"border": 8, "border_color": "red"}],
            "parameter": "date_1"
        },
        # Pattern 5: range to merge --> no list
        "@E@2:@E@5": {
            "value": "=100",
            "merged": True
        },
        # Check: default value
        "@F@1": {
            "format": [{"border": 8, "border_color": "red"}],
        },
        # Check: default value
        "@F@2": {
            "value": "jsg",
        },
    }
    _df_data: DataFrame = DataFrame(
        [
            [date(2022, 1, 1), 'project ABC', 100, 50],
            [date(2022, 8, 1), 'project ABC', 110, 75],
            [date(2022, 8, 28), 'project ABC', 100, 70],

            [date(2022, 1, 1), 'project DEF', 90, 45],
            [date(2022, 8, 1), 'project DEF', 100, 80],
            [date(2022, 8, 28), 'project DEF', 95, 81],
        ],
        columns=['measure date', 'project', 'weight', 'done']
    )

    def test_01_config_checker(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker: ConfigChecker = ConfigChecker(
            lst_widgets_json_schemas=[WidgetTableZoom.get_dict_config_schema()],
            str_base_json_schema_id=WidgetTableZoom.get_widget_id()
        )

        for i_test in self._test_data_by_pattern:
            if "exception" in i_test:
                with self.assertRaisesRegex(
                    Exception,
                    i_test["exception"],
                    msg=f"Exception not raised when executing test '{i_test['msg']}'."
                ):
                    _the_config_checker.validate(
                        dict_to_validate=i_test['test'],
                    )
            else:
                try:
                    _the_config_checker.validate(
                        dict_to_validate=i_test['test'],
                    )
                except ValidationError as exception:
                    raise Exception(f"Unexpected exception when executing test '{i_test['msg']}'.") from exception

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_02_unitary(self):

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We instantiate the widget
        _the_widget: WidgetTableZoom = WidgetTableZoom(
            str_address="B2",
            dict_parameters_map={},
            dict_config=self._zoom_config,
            dict_raw_parameters={
                "date_3": "that is date 3",
                "date_1": "that is date 1",
                "Trend": "that is a trend",
                "date_2": "that is date 2"
            },
            str_sheet_name="abc",
            dict_default_format={}
        )

        # We print it into an excel spreadsheet
        _the_workbook = xlsxwriter.Workbook(Path(os.path.join(os.path.dirname(__file__), 'TC02.excel.xlsx')))
        _the_worksheet = _the_workbook.add_worksheet()

        # We print the widget
        _the_widget.write_to_excel(
            wb_workbook=_the_workbook,
            ws_worksheet=_the_worksheet
        )

        # We close the workbook
        _the_workbook.close()

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function_list_parameters(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _lst_the_parameters: list = WidgetTableZoom._list_parameters(
            config=self._zoom_config
        )

        self.assertListEqual(
            list1=['date_1', 'date_2', 'date_3'],
            list2=_lst_the_parameters,
            msg=f"Function list_parameters did not return expected results"
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function_get_parameters(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _dict_the_parameters: dict = WidgetTableZoom._get_parameters(
            config=self._zoom_config,
            dict_parameters={"date_2": date(2022, 9, 3), "date_3": "", "Trend": "", "date_1": "1"}
        )

        self.assertDictEqual(
            d1={"date_2": date(2022, 9, 3), "date_3": "", "date_1": "1"},
            d2=_dict_the_parameters,
            msg=f"Function get_parameters did not return expected results"
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function_process_range(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _list_the_test_data: list = [
            {
                "msg": "# Pattern 1: single cell --> no list",
                "test": {
                    "C5": {"format": {"border": 8, "border_color": "red"}, "value": "project ABC"}
                },
                "expected": {
                    'C5': {
                        'function': 'write',
                        'parameter': {"format": {"border": 8, "border_color": "red"}, "value": "project ABC"}
                    }
                },
            },
            {
                "msg": "# Pattern 2: range which replicates one cell",
                "test": {"@A@6:@B@6": {"parameter": "param_1"}},
                "expected": {
                    'B8': {'function': 'write', 'parameter': {"format": {"border": 1}, "value": "val_1"}},
                    'C8': {'function': 'write', 'parameter': {"format": {"border": 1}, "value": "val_1"}},
                },
            },
            {
                "msg": "# Pattern 3: range as list of cells",
                "test": {
                    "@A@6:@B@6": [
                        {"format": {"border": 2}},
                        {"value": "pattern 3"}
                    ]
                },
                "expected": {
                    'B8': {'function': 'write', 'parameter': {"format": {"border": 2}, "value": "default"}},
                    'C8': {'function': 'write', 'parameter': {"format": {"border": 1}, "value": "pattern 3"}},
                },
            },
            {
                "msg": "# Pattern 4a: range with format and value as: (i) either one value to replicate (similar to "
                       "pattern 2) or (ii) list of values to apply (similar to patter 3)",
                "test": {
                    "@B@1:@D@1": {
                        "format": {"border_color": "brown"},
                        "parameter": ["param_1", "param_2", "param_3"]
                    }
                },
                "expected": {
                    'C3': {'function': 'write', 'parameter': {"format": {"border_color": "brown"}, "value": "val_1"}},
                    'D3': {'function': 'write', 'parameter': {"format": {"border_color": "brown"},
                                                              "value": date(2022, 9, 9)}},
                    'E3': {'function': 'write', 'parameter': {"format": {"border_color": "brown"}, "value": 1.5}},
                },
            },
            {
                "msg": "# Pattern 4b: range with format and value as: (i) either one value to replicate (similar to "
                       "pattern 2) or (ii) list of values to apply (similar to patter 3)",
                "test": {
                    "@D@1:@E@1": {
                        "format": [{"border": 0}, {"border": 1}],
                        "parameter": "param_1"
                    },
                },
                "expected": {
                    'E3': {'function': 'write', 'parameter': {"format": {"border": 0}, "value": "val_1"}},
                    'F3': {'function': 'write', 'parameter': {"format": {"border": 1}, "value": "val_1"}},
                },
            },
            {
                "msg": "# Pattern 5: range to merge --> no list",
                "test": {
                    "@E@2:@E@$5": {
                        "value": "=100",
                        "merged": True
                    }
                },
                "expected": {
                    'F4:F7': {'function': 'merge_range', 'parameter': {"format": {"border": 1}, "value": "=100"}}
                },
            },
        ]

        for i_test in _list_the_test_data:

            i_test_case: list = list(i_test["test"].items())[0]

            _the_result: dict = WidgetTableZoom._process_range(
                str_reference_address="B3",
                str_address=i_test_case[0],
                config=i_test_case[1],
                dict_parameters={"param_1": "val_1", "param_2": date(2022, 9, 9), "param_3": 1.5},
                dict_default_format={"border": 1},
                default_value="default"
            )

            self._logger.info(f"-------------------------------------------")
            self._logger.info(f"TEST CASE: {i_test['msg']}")
            self._logger.info(f"RESULT   : \n{_the_result}")

            self.assertDictEqual(
                d1=i_test["expected"],
                d2=_the_result,
                msg=i_test["msg"]
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_function_for_each_cell_in_range(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _lst_the_test_data: list = [
            {
                "msg": "not a range but one cell",
                "test": "A1",
                "expected": ["A1"]
            },
            {
                "msg": "not a range but one cell",
                "test": "$A1",
                "expected": ["A1"]
            },
            {
                "msg": "a simple range",
                "test": "A1:C2",
                "expected": ['A1', 'B1', 'C1', 'A2', 'B2', 'C2']
            },
            {
                "msg": "a simple range",
                "test": "$A1:C$2",
                "expected": ['A1', 'B1', 'C1', 'A2', 'B2', 'C2']
            },
        ]

        for i_test in _lst_the_test_data:
            self.assertListEqual(
                list1=i_test["expected"],
                list2=WidgetTableZoom._for_each_cell_in_range(i_test["test"]),
                msg=i_test["msg"]
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
