"""Integration regressions: actual RuFaS modules, datasets and solver (no fake motor)."""
import json
import sys
import unittest
from unittest.mock import patch
from rufas_data import holstein_profile, catalog, ROOT, POPULATION
from rufas_solver import (Formulator, planejar, validate, Supply, NASEMRequirementsAdapter,
                          NASEMRequirementsCalculator, NRCRequirementsCalculator, MODEL)


class NativeIntegrationTests(unittest.TestCase):
    def test_profile_is_a_real_holstein_cow(self):
        p=holstein_profile()
        animals=json.loads((ROOT/POPULATION).read_text())['cows']
        cow=next(a for a in animals if a['id']==p['animal_id'])
        self.assertEqual(cow['breed'],'HO')
        self.assertEqual(cow['body_weight'],validate({})['peso_vivo'])
        self.assertEqual(cow['days_in_milk'],validate({})['del_dias'])

    def test_independent_nasem_package_is_not_loaded(self):
        self.assertNotIn('nasem_dairy',sys.modules)

    def test_correct_library_for_each_standard(self):
        for standard in ('NRC','NASEM'):
            f=Formulator({'padrao':standard})
            self.assertTrue(type(f.feeds[0]).__name__.startswith(standard))
            self.assertEqual(f.feeds[0].__class__.__module__,'RUFAS.data_structures.feed_storage_to_animal_connection')

    def test_native_requirements_are_actually_called(self):
        for standard,cls in [('NRC',NRCRequirementsCalculator),('NASEM',NASEMRequirementsCalculator)]:
            with patch.object(cls,'calculate_requirements',wraps=cls.calculate_requirements) as native:
                f=Formulator({'padrao':standard});f.evaluate(f.seed([0]),0)
                self.assertGreater(native.call_count,0)
                self.assertEqual(native.call_args.kwargs['body_weight'],f.s['peso_vivo'])

    def test_starch_boundary_is_percent_dm_not_kg(self):
        f=Formulator({});x=f.seed([0])
        with patch.object(Supply,'calculate_NASEM_metabolizable_energy',wraps=Supply.calculate_NASEM_metabolizable_energy) as native:
            _,_,diag,_,_=f.evaluate(x,0)
        self.assertAlmostEqual(native.call_args.args[3],diag['amido_pct'])
        self.assertNotAlmostEqual(native.call_args.args[3],diag['amido_kg'])

    def test_stock_total_and_zero_are_distinct_from_unlimited(self):
        f=Formulator({'estoques':{'51':10000}})
        self.assertAlmostEqual(next(i for i in f.limit_report() if i['id']==51)['kg_ms_vaca_dia'],10000/3000)
        f=Formulator({'estoques':{'51':0}})
        self.assertEqual(next(i for i in f.limit_report() if i['id']==51)['kg_ms_vaca_dia'],0)

    def test_impossible_budget_fails_before_supply_search(self):
        f=Formulator({'orcamento_dia':1});r,_=f.solve(0)
        self.assertFalse(r['sucesso']);self.assertEqual(r['status'],'inviavel_linear');self.assertEqual(f.calls,0)

    def test_full_horizon_and_fixed_milk_both_standards(self):
        for standard in ('NRC','NASEM'):
            with self.subTest(standard=standard):
                r=planejar({'padrao':standard})
                self.assertTrue(r['sucesso'],r.get('mensagem'))
                self.assertEqual(r['proveniencia']['modelo'],MODEL)
                self.assertEqual(r['leite_total_kg'],120000)
                daily=[d for p in r['periodos'] for d in p['diario']]
                self.assertEqual(len(daily),30)
                self.assertTrue(all(d['menor_residuo']>=-1e-5 for d in daily))
                self.assertEqual(daily[-1]['del_dias'],119)
                self.assertNotEqual(daily[0]['exigencias'],daily[-1]['exigencias'])
                for p in r['periodos']:
                    self.assertTrue(all(c['atendida'] for c in p['resultado']['restricoes']))
                    self.assertAlmostEqual(sum(i['custo_dia'] for i in p['resultado']['ingredientes']),p['resultado']['custo_total_dia'])

    def test_price_exclusion_and_limited_stock_both_standards(self):
        for standard in ('NRC','NASEM'):
            cases=[{'precos_custom':{'51':.30}}, {'alimentos_bloqueados':[51]}, {'estoques':{'51':10000}}]
            for change in cases:
                with self.subTest(standard=standard,change=change):
                    r=planejar({'padrao':standard,**change})
                    self.assertTrue(r['sucesso'],r.get('detalhe_solver',r.get('mensagem')))
                    ingredients=r['periodos'][0]['resultado']['ingredientes']
                    if 'alimentos_bloqueados' in change:self.assertNotIn(51,[i['id'] for i in ingredients])
                    if 'estoques' in change:
                        total=sum(p['dias']*100*sum(i['kg_ms'] for i in p['resultado']['ingredientes'] if i['id']==51) for p in r['periodos'])
                        self.assertLessEqual(total,10000+.001)

    def test_blocks_keep_the_user_interval(self):
        r=planejar({'dias_simulacao':6,'intervalo_dieta':3})
        self.assertTrue(r['sucesso'],r.get('mensagem'))
        self.assertEqual([(p['inicio'],p['fim']) for p in r['periodos']],[(1,3),(4,6)])

    def test_unknown_breed_and_unsupported_premix_fail_explicitly(self):
        for change in ({'raca':'JE'},{'premix_composicao':{'Zn':100}},{'dias_simulacao':201}):
            with self.assertRaises(ValueError):validate(change)

    def test_nonpregnant_has_no_invented_gestation_before_dim100(self):
        f=Formulator({'dias_gestacao':0})
        for day in (0,9,10,29,149):
            with self.subTest(day=day):
                req=f.requirements(day)
                self.assertEqual(req.pregnancy_energy,0.)
        # The boundary no longer creates a sudden MP fall at DIM 100.
        self.assertLess(abs(f.requirements(9).metabolizable_protein-f.requirements(10).metabolizable_protein),1.)

    def test_adapter_preserves_pregnant_and_known_uterine_states(self):
        for args in [(True,18,90,.2,.204),(True,200,90,30.,5.),(True,None,50,30.,5.)]:
            self.assertEqual(NASEMRequirementsAdapter._calculate_pregnancy_energy_requirements(*args),
                             NASEMRequirementsCalculator._calculate_pregnancy_energy_requirements(*args))
        f=Formulator({})
        self.assertGreater(f.requirements(0).pregnancy_energy,0.)

    def test_user_nonpregnant_150_day_scenario(self):
        r=planejar({'dias_gestacao':0,'dias_simulacao':150,'preco_leite_kg':3.})
        self.assertTrue(r['sucesso'],r.get('mensagem'))
        self.assertEqual(len(r['periodos']),5)
        self.assertEqual(r['leite_total_kg'],600000)
        daily=[d for p in r['periodos'] for d in p['diario']]
        self.assertEqual(len(daily),150)
        self.assertTrue(all(d['menor_residuo']>=-1e-5 for d in daily))


if __name__=='__main__':unittest.main()
