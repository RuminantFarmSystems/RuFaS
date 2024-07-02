from RUFAS.routines.animal.animal_health.animal_health_status import AnimalHealthStatus
from RUFAS.routines.animal.animal_health.disease import Disease
from RUFAS.time import Time
from RUFAS.routines.animal.animal_health.outcomes import DiseaseOutcomes


class AnimalHealth:
    def __init__(self):
        self.diseases: list[Disease] = []
        # create the list of diseases

    def daily_health_routine(self, animal_health_status: AnimalHealthStatus, time: Time):
        if animal_health_status.status == DiseaseOutcomes.REMAIN_DISEASED:
            Disease.immediate_effect()

        elif (
            not animal_health_status.status == DiseaseOutcomes.REMAIN_DISEASED
            and not animal_health_status.status == DiseaseOutcomes.RECOVERY
        ):
            for disease in self.diseases:
                animal_at_risk = disease.assess_disease_risk()
                if animal_at_risk:
                    incidence_rate = disease.calculate_incidence_rate()
                    will_develop_disease = disease.will_develop_disease(incidence_rate)
                    if will_develop_disease:
                        disease_start_date = disease.determine_at_risk_period()
                        animal_health_status.disease_start_date = disease_start_date
        elif animal_health_status.status == DiseaseOutcomes.RECOVERY:
            if animal_health_status:  # some way to determine if the animal is in the same life stage when it recovered
                Disease.intermediate_effect()
            else:
                Disease.lasting_effect()
