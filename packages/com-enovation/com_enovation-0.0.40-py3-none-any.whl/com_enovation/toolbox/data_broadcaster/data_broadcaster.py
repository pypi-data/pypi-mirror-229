import json
import os
from copy import deepcopy
from inspect import stack
from logging import Logger, getLogger

from com_enovation.toolbox.data_handler.data_handler import DataHandler


class DataBroadcaster:
    """
    A class to distribute:
    - For a list of recipients
      - Filter the data
      - Produce relevant dashboards
      - Persist into file system.

    Data to broadcast are provided into dataframe(s), at least one, and are to be prepared ahead of calling the
    broadcaster.

    Configuration is of the kind:
    {
        "dashboards configurations": {
            "a label for a dashboard": {
                "description": "a description for the excel dashboard, facultative",
                "path": "path to the excel dashboard configuration file"
            },
            (...)
        },
        "distributions configurations": {

            "a label for a distribution": {

                "description": "a description for the distribution, facultative",
                "dashboard configuration": "a label for a dashboard configuration",

                "data handlers": {

                    "a label for a data set to handle": {
                        # Note: this label should be among the function parameters when calling "distribute"

                        "description": "a description of the logic across the below steps",

                        "steps": [
                            {
                                "description": "a description of the step",
                                "feature": "a label of a data handler feature",
                                "param": {
                                    (...),
                                    "b_copy": true | false
                                }
                            }
                        ]
                    }
                }
            }
        }
    }
    """

    # Instance properties (decorated with @property)

    # Constants
    # -- To configure the dashboards configurations
    _const_str__config_tag__dashboards_cfgs__as_dict: str = "dashboards configurations"
    _const_str__config_tag__dashboard_cfg__path__as_path: str = "path"
    _const_str__config_tag__dashboard_cfg__description__as_str: str = "description"
    #     ... The below node is added during the initialization, and contains the dashboard configuration that is read
    #         from the files @path
    _const_str__config_tag__dashboard_cfg__configuration__as_dict: str = "configuration"

    # -- To configure the distributions aliases
    _const_str__config_tag__distributions_cfgs__as_dict: str = "distributions configurations"
    _const_str__config_tag__distribution_cfg__description__as_str: str = "description"
    _const_str__config_tag__distribution_cfg__dashboard_cfg__as_str: str = "description"
    _const_str__config_tag__distribution_cfg__data_sets_handlers_cfgs__as_dict: str = "data sets handlers"

    # Class properties
    _logger: Logger = getLogger(__name__)

    def __init__(
            self,
            dict_config: dict,
    ):
        """

        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self._dict_dashboards_configurations: dict = self._load_dashboards_configurations(
            dict_dashboards_configurations=dict_config.get(self._const_str__config_tag__dashboards_cfgs__as_dict, None)
        )

        self._data_handlers: dict[str, DataHandler] = self._instantiate_data_handlers(
            dict_distributions_configurations=dict_config.get(self._const_str__config_tag__distributions_cfgs__as_dict)
        )

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returned")

    def _load_dashboards_configurations(
            self,
            dict_dashboards_configurations: dict
    ) -> dict:
        """
        Process the node "dashboards configurations", that is a node at the root of the DataBroadcaster configuration
        file.

        This node is composed of the kind:
        {
            "dashboards configurations": {
                "a label for a dashboard": {
                    "description": "a description for the excel dashboard, facultative",
                    "path": "path to the excel dashboard configuration file"
                },
                (...)
            },
            "distributions configurations": {...}
        }

        Business rules:
        - BR-01: the node "dashboards configurations" is mandatory
        - BR-02: there should be at least one dashboard configuration
        - BR-03: each dashboard configuration should contain a node "path" (to a configuration file)
        - BR-04: each "path" should lead to an existing file
        - BR-05: each configuration file should be a json file (that can be loaded as a dictionary)
        - BR-06: each dashboard configuration could have a node "description" that must be of type string
        - BR-07: each dashboard configuration does not have other nodes but "path" and "description"

        Logic:
        - For each "dashboard configuration"
        - Load the "dashboard configuration file"
        - And return a deep-copied dictionary.
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _dict_the_return: dict = deepcopy(dict_dashboards_configurations)

        # BR-01: the node "dashboards configurations" is mandatory
        if _dict_the_return is None:
            raise Exception(f"BR-01: The node '{self._const_str__config_tag__dashboards_cfgs__as_dict}' is mandatory.")

        # BR-02: there should be at least one dashboard configuration
        if len(_dict_the_return) == 0:
            raise Exception(f"BR-02: there should be at least one dashboard configuration.")

        # We loop through each dashboard configuration
        for k_dashboard_config, v_dashboard_config in _dict_the_return.items():

            # We get the node "path"
            _str_the_path: str = v_dashboard_config.get(self._const_str__config_tag__dashboard_cfg__path__as_path, None)

            # BR-03: each dashboard configuration should contain a node "path" (to a configuration file)
            if _str_the_path is None:
                raise Exception(
                    f"BR-03: dashboard configuration for '{k_dashboard_config}' should contain a node "
                    f"'{self._const_str__config_tag__dashboard_cfg__path__as_path}' (to a configuration file)"
                )

            # BR-04: each "path" should lead to an existing file
            if os.path.isfile(path=_str_the_path) is False:
                raise Exception(
                    f"BR-04: path '{_str_the_path}' (for dashboard configuration '{k_dashboard_config}') should lead "
                    f"to an existing file"
                )

            try:
                with open(file=_str_the_path, mode='r') as json_file:
                    _dict_the_dashboard_configuration: dict = json.load(fp=json_file)
            except Exception as an_exception:
                raise Exception(
                    f"BR-05: configuration file '{_str_the_path}' for dashboard '{k_dashboard_config}' should be a "
                    f"json file (that can be loaded as a dictionary)."
                ) from an_exception

            # We get the node description
            _str_the_description: str | None = \
                v_dashboard_config.get(self._const_str__config_tag__dashboard_cfg__description__as_str, None)

            # BR-06: each dashboard configuration could have a node "description" that must be of type string
            if _str_the_description is not None:
                if isinstance(_str_the_description, str) is False:
                    raise Exception(
                        f"BR-06: each dashboard configuration could have a node "
                        f"'{self._const_str__config_tag__dashboard_cfg__description__as_str}' that must be of type "
                        f"string (but which is of  type '{type(_str_the_description)}')."
                    )

            # BR-07: each dashboard configuration does not have other nodes but "path" and "description"
            _lst_unexpected_nodes: list[str] = list(
                set(v_dashboard_config.keys())
                - {
                    self._const_str__config_tag__dashboard_cfg__path__as_path,
                    self._const_str__config_tag__dashboard_cfg__description__as_str
                }
            )
            if len(_lst_unexpected_nodes) > 0:
                raise Exception(
                    f"BR-07: dashboard configuration (for '{k_dashboard_config}') does have unexpected nodes: "
                    f"'{', '.join(_lst_unexpected_nodes)}'."
                )

            v_dashboard_config[self._const_str__config_tag__dashboard_cfg__configuration__as_dict] = \
                _dict_the_dashboard_configuration

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return _dict_the_return

    @staticmethod
    def _instantiate_data_handlers(
            dict_distributions_configurations: dict
    ) -> dict[str, DataHandler]:
        """
        Instantiate as many data handlers as data sets to broadcast. These data handlers will then be called to check/
        modify data for each distribution.

        From the Broadcaster configuration below:
        {
            "dashboards configurations": {...},
            "distributions configurations": {

                "a label for a distribution, aka k_distribution_lbl in the logic below": {

                    "description": "a description for the distribution, facultative",
                    (...),

                    "data sets handlers": {

                        "a label for a data set to handle, aka k_data_set in the logic below": {
                            # Note: this label should be among the function parameters when calling "distribute"

                            "description": "a description of the logic across the below steps",

                            "steps": [
                                {
                                    "description": "a description of the step",
                                    "feature": "a label of a data handler feature",
                                    "param": {
                                        (...),
                                        "b_copy": true | false
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }

        We produce a data handler for the data set "a label for a data set to handle", from the below configuration:
        {
            "a label for a distribution": {
                # That corresponds to "a label for the sequence that can be run in isolation"

                "description": "a description of the logic across the below steps",
                "steps": [
                    {
                        "description": "a description of the step",
                        "feature": "a label of a data handler feature",
                        "param": {
                            (...),
                            "b_copy": true | false
                        }
                    }
                ]
            }
        }

        """
        DataBroadcaster._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _dict_the_return: dict[str, DataHandler] = {}
        _dict_the_data_sets_handlers_cfgs: dict[str, dict] = {}

        # For each distribution
        for k_distribution_lbl, v_distribution_cfg in dict_distributions_configurations.items():

            # For each data set to handle
            for k_data_set, v_data_set_handler_cfg in v_distribution_cfg.get(
                    DataBroadcaster._const_str__config_tag__distribution_cfg__data_sets_handlers_cfgs__as_dict,
                    {}
            ).items():
                # We get the existing data handler
                _dict_existing_dh: dict = _dict_the_data_sets_handlers_cfgs.get(
                    k_data_set,
                    {}
                )

                _dict_existing_dh[k_distribution_lbl] = v_data_set_handler_cfg

                # We update the repository of data handlers
                _dict_the_data_sets_handlers_cfgs[k_data_set] = _dict_existing_dh

        for k_data_set, v_dh_cfg in _dict_the_data_sets_handlers_cfgs.items():
            _dict_the_return[k_data_set] = DataHandler(dict_config=v_dh_cfg)

        DataBroadcaster._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return _dict_the_return

    def distribute(
            self,
    ):
        """
        on peut commencer à distribuer...
        """
        pass
