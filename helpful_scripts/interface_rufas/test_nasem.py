"""Run with .venv_nasem/bin/python -m unittest discover -s helpful_scripts/interface_rufas -p 'test_nasem.py' -v."""
import unittest
import numpy as np
import nasem_dairy as nd
from nasem_solver import Formulator,validate,library,planejar


class NasemTests(unittest.TestCase):
    def test_upstream_reference(self):
        diet,animal,equations,_=nd.demo('lactating_cow_test')
        result=nd.nasem(diet,animal,equations)
        # Published package example, independent of our optimization implementation.
        self.assertAlmostEqual(result.get_value('Mlk_Prod_NEalow'),31.261172,places=4)
        self.assertAlmostEqual(result.get_value('An_MPIn_g'),2565.213678,places=3)
        self.assertAlmostEqual(result.get_value('Mlk_Prod_MPalow'),35.906472,places=4)

    def test_no_guessed_mapping(self):
        f,*_=library()
        self.assertEqual(len(f),16)
        self.assertNotIn(19,f.id.tolist())
        with self.assertRaises(ValueError):Formulator({'precos_custom':{'19':1}})

    def test_invalid_herd_and_horizon(self):
        for s in [dict(vacas_lactacao=101,tamanho_rebanho=100),dict(dias_simulacao=300),dict(intervalo_dieta=1,dias_simulacao=100),dict(data_inicio='invalid'),dict(estoques={'51':-1})]:
            with self.assertRaises(ValueError):validate(s)

    def test_zero_stock_and_block(self):
        f=Formulator({'estoques':{'51':0},'alimentos_bloqueados':[58]})
        self.assertNotIn(58,f.f.id.tolist())
        idx=f.f.index[f.f.id==51][0]
        self.assertEqual(f.bounds[idx][1],0)

    def test_engine_uses_target_amino_acids(self):
        f=Formulator({})
        seed=__import__('json').loads(__import__('pathlib').Path(__file__).with_name('nasem_seed.json').read_text())
        x=np.array([seed.get(str(int(r.id)),0) for _,r in f.f.iterrows()])
        f.s['leite_kg']=30.
        low=f.evaluate(x,0)
        f.s['leite_kg']=40.
        f.point_cache.clear()
        high=f.evaluate(x,0)
        for key in ['Energia para a produção escolhida','Proteína metabolizável','Aminoácido Met']:
            l=next(c['folga'] for c in low[1] if c['nome']==key)
            h=next(c['folga'] for c in high[1] if c['nome']==key)
            self.assertGreater(l,h)
        self.assertTrue(all(np.isfinite(low[0])))

    def test_premix_units(self):
        f=Formulator({'premix_composicao':{'Ca':200,'Zn':5000,'VitA':10000}})
        self.assertEqual(f.premix['Fd_Ash'],100)
        self.assertEqual(f.premix['Fd_acCa_input'],.70)
        self.assertEqual(f.premix['Fd_Ca'],20)
        self.assertEqual(f.premix['Fd_Zn'],5000)
        with self.assertRaises(ValueError):Formulator({'premix_composicao':{'Ca':1200}})

    def test_fixed_milk_and_optional_budget(self):
        self.assertEqual(validate({})['objetivo'],'custo')
        self.assertIsNone(validate({})['orcamento_dia'])
        for goal in ('producao','margem'):
            with self.assertRaises(ValueError):validate({'objetivo':goal})
        with self.assertRaises(ValueError):validate({'orcamento_dia':0})

    def test_objective_has_only_feed_variables(self):
        from unittest.mock import patch
        from scipy.optimize import OptimizeResult
        f=Formulator({'leite_kg':40})
        def fake_minimize(fun,x0,**kwargs):
            self.assertEqual(len(x0),len(f.f))
            self.assertEqual(len(kwargs['bounds']),len(f.f))
            self.assertAlmostEqual(fun(x0),f.prices@x0+f.q*f.qprice)
            return OptimizeResult(x=x0,success=False,message='intentional test stop',nit=1)
        with patch('nasem_solver.minimize',side_effect=fake_minimize):
            result,_=f.solve(0)
        self.assertFalse(result['sucesso'])

    def test_budget_is_a_constraint_not_a_milk_adjustment(self):
        f=Formulator({'leite_kg':40,'orcamento_dia':1})
        x=np.ones(len(f.f))
        residual,checks,*_=f.evaluate(x,0)
        self.assertLess(next(c['folga'] for c in checks if c['nome']=='Orçamento alimentar'),0)
        self.assertEqual(f.s['leite_kg'],40)



if __name__=='__main__':unittest.main()
