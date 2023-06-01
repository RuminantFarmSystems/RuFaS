from typing import List

class AmendmentSchedule:

    def __init__(self, years: int | List[int], days: int | List[int], pattern_skip: int = 0, pattern_repeat: int = 0):
        """
        Initializes a base soil amendment schedule.

        Parameters
        ----------
        years : int | List[int]
            Year(s) in which amendment will happen.
        days : int | List[int]
            Day(s) on which amendment will happen.
        pattern_skip : int, default=0
            Number of years to skip between amendment schedule repetitions.
        pattern_repeat : int, default=0
            Number of times the specified amendment schedule should be repeated.

        """
