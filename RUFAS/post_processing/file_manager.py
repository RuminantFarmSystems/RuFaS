class FileManager:
    """
    Class overseeing file management activities in RuFaS.
    """
    def __init__(self, metadata_prefix: str, supported_prefixes: dict[str, str]) -> None:
        self.metadata_prefix = metadata_prefix
        self.supported_filter_types_prefixes = supported_prefixes
