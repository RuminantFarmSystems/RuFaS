from .base_storage import BaseStorage


class CustomStorage(BaseStorage):
    def __init__(self, storage, storage_data):
        super().__init__(storage, storage_data)
