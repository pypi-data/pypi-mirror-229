import os
import unittest
from pathlib import Path
from logging import Logger, getLogger
from inspect import stack
from pandas import DataFrame, read_excel

from com_enovation.toolbox.data_handler.data_modifier.data_modification_feature_factory \
    import DataModificationFeatureFactory


class TestDataModificationFeatureFactory_AuditColumnChanged(unittest.TestCase):
    _logger: Logger = getLogger(__name__)

    def test_audit_column_changed(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We load the data extract
        df_data_extract: DataFrame = read_excel(
            Path(os.path.join(os.path.dirname(__file__),
                              '01.data_extract_for_audit_column.xlsx'))
        )

        # 1. We audit the column, grouping on one single column, first occurrence returns False
        df_data_extract = DataModificationFeatureFactory(). \
            get_data_modification_feature__audit_column__changed(
            s_column_to_audit="Jsg - Audited Column",
            s_column_audit="Jsg - Audited Column_audit",
            lst_key_columns=["Jsg - ID", "a column which does not exist"]
        )(df_data_extract)

        self.assertListEqual(
            list1=df_data_extract["Jsg - Audited Column_audit"].values.tolist(),
            list2=[
                False,
                False,
                True,
                False,
                False,
                True,
                False,
                True,
                False,
                False,
                True,
                False,
                False,
                True,
                True,

                True
            ],
            msg="1. We audit the column, grouping on one single column, first occurrence returns False"
        )

        # 2. We audit the column, grouping on one single column, first occurrence returns True
        df_data_extract = DataModificationFeatureFactory(). \
            get_data_modification_feature__audit_column__changed(
            s_column_to_audit="Jsg - Audited Column",
            s_column_audit="Jsg - Audited Column_audit",
            lst_key_columns=["Jsg - ID"],
            b_first_as_changed=True
        )(df_data_extract)

        self.assertListEqual(
            list1=df_data_extract["Jsg - Audited Column_audit"].values.tolist(),
            list2=[
                True,
                False,
                True,
                True,
                False,
                True,
                True,
                True,
                False,
                True,
                True,
                False,
                True,
                True,
                True,

                True
            ],
            msg="2. We audit the column, grouping on one single column, first occurrence returns True"
        )

        # 3. We audit the column, grouping on two columns, first occurrence returns False
        df_data_extract = DataModificationFeatureFactory(). \
            get_data_modification_feature__audit_column__changed(
            s_column_to_audit="Jsg - Audited Column",
            s_column_audit="Jsg - Audited Column_audit",
            lst_key_columns=["Jsg - ID", "Jsg - Snapshot"],
            b_first_as_changed=False
        )(df_data_extract)

        self.assertListEqual(
            list1=df_data_extract["Jsg - Audited Column_audit"].values.tolist(),
            list2=[
                False,
                False,
                True,
                False,
                False,
                False,
                False,
                True,
                False,
                False,
                False,
                False,
                False,
                True,
                True,

                True
            ],
            msg="3. We audit the column, grouping on two columns, first occurrence returns False"
        )

        # 4. We audit the column, grouping on two columns, first occurrence returns True
        df_data_extract = DataModificationFeatureFactory(). \
            get_data_modification_feature__audit_column__changed(
            s_column_to_audit="Jsg - Audited Column",
            s_column_audit="Jsg - Audited Column_audit",
            lst_key_columns=["Jsg - ID", "Jsg - Snapshot"],
            b_first_as_changed=True
        )(df_data_extract)

        self.assertListEqual(
            list1=df_data_extract["Jsg - Audited Column_audit"].values.tolist(),
            list2=[
                True,
                False,
                True,
                True,
                False,
                True,
                True,
                True,
                True,
                True,
                True,
                False,
                True,
                True,
                True,

                True
            ],
            msg="4. We audit the column, grouping on two columns, first occurrence returns True"
        )

        # 5. Exception if we audit a column which does not exist
        with self.assertRaisesRegex(
                Exception,
                f"The column to audit 'Jsg - not existing column' does not exist in the dataframe, which contains the "
                f"following columns: 'Jsg - ID, Jsg - Snapshot, Jsg - Audited Column'."
        ):
            DataModificationFeatureFactory(). \
                get_data_modification_feature__audit_column__changed(
                s_column_to_audit="Jsg - not existing column",
                s_column_audit="Jsg - Audited Column_audit",
                lst_key_columns=["Jsg - ID"]
            )(df_data_extract[["Jsg - ID", "Jsg - Snapshot", "Jsg - Audited Column"]])

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
