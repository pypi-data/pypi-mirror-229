import os
from inspect import stack
from logging import getLogger, Logger
from pathlib import Path
from unittest import TestCase

import numpy
import xlsxwriter
from pandas import DataFrame, to_datetime
from pandas.testing import assert_frame_equal

from com_enovation.helper import excel_loader
from com_enovation.toolbox.excel_dashboard.excel_dashboarder import ExcelDashboarder
from com_enovation.toolbox.excel_dashboard.config_checker import ConfigChecker
from com_enovation.toolbox.excel_dashboard.widgets.table.widget_table import WidgetTable


class TestWidget(TestCase):

    _logger: Logger = getLogger(__name__)

    _table_config: dict = {

        "options": {

            # to turn on or off the autofilter in the header row. It is on by default
            "autofilter": False,

            # to turn on or off the header row in the table. It is on by default
            "header_row": True,

            # to create columns of alternating color in the table. It is on by default
            "banded_columns": False,

            # to create rows of alternating color in the table. It is on by default
            "banded_rows": True,

            # to highlight the first column of the table. The type of highlighting will depend on the style of the
            # table. It may be bold text or a different color. It is off by default
            "first_column": True,

            # to highlight the last column of the table. The type of highlighting will depend on the style of the
            # table. It may be bold text or a different color. It is off by default
            "last_column": True,

            # to set the style of the table. Standard Excel table format names should be used (with matching
            # capitalization)
            "style": "Table Style Medium 15",

            # to turn on the total row in the last row of a table. It is distinguished from the other rows by a
            # different formatting and also with dropdown SUBTOTAL functions
            "total_row": True,

            # default tables are named Table1, Table2, etc. The name parameter can be used to set the name of the
            # table
            "name": "jsg_table_name",

            # to set properties for columns within the table
            "columns": [
                {
                    # the column header
                    "header": "jsg data col 1",

                    # the format for the column header
                    "header_format": {
                       "font_name": "Times New Roman",
                       "font_size": 15,
                    },

                    # total captions are specified via the columns property and the total_string sub properties
                    "total_string": "jsg data col 1 total",

                    # total functions are specified via the columns property and the total_function sub properties
                    # total_function is a string among: average, count_nums, count, max, min, std_dev, sum, var
                    "total_function": "count",

                    # to set a calculated value for the total_function using the total_value sub property. Only
                    # necessary when creating workbooks for applications that cannot calculate the value of
                    # formulas automatically. This is similar to setting the value optional property in
                    # write_formula()
                    "total_value": 1,

                    # "the format for the column"
                    "format": {
                       "font_name": "Times New Roman",
                       "font_size": 15,
                    }
                },
                {
                    # the column header
                    "header": "jsg formula col 2",

                    # the format for the column header
                    "header_format": {
                       "font_name": "Times New Roman",
                       "font_size": 15,
                    },

                    # column formulas applied using the column formula property
                    "formula": "=today()",

                    # total captions are specified via the columns property and the total_string sub properties
                    "total_string": "jsg today total",

                    # total functions are specified via the columns property and the total_function sub properties
                    # total_function is a string among: average, count_nums, count, max, min, std_dev, sum, var
                    "total_function": "average",

                    # to set a calculated value for the total_function using the total_value sub property. Only
                    # necessary when creating workbooks for applications that cannot calculate the value of
                    # formulas automatically. This is similar to setting the value optional property in
                    # write_formula()
                    "total_value": 15,

                    # "the format for the column"
                    "format": {
                       "font_name": "Times New Roman",
                       "font_size": 15,
                    }
                },
                {
                    # the column header
                    "header": "jsg data col 3",

                    # "the format for the column"
                    "format": {
                       "font_name": "Times New Roman",
                       "font_size": 15
                    },
                },
                {
                    # the column header
                    "header": "jsg formula col 4",

                    # the format for the column header
                    "header_format": {
                       "font_name": "Times New Roman",
                       "font_size": 15,
                    },

                    # # total captions are specified via the columns property and the total_string sub properties
                    "total_string": "jsg today total",
                    #
                    # # total functions are specified via the columns property and the total_function sub properties
                    # # total_function is a string among: average, count_nums, count, max, min, std_dev, sum, var
                    "total_function": "count",
                    #
                    # # to set a calculated value for the total_function using the total_value sub property. Only
                    # # necessary when creating workbooks for applications that cannot calculate the value of
                    # # formulas automatically. This is similar to setting the value optional property in
                    # # write_formula()
                    "total_value": 15,
                    #
                    # # "the format for the column"
                    # "format": {
                    #    "font_name": "Times New Roman",
                    #    "font_size": 15
                    #    # "num_format": 'mmm d yyyy hh:mm AM/PM'
                    # },

                    # column formulas applied using the column formula property
                    # JSG as of 07-MAR-2023: "formula": "=today()+5000",
                    "formula": "=[[#This Row],[jsg formula col 2]]+5000",
                },
                {
                    # the column header
                    "header": "jsg today ter header",

                    # the format for the column header
                    "header_format": {
                       "font_name": "Times New Roman",
                       "font_size": 15,
                    },

                    # "the format for the column"
                    "format": {
                       "font_name": "Times New Roman",
                       "font_size": 15,
                       "num_format": 'MM/DD/YY'
                    },

                    # column formulas applied using the column formula property
                    "formula": "=DATE(2022,8,17)",
                },
            ]
        }
    }

    def test_01_config_checker(self):

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_config_checker: ConfigChecker = ConfigChecker(
            lst_widgets_json_schemas=[WidgetTable.get_dict_config_schema()],
            str_base_json_schema_id=WidgetTable.get_widget_id()
        )

        _the_config_checker.validate(
            dict_to_validate=self._table_config,
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_02_unitary(self):

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _df_data: DataFrame = DataFrame(
            [
                [10, 'a'],
                [20, 'b'],
                [30, 'c']
            ],
            columns=['jsg numbers col1', 'jsg string col2']
        )

        # We instantiate the widget
        _the_widget: WidgetTable = WidgetTable(
            str_address="B2",
            dict_parameters_map={"df_data": "jsg_data"},
            dict_config=self._table_config,
            dict_raw_parameters={"jsg_data": _df_data},
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

        # #############################################################################################################
        # We now read the Excel spreadsheet, and assert the result is as expected
        # #############################################################################################################
        _bean: excel_loader.ExcelLoaderBean = excel_loader.ExcelLoader().load_tables(
            str_path=os.path.join(os.path.dirname(__file__), 'TC02.excel.xlsx')
        )

        _df_read_data: DataFrame = _bean.dict_tables["jsg_table_name"]

        # Before doing anything, we expect:
        # - As many columns as configured
        # - One extra line, corresponding to the total line
        self.assertEqual(
            first=len(
                self._table_config[
                    WidgetTable.const_str__config_label__str_options
                ][
                    WidgetTable.const_str__config_label__str_columns
                ]
            ),
            second=len(_df_read_data.columns),
            msg="We expect the same number of columns as configured."
        )
        self.assertEqual(
            first=len(_df_data.index),
            second=len(_df_read_data.index)-1,
            msg="We expect one extra line in the excel spreadsheet, corresponding to the line total."
        )

        # We remove the formula columns, and apply the same name as the original data frame
        _df_read_data = _df_read_data[[
            i_column[WidgetTable.const_str__config_label__str_header]
            for i_column in self._table_config[
                WidgetTable.const_str__config_label__str_options
            ][
                WidgetTable.const_str__config_label__str_columns
            ]
            if WidgetTable.const_str__config_label__str_formula not in i_column
        ]]
        self.assertEqual(
            first=len(_df_data.columns),
            second=len(_df_read_data.columns),
            msg="After having removed the formula columns, we expect the same number of columns."
        )
        _df_read_data.columns = _df_data.columns

        # We remove the last total row
        _df_read_data = _df_read_data[:-1]

        assert_frame_equal(
            left=_df_data,
            right=_df_read_data,
            obj=f"Reading at the excel did not return the expected data.",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_03_application(self):

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _df_data: DataFrame = DataFrame(
            [
                [10, 'a'],
                [20, 'b'],
                [30, 'c']
            ],
            columns=['jsg numbers col1', 'jsg string col2']
        )

        _the_excel_dashboard: ExcelDashboarder = ExcelDashboarder()

        _the_excel_dashboard.excelize(
            p_output_file_path=Path(os.path.join(os.path.dirname(__file__), 'TC03.excel.xlsx')),
            dict_config={
                "sheets": {
                    "test_sheet_name": {
                        "widgets": {
                            "test_a_widget_label": {
                                "address": "B2",
                                "widget_id": "https://enovation.com/excel_dashboard/table",
                                "config": self._table_config,
                                "parameters_map": {"df_data": "jsg_data"}
                            }
                        }
                    }
                }
            },
            **{"jsg_data": _df_data}
        )

        # #############################################################################################################
        # We now read the Excel spreadsheet, and assert the result is as expected
        # #############################################################################################################
        _bean: excel_loader.ExcelLoaderBean = excel_loader.ExcelLoader().load_tables(
            str_path=os.path.join(os.path.dirname(__file__), 'TC03.excel.xlsx')
        )

        _df_read_data: DataFrame = _bean.dict_tables["jsg_table_name"]

        # Before doing anything, we expect:
        # - As many columns as configured
        # - One extra line, corresponding to the total line
        self.assertEqual(
            first=len(
                self._table_config[
                    WidgetTable.const_str__config_label__str_options
                ][
                    WidgetTable.const_str__config_label__str_columns
                ]
            ),
            second=len(_df_read_data.columns),
            msg="We expect the same number of columns as configured."
        )
        self.assertEqual(
            first=len(_df_data.index),
            second=len(_df_read_data.index)-1,
            msg="We expect one extra line in the excel spreadsheet, corresponding to the line total."
        )

        # We remove the formula columns, and apply the same name as the original data frame
        _df_read_data = _df_read_data[[
            i_column[WidgetTable.const_str__config_label__str_header]
            for i_column in self._table_config[
                WidgetTable.const_str__config_label__str_options
            ][
                WidgetTable.const_str__config_label__str_columns
            ]
            if WidgetTable.const_str__config_label__str_formula not in i_column
        ]]
        self.assertEqual(
            first=len(_df_data.columns),
            second=len(_df_read_data.columns),
            msg="After having removed the formula columns, we expect the same number of columns."
        )
        _df_read_data.columns = _df_data.columns

        # We remove the last total row
        _df_read_data = _df_read_data[:-1]

        assert_frame_equal(
            left=_df_data,
            right=_df_read_data,
            obj=f"Reading at the excel did not return the expected data.",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returned")

    def test_04_wrong_nb_of_columns(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _df_data: DataFrame = DataFrame(
            [
                [10, 'a', ""],
                [20, 'b', ""],
                [30, 'c', ""]
            ],
            columns=['jsg numbers col1', 'jsg string col2', 'jsg string col3']
        )

        # We instantiate the widget
        with self.assertRaisesRegex(
                Exception,
                f"We do not have a coherent number of columns"
                f"[\\s\\S]*df_data contains '3' records"
                f"[\\s\\S]*configuration contains in total '5' columns"
                f"[\\s\\S]*among which, '2' are non formula"
        ):
            _the_widget: WidgetTable = WidgetTable(
                str_address="B2",
                dict_parameters_map={"df_data": "jsg_data"},
                dict_config=self._table_config,
                dict_raw_parameters={"jsg_data": _df_data},
                str_sheet_name="abc",
                dict_default_format={}
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_05_duplicated_columns_labels(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _df_data: DataFrame = DataFrame(
            [
                [10, 'a'],
                [20, 'b'],
                [30, 'c']
            ],
            columns=['jsg numbers col1', 'jsg numbers col1']
        )

        # We instantiate the widget
        with self.assertRaisesRegex(
                Exception,
                f"In the configuration of the widget Table, you mentioned several columns with the same labels... "
                f"Check columns labelled 'jsg data col 1'."
        ):
            _the_widget: WidgetTable = WidgetTable(
                str_address="B2",
                dict_parameters_map={"df_data": "jsg_data"},
                dict_config={
                    "options": {
                        "columns": [
                            {"header": "jsg data col 1"},
                            {"header": "jsg data col 1"},
                            {"header": "jsg today ter header", "formula": "=DATE(2022,8,17)"}
                        ]
                    }
                },
                dict_raw_parameters={"jsg_data": _df_data},
                str_sheet_name="abc",
                dict_default_format={}
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_06_nan_values(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_excel_dashboard: ExcelDashboarder = ExcelDashboarder()

        _df_data: DataFrame = DataFrame(
            [
                [10, 'a'],
                [20, 'b'],
                [30, numpy.nan]
            ],
            columns=['jsg numbers col1', 'jsg string col2']
        )

        _the_excel_dashboard.excelize(
            p_output_file_path=Path(os.path.join(os.path.dirname(__file__), 'TC06.excel.xlsx')),
            dict_config={
                "workbook.options": {"nan_inf_to_errors": True},
                "sheets": {
                    "test_sheet_name": {
                        "worksheet.freeze_panes": {"row": 1, "col":  1},
                        "worksheet.set_column": [
                            {
                                "first_col": 0,
                                "last_col": 1,
                                "width": 50
                            }
                        ],
                        "widgets": {
                            "test_a_widget_label": {
                                "address": "A1",
                                "widget_id": "https://enovation.com/excel_dashboard/table",
                                "config": {
                                    "options": {
                                        "columns": [
                                            {"header": "jsg numbers col1"},
                                            {"header": "jsg string col2"}
                                        ],
                                        "total_row": True
                                    }
                                },
                                "parameters_map": {
                                    "df_data": "df_data"
                                }
                            }
                        }
                    }
                }
            },
            df_data=_df_data
        )

    def test_07_total_row(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _df_data: DataFrame = DataFrame(
            [
                [10, 'a'],
                [20, 'b']
            ],
            columns=['jsg numbers col1', 'jsg string col2']
        )

        # #############################################################################################################
        # 1. Without any total row!

        # 1.1. We produce the Excel file
        ExcelDashboarder().excelize(
            p_output_file_path=Path(os.path.join(os.path.dirname(__file__), 'TC07.excel.With_out_Totals.xlsx')),
            dict_config={
                "workbook.options": {"nan_inf_to_errors": True},
                "sheets": {
                    "test_sheet_name": {
                        "worksheet.freeze_panes": {"row": 1, "col":  1},
                        "worksheet.set_column": [
                            {
                                "first_col": 0,
                                "last_col": 1,
                                "width": 50
                            }
                        ],
                        "widgets": {
                            "test_a_widget_label": {
                                "address": "A1",
                                "widget_id": "https://enovation.com/excel_dashboard/table",
                                "config": {
                                    "options": {
                                        "columns": [
                                            {"header": "jsg numbers col1"},
                                            {"header": "jsg string col2"}
                                        ],
                                        "total_row": False,
                                        "name": "jsg_table_name"
                                    }
                                },
                                "parameters_map": {
                                    "df_data": "df_data"
                                }
                            }
                        }
                    }
                }
            },
            df_data=_df_data
        )

        # 1.2. We read the Excel spreadsheet, and assert the result is as expected
        _bean: excel_loader.ExcelLoaderBean = excel_loader.ExcelLoader().load_tables(
            str_path=os.path.join(os.path.dirname(__file__), 'TC07.excel.With_out_Totals.xlsx')
        )

        _df_read_data: DataFrame = _bean.dict_tables["jsg_table_name"]

        # Before doing anything, we expect 2 lines (as no total!)
        self.assertEqual(
            first=len(_df_data.index),
            second=len(_df_read_data.index),
            msg="Given there is no total row, we expect the same number of lines in the excel as in the dataframe."
        )

        # #############################################################################################################
        # 2. Without a total row!

        # 2.1. We produce the Excel file
        ExcelDashboarder().excelize(
            p_output_file_path=Path(os.path.join(os.path.dirname(__file__), 'TC07.excel.WithTotals.xlsx')),
            dict_config={
                "workbook.options": {"nan_inf_to_errors": True},
                "sheets": {
                    "test_sheet_name": {
                        "worksheet.freeze_panes": {"row": 1, "col":  1},
                        "worksheet.set_column": [
                            {
                                "first_col": 0,
                                "last_col": 1,
                                "width": 50
                            }
                        ],
                        "widgets": {
                            "test_a_widget_label": {
                                "address": "A1",
                                "widget_id": "https://enovation.com/excel_dashboard/table",
                                "config": {
                                    "options": {
                                        "columns": [
                                            {"header": "jsg numbers col1"},
                                            {"header": "jsg string col2"}
                                        ],
                                        "total_row": True,
                                        "name": "jsg_table_name"
                                    }
                                },
                                "parameters_map": {
                                    "df_data": "df_data"
                                }
                            }
                        }
                    }
                }
            },
            df_data=_df_data
        )

        # 2.2. We read the Excel spreadsheet, and assert the result is as expected
        _bean: excel_loader.ExcelLoaderBean = excel_loader.ExcelLoader().load_tables(
            str_path=os.path.join(os.path.dirname(__file__), 'TC07.excel.WithTotals.xlsx')
        )

        _df_read_data: DataFrame = _bean.dict_tables["jsg_table_name"]

        # Before doing anything, we expect 2 lines (as no total!)
        self.assertEqual(
            first=len(_df_data.index),
            second=len(_df_read_data.index)-1,
            msg="Given there is a total row, we expect one extra "
                "line in the excel spreadsheet compared to the dataframe"
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_08_conditional_format__manual_check(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _df_data: DataFrame = DataFrame(
            [
                [10, 'a'],
                [20, 'b']
            ],
            columns=['jsg numbers col1', 'jsg string col2']
        )

        # #############################################################################################################
        # 1. Without any total row!

        # 1.1. We produce the Excel file
        ExcelDashboarder().excelize(
            p_output_file_path=Path(os.path.join(os.path.dirname(__file__),
                                                 'TC08.excel.CondFormatWith_out_Totals.xlsx')),
            dict_config={
                "workbook.options": {"nan_inf_to_errors": True},
                "sheets": {
                    "test_sheet_name": {
                        "worksheet.freeze_panes": {"row": 1, "col":  1},
                        "worksheet.set_column": [
                            {
                                "first_col": 0,
                                "last_col": 1,
                                "width": 50
                            }
                        ],
                        "widgets": {
                            "test_a_widget_label": {
                                "address": "A1",
                                "widget_id": "https://enovation.com/excel_dashboard/table",
                                "config": {
                                    "options": {
                                        "columns": [
                                            {"header": "jsg numbers col1"},
                                            {"header": "jsg string col2"}
                                        ],
                                        "total_row": False,
                                        "name": "jsg_table_name"
                                    },
                                    "conditional_formattings": [
                                      {
                                        "range": "@A:@A",
                                        "options": {
                                            "type": "cell", "criteria": "equal to", "value": 20,
                                            "format": {"bg_color": "red"}
                                        }
                                      }
                                    ],
                                },
                                "parameters_map": {
                                    "df_data": "df_data"
                                }
                            }
                        }
                    }
                }
            },
            df_data=_df_data
        )

        # #############################################################################################################
        # 2. Without a total row!

        # 2.1. We produce the Excel file
        ExcelDashboarder().excelize(
            p_output_file_path=Path(os.path.join(os.path.dirname(__file__), 'TC08.excel.CondFormatWithTotals.xlsx')),
            dict_config={
                "workbook.options": {"nan_inf_to_errors": True},
                "sheets": {
                    "test_sheet_name": {
                        "worksheet.freeze_panes": {"row": 1, "col":  1},
                        "worksheet.set_column": [
                            {
                                "first_col": 0,
                                "last_col": 1,
                                "width": 50
                            }
                        ],
                        "widgets": {
                            "test_a_widget_label": {
                                "address": "A1",
                                "widget_id": "https://enovation.com/excel_dashboard/table",
                                "config": {
                                    "options": {
                                        "columns": [
                                            {"header": "jsg numbers col1"},
                                            {"header": "jsg string col2"}
                                        ],
                                        "total_row": True,
                                        "name": "jsg_table_name"
                                    },
                                    "conditional_formattings": [
                                      {
                                        "range": "@A:@A",
                                        "options": {
                                            "type": "cell", "criteria": "equal to", "value": 20,
                                            "format": {"bg_color": "red"}
                                        }
                                      }
                                    ],
                                },
                                "parameters_map": {
                                    "df_data": "df_data"
                                }
                            }
                        }
                    }
                }
            },
            df_data=_df_data
        )

        # MANUAL CHECK: conditional formatting should span across the whole table

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_09_nat_values(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_excel_dashboard: ExcelDashboarder = ExcelDashboarder()

        _df_data: DataFrame = DataFrame(
            [
                [10, '2023-03-25'],
                [20, None],
            ],
            columns=['jsg numbers col1', 'jsg string col2']
        )

        _df_data['jsg string col2'] = to_datetime(
            _df_data['jsg string col2']
        ).dt.normalize()

        _the_excel_dashboard.excelize(
            p_output_file_path=Path(os.path.join(os.path.dirname(__file__), 'TC09.excel.NatValues.xlsx')),
            dict_config={
                "workbook.options": {"nan_inf_to_errors": True},
                "sheets": {
                    "test_sheet_name": {
                        "widgets": {
                            "test_a_widget_label": {
                                "address": "A1",
                                "widget_id": "https://enovation.com/excel_dashboard/table",
                                "config": {
                                    "options": {
                                        "columns": [
                                            {"header": "jsg numbers col1"},
                                            {"header": "jsg string col2"}
                                        ]
                                    }
                                },
                                "parameters_map": {
                                    "df_data": "df_data"
                                }
                            }
                        }
                    }
                }
            },
            df_data=_df_data
        )
