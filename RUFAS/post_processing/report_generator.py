from dataclasses import dataclass


@dataclass
class ReportGeneratorConfig:
    """
    Attributes
    ----------
    """


class ReportGenerator:
    """
    A class to generate reports based on filtered data and aggregation criteria and store them in a dictionary.

    Parameters
    ----------
    config : ReportGeneratorConfig
            Configuration dataclass for ReportGenerator.

    Attributes
    ----------
    reports : dict[str, dict[str, list[Any]]]
        A dictionary containing the generated reports, with the report name as the key and the report data as the value.
    time : RufasTime | None
        A ``RufasTime`` object used to track the simulation time

    Notes
    -----
    ReportGenerator consumes variables selected from OutputManager by filters. To inspect whether source variables were
    reported to OutputManager daily or on another cadence, use OutputManager's `report_variables_usage_counts()` output:
    `variables_usage_counts` shows filter selection counts, and `variables_not_reported_daily` lists variables treated
    as non-daily for reporting diagnostics with `variable_name` and `report_count` columns.
    """

    def __init__(self, config: ReportGeneratorConfig) -> None:
        pass
