import os
import shutil

import numpy as np
import pandas as pd
import pytest
from zen_garden import Results, run

from tests.end_to_end.utils.test_helpers import (
    compare_variables_results,
)


def copy_dataset(fixtures_path, tmp_path, data_set_name, files):
    """Copy ``test_1a`` to ``tmp_path`` and add or overwrite input files.

    Args:
        fixtures_path: Folder containing the standard fixtures.
        tmp_path: Temporary folder of the test.
        data_set_name: Name of the copied data set.
        files: Mapping of paths relative to the data set to file contents.

    Returns:
        Path of the copied data set.
    """
    dataset = tmp_path / data_set_name
    shutil.copytree(os.path.join(fixtures_path, "test_1a"), dataset)
    for relative_path, content in files.items():
        (dataset / relative_path).write_text(content)
    return dataset


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


@pytest.mark.parametrize(
    "direction, node, limit", [("out", "DE", 3.0), ("in", "CH", 5.0)]
)
def test_transport_limit(fixtures_path, tmp_path, direction, node, limit):
    """Test that the yearly transport limit into or out of a node is binding.

    Natural gas is made cheaper in DE and the import availability in CH is
    raised, so that without limits all 22 GWh of gas consumed in CH are
    transported from DE. The limit on the flow out of DE or into CH (net of
    losses) is therefore binding.
    """
    data_set_name = f"test_1a_transport_limit_{direction}"
    dataset = copy_dataset(
        fixtures_path,
        tmp_path,
        data_set_name,
        {
            "set_carriers/natural_gas/price_import.csv": "node,price_import\nDE,10\n",
            "set_carriers/natural_gas/availability_import.csv": (
                "node,time,availability_import\nCH,0,20\nCH,1,20\nDE,1,100\n"
            ),
            f"set_carriers/natural_gas/transport_limit_{direction}.csv": (
                f"node,transport_limit_{direction}\n{node},{limit}\n"
            ),
        },
    )
    run(
        config=os.path.join(fixtures_path, "config_transport_limit.yaml"),
        dataset=str(dataset),
        folder_output=str(tmp_path / "outputs"),
    )

    results = Results(str(tmp_path / "outputs" / data_set_name))
    flow_transport = results.get_unprocessed_result("flow_transport")
    flow_transport_loss = results.get_unprocessed_result("flow_transport_loss")
    # all time steps have a duration of one hour
    flows = {
        "out": flow_transport.xs("DE-CH", level=1).sum(),
        "in": (flow_transport - flow_transport_loss).xs("DE-CH", level=1).sum(),
    }

    assert np.isclose(flows[direction], limit)


def test_carbon_emissions_annual_limit_nodal(fixtures_path, tmp_path):
    """Test the nodal carbon emissions and the binding nodal limit.

    Without the limit, CH emits 0.0042 Mt (the base unit of emissions). The
    limit for CH is 0.01314 Gt = 13.14 Mt per full year, i.e.,
    13.14 * 2 / 8760 = 0.003 Mt for the two modeled hours, so that CH imports
    less gas and receives more gas from DE.
    """
    data_set_name = "test_1a_carbon_emissions_annual_limit_nodal"
    dataset = copy_dataset(
        fixtures_path,
        tmp_path,
        data_set_name,
        {
            "energy_system/carbon_emissions_annual_limit_nodal.csv": (
                "node,carbon_emissions_annual_limit_nodal\nCH,0.01314\n"
            ),
        },
    )
    run(
        config=os.path.join(
            fixtures_path, "config_carbon_emissions_annual_limit_nodal.yaml"
        ),
        dataset=str(dataset),
        folder_output=str(tmp_path / "outputs"),
    )

    results = Results(str(tmp_path / "outputs" / data_set_name))
    emissions_nodal = results.get_unprocessed_result("carbon_emissions_annual_nodal")
    emissions_annual = results.get_unprocessed_result("carbon_emissions_annual")
    emissions_carrier = results.get_unprocessed_result("carbon_emissions_carrier")

    # without technology emissions, the nodal emissions are the carrier emissions
    expected_nodal = emissions_carrier.groupby(level=1).sum()
    assert np.allclose(
        emissions_nodal.groupby(level=0).sum().sort_index(),
        expected_nodal.sort_index(),
    )
    assert np.isclose(emissions_nodal.sum(), emissions_annual.sum())
    assert np.isclose(emissions_nodal.loc["CH"].sum(), 0.003)


def test_carbon_emissions_annual_nodal_transport(fixtures_path, tmp_path):
    """Test that net exports of the carbon carrier are attributed to the nodes.

    Natural gas stands in for the carbon carrier and the boiler for the carbon
    storage technology, whose carbon intensity is applied to the net exports.
    """
    data_set_name = "test_1a_carbon_emissions_annual_nodal_transport"
    boiler = "set_technologies/set_conversion_technologies/natural_gas_boiler"
    dataset = copy_dataset(
        fixtures_path,
        tmp_path,
        data_set_name,
        {
            f"{boiler}/carbon_intensity_technology.csv": (
                "node,carbon_intensity_technology\nDE,-0.1\nCH,-0.1\n"
            ),
        },
    )
    run(
        config=os.path.join(
            fixtures_path, "config_carbon_emissions_annual_limit_nodal_transport.yaml"
        ),
        dataset=str(dataset),
        folder_output=str(tmp_path / "outputs"),
    )

    results = Results(str(tmp_path / "outputs" / data_set_name))
    emissions_nodal = (
        results.get_unprocessed_result("carbon_emissions_annual_nodal")
        .groupby(level=0)
        .sum()
    )
    emissions_carrier = (
        results.get_unprocessed_result("carbon_emissions_carrier")
        .groupby(level=1)
        .sum()
    )
    emissions_technology = (
        results.get_unprocessed_result("carbon_emissions_technology")
        .groupby(level=1)
        .sum()
    )
    carbon_intensity = results.get_unprocessed_result(
        "carbon_intensity_technology"
    ).loc[("natural_gas_boiler", "DE")]
    flow_transport = results.get_unprocessed_result("flow_transport")
    flow_transport_loss = results.get_unprocessed_result("flow_transport_loss")
    # all time steps have a duration of one hour
    flow_out_de = flow_transport.xs("DE-CH", level=1).sum()
    flow_in_ch = (flow_transport - flow_transport_loss).xs("DE-CH", level=1).sum()
    assert flow_out_de > 0
    assert carbon_intensity < 0

    net_export = pd.Series({"DE": flow_out_de, "CH": -flow_in_ch})
    expected = (
        emissions_carrier
        + emissions_technology.reindex(emissions_carrier.index)
        + carbon_intensity * net_export
    )
    assert np.allclose(
        emissions_nodal.sort_index(), expected.reindex(emissions_nodal.index)
    )
