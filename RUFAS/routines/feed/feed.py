import math
from typing import Any, Dict, List, Union

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.ration.user_defined_ration import UserDefinedRationManager as UserDefinedRationManager
from RUFAS.units import MeasurementUnits

from RUFAS.routines.feed import carbon_loss, nitrogen_loss, protein_degradation
from RUFAS.routines.feed.feed_typed_dicts import PurchasedFeedTypedDict
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination

udrm = UserDefinedRationManager()


def daily_feed_routine(feed, fields, animal_manager):
    """
    Description:
        Executes the functions that run the daily feed routines for both storage
        and feed management.

    Args:
        feed: an instance of the Feed object
        fields: an instance of the Field object (contains harvest information)
        animal_manager: an instance of the AnimalManager object
    """

    # feed storage routines to be run daily
    feed.daily_feed_storage(fields)

    # feed management routines to be run daily
    feed.daily_feed_management(animal_manager)


def annual_feed_routine(feed):
    feed.reset_feed_data()


class Feed:
    def __init__(self, data: PurchasedFeedTypedDict):
        """
        Description:
            Stores the information for the feeds managed by the farm, and the methods
            for storage.

        Args:
            data: the feed information from the input JSON file
        """
        self.om = OutputManager()
        self.im = InputManager()
        self.nutrient_standard = self.im.get_data("config.nutrient_standard")
        self.nutrient_table = "NASEM_Comp" if self.nutrient_standard == "NASEM" else "NRC_Comp"

        self.all_feed_units = self._retrieve_data(data_source="user_feeds", var_names=["rufas_id", "Name", "units"])

        purchased_feeds_list = [feed_item["purchased_feed"] for feed_item in data["purchased_feeds"]]
        purchased_feed_costs = {
            str(feed_item["purchased_feed"]): feed_item["purchased_feed_cost"] for feed_item in data["purchased_feeds"]
        }

        self.farm_grown_feeds = data["farm_grown_feeds"]
        self.purchased_feeds = self.get_quality_specific_purchased_feed_ids(purchased_feeds_list)

        self.input_feed_combinations = {
            AnimalCombination.CALF: set(self.get_quality_specific_purchased_feed_ids(data["calf_feeds"])),
            AnimalCombination.GROWING: set(self.get_quality_specific_purchased_feed_ids(data["growing_feeds"])),
            AnimalCombination.CLOSE_UP: set(self.get_quality_specific_purchased_feed_ids(data["close_up_feeds"])),
            AnimalCombination.GROWING_AND_CLOSE_UP: set(
                self.get_quality_specific_purchased_feed_ids(data["growing_feeds"])
            )
            | set(self.get_quality_specific_purchased_feed_ids(data["close_up_feeds"])),
            AnimalCombination.LAC_COW: set(self.get_quality_specific_purchased_feed_ids(data["lac_cow_feeds"])),
        }

        self.all_feed_ids = self.get_all_feed_units(purchased_feeds_list, data["farm_grown_feeds"])

        # dictionary of nutrients needed for this run
        # initially, this only contains information for purchased feeds as none
        # of the farm_grown_feeds have been harvested yet
        self.available_feeds = self.get_nutrient_vals(self.purchased_feeds, False)
        self.calf_feeds = self.get_calf_feeds()
        # setting up the feed costs based on the input
        self.feed_costs = purchased_feed_costs
        self.feed_costs = self.get_quality_specific_feed_costs(purchased_feeds_list)

        # The nutrient requirements used in the ration calculations.
        self.nutrient_rqmts = ["FU", "RU", "ME_DM", "RDP_DM", "RUP_DM"]

        # Storage receptacles managed by the feed module
        self.storage_options = {}

        for count, storage_option in enumerate(data["storage_options"]):
            self.storage_options[f"storage_option_{count}"] = self.Storage(storage_option)

        self.available_storage = dict(self.storage_options)
        self.standard_storage_count = 0

        # Summary variables tracked for output
        self.C = 0.0
        self.N = 0.0
        self.P = 0.0
        self.DM = 0.0
        self.NDF = 0.0
        self.CP = 0.0
        self.NPN = 0.0

        self.C_loss = 0.0
        self.CP_loss = 0.0

        # a list of storage objects with new crops
        self.new_forages = []

        # Loading in user-defined ration values
        self.user_defined_ration_percentages = data["user_defined_ration_percentages"]
        target_user_defined_ration_percentage_sum = 100.0
        user_defined_ration_percentage_sum_tolerance = 0.01
        info_map = {
            "class": self.__class__.__name__,
            "function": "__init__",
        }
        udrm.calf_ration = {
            str(dict["feed_type"]): dict["ration_percentage"] for dict in self.user_defined_ration_percentages["calf"]
        }

        if not math.isclose(
            sum(udrm.calf_ration.values()),
            target_user_defined_ration_percentage_sum,
            abs_tol=user_defined_ration_percentage_sum_tolerance,
        ):
            self.om.add_warning(
                "User defined calf_ration percentages do not sum to 100",
                f"User defined calf_ration sums to {sum(udrm.calf_ration.values())}",
                info_map,
            )

        udrm.growing_ration = {
            str(dict["feed_type"]): dict["ration_percentage"]
            for dict in self.user_defined_ration_percentages["growing"]
        }
        if not math.isclose(
            sum(udrm.growing_ration.values()),
            target_user_defined_ration_percentage_sum,
            abs_tol=user_defined_ration_percentage_sum_tolerance,
        ):
            self.om.add_warning(
                "User defined growing_ration percentages do not sum to 100",
                f"User defined growing_ration sums to {sum(udrm.growing_ration.values())}",
                info_map,
            )

        udrm.close_up_ration = {
            str(dict["feed_type"]): dict["ration_percentage"]
            for dict in self.user_defined_ration_percentages["close_up"]
        }
        if not math.isclose(
            sum(udrm.close_up_ration.values()),
            target_user_defined_ration_percentage_sum,
            abs_tol=user_defined_ration_percentage_sum_tolerance,
        ):
            self.om.add_warning(
                "User defined close_up_ration percentages do not sum to 100",
                f"User defined close_up_ration sums to {sum(udrm.close_up_ration.values())}",
                info_map,
            )

        udrm.lactating_cow_ration = {
            str(dict["feed_type"]): dict["ration_percentage"]
            for dict in self.user_defined_ration_percentages["lac_cow"]
        }
        if not math.isclose(
            sum(udrm.lactating_cow_ration.values()),
            target_user_defined_ration_percentage_sum,
            abs_tol=user_defined_ration_percentage_sum_tolerance,
        ):
            self.om.add_warning(
                "User defined lactating_cow_ration percentages do not sum to 100",
                f"User defined lactating_cow_ration sums to {sum(udrm.lactating_cow_ration.values())}",
                info_map,
            )

        udrm.tolerance = self.user_defined_ration_percentages["tolerance"]

        udrm.milk_reduction_maximum = self.user_defined_ration_percentages["milk_reduction_maximum"]

    def summarize_feed_storage(self):
        """
        Description:
            Summarize nutrients and losses over the managed storage receptacles
        """

        for storage in self.storage_options.values():
            self.C += storage.C
            self.N += storage.C
            self.P += storage.C
            self.DM += storage.C
            self.CP += storage.C

            self.C_loss += storage.C_loss
            self.CP_loss += storage.CP_loss

            self.NPN += storage.NPN
            info_map = {
                "class": self.__class__.__name__,
                "function": self.summarize_feed_storage.__name__,
                "storage_type": storage,
            }
            nutrient_dict_units = {
                "carbon": MeasurementUnits.KILOGRAMS,
                "nitrogen": MeasurementUnits.KILOGRAMS,
                "phosphorus": MeasurementUnits.KILOGRAMS,
                "dry_matter": MeasurementUnits.KILOGRAMS,
                "crude_protein": MeasurementUnits.KILOGRAMS,
                "carbon_loss": MeasurementUnits.KILOGRAMS,
                "crude_protein_loss": MeasurementUnits.KILOGRAMS,
            }
            nutrients_dict = {}
            nutrients_dict["carbon"] = self.C
            nutrients_dict["nitrogen"] = self.N
            nutrients_dict["phosphorus"] = self.P
            nutrients_dict["dry_matter"] = self.DM
            nutrients_dict["crude_protein"] = self.CP
            nutrients_dict["carbon_loss"] = self.C_loss
            nutrients_dict["crude_protein_loss"] = self.CP_loss
            self.om.add_variable("nutrients_summary", nutrients_dict, dict(info_map, **{"units": nutrient_dict_units}))

    class Storage:
        def __init__(self, data):
            """
            Description:
                A subclass of feed storage specifying a single storage receptacle.

            Args:
                data: a dictionary containing information to define the storage
                    receptacle
            """

            self.storage_type = data["storage_type"]
            self.moisture = data["moisture"]
            self.additive = data["additive"]
            self.packing_density = data["packing_density"]

            self.inoculation = data["inoculation"]
            self.bunk_type = data["bunk_type"]
            self.ventilation = data["ventilation"]
            self.removal_rate = data["removal_rate"]

            self.DM = data["initial_dry_matter"]

            self.crop_name = "null"

            self.storage_quality = "null"

            self.storage = True

            self.CP_percent = 0.0
            self.C_percent = 0

            self.feed_id = "null"
            # string representation of the feed key to available feeds
            self.feed_key = "null"
            self.forage_quality = "null"

            self.DMI_forage_max = {
                "calves": 0,
                "heiferIs": 0,
                "heiferIIs": 0,
                "heiferIIIs": 0,
                "dry_cows": 0,
                "lactating_cows": 0,
            }

            self.days_since_feedout = -1
            self.req_inv = {}
            self.cow_days = {}
            self.inclusion_rate_est = {}
            self.inclusion_pct = {}
            self.animal_avg_BW = 0

            self.C_percent = 0.0
            self.DM_percent = 0.0
            self.NDF_percent = 0.0

            self.NDF = 0.0
            self.C = 0.0
            self.N = 0.0
            self.P = 0.0

            self.C_harvest_gas = 0.0
            self.C_harvest_particle = 0.0

            self.C_storage_gas = 0.0
            self.C_storage_leachate = 0.0

            self.C_feed_out_gas = 0.0
            self.C_feed_out_particle = 0.0

            self.C_loss = 0.0

            self.CP = 0.0

            self.CP_gas = 0.0
            self.CP_leachate = 0.0
            self.CP_loss = 0.0

            self.NPN = 0.0

            self.C_harvest_gas_percent = 0.0
            self.C_harvest_particle_percent = 0.0

            self.C_storage_gas_percent = 0.0
            self.C_storage_leachate_percent = 0.0

            self.C_feed_out_gas_percent = 0.0
            self.C_feed_out_particle_percent = 0.0

            self.CP_gas_percent = 0.0
            self.CP_leachate_percent = 0.0
            self.NPN_min_percent = 0.0

        def calibrate_storage(self, crop):  # noqa
            """
            Description:
                Calibrates the feed storage loss model to the crop being stored in the receptacle.
                Based on information provided by Kevin Painke-Buisse of the DFRC 2019
                "pseudocode_feed" F.1.4

            Args:
                crop: The crop to be stored
            """

            self.crop_name = crop.crop_name
            self.storage_quality = crop.harvest_quality
            self.feed_id = crop.feed_id

            if self.crop_name == "corn":
                self.storage = True
                self.CP_percent = 0.08
                self.C_percent = 0.58
                if self.moisture == "direct_cut":
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0.02
                    self.NPN_min_percent = 0.50
                    self.C_harvest_gas_percent = 0.01
                    self.C_harvest_particle_percent = 0.005
                    self.C_storage_gas_percent = 0.08
                    self.C_storage_leachate_percent = 0.02
                    self.C_feed_out_gas_percent = 0.02
                    self.C_feed_out_particle_percent = 0
                elif self.moisture == "wilted":
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0
                    self.NPN_min_percent = 0.45
                    self.C_harvest_gas_percent = 0.015
                    self.C_harvest_particle_percent = 0.005
                    self.C_storage_gas_percent = 0.07
                    self.C_storage_leachate_percent = 0
                    self.C_feed_out_gas_percent = 0.02
                    self.C_feed_out_particle_percent = 0
                elif self.moisture == "baleage":
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0
                    self.NPN_min_percent = 0.40
                    self.C_harvest_gas_percent = 0.015
                    self.C_harvest_particle_percent = 0.005
                    self.C_storage_gas_percent = 0.12
                    self.C_storage_leachate_percent = 0
                    self.C_feed_out_gas_percent = 0.02
                    self.C_feed_out_particle_percent = 0

            elif self.crop_name == "alfalfa":
                self.storage = True
                self.C_percent = 0.58
                if self.moisture == "direct_cut":
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0.025
                    self.NPN_min_percent = 0.40
                    self.C_harvest_gas_percent = 0.03
                    self.C_harvest_particle_percent = 0
                    self.C_storage_gas_percent = 0.095
                    self.C_storage_leachate_percent = 0.025
                    self.C_feed_out_gas_percent = 0.02
                    self.C_feed_out_particle_percent = 0
                elif self.moisture == "wilted":
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0
                    self.NPN_min_percent = 0.40
                    self.C_harvest_gas_percent = 0.035
                    self.C_harvest_particle_percent = 0.015
                    self.C_storage_gas_percent = 0.09
                    self.C_storage_leachate_percent = 0
                    self.C_feed_out_gas_percent = 0.02
                    self.C_feed_out_particle_percent = 0
                elif self.moisture == "haylage":
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0
                    self.NPN_min_percent = 0.35
                    self.C_harvest_gas_percent = 0.045
                    self.C_harvest_particle_percent = 0.025
                    self.C_storage_gas_percent = 0.07
                    self.C_storage_leachate_percent = 0
                    self.C_feed_out_gas_percent = 0.02
                    self.C_feed_out_particle_percent = 0
                elif self.moisture == "moist_hay":
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0
                    self.NPN_min_percent = 0.30
                    self.C_harvest_gas_percent = 0.07
                    self.C_harvest_particle_percent = 0.10
                    self.C_storage_gas_percent = 0.03
                    self.C_storage_leachate_percent = 0
                    self.C_feed_out_gas_percent = 0
                    self.C_feed_out_particle_percent = 0.01
                elif self.moisture == "dry_hay":
                    self.CP_gas_percent = 0
                    self.CP_leachate_percent = 0
                    self.NPN_min_percent = 0.20
                    self.C_harvest_gas_percent = 0.07
                    self.C_harvest_particle_percent = 0.16
                    self.C_storage_gas_percent = 0.02
                    self.C_storage_leachate_percent = 0
                    self.C_feed_out_gas_percent = 0
                    self.C_feed_out_particle_percent = 0.01

        def forage_quality_assessment(self, feed):
            """
            Description:
                Updates values in the storage object relevant to the quality of
                the feed utilizing feed database functions

            Args:
                feed: an instance of class Feed
            """
            self.feed_key = str(self.feed_id) + "g"
            self.forage_quality = "null"

        def store_crop(self, feed, crop):
            """
            Description:
                Helper method for "storing" the specified crop
                Updates mineral components and losses as a crop is stored.
                "pseudocode_feed" F.1.1

            Args:
                feed: instance of the Feed class
                crop: the crop to be stored,
                    an instance of the family of classes under BaseCrop defined in the crop_types folder
            """

            if self.storage:
                if self.DM == 0:
                    # forage to be fed out 30 days after harvest for new yield
                    # if there is already forage in the receptacle days_since_feedout
                    # is not reset
                    self.days_since_feedout = -30
                self.feed_id = crop.raw_id
                self.DM += crop.yield_actual * crop.DM_harvest_percent
                self.NDF += crop.NDF_yield
                self.N += crop.N_yield
                self.P += crop.P_yield
                self.DM_percent = self.DM / crop.yield_actual
                self.NDF_percent = self.NDF / crop.yield_actual
                self.C += crop.yield_actual * self.C_percent

                # "pseudocode_feed" F.1.2
                self.CP += 6.25 * self.N / self.DM

                # Reset harvest quality for the crop
                crop.harvest_quality = ""

            if self not in feed.new_forages:
                feed.new_forages.append(self)

        def calculate_losses(self):
            """
            Description:
                Calculates mineral losses for the storage method once all crops are stored
                "pseudocode_feed" F.1.3
            """
            carbon_loss.update_all(self)
            nitrogen_loss.update_all(self)
            protein_degradation.update_all()

        def reset_storage(self):
            """
            Description:
                Storage class method resets receptacle to initial settings.
            """
            reset_data = {
                "storage_type": self.storage_type,
                "moisture": self.moisture,
                "additive": self.additive,
                "packing_density": self.packing_density,
                "inoculation": self.inoculation,
                "bunk_type": self.bunk_type,
                "ventilation": self.ventilation,
                "removal_rate": self.removal_rate,
                "initial_dry_matter": 0,
            }

            self.__init__(reset_data)

    @staticmethod
    def required_inventory(storage, animal_manager):
        """
        Description:
            Computes the required inventory necessary across all animals for a
            given forage based on the count of the animals, the body weight,
            and inclusion percent associated with the input forage. This class
            method for the feed class updates feed class variables along with class
            variables associated with the input storage object. Each calculation
            has a reference to the respective calculation in the pseudocode

        Args:
            storage: a storage object that contains forage being assessed
            animal_manager: the class object Animal Manager which tracks
            the state of the animals
        """
        # animals = dictionary with animals as keys and animal objects as values
        animals = {
            "calves": animal_manager.calves,
            "heiferIs": animal_manager.heiferIs,
            "heiferIIs": animal_manager.heiferIIs,
            "heiferIIIs": animal_manager.heiferIIIs,
        }
        lactating_cows = []
        dry_cows = []
        for cow in animal_manager.cows:
            if cow.milking:
                lactating_cows.append(cow)
            else:
                dry_cows.append(cow)
        animals["dry_cows"] = dry_cows
        animals["lactating_cows"] = lactating_cows
        # avg_BW = Average bodyweight of specified Animal Class (kg)
        avg_BW = {}
        # animal_class_size_avg = amount of animals on the farm of that type
        animal_class_size_avg = {}
        for key, val in animals.items():
            BW = 0
            for animal in val:
                BW += animal.body_weight
            animal_class_size_avg[key] = len(val)
            if len(val) > 0:
                avg_BW[key] = BW / len(val)
            else:
                avg_BW[key] = 0
        # inclusion_pct = recommended inclusion rate as a percentage of
        # bodyweight for Animal Class
        # (currently not unique across different feeds)
        inclusion_pct = {
            "calves": 2.0,
            "heiferIs": 2.0,
            "heiferIIs": 2.0,
            "heiferIIIs": 2.0,
            "dry_cows": 1.7,
            "lactating_cows": 2.0,
        }
        # inclusion_rate_est = Estimated inclusion rate to meet Animal Class
        # requirements (kg DM)
        # [F.2.A.5]
        inclusion_rate_est = {}
        for animal, val in inclusion_pct.items():
            inclusion_rate_est[animal] = (val / 100) * avg_BW[animal]
        # days_remaining = the number of days until the expected start date for
        # feedout from the next harvest
        days_remaining = 365 - storage.days_since_feedout
        # cow_days = total number of feeding days until next year’s forage
        # begins to be fed out
        cow_days = {
            "calves": 0,
            "heiferIs": 0,
            "heiferIIs": 0,
            "heiferIIIs": 0,
            "dry_cows": 0,
            "lactating_cows": 0,
        }
        for animal in cow_days:
            cow_days[animal] = animal_class_size_avg[animal] * days_remaining
        # req_inv = required inventory for corresponding animal class (kg DM)
        req_inv = {
            "calves": 0,
            "heiferIs": 0,
            "heiferIIs": 0,
            "heiferIIIs": 0,
            "dry_cows": 0,
            "lactating_cows": 0,
        }
        # [F.2.A.4]
        for animal, val in cow_days.items():
            req_inv[animal] = inclusion_rate_est[animal] * val
        # updating class variables for input storage object input
        storage.req_inv = req_inv
        storage.cow_days = cow_days
        storage.inclusion_rate_est = inclusion_rate_est
        storage.inclusion_pct = inclusion_pct
        storage.animal_avg_BW = avg_BW

    @staticmethod
    def forage_inventory_plan(storage):  # noqa
        """
        Description:
            Assess farm grown forage stocks and plan maximum intake of each
            forage to ensure there is enough forage to last a FULL YEAR.
            Forage inventory is conducted at least 1x/year after harvest and
            then at a user specified number of times. This function calculates
            those values and stores it in the input storage object. Each calculation
            has a reference to its respective calculation in the pseudocode

        Args:
            storage: the storage object containing the forage being assessed
        """

        # HIGH QUALITY FORAGE
        # Calculating DMI for Lactating Cows only
        # ------------------------------
        if storage.forage_quality == "immature" or storage.forage_quality == "mid_maturity":
            # [F.2.A.6]
            if 1.1 * storage.req_inv["lactating_cows"] >= storage.DM:
                storage.DMI_forage_max["lactating_cows"] = storage.DM / storage.cow_days["lactating_cows"]
            else:
                storage.DMI_forage_max["lactating_cows"] = 1.1 * storage.inclusion_rate_est["lactating_cows"]

        # LOW QUALITY FORAGE
        # Calculating DMI for all EXCEPT Lactating Cows
        # ------------------------------
        elif storage.forage_quality == "mature":
            tot_req_inv_non_lactating_cows = 0
            # updating required inventory for non lactating cows
            for animal in storage.req_inv:
                if animal != "lactating_cows":
                    tot_req_inv_non_lactating_cows += storage.req_inv[animal]
            # Assigning DMI when there is sufficient inventory
            # [F.2.A.9]
            if tot_req_inv_non_lactating_cows <= storage.DM:
                storage.DMI_forage_max = storage.inclusion_rate_est
                storage.DMI_forage_max["lactating_cows"] = 0
            # updating inclusion rate estimate until inventory is sufficient to
            # satisfy the newly calculated inclusion rate estimate
            # [F.2.A.10]
            else:
                while round(tot_req_inv_non_lactating_cows) > round(storage.DM):
                    inv_delta = tot_req_inv_non_lactating_cows - storage.DM
                    denominator = 0

                    for animal, val in storage.animal_avg_BW.items():
                        if animal != "lactating_cows":
                            denominator += val * storage.cow_days[animal]

                    inclusion_pct_delta = inv_delta / denominator

                    for animal, val in storage.inclusion_rate_est.items():
                        storage.inclusion_pct[animal] = (
                            max(
                                storage.inclusion_pct[animal] / 100 - inclusion_pct_delta,
                                0,
                            )
                            * 100
                        )
                        storage.inclusion_rate_est[animal] = (
                            storage.inclusion_pct[animal] / 100
                        ) * storage.animal_avg_BW[animal]
                        storage.req_inv[animal] = storage.inclusion_rate_est[animal] * storage.cow_days[animal]
                    tot_req_inv_non_lactating_cows = 0

                    for animal in storage.req_inv:
                        if animal != "lactating_cows":
                            tot_req_inv_non_lactating_cows += storage.req_inv[animal]
                # booleans to check if new calculated inclusion rate > 0
                if tot_req_inv_non_lactating_cows == 0:
                    tot_cow_days = sum(storage.cow_days.values()) - storage.cow_days["lactating_cows"]
                    for animal, val in storage.cow_days.items():
                        storage.DMI_forage_max = ((val / tot_cow_days) * storage.DM) / val
                else:
                    storage.DMI_forage_max = storage.inclusion_rate_est
                storage.DMI_forage_max["lactating_cows"] = 0

        # NO QUALITY ASSESSMENT
        # Calculating DMI for all animal classes
        # -----------------------------
        else:
            # calculating total required inventory across all animal classes
            tot_req_inv = sum(storage.req_inv.values())
            # assigning DMI when there is sufficient inventory
            # [F.2.A.7]
            if tot_req_inv <= storage.DM:
                tot_req_inv_non_lactating_cows = 0

                for animal, val in storage.DMI_forage_max.items():
                    if animal != "lactating_cows":
                        storage.DMI_forage_max[animal] = storage.inclusion_rate_est[animal]
                        tot_req_inv_non_lactating_cows += val

                available_forage = storage.DM - tot_req_inv_non_lactating_cows
                if storage.cow_days["lactating_cows"] > 0:
                    storage.DMI_forage_max["lactating_cows"] = available_forage / storage.cow_days["lactating_cows"]
            # updating inclusion rate estimate until inventory is sufficient to
            # satisfy that newly calculated inclusion rate estimate
            # [F.2.A.8]
            else:
                while round(tot_req_inv) > round(storage.DM):
                    inv_delta = tot_req_inv - storage.DM
                    denominator = 0
                    for animal, val in storage.animal_avg_BW.items():
                        if animal != "lactating_cows":
                            denominator += val * storage.cow_days[animal]

                    inclusion_pct_delta = inv_delta / denominator
                    for animal, val in storage.inclusion_rate_est.items():
                        storage.inclusion_pct[animal] = (
                            max(
                                storage.inclusion_pct[animal] / 100 - inclusion_pct_delta,
                                0,
                            )
                            * 100
                        )
                        storage.inclusion_rate_est[animal] = (
                            storage.inclusion_pct[animal] / 100
                        ) * storage.animal_avg_BW[animal]
                        storage.req_inv[animal] = storage.inclusion_rate_est[animal] * storage.cow_days[animal]

                    tot_req_inv = sum(storage.req_inv.values())

                tot_req_inv_non_lactating_cows = 0
                for animal in storage.DMI_forage_max:
                    if animal != "lactating_cows":
                        storage.DMI_forage_max[animal] = storage.inclusion_rate_est[animal]
                        tot_req_inv_non_lactating_cows += storage.inclusion_rate_est[animal]

                available_forage = storage.DM - tot_req_inv_non_lactating_cows
                if storage.cow_days["lactating_cows"] > 0:
                    storage.DMI_forage_max["lactating_cows"] = available_forage / storage.cow_days["lactating_cows"]

    def daily_feed_storage(self, fields):  # noqa
        """
        Description:
            Executes daily routines relating to crop and feed storage, which
            handles newly harvested crops.Yield is stored at harvest in available
            storage grouped by crop type and quality. Once used, that storage
            receptacle is removed from the list of available storage. If
            insufficient storage is specified, a "standard" storage receptacle
            is generated.

        Args:
            fields : an instance of the Field object (contains harvest information)
        """
        # aggregate crop yield across fields
        return

        for field in fields.fields.values():
            name = list(field.crop.current_crop.keys())[0]
            crop = field.crop.current_crop[name]
            # there is forage to be stored
            if crop.yield_actual != 0:
                stored = False
                # search for matching storage profile
                for storage in self.available_storage.values():
                    if (
                        storage.feed_id == crop.feed_id
                        and storage.storage is True
                        and storage.storage_quality == crop.harvest_quality
                        and not stored
                    ):
                        storage.store_crop(self, crop)
                        if storage not in self.new_forages:
                            self.new_forages.append(storage)
                        stored = True

                # search for available, empty storage
                if not stored:
                    for storage in self.available_storage.values():
                        if storage.DM == 0 and not stored:
                            storage.calibrate_storage(crop)
                            storage.store_crop(self, crop)
                            if storage not in self.new_forages:
                                self.new_forages.append(storage)
                            stored = True

                # generate standard storage
                if not stored:
                    if len(self.available_storage) == 0:
                        standard_data = {
                            "storage_type": "bag",
                            "moisture": "direct_cut",
                            "additive": "preservative",
                            "packing_density": 200,
                            "inoculation": "heterofermentative",
                            "bunk_type": "open_floor",
                            "ventilation": True,
                            "removal_rate": 6,
                            "initial_dry_matter": 0,
                        }
                        standard_name = "standard_storage_" + str(self.standard_storage_count)
                        self.available_storage[standard_name] = self.Storage(standard_data)
                        self.storage_options[standard_name] = self.available_storage[standard_name]

                        self.standard_storage_count += 1

                    storage_name, storage = self.available_storage.popitem()
                    self.storage_options[storage_name].calibrate_storage(crop)
                    self.storage_options[storage_name].store_crop(self, crop)
                    if storage not in self.new_forages:
                        self.new_forages.append(storage)

        # calculate losses and update storage options after crop allocation
        for storage_name, storage in self.storage_options.items():
            if storage_name in self.available_storage and storage.DM != 0:
                storage.calculate_losses()
                self.available_storage.pop(storage_name)

            self.summarize_feed_storage()

    def daily_feed_management(self, animal_manager):  # noqa
        """
        Description:
            Executes daily routines relating to feed management, specifically a
            daily feedout process and checking for new forages that need an
            inventory plan. If the list new_forages contains a forage which
            had been harvested at least 30 days ago, forage_inv_plan will be
            called.

        Args:
            animal_manager: The state of the AnimalManager class object
        """
        # Daily feedout for silos with farm grown forages in them per pen based
        # on ration formulated
        feeds_fed = []
        for key, silo in self.storage_options.items():
            if silo.days_since_feedout >= 0 and silo.DM > 0:
                for pen in animal_manager.all_pens:
                    if silo.feed_key in pen.ration and silo.feed_key not in feeds_fed:
                        if (silo.DM - pen.ration[silo.feed_key]) > 0:
                            silo.DM -= pen.ration[silo.feed_key]
                        else:
                            silo.DM = 0
                            silo.reset_storage()
                            self.available_storage[key] = silo
                        break
                feeds_fed.append(silo.feed_key)
                silo.days_since_feedout += 1
            elif silo not in self.new_forages and silo.DM > 0:
                silo.days_since_feedout += 1
        # inventory plan for new forages
        # if it is the day before the ration interval will be calculated
        ration_interval = (
            (animal_manager.simulation_day + 1) % animal_manager.formulation_interval
        ) == 1 or animal_manager.formulation_interval == 1
        for silo in self.new_forages:
            if silo.days_since_feedout >= -1 and ration_interval and silo.feed_id != "null":
                silo.forage_quality_assessment(self)
                self.required_inventory(silo, animal_manager)
                self.forage_inventory_plan(silo)
                self.add_to_available_feeds([silo.feed_id], [silo.DM_percent], [silo.NDF_percent])
                self.update_available_feed(silo.feed_key, "limit", silo.DMI_forage_max)
                silo.days_since_feedout += 1
                self.new_forages.pop(self.new_forages.index(silo))
            else:
                silo.days_since_feedout += 1
        # yearly reset of silos
        # When ration formulation is in, the silos will automatically be fed out
        for key, silo in self.storage_options.items():
            if silo.days_since_feedout > 365:
                silo.reset_storage()
                self.available_storage[key] = silo

    def reset_feed_data(self):
        """
        Description:
            Resets the accumulated data so they can be interpreted as annual sums.
            Option to reset feed storage model entirely each year.
        """

        self.C = 0.0
        self.N = 0.0
        self.P = 0.0
        self.DM = 0.0
        self.NDF = 0.0
        self.CP = 0.0
        self.NPN = 0.0

        self.C_loss = 0.0
        self.CP_loss = 0.0

    # The functions below are Feed class functions that provide utilization of
    # the feed database
    def get_all_feed_units(self, purchased_feeds, grown_feeds):
        """
        Description:
            Constructs and returns a dictionary of where the keys are the feed IDs
            and the values are dictionaries containing the name and the units of
            the feed.

        Args:
            purchased_feeds: the list of entries (ints) of feeds that are
                purchased
            grown_feeds: the list of entries (ints) of feeds that will be grown

        Returns:
            a dictionary where the keys are the feed IDs and the values are
            dictionaries with feed information:
            - if the feed is purchased, ID is the string form of the ID
            (e.g. '2')
            - if the feed is grown, ID is the string form of the ID plus 'g'
            (e.g. '8g')
            - feed name is as it is in the user_feeds table
            - units is the string representing the units for the feed
            (e.g. 'kg')
        """
        dict_list = self.all_feed_units

        all_feed_info = {
            str(result["rufas_id"]): {"Name": result["Name"], "units": result["units"]} for result in dict_list
        }

        purchased_mapping_ids = self.get_quality_specific_purchased_feed_ids(purchased_feeds)

        purchased_mapping = {}
        for id in range(len(purchased_feeds)):
            purchased_mapping.update({str(purchased_feeds[id]): str(purchased_mapping_ids[id])})

        grown_feeds_mapping = {str(feed): str(feed) + "g" for feed in grown_feeds}

        all_feeds_mapping = purchased_mapping.copy()
        all_feeds_mapping.update(grown_feeds_mapping)

        for entry in all_feeds_mapping:
            if not entry == all_feeds_mapping[entry]:
                all_feed_info.update({all_feeds_mapping[entry]: all_feed_info[entry]})
                all_feed_info[all_feeds_mapping[entry]] = all_feed_info.pop(entry)

        return all_feed_info

    def get_quality_specific_purchased_feed_ids(self, entries: Union[int, List[int]]) -> List[int]:
        """
        Description:
            Constructs and returns a dictionary of the purchased feed IDs based on
            whether the quality of each feed can be determined at harvest.

        Args:
            entries: the purchased feed entries

        Returns:
            a dictionary where the keys are the feed entries and the keys are
            the feed IDs that can be used to find nutrient values in
            the nutrients table
        """
        if isinstance(entries, int):
            entry_list = [entries]
        else:
            entry_list = entries

        purchased_feed_ids: List[int] = []
        for entry in entry_list:
            purchased_feed_ids.append(entry)
        return purchased_feed_ids

    def get_quality_specific_feed_costs(self, input_feed_ids: List[int]) -> Dict[str, float]:
        """
        Returns an updated version of the purchased feed costs dictionary.
        A purchased feed id key will be updated if it is in the list of entries
        split by mid-maturity.
        Args:
            input_feed_ids: A list of purchased feed ids.
        Returns:
            A dictionary that stores key-value pairs, where the keys are
            purchased feed ids (potentially updated) and the values are feed costs.
        """

        quality_specific_feed_ids: Dict[str, str] = {}
        for input_feed_id in input_feed_ids:
            quality_id = self.get_quality_specific_purchased_feed_ids(input_feed_id)[0]
            quality_specific_feed_ids[str(input_feed_id)] = str(quality_id)

        updated_costs: Dict[str, float] = {}
        for key, val in self.feed_costs.items():
            updated_costs[quality_specific_feed_ids[key]] = val
        # feed value costs according to feeds split by maturity
        return updated_costs

    def add_to_available_feeds(self, new_grown_feeds, DM_list, NDF_list):
        """
        Description:
            Appends the nutrient values of new_grown_feeds to the available_feeds
            dictionary according to their quality (if applicable). If a feed is
            not split by quality, then the values at the respective indices of
            DM_list and NDF_list are ignored.

        Args:
            new_grown_feeds: the list of feed entries to be added to
                available_feeds with nutrient values based on their quality
            DM_list: the list of dry matter percentages for each feed in
                new_grown_feeds (indices match up)
            NDF_list: the list of NDF percentages for each feed in
                new_grown_feeds (indices match up)
        """
        new_feed_ids = []
        for i, new_feed in enumerate(new_grown_feeds):
            new_feed_ids.append(new_feed)
            self.feed_costs[str(new_feed_ids[-1]) + "g"] = 0
        self.available_feeds.update(self.get_nutrient_vals(new_feed_ids, True))

    def update_available_feed(self, feed_id, nutrient, new_val):
        """
        Description:
            Updates the dictionary of available feeds with a particular nutrient
            value.

        Args:
            feed_id: string - the ID of the feed to be modified (string should
                end in 'g' if it is a grown feed
            nutrient: the nutrient to be modified
            new_val: the new value of the nutrient
        """
        self.available_feeds[feed_id][nutrient] = new_val

    def remove_from_available_feeds(self, feeds_to_be_removed):
        """
        Description:
            Removes the IDs in feeds_to_be_removed from available_feeds.

        Args:
            feeds_to_be_removed: a list of feed IDs
        """
        for feed_id in feeds_to_be_removed:
            self.available_feeds.pop(feed_id)

    def get_nutrient_vals(self, feed_ids, is_grown):
        """
        Description:
            Constructs and returns the dictionary of nutrient values for the feeds
            represented by feed_ids.

        Args:
            feed_ids: list of feed IDs
            is_grown: boolean - true if the feeds represented by feed_ids are
                grown, false if purchased

        Returns: a dictionary where the keys are the the feed identifiers and
        the values are nutrient dictionaries
        """
        dict_list = self._retrieve_data(
            data_source=self.nutrient_table,
            identifier="rufas_id",
            desired_rows=feed_ids,
        )
        # missing: (26, 54, 136, 139, 157)
        nutrient_vals = {}
        for dictionary in dict_list:
            feed_id = dictionary["rufas_id"]
            # the key in the available_feeds dictionary has a 'g' as the
            # suffix if it is a grown feed
            feed_key = str(feed_id)

            if is_grown:
                feed_key += "g"

            nutrient_vals[feed_key] = dictionary
        return nutrient_vals

    def get_calf_feeds(self):
        feed_ids = [202, 203, 216]
        if "DE_Base" in list(self.available_feeds.items())[0][1].keys():
            columns = ["rufas_id", "DM", "CP", "EE", "DE_Base"]
        else:
            columns = ["rufas_id", "DM", "CP", "EE", "DE"]

        nutrients = self._retrieve_data(
            data_source=self.nutrient_table,
            var_names=columns,
            identifier="rufas_id",
            desired_rows=feed_ids,
        )

        calf_feeds = {}
        for feed_id in feed_ids:
            feed_id_nutrient = next(nutrient for nutrient in nutrients if nutrient["rufas_id"] == feed_id)
            calf_feeds[feed_id] = {
                key: feed_id_nutrient[key] for key in list(feed_id_nutrient.keys()) if key != "rufas_id"
            }
        return calf_feeds

    def _pack_into_dict(self, var_names: List[str], var_values: List[Any]) -> Dict[str, Any]:
        """
        Pack the provided variable names and values into a dictionary.

        Parameters
        ----------
        var_names : List[str]
            List of keys for the resulting dictionary.
        var_values : List[Any]
            Corresponding values for the keys specified in `var_names`.

        Returns
        -------
        Dict[str, Any]
            Dictionary constructed from the provided variable names and values.

        Raises
        ------
        ValueError
            If the lengths of `var_names` and `var_values` are not the same.

        Notes
        -----
        Ensure that both `var_names` and `var_values` have the same length.
        Each name in `var_names` will be paired with its corresponding value from `var_values`.

        Example
        -------
        >>> self._pack_into_dict(['a', 'b'], [1, 2])
        {'a': 1, 'b': 2}

        """
        result_dict = {}
        for id_var, var_name in enumerate(var_names):
            result_dict[var_name] = var_values[id_var]
        return result_dict

    def _retrieve_data(
        self,
        data_source: str,
        var_names: List[str] = None,
        unique_value: bool = False,
        identifier: str = None,
        desired_rows: List[Any] = None,
        compare_val: int = None,
        low_col: str = None,
        high_col: str = None,
    ) -> List[Dict[str, Any]]:
        """
         This function retrieves and filters the desired data, pack each "row" into a dictionary object, and returns a
         list of desired rows

         Parameters
         ----------
         data_source : str
             Path to retrieve the desired data from IM.
         var_names : List[str] = None
             A list of desired variables (columns) to retrieve.
             If omitted, all existing columns are returned.
         unique_value: bool = False
             If True, returns only unique values. Default is False.
         identifier: str = None
             Column name used for filtering based on `desired_rows`.
             Both `identifier` and `desired_rows` must be provided for filtering.
         desired_rows: List[Any] = None
             Desired row values for filtering. Rows with these values in the `identifier` column are returned.
         compare_val: int = None
             Baseline value for comparison. Used with `low_col` and `high_col` to filter rows. The "compare_val" should
             fall in the range of [low_col_value, high_col_value], otherwise the current row will be ignored.
         low_col: str = None
             Column indicating the lower bound for comparison with `compare_val`.
         high_col: str = None
             Column indicating the upper bound for comparison with `compare_val`.

         Returns
         -------
         List[Dict[str, Any]]
             Returns a list of dictionaries, each dictionary corresponds to a row in the csv file.

         Example
         -------
        1. Retrieve specific columns:
         >>> self._retrieve_data(data_source="NASEM_Comp", var_names=["rufas_id", "Name", "feed_type"])
         Returns rows from the data source "NASEM_Comp" with columns "rufas_id", "Name", and "feed_type" packed into
         dictionaries.

         2. Filter by specific rows based on an identifier:
         >>> self._retrieve_data(data_source="NASEM_Comp", identifier="rufas_id", desired_rows=[1, 2, 157])
         Returns rows where the "rufas_id" column has values 1, 2 or 157.

         3. Use a value for range comparison:
         >>> self._retrieve_data(data_source="NASEM_Comp", compare_val=5, low_col="lower_limit", high_col="limit")
         Returns rows where the "compare_val" of 5 lies between the values in columns "lower_limit" and "limit".

         4. Retrieve unique values from specified columns:
         >>> self._retrieve_data(data_source="NASEM_Comp", var_names=["rufas_id", "Name"], unique_value=True)
         Returns unique rows (based on "rufas_id" and "Name" columns) from the data source "NASEM_Comp".

         5. No filters or specific columns, retrieve all data:
         >>> self._retrieve_data(data_source="NASEM_Comp")
         Returns all rows from the data source "NASEM_Comp" with all columns packed into dictionaries.

         6. Filtering with range comparison and specific desired rows:
         >>> self._retrieve_data(data_source="NASEM_Comp", identifier="feed_type", desired_rows=["Conc"],
         compare_val=10, low_col="lower_limit", high_col="limit")

         Returns rows where the "feed_type" column has values "Conc" and where the value 10 lies between the values in
         columns "lower_limit" and "limit".
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._retrieve_data.__name__,
        }

        result_list = []
        values = []
        data = self.im.get_data(data_source)
        if not var_names:
            var_names = list(data.keys())

        for i in range(len(data[var_names[0]])):
            try:
                if desired_rows and identifier and data[identifier][i] not in desired_rows:
                    continue
                if compare_val and low_col and high_col:
                    low_val, high_val = data[low_col][i], data[high_col][i]
                    if not (low_val <= compare_val <= high_val):
                        continue
                var_values = [data[key][i] for key in var_names]
                if unique_value and var_values in values:
                    continue
                values.append(var_values)
                result_list.append(self._pack_into_dict(var_names, var_values))
            except IndexError as e:
                self.om.add_error("Length mismatch", str(e), info_map=info_map)
                raise e

        return result_list
