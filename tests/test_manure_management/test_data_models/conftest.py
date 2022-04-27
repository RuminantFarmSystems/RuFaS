"""
This file should contain reusable fixtures for the
`test_manure_management` package.
"""

from dataclasses import asdict

from pytest import fixture

from RUFAS.routines import AnimalManagement
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.manure_management.data_models.manure import Manure
from RUFAS.routines.manure_management.data_models.simple_animal_management import SimpleAnimalManagement
from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen


@fixture
def pen(mocker):
    p = mocker.Mock(spec=Pen)
    p.manure = asdict(Manure())
    p.id = 0
    p.animals_in_pen = []
    p.classes_in_pen = set()
    p.housing_type = 'open air barn'
    p.bedding_type = 'organic'
    p.manure_handling = 'manual_scraping'
    p.manure_separator = 'sedimentation'
    p.manure_storage = 'storage_pit'
    return p


@fixture
def simple_pen(pen):
    return SimplePen(pen)


@fixture
def mock_func_returns_none(*args, **kwargs):
    """
    Patch functions that return value

    """

    return None


@fixture
def mock_func_lets_pass(*args, **kwargs):
    """
    Patch functions that have side effects

    """

    pass


@fixture
def animal_management(mocker):
    am = mocker.Mock(spec=AnimalManagement)
    am.all_pens = []
    return am


@fixture
def simple_animal_management(animal_management, pen):
    sam = SimpleAnimalManagement(animal_management)
    sam.all_pens = []
    num_pens = 10

    for i in range(num_pens):
        sp = SimplePen(pen)
        sp.id = i
        sam.all_pens.append(sp)

    return sam
