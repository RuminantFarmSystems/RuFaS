from RUFAS.routines.manure_management.data_models.manure import Manure


def test_simple_pen_init_should_get_an_obj_with_correct_attr_values(simple_pen) -> None:
    sp = simple_pen
    assert sp.manure == Manure()
    assert sp.id == 0
    assert sp.animals_in_pen == []
    assert sp.classes_in_pen == set()
    assert sp.housing_type == 'open air barn'
    assert sp.bedding_type == 'organic'
    assert sp.manure_handler == 'manual_scraping'
    assert sp.manure_separator == 'sedimentation'
    assert sp.manure_storage == 'storage_pit'


def test_simple_pen_str_should_return_formatted_str(simple_pen) -> None:
    assert str(simple_pen) == 'SimplePen data: \n' \
                              'manure: Manure(U=0, TAN_s=0, MN=0, Mkg=0, TSd=0, VSd=0, VSnd=0, WIP_frac=0, ' \
                              'WOP_frac=0, p_excrt_manure=0, p_frac=0, K_manure=0, CH4_manure=0) \n' \
                              'id: 0 \n' \
                              'animals_in_pen: [] \n' \
                              'classes_in_pen: set() \n' \
                              'housing_type: open air barn \n' \
                              'bedding_type: organic \n' \
                              'manure_handler: manual_scraping \n' \
                              'manure_separator: sedimentation \n' \
                              'manure_storage: storage_pit \n'
