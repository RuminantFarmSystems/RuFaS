from RUFAS.biophysical.animal.animal_health.animal_health_status import AnimalHealthStatus
from RUFAS.biophysical.animal.animal_health.disease import Disease
from RUFAS.biophysical.animal.animal_health.outcomes import DiseaseOutcomes
from RUFAS.rufas_time import RufasTime


class AnimalHealth:
    def __init__(self) -> None:
        self.diseases: list[Disease] = []
        # create the list of diseases

    def daily_health_routine(self, animal_health_status: AnimalHealthStatus, time: RufasTime) -> None:
        if animal_health_status.status == DiseaseOutcomes.DISEASED:
            # Disease.immediate_effect()
            pass

        elif animal_health_status.status == DiseaseOutcomes.IN_RECOVERY:
            if animal_health_status:  # some way to determine if the animal is in the same life stage when it recovered
                # Disease.intermediate_effect()
                pass
            else:
                # Disease.lasting_effect()
                pass
        else:
            for disease in self.diseases:
                animal_at_risk = disease.assess_disease_risk(time, animal_health_status)
                if animal_at_risk:
                    incidence_rate = disease.calculate_incidence_rate()
                    will_develop_disease = disease.will_develop_disease(incidence_rate)
                    if will_develop_disease:
                        disease_start_date = disease.determine_at_risk_period(animal_health_status)
                        animal_health_status.disease_start_date = disease_start_date
