"""Shared input handling for carrier-specific technology share parameters."""

import logging
from typing import ClassVar

import pandas as pd
from zen_garden.model.component_types.parameter import GenericParameter

logger = logging.getLogger(__name__)


class TechShareParameter(GenericParameter):
    """Dimensionless yearly share of a conversion technology per carrier.

    The values are read from ``<parameter_name>.csv`` in the technology folder
    with the columns ``carrier``, ``node``, ``year`` and ``<parameter_name>``.
    The ``carrier`` column may be omitted, in which case the values apply to
    all carriers in :attr:`carrier_attribute` of the technology. Missing
    entries fall back to the default in ``attributes.yaml`` or, if the
    attribute is not specified there, to :attr:`default_value`.

    The standard loader cannot resolve the technology-specific carrier sets as
    an input index, so the values are loaded once per carrier of the
    technology and stacked afterwards.
    """

    _abstract_parameter = True
    #: technology attribute that lists the carriers the share refers to
    carrier_attribute: ClassVar[str]
    unit_category = {}
    default_unit = "max_load"

    @classmethod
    def store_input_data(cls, element) -> None:
        """Load the share for every carrier listed in ``carrier_attribute``."""
        carriers = getattr(element, cls.carrier_attribute)
        if not carriers:
            cls._store_value(element, cls.name, None)
            return
        loader = element.element_data_loader
        index_sets = ["set_nodes", "set_years"]
        default_output, default_value, index_name_list = loader.create_default_output(
            index_sets,
            cls.unit_category,
            file_name=cls.name,
            parameter_default_value=cls.default_value,
            parameter_default_unit=cls.default_unit,
        )
        carrier_header = loader.index_names["set_carriers"]
        input_frames, scenario_factor = cls._read_input_frames(element)
        for df_input in input_frames:
            if carrier_header in df_input.columns:
                unknown_carriers = set(df_input[carrier_header]).difference(carriers)
                if unknown_carriers:
                    logger.warning(
                        f"{cls.name} of {element.name} is given for carriers "
                        f"{sorted(unknown_carriers)} which are not in its "
                        f"{cls.carrier_attribute}. These values are ignored."
                    )

        values = {}
        for carrier in carriers:
            df_output = default_output
            for df_input in input_frames:
                if carrier_header in df_input.columns:
                    df_input = df_input[df_input[carrier_header] == carrier].drop(
                        columns=carrier_header
                    )
                    if df_input.empty:
                        continue
                df_output = loader._extract_general_input_data(
                    df_input.copy(),
                    df_output,
                    cls.name,
                    index_name_list,
                    default_value,
                    index_sets,
                )
            values[carrier] = df_output
        value = pd.concat(values, names=[carrier_header]) * scenario_factor
        cls._store_value(element, cls.name, value)

    @classmethod
    def _read_input_frames(cls, element) -> tuple[list[pd.DataFrame], float]:
        """Read the base input file and the scenario-specific partial file."""
        loader = element.element_data_loader
        file_name, scenario_factor = loader.scenario_dict.get_param_file(
            element.name, cls.name
        )
        file_names = [file_name]
        part_file_name = loader.scenario_dict.get_param_part_file(
            element.name, cls.name
        )
        if part_file_name is not None:
            file_names.append(part_file_name)
        input_frames = []
        for name in file_names:
            df_input = loader.attribute_data_loader.read_csv(name)
            if df_input is not None and not df_input.empty:
                input_frames.append(df_input)
        return input_frames, scenario_factor
