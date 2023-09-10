from inspect import stack
from unittest import TestCase
from logging import Logger, getLogger

from pandas import DataFrame

from com_enovation.helper.pandas_dataframe_typer import PandasDataframeTyper
from com_enovation.toolbox.backlog.bck_compare.bck_comparer import BacklogComparer


class TestFunctionCheckParameterDictColumns(TestCase):
    _logger: Logger = getLogger(__name__)

    def test_001(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        BacklogComparer()._check_parameter_dict_columns(
            df_src=DataFrame(
                {
                    "key1": ["k1-valA", "k1-valB"],
                    "col1": ["col1-valA", "col1-valB"]
                }
            ),
            df_tgt=DataFrame(
                {
                    "key1": ["k1-valA", "k1-valB"],
                    "col1": ["col1-valA", "col1-valB"]
                }
            ),
            dict_columns={
                BacklogComparer.str__dict_columns__json_tag__key_columns: {
                    "key1": {
                        BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                    }
                },
                BacklogComparer.str__dict_columns__json_tag__compared_columns: {
                    "col1": {
                        BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                    }
                }
            }
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_BR_101(self):
        """
        BR_101: parameter "key columns" should exist
        :return:
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        with self.assertRaisesRegex(
                KeyError,
                f"'key columns'"
        ):

            BacklogComparer()._check_parameter_dict_columns(
                df_src=DataFrame(
                    {
                        "key1": ["k1-valA", "k1-valB"],
                        "col1": ["col1-valA", "col1-valB"]
                    }
                ),
                df_tgt=DataFrame(
                    {
                        "key1": ["k1-valA", "k1-valB"],
                        "col1": ["col1-valA", "col1-valB"]
                    }
                ),
                dict_columns={
                    # BacklogComparer.str__dict_columns__json_tag__key_columns: {
                    #     "key1": {
                    #         BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                    #     }
                    # },
                    BacklogComparer.str__dict_columns__json_tag__compared_columns: {
                        "col1": {
                            BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                        }
                    }
                }
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_BR_102(self):
        """
        BR_102: parameter "key columns" should be a dictionary
        :return:
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        with self.assertRaisesRegex(
                AttributeError,
                f"'str' object has no attribute 'keys'"
        ):
            BacklogComparer()._check_parameter_dict_columns(
                df_src=DataFrame(
                    {
                        "key1": ["k1-valA", "k1-valB"],
                        "col1": ["col1-valA", "col1-valB"]
                    }
                ),
                df_tgt=DataFrame(
                    {
                        "key1": ["k1-valA", "k1-valB"],
                        "col1": ["col1-valA", "col1-valB"]
                    }
                ),
                dict_columns={
                    BacklogComparer.str__dict_columns__json_tag__key_columns: "key 1",
                    BacklogComparer.str__dict_columns__json_tag__compared_columns: {
                        "col1": {
                            BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                        }
                    }
                }
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_BR_103(self):
        """
        BR_103: parameter "key columns" should contain at least one property
        :return:
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        with self.assertRaisesRegex(
                Exception,
                f"^"
                f"{{}} does not have enough properties"
                f"[\\s,\\S]*"
                f"On instance\\['{BacklogComparer.str__dict_columns__json_tag__key_columns}'\\]"
                f"[\\S,\\s]*"
                f"$"
        ):
            BacklogComparer()._check_parameter_dict_columns(
                df_src=DataFrame(
                    {
                        "key1": ["k1-valA", "k1-valB"],
                        "col1": ["col1-valA", "col1-valB"]
                    }
                ),
                df_tgt=DataFrame(
                    {
                        "key1": ["k1-valA", "k1-valB"],
                        "col1": ["col1-valA", "col1-valB"]
                    }
                ),
                dict_columns={
                    BacklogComparer.str__dict_columns__json_tag__key_columns: {
                        # "key1": {
                        #     BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                        # }
                    },
                    BacklogComparer.str__dict_columns__json_tag__compared_columns: {
                        "col1": {
                            BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                        }
                    }
                }
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_BR_104(self):
        """
        BR_104: parameter "key columns" should only contains keys among columns intersecting in both dataframes
        :return:
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        with self.assertRaisesRegex(
                Exception,
                f"Additional properties are not allowed \\('key2' was unexpected\\)"
        ):
            BacklogComparer()._check_parameter_dict_columns(
                df_src=DataFrame(
                    {
                        "key1": ["k1-valA", "k1-valB"],
                        "col1": ["col1-valA", "col1-valB"]
                    }
                ),
                df_tgt=DataFrame(
                    {
                        "key1": ["k1-valA", "k1-valB"],
                        "key2": ["k1-valA", "k1-valB"],
                        "col1": ["col1-valA", "col1-valB"]
                    }
                ),
                dict_columns={
                    BacklogComparer.str__dict_columns__json_tag__key_columns: {
                        "key2": {
                            BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                        }
                    },
                    BacklogComparer.str__dict_columns__json_tag__compared_columns: {
                        "col1": {
                            BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                        }
                    }
                }
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_BR_105(self):
        """
        BR_105: parameter "key columns" should contains records containing "type" key only
        :return:
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        with self.assertRaisesRegex(
                Exception,
                f"Additional properties are not allowed \\('jsg' was unexpected\\)"
        ):
            BacklogComparer()._check_parameter_dict_columns(
                df_src=DataFrame(
                    {
                        "key1": ["k1-valA", "k1-valB"],
                        "col1": ["col1-valA", "col1-valB"]
                    }
                ),
                df_tgt=DataFrame(
                    {
                        "key1": ["k1-valA", "k1-valB"],
                        "col1": ["col1-valA", "col1-valB"]
                    }
                ),
                dict_columns={
                    BacklogComparer.str__dict_columns__json_tag__key_columns: {
                        "key1": {
                            BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                            "jsg": "unexpected",
                        }
                    },
                    BacklogComparer.str__dict_columns__json_tag__compared_columns: {
                        "col1": {
                            BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                        }
                    }
                }
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_BR_106(self):
        """
        BR_106: parameter "key columns" should contains records containing "type" key
        :return:
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        with self.assertRaisesRegex(
                Exception,
                f"'type' is a required property"
        ):
            BacklogComparer()._check_parameter_dict_columns(
                df_src=DataFrame(
                    {
                        "key1": ["k1-valA", "k1-valB"],
                        "col1": ["col1-valA", "col1-valB"]
                    }
                ),
                df_tgt=DataFrame(
                    {
                        "key1": ["k1-valA", "k1-valB"],
                        "col1": ["col1-valA", "col1-valB"]
                    }
                ),
                dict_columns={
                    BacklogComparer.str__dict_columns__json_tag__key_columns: {
                        "key1": {
                            # BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                        }
                    },
                    BacklogComparer.str__dict_columns__json_tag__compared_columns: {
                        "col1": {
                            BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                        }
                    }
                }
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def test_BR_107(self):
        """
        BR_107: parameter "key columns - type" should be a string
        :return:
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        with self.assertRaisesRegex(
                Exception,
                f"'dummy' is not one of \\['date', 'float', 'int', 'str'\\]"
        ):
            BacklogComparer()._check_parameter_dict_columns(
                df_src=DataFrame(
                    {
                        "key1": ["k1-valA", "k1-valB"],
                        "col1": ["col1-valA", "col1-valB"]
                    }
                ),
                df_tgt=DataFrame(
                    {
                        "key1": ["k1-valA", "k1-valB"],
                        "col1": ["col1-valA", "col1-valB"]
                    }
                ),
                dict_columns={
                    BacklogComparer.str__dict_columns__json_tag__key_columns: {
                        "key1": {
                            BacklogComparer.str__dict_columns__json_tag__type: "dummy",
                        }
                    },
                    BacklogComparer.str__dict_columns__json_tag__compared_columns: {
                        "col1": {
                            BacklogComparer.str__dict_columns__json_tag__type: PandasDataframeTyper.str__type__str,
                        }
                    }
                }
            )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
