import shutil
from inspect import stack
from logging import Logger, getLogger
from pathlib import Path
import win32com.client


class XlsRefreshDataConnections:
    """
    Class that interacts with Excel to refresh data connections/ queries.
    """

    # Class Properties
    _lst_authorized_extensions: list[str] = [".xls", ".xlsm", ".xlsx"]
    _logger: Logger = getLogger(__name__)

    def refresh_data_connections(
            self,
            p_file: Path,
            p_save_as: Path = None,
            b_visible: bool = False
    ):
        """
        Function that executes the following steps:
        - Open an Excel Spreadsheet from its path
        - Refresh all data connections
        - Persist the file, or save as another file
        - Let Excel open in case b_visible is set to True (otherwise, Excel instance is not visible)

        Note: when crashing, a zombie process might survive:
        - ps | grep EXCEL --> return the process id
        - kill <process id>
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

        # We check the parameter p_file
        if p_file.is_file() is False:
            raise Exception(f"Path p_file:'{p_file}' does not lead to an existing file.")
        if p_file.suffix not in self._lst_authorized_extensions:
            raise Exception(f"Path p_file:'{p_file}' does not appear to have an extension among the ones authorized: "
                            f"{', '.join(self._lst_authorized_extensions)}")

        if p_save_as is None:
            _p_the_path: Path = p_file

        else:
            # We check the parameter p_save_as
            if p_save_as.is_file() is True:
                raise Exception(f"Path p_save_as:'{p_save_as}' does lead to an existing file.")
            if p_file.suffix not in self._lst_authorized_extensions:
                raise Exception(f"Path p_save_as:'{p_save_as}' does not appear to have an extension among the ones "
                                f"authorized: {', '.join(self._lst_authorized_extensions)}")

            # We need to copy the file that will be refreshed, as it will be persisted!
            shutil.copyfile(
                src=p_file,
                dst=p_save_as
            )
            _p_the_path: Path = p_save_as

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
            o_wb = o_xlapp.workbooks.open(str(_p_the_path))
            self._logger.info(f"Excel file '{_p_the_path}' is opened.")
        except Exception as an_exception:
            try:
                o_xlapp.Quit()
            except Exception as sub_exception:
                self._logger.error(f"Tried to quit Excel, but faced an exception.", sub_exception)

            raise Exception(f"Calling o_xlapp.workbooks.open(_p_the_path='{_p_the_path}') raised an exception")\
                from an_exception

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

        if b_visible:
            o_xlapp.Visible = True

        else:

            # We save
            try:
                o_wb.Save()
                self._logger.info(f"Excel file '{_p_the_path}' is saved.")
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
