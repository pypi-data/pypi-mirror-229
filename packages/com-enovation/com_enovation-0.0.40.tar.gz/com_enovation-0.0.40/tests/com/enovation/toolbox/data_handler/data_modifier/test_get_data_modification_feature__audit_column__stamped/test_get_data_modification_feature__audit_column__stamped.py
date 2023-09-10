import os
import unittest
from pathlib import Path
from logging import Logger, getLogger
from inspect import stack
from pandas import DataFrame, read_excel

from com_enovation.toolbox.data_handler.data_modifier.data_modification_feature_factory \
    import DataModificationFeatureFactory


class TestDataModificationFeatureFactory_AuditColumnStamped(unittest.TestCase):
    _logger: Logger = getLogger(__name__)

    def test_audit_column_stamped(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the data extract
        df_data_extract: DataFrame = read_excel(
            Path(os.path.join(os.path.dirname(__file__),
                              '01.data_extract_for_audit_column.xlsx'))
        )

        # 1. We audit the column, grouping on one single column
        df_data_extract = DataModificationFeatureFactory(). \
            get_data_modification_feature__audit_column__stamped(
            s_column_to_audit="Jsg - Audited Column",
            s_column_to_stamp="Jsg - Stamp Column",
            s_column_audit="Jsg - Audited Column_audit",
            lst_key_columns=["Jsg - ID", "a column which does not exist"]
        )(df_data_extract)

        self.assertListEqual(
            list1=df_data_extract["Jsg - Audited Column_audit"].values.tolist(),
            list2=[
                1,
                1,
                3,
                4,
                4,
                6,
                7,
                8,
                8,
                10,
                11,
                11,
                13,
                14,
                15,

                16
            ],
            msg="1. We audit the column, grouping on one single column"
        )

        # 2. We audit the column, grouping on two columns
        df_data_extract = DataModificationFeatureFactory(). \
            get_data_modification_feature__audit_column__stamped(
            s_column_to_audit="Jsg - Audited Column",
            s_column_to_stamp="Jsg - Stamp Column",
            s_column_audit="Jsg - Audited Column_audit",
            lst_key_columns=["Jsg - ID", "Jsg - Snapshot"]
        )(df_data_extract)

        self.assertListEqual(
            list1=df_data_extract["Jsg - Audited Column_audit"].values.tolist(),
            list2=[
                1,
                1,
                3,
                4,
                4,
                6,
                7,
                8,
                9,
                10,
                11,
                11,
                13,
                14,
                15,
                16,
            ],
            msg="2. We audit the column, grouping on two columns"
        )

        # 3. We audit a column, using this same column as the stamp (equivalent to add the last audited value)
        df_data_extract = DataModificationFeatureFactory(). \
            get_data_modification_feature__audit_column__stamped(
            s_column_to_audit="Jsg - Audited Column",
            s_column_to_stamp="Jsg - Audited Column",
            s_column_audit="Jsg - Audited Column_audit",
            lst_key_columns=["Jsg - ID"]
        )(df_data_extract)

        self.assertListEqual(
            list1=df_data_extract["Jsg - Audited Column_audit"].values.tolist(),
            list2=[
                "A",
                "A",
                "B",
                "B",
                "B",
                "C",
                "A",
                "B",
                "B",
                "B",
                "C",
                "C",
                "A",
                "C",
                "B",
                "A"
            ],
            msg="We audit a column, using this same column as the stamp (equivalent to add the last audited value)"
        )

        # 5. Exception if we audit a column which does not exist
        with self.assertRaisesRegex(
                Exception,
                f"The column to audit 'Jsg - not existing column' does not exist in the dataframe, which contains the "
                f"following columns: 'Jsg - ID, Jsg - Snapshot, Jsg - Audited Column, Jsg - Stamp Column'."
        ):
            DataModificationFeatureFactory(). \
                get_data_modification_feature__audit_column__stamped(
                s_column_to_audit="Jsg - not existing column",
                s_column_to_stamp="Jsg - Stamp Column",
                s_column_audit="Jsg - Audited Column_audit",
                lst_key_columns=["Jsg - ID"]
            )(df_data_extract[["Jsg - ID", "Jsg - Snapshot", "Jsg - Audited Column", "Jsg - Stamp Column"]])

        # 6. Exception if we rely on a stamp column which does not exist
        with self.assertRaisesRegex(
                Exception,
                f"The column to stamp 'Jsg - not existing column' does not exist in the dataframe, which contains the "
                f"following columns: 'Jsg - ID, Jsg - Snapshot, Jsg - Audited Column, Jsg - Stamp Column'."
        ):
            DataModificationFeatureFactory(). \
                get_data_modification_feature__audit_column__stamped(
                s_column_to_audit="Jsg - Audited Column",
                s_column_to_stamp="Jsg - not existing column",
                s_column_audit="Jsg - Audited Column_audit",
                lst_key_columns=["Jsg - ID", "a column which does not exist"]
            )(df_data_extract[["Jsg - ID", "Jsg - Snapshot", "Jsg - Audited Column", "Jsg - Stamp Column"]])

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
