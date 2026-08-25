import collections
from typing import Any, Counter

import numpy as np

from RUFAS.post_processing.file_manager import FileManager


class PoolManager:
    """
    Class overseeing the management of the variables pool including chunkification.
    """
    pool_element_type = dict[str, list[Any]]

    def __init__(self, file_manager: FileManager) -> None:
        self.variables_pool: dict[str, PoolManager.pool_element_type] = {}
        self.chunkification: bool = False
        self.saved_pool_chunks_num: int = 0
        self.available_memory: int = 0
        self.average_add_variable_call_addition: int = 118
        self.add_variable_call = 0
        self.save_chunk_threshold_call_count: int = 0
        self.current_pool_size: int = 0
        self.maximum_pool_size: float = np.inf
        self._variables_usage_counter: Counter[str] = collections.Counter()
        self.file_manager = file_manager
