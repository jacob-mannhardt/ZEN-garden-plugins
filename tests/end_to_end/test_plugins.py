import os
import shutil

import numpy as np
import pandas as pd
from zen_garden import Results, run

from tests.end_to_end.utils.test_helpers import (
    compare_variables_results,
)


# All the tests
###############
def test_1a(fixtures_path, capsys):
    # add duals for this test

    # test also whether config and dataset can take just file name in cwd
    cwd = os.getcwd()
    os.chdir(fixtures_path)
    try:
        # run the test
        data_set_name = "test_1a"
        run(
            config="config_duals.yaml",
            dataset=data_set_name,
        )

        # read the results and check again
        res = Results(os.path.join("outputs", data_set_name))
        compare_variables_results(
            data_set_name, res, fixtures_path, "test_variables.yaml"
        )

        output = capsys.readouterr().out
        assert "[Plugin Template] Example setting: set_value" in output
        assert "[Plugin Template] Example number: 42" in output
        assert "[Plugin Template] Plugin loaded successfully!" in output
    finally:
        os.chdir(cwd)


def test_plugin_template_add_new_constraint(fixtures_path):
    """Test that the node-indexed variable equals the input parameter."""
    data_set_name = "test_1a"
    run(
        config=os.path.join(
            fixtures_path, "config_plugin_template_add_new_constraint.yaml"
        ),
        dataset=os.path.join(fixtures_path, data_set_name),
    )

    results = Results(os.path.join(fixtures_path, "outputs", data_set_name))
    new_variable = results.get_unprocessed_result("new_variable")
    parameter_input = pd.read_csv(
        os.path.join(
            fixtures_path, data_set_name, "energy_system", "new_parameter.csv"
        ),
        index_col="node",
    )["new_parameter"]

    assert new_variable.index.name == "node"
    assert set(new_variable.index) == set(parameter_input.index)
    assert np.allclose(new_variable.sort_index(), parameter_input.sort_index())


def test_tech_share_limits(fixtures_path, tmp_path):
    """Test that the technology share limits bind.

    The dataset extends test_1a by a more efficient boiler, which would supply
    all heat without the plugin. Its share of the heat demand in DE is limited
    to 30%, and the less efficient boiler must consume at least 80% of the
    natural gas used by conversion technologies in CH.
    """
    data_set_name = "test_tech_share_limits"
    dataset = tmp_path / data_set_name
    shutil.copytree(os.path.join(fixtures_path, "test_1a"), dataset)
    conversion_technologies = (
        dataset / "set_technologies" / "set_conversion_technologies"
    )
    boiler = conversion_technologies / "natural_gas_boiler"
    efficient_boiler = conversion_technologies / "natural_gas_boiler_efficient"
    shutil.copytree(boiler, efficient_boiler)
    attributes = (efficient_boiler / "attributes.yaml").read_text()
    (efficient_boiler / "attributes.yaml").write_text(
        attributes.replace("default_value: 1.1", "default_value: 1.0")
    )
    system = (dataset / "system.yaml").read_text()
    (dataset / "system.yaml").write_text(
        system.replace(
            "- natural_gas_boiler\n",
            "- natural_gas_boiler\n- natural_gas_boiler_efficient\n",
        )
    )
    (efficient_boiler / "demand_share_max_by_tech.csv").write_text(
        "carrier,node,year,demand_share_max_by_tech\nheat,DE,2022,0.3\n"
    )
    # without carrier column, the share applies to all input carriers
    (boiler / "input_share_min_by_tech.csv").write_text(
        "node,year,input_share_min_by_tech\nCH,2022,0.8\n"
    )

    run(
        config=os.path.join(fixtures_path, "config_tech_share_limits.yaml"),
        dataset=str(dataset),
    )

    results = Results(os.path.join(fixtures_path, "outputs", data_set_name))
    output = results.get_total("flow_conversion_output")[2022]
    input_flow = results.get_total("flow_conversion_input")[2022]
    demand = results.get_total("demand")[2022]

    efficient_output_de = output[("natural_gas_boiler_efficient", "heat", "DE")]
    assert np.isclose(efficient_output_de, 0.3 * demand[("heat", "DE")])

    gas_input_ch = input_flow.xs(("natural_gas", "CH"), level=(1, 2))
    assert np.isclose(gas_input_ch["natural_gas_boiler"], 0.8 * gas_input_ch.sum())
