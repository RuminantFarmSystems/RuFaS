import ..RUFAS
from pathlib import Path


config_dictionary = {
    "start_date": "1989:1",
    "end_date": "2019:365",
    "csv_dir": "output/CSVs/",
    "graphic_dir": "output/graphics/",
    "set_seed": False,
    "seed": 0
}

field_data = {
                "soil": "ARL_soil.json",
                "crop": "ARL_rotation.json",
                "field_management": "ARL_field_management.json"
            }

config = RUFAS.classes.Config(data=config_dictionary, weather_file="ARL_weather.csv")

time = RUFAS.classes.Time(config=config)

weather = RUFAS.classes.Weather(weather_file="ARL_weather.csv", config=config)

field = RUFAS.routines.Field("test field", field_data=field_data, time=time)

fields = RUFAS.classes.Fields({"test field": field_data}, time)

soil_data = RUFAS.routines.read_json_file(Path("/input/soil/ARL_soil.json"))

soil = RUFAS.routines.Soil(data=soil_data)

crop_data = RUFAS.routines.read_json_file(Path("/input/crop/ARL_rotation.json"))

crop = RUFAS.routines.Crop(data=crop_data, time=time)

field_management_data = RUFAS.routines.read_json_file(Path("/input/field_management/ARL_field_management.json"))

field_management = RUFAS.routines.FieldManagement(app_data=field_management_data, time=time)

## Test Crop and soil routines
    ### They are all returning 'None' type for some reason.

daily_crops = RUFAS.routines.daily_crop_routine(soil=soil, crop=crop, weather=weather, time=time, field_management=field_management) #None

daily_soil = RUFAS.routines.daily_soil_routine(soil=soil, crop=crop, field_management=field_management, weather=weather, time=time) #None

annual_crops = RUFAS.routines.annual_crop_routine(crop=crop, time=time) #None


# animal_management = RUFAS.routines.AnimalManagement()

# manure_storage = RUFAS.routines.ManureStorage(animal_management=animal_management)

# field_management =

## Test daily_soil_routine

## Test daily_crop_routine