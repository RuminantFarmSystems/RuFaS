from .base_reception_pit import BaseReceptionPit


class NullReceptionPit(BaseReceptionPit):
    def __init__(self, separator, reception_pit='null_reception', reception_pit_data=None):
        super().__init__(reception_pit, reception_pit_data, separator)

    def update_all(self):
        # TODO: this will need to be changed when improvements are made to the base reception pit class
        super().update_all()
