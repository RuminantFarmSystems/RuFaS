from typing import List

from pytest import fixture
from pytest_mock import MockerFixture

from RUFAS.routines import AnimalManagement
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.manure_management.misc.simple_animal_management import SimpleAnimalManagement
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen


@fixture
def calf(mocker: MockerFixture) -> Calf:
    c = mocker.MagicMock(spec=Calf)
    return c


@fixture
def heiferI(mocker: MockerFixture) -> HeiferI:
    h1 = mocker.MagicMock(spec=HeiferI)
    return h1


@fixture
def heiferII(mocker: MockerFixture) -> HeiferII:
    h2 = mocker.MagicMock(spec=HeiferII)
    return h2


@fixture
def heiferIII(mocker: MockerFixture) -> HeiferIII:
    h3 = mocker.MagicMock(spec=HeiferIII)
    return h3


@fixture
def cow(mocker: MockerFixture) -> Cow:
    cw = mocker.MagicMock(spec=Cow)
    return cw


@fixture
def pen0(mocker: MockerFixture, calf: Calf) -> Pen:
    p0 = mocker.MagicMock(spec=Pen)
    p0.id = 0
    p0.animals_in_pen = [calf] * 80
    p0.classes_in_pen = {calf.__class__}
    p0.housing_type = 'open air barn'
    p0.bedding_type = 'sand'
    p0.manure_handling = 'manual_scraping'
    p0.manure_separator = 'sedimentation'
    p0.manure_management = 'storage_pit'
    p0.manure = {
        'U': 0,
        'TAN_s': 0,
        'MN': 0,
        'Mkg': 0,
        'TSd': 0,
        'VSd': 0,
        'VSnd': 0,
        'WIP_frac': 0,
        'WOP_frac': 0,
        'p_excrt_manure': 0,
        'p_frac': 0,
        'K_manure': 0,
        'CH4_manure': 0
    }
    return p0


@fixture
def simple_pen0(pen0: Pen) -> SimplePen:
    return SimplePen(pen0)


@fixture
def pen1(mocker: MockerFixture, heiferI) -> Pen:
    p1 = mocker.MagicMock(spec=Pen)
    p1.id = 1
    p1.animals_in_pen = [calf] * 80
    p1.classes_in_pen = {heiferI.__class__}
    p1.housing_type = 'open air barn'
    p1.bedding_type = 'organic'
    p1.manure_handling = 'flush_system'
    p1.manure_separator = 'sedimentation'
    p1.manure_management = 'storage_pit'
    p1.manure = {
        'U': 0,
        'TAN_s': 0,
        'MN': 0,
        'Mkg': 0,
        'TSd': 0,
        'VSd': 0,
        'VSnd': 0,
        'WIP_frac': 0,
        'WOP_frac': 0,
        'p_excrt_manure': 0,
        'p_frac': 0,
        'K_manure': 0,
        'CH4_manure': 0
    }
    return p1


@fixture
def simple_pen1(pen1: Pen) -> SimplePen:
    return SimplePen(pen1)


@fixture
def pen2(mocker: MockerFixture, heiferII) -> Pen:
    p2 = mocker.MagicMock(spec=Pen)
    p2.id = 2
    p2.animals_in_pen = [heiferII] * 383
    p2.classes_in_pen = {heiferI.__class__}
    p2.housing_type = 'open air barn'
    p2.bedding_type = 'organic'
    p2.manure_handling = 'automatic_alley_scrapers'
    p2.manure_separator = 'sedimentation'
    p2.manure_management = 'storage_pit'
    p2.manure = {
        'U': 0,
        'TAN_s': 0,
        'MN': 0,
        'Mkg': 0,
        'TSd': 0,
        'VSd': 0,
        'VSnd': 0,
        'WIP_frac': 0,
        'WOP_frac': 0,
        'p_excrt_manure': 0,
        'p_frac': 0,
        'K_manure': 0,
        'CH4_manure': 0
    }
    return p2


@fixture
def simple_pen2(pen2: Pen) -> SimplePen:
    return SimplePen(pen2)


@fixture
def pen3(mocker: MockerFixture, heiferIII) -> Pen:
    p3 = mocker.MagicMock(spec=Pen)
    p3.id = 3
    p3.animals_in_pen = [heiferIII] * 26
    p3.classes_in_pen = {heiferIII.__class__}
    p3.housing_type = 'open air barn'
    p3.bedding_type = 'sand'
    p3.manure_handling = 'manual_scraping'
    p3.manure_separator = 'sedimentation'
    p3.manure_management = 'anaerobic_lagoon'
    p3.manure = {
        'U': 0,
        'TAN_s': 0,
        'MN': 0,
        'Mkg': 0,
        'TSd': 0,
        'VSd': 0,
        'VSnd': 0,
        'WIP_frac': 0,
        'WOP_frac': 0,
        'p_excrt_manure': 0,
        'p_frac': 0,
        'K_manure': 0,
        'CH4_manure': 0
    }
    return p3


@fixture
def simple_pen3(pen3: Pen) -> SimplePen:
    return SimplePen(pen3)


@fixture
def pen4(mocker: MockerFixture, cow) -> Pen:
    p4 = mocker.MagicMock(spec=Pen)
    p4.id = 4
    p4.animals_in_pen = [cow] * 123
    p4.classes_in_pen = {cow.__class__}
    p4.housing_type = 'open air barn'
    p4.bedding_type = 'sand'
    p4.manure_handling = 'flush_system'
    p4.manure_separator = 'sedimentation'
    p4.manure_management = 'anaerobic_lagoon'
    p4.manure = {
        'U': 41.820000000000086,
        'TAN_s': 17.22000000000003,
        'MN': 29268.368085483322,
        'Mkg': 4625.265486883253,
        'TSd': 555.972373554,
        'VSd': 871751.7989999971,
        'VSnd': 105704.96999999994,
        'WIP_frac': 0.018780355705625296,
        'WOP_frac': 0.0018780355705625281,
        'p_excrt_manure': 1410.266423262114,
        'p_frac': 0.03756071141125059,
        'K_manure': 22543.409151600008,
        'CH4_manure': 32747.032292369433
    }
    return p4


@fixture
def simple_pen4(pen4: Pen) -> SimplePen:
    return SimplePen(pen4)


@fixture
def pen5(mocker: MockerFixture, cow) -> Pen:
    p4 = mocker.MagicMock(spec=Pen)
    p4.id = 5
    p4.animals_in_pen = [cow] * 200
    p4.classes_in_pen = {cow.__class__}
    p4.housing_type = 'open air barn'
    p4.bedding_type = 'sand'
    p4.manure_handling = 'automatic_alley_scrapers'
    p4.manure_separator = 'sedimentation'
    p4.manure_management = 'anaerobic_lagoon'
    p4.manure = {
        'U': -8.21877023874877,
        'TAN_s': -8.471386089652981,
        'MN': 87.07890329618208,
        'Mkg': 13382.668699008762,
        'TSd': 1514.194202561067,
        'VSd': 1490968.8180373649,
        'VSnd': 164883.5777808976,
        'WIP_frac': 0.013321181207350766,
        'WOP_frac': 0.001332118120735078,
        'p_excrt_manure': 1782.0912806622414,
        'p_frac': 0.026642362414701533,
        'K_manure': 21716.207089775304,
        'CH4_manure': 104895.99965614344
    }
    return p4


@fixture
def simple_pen5(pen5: Pen) -> SimplePen:
    return SimplePen(pen5)


@fixture
def pen6(mocker: MockerFixture, cow) -> Pen:
    p6 = mocker.MagicMock(spec=Pen)
    p6.id = 6
    p6.animals_in_pen = [cow] * 300
    p6.classes_in_pen = {cow.__class__}
    p6.housing_type = 'open air barn'
    p6.bedding_type = 'sand'
    p6.manure_handling = 'manual_scraping'
    p6.manure_separator = 'rotary_screen'
    p6.manure_management = 'storage_pit_2'
    p6.manure = {
        'U': -12.31738359791296,
        'TAN_s': -12.695257841678291,
        'MN': 156.20576797571582,
        'Mkg': 21581.473117927293,
        'TSd': 2351.785791504836,
        'VSd': 2351211.8252003524,
        'VSnd': 260845.96680774132,
        'WIP_frac': 0.018676377647928843,
        'WOP_frac': 0.0018676377647928854,
        'p_excrt_manure': 2686.5874891094636,
        'p_frac': 0.03735275529585769,
        'K_manure': 37212.11263776267,
        'CH4_manure': 168967.63229234514
    }
    return p6


@fixture
def simple_pen6(pen6: Pen) -> SimplePen:
    return SimplePen(pen6)


@fixture
def pen7(mocker: MockerFixture, cow) -> Pen:
    p7 = mocker.MagicMock(spec=Pen)
    p7.id = 7
    p7.animals_in_pen = [cow] * 249
    p7.classes_in_pen = {cow.__class__}
    p7.housing_type = 'open air barn'
    p7.bedding_type = 'sand'
    p7.manure_handling = 'flush_system'
    p7.manure_separator = 'rotary_screen'
    p7.manure_management = 'storage_pit_2'
    p7.manure = {
        'U': -10.217003227410219,
        'TAN_s': -10.530013513283803,
        'MN': 145.80000044268039,
        'Mkg': 18175.810710763388,
        'TSd': 1881.623614071462,
        'VSd': 1918330.46651064,
        'VSnd': 214380.5222998497,
        'WIP_frac': 0.015252648668288947,
        'WOP_frac': 0.0015252648668288948,
        'p_excrt_manure': 2226.393919873888,
        'p_frac': 0.030505297336577895,
        'K_manure': 33066.02975698042,
        'CH4_manure': 141797.1071960314
    }
    return p7


@fixture
def simple_pen7(pen7: Pen) -> SimplePen:
    return SimplePen(pen7)


@fixture
def pen8(mocker: MockerFixture, cow) -> Pen:
    p8 = mocker.MagicMock(spec=Pen)
    p8.id = 8
    p8.animals_in_pen = [cow] * 132
    p8.classes_in_pen = {cow.__class__}
    p8.housing_type = 'open air barn'
    p8.bedding_type = 'sand'
    p8.manure_handling = 'automatic_alley_scrapers'
    p8.manure_separator = 'rotary_screen'
    p8.manure_management = 'storage_pit_2'
    p8.manure = {
        'U': -5.4129916927139545,
        'TAN_s': -5.578608713677893,
        'MN': 89.1914881532747,
        'Mkg': 10171.805532863347,
        'TSd': 1005.5661755578118,
        'VSd': 1044165.7072872529,
        'VSnd': 117297.77262013064,
        'WIP_frac': 0.007673538986720085,
        'WOP_frac': 0.0007673538986720084,
        'p_excrt_manure': 1182.56266275683,
        'p_frac': 0.01534707797344017,
        'K_manure': 19649.062405081026,
        'CH4_manure': 79298.06857534732
    }
    return p8


@fixture
def simple_pen8(pen8: Pen) -> SimplePen:
    return SimplePen(pen8)


@fixture
def all_pens(pen0: Pen, pen1: Pen,
             pen2: Pen, pen3: Pen,
             pen4: Pen, pen5: Pen,
             pen6: Pen, pen7: Pen,
             pen8: Pen) -> List[Pen]:
    return [pen0, pen1, pen2, pen3, pen4, pen5, pen6, pen7, pen8]


@fixture
def animal_management(mocker: MockerFixture, all_pens) -> AnimalManagement:
    am = mocker.Mock(spec=AnimalManagement)
    am.all_pens = all_pens
    return am


@fixture
def simple_animal_management(animal_management):
    sam = SimpleAnimalManagement(animal_management)
    return sam


@fixture
def my_pen(mocker: MockerFixture, cow) -> Pen:
    p = mocker.MagicMock(spec=Pen)
    p.id = 100
    p.animals_in_pen = [cow] * 10
    p.classes_in_pen = {cow.__class__}
    p.housing_type = 'open air barn'
    p.bedding_type = 'sand'
    p.manure_handling = 'manual_scraping'
    p.manure_separator = 'rotary_screen'
    p.manure_management = 'storage_pit_2'
    p.manure = {
        'U': 0,
        'TAN_s': 0,
        'MN': 0,
        'Mkg': 0,
        'TSd': 0,
        'VSd': 0,
        'VSnd': 0,
        'WIP_frac': 0,
        'WOP_frac': 0,
        'p_excrt_manure': 0,
        'p_frac': 0,
        'K_manure': 0,
        'CH4_manure': 0
    }
    return p


@fixture
def my_simple_pen(my_pen: Pen) -> SimplePen:
    return SimplePen(my_pen)


@fixture
def my_simple_animal_management(animal_management: AnimalManagement) -> SimpleAnimalManagement:
    sam = SimpleAnimalManagement(animal_management)
    sam.all_pens = [my_simple_pen]
    return sam
