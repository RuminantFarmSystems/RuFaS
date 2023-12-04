import argparse
import os.path
from pathlib import Path
from mock import MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from RUFAS.config import Config
from RUFAS.routines.animal.life_cycle.herd_factory import HerdFactory
from config import global_variables
from main import (
    CaseInsensitiveArgumentAction,
    clear_output_dir,
    execute_simulations,
    is_file_in_dir,
    main,
    parse_gnu_args,
    run_load_vars_pool,
    run_rufas,
    run_validation,
    METADATA_PATHS,
    initialize_herd,
)

from RUFAS.simulation_engine import SimulationEngine
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager, LogVerbosity

dir_path = os.path.join(global_variables.ROOT_DIR, "input")
file_path = os.path.join(dir_path, "input/ARL.json")


@pytest.mark.parametrize(
    "load_pool, no_graphics, format_option, verbose, clear_output, exclude_info_maps, only_run_validation,"
    "graphics_dir, vars_file_path, output_dir, filters_dir, init_herd, save_animals, save_animals_path,"
    "terminate_simulation_post_herd_generation",
    [
        (False, False, "verbose", LogVerbosity.ERRORS, True, True, True, "graphics", "", "output/",
         "output/output_filters", False, False, "output/", False),
        (False, True, "basic", LogVerbosity.LOGS, False, False, False, "custom_graphics", "", "output/",
         "output/output_filters", True, False, "output/", False),
        (False, True, "block", LogVerbosity.NONE, True, False, False, "graphics", "", "output/",
         "output/output_filters", True, True, "output/", False),
        (True, False, "inline", LogVerbosity.WARNINGS, False, False, False, "custom_graphics", "path.json", "output/",
         "output/output_filters", True, True, "output/", True),
        (True, True, "verbose", LogVerbosity.LOGS, False, True, False, "graphics", "path.json", "output/",
         "output/output_filters", False, False, "output/", True),
    ],
)
def test_main(
        load_pool: bool,
        no_graphics: bool,
        format_option: str,
        verbose: LogVerbosity,
        clear_output: bool,
        exclude_info_maps: bool,
        only_run_validation: bool,
        graphics_dir: str,
        vars_file_path: str,
        output_dir: str,
        filters_dir: str,
        init_herd: bool,
        save_animals: bool,
        save_animals_path: str,
        terminate_simulation_post_herd_generation: bool
) -> None:
    with patch("main.parse_gnu_args") as mock_parse_gnu_args:
        mock_parse_gnu_args.return_value = argparse.Namespace(
            no_graphics=no_graphics,
            format_option=format_option,
            verbose=verbose,
            clear_output=clear_output,
            exclude_info_maps=exclude_info_maps,
            only_run_validation=only_run_validation,
            graphics_dir=graphics_dir,
            load_pool=vars_file_path,
            output_dir=output_dir,
            filters_dir=filters_dir,
            init_herd=init_herd,
            save_animals=save_animals,
            save_animals_dir=save_animals_path,
            terminate_simulation_post_herd_generation=terminate_simulation_post_herd_generation
        )

        with patch("main.run_rufas") as mock_run_rufas:
            main()
            mock_parse_gnu_args.assert_called_once()
            mock_run_rufas.assert_called_once_with(
                load_pool,
                produce_graphics=not no_graphics,
                format_option=format_option,
                verbose=verbose,
                clear_output=clear_output,
                exclude_info_maps=exclude_info_maps,
                only_run_validation=only_run_validation,
                graphics_dir=Path(graphics_dir),
                vars_file_path=Path(vars_file_path),
                output_dir=Path(output_dir),
                filters_dir=Path(filters_dir),
                init_herd=init_herd,
                save_animals=save_animals,
                save_animals_dir=Path(save_animals_path),
                terminate_simulation_post_herd_generation=terminate_simulation_post_herd_generation
            )


@pytest.mark.parametrize(
    "format_option, produce_graphics, verbose, clear_output, exclude_info_maps, only_run_validation,"
    "graphics_dir, load_pool, vars_file_path, output_dir, filters_dir, init_herd, save_animals, save_animals_dir,"
    "terminate_simulation_post_herd_generation",
    [
        ("verbose", True, LogVerbosity.NONE, True, True, True, "", False, "", "output/", "output/output_filters", False,
         False, "output/", False),
        ("block", False, LogVerbosity.LOGS, True, True, True, "", False, "", "output/", "output/output_filters", False,
         False, "output/", False),
        ("inline", True, LogVerbosity.ERRORS, True, True, True, "", False, "", "output/", "output/output_filters",
         False, False, "output/", False),
        ("basic", True, LogVerbosity.WARNINGS, False, True, True, "", False, "", "output/", "output/output_filters",
         False, False, "output/", False),
        ("verbose", True, LogVerbosity.NONE, True, False, True, "", False, "", "output/", "output/output_filters",
         False, False, "output/", False),
        ("block", True, LogVerbosity.LOGS, True, True, False, "", False, "", "output/", "output/output_filters", False,
         False, "output/", False),
        ("inline", False, LogVerbosity.ERRORS, True, True, True, "", False, "", "output/", "output/output_filters",
         False, False, "output/", False),
        ("basic", False, LogVerbosity.WARNINGS, False, True, True, "", False, "", "output/", "output/output_filters",
         False, False, "output/", False),
        ("verbose", False, LogVerbosity.NONE, True, False, True, "", False, "", "output/", "output/output_filters",
         False, False, "output/", False),
        ("block", False, LogVerbosity.LOGS, True, True, False, "", False, "", "output/", "output/output_filters", False,
         False, "output/", False),
        ("inline", False, LogVerbosity.ERRORS, False, True, True, "", False, "", "output/", "output/output_filters",
         False, False, "output/", False),
        ("basic", False, LogVerbosity.WARNINGS, True, False, True, "", False, "", "output/", "output/output_filters",
         False, False, "output/", False),
        ("verbose", False, LogVerbosity.NONE, True, True, False, "", False, "", "output/", "output/output_filters",
         False, False, "output/", False),
        ("block", False, LogVerbosity.WARNINGS, False, False, True, "", False, "", "output/", "output/output_filters",
         False, False, "output/", False),
        ("inline", False, LogVerbosity.LOGS, False, True, False, "", False, "", "output/", "output/output_filters",
         False, False, "output/", False),
        ("basic", False, LogVerbosity.ERRORS, False, False, False, "", False, "", "output/", "output/output_filters",
         False, False, "output/", False),
        ("basic", False, LogVerbosity.LOGS, False, False, False, "graphics", False, "", "output/",
         "output/output_filters", False, False, "output/", False),
        ("basic", False, LogVerbosity.LOGS, False, False, False, "graphics", True, "path.json", "output/",
         "output/output_filters", False, False, "output/", False),
    ],
)
def test_run_rufas(
        format_option: str,
        produce_graphics: bool,
        verbose: LogVerbosity,
        clear_output: bool,
        exclude_info_maps: bool,
        only_run_validation: bool,
        graphics_dir: str,
        load_pool: bool,
        vars_file_path: str,
        output_dir: str,
        filters_dir: str,
        init_herd: bool,
        save_animals: bool,
        save_animals_dir: str,
        terminate_simulation_post_herd_generation: bool,
        mocker: MockerFixture,
        capsys,
) -> None:
    """Checks that run_rufas() calls the correct functions in the correct order"""
    # Arrange
    metadata_file_list = METADATA_PATHS
    patch_execute_simulations = mocker.patch("main.execute_simulations")
    patch_run_validation = mocker.patch("main.run_validation")
    patch_run_load_vars_pool = mocker.patch("main.run_load_vars_pool")
    patch_clear_output_dir = mocker.patch("main.clear_output_dir")

    # Act
    run_rufas(
        load_pool,
        produce_graphics,
        format_option,
        verbose,
        clear_output,
        exclude_info_maps,
        only_run_validation,
        graphics_dir,
        vars_file_path,
        output_dir,
        filters_dir,
        init_herd,
        save_animals,
        save_animals_dir,
        terminate_simulation_post_herd_generation
    )

    # Assert
    if load_pool:
        patch_run_load_vars_pool.assert_called_once_with(
            vars_file_path,
            exclude_info_maps,
            format_option,
            produce_graphics,
            graphics_dir,
            clear_output,
            output_dir,
            filters_dir,
        )
        return
    elif only_run_validation:
        patch_run_validation.assert_called_once_with(
            metadata_file_list,
            exclude_info_maps,
            format_option,
            verbose,
            output_dir,
        )
    else:
        patch_execute_simulations.assert_called_once_with(
            metadata_file_list,
            exclude_info_maps,
            produce_graphics,
            graphics_dir,
            format_option,
            verbose,
            output_dir,
            filters_dir,
            init_herd,
            save_animals,
            save_animals_dir,
            terminate_simulation_post_herd_generation
        )

    if clear_output:
        patch_clear_output_dir.assert_called_once()
    else:
        patch_clear_output_dir.assert_not_called()

    captured = capsys.readouterr()
    expected_message = "RuFaS: Ruminant Farm Systems Model 2023\n"
    assert expected_message in captured.out


@pytest.mark.parametrize("is_data_valid", [(True), (False)])
def test_run_validation(mocker: MockerFixture, is_data_valid: bool) -> None:
    """Checks that run_validation() calls the correct functions in the correct order"""
    mock_output_manager = mocker.MagicMock(auto_spec=OutputManager)
    mock_input_manager = mocker.MagicMock(auto_spec=InputManager)
    mock_output_manager.flush_pools.return_value = None
    mock_input_manager.flush_pool.return_value = None
    mock_output_manager.dump_all_nondata_pools.return_value = None
    mock_output_manager.save_results.return_value = None
    mocker.patch("main.OutputManager", return_value=mock_output_manager)
    mocker.patch("main.InputManager", return_value=mock_input_manager)
    metadata_prefix1 = "dummy_prefix1"
    metadata_prefix2 = "dummy_prefix2"
    metadata_file_path1 = Path("metadata_file1.json")
    metadata_file_path2 = Path("metadata_file2.json")
    metadata_file_list = [
        {"prefix": metadata_prefix1, "path": metadata_file_path1},
        {"prefix": metadata_prefix2, "path": metadata_file_path2},
    ]
    mock_input_manager.start_data_processing.return_value = is_data_valid
    exclude_info_maps = False
    format_option = "verbose"
    verbose = LogVerbosity.NONE
    output_dir = Path("output/")

    run_validation(metadata_file_list, exclude_info_maps, format_option, verbose, output_dir)

    assert mock_output_manager.flush_pools.call_count == len(metadata_file_list)
    assert mock_input_manager.flush_pool.call_count == len(metadata_file_list)
    assert mock_output_manager.dump_all_nondata_pools.call_count == len(
        metadata_file_list
    )
    assert mock_output_manager.dump_all_nondata_pools.call_args_list == [
        mocker.call(output_dir, exclude_info_maps, format_option)
    ] * len(metadata_file_list)


@pytest.mark.parametrize(
    "set_seed, seed, terminate_simulation_post_herd_generation, add_log_count",
    [
        (False, 42, True, 3),
        (False, 42, False, 2),
        (False, 31415, True, 3),
        (False, 31415, False, 2),
        (True, 42, True, 3),
        (True, 42, False, 2),
        (True, 31415, True, 3),
        (True, 31415, False, 2),
    ],
)
def test_initialize_herd(
        mocker: MockerFixture,
        set_seed: bool,
        seed: int,
        terminate_simulation_post_herd_generation: bool,
        add_log_count: int
) -> None:
    mock_output_manager = mocker.MagicMock(auto_spec=OutputManager)
    mock_simulation_config = mocker.MagicMock(auto_spec=Config)
    mock_herd_factory = mocker.MagicMock(auto_spec=HerdFactory)

    mock_output_manager.add_log.return_value = None
    mock_simulation_config.set_seed = set_seed
    mock_simulation_config.seed = seed
    mock_herd_factory.initialize_herd.return_value = None

    patch_random_seed = mocker.patch("random.seed", return_value=None)
    patch_numpy_random_seed = mocker.patch("numpy.random.seed", return_value=None)

    mocker.patch("main.OutputManager", return_value=mock_output_manager)
    mocker.patch("main.HerdFactory", return_value=mock_herd_factory)

    initialize_herd(simulation_config=mock_simulation_config,
                    init_herd=False,
                    save_animals=False,
                    save_animals_dir=Path("output/"),
                    terminate_simulation_post_herd_generation=terminate_simulation_post_herd_generation)

    if set_seed:
        patch_random_seed.assert_called_once_with(seed)
        patch_numpy_random_seed.assert_called_once_with(seed)
    else:
        patch_random_seed.assert_not_called()
        patch_numpy_random_seed.assert_not_called()

    assert mock_herd_factory.initialize_herd.call_count == 1
    assert mock_output_manager.add_log.call_count == add_log_count

@pytest.mark.parametrize(
    "produce_graphics, exlclude_info_maps, is_data_valid, terminate_simulation_post_herd_generation, "
    "initialize_herd_call_count, simulate_call_count, add_error_call_count, format_option",
    [
        (False, False, True, False, 2, 2, 0, "verbose"),
        (False, False, False, False, 0, 0, 4, "block"),
        (False, True, True, False, 2, 2, 0, "inline"),
        (False, True, False, False, 0, 0, 4, "basic"),
        (True, False, True, False, 2, 2, 0, "verbose"),
        (True, False, False, False, 0, 0, 4, "block"),
        (True, True, True, False, 2, 2, 0, "basic"),
        (True, True, False, False, 0, 0, 4, "inline"),

        (False, False, True, True, 2, 0, 0, "verbose"),
        (False, False, False, True, 0, 0, 4, "block"),
        (False, True, True, True, 2, 0, 0, "inline"),
        (False, True, False, True, 0, 0, 4, "basic"),
        (True, False, True, True, 2, 0, 0, "verbose"),
        (True, False, False, True, 0, 0, 4, "block"),
        (True, True, True, True, 2, 0, 0, "basic"),
        (True, True, False, True, 0, 0, 4, "inline"),
    ],
)
def test_execute_simulations(
        mocker: MockerFixture,
        produce_graphics: bool,
        exlclude_info_maps: bool,
        is_data_valid: bool,
        terminate_simulation_post_herd_generation: bool,
        initialize_herd_call_count: int,
        simulate_call_count: int,
        add_error_call_count: int,
        format_option: str,
) -> None:
    """Checks that execute_simulations() calls the correct functions in the correct order"""
    # Arrange
    mock_output_manager = mocker.MagicMock(auto_spec=OutputManager)
    mock_input_manager = mocker.MagicMock(auto_spec=InputManager)
    mock_config = mocker.MagicMock(auto_spec=Config)
    mock_output_manager.flush_pools.return_value = None
    mock_input_manager.flush_pool.return_value = None
    mock_output_manager.dump_all_nondata_pools.return_value = None
    mock_output_manager.save_results.return_value = None
    mocker.patch("main.OutputManager", return_value=mock_output_manager)
    mocker.patch("main.InputManager", return_value=mock_input_manager)
    mocker.patch("main.Config", return_value=mock_config)
    metadata_file_path1 = Path("metadata_file1.json")
    metadata_file_path2 = Path("metadata_file2.json")
    metadata_prefix1 = "dummy_prefix1"
    metadata_prefix2 = "dummy_prefix2"
    metadata_file_list = [
        {"prefix": metadata_prefix1, "path": metadata_file_path1},
        {"prefix": metadata_prefix2, "path": metadata_file_path2},
    ]
    mock_input_manager.start_data_processing.return_value = is_data_valid

    patch_initialize_herd = mocker.patch("main.initialize_herd")

    mock_simulator = mocker.MagicMock(auto_spec=SimulationEngine)
    mock_simulator.simulate.return_value = None
    mocker.patch("main.SimulationEngine", return_value=mock_simulator)
    output_dir = Path("output/")
    filters_dir = Path("output/output_filters/")

    # Act
    execute_simulations(
        metadata_files=metadata_file_list,
        exclude_info_maps=exlclude_info_maps,
        produce_graphics=produce_graphics,
        graphics_dir=Path(""),
        format_option=format_option,
        output_dir=output_dir,
        filters_dir=filters_dir,
        init_herd=False,
        save_animals=False,
        save_animals_dir=Path("output/"),
        terminate_simulation_post_herd_generation=terminate_simulation_post_herd_generation
    )

    # Assert
    assert patch_initialize_herd.call_count == initialize_herd_call_count
    assert mock_simulator.simulate.call_count == simulate_call_count
    assert mock_output_manager.add_error.call_count == add_error_call_count
    assert mock_output_manager.flush_pools.call_count == len(metadata_file_list)
    assert mock_input_manager.flush_pool.call_count == len(metadata_file_list)
    assert mock_output_manager.dump_all_nondata_pools.call_count == len(
        metadata_file_list
    )
    assert mock_output_manager.dump_all_nondata_pools.call_args_list == [
        mocker.call(output_dir, exlclude_info_maps, format_option)
    ] * len(metadata_file_list)
    assert mock_output_manager.save_results.call_count == len(metadata_file_list)
    assert mock_output_manager.save_results.call_args_list == [
        mocker.call(
            output_dir,
            filters_dir,
            exlclude_info_maps,
            produce_graphics,
            Path(""),
        ),
    ] * len(metadata_file_list)


@pytest.mark.parametrize(
    "vars_file_path, exclude_info_maps, format_option, produce_graphics, graphics_dir, clear_output",
    [
        ("", True, "verbose", True, Path(""), True),
        ("", True, "verbose", True, Path(""), False),
        ("path.json", True, "verbose", False, Path(""), False),
        ("path.json", True, "verbose", False, Path(""), True),
        ("", False, "verbose", True, Path(""), False),
        ("", False, "verbose", False, Path(""), False),
        ("path.json", False, "verbose", False, Path(""), True),
    ],
)
def test_run_load_vars_pool(mocker: MockerFixture, vars_file_path: str, exclude_info_maps: bool,
                            format_option: str, produce_graphics: bool,
                            graphics_dir: Path, clear_output: bool, ) -> None:
    """Checks the run_load_vars_pool function in main.py"""
    output_dir = Path("output/")
    filters_dir = Path("output/output_filters/")
    mock_output_manager = mocker.MagicMock(auto_spec=OutputManager)
    patch_clear_output_dir = mocker.patch("main.clear_output_dir")
    mock_output_manager.flush_pools.return_value = None
    mock_output_manager.load_variables_pool_from_file.return_value = None
    mock_output_manager.set_metadata_prefix.return_value = None
    mock_output_manager.dump_all_nondata_pools.return_value = None
    mock_output_manager.save_results.return_value = None
    mocker.patch("main.OutputManager", return_value=mock_output_manager)

    run_load_vars_pool(vars_file_path, exclude_info_maps, format_option, produce_graphics, graphics_dir, clear_output,
                       output_dir, filters_dir)

    if clear_output:
        patch_clear_output_dir.assert_called_once()
    else:
        patch_clear_output_dir.assert_not_called()
    assert mock_output_manager.flush_pools.call_count == 1
    assert mock_output_manager.load_variables_pool_from_file.call_count == 1
    assert mock_output_manager.set_metadata_prefix.call_count == 1
    assert mock_output_manager.save_results.call_count == 1
    assert mock_output_manager.dump_all_nondata_pools.call_count == 1


@pytest.mark.parametrize(
    "is_file_found_in_dir",
    [True, False],
)
def test_clear_output_dir(mocker: MockerFixture, is_file_found_in_dir: bool) -> None:
    """Checks clear_output_dir function in main.py"""
    mock_output_manager = mocker.MagicMock(auto_spec=OutputManager)
    mock_output_manager.add_log.return_value = None
    mock_output_manager.add_error.return_value = None
    mocker.patch("main.OutputManager", return_value=mock_output_manager)
    patch_empty_dir = mocker.patch("RUFAS.util.Utility.empty_dir")
    with patch("main.is_file_in_dir", return_value=is_file_found_in_dir):
        with patch('main.Path', new_callable=MagicMock) as mock_path:
            vars_file_path = mock_path.return_value / "dummy_vars_file.txt"
            clear_output_dir(vars_file_path)
            if is_file_found_in_dir:
                assert mock_output_manager.add_log.call_count == 0
                assert mock_output_manager.add_error.call_count == 1
                patch_empty_dir.assert_not_called()
            else:
                patch_empty_dir.assert_called_once()
                assert mock_output_manager.add_log.call_count == 1
                assert mock_output_manager.add_error.call_count == 0


@pytest.mark.parametrize(
    "dir_path, file_path, expected_result",
    [
        (None, None, False),
        (Path("path/to/directory"), Path("path/to/directory/file.json"), True),
        (Path("path/to/directory"), Path("path/to/different_directory/file.json"), False),
        (Path("path/to/directory"), Path("path/to/directory/subdirectory/file.json"), True),
        (Path("path/to/directory"), None, False),
    ],
)
def test_is_file_in_dir(dir_path: Path, file_path: Path, expected_result: bool) -> None:
    """Checks is_file_in_dir function in main.py"""
    assert is_file_in_dir(dir_path, file_path) is expected_result


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
    assert mock_add_argument.call_count == 14
    assert mock_add_argument.call_args_list == [
        mocker.call(
            "-f",
            "--format-option",
            choices=["block", "inline", "verbose", "basic"],
            help="Select formatting option for variable_names.txt file",
        ),
        mocker.call(
            "-g",
            "--no-graphics",
            help="Prevent graphics from generating",
            action="store_true",
        ),
        mocker.call(
            "-G",
            "--graphics_dir",
            help="The saving directory for graphics",
            default="graphics",
        ),
        mocker.call(
            "-v",
            "--verbose",
            choices=["errors", "warnings", "logs", "none"],
            default="none",
            help="Specify the log type to be printed",
        ),
        mocker.call(
            "-c",
            "--clear-output",
            help="Clear output directory before running the simulation",
            action="store_true",
        ),
        mocker.call(
            "-i",
            "--exclude_info_maps",
            help="Exclude info_maps from the output",
            action="store_true",
        ),
        mocker.call(
            "-o",
            "--only-run-validation",
            help="Only validate the data, don't run a simulation",
            action="store_true",
        ),
        mocker.call(
            "-l",
            "--load-pool",
            help="Load the output manager's variables pool from provided path",
            default="",
        ),
        mocker.call(
            "-O",
            "--output-dir",
            help="The saving directory for output",
            default="output/",
        ),
        mocker.call(
            "-F",
            "--filters-dir",
            help="The directory for the files containing the keys for filtering",
            default="output/output_filters/",
        ),
        mocker.call(
            "-I",
            "--init_herd",
            help="Initialize herd with simulation",
            action="store_true",
        ),
        mocker.call(
            "-s",
            "--save_animals",
            help="Save animals to CSV files",
            action="store_true",
        ),
        mocker.call(
            "-S",
            "--save_animals_dir",
            help="The directory for the output animal population JSON file",
            default="output/",
        ),
        mocker.call(
            "-t",
            "--terminate_simulation_post_herd_generation",
            help="Save generated animals to CSV files",
            action="store_true",
        ),
    ]
    mock_parse_args.assert_called_once()
    assert actual_args == "test_args"


def test_case_insensitive_argument_action():
    parser = argparse.ArgumentParser()
    parser.register("action", "ci_action", CaseInsensitiveArgumentAction)

    namespace = argparse.Namespace()

    arguments = ["-f", "-F"]
    value = "test_value"

    for argument in arguments:
        action = parser.add_argument(argument, action="ci_action")
        action(parser, namespace, value, option_string=argument)

    for argument in arguments:
        assert hasattr(namespace, argument)
        assert getattr(namespace, argument) == value
