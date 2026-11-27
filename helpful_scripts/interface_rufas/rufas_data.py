"""Read native RuFaS inputs without loading the scientific engine in the HTTP server."""
import csv
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POPULATION = 'input/data/animal/animal_population.json'
MANAGEMENT = 'input/data/animal/example_freestall_animal.json'
PRICES = 'helpful_scripts/nrc2001_dieta_lp/alimentos_precos.csv'
LIBRARIES = {'NRC': 'input/data/feed/NRC_comp.csv',
             'NASEM': 'input/data/feed/NASEM_Comp_with_TDN_urea.csv'}


@lru_cache(maxsize=1)
def holstein_profile():
    """Use an actual lactating HO cow, not an invented generic breed profile."""
    population = json.loads((ROOT / POPULATION).read_text())
    candidates = [a for a in population['cows']
                  if a['breed'] == 'HO' and a['animal_type'] == 'LacCow' and a['days_in_milk'] > 0]
    cow = min(candidates, key=lambda a: (100 * abs(a['parity'] - 2) + abs(a['days_in_milk'] - 90), a['id']))
    management = json.loads((ROOT / MANAGEMENT).read_text())['animal_config']['management_decisions']
    return dict(raca='HO', nome='Holandesa (Holstein)', animal_id=cow['id'], fonte=POPULATION,
                configuracao=MANAGEMENT,
                parametros=dict(peso_vivo=cow['body_weight'], peso_adulto=cow['mature_body_weight'],
                                del_dias=cow['days_in_milk'], paridade=cow['parity'],
                                dias_gestacao=cow['days_in_pregnancy'], idade_dias=cow['days_born'],
                                intervalo_partos=cow['calving_interval'],
                                gordura_pct=management['milk_fat_percent'],
                                proteina_pct=management['milk_protein_percent']),
                hipoteses={'escore_corporal': 3., 'lactose_pct': 4.8, 'leite_kg': 40.,
                           'alojamento': 'Barn', 'distancia': 0., 'variacao_tecido': 0.})


def catalog(standard):
    if standard not in LIBRARIES:
        raise ValueError('Padrão deve ser NRC ou NASEM.')
    with (ROOT / LIBRARIES[standard]).open(newline='', encoding='utf-8-sig') as stream:
        library = {int(r['rufas_id']): r for r in csv.DictReader(stream)}
    with (ROOT / PRICES).open(newline='', encoding='utf-8-sig') as stream:
        prices = list(csv.DictReader(stream))
    feeds, missing = [], []
    for p in prices:
        if not p['rufas_id']:
            premix = dict(kg_ms=float(p['fixo_kg']), preco=float(p['preco_cotado']) / float(p['kg_por_unidade']))
            continue
        identifier = int(p['rufas_id'])
        if identifier not in library:
            missing.append(p['alimento'])
            continue
        raw = library[identifier]
        feeds.append(dict(id=identifier, nome=p['alimento'], MS=float(raw['DM']),
                          preco_natural=float(p['preco_cotado']) / float(p['kg_por_unidade']),
                          composicao=raw))
    return dict(alimentos=feeds, premix=premix, ausentes=missing, padrao=standard,
                fonte=LIBRARIES[standard], perfil=holstein_profile())
