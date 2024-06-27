from .time import Time
from .input_manager import InputManager
from .output_manager import OutputManager


class EndToEndTester():
    """Executes an end-to-end test on RuFaS."""

    def __init__(self) -> None:
        self.im = InputManager()
        self.om = OutputManager()
        self.time = Time()

    def run_end_to_end_testing(self) -> None:
        """Runs a limited RuFaS simulation and compares the output to pre-computed outputs."""
        pass
