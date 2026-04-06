from RUFAS.input_manager import InputManager


def test_extract_target_and_save_block_reads_nested_crop_configuration_paths() -> None:
    """Cross-validation paths should match the nested pool shape for crop configurations."""
    im = InputManager()
    setattr(
        im,
        "_InputManager__pool",
        {
            "crop_configurations": {
                "crop_configurations": [
                    {
                        "minimum_temperature": 4.0,
                        "optimal_temperature": 25.0,
                    }
                ]
            }
        },
    )

    result = im._extract_target_and_save_block(
        {
            "variables": {
                "minimum_temperature": "crop_configurations.crop_configurations.0.minimum_temperature",
                "optimal_temperature": "crop_configurations.crop_configurations.0.optimal_temperature",
            }
        },
        eager_termination=True,
    )

    assert result == {
        "minimum_temperature": 4.0,
        "optimal_temperature": 25.0,
    }
