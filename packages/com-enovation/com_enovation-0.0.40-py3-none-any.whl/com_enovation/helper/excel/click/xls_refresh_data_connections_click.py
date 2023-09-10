import logging
from pathlib import Path

import click

from com_enovation.helper.excel.xls_refresh_data_connections import XlsRefreshDataConnections

_logger: logging.Logger = logging.getLogger(__name__)


@click.command('xls-refresh')
@click.argument('file', type=click.Path(exists=True))
@click.option('--save_as', default=None, type=click.Path(), help='To persist the refresh excel file as.')
def xls_refresh_data_connections(
        file: Path,
        save_as: Path
):
    """
    Command to open an Excel FILE, refresh all queries and connections, before persisting the file or SAVE-AS another
    path.

    Note: when crashing, a zombie process might survive:
    - ps | grep EXCEL
    - kill xxx
    """

    XlsRefreshDataConnections().refresh_data_connections(
        p_file=Path(file),
        p_save_as=Path(save_as)
    )
