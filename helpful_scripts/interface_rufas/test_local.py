"""Regressões da camada independente: python -m unittest discover -s helpful_scripts/interface_rufas -p 'test_*.py'."""
import math
import unittest
from solver_dinamico import otimizar_dieta, calcular_exigencias_nrc, gerar_curva_otimizacao_leite


class LocalTests(unittest.TestCase):
    def test_reference_and_residuals(self):
        r = otimizar_dieta()
        self.assertTrue(r['sucesso'])
        self.assertAlmostEqual(r['custo_total_dia'],34.54,places=2)
        self.assertEqual(len(r['restricoes']),27)
        self.assertTrue(all(x['atendida'] for x in r['restricoes']))
        self.assertAlmostEqual(sum(i['kg_ms'] for i in r['ingredientes']),r['consumo_total_ms'],places=2)

    def test_block_and_zero_cap(self):
        r = otimizar_dieta(alimentos_bloqueados=[51], teto_caroco=0)
        self.assertTrue(r['sucesso'])
        self.assertFalse({51,58} & {x['id'] for x in r['ingredientes']})

    def test_prices_change_optimum(self):
        base = otimizar_dieta()
        expensive = otimizar_dieta(precos_custom={51:0.380})
        self.assertGreater(expensive['custo_total_dia'],base['custo_total_dia'])
        self.assertNotEqual(expensive['ingredientes'],base['ingredientes'])

    def test_days_affect_intake(self):
        self.assertLess(calcular_exigencias_nrc(del_dias=10)['ms_max'],calcular_exigencias_nrc(del_dias=300)['ms_max'])

    def test_bad_data(self):
        for args in [dict(peso_vivo=0),dict(precos_custom={51:-1}),dict(teto_caroco=-1),dict(preco_leite_kg=math.nan),dict(precos_custom={9999:1})]:
            with self.assertRaises(ValueError):
                otimizar_dieta(**args)

    def test_infeasible(self):
        self.assertFalse(otimizar_dieta(alimentos_bloqueados=[51,156,19,106,44,154,167,169,58,60,163,33,193,67,234,231,239]).get('sucesso'))

    def test_curve_propagation(self):
        r=otimizar_dieta(leite_kg=40,precos_custom={51:.38},alimentos_bloqueados=[58],del_dias=120)
        c=gerar_curva_otimizacao_leite(faixa_producao=[40],precos_custom={51:.38},alimentos_bloqueados=[58],del_dias=120)[0]
        self.assertEqual(c['custo'],r.get('custo_total_dia'))


if __name__=='__main__':
    unittest.main()
