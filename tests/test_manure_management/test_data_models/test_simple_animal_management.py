def test_number_of_pens_should_return_10(simple_animal_management) -> None:
    assert len(simple_animal_management.all_pens) == 10


def test_each_pen_should_be_a_unique_obj(simple_animal_management) -> None:
    sam = simple_animal_management
    obj_ids = set([id(p) for p in sam.all_pens])
    assert len(obj_ids) == len(sam.all_pens)


def test_each_pen_should_have_a_unique_pen_id(simple_animal_management) -> None:
    sam = simple_animal_management
    pen_ids = set([p.id for p in sam.all_pens])
    assert len(pen_ids) == len(sam.all_pens)


def test_simple_animal_management_str_should_return_formatted_str(simple_animal_management) -> None:
    sam = simple_animal_management
    sam.all_pens = sam.all_pens[:2]
    assert str(sam) == 'Pen 0: \n' \
                       ' SimplePen data: \n' \
                       'manure: Manure(U=0, TAN_s=0, MN=0, Mkg=0, TSd=0, VSd=0, VSnd=0, WIP_frac=0, ' \
                       'WOP_frac=0, p_excrt_manure=0, p_frac=0, K_manure=0, CH4_manure=0) \n' \
                       'id: 0 \n' \
                       'animals_in_pen: [] \n' \
                       'classes_in_pen: set() \n' \
                       'housing_type: open air barn \n' \
                       'bedding_type: organic \n' \
                       'manure_handler: manual_scraping \n' \
                       'manure_separator: sedimentation \n' \
                       'manure_storage: storage_pit \n' \
                       ' \n' \
                       'Pen 1: \n' \
                       ' SimplePen data: \n' \
                       'manure: Manure(U=0, TAN_s=0, MN=0, Mkg=0, TSd=0, VSd=0, VSnd=0, WIP_frac=0, ' \
                       'WOP_frac=0, p_excrt_manure=0, p_frac=0, K_manure=0, CH4_manure=0) \n' \
                       'id: 1 \n' \
                       'animals_in_pen: [] \n' \
                       'classes_in_pen: set() \n' \
                       'housing_type: open air barn \n' \
                       'bedding_type: organic \n' \
                       'manure_handler: manual_scraping \n' \
                       'manure_separator: sedimentation \n' \
                       'manure_storage: storage_pit \n' \
                       ' \n'
