"""Dieta de custo mínimo por programação linear, com as exigências do NRC (2001).

Vaca de referência: coluna Holandesa de 54,4 kg de leite da Tabela 14-7 (680 kg de peso vivo,
90 dias em lactação, 3,5% de gordura e 3,0% de proteína verdadeira no leite).

Fontes dos dados:
- Composição dos alimentos: biblioteca NRC do RuFaS (input/data/feed/NRC_comp.csv), igual às
  Tabelas 15-1, 15-2a e 15-3 do livro nos alimentos conferidos.
- Energia (NEL-4X): Tabela 15-1 (coluna em alimentos_precos.csv).
- Absorção de Ca e P: Capítulo 6 e Tabela 15-4.
- Preços: alimentos_precos.csv, com fonte e data de cada cotação.

Uso, a partir da raiz do projeto:
    .venv/bin/python helpful_scripts/nrc2001_dieta_lp/solver.py
    .venv/bin/python helpful_scripts/nrc2001_dieta_lp/solver.py --sensibilidade
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linprog

PASTA = Path(__file__).resolve().parent
BIBLIOTECA = PASTA.parents[1] / "input" / "data" / "feed" / "NRC_comp.csv"
PRECOS = PASTA / "alimentos_precos.csv"

# Vaca e exigências da Tabela 14-7 (coluna Holandesa, 54,4 kg de leite)
PESO_VIVO = 680.0
EXIG_NEL = 48.3  # Mcal/dia
EXIG_RDP = 2947.0  # g/dia
EXIG_PM = 3476.0  # g/dia
EXIG_CA_ABS = 88.0  # g/dia
EXIG_P_ABS = 80.3  # g/dia
MS_TABELA = 30.0  # kg de MS que a tabela usa para converter % da dieta em gramas
EXIG_MINERAIS_PCT = [("Mg", 0.21), ("K", 1.07), ("Na", 0.22), ("Cl", 0.29), ("S", 0.20)]
MS_MIN, MS_MAX = 30.0, 30.95  # faixa de consumo (escolha nossa: 30 kg da tabela até 30,95 kg da dieta do livro)

# Coeficientes de absorção (Ca, P) por fonte: Tabela 15-4 e Capítulo 6. Demais: forragem 0,30/0,64; outros 0,60/0,70.
ABSORCAO = {234: (0.70, 0.0), 231: (0.94, 0.75), 239: (0.0, 0.0), 67: (0.80, 0.70)}
GORDURA_SUPLEMENTAR = {58, 169, 67}  # oleaginosas e sabões de cálcio (Capítulo 3)
FONTES_MINERAIS = set(range(229, 252))  # sem NFC: cinzas = 100% da MS
TETO_CAROCO = {58: 2.53}  # maior quantidade de caroço nas dietas da Tabela 14-7 (escolha nossa)

COLUNAS_BIBLIOTECA = {
    "DM": "MS", "TDN": "TDN", "CP": "PB", "EE": "EE", "NDF": "NDF", "ADF": "ADF", "ash": "cinzas",
    "calcium": "Ca", "phosphorus": "P", "magnesium": "Mg", "potassium": "K", "sodium": "Na",
    "chlorine": "Cl", "sulfur": "S", "N_B": "B", "N_C": "C",
}


def carregar_alimentos():
    """Junta preços e NEL-4X (CSV) com a composição da biblioteca do RuFaS."""
    precos = pd.read_csv(PRECOS)
    precos["preco_kg_natural"] = precos.preco_cotado / precos.kg_por_unidade
    premix = precos[precos.fixo_kg.notna()].iloc[0]
    cand = precos[precos.fixo_kg.isna()].copy()
    cand["rufas_id"] = cand.rufas_id.astype(int)
    lib = pd.read_csv(BIBLIOTECA).set_index("rufas_id")
    linhas = []
    for _, c in cand.iterrows():
        r = lib.loc[c.rufas_id]
        forragem = int(r.feed_type == "Forage")
        tipo_kp = ("umida" if bool(r.is_wetforage) else "seca") if forragem else "conc"
        ac_ca, ac_p = ABSORCAO.get(c.rufas_id, (0.30, 0.64) if forragem else (0.60, 0.70))
        linha = {novo: r[antigo] for antigo, novo in COLUNAS_BIBLIOTECA.items()}
        linha.update(id=c.rufas_id, nome=c.alimento, forragem=forragem, tipo_kp=tipo_kp, NEL=c.nel4x_tab15_1,
                     Kd=max(r.Kd, 1e-9) if r.N_B > 0 else 1.0, dRUP=r.dRUP if r.CP > 0 else 0.0,
                     ac_ca=ac_ca, ac_p=ac_p, preco_natural=c.preco_kg_natural)
        linhas.append(linha)
    F = pd.DataFrame(linhas).fillna(0)
    F.loc[F.id.isin(FONTES_MINERAIS), "cinzas"] = 100.0
    F["preco"] = F.preco_natural / (F.MS / 100)  # R$/kg de MS
    return F, float(premix.fixo_kg), float(premix.preco_kg_natural)


def coeficientes_proteina(F, pv_pct, conc_pct, desconto):
    """RUP, RDP e PM (g/kg de MS) com as equações do Capítulo 5."""
    def kp(tipo, ndf):
        if tipo == "umida":
            return 3.054 + 0.614 * pv_pct
        if tipo == "seca":
            return 3.362 + 0.479 * pv_pct - 0.007 * conc_pct - 0.017 * ndf
        return 2.904 + 1.375 * pv_pct - 0.020 * conc_pct

    k = np.array([kp(t, n) for t, n in zip(F.tipo_kp, F.NDF)])
    rup_pct = F.B.values * k / (F.Kd.values + k) + F.C.values
    rup = F.PB.values * rup_pct / 100 * 10
    rdp = F.PB.values * 10 - rup
    rup_dig = rup * F.dRUP.values / 100
    pm_ndt = 0.64 * 0.13 * F.TDN.values * desconto * 10 + rup_dig + 0.4 * 11.8  # proteína microbiana limitada por NDT
    pm_rdp = 0.64 * 0.85 * rdp + rup_dig + 0.4 * 11.8  # proteína microbiana limitada por RDP
    return rup, rdp, pm_ndt, pm_rdp


def restricoes_percentuais(F):
    """Restrições em % da MS total: Tabela 4-3, Capítulos 3, 5 e 6."""
    nfc = (100 - (F.NDF + F.PB + F.EE + F.cinzas)).clip(lower=0).values
    ndf_f = (F.NDF * F.forragem).values
    gord_sup = (F.EE * F.id.isin(GORDURA_SUPLEMENTAR)).values
    return [
        ("NDF de forragem >= 15%", "ge", ndf_f, 15), ("NDF >= 25%", "ge", F.NDF.values, 25),
        ("ADF >= 17%", "ge", F.ADF.values, 17), ("NDF + 2 NDFf >= 63%", "ge", F.NDF.values + 2 * ndf_f, 63),
        ("ADF + NDFf >= 36%", "ge", F.ADF.values + ndf_f, 36), ("NFC <= 44%", "le", nfc, 44),
        ("NFC - 2 NDFf <= 6%", "le", nfc - 2 * ndf_f, 6), ("EE <= 7%", "le", F.EE.values, 7),
        ("Gordura suplementar <= 4%", "le", gord_sup, 4), ("Ca <= 1%", "le", F.Ca.values, 1.0),
        ("P <= 0,42%", "le", F.P.values, 0.42), ("PB <= 19%", "le", F.PB.values, 19.0),
    ]


def montar_restricoes(F, premix_kg, coef):
    """Monta A_ub·x <= b_ub. Restrições em % viram Σ(a_i - b)·x_i >= b·premix (linear)."""
    rup, rdp, pm_ndt, pm_rdp = coef
    em_gramas = [
        ("Energia (NEL)", F.NEL.values, EXIG_NEL), ("RDP", rdp, EXIG_RDP),
        ("Ca absorvível", F.Ca.values * 10 * F.ac_ca.values, EXIG_CA_ABS),
        ("P absorvível", F.P.values * 10 * F.ac_p.values, EXIG_P_ABS),
    ]
    em_gramas += [(nome, F[nome].values * 10, pct * MS_TABELA * 10) for nome, pct in EXIG_MINERAIS_PCT]
    em_gramas += [("Ca >= P", (F.Ca - F.P).values * 10, 0), ("Ca <= 7 P", (7 * F.P - F.Ca).values * 10, 0),
                  ("PM (microbiana por NDT)", pm_ndt, EXIG_PM), ("PM (microbiana por RDP)", pm_rdp, EXIG_PM)]
    A = [-a for _, a, _ in em_gramas]
    b = [-v for _, _, v in em_gramas]
    nomes = [n for n, _, _ in em_gramas]
    for nome, sentido, a, lim in restricoes_percentuais(F):
        A.append(-(a - lim) if sentido == "ge" else a - lim)
        b.append(-lim * premix_kg if sentido == "ge" else lim * premix_kg)
        nomes.append(nome)
    n = len(F)
    A += [np.ones(n), -np.ones(n)]
    b += [MS_MAX - premix_kg, -(MS_MIN - premix_kg)]
    nomes += ["Consumo de MS <= 30,95 kg", "Consumo de MS >= 30 kg"]
    return np.array(A), np.array(b), nomes


def ponto_da_dieta(F, x, premix_kg):
    """Consumo em % do peso vivo, % de concentrado e desconto do NDT da dieta resolvida."""
    total = x.sum() + premix_kg
    ndt = float(F.TDN.values @ x) / 100
    ndt_pct = 100 * ndt / total
    multiplo = ndt / (0.035 * (PESO_VIVO * 0.96) ** 0.75)
    desconto = (ndt_pct - (0.18 * ndt_pct - 10.3) * (multiplo - 1)) / ndt_pct if ndt_pct >= 60 else 1.0
    conc_pct = 100 * (1 - x[F.forragem.values == 1].sum() / total)
    return 100 * total / PESO_VIVO, conc_pct, desconto


def resolver(F, premix_kg, premix_preco, teto=None):
    """Resolve com simplex (HiGHS dual simplex) e repete até a taxa de passagem e o desconto estabilizarem."""
    limites = [(0, (teto or {}).get(int(i))) for i in F.id]
    ponto = (4.55, 40.6, 0.837)  # partida: dieta da Tabela 14-7
    for iteracao in range(1, 51):
        coef = coeficientes_proteina(F, *ponto)
        A, b, nomes = montar_restricoes(F, premix_kg, coef)
        r = linprog(F.preco.values, A_ub=A, b_ub=b, bounds=limites, method="highs-ds")
        if r.status != 0:
            raise RuntimeError(f"Problema sem solução: {r.message}")
        novo = ponto_da_dieta(F, r.x, premix_kg)
        if max(abs(u - v) for u, v in zip(novo, ponto)) < 1e-6:
            break
        ponto = novo
    custo = float(F.preco.values @ r.x) + premix_kg * premix_preco
    return dict(x=r.x, custo=custo, A=A, b=b, nomes=nomes, r=r, coef=coef, ponto=ponto, iteracoes=iteracao,
                total=r.x.sum() + premix_kg)


def relatorio(titulo, F, s, premix_kg, premix_preco):
    """Imprime a dieta, o custo por ingrediente, a conferência das exigências e as restrições ativas."""
    x, total = s["x"], s["total"]
    folga = s["b"] - s["A"] @ x
    print(f"\n=== {titulo}: R$ {s['custo']:.2f}/dia (R$ {s['custo'] / 54.4:.3f}/kg de leite)")
    pv_pct, conc_pct, desconto = s["ponto"]
    print(f"    consumo {total:.2f} kg MS | ponto fixo: {pv_pct:.2f}% do PV, {conc_pct:.1f}% de concentrado,"
          f" desconto {desconto:.3f} | iterações {s['iteracoes']} | restrições violadas {int((folga < -1e-6).sum())}")
    print(f"    {'Alimento':<22}{'kg MS':>8}{'kg natural':>12}{'R$/kg MS':>10}{'R$':>8}")
    for i in np.where(x > 1e-4)[0]:
        print(f"    {F.nome[i]:<22}{x[i]:8.2f}{x[i] / (F.MS[i] / 100):12.2f}{F.preco[i]:10.3f}{x[i] * F.preco[i]:8.2f}")
    custo_premix = premix_kg * premix_preco
    print(f"    {'Premix (fixo)':<22}{premix_kg:8.2f}{premix_kg:12.2f}{premix_preco:10.3f}{custo_premix:8.2f}")
    rup, rdp, pm_ndt, pm_rdp = s["coef"]
    print(f"    NEL {F.NEL.values @ x:.2f} Mcal | RDP {rdp @ x:.0f} g | RUP {rup @ x:.0f} g |"
          f" PM {min(pm_ndt @ x, pm_rdp @ x):.0f} g | PB {F.PB.values @ x / total:.1f}%"
          f" | EE {F.EE.values @ x / total:.2f}% | NDF {F.NDF.values @ x / total:.1f}%")
    print("    Restrições no limite:", ", ".join(n for n, f in zip(s["nomes"], folga) if abs(f) < 1e-6))
    custo_reduzido = s["r"].lower.marginals
    print("    Fora da dieta (quanto o preço por kg de MS teria de cair para entrar):")
    for i in np.where(x <= 1e-4)[0]:
        print(f"      {F.nome[i]:<22} R$ {F.preco[i]:.3f} -> cair R$ {custo_reduzido[i]:.3f}"
              f" ({100 * custo_reduzido[i] / F.preco[i]:.0f}%)")


def sensibilidade(F, premix_kg, premix_preco):
    """Testes da versão com teto de caroço: preços alternativos e dieta sem premix."""
    print("\n=== Sensibilidade (com teto de caroço)")
    testes = [("Silagem de milho a R$ 380/t", {51: 0.380}), ("Casca de soja a R$ 1.300/t", {163: 1.300}),
              ("Polpa cítrica a R$ 1,45/kg", {33: 1.45}), ("Farelo de algodão a R$ 1.400/t", {60: 1.400})]
    for titulo, novos in testes:
        G = F.copy()
        for i, preco_natural in novos.items():
            G.loc[G.id == i, "preco"] = preco_natural / (G.loc[G.id == i, "MS"] / 100)
        s = resolver(G, premix_kg, premix_preco, TETO_CAROCO)
        dieta = ", ".join(f"{n} {v:.2f}" for n, v in zip(G.nome, s["x"]) if v > 0.004)
        print(f"  {titulo:<32} R$ {s['custo']:.2f} | {dieta}")
    s = resolver(F, 0.0, premix_preco, TETO_CAROCO)
    print(f"  {'Sem premix':<32} R$ {s['custo']:.2f} (dieta incompleta em vitaminas e microminerais)")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sensibilidade", action="store_true", help="roda também os testes de sensibilidade")
    args = parser.parse_args()
    F, premix_kg, premix_preco = carregar_alimentos()
    relatorio("A. Sem teto por ingrediente", F, resolver(F, premix_kg, premix_preco), premix_kg, premix_preco)
    relatorio("B. Caroço de algodão <= 2,53 kg (recomendada)", F,
              resolver(F, premix_kg, premix_preco, TETO_CAROCO), premix_kg, premix_preco)
    if args.sensibilidade:
        sensibilidade(F, premix_kg, premix_preco)


if __name__ == "__main__":
    main()
