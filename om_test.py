from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits

if __name__ == "__main__":
    om = OutputManager()
    variables = {
        "a": 1,
        "b": 2.2,
        "c": "3",
        "d": [4, 5, 6],
    }
    info_maps = [
        {"class": "test", "function": "test", "units": MeasurementUnits.UNITLESS} for _ in range(len(variables))
    ]
    thread = om.add_variable_bulk_async(variables, info_maps)
    om.add_variable("d", 10, {**info_maps[0], "units": MeasurementUnits.UNITLESS})
    om.add_variable("c", 11, {**info_maps[0], "units": MeasurementUnits.UNITLESS})
    om.add_variable("e", 7, {**info_maps[0], "units": MeasurementUnits.UNITLESS})
    om.add_variable("f", 8, {**info_maps[0], "units": MeasurementUnits.UNITLESS})
    om.add_variable("g", 9, {**info_maps[0], "units": MeasurementUnits.UNITLESS})

    # print(om.variables_pool)
    # print("Main thread is continuing to do other work...")

    thread.join()
    print(om.variables_pool)
