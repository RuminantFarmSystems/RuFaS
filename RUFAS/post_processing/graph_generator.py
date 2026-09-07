from dataclasses import dataclass


@dataclass
class GraphGeneratorConfig:
    """
    Attributes
    ----------
    """


class GraphGenerator:
    """
    GraphGenerator is used to generate graphs from the simulation results.

    Parameters
    ----------
    config : GraphGeneratorConfig
        Configuration dataclass for GraphGenerator.

    Attributes
    ----------
    metadata_prefix : str, optional
        Prefix applied to graph metadata. Defaults to ``""``.
    time : RufasTime, optional
        ``RufasTime`` object used to track simulation time. Defaults to ``None``.

    Notes
    -----
    This class is not multi-thread safe!!!
    """

    def __init__(self, config: GraphGeneratorConfig) -> None:
        pass
