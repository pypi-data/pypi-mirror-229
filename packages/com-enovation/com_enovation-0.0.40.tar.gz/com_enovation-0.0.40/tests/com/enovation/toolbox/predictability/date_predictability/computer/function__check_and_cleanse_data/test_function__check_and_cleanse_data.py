from unittest import TestCase
from pandas import DataFrame
from inspect import stack
from logging import Logger, getLogger
from datetime import datetime

from pandas.testing import assert_frame_equal

from com_enovation.toolbox.predictability.dp_date_predictability.dp_computer import DatePredictabilityComputer


class TestFunctionCheckAndCleanseData(TestCase):

    _logger: Logger = getLogger(__name__)

    def test_BR_Data(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        the_df_client_measures: DataFrame = DataFrame(columns=["key", "a date column", "measure"], data=[
            ['a', datetime(2020, 5, 10), datetime(2020, 5, 18)],
            ['a', datetime(2020, 5, 19), datetime(2020, 5, 19)],
        ])
        DatePredictabilityComputer()._check_and_cleanse_data(
            df_measures=the_df_client_measures,
            str_column_label_date="a date column",
        )

        self.assertEqual(
            first=2,
            second=len(
                DatePredictabilityComputer()._check_and_cleanse_data(
                    df_measures=the_df_client_measures,
                    str_column_label_date="a date column",
                ).index
            ),
            msg="Unexpected number of lines in returned DataFrame."
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_LOG_Data_002_Remove_duplicates(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # 1. Duplicate from first record --> one line deleted
        the_df_client_measures: DataFrame = DataFrame(columns=["key", "date", "measure"], data=[
            ['a', datetime(2020, 5, 10), datetime(2020, 5, 18)],
            ['a', datetime(2020, 5, 17), datetime(2020, 5, 18)],
            ['a', datetime(2020, 5, 19), datetime(2020, 5, 19)],
        ])
        assert_frame_equal(
            left=DataFrame(columns=["key", "date", "measure"], data=[
                ['a', datetime(2020, 5, 10), datetime(2020, 5, 18)],
                ['a', datetime(2020, 5, 19), datetime(2020, 5, 19)],
            ]),
            right=DatePredictabilityComputer()._check_and_cleanse_data(
                df_measures=the_df_client_measures
            ).reset_index(drop=True),
            obj=f"UC 1, did not delete properly duplicates",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        # 2. Duplicate from last record --> no line deleted
        the_df_client_measures: DataFrame = DataFrame(columns=["key", "date", "measure"], data=[
            ['a', datetime(2020, 5, 10), datetime(2020, 5, 18)],
            ['a', datetime(2020, 5, 17), datetime(2020, 5, 19)],
            ['a', datetime(2020, 5, 19), datetime(2020, 5, 19)],
        ])
        assert_frame_equal(
            left=the_df_client_measures,
            right=DatePredictabilityComputer()._check_and_cleanse_data(
                df_measures=the_df_client_measures
            ).reset_index(drop=True),
            obj=f"UC 2, did not delete properly duplicates",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        # 3. Duplicate in the middle --> several lines deleted
        the_df_client_measures: DataFrame = DataFrame(columns=["key", "date", "measure"], data=[
            ['a', datetime(2020, 5, 10), datetime(2020, 5, 18)],
            ['a', datetime(2020, 5, 11), datetime(2020, 5, 18)],
            ['a', datetime(2020, 5, 12), datetime(2020, 5, 18)],
            ['a', datetime(2020, 5, 13), datetime(2020, 5, 19)],
            ['a', datetime(2020, 5, 14), datetime(2020, 5, 19)],
            ['a', datetime(2020, 5, 15), datetime(2020, 5, 19)],
            ['a', datetime(2020, 5, 16), datetime(2020, 5, 20)],
            ['a', datetime(2020, 5, 17), datetime(2020, 5, 20)],
            ['a', datetime(2020, 5, 18), datetime(2020, 5, 19)],
            ['a', datetime(2020, 5, 19), datetime(2020, 5, 19)],
        ])
        assert_frame_equal(
            left=DataFrame(columns=["key", "date", "measure"], data=[
                ['a', datetime(2020, 5, 10), datetime(2020, 5, 18)],
                ['a', datetime(2020, 5, 13), datetime(2020, 5, 19)],
                ['a', datetime(2020, 5, 16), datetime(2020, 5, 20)],
                ['a', datetime(2020, 5, 18), datetime(2020, 5, 19)],
                ['a', datetime(2020, 5, 19), datetime(2020, 5, 19)],
            ]),
            right=DatePredictabilityComputer()._check_and_cleanse_data(
                df_measures=the_df_client_measures
            ).reset_index(drop=True),
            obj=f"UC 2, did not delete properly duplicates",
            atol=0.00001,
            check_like=True  # To exclude index, and not to care about column ordering
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_BR_Data_001_at_least_one_record(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # 1. Exception raised with no record
        the_df_client_measures: DataFrame = DataFrame(columns=["a key", "a date column", "measure"], data=[])
        with self.assertRaisesRegex(
                Exception,
                f"BR_Data_001 - The parameter df_measures contains '0' records, while it should contain at least '1'."
        ):
            DatePredictabilityComputer()._check_and_cleanse_data(
                df_measures=the_df_client_measures,
                str_column_label_key="a key",
                str_column_label_date="a date column"
            )

        # 2. No exception raised with one record
        the_df_client_measures: DataFrame = DataFrame(columns=["key", "a date column", "measure"], data=[
            ["a", datetime(2020, 5, 17), datetime(2020, 5, 18)],
        ])
        DatePredictabilityComputer()._check_and_cleanse_data(
            df_measures=the_df_client_measures,
            str_column_label_date="a date column",
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_BR_Data_002_no_null_value(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        the_df_client_measures: DataFrame = DataFrame(columns=["date", "measure"], data=[
            [datetime(2020, 5, 17), datetime(2020, 5, 18)],
            [datetime(2020, 5, 18), None],
        ])

        with self.assertRaisesRegex(
                Exception,
                f"BR_Data_002 - The parameter df_measures contains '1' null values, which is not expected. Make sure "
                f"you call the function with a dataframe df_measures which does not contain any null value."
        ):
            DatePredictabilityComputer()._check_and_cleanse_data(
                df_measures=the_df_client_measures,
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_BR_Data_003_dates(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # 1. No exception when string can be formatted as date
        the_df_client_measures: DataFrame = DataFrame(columns=["key", "date", "measure"], data=[
            ['a', "2020-5-17", datetime(2020, 5, 18)],
            ['a', "2020-5-18", datetime(2020, 5, 18)],
        ])
        DatePredictabilityComputer()._check_and_cleanse_data(
            df_measures=the_df_client_measures,
        )

        # 2. Exception when string cannot be formatted as date
        the_df_client_measures: DataFrame = DataFrame(columns=["key", "date", "measure"], data=[
            ['a', "2020-5-aa", datetime(2020, 5, 18)],
            ['a', "2020-5-18", datetime(2020, 5, 18)],
        ])
        self._logger.warning(f"The following warning is to be expected! UserWarning: Could not infer format, so each "
                           f"element will be parsed individually, falling back to `dateutil`. To ensure parsing is "
                           f"consistent and as-expected, please specify a format\n"
                           f"... START")
        with self.assertRaisesRegex(
                Exception,
                f"BR_Data_003 - An exception occurred while typing columns 'date' and 'measure' to dates. Check the "
                f"data, and retry."
        ):
            DatePredictabilityComputer()._check_and_cleanse_data(
                df_measures=the_df_client_measures,
            )
        self._logger.warning(f"... END")

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_BR_Data_004_duplicated_date(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # 1. duplicated date without key column
        the_df_client_measures: DataFrame = DataFrame(columns=["date", "measure"], data=[
            ["2020-05-18", datetime(2020, 5, 18)],
            ["2020-05-18", datetime(2020, 5, 18)],
        ])
        with self.assertRaisesRegex(
                Exception,
                f"BR_Data_004 - The parameter df_measures contains '1' records duplicated, which is not expected. Make "
                f"sure your remove all duplicates for values"
        ):
            DatePredictabilityComputer()._check_and_cleanse_data(
                df_measures=the_df_client_measures,
            )

        # 2. duplicated date with one key column
        the_df_client_measures: DataFrame = DataFrame(columns=["key", "date", "measure"], data=[
            ["a key", "2020-05-18", datetime(2020, 5, 18)],
            ["a key", "2020-05-18", datetime(2020, 5, 18)],
        ])
        with self.assertRaisesRegex(
                Exception,
                f"BR_Data_004 - The parameter df_measures contains '1' records duplicated, which is not expected. Make "
                f"sure your remove all duplicates for values"
        ):
            DatePredictabilityComputer()._check_and_cleanse_data(
                df_measures=the_df_client_measures,
            )

        # 3. duplicated date with one several key columns
        the_df_client_measures: DataFrame = DataFrame(columns=["key 1", "key 2", "date", "measure"], data=[
            ["a", "b", "2020-05-17", datetime(2020, 5, 18)],
            ["a", "b", "2020-05-18", datetime(2020, 5, 18)],
            ["a", "c", "2020-05-18", datetime(2020, 5, 18)],
            ["a", "c", "2020-05-18", datetime(2020, 5, 18)],
        ])
        with self.assertRaisesRegex(
                Exception,
                f"BR_Data_004 - The parameter df_measures contains '1' records duplicated, which is not expected. Make "
                f"sure your remove all duplicates for values"
        ):
            DatePredictabilityComputer()._check_and_cleanse_data(
                df_measures=the_df_client_measures,
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
