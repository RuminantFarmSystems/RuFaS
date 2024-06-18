from RUFAS.routines.animal.animal_health.recovery import DiseaseRecovery
from RUFAS.routines.animal.animal_health.incidence import DiseaseIncidence
from RUFAS.routines.animal.animal_health.disease import Disease


class AnimalHealthReporter:
    # modeling after AnimalModuleReporter class - this could likely be folded into that if desired.
    @classmethod
    def report_total_disease_days(cls, disease: Disease) -> None:
        """Adds total animal-days of disease to Output Manager.

        Parameters
        ----------
        disease : Disease
            The disease being reported on.
        """
        pass

    @classmethod
    def report_disease_incidence(cls, incidence: DiseaseIncidence) -> None:
        """Adds disease-incidence data to Output Manager.

        Parameters
        ----------
        incidence : DiseaseIncidence
            The incidence data on the disease.
        """
        pass

    @classmethod
    def report_lost_milk_production(cls, disease: Disease, recovery: DiseaseRecovery) -> None:
        """Reports lost milk production due to disease to Output Manager.

        Parameters
        ----------
        disease : Disease
            The disease that caused the animal milk production loss.
        recovery : DiseaseRecovery
            Disease recovery effects (intermediate and long-term).
        """
        pass

    @classmethod
    def report_feed_efficiency_decreases(cls, disease: Disease, recovery: DiseaseRecovery) -> None:
        """Reports feed efficiency decreases due to disease to Output Manager.

        Parameters
        ----------
        disease : Disease
            The disease that caused the animal milk production loss.
        recovery : DiseaseRecovery
            Disease recovery effects (intermediate and long-term).
        """
        pass

    @classmethod
    def report_milk_co2_increases(cls, disease: Disease, recovery: DiseaseRecovery) -> None:
        """Reports increases in milk kgCO2/kgMilk due to disease to Output Manager.

        Parameters
        ----------
        disease : Disease
            The disease that caused the animal milk production loss.
        recovery : DiseaseRecovery
            Disease recovery effects (intermediate and long-term).
        """
        pass

    @classmethod
    def report_income_losses(cls) -> None:
        """Reports losses in income due to disease to Output Manager.

        """
        pass
