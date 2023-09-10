import logging
from inspect import stack

import click
from pandas import DataFrame, read_csv, read_excel

from com_enovation.helper.click.python_literal_argument_and_option import PythonLiteralOption

_logger: logging.Logger = logging.getLogger(__name__)


@click.command('df-load-csv')
@click.pass_context
@click.argument('file', type=click.Path(exists=True))
@click.argument('alias', type=str, default='csv')
@click.option('-c', '--columns', type=list, cls=PythonLiteralOption, default=[],
              help="Columns labels to load, others will be discarded.")
def df_load_csv(ctx_context, file, columns, alias):
    """
    Load listed columns from a csv file into a dataframe that is labelled using an alias for later use.

    :param alias: name given to the dataframe being loaded, so it can be used later on by other commands.
    :param columns: columns from the CSV file to be loaded. Other columns will be ignored.
    :param ctx_context: Click context.
    :param file: csv file to load
    """
    _logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

    if alias in ctx_context.obj:
        _logger.warning(
            f"Warning: another object with alias '{alias}' already exists, of type {type(alias)}. This data "
            f"will be overridden with the 'csv' file '{file}'."
        )

    # We load the csv
    df_the_measures: DataFrame = read_csv(file)
    _logger.info(f"CSV file read, shape '{df_the_measures.shape}'.")

    # We only keep the listed columns, if such "listed columns" were even provided as parameter
    if columns:

        # We check the listed columns are effectively in the data source
        lst_the_inexistant_columns: list = list(set(columns) - set(df_the_measures.columns))
        if len(lst_the_inexistant_columns) > 0:
            raise Exception(
                f"selected columns '{', '.join(lst_the_inexistant_columns)}' are not among existing ones "
                f"'{', '.join(df_the_measures.columns)}'."
            )

        # We filter out non listed columns
        df_the_measures = df_the_measures[list(columns)]
        _logger.info(f"Dataframe reduced, shape '{df_the_measures.shape}'.")

    # We update the context data store
    ctx_context.obj[alias] = df_the_measures
    ctx_context.obj["_" + alias] = {
        "path": file,
        "src": "load_csv"
    }

    _logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")


@click.command('df-load-xls')
@click.pass_context
@click.argument('file', type=click.Path(exists=True))
@click.argument('alias', type=str, default='xls')
@click.option('-c', '--columns', type=list, cls=PythonLiteralOption, default=[],
              help="Columns labels to load, others will be discarded.")
@click.option('-k', '--kwargs', type=dict, cls=PythonLiteralOption, default={},
              help="Parameters for the underlying function pandas.read_excel.")
def df_load_xls(ctx_context, file, columns, alias, kwargs):
    """
    Load an Excel spreadsheet from path FILE, and store it in context as ALIAS.

    In case COLUMNS is provided, only the listed columns are retrieved.

    In case KWARGS is provided, it is provided as parameters to the underlying function pandas.read_excel.
    Illustration: enov --verbose df-load-xls --kwargs "{'sheet_name': 'whatever'}" <PATH>
    """
    _logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called.")

    if alias in ctx_context.obj:
        _logger.warning(
            f"Warning: another object with alias '{alias}' already exists, of type {type(alias)}. This data "
            f"will be overridden with the 'xls-x' file '{file}'."
        )

    # We load the csv
    if len(kwargs) == 0:
        df_the_measures: DataFrame = read_excel(file)
    else:
        df_the_measures: DataFrame = read_excel(file, **kwargs)
    _logger.info(f"XLS-x file read, shape '{df_the_measures.shape}'.")

    # We only keep the listed columns, if such "listed columns" were even provided as parameter
    if columns:

        # We check the listed columns are effectively in the data source
        lst_the_inexistant_columns: list = list(set(columns) - set(df_the_measures.columns))
        if len(lst_the_inexistant_columns) > 0:
            raise Exception(
                f"selected columns '{', '.join(lst_the_inexistant_columns)}' are not among existing ones "
                f"'{', '.join(df_the_measures.columns)}'."
            )

        # We filter out non listed columns
        df_the_measures = df_the_measures[list(columns)]
        _logger.info(f"Dataframe reduced, shape '{df_the_measures.shape}'.")

    _logger.info(f"Stored as '{alias}' in context.")

    # We update the context data store
    ctx_context.obj[alias] = df_the_measures
    ctx_context.obj["_" + alias] = {
        "path": file,
        "src": "load_xls"
    }

    _logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
