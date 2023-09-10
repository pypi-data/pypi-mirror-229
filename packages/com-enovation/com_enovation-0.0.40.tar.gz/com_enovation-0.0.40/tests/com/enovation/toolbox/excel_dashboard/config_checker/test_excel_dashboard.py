from inspect import stack
from logging import getLogger, Logger
from unittest import TestCase

from jsonschema import ValidationError

from com_enovation.toolbox.excel_dashboard.config_checker import ConfigChecker


class TestCheckConfigExcelDashboard(TestCase):

    _logger: Logger = getLogger(__name__)

    _the_config_checker: ConfigChecker = ConfigChecker(
        lst_widgets_json_schemas=[
            {
                "$id": "https://enovation.com/excel_dashboard/cover_sheet",
                "type": "object",
                "required": [
                    "narrative"
                ],
                "additionalProperties": False,
                "properties": {
                    "narrative": {
                        "type": "string"
                    }
                }
            }
        ]
    )

    def test_01_successful(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self._the_config_checker.validate(
            dict_to_validate={
                "sheets": {
                    "test_sheet_name": {
                        "widgets": {
                            "test_a_widget_label": {
                                "address": "A1",
                                "widget_id": "https://enovation.com/excel_dashboard/cover_sheet",
                                "config": {
                                    "narrative": "the text to print for test"
                                },
                            }
                        }
                    }
                }
            },
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_02_unexpected_node(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        with self.assertRaisesRegex(
                ValidationError,
                f"is not valid under any of the given schemas"
        ):
            self._the_config_checker.validate(
                dict_to_validate={
                    "sheets": {
                        "test_sheet_namef": {
                            "widgets": {
                                "test_a_widget_label": {
                                    "address": "A1",
                                    "widget_id": "https://enovation.com/excel_dashboard/cover_sheet",
                                    "config": {
                                        "narrative": "the text to print for test",
                                        "test unexpected node": "jsg"
                                    },
                                }
                            }
                        }
                    }
                },
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_03_missing_node(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        with self.assertRaisesRegex(
                ValidationError,
                f"is not valid under any of the given schemas"
        ):
            self._the_config_checker.validate(
                dict_to_validate={
                    "sheets": {
                        "test_sheet_namef": {
                            "widgets": {
                                "test_a_widget_label": {
                                    "address": "A1",
                                    "widget_id": "https://enovation.com/excel_dashboard/cover_sheet",
                                    "config": {
                                        # "narrative": "the text to print for test",
                                    },
                                }
                            }
                        }
                    }
                },
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
