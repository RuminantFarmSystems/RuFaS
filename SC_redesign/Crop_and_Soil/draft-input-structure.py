"""
This module will define a few dictionaries that will outline a rough estimate of the inputs that the Soil and Crop
module will ultimately need.

This task was undertaken to aid Niko in the development of the DataCollection App

I've broken a field down into multiple compoents:
1. fertilizer specifications
2. manure specifications
3. tillage specifications
4. cropping specifications
5. soil specifications

After making examples of these spec dictionaries, I then combine them into a couple of example fields, which
then get combined into a collection of fields (farm)

Some things to note:
* A field can have one or more of the component specification (except soil - only one soil spec)
* multiple fields can share one or more component specifications
"""

class CSInput:

    @classmethod
    def make_dictionaries(cls):


        # ---- Management practices ----
        # Fertilizer
        """
        This first fertilizer method specifies that the 82N_0P_0K mix is applied every 4 years, starting in 2000.
        This application coincides with corn years and is applied when corn is planted.
        """
        first_fert_specification = {
            "mix": "82N_0P_0K",  # the mix of soil used for this application
            "NPK_content": None,  # the nutrient breakdown of the mix (%)
            "mass_applied": 2839.5,  # the amount of this fertilizer applied at each application (kg/acre)
            "application_depth": 8,  # depth (cm) of application
            "surface_coverage": 80,  # % of the field covered by the application
            "application_years": [2000, 2004, 2008, 2012],  # The years on which the application occurs
            "relative_day": "at planting",  # the timing to apply, relative to planting event
            "specific_day": None,  # the calendar day on which to apply
            # Alternative method to specify application years (pattern-based, optional)
            "start_year": 2000,  # first application year
            "repeat": 0,  # how many times should the application be repeated (after first) before skipping?
            "skip": 3,  # how many years to skip before restarting the applications pattern?
            "cycles": 4,  # how many times should the entire application pattern repeat?
        }

        """
        This second fertilizer method specifies that a custom mix is applied 3 years in a row, with one year
        skipped in between. This coincides with alfalfa years. It is applied on the 99th day of the year, when applied.
        """
        second_fert_specification = {
            "mix": "custom_mix",  # the mix of soil used for this application
            "NPK_content": (0, 10, 10),  # the nutrient breakdown of the mix (%)
            "mass_applied": 100.8,  # the amount of this fertilizer applied at each application (kg/acre)
            "application_depth": 8,  # depth (cm) of application
            "surface_coverage": 80,  # % of the field covered by the application
            "application_years": [2001, 2002, 2003, 2005, 2006, 2007, 2009, 2010, 2011],
            # The years on which the application occurs
            "relative_day": "on a specific date",  # the timing to apply, relative to planting event
            "specific_day": 99,  # the calendar day on which to apply
            # Alternative method to specify application years (pattern-based, optional)
            "start_year": 2001,  # first application year
            "repeat": 2,  # how many times should the application be repeated (after first) before skipping?
            "skip": 1,  # how many years to skip before restarting the applications pattern?
            "cycles": 3  # how many times should the entire application pattern repeat?
        }

        # Manure
        """
        This manure application occurs only twice, on year 0 (corn), and year 4 (alfalfa), more than 7 days after 
        planting (i.e., on different days).

        NOTE: As with fertilizer, a field can have multiple (or no) manure and  tillage specifications, but for the 
        sake of brevity, I'll only include one example here.
        """
        first_manure_specification = {
            "NPK_content": (0, 10, 10),  # the nutrient breakdown of the manure (%)
            "mass_applied": 1000,  # the amount of this manure applied at each application (kg/acre)
            "application_depth": 0,  # depth (cm) of application
            "surface_coverage": 80,  # % of the field covered by the application
            "application_years": [2000, 2004],  # The years on which the application occurs
            "relative_day": "more than 7 days after planting",  # the timing to apply, relative to planting event
            "specific_day": None,  # the calendar day on which to apply
            # Alternative method to specify application years (pattern-based, optional)
            "start_year": None,  # first application year
            "repeat": None,  # how many times should the application be repeated (after first) before skipping?
            "skip": None,  # how many years to skip before restarting the applications pattern?
            "cycles": None  # how many times should the entire application pattern repeat?
        }

        # Tillage
        """This tillage operation occurs every year on day 199"""
        first_tillage_specification = {
            "tillage_years": None,  # The years on which the tillage occurs
            "relative_day": "on a specific day",  # the timing to till, relative to planting event
            "specific_day": 199,  # the calendar day on which to till
            # Alternative method to specify tillage years (pattern-based, optional)
            "start_year": 2000,  # first tillage year
            "repeat": 9,  # how many times should the tillage be repeated (after first) before skipping?
            "skip": 0,  # how many years to skip before restarting the pattern?
            "cycles": 1,  # how many times should the entire pattern repeat?
            "method": "diskplow"  # the method by which the field was tilled (open-ended, or list of options?)
        }

        # Crops
        """this crop specification plants and harvests corn every 4 years"""
        first_crop_specification = {"species": "corn",  # species of the crop
                                    "planting_years": [2000, 2004, 2008, 2012],
                                    "planting_day": 120,
                                    # Alternative method to specify planting years (pattern-based, optional)
                                    "planting_start_year": None,  # first planting year
                                    "planting_repeat": None, # how many times should the planting be repeated (after first) before skipping?
                                    "planting_skip": None,  # how many years to skip before restarting the pattern?
                                    "planting_cycles": None,  # how many times should the entire pattern repeat?

                                    "harvest_years": [2000, 2004, 2008, 2012],
                                    "harvest_day": 300,
                                    # Alternative method to specify harvest years (pattern-based, optional)
                                    "harvest_start_year": None,  # first harvest year
                                    "harvest_repeat": None,
                                    # how many times should the harvest be repeated (after first) before skipping?
                                    "harvest_skip": None,  # how many years to skip before restarting the pattern?
                                    "harvest_cycles": None,  # how many times should the entire pattern repeat?
                                    }

        """this crop specification plants and alfalfa every 4 years (the year after corn) and harvests it three years
        after planting."""
        second_crop_specification = {"species": "alfalfa",  # crop species
                                     "planting_years": [2001, 2005, 2009],
                                     "planting_day": 135,  # day of year to plant
                                     # Alternative method to specify planting years (pattern-based, optional)
                                     "planting_start_year": None,  # first planting year
                                     "planting_repeat": None,
                                     # how many times should the planting be repeated (after first) before skipping?
                                     "planting_skip": None,  # how many years to skip before restarting the pattern?
                                     "planting_cycles": None,  # how many times should the entire pattern repeat?

                                     "harvest_years": [2003, 2007, 2011],  # years to harvest
                                     "harvest_day": 290,  # day of year to harvest
                                     # Alternative method to specify harvest years (pattern-based, optional)
                                     "harvest_start_year": None,  # first harvest year
                                     "harvest_repeat": None,
                                     # how many times should the harvest be repeated (after first) before skipping?
                                     "harvest_skip": None,  # how many years to skip before restarting the pattern?
                                     "harvest_cycles": None,  # how many times should the entire pattern repeat?
                                     }

        """this crop specification plants and harvests soybeans years in a row, skipping a year in between."""
        third_crop_specification = {"species": "soybean",
                                    "planting_years": [2001, 2002, 2003, 2005, 2006, 2007, 2009, 2010, 2011],
                                    "planting_day": 135,  # day of year to plant
                                    # Alternative method to specify planting years (pattern-based, optional)
                                    "planting_start_year": None,  # first planting year
                                    "planting_repeat": None,
                                    # how many times should the planting be repeated (after first) before skipping?
                                    "planting_skip": None,  # how many years to skip before restarting the pattern?
                                    "planting_cycles": None,  # how many times should the entire pattern repeat?

                                    "harvest_years": [2001, 2002, 2003, 2005, 2006, 2007, 2009, 2010, 2011],  # years to harvest
                                    "harvest_day": 320,  # day of year to harvest
                                    # Alternative method to specify harvest years (pattern-based, optional)
                                    "harvest_start_year": None,  # first harvest year
                                    "harvest_repeat": None,
                                    # how many times should the harvest be repeated (after first) before skipping?
                                    "harvest_skip": None,  # how many years to skip before restarting the pattern?
                                    "harvest_cycles": None,  # how many times should the entire pattern repeat?
                                    }


        # ---- Soil ----
        """Soil types will be very similar across large areas of land, so it is possible that many (or all) fields
        share the same soil type"""
        soil_specification = {
            "sample_latitude": 44.500003,  # decimal latitude for a sample of this soil type
            "sample_longitude": -89.5000009,  # decimal longitude for a sample of this soil type
            "soil_order": "mollisol",  # the soil Order
            # ... for simplicity, I'm not going to include all the soil attributes here. They look good. ...
            # ...
            "profile": {"layer_one": "...",  # layer attributes
                        "layer_two": "...",
                        "...": "..."}
        }



        # ---- Field Properties ----
        """A field is the highest-level entity (besides the farm). It can represent one of two real-world concepts:

            1. an single agricultural field. This field has a location and dimensions in space, it contains soil with 
            fixed starting conditions, crops are grown in it, and it undergoes management practices

            2. a collection of multiple agricultural fields that all experience IDENTICAL management practices. 
            This means that the same crops are planted and harvestd in the field at the same (approximate) time, 
            fertilizer and manure amendments occur at the same (approximate) time, etc. This type of 'field' 
            (a management unit) has a general location in space (e.g., the center of a farm), and a total land area 
            (i.e., the sum of the individual fields)
        """

        """this first field uses the soil spec, two fertilizer specs, oen tillage spec, 
        and uses as corn/alfalfa rotation"""
        first_field = {
            "ID": "field 1",  # an identifier so that we can keep track of this unique field/management unit
            "latitude": 44.500000,   # decimal latitude of this field
            "longitude": -89.5000000,  # decimal longitude of this field
            "area": 397.5,  # the land area of this field
            "slope": 12.0,  # the average slope (%) of the field
            "fertilizer_applications": [first_fert_specification, second_fert_specification],  # fertilizer
            "manure_applications": [first_manure_specification],  # manure
            "tillage": [first_tillage_specification],  # tillage
            "crop_specifications": [first_crop_specification, first_crop_specification],
            "soil": soil_specification
        }

        """this field uses the soil spec, one fertilizer spec, and no manure or tillage specs. a corn/soybean rotation
        is used."""
        second_field = {
            "ID": "Andrew the field",  # an identifier so that we can keep track of this unique field/management unit
            "latitude": 44.500001,  # decimal latitude of this field
            "longitude": -89.5000001,  # decimal longitude of this field
            "area": 187,  # the land area of this field
            "slope": 5.1,  # the average slope (%) of the field
            "fertilizer_applications": [first_fert_specification],  # fertilizer
            "manure_applications": None,  # manure
            "tillage": None,  # tillage
            "crop_specifications": [first_crop_specification, third_crop_specification],  # crops
            "soil": soil_specification
        }

        """the farm contains both fields"""
        farm = {"first_field": first_field,
                "second_field": second_field}

        return farm


print(CSInput.make_dictionaries())

