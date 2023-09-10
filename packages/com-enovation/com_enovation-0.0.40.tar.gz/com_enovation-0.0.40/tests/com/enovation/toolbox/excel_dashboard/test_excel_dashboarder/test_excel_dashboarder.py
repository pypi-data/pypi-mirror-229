import os
from inspect import stack
from logging import Logger, getLogger
from pathlib import Path
from unittest import TestCase

from com_enovation.toolbox.excel_dashboard.excel_dashboarder import ExcelDashboarder


class TestExcelDashboarder(TestCase):

    _logger: Logger = getLogger(__name__)

    def test_01(self):

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _the_excel_dashboard: ExcelDashboarder = ExcelDashboarder()

        _the_excel_dashboard.excelize(
            p_output_file_path=Path(os.path.join(os.path.dirname(__file__), 'TC01.excel.xlsx')),
            dict_config={
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
                                "widget_id": "https://enovation.com/excel_dashboard/cover_sheet",
                                "config": {
                                    "narrative": "the first text is '{0}' and the second is '{1}'."
                                },
                            }
                        }
                    }
                }
            },
            **{"tokens": ["ici c'est paris", "mais pourquoi donc?"]}
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returned")
