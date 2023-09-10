import inspect
from unittest import TestCase
import logging
import os

from com_enovation.helper.excel_loader import ExcelLoader, ExcelLoaderBean


class TestXlsFileHelper(TestCase):

    _logger: logging.Logger = logging.getLogger(__name__)

    def test_function_read_xls_as_dataframe(self):
        """
        Test the function to read_xls_as_dataframe:
            - Test case 1: the xls file exists, and is correctly loaded
            - Test case 2: the xls file does not exist, and an error is thrown
            - Test case 3: the xls file exists, but is corrupted, and an error is thrown
        """
        self._logger.debug(f"Function '{inspect.stack()[0].filename} - {inspect.stack()[0].function}' "
                           f"is called.")

        the_loader: ExcelLoader = ExcelLoader()

        # Test case 1
        the_test_case_1_bean: ExcelLoaderBean = the_loader.load_tables(
            str_path=os.path.join(os.path.dirname(__file__), 'TC01.ExcelFileWithTables.xlsx')
        )

        self._logger.debug("Test case 1 executed")

        self._logger.debug(f"Function '{inspect.stack()[0].filename} - {inspect.stack()[0].function}' "
                           f"is returning.")
