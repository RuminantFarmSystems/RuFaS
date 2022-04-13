from typing import Dict, Type

from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.base_separator import BaseSeparator
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.belt_press import BeltPress
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.custom_separator import CustomSeparator
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.decanting_centrifuge import \
    DecantingCentrifuge
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.mechanical_separator import \
    MechanicalSeparator
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.moving_disc_press import \
    MovingDiscPress
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.null_separator import NullSeparator
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.rotary_screen import RotaryScreen
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.screw_press import ScrewPress
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.sedimentation import Sedimentation
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.slope_screen import SlopeScreen
from RUFAS.routines.manure_management.manure_separators.manure_separator_enum import ManureSeparatorEnum
from RUFAS.routines.manure_management.manure_separators.manure_separator_init_data import ManureSeparatorInitData
from RUFAS.routines.manure_management.storage_options.storage_option_classes.base_storage import BaseStorage


class ManureSeparatorFactory:
    @classmethod
    def get_instance(cls, pen: SimplePen, storage_option: BaseStorage) -> BaseSeparator:
        manure_separator_enum = ManureSeparatorEnum.get_enum(pen.manure_handler)
        params = {
            'pen': pen,
            'storage_option': storage_option,
            'separator_data': cls.get_manure_separator_init_data(manure_separator_enum)
        }

        enum_to_class: Dict[ManureSeparatorEnum: Type[BaseSeparator]] = {
            ManureSeparatorEnum.BASE_SEPARATOR: BaseSeparator,
            ManureSeparatorEnum.BELT_PRESS: BeltPress,
            ManureSeparatorEnum.CUSTOM_SEPARATOR: CustomSeparator,
            ManureSeparatorEnum.DECANTING_CENTRIFUGE: DecantingCentrifuge,
            ManureSeparatorEnum.MECHANICAL_SEPARATOR: MechanicalSeparator,
            ManureSeparatorEnum.MOVING_DISC_PRESS: MovingDiscPress,
            ManureSeparatorEnum.NULL_SEPARATOR: NullSeparator,
            ManureSeparatorEnum.ROTARY_SCREEN: RotaryScreen,
            ManureSeparatorEnum.SCREW_PRESS: ScrewPress,
            ManureSeparatorEnum.SEDIMENTATION: Sedimentation,
            ManureSeparatorEnum.SLOPE_SCREEN: SlopeScreen
        }

        return enum_to_class[manure_separator_enum](**params)

    # TODO: Check logic
    @classmethod
    def get_manure_separator_init_data(cls, manure_separator_enum: ManureSeparatorEnum) -> ManureSeparatorInitData:
        enum_to_init_data: Dict[ManureSeparatorEnum: ManureSeparatorInitData] = {
            ManureSeparatorEnum.SEDIMENTATION: ManureSeparatorInitData(
                    TS_removal_efficiency=0.3,
                    VS_removal_efficiency=0.55,
                    N_removal_efficiency=0.3,
                    P_removal_efficiency=0.4,
                    K_removal_efficiency=0.15,
                    TS_DM_effluent_rate=0.2
            )
        }
        if manure_separator_enum in enum_to_init_data:
            return enum_to_init_data[manure_separator_enum]
        return ManureSeparatorInitData()
