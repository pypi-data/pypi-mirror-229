import logging
from pathlib import Path

import click
from click import Context

from com_enovation.helper.excel.xls_data_connection_to_df import XlsDataConnectionToDf, ExcelTables

_logger: logging.Logger = logging.getLogger(__name__)


@click.command('xls-connection-to-df')
@click.argument('file', type=click.Path(exists=True))
@click.argument('alias', type=str, default='xls')
@click.option('--persist/--no-persist', default=True, help='To persist the refresh excel file.')
@click.pass_context
def xls_connection_to_df(
        ctx_context: Context,
        file: Path,
        alias: str,
        persist: bool
):
    """
    Command to open an Excel file from PATH, refresh all queries and connections, before persisting the file (if
    PERSIST is left to true) and returning all the tables in an ExcelTables bean. This bean is persisted in context as
    ALIAS (defaulted to 'xls').

    Note: when crashing, a zombie process might survive:
    - ps | grep EXCEL
    - kill xxx
    """

    if alias in ctx_context.obj:
        _logger.warning(
            f"Warning: another object with alias '{alias}' already exists, of type {type(alias)}. This data "
            f"will be overridden."
        )

    obj_bean: ExcelTables = XlsDataConnectionToDf().refresh_and_return_xls_connections(
        p_path=Path(file),
        b_persist=persist
    )

    # We update the context data store
    ctx_context.obj[alias] = obj_bean
    ctx_context.obj["_" + alias] = {
        "path": file,
        "src": "xls-connections-to-df"
    }
