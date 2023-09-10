import logging
import os

import click
from click import Context


_logger: logging.Logger = logging.getLogger(__name__)


@click.command('dbg')
@click.pass_context
def debug(ctx_context: Context):
    """
    Command to run whenever you need to plug in a debugger on a given process. The command display the process id,
    so you can plug the debugger, and wait for you to confirm in the terminal to resume execution...
    """

    click.echo(f"Process ID: {os.getpid()}")

    click.confirm('Ready to continue?', abort=True, default=True)

