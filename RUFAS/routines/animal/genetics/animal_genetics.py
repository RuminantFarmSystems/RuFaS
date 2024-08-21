from RUFAS.input_manager import InputManager
from RUFAS.time import Time

PTA_increase_lookup_table = {2020: 369, 2015: 253, 2010: 140, 2005: 107, 2000: 0}


class AnimalGenetics:
    def __init__(self) -> None:
        im = InputManager()
        net_merit_HO = im.get_data("animal_net_merit")
        top_listing_semen_HO = im.get_data("animal_top_listing_semen")
        self.net_merit = {
            "HO": {
                net_merit_HO["year_month"][i]: {"average": net_merit_HO["average"][i], "std": net_merit_HO["std"][i]}
                for i in range(len(net_merit_HO["year_month"]))
            }
        }
        self.adjust_input_values()
        # self.top_semen = {
        #     "HO": {
        #
        #     }
        # }

    def adjust_input_values(self) -> None:
        for year_month in self.net_merit["HO"].keys():
            print(year_month)
            year = int(year_month[:4])
            print(all(PTA_increase_lookup_table[i] for i in PTA_increase_lookup_table.keys() if year >= i))
        pass

    def assign_net_merit_value_to_animals_entering_herd(self, birth_date: str) -> float:
        pass
        return 0.0

    def assign_net_merit_value_to_newborn_calf(self, time: Time, dam_net_merit_value: float) -> float:
        pass
        return 0.0
