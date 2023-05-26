def main():
    # An example of how to set up each component of a simulation engine manually.
    config_input_manager = ConfigInputManager(DictInputReader(), ConfigInputValidator())
    config_input_data = config_input_manager.load_input({'start_date': '2010-01-01', 'end_date': '2015-12-31'})
    config_manager = ConfigManager(config_input_data)

    weather_input_manager = WeatherInputManager(CSVFileInputReader(), WeatherInputValidator())
    weather_input_data = weather_input_manager.load_input(Path('weather.csv'))
    weather_manager = WeatherManager(weather_input_data)

    animal_input_manager = AnimalInputManager(JSONFileInputReader(), AnimalInputValidator())
    animal_input_data = animal_input_manager.load_input(Path('animal.json'))
    animal_manager = AnimalManager(animal_input_data)

    manure_input_manager = ManureInputManager(JSONFileInputReader(), ManureInputValidator())
    manure_input_data = manure_input_manager.load_input(Path('manure.json'))
    manure_manager = ManureManager(manure_input_data)

    field_input_manager = FieldInputManager(JSONFileInputReader(), FieldInputValidator())
    field_input_data = field_input_manager.load_input(Path('field.json'))
    field_manager = FieldManager(field_input_data)

    feed_input_manager = FeedInputManager(JSONFileInputReader(), FeedInputValidator())
    feed_input_data = feed_input_manager.load_input(Path('feed.json'))
    feed_manager = FeedManager(feed_input_data)

    state = State({
        'config': config_manager,
        'weather': weather_manager,
        'animal': animal_manager,
        'manure': manure_manager,
        'field': field_manager,
        'feed': feed_manager,
    })

    simple_simulation_runner = SimpleSimulationRunner(state)
    simple_simulation_runner.run_simulation()

    # Another example
    # Assume we have two states that we want to run in parallel
    non_singleton_output_manager1 = SensitivityAnalysisOutputManager()
    non_singleton_output_manager2 = SensitivityAnalysisOutputManager()
    multi_processing_simulation_runner = MultiProcessingSimulationRunner(
        simulation_params_list=[
            {
                'state': state1,
                'output_manager': non_singleton_output_manager1,
            },
            {
                'state': state2,
                'output_manager': non_singleton_output_manager2,
            },
        ],
        sensitivity_analysis_params=[
            {
                'config': {
                    'start_date': '2012-01-01',
                    'end_date': '2012-06-30',
                },
                'animal': {
                    'herd_num': 10000
                }
            },
            {
                'config': {
                    'start_date': '2012-07-01',
                    'end_date': '2012-12-31',
                },
                'animal': {
                    'herd_num': 10000
                }
            }
        ]
    )
    multi_processing_simulation_runner.start_processes()
    multi_processing_simulation_runner.join_processes()
    results1 = non_singleton_output_manager1.get_variables(['some_var1', 'some_var2'])
    results2 = non_singleton_output_manager2.get_variables(['some_var1', 'some_var2'])


