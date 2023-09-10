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
            p_output_file_path=Path(os.path.join(os.path.dirname(__file__), 'TC01.excel.xlsm')),
            dict_config={
                "vba": {
                    "workbook.add_vba_project": os.path.join(os.path.dirname(__file__), 'vbaProject.bin'),
                    # "workbook.set_vba_name": "jsg_wb",
                    # "worksheet.set_vba_name": {
                    #     "jsg_sheet_1": "Sheet1",
                    #     "jsg_sheet_2": "Sheet2"
                    # }
                },
                "sheets": {
                    "jsg_sheet_1": {
                        "widgets": {
                            "test_first_label": {
                                "address": "B2",
                                "widget_id": "https://enovation.com/excel_dashboard/cover_sheet",
                                "config": {
                                    "narrative": "the first text is '{0}' and the second is '{1}'."
                                },
                            }
                        }
                    },
                    "jsg_sheet_2": {
                        "widgets": {
                            "test_second_label": {
                                "address": "C3",
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
