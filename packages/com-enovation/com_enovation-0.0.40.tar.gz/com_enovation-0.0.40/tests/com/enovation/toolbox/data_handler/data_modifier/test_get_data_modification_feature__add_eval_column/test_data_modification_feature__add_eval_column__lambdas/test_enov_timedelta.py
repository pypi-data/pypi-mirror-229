import unittest
from datetime import datetime
from inspect import stack
from logging import Logger, getLogger
from pandas import Series, NaT
from pandas.testing import assert_series_equal

from com_enovation.toolbox.data_handler.data_modifier.data_modification_feature__add_eval_column__lambdas \
    import _enov_timedelta


class TestEnovTimedelta(unittest.TestCase):
    _logger: Logger = getLogger(__name__)

    def test_timedelta(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _s_date: Series = Series([
            datetime(2023, 4, 9),
            datetime(2023, 4, 10)
        ])

        _s_date_plus_10d: Series = _enov_timedelta(
            s_column=_s_date,
            f_delta_days=10
        )

        assert_series_equal(
            left=Series([
                datetime(2023, 4, 19),
                datetime(2023, 4, 20)
            ]),
            right=_s_date_plus_10d,
            obj="Test 1: when adding 10 days, not reconciling..."
        )

        _s_date_minus_10d: Series = _enov_timedelta(
            s_column=_s_date,
            f_delta_days=-10
        )

        assert_series_equal(
            left=Series([
                datetime(2023, 3, 30),
                datetime(2023, 3, 31)
            ]),
            right=_s_date_minus_10d,
            obj="Test 2: when removing 10 days, not reconciling..."
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_timedelta_with_missing_values(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _s_date: Series = Series([
            datetime(2023, 4, 9),
            None
        ])

        _s_date_plus_10d: Series = _enov_timedelta(
            s_column=_s_date,
            f_delta_days=10
        )

        assert_series_equal(
            left=Series([
                datetime(2023, 4, 19),
                NaT
            ]),
            right=_s_date_plus_10d,
            obj="Test 1: when adding 10 days, not reconciling..."
        )

        _s_date_minus_10d: Series = _enov_timedelta(
            s_column=_s_date,
            f_delta_days=-10
        )

        assert_series_equal(
            left=Series([
                datetime(2023, 3, 30),
                NaT
            ]),
            right=_s_date_minus_10d,
            obj="Test 2: when removing 10 days, not reconciling..."
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
