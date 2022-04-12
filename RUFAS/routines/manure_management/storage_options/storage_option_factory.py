from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen
from RUFAS.routines.manure_management.storage_options.storage_option_classes.anaerobic_lagoon import AnaerobicLagoon
from RUFAS.routines.manure_management.storage_options.storage_option_classes.base_storage import BaseStorage
from RUFAS.routines.manure_management.storage_options.storage_option_classes.custom_storage import CustomStorage
from RUFAS.routines.manure_management.storage_options.storage_option_enum import StorageOptionEnum
from RUFAS.routines.manure_management.storage_options.storage_option_init_data import StorageOptionInitData
from RUFAS.routines.manure_management.storage_options.storage_option_classes.storage_pond import StoragePond


class StorageOptionFactory:
    @classmethod
    def get_instance(cls, pen: SimplePen) -> BaseStorage:
        storage_option_enum = StorageOptionEnum.get_enum(pen.manure_storage)
        params = {
            'pen': pen,
            'storage_option_init_data': cls.get_storage_option_init_data(storage_option_enum)
        }
        enum_to_class = {
            storage_option_enum.STORAGE_POND: StoragePond,
            storage_option_enum.ANAEROBIC_LAGOON: AnaerobicLagoon,
            storage_option_enum.CUSTOM_STORAGE: CustomStorage
        }
        return enum_to_class[storage_option_enum](**params)

    @classmethod
    def get_storage_option_init_data(cls, storage_option_enum: StorageOptionEnum) -> StorageOptionInitData:
        init_data = StorageOptionInitData()

        # Customize init data here based on enum if necessary
        # ...

        return init_data
