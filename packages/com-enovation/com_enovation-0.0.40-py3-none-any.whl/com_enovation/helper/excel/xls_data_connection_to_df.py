import datetime
from inspect import stack
from logging import Logger, getLogger
from pathlib import Path
from types import NoneType

import pywintypes
import win32com.client
from pandas import DataFrame


class ExcelTables:
    _dict_tables: dict[str, DataFrame]

    def __init__(
            self,
            dict_tables: dict[str, DataFrame],
    ):
        self._dict_tables = dict_tables

    @property
    def dict_tables(self) -> dict[str, DataFrame]:
        return self._dict_tables


class XlsDataConnectionToDf:
    """
    Class that interacts with Excel to perform actions such as:
    - Load an Excel file, refresh all data connections, persist and export data into a dataframe
    - TODO.
    """

    # Class Properties
    _lst_authorized_extensions: list[str] = [".xls", ".xlsm", ".xlsx"]
    _logger: Logger = getLogger(__name__)

    def refresh_and_return_xls_connections(
            self,
            p_path: Path,
            b_persist: bool = True,
    ) -> ExcelTables:
        """
        Function that executes the following steps:
        - Open an Excel Spreadsheet from its path
        - Refresh all data connections
        - Persist the file
        - Export all the Tables, or the ones from the paramater l_tables, and return them as DataFrames.

        Note: when crashing, a zombie process might survive:
        - ps | grep EXCEL --> return the process id
        - kill <process id>

        Idea for later:
        - Could add logic to only refresh one table
        - https://stackoverflow.com/questions/34296591/how-do-i-make-an-excel-refreshall-wait-to-close-until-finished
            for sheet in workbook.Sheets:
                print(sheet.name)
                    for table in sheet.QueryTables:
                        print("Found a query table on %s called %s" % (sheet.name, table.name))

                        # i.e.: disable background query, and therefore cause Excel to 'wait' until it's done refreshing
                        table.BackgroundQuery = False

                        # This both refreshes the table, AND if the Refresh() method returns True
                        # (i.e.: refreshes successfully), tells you so.
                        if table.Refresh() == True:
                            print("Query table %s refreshed!" % table.name)
                        else:
                            print("Query table %s FAILED to refresh." % table.name)

        :param p_path: path to the Excel file that contains the connections/ queries to refresh and export
        :param b_persist: persist the Excel file once all connections were refreshed. True by default.
        :return: an instance of ExcelTables
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        # We check the parameter p_path
        if p_path.is_file() is False:
            raise Exception(f"Path '{p_path}' does not lead to an existing file.")
        if p_path.suffix not in self._lst_authorized_extensions:
            raise Exception(f"Path '{p_path}' does not appear to have an extension among the ones authorized: "
                            f"{', '.join(self._lst_authorized_extensions)}")

        # Start an instance of Excel
        # - Using Dispatch: if an Excel instance was running, the Quit action will close all the worksheets
        # - Using DispatchEx: we have an isolated instance of Excel, that we can even hide...
        # noinspection is required as "client" is not recognize as a member of win32com
        try:
            # noinspection PyUnresolvedReferences
            o_xlapp = win32com.client.DispatchEx("Excel.Application")
            self._logger.info(f"Excel application is launched")
        except Exception as an_exception:
            raise Exception(f"Calling win32com.client.DispatchEx('Excel.Application') raised an exception")\
                from an_exception

        # Open the workbook in said instance of Excel
        try:
            o_wb = o_xlapp.workbooks.open(str(p_path))
            self._logger.info(f"Excel file '{p_path}' is opened.")
        except Exception as an_exception:
            try:
                o_xlapp.Quit()
            except Exception as sub_exception:
                self._logger.error(f"Tried to quit Excel, but faced an exception.", sub_exception)

            raise Exception(f"Calling o_xlapp.workbooks.open(p_path='{p_path}') raised an exception")\
                from an_exception

        # Optional, e.g. if you want to debug
        # o_xlapp.Visible = True

        # Refresh all data connections.
        try:
            o_wb.RefreshAll()
            self._logger.info(f"All data connections/ queries are being refreshed.")
        except Exception as an_exception:
            try:
                o_wb.Close(SaveChanges=False)
                o_xlapp.Quit()
            except Exception as sub_exception:
                self._logger.error(f"Tried to close and quit Excel, but faced an exception.", sub_exception)

            raise Exception(f"Calling o_wb.RefreshAll() raised an exception")\
                from an_exception

        # Wait for refresh to be done
        try:
            o_xlapp.CalculateUntilAsyncQueriesDone()
            self._logger.info(f"All data connections/ queries are now refreshed.")
        except Exception as an_exception:
            try:
                o_wb.Close(SaveChanges=False)
                o_xlapp.Quit()
            except Exception as sub_exception:
                self._logger.error(f"Tried to close and quit Excel, but faced an exception.", sub_exception)

            raise Exception(f"Calling o_xlapp.CalculateUntilAsyncQueriesDone() raised an exception")\
                from an_exception

        # We get all objects across all sheets into an instance of ExcelTables
        try:
            o_the_return: ExcelTables = self._workbook_to_bean(o_wb)
            self._logger.info(f"Workbook data retrieved into bean.")
        except Exception as an_exception:
            try:
                o_wb.Close(SaveChanges=False)
                o_xlapp.Quit()
            except Exception as sub_exception:
                self._logger.error(f"Tried to close and quit Excel, but faced an exception.", sub_exception)

            raise Exception(f"Calling _workbook_to_bean(o_wb) raised an exception")\
                from an_exception

        # We persist the file
        if b_persist:
            try:
                o_wb.Save()
                self._logger.info(f"Excel file '{p_path}' is saved.")
            except Exception as an_exception:
                try:
                    o_wb.Close(SaveChanges=False)
                    o_xlapp.Quit()
                except Exception as sub_exception:
                    self._logger.error(f"Tried to close and quit Excel, but faced an exception.", sub_exception)

                raise Exception(f"Calling o_wb.Save() raised an exception")\
                    from an_exception

        # We close the workbook
        try:
            o_wb.Close(SaveChanges=False)
        except Exception as an_exception:
            try:
                o_xlapp.Quit()
            except Exception as sub_exception:
                self._logger.error(f"Tried to close Excel, but faced an exception.", sub_exception)

            raise Exception(f"Calling o_wb.Close(SaveChanges=False) raised an exception")\
                from an_exception

        o_xlapp.Quit()
        del o_xlapp

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")

        return o_the_return

    def _workbook_to_bean(self, o_wb) -> ExcelTables:
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")
        _dict_tables: dict[str, DataFrame] = {}

        # We process each and every worksheet
        for i_worksheet in o_wb.Worksheets:

            # We process each and every table
            for i_object in i_worksheet.ListObjects:

                _tpl_the_extracted_values: tuple = i_object.Range.Value

                _df_the_data: DataFrame = self._range_values_to_dataframe(
                    tpl_of_tpl_data_incl_headers=_tpl_the_extracted_values,
                    b_has_headers=True
                )

                _dict_tables[i_object.Name] = _df_the_data

        _o_the_return: ExcelTables = ExcelTables(_dict_tables)

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")

        return _o_the_return

    def _range_values_to_dataframe(
            self,
            tpl_of_tpl_data_incl_headers: tuple,
            b_has_headers: bool = True
    ) -> DataFrame:
        """
        To generate a DataFrame, we need:
        - To transform the tuple of tuples into lists
        - To transcode pywin.types into native types...
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        # We transform the data from tuples of tuples into list of list
        _lst_of_lst_data: list = [
            [
                self._transcode_pywintypes(i_cell)
                for i_cell in i_row
            ]
            for i_row in tpl_of_tpl_data_incl_headers
        ]

        if b_has_headers:
            _df_the_return: DataFrame = DataFrame(
                data=_lst_of_lst_data[1:],
                columns=_lst_of_lst_data[0]
            )
        else:
            _df_the_return: DataFrame = DataFrame(
                data=_lst_of_lst_data
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")

        return _df_the_return

    def _transcode_pywintypes(
            self,
            cell_value
    ):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        if isinstance(cell_value, pywintypes.TimeType):

            # It might happen that float values are considered as datetime...
            # As example, cell_value.timestamp() for '7' would return a negative number, that would crash
            if cell_value.timestamp() <= 0:
                self._logger.error(
                    f"One cell value is wrongly retrieved as a date, but function timestamp() returns a negative "
                    f"value. This could come from a numeric value in the source, refreshed as a date in the query. "
                    f"Check the query that refreshes data, and search for wrong cast into datetime...")
                _the_return: None = None

            else:
                # noinspection PyArgumentList
                _the_return: datetime.datetime = datetime.datetime.fromtimestamp(
                    timestamp=cell_value.timestamp(),
                    # tz=cell_value.tzinfo
                )

                # _the_return = cell_value.tzinfo.fromutc(_the_return)

        elif isinstance(cell_value, str):
            _the_return: str = cell_value

        elif isinstance(cell_value, NoneType):
            _the_return: NoneType = cell_value

        elif isinstance(cell_value, float):
            _the_return: float = cell_value

        else:
            raise Exception(f"Unexpected type {type(cell_value)}")

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning.")

        return _the_return
