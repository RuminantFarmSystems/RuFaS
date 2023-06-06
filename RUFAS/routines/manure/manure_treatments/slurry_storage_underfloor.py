from RUFAS.routines.manure.manure_treatments.base_slurry_storage import BaseSlurryStorage


class SlurryStorageUnderfloor(BaseSlurryStorage):
    def __init__(self, weather, time, manure_treatment_config) -> None:
        """
        Call the parent class initializer and set the attributes.

        Parameters
        ----------
        weather : Weather
            A Weather object.
        time : Time
            A Time object.
        manure_treatment_config : ManureTreatmentConfig
            A ManureTreatmentConfig object containing the configuration data for the manure treatment system.

        """
        super().__init__(weather, time, manure_treatment_config)
        self.storage_time_period = self.config.storage_time_period
