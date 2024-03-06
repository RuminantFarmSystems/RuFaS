from typing import TypedDict


class PregCheckConfig(TypedDict, total=False):
    """
    List of expected keys for preg check configuration dictionary,
    used in daily pregnancy check routine for HeiferII and Cow classes.

    Each dictionary contains:
        - 'day': The number of days from the AI day when the pregnancy check should occur.
        - 'loss_rate': The probability of pregnancy loss at this check.
        - 'on_preg_loss': The event message to log if pregnancy loss occurs at this check.
        - 'on_preg': The event message to log if the cow remains pregnant at this check.
        - 'on_not_preg' (optional): The event message to log if the cow is not pregnant, due to a failed conception,
         at the start of the first check.
    """

    day: int
    loss_rate: float
    on_preg_loss: str
    on_preg: str
    on_not_preg: str
