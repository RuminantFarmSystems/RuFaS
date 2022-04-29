from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.manure_management.data_models.manure import Manure
from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen


def test_simple_pen_init_should_get_an_obj_with_correct_attr_values(simple_pen0) -> None:
    sp = simple_pen0
    assert sp.manure == Manure()
    assert sp.id == 0
    assert all([animal.__class__ is Calf for animal in sp.animals_in_pen])
    assert len(sp.animals_in_pen) == 80
    assert sp.classes_in_pen == {Calf}
    assert sp.housing_type == 'open air barn'
    assert sp.bedding_type == 'sand'
    assert sp.manure_handler == 'manual_scraping'
    assert sp.manure_separator == 'sedimentation'
    assert sp.manure_storage == 'storage_pit'


def test_simple_pen_str_should_return_formatted_str(simple_pen0: SimplePen) -> None:
    assert str(simple_pen0) == '\n'.join([
        f'SimplePen data:',
        f'manure: Manure(U=0, TAN_s=0, MN=0, Mkg=0, TSd=0, VSd=0, VSnd=0, WIP_frac=0, '
        'WOP_frac=0, p_excrt_manure=0, p_frac=0, K_manure=0, CH4_manure=0)',
        f'id: 0',
        f'animals_in_pen: {["Calf"] * 80}',
        f"classes_in_pen: ['Calf']",
        f'housing_type: open air barn',
        f'bedding_type: sand',
        f'manure_handler: manual_scraping',
        f'manure_separator: sedimentation',
        f'manure_storage: storage_pit'
    ])
