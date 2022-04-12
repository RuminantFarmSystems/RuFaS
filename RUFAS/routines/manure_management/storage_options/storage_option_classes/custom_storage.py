from .base_storage import BaseStorage


class CustomStorage(BaseStorage):
    def __init__(self, pen, storage_option_init_data):
        super().__init__(pen, storage_option_init_data)
