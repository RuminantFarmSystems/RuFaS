import argparse
import os.path
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

import config.global_variables
from config import global_variables
from main import execute_simulations, run_validation
from main import parse_gnu_args
from main import run_rufas
from main import set_global_variables
from main import METADATA_PATHS
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager

dir_path = os.path.join(global_variables.ROOT_DIR, "input")
file_path = os.path.join(dir_path, "input/ARL.json")


@pytest.mark.parametrize(
    "make_graphs, verbose, clear_output, exclude_info_maps, only_run_validation",
    [
        (True, True, True, True, True),
        (False, True, True, True, True),
        (True, False, True, True, True),
        (True, True, False, True, True),
        (True, True, True, False, True),
        (True, True, True, True, False),
        (False, False, True, True, True),
        (False, True, False, True, True),
        (False, True, True, False, True),
        (False, True, True, True, False),
        (False, False, False, True, True),
        (False, False, True, False, True),
        (False, False, True, True, False),
        (False, False, False, False, True),
        (False, False, False, True, False),
        (False, False, False, False, False)
    ],
)
def test_run_rufas(
    make_graphs: bool,
    verbose: bool,
    clear_output: bool,
    exclude_info_maps: bool,
    only_run_validation: bool,
    mocker: MockerFixture,
) -> None:
    """Checks that run_rufas() calls the correct functions in the correct order"""
    # Arrange
    patch_set_global_variables = mocker.patch("main.set_global_variables")
    metadata_file_list = METADATA_PATHS
    patch_execute_simulations = mocker.patch("main.execute_simulations")
    patch_run_validation = mocker.patch("main.run_validation")
    patch_empty_dir = mocker.patch("RUFAS.util.Utility.empty_dir")
    patch_sys_stdout = mocker.patch("sys.stdout.write")

    # Act
    run_rufas(make_graphs, verbose, clear_output, exclude_info_maps, only_run_validation)

    # Assert
    patch_set_global_variables.assert_called_once_with(make_graphs, verbose)
    if only_run_validation:
        patch_run_validation.assert_called_once_with(metadata_file_list, exclude_info_maps)
    else:
        patch_execute_simulations.assert_called_once_with(metadata_file_list, exclude_info_maps)

    if clear_output:
        patch_empty_dir.assert_called_once()
    else:
        patch_empty_dir.assert_not_called()

    if verbose:
        patch_sys_stdout.assert_called_once_with("RuFaS: Ruminant Farm Systems Model 2023\n")


@pytest.mark.parametrize(
    "make_graphs, verbose", [(True, True), (False, True), (True, False), (False, False)]
)
def test_set_global_variables(make_graphs: bool, verbose: bool) -> None:
    """Checks that set_global_variables() sets the global variables correctly"""
    # Arrange
    old_make_graphs = config.global_variables.PRODUCE_GRAPHICS
    old_verbose = config.global_variables.PRINT_STATUS_MESSAGES

    # Act
    set_global_variables(make_graphs, verbose)

    # Assert
    assert config.global_variables.PRODUCE_GRAPHICS == make_graphs
    assert config.global_variables.PRINT_STATUS_MESSAGES == verbose

    # Cleanup
    config.global_variables.PRODUCE_GRAPHICS = old_make_graphs
    config.global_variables.PRINT_STATUS_MESSAGES = old_verbose


@pytest.mark.parametrize(
        "is_data_valid, verbose",
        [(True, True), (True, False), (False, True), (False, False)
         ]
)
def test_run_validation(mocker: MockerFixture, is_data_valid: bool, verbose: bool, capsys) -> None:
    """Checks that run_validation() calls the correct functions in the correct order"""
    mock_output_manager = mocker.MagicMock(auto_spec=OutputManager)
    mock_input_manager = mocker.MagicMock(auto_spec=InputManager)
    mock_output_manager.flush_pools.return_value = None
    mock_input_manager.flush_pool.return_value = None
    mock_output_manager.dump_all_nondata_pools.return_value = None
    mock_output_manager.save_variables.return_value = None
    old_verbose = config.global_variables.PRINT_STATUS_MESSAGES
    config.global_variables.PRINT_STATUS_MESSAGES = verbose
    mocker.patch("main.OutputManager", return_value=mock_output_manager)
    mocker.patch("main.InputManager", return_value=mock_input_manager)
    metadata_prefix1 = "dummy_prefix1"
    metadata_prefix2 = "dummy_prefix2"
    metadata_file_path1 = Path("metadata_file1.json")
    metadata_file_path2 = Path("metadata_file2.json")
    metadata_file_list = [{"prefix": metadata_prefix1, "path": metadata_file_path1},
                          {"prefix": metadata_prefix2, "path": metadata_file_path2}, ]
    mock_input_manager.start_data_processing.return_value = is_data_valid

    run_validation(metadata_file_list, True)

    assert mock_output_manager.flush_pools.call_count == len(metadata_file_list)
    assert mock_input_manager.flush_pool.call_count == len(metadata_file_list)
    assert mock_output_manager.dump_all_nondata_pools.call_count == len(metadata_file_list)
    assert mock_output_manager.dump_all_nondata_pools.call_args_list == [
        mocker.call("output", True)
    ] * len(metadata_file_list)

    captured = capsys.readouterr()

    if config.global_variables.PRINT_STATUS_MESSAGES:
        if is_data_valid:
            expected_messages = ['***Only validating data, no simulation will follow.***\n\n',
                                'Check logs for more detailed data validation info.\n',
                                'Validating data for metadata_file1.json...\n',
                                'Data is valid.\n\n',
                                'Validating data for metadata_file2.json...\n',
                                'Data is valid.\n\n',
                                ]
        else:
            expected_messages = ['***Only validating data, no simulation will follow.***\n\n',
                                'Check logs for more detailed data validation info.\n',
                                'Validating data for metadata_file1.json...\n',
                                "Data not valid for metadata_file1.json.\n\n",
                                'Validating data for metadata_file2.json...\n',
                                "Data not valid for metadata_file2.json.\n\n"
                                ]
    else:
        expected_messages = ["***Only validating data, no simulation will follow.***\n\n"]

    for message in expected_messages:
        assert message in captured.out

    config.global_variables.PRINT_STATUS_MESSAGES = old_verbose


@pytest.mark.parametrize(
        "is_data_valid, simulate_call_count, add_error_call_count",
        [(True, 2, 0),
         (False, 0, 2),
         ]
)
def test_execute_simulations(mocker: MockerFixture, is_data_valid: bool,
                             simulate_call_count: int, add_error_call_count: int, ) -> None:

    """Checks that execute_simulations() calls the correct functions in the correct order"""
    # Arrange
    mock_output_manager = mocker.MagicMock(auto_spec=OutputManager)
    mock_input_manager = mocker.MagicMock(auto_spec=InputManager)
    mock_output_manager.flush_pools.return_value = None
    mock_input_manager.flush_pool.return_value = None
    mock_output_manager.dump_all_nondata_pools.return_value = None
    mock_output_manager.save_variables.return_value = None
    mocker.patch("main.OutputManager", return_value=mock_output_manager)
    mocker.patch("main.InputManager", return_value=mock_input_manager)
    metadata_file_path1 = Path("metadata_file1.json")
    metadata_file_path2 = Path("metadata_file2.json")
    metadata_prefix1 = "dummy_prefix1"
    metadata_prefix2 = "dummy_prefix2"
    metadata_file_list = [{"prefix": metadata_prefix1, "path": metadata_file_path1},
                          {"prefix": metadata_prefix2, "path": metadata_file_path2}, ]
    mock_input_manager.start_data_processing.return_value = is_data_valid
    mock_simulator = mocker.MagicMock(auto_spec=SimulationEngine)
    mock_simulator.simulate.return_value = None
    mocker.patch("main.SimulationEngine", return_value=mock_simulator)

    # Act
    execute_simulations(metadata_file_list, True)

    # Assert
    assert mock_simulator.simulate.call_count == simulate_call_count
    assert mock_output_manager.add_error.call_count == add_error_call_count
    assert mock_output_manager.flush_pools.call_count == len(metadata_file_list)
    assert mock_input_manager.flush_pool.call_count == len(metadata_file_list)
    assert mock_output_manager.dump_all_nondata_pools.call_count == len(metadata_file_list)
    assert mock_output_manager.dump_all_nondata_pools.call_args_list == [
        mocker.call("output", True),
    ] * len(metadata_file_list)
    assert mock_output_manager.save_variables.call_count == len(metadata_file_list)
    assert mock_output_manager.save_variables.call_args_list == [
        mocker.call("output", "output/output_filters/", True),
    ] * len(metadata_file_list)


def test_parse_gnu_args(mocker: MockerFixture) -> None:
    """Checks that parse_gnu_args() correctly parses the user's input."""
    # Arrange
    mock_parser = mocker.MagicMock(auto_spec=argparse.ArgumentParser)
    mock_add_argument = mocker.patch.object(mock_parser, "add_argument")
    mock_parse_args = mocker.patch.object(
        mock_parser, "parse_args", return_value="test_args"
    )
    mocker.patch("main.argparse.ArgumentParser", return_value=mock_parser)

    # Act
    actual_args = parse_gnu_args()

    # Assert
    assert mock_add_argument.call_count == 5
    assert mock_add_argument.call_args_list == [
        mocker.call(
            "-ng",
            "--no-graphics",
            help="Prevent graphics from generating",
            action="store_true",
        ),
        mocker.call(
            "-v",
            "--verbose",
            help="Print progress messages while simulation is running",
            action="store_true",
        ),
        mocker.call(
            "-co",
            "--clear-output",
            help="Clear output directory before running the simulation",
            action="store_true",
        ),
        mocker.call(
            "-ei",
            "--exclude_info_maps",
            help="Exclude info_maps from the output",
            action="store_true",
        ),
        mocker.call(
            "-ov",
            "--only-run-validation",
            help="Only validate the data, don't run a simulation",
            action="store_true",
        )
    ]
    mock_parse_args.assert_called_once()
    assert actual_args == "test_args"
