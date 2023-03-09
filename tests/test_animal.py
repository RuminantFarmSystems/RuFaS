"""
RUFAS: Ruminant Farm Systems Model
File name: test_animal.py
Description: Implements test cases
Author(s): Pooya Hekmati, sh2235@cornell.edu
"""

from RUFAS.routines.animal.ration.ration_driver import AvailableFeeds
import pytest

from RUFAS.routines.animal.life_cycle.animal_events import AnimalEvents
import RUFAS.routines.animal.ration.animal_requirements


@pytest.fixture
def cow_a() -> dict:
    cow_a_dict = {
        'body_weight': 600,
        'mature_body_weight': 700,
        'day_of_pregnancy': 30,
        'animal_type': 'cow',
        'parity': 1,
        'calving_interval': 365,
        'milk_protein': 3.45,
        'Fat_Milk': 4,
        'Lactose_Milk': 4.9,
        'Milk': 30,
        'DIM': 120,
        'lactating': True,
        'BCS5': 3,
        'PrevTemp': None,
        'ADG_heifer': None,
        'daily_growth': None,
        'age': 1000,
        'distance': None
    }
    return cow_a_dict


@pytest.fixture
def cow_b() -> dict:
    cow_b_dict = {
        'body_weight': 680,
        'mature_body_weight': 700,
        'day_of_pregnancy': 150,
        'animal_type': 'cow',
        'parity': 3,
        'calving_interval': 365,
        'milk_protein': 3.45,
        'Fat_Milk': 4,
        'Lactose_Milk': 4.9,
        'Milk': 25,
        'DIM': 240,
        'lactating': False,
        'BCS5': 3,
        'PrevTemp': None,
        'ADG_heifer': None,
        'daily_growth': None,
        'age': 1000,
        'distance': None
    }
    return cow_b_dict


@pytest.fixture
def heifer_a() -> dict:
    heifer_a_dict = {
        'body_weight': 230,
        'mature_body_weight': 700,
        'day_of_pregnancy': None,
        'animal_type': 'heifer',
        'parity': 0,
        'calving_interval': None,
        'milk_protein': 0.0,
        'Fat_Milk': 0.0,
        'Lactose_Milk': 0.0,
        'Milk': 0.0,
        'DIM': None,
        'lactating': False,
        'BCS5': 3,
        'PrevTemp': 15,
        'ADG_heifer': 0.65,
        'daily_growth': None,
        'age': 210,
        'distance': None
    }
    return heifer_a_dict


@pytest.fixture
def heifer_b() -> dict:
    heifer_b_dict = {
        'body_weight': 340,
        'mature_body_weight': 700,
        'day_of_pregnancy': 1,
        'animal_type': 'heifer',
        'parity': 0,
        'calving_interval': None,
        'milk_protein': 0.0,
        'Fat_Milk': 0.0,
        'Lactose_Milk': 0.0,
        'Milk': 0.0,
        'DIM': None,
        'lactating': False,
        'BCS5': 3,
        'PrevTemp': 15,
        'ADG_heifer': 0.9,
        'daily_growth': None,
        'age': 365,
        'distance': None
    }
    return heifer_b_dict


def test_calculate_NRC_energy_maintenance_requirements(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NRC_energy_maintenance_requirements in file routines/animal/ration/animal_requirements.py"""
    result_NEmaint, result_CW, result_CBW = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_maintenance_requirements(
            cow_a['body_weight'], cow_a['mature_body_weight'], cow_a['day_of_pregnancy'], cow_a['BCS5'],
            cow_a['PrevTemp'], cow_a['animal_type'])
    assert (result_NEmaint, result_CW, result_CBW) == pytest.approx(
        (9.7, 0, 43.92), rel=5e-1)

    result_NEmaint, result_CW, result_CBW = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_maintenance_requirements(
            cow_b['body_weight'], cow_b['mature_body_weight'], cow_b['day_of_pregnancy'], cow_b['BCS5'],
            cow_b['PrevTemp'], cow_b['animal_type'])
    assert (result_NEmaint, result_CW, result_CBW) == pytest.approx(
        (10.65, 0, 43.92), rel=5e-1)

    result_NEmaint, result_CW, result_CBW = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_maintenance_requirements(
            heifer_a['body_weight'], heifer_a['mature_body_weight'], heifer_a['day_of_pregnancy'], heifer_a['BCS5'],
            heifer_a['PrevTemp'], heifer_a['animal_type'])
    assert (result_NEmaint, result_CW, result_CBW) == pytest.approx(
        (14.23, 0, 0), rel=5e-1)

    result_NEmaint, result_CW, result_CBW = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_maintenance_requirements(
            heifer_b['body_weight'], heifer_b['mature_body_weight'], heifer_b['day_of_pregnancy'], heifer_b['BCS5'],
            heifer_b['PrevTemp'], heifer_b['animal_type'])
    assert (result_NEmaint, result_CW, result_CBW) == pytest.approx(
        (19.07, 0, 43.92), rel=5e-1)


def test_calculate_NRC_energy_growth_requirements(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NRC_energy_growth_requirements in file routines/animal/ration/animal_requirements.py"""
    result_NEg, result_ADG, result_EQSBW = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_growth_requirements(
            cow_a['body_weight'], cow_a['mature_body_weight'], 22, cow_a['animal_type'],
            cow_a['parity'], cow_a['calving_interval'], cow_a['ADG_heifer'])
    assert (result_NEg, result_ADG, result_EQSBW) == pytest.approx(
        (0.77, 0.18, 394.065), rel=1e-1)

    result_NEg, result_ADG, result_EQSBW = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_growth_requirements(
            cow_b['body_weight'], cow_b['mature_body_weight'], 0, cow_b['animal_type'],
            cow_b['parity'], cow_b['calving_interval'], cow_b['ADG_heifer'])
    assert (result_NEg, result_ADG, result_EQSBW) == pytest.approx(
        (0.0, 0, 464.343), rel=1e-1)

    result_NEg, result_ADG, result_EQSBW = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_growth_requirements(
            heifer_a['body_weight'], heifer_a['mature_body_weight'], 0, heifer_a['animal_type'],
            heifer_a['parity'], heifer_a['calving_interval'], heifer_a['ADG_heifer'])
    assert (result_NEg, result_ADG, result_EQSBW) == pytest.approx(
        (1.5, 0.65, 157.057), rel=1e-1)

    result_NEg, result_ADG, result_EQSBW = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_growth_requirements(
            heifer_b['body_weight'], heifer_b['mature_body_weight'], 0, heifer_b['animal_type'],
            heifer_b['parity'], heifer_b['calving_interval'], heifer_b['ADG_heifer'])
    assert (result_NEg, result_ADG, result_EQSBW) == pytest.approx(
        (2.9, 0.9, 232.171), rel=1e-1)


def test_calculate_NRC_energy_pregnancy_requirements(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NRC_energy_pregnancy_requirements in file routines/animal/ration/animal_requirements.py"""
    result_NEpreg = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_pregnancy_requirements(
        cow_a['day_of_pregnancy'], 40)
    assert (result_NEpreg) == pytest.approx((0), rel=1e-1)

    result_NEpreg = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_pregnancy_requirements(
        cow_b['day_of_pregnancy'], 40)
    assert (result_NEpreg) == pytest.approx((0), rel=1e-1)

    result_NEpreg = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_pregnancy_requirements(
        heifer_a['day_of_pregnancy'], 0)
    assert (result_NEpreg) == pytest.approx((0), rel=1e-1)

    result_NEpreg = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_pregnancy_requirements(
        heifer_b['day_of_pregnancy'], 40)
    assert (result_NEpreg) == pytest.approx((0), rel=1e-1)


def test_calculate_NRC_energy_lactation_requirements(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NRC_energy_lactation_requirements in file routines/animal/ration/animal_requirements.py"""
    result_NEl = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_lactation_requirements(
        cow_a['animal_type'], cow_a['Fat_Milk'], cow_a['milk_protein'],
        cow_a['Lactose_Milk'], cow_a['Milk'])
    assert (result_NEl) == pytest.approx((23), rel=1e-1)

    result_NEl = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_lactation_requirements(
        cow_b['animal_type'], cow_b['Fat_Milk'], cow_b['milk_protein'],
        cow_b['Lactose_Milk'], cow_b['Milk'])
    assert (result_NEl) == pytest.approx((19), rel=1e-1)

    result_NEl = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_lactation_requirements(
        heifer_a['animal_type'], heifer_a['Fat_Milk'], heifer_a['milk_protein'],
        heifer_a['Lactose_Milk'], heifer_a['Milk'])
    assert (result_NEl) == pytest.approx((0), rel=1e-1)

    result_NEl = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_lactation_requirements(
        heifer_b['animal_type'], heifer_b['Fat_Milk'], heifer_b['milk_protein'],
        heifer_b['Lactose_Milk'], heifer_b['Milk'])
    assert (result_NEl) == pytest.approx((0), rel=1e-1)


def test_calculate_NRC_protein_requirements(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NRC_protein_requirements in file routines/animal/ration/animal_requirements.py"""
    result_MP_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_protein_requirements(
        cow_a['body_weight'], 22, cow_a['day_of_pregnancy'], cow_a['animal_type'],
        cow_a['Milk'], cow_a['milk_protein'], 40, 3, 1, 220)
    assert (result_MP_req) == pytest.approx((1965), rel=1e-1)

    result_MP_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_protein_requirements(
        cow_b['body_weight'], 0, cow_b['day_of_pregnancy'], cow_b['animal_type'],
        cow_b['Milk'], cow_b['milk_protein'], 0, 3, 1, 0)
    assert (result_MP_req) == pytest.approx((1624), rel=1e-1)

    result_MP_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_protein_requirements(
        heifer_a['body_weight'], 22, heifer_a['day_of_pregnancy'], heifer_a['animal_type'],
        heifer_a['Milk'], heifer_a['milk_protein'], 40, 3, 1, 220)
    assert (result_MP_req) == pytest.approx((374), rel=1e-1)

    result_MP_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_protein_requirements(
        heifer_b['body_weight'], 0, heifer_b['day_of_pregnancy'], heifer_b['animal_type'],
        heifer_b['Milk'], heifer_b['milk_protein'], 0, 3, 1, 0)
    assert (result_MP_req) == pytest.approx((301), rel=1e-1)


def test_calculate_NRC_calcium_requirements(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NRC_calcium_requirements in file routines/animal/ration/animal_requirements.py"""
    result_Ca_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_calcium_requirements(
        cow_a['body_weight'], cow_a['mature_body_weight'], cow_a['day_of_pregnancy'], cow_a['animal_type'],
        cow_a['lactating'], 1, cow_a['Milk'])
    assert (result_Ca_req) == pytest.approx((66), rel=1e-1)

    result_Ca_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_calcium_requirements(
        cow_b['body_weight'], cow_b['mature_body_weight'], cow_b['day_of_pregnancy'], cow_b['animal_type'],
        cow_b['lactating'], 1, cow_b['Milk'])
    assert (result_Ca_req) == pytest.approx((52), rel=1e-1)

    result_Ca_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_calcium_requirements(
        heifer_a['body_weight'], heifer_a['mature_body_weight'], heifer_a['day_of_pregnancy'], heifer_a['animal_type'],
        heifer_a['lactating'], 1, heifer_a['Milk'])
    assert (result_Ca_req) == pytest.approx((17), rel=1e-1)

    result_Ca_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_calcium_requirements(
        heifer_b['body_weight'], heifer_b['mature_body_weight'], heifer_b['day_of_pregnancy'], heifer_b['animal_type'],
        heifer_b['lactating'], 1, heifer_b['Milk'])
    assert (result_Ca_req) == pytest.approx((17.5), rel=1e-1)


def test_calculate_NRC_phosphorus_requirements(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NRC_phosophorus_requirements in file routines/animal/ration/animal_requirements.py"""
    result_P_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_phosphorus_requirements(
        cow_a['body_weight'], cow_a['mature_body_weight'], cow_a['day_of_pregnancy'], cow_a['Milk'],
        cow_a['animal_type'], 1)
    assert (result_P_req) == pytest.approx((33), rel=1e-1)

    result_P_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_phosphorus_requirements(
        cow_b['body_weight'], cow_b['mature_body_weight'], cow_b['day_of_pregnancy'], cow_b['Milk'],
        cow_b['animal_type'], 1)
    assert (result_P_req) == pytest.approx((29), rel=1e-1)

    result_P_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_phosphorus_requirements(
        heifer_a['body_weight'], heifer_a['mature_body_weight'], heifer_a['day_of_pregnancy'], heifer_a['Milk'],
        heifer_a['animal_type'], 1)
    assert (result_P_req) == pytest.approx((7.5), rel=1e-1)

    result_P_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_phosphorus_requirements(
        heifer_b['body_weight'], heifer_b['mature_body_weight'], heifer_b['day_of_pregnancy'], heifer_b['Milk'],
        heifer_b['animal_type'], 1)
    assert (result_P_req) == pytest.approx((6.9), rel=1e-1)


def test_calculate_NRC_DMI(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NRC_DMI in file routines/animal/ration/animal_requirements.py"""
    result_DMIest = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_DMI(
        cow_a['animal_type'], cow_a['body_weight'], cow_a['day_of_pregnancy'], cow_a['DIM'], cow_a['lactating'],
        cow_a['Milk'], cow_a['Fat_Milk'])
    assert (result_DMIest) == pytest.approx((22.5), rel=1e-1)

    result_DMIest = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_DMI(
        cow_b['animal_type'], cow_b['body_weight'], cow_b['day_of_pregnancy'], cow_b['DIM'], cow_b['lactating'],
        cow_b['Milk'], cow_b['Fat_Milk'])
    assert (result_DMIest) == pytest.approx((13.4), rel=1e-1)

    result_DMIest = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_DMI(
        heifer_a['animal_type'], heifer_a['body_weight'], heifer_a['day_of_pregnancy'], heifer_a['DIM'], heifer_a['lactating'],
        heifer_a['Milk'], heifer_a['Fat_Milk'])
    assert (result_DMIest) == pytest.approx((0), rel=1e-1)

    result_DMIest = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_DMI(
        heifer_b['animal_type'], heifer_b['body_weight'], heifer_b['day_of_pregnancy'], heifer_b['DIM'], heifer_b['lactating'],
        heifer_b['Milk'], heifer_b['Fat_Milk'])
    assert (result_DMIest) == pytest.approx((0), rel=1e-1)


def test_calculate_NASEM_energy_lactation_requirements(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NASEM_energy_lactation_requirements in file routines/animal/ration/animal_requirements.py"""
    result_NEl = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_lactation_requirements(
        cow_a['animal_type'], cow_a['Fat_Milk'], cow_a['milk_protein'], cow_a['Lactose_Milk'], cow_a['Milk'])
    assert (result_NEl) == pytest.approx((23), rel=1e-1)

    result_NEl = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_lactation_requirements(
        cow_b['animal_type'], cow_b['Fat_Milk'], cow_b['milk_protein'], cow_b['Lactose_Milk'], cow_b['Milk'])
    assert (result_NEl) == pytest.approx((19), rel=1e-1)

    result_NEl = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_lactation_requirements(
        heifer_a['animal_type'], heifer_a['Fat_Milk'], heifer_a['milk_protein'], heifer_a['Lactose_Milk'], heifer_a['Milk'])
    assert (result_NEl) == pytest.approx((0), rel=1e-1)

    result_NEl = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_lactation_requirements(
        heifer_b['animal_type'], heifer_b['Fat_Milk'], heifer_b['milk_protein'], heifer_b['Lactose_Milk'], heifer_b['Milk'])
    assert (result_NEl) == pytest.approx((0), rel=1e-1)


def test_calculate_NASEM_DMI(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NASEM_DMI in file routines/animal/ration/animal_requirements.py"""
    result_DMIest = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_DMI(
        cow_a['body_weight'], cow_a['mature_body_weight'], cow_a['DIM'], cow_a['lactating'],
        15, cow_a['parity'], cow_a['BCS5'])
    assert (result_DMIest) == pytest.approx((19), rel=1e-1)

    result_DMIest = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_DMI(
        cow_b['body_weight'], cow_b['mature_body_weight'], cow_b['DIM'], cow_b['lactating'],
        15, cow_b['parity'], cow_b['BCS5'])
    assert (result_DMIest) == pytest.approx((12), rel=1e-1)

    result_DMIest = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_DMI(
        heifer_a['body_weight'], heifer_a['mature_body_weight'], heifer_a['DIM'], heifer_a['lactating'],
        15, heifer_a['parity'], heifer_a['BCS5'])
    assert (result_DMIest) == pytest.approx((6), rel=1e-1)

    result_DMIest = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_DMI(
        heifer_b['body_weight'], heifer_b['mature_body_weight'], heifer_b['DIM'], heifer_b['lactating'],
        15, heifer_b['parity'], heifer_b['BCS5'])
    assert (result_DMIest) == pytest.approx((8), rel=1e-1)


def test_calculate_NASEM_energy_maintenance_requirements(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NASEM_energy_maintenance_requirements in file routines/animal/ration/animal_requirements.py"""
    result_NEmaint, result_GrUterW, result_UterW = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_maintenance_requirements(
            cow_a['body_weight'], cow_a['mature_body_weight'], cow_a['day_of_pregnancy'], cow_a['DIM'])
    assert (result_NEmaint, result_GrUterW, result_UterW) == pytest.approx(
        (11.12, 65.11, 0.2), rel=1e-1)

    result_NEmaint, result_GrUterW, result_UterW = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_maintenance_requirements(
            cow_b['body_weight'], cow_b['mature_body_weight'], cow_b['day_of_pregnancy'], cow_b['DIM'])
    assert (result_NEmaint, result_GrUterW, result_UterW) == pytest.approx(
        (12.59, 48.52, 0.2), rel=1e-1)

    result_NEmaint, result_GrUterW, result_UterW = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_maintenance_requirements(
            heifer_a['body_weight'], heifer_a['mature_body_weight'], heifer_a['day_of_pregnancy'], heifer_a['DIM'])
    assert (result_NEmaint, result_GrUterW,
            result_UterW) == pytest.approx((5.9, 0, 0), rel=1e-1)

    result_NEmaint, result_GrUterW, result_UterW = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_maintenance_requirements(
            heifer_b['body_weight'], heifer_b['mature_body_weight'], heifer_b['day_of_pregnancy'], heifer_b['DIM'])
    assert (result_NEmaint, result_GrUterW, result_UterW) == pytest.approx(
        (6.3, 77.71, 10.25), rel=1e-1)


def test_calculate_NASEM_energy_growth_requirements(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NASEM_energy_growth_requirements in file routines/animal/ration/animal_requirements.py"""
    result_NEg, result_ADG, result_frame_weight_gain = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_growth_requirements(
            cow_a['body_weight'], cow_a['mature_body_weight'], cow_a['ADG_heifer'], cow_a['animal_type'],
            cow_a['parity'], cow_a['calving_interval'])
    assert (result_NEg, result_ADG, result_frame_weight_gain) == pytest.approx(
        (1.1, 0.18, 0.44), rel=1e-1)

    result_NEg, result_ADG, result_frame_weight_gain = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_growth_requirements(
            cow_b['body_weight'], cow_b['mature_body_weight'], cow_b['ADG_heifer'], cow_b['animal_type'],
            cow_b['parity'], cow_b['calving_interval'])
    assert (result_NEg, result_ADG, result_frame_weight_gain) == pytest.approx(
        (0.0, 0.00001, 0.0), rel=1e-1)

    result_NEg, result_ADG, result_frame_weight_gain = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_growth_requirements(
            heifer_a['body_weight'], heifer_a['mature_body_weight'], heifer_a['ADG_heifer'], heifer_a['animal_type'],
            heifer_a['parity'], heifer_a['calving_interval'])
    assert (result_NEg, result_ADG, result_frame_weight_gain) == pytest.approx(
        (2.5, 0.65, 0.31), rel=1e-1)

    result_NEg, result_ADG, result_frame_weight_gain = \
        RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_growth_requirements(
            heifer_b['body_weight'], heifer_b['mature_body_weight'], heifer_b['ADG_heifer'], heifer_b['animal_type'],
            heifer_b['parity'], heifer_b['calving_interval'])
    assert (result_NEg, result_ADG, result_frame_weight_gain) == pytest.approx(
        (4.1, 0.9, 0.35), rel=1e-1)


def test_calculate_NASEM_energy_pregnancy_requirements(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NASEM_energy_pregnancy_requirements in file routines/animal/ration/animal_requirements.py"""
    result_NEpreg, result_GrUterWGain = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_pregnancy_requirements(
        cow_a['lactating'], cow_a['day_of_pregnancy'], cow_a['DIM'], 49, 0.2)
    assert (result_NEpreg, result_GrUterWGain) == pytest.approx(
        (0.4, 0.096), rel=1e-1)

    result_NEpreg, result_GrUterWGain = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_pregnancy_requirements(
        cow_b['lactating'], cow_b['day_of_pregnancy'], cow_b['DIM'], 49, 0.2)
    assert (result_NEpreg, result_GrUterWGain) == pytest.approx(
        (4.2, 1.0), rel=1e-1)

    result_NEpreg, result_GrUterWGain = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_pregnancy_requirements(
        heifer_a['lactating'], heifer_a['day_of_pregnancy'], heifer_a['DIM'], 49, 0.2)
    assert (result_NEpreg, result_GrUterWGain) == pytest.approx(
        (0, 0), rel=1e-1)

    result_NEpreg, result_GrUterWGain = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_pregnancy_requirements(
        heifer_b['lactating'], heifer_b['day_of_pregnancy'], heifer_b['DIM'], 49, 0.2)
    assert (result_NEpreg, result_GrUterWGain) == pytest.approx(
        (4.9, 1.2), rel=1e-1)


def test_calculate_NASEM_protein_requirements(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NASEM_protein_requirements in file routines/animal/ration/animal_requirements.py"""
    result_MP_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_protein_requirements(
        cow_a['lactating'], cow_a['body_weight'], 1, 0.1, 22,
        cow_a['milk_protein'], cow_a['Milk'])
    assert (result_MP_req) == pytest.approx((1505), rel=1e-1)

    result_MP_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_protein_requirements(
        cow_b['lactating'], cow_b['body_weight'], 1, 1, 8,
        cow_b['milk_protein'], cow_b['Milk'])
    assert (result_MP_req) == pytest.approx((715), rel=1e-1)

    result_MP_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_protein_requirements(
        heifer_a['lactating'], heifer_a['body_weight'], 1, 1, 7,
        heifer_a['milk_protein'], heifer_a['Milk'])
    assert (result_MP_req) == pytest.approx((548), rel=1e-1)

    result_MP_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_protein_requirements(
        heifer_b['lactating'], heifer_b['body_weight'], 1, 1, 7,
        heifer_b['milk_protein'], heifer_b['Milk'])
    assert (result_MP_req) == pytest.approx((586), rel=1e-1)


def test_calculate_NASEM_calcium_requirements(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NASEM_calcium_requirements in file routines/animal/ration/animal_requirements.py"""
    result_Ca_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_calcium_requirements(
        cow_a['body_weight'], cow_a['mature_body_weight'], cow_a['day_of_pregnancy'], 1,
        22, cow_a['milk_protein'], cow_a['Milk'])
    assert (result_Ca_req) == pytest.approx((54), rel=1e-1)

    result_Ca_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_calcium_requirements(
        cow_b['body_weight'], cow_b['mature_body_weight'], cow_b['day_of_pregnancy'], 1,
        8, cow_b['milk_protein'], cow_b['Milk'])
    assert (result_Ca_req) == pytest.approx((38), rel=1e-1)

    result_Ca_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_calcium_requirements(
        heifer_a['body_weight'], heifer_a['mature_body_weight'], heifer_a['day_of_pregnancy'], 1,
        7, heifer_a['milk_protein'], heifer_a['Milk'])
    assert (result_Ca_req) == pytest.approx((7), rel=1e-1)

    result_Ca_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_calcium_requirements(
        heifer_b['body_weight'], heifer_b['mature_body_weight'], heifer_b['day_of_pregnancy'], 1,
        7, heifer_b['milk_protein'], heifer_b['Milk'])
    assert (result_Ca_req) == pytest.approx((7), rel=1e-1)


def test_calculate_NASEM_phosphorus_requirements(cow_a:dict, cow_b:dict, heifer_a:dict, heifer_b:dict)->None:
    """Unit test for function calculate_NASEM_phosphorus_requirements in file routines/animal/ration/animal_requirements.py"""
    result_P_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_phosphorus_requirements(
        cow_a['body_weight'], cow_a['mature_body_weight'], cow_a['animal_type'], cow_a['day_of_pregnancy'], 1, 20,
        cow_a['milk_protein'], cow_a['Milk'])
    assert (result_P_req) == pytest.approx((55), rel=1e-1)

    result_P_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_phosphorus_requirements(
        cow_b['body_weight'], cow_b['mature_body_weight'], cow_b['animal_type'], cow_b['day_of_pregnancy'], 1, 8,
        cow_b['milk_protein'], cow_b['Milk'])
    assert (result_P_req) == pytest.approx((28), rel=1e-1)

    result_P_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_phosphorus_requirements(
        heifer_a['body_weight'], heifer_a['mature_body_weight'], heifer_a['animal_type'], heifer_a['day_of_pregnancy'], 1, 7,
        heifer_a['milk_protein'], heifer_a['Milk'])
    assert (result_P_req) == pytest.approx((13), rel=1e-1)

    result_P_req = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_phosphorus_requirements(
        heifer_b['body_weight'], heifer_b['mature_body_weight'], heifer_b['animal_type'], heifer_b['day_of_pregnancy'], 1, 7,
        heifer_b['milk_protein'], heifer_b['Milk'])
    assert (result_P_req) == pytest.approx((12.4), rel=1e-1)


def test_norm():
    """Unit test for function norm in file routines/animal/clustering_pen_grouping.py"""
    pass


def test_percentile_list():
    """Unit test for function percentile_list in file routines/animal/clustering_pen_grouping.py"""
    pass


def test_grouping():
    """Unit test for function grouping in file routines/animal/clustering_pen_grouping.py"""
    pass


def test_update_animals():
    """Unit test for function update_animals in file routines/animal/pen.py"""
    pass


def test_call_animal_nutrient_rqmts():
    """Unit test for function call_animal_nutrient_rqmts in file routines/animal/pen.py"""
    pass


def test_calc_avg_nutrient_rqmts():
    """Unit test for function calc_avg_nutrient_rqmts in file routines/animal/pen.py"""
    pass


def test_calc_avg_stats():
    """Unit test for function calc_avg_stats in file routines/animal/pen.py"""
    pass


def test_calc_ration():
    """Unit test for function calc_ration in file routines/animal/pen.py"""
    pass


def test_calc_manure():
    """Unit test for function calc_manure in file routines/animal/pen.py"""
    pass


def test_reset_manure():
    """Unit test for function reset_manure in file routines/animal/pen.py"""
    pass


def test_calc_avg_growth():
    """Unit test for function calc_avg_growth in file routines/animal/pen.py"""
    pass


def test_calc_daily_walking_dist():
    """Unit test for function calc_daily_walking_dist in file routines/animal/pen.py"""
    pass


def test_call_p_rqmts():
    """Unit test for function call_p_rqmts in file routines/animal/pen.py"""
    pass


def test_daily_p_update():
    """Unit test for function daily_p_update in file routines/animal/pen.py"""
    pass


def test_set_up_new_animal():
    """Unit test for function set_up_new_animal in file routines/animal/pen.py"""
    pass


def test_clear():
    """Unit test for function clear in file routines/animal/pen.py"""
    pass


def test_set_nutrient_list():
    """Unit test for function set_nutrient_list in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_set_config():
    """Unit test for function set_config in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_set_default_nutrient_rqmts():
    """Unit test for function set_default_nutrient_rqmts in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_set_ration():
    """Unit test for function set_ration in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_set_p_intake():
    """Unit test for function set_p_intake in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_daily_p_update():
    """Unit test for function daily_p_update in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_calc_base_manure():
    """Unit test for function calc_base_manure in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_set_p_purchased():
    """Unit test for function set_p_purchased in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_update_pen_history():
    """Unit test for function update_pen_history in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_update_body_weight_history():
    """Unit test for function update_body_weight_history in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_init_from_string():
    """Unit test for function init_from_string in file routines/animal/life_cycle/animal_events.py"""
    pass


def test_add_event():
    """Unit test for function add_event in file routines/animal/life_cycle/animal_events.py"""
    pass


def test___str__():
    """Unit test for function __str__ in file routines/animal/life_cycle/animal_events.py"""
    pass


@pytest.mark.parametrize(
        "events_list, event_descriptions, expected_days",
        [
            (
                    [],
                    ['dummy'],
                    [-1]
            ),
            (
                    [(1, 2, 'event1'), (3, 4, 'event2'),
                     (5, 6, 'event1'), (7, 8, 'event3')],
                    ['event1', 'event2', 'event3', 'event0'],
                    [5, 3, 7, -1]
            )
        ],
)
def test_get_most_recent_date(events_list, event_descriptions, expected_days):
    """Unit test for function get_most_recent_date in file routines/animal/life_cycle/animal_events.py"""
    animal_event = AnimalEvents()
    for animal_age, simulation_day, event_description in events_list:
        animal_event.add_event(animal_age, simulation_day, event_description)

    for event_description, expected in zip(event_descriptions, expected_days):
        actual = animal_event.get_most_recent_date(event_description)
        assert actual == expected


def test_next_id():
    """Unit test for function next_id in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_init_animals():
    """Unit test for function init_animals in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_get_calves():
    """Unit test for function get_calves in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_get_heiferIs():
    """Unit test for function get_heiferIs in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_get_heiferIIs():
    """Unit test for function get_heiferIIs in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_get_heiferIIIs():
    """Unit test for function get_heiferIIIs in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_get_cows():
    """Unit test for function get_cows in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_get_replacement_cows():
    """Unit test for function get_replacement_cows in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_initialization_db_summary():
    """Unit test for function initialization_db_summary in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_init_values():
    """Unit test for function init_values in file routines/animal/life_cycle/calf.py"""
    pass


def test_assign_calf_values():
    """Unit test for function assign_calf_values in file routines/animal/life_cycle/calf.py"""
    pass


def test_get_calf_values():
    """Unit test for function get_calf_values in file routines/animal/life_cycle/calf.py"""
    pass


def test_calc_nutrient_rqmts():
    """Unit test for function calc_nutrient_rqmts in file routines/animal/life_cycle/calf.py"""
    pass


def test_calc_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/life_cycle/calf.py"""
    pass


def test_phosphorus_rqmts():
    """Unit test for function phosphorus_rqmts in file routines/animal/life_cycle/calf.py"""
    pass


def test_update():
    """Unit test for function update in file routines/animal/life_cycle/calf.py"""
    pass


def test_update_milk_production_history():
    """Unit test for function update_milk_production_history in file routines/animal/life_cycle/cow.py"""
    pass


def test__determine_param_value():
    """Unit test for function _determine_param_value in file routines/animal/life_cycle/cow.py"""
    pass


def test__milking_update():
    """Unit test for function _milking_update in file routines/animal/life_cycle/cow.py"""
    pass


def test_calc_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/life_cycle/cow.py"""
    pass


def test_phosphorus_rqmts():
    """Unit test for function phosphorus_rqmts in file routines/animal/life_cycle/cow.py"""
    pass


def test_calc_daily_walking_dist():
    """Unit test for function calc_daily_walking_dist in file routines/animal/life_cycle/cow.py"""
    pass


def test_get_bw_change():
    """Unit test for function get_bw_change in file routines/animal/life_cycle/cow.py"""
    pass


def test_update():
    """Unit test for function update in file routines/animal/life_cycle/cow.py"""
    pass


def test__determine_estrus_day():
    """Unit test for function _determine_estrus_day in file routines/animal/life_cycle/cow.py"""
    pass


def test__restart_estrus():
    """Unit test for function _restart_estrus in file routines/animal/life_cycle/cow.py"""
    pass


def test__later_estrus():
    """Unit test for function _later_estrus in file routines/animal/life_cycle/cow.py"""
    pass


def test__return_estrus():
    """Unit test for function _return_estrus in file routines/animal/life_cycle/cow.py"""
    pass


def test__after_ai_estrus():
    """Unit test for function _after_ai_estrus in file routines/animal/life_cycle/cow.py"""
    pass


def test__after_abortion_estrus():
    """Unit test for function _after_abortion_estrus in file routines/animal/life_cycle/cow.py"""
    pass


def test__ed_update():
    """Unit test for function _ed_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__determine_tai_program_day():
    """Unit test for function _determine_tai_program_day in file routines/animal/life_cycle/cow.py"""
    pass


def test__tai_program_day_after_preg_check():
    """Unit test for function _tai_program_day_after_preg_check in file routines/animal/life_cycle/cow.py"""
    pass


def test__OvSynch56_update():
    """Unit test for function _OvSynch56_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__OvSynch48_update():
    """Unit test for function _OvSynch48_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__CoSynch72_update():
    """Unit test for function _CoSynch72_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__5dCoSynch_update():
    """Unit test for function _5dCoSynch_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__user_defined_update():
    """Unit test for function _user_defined_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__determine_presynch_program_day():
    """Unit test for function _determine_presynch_program_day in file routines/animal/life_cycle/cow.py"""
    pass


def test__presynch_update():
    """Unit test for function _presynch_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__doubleovsynch_update():
    """Unit test for function _doubleovsynch_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__g6g_update():
    """Unit test for function _g6g_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__user_defined_presynch_update():
    """Unit test for function _user_defined_presynch_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__tai_update():
    """Unit test for function _tai_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__ed_tai_update():
    """Unit test for function _ed_tai_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__resynch_ed_tai():
    """Unit test for function _resynch_ed_tai in file routines/animal/life_cycle/cow.py"""
    pass


def test__open():
    """Unit test for function _open in file routines/animal/life_cycle/cow.py"""
    pass


def test__adjust_conception():
    """Unit test for function _adjust_conception in file routines/animal/life_cycle/cow.py"""
    pass


def test__preg_update():
    """Unit test for function _preg_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__cull_update():
    """Unit test for function _cull_update in file routines/animal/life_cycle/cow.py"""
    pass


def test_death_update():
    """Unit test for function death_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__health_cull_update():
    """Unit test for function _health_cull_update in file routines/animal/life_cycle/cow.py"""
    pass


def test_get_heiferI_values():
    """Unit test for function get_heiferI_values in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_calc_nutrient_rqmts():
    """Unit test for function calc_nutrient_rqmts in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_calc_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_phosphorus_rqmts():
    """Unit test for function phosphorus_rqmts in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_get_non_preg_bw_change():
    """Unit test for function get_non_preg_bw_change in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_update():
    """Unit test for function update in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_get_bw_change():
    """Unit test for function get_bw_change in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_init_values():
    """Unit test for function init_values in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_assign_heiferII_values():
    """Unit test for function assign_heiferII_values in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_get_heiferII_values():
    """Unit test for function get_heiferII_values in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_calc_nutrient_rqmts():
    """Unit test for function calc_nutrient_rqmts in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_calc_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_phosphorus_rqmts():
    """Unit test for function phosphorus_rqmts in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_update():
    """Unit test for function update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__determine_estrus_day():
    """Unit test for function _determine_estrus_day in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__return_estrus():
    """Unit test for function _return_estrus in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__after_ai_estrus():
    """Unit test for function _after_ai_estrus in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__after_abortion_estrus():
    """Unit test for function _after_abortion_estrus in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__ed_update():
    """Unit test for function _ed_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__determine_tai_program_day():
    """Unit test for function _determine_tai_program_day in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__tai_program_day_after_abortion():
    """Unit test for function _tai_program_day_after_abortion in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__5dCG2P_update():
    """Unit test for function _5dCG2P_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__5dCGP_update():
    """Unit test for function _5dCGP_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__user_defined_update():
    """Unit test for function _user_defined_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__tai_update():
    """Unit test for function _tai_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__determine_synch_ed_program_day():
    """Unit test for function _determine_synch_ed_program_day in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__determine_synch_ed_estrus_day():
    """Unit test for function _determine_synch_ed_estrus_day in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__synch_ed_program_day_after_abortion():
    """Unit test for function _synch_ed_program_day_after_abortion in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__2P_update():
    """Unit test for function _2P_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__CP_update():
    """Unit test for function _CP_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__synch_ed_update():
    """Unit test for function _synch_ed_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__open():
    """Unit test for function _open in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__preg_update():
    """Unit test for function _preg_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_get_heiferIII_values():
    """Unit test for function get_heiferIII_values in file routines/animal/life_cycle/heiferIII.py"""
    pass


def test_calc_nutrient_rqmts():
    """Unit test for function calc_nutrient_rqmts in file routines/animal/life_cycle/heiferIII.py"""
    pass


def test_calc_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/life_cycle/heiferIII.py"""
    pass


def test_update():
    """Unit test for function update in file routines/animal/life_cycle/heiferIII.py"""
    pass


def test_initialize_herd():
    """Unit test for function initialize_herd in file routines/animal/life_cycle/life_cycle.py"""
    pass


def test_daily_update():
    """Unit test for function daily_update in file routines/animal/life_cycle/life_cycle.py"""
    pass


def test__calc_average():
    """Unit test for function _calc_average in file routines/animal/life_cycle/life_cycle.py"""
    pass


def test_manure_calculations():
    """Unit test for function manure_calculations in file routines/animal/manure/calf_manure_excretion.py"""
    pass


def test_manure_calculations():
    """Unit test for function manure_calculations in file routines/animal/manure/dry_cow_manure_excretion.py"""
    pass


def test_manure_calculations():
    """Unit test for function manure_calculations in file routines/animal/manure/growing_heifer_manure_excretion.py"""
    pass


def test_manure_calculations():
    """Unit test for function manure_calculations in file routines/animal/manure/lactating_cow_manure_excretion.py"""
    pass


def test_optimize():
    """Unit test for function optimize in file routines/animal/ration/calf_ration.py"""
    pass


def test_calc_requirements():
    """Unit test for function calc_requirements in file routines/animal/ration/calf_ration.py"""
    pass


def test_set_globals():
    """Unit test for function set_globals in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_list_reconfig():
    """Unit test for function list_reconfig in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_objective():
    """Unit test for function objective in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_NEmact_constraint():
    """Unit test for function NEmact_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_NEl_constraint():
    """Unit test for function NEl_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_NEgact_constraint():
    """Unit test for function NEgact_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_calcium_constraint():
    """Unit test for function calcium_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_phosphorus_constraint():
    """Unit test for function phosphorus_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_protien_constraint():
    """Unit test for function protien_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_NDF_constraint_1():
    """Unit test for function NDF_constraint_1 in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_NDF_constraint_2():
    """Unit test for function NDF_constraint_2 in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_forage_NDF_constraint():
    """Unit test for function forage_NDF_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_fat_constraint():
    """Unit test for function fat_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_DMI_constraint():
    """Unit test for function DMI_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_energy_req_limit_constraint():
    """Unit test for function energy_req_limit_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_get_ration_vals():
    """Unit test for function get_ration_vals in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_optimize():
    """Unit test for function optimize in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_calc_rqmts():
    """Unit test for function calc_rqmts in file routines/animal/ration/cow_requirements.py"""
    pass


def test_energy_activity_rqmts():
    """Unit test for function energy_activity_rqmts in file routines/animal/ration/cow_requirements.py"""
    pass


def test_optimize():
    """Unit test for function optimize in file routines/animal/ration/growing_heifer_ration.py"""
    pass


def test_calculate_rqmts():
    """Unit test for function calculate_rqmts in file routines/animal/ration/growing_heifer_ration.py"""
    pass


def test_get_ration():
    """Unit test for function get_ration in file routines/animal/ration/hardcoded_ration.py"""
    pass


def test_get_nutrient_rqmts():
    """Unit test for function get_nutrient_rqmts in file routines/animal/ration/hardcoded_ration.py"""
    pass


def test_optimization():
    """Unit test for function optimization in file routines/animal/ration/ration_driver.py"""
    pass


def test_ration_formulation():
    """Unit test for function ration_formulation in file routines/animal/ration/ration_driver.py"""
    pass


def test_ration_report():
    """Unit test for function ration_report in file routines/animal/ration/ration_driver.py"""
    pass


def test_set_requirements():
    """Unit test for function set_requirements in file routines/animal/ration/ration_driver.py"""
    pass


def test_feed_nutrients():
    """Unit test for function feed_nutrients in file routines/animal/ration/ration_driver.py"""
    pass


def test_get_feed_data_from_feed_ids() -> None:
    """Unit test for function get_feed_data_from_feed_ids in file routines/animal/ration/ration_driver.py"""

    # Arrange
    feed_ids = {155, 157}
    available_feeds = AvailableFeeds()
    available_feeds.feed_id = [136, 139, 155, 157]
    available_feeds.CP = [0, 0, 25.4, 18]
    available_feeds.DE = [0, 0, 5.59, 3.69]
    available_feeds.EE = [0, 0, 30.8, 3]
    available_feeds.Kd = [0, 0, 0, 0]
    available_feeds.NDF = [0, 0, 0, 0]
    available_feeds.N_A = [0, 0, 0, 0]
    available_feeds.N_B = [0, 0, 0, 0]
    available_feeds.TDN = [0, 0, 0, 0]
    available_feeds.calcium = [22, 34, 1, 0.7]
    available_feeds.dRUP = [0, 0, 0, 0]
    available_feeds.dry_cow_limit = [100, 100, 100, 100]
    available_feeds.feed_key = ['136', '139', '155', '157']
    available_feeds.is_fat = [0, 0, 0, None]
    available_feeds.is_wetforage = [0, 0, 0, None]
    available_feeds.lactating_cow_limit = [100, 100, 100, 100]
    available_feeds.phosphorus = [19.3, 0, 0.75, 0.45]
    available_feeds.price = [0.1, 0.05, 0.82, 0.44]
    available_feeds.type = ['Mineral', 'Mineral', 'Milk', 'Starter']

    # Assert before
    assert len(available_feeds._feed_id_to_list_idx_dict) == 0

    # Act
    pen_specific_feed_data = available_feeds.get_feed_data_from_feed_ids(
        feed_ids)

    # Assert after
    expected_feed_id_to_list_idx_dict = {
        136: 0,
        139: 1,
        155: 2,
        157: 3
    }
    assert available_feeds._feed_id_to_list_idx_dict == expected_feed_id_to_list_idx_dict

    expected_pen_specific_feed_data = {
        'feed_id': [155, 157],
        'heiferIII_limit': [],
        'heiferII_limit': [],
        'heiferI_limit': [],
        'calf_limit': [],
        'CP': [25.4, 18],
        'DE': [5.59, 3.69],
        'EE': [30.8, 3],
        'Kd': [0, 0],
        'NDF': [0, 0],
        'N_A': [0, 0],
        'N_B': [0, 0],
        'TDN': [0, 0],
        'calcium': [1, 0.7],
        'dRUP': [0, 0],
        'dry_cow_limit': [100, 100],
        'feed_key': ['155', '157'],
        'is_fat': [0, None],
        'is_wetforage': [0, None],
        'lactating_cow_limit': [100, 100],
        'phosphorus': [0.75, 0.45],
        'price': [0.82, 0.44],
        'type': ['Milk', 'Starter']
    }
    assert pen_specific_feed_data == expected_pen_specific_feed_data
