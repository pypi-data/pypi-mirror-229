import os
import re
import unittest
from datetime import datetime
from inspect import stack
from logging import Logger, getLogger
from pathlib import Path

from numpy import nan
from pandas import Series, DataFrame, read_excel
from pandas.testing import assert_series_equal

from com_enovation.toolbox.data_handler.data_modifier.data_modification_feature_factory import \
    DataModificationFeatureFactory


class TestEnovAddEvalLambda(unittest.TestCase):
    _logger: Logger = getLogger(__name__)

    def test_add_eval_column__lambda(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the data extract
        df_data_extract: DataFrame = read_excel(
            Path(os.path.join(os.path.dirname(__file__), '01.data_extract.xlsx'))
        )

        df_the_modified_dataframe: DataFrame = DataModificationFeatureFactory(). \
            get_data_modification_feature__add_eval_columns(
            str_expressions=f"LastCommentAsTuple = @enov__lambda__process_comments__get_last_comment_as_tuple("
                            f"lst_s_people=[ProjectManager, Consultants], s_comments=Comments)\n"
                            f"LastCommentDate = @enov_get_record_at_index_from_tuple(LastCommentAsTuple, 0)\n"
                            f"LastCommentWriter = @enov_get_record_at_index_from_tuple(LastCommentAsTuple, 1)",
            lst_dependencies=[
                "tests.com.enovation.toolbox.data_handler.data_modifier."
                "test_get_data_modification_feature__add_eval_column."
                "test_data_modification_feature__add_eval_column__lambdas."
                "test_lambdas."
                "enov__lambda__process_comments__get_last_comment_as_tuple"],
            b_copy=True
        )(df_data_extract)

        assert_series_equal(
            left=df_data_extract["ExpectedResultDate"],
            right=df_the_modified_dataframe["LastCommentDate"],
            obj="Actual result DATE is not equal to expected result when calling lambda function process_comments",
            check_names=False
        )

        assert_series_equal(
            left=df_data_extract["ExpectedResultWriter"].replace(nan, None),
            right=df_the_modified_dataframe["LastCommentWriter"],
            obj="Actual result WRITER is not equal to expected result when calling lambda function process_comments",
            check_names=False
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")


def enov__lambda__process_comments__get_last_comment_as_tuple(
        s_comments: Series,
        lst_s_people: list[Series] = None,
        s_snapshot_date: Series = None
) -> Series:

    _s_people: None | Series = None
    _df_the_dataframe: None | DataFrame = None

    if lst_s_people is not None:

        if len(lst_s_people) > 0:
            _s_people: Series = lst_s_people[0].astype(str)

            if len(lst_s_people) > 1:
                for i_s_people in lst_s_people[1:]:
                    _s_people = _s_people+i_s_people.astype(str)

            _df_the_dataframe = DataFrame({
                "people": _s_people,
                "comments": s_comments
            })

    else:
        _df_the_dataframe = DataFrame({
            "comments": s_comments
        })

    if s_snapshot_date is not None:
        _df_the_dataframe = _df_the_dataframe.assign(snapshot_date=s_snapshot_date)

    def _get_last_comment_as_tuple(s_row: Series) -> tuple[datetime | None, str | None, str | None] | None:
        _the_return = None

        # We split the comments, comment by comment...
        _lst_comments_as_tuples: list[tuple[str, str]] = re.findall(
            string=s_row["comments"],
            pattern="^((?:(?:0[1-9])|(?:[1-2][0-9])|(?:3[0-1]))\\-"
                    "(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\-20\\d{2} "
                    "(?:\\d{2}\\:\\d{2}\\:\\d{2}) (?:AM|PM)) by ([^\\:]*) [\\:] (.*)",
            flags=re.MULTILINE
        )

        if len(_lst_comments_as_tuples) > 0:
            _dt_the_last_date: datetime | None = None
            _s_the_writer: str | None = None
            _s_the_msg: str | None = None

            for i_commment_as_tuple in _lst_comments_as_tuples:
                _dt_the_date: datetime = datetime.strptime(i_commment_as_tuple[0], "%d-%b-%Y %I:%M:%S %p")

                _b_in: bool = True

                if "snapshot_date" in s_row:
                    if _dt_the_date >= s_row["snapshot_date"]:
                        _b_in = False

                if "people" in s_row:
                    if i_commment_as_tuple[1] not in s_row["people"]:
                        _b_in = False

                if _b_in:

                    if _dt_the_last_date is None:
                        _dt_the_last_date = _dt_the_date
                        _s_the_writer = i_commment_as_tuple[1]
                        _s_the_msg = i_commment_as_tuple[2]

                    elif _dt_the_date > _dt_the_last_date:
                        _dt_the_last_date = _dt_the_date
                        _s_the_writer = i_commment_as_tuple[1]
                        _s_the_msg = i_commment_as_tuple[2]

            return _dt_the_last_date, _s_the_writer, _s_the_msg

        return None

    _df_the_dataframe["enov_last_comment"] = _df_the_dataframe.apply(
        func=_get_last_comment_as_tuple,
        axis=1,
    )

    return _df_the_dataframe["enov_last_comment"]
