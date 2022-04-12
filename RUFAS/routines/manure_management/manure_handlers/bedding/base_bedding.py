from __future__ import annotations


class BaseBedding:
    def __init__(self, arg_mass: float, arg_density: float):
        self.mass = arg_mass
        self._density = arg_density

    @property
    def density(self):
        return self._density

    @property
    def volume(self):
        """A calculated attribute for volume

        Automatically updated when either mass or density is changed.

        """

        return self.mass / self._density

    def __add__(self, other: BaseBedding) -> BaseBedding:
        if not isinstance(other, BaseBedding):
            raise TypeError('Cannot add a non-Bedding to a Bedding.')
        new_mass = self.mass + other.mass
        new_volume = self.volume + other.volume
        new_density = new_mass / new_volume
        return BaseBedding(new_mass, new_density)

    def __str__(self):
        return f'{self.__class__.__name__}: ' \
               f'mass = {self.mass}, ' \
               f'density = {self.density}, ' \
               f'volume = {self.volume}'


if __name__ == '__main__':
    b = BaseBedding(10, 2)
    print(b)

    c = BaseBedding(20, 5)
    print(c)

    b += c
    print(b)
