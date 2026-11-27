"""Dieta de custo mínimo pelo NASEM (2021), escrita com PuLP.

Vaca adulta com 100 dias em lactação da Tabela 21-1. O arquivo segue de cima para baixo: vaca, exigências,
alimentos, rodadas (modelo, restrições, resolver e medir a dieta) e resultado. As rodadas existem porque a
energia e a proteína microbiana de cada alimento dependem da dieta escolhida (consumo, % de amido e fibra e
amido fermentados). A documentação completa está em README.md, nesta pasta.

Uso, a partir da raiz do repositório (requer pulp==2.9.0 e pandas):
    python helpful_scripts/nasem2021_dieta_lp/dieta_pulp.py
"""

from math import exp
from pathlib import Path

import pandas as pd
import pulp

PASTA = Path(__file__).resolve().parent

# ---------------------------------------------------------------- 1. Vaca (Tabela 21-1)
PV, PC_MAT = 700.0, 700.0          # peso corporal e peso adulto (kg)
DEL, GESTACAO = 100, 10            # dias em lactação e dia de gestação
LEITE, GORDURA, PROTEINA, LACTOSE = 55.0, 3.5, 2.83, 4.85   # kg/d e % do leite
GANHO, RESERVAS, ECC = 0.10, 0.21, 3.0                      # kg/d, kg/d e escore corporal (vaca multípara)
IMS_TABELA = 29.4                  # consumo da Tabela 21-1 (kg MS/d)
PREMIX = 0.49                      # premix vitamínico e mineral fixo (kg/d)

# ---------------------------------------------------------------- 2. Exigências (não dependem da dieta)
r = PV / PC_MAT
k = 0.0243 - 0.0000245 * GESTACAO
utero = 0.06275 * PC_MAT * 1.825 * exp(-k * (280 - GESTACAO))   # útero gravídico (kg)
ganho_utero = k * utero                                            # kg/d
ell_por_kg_leite = 0.0929 * GORDURA + 0.0547 / 0.93 * PROTEINA + 0.0395 * LACTOSE

EXIG_ELL = (0.10 * (PV - utero) ** 0.75                                            # mantença
            + (9.4 * (0.067 + 0.375 * r) + 5.55 * (0.201 - 0.081 * r)) * 0.85 * GANHO / 0.61  # crescimento
            + ganho_utero * 0.882 / 0.14 * 0.66                                    # gestação
            + ell_por_kg_leite * LEITE                                             # leite
            + 5.6 * RESERVAS)                                                      # reservas corporais

# PM que não depende da dieta: descamação, leite, crescimento, urina endógena e gestação (g/d)
PM_FIXA = ((0.20 * PV ** 0.60 * 0.85 + PROTEINA * 10 * LEITE + 0.86 * 0.85 * GANHO * (0.201 - 0.081 * r) * 1000)
           / 0.69 + 53 * 6.25 * PV / 1000 + ganho_utero * 125 / 0.33)

# Ca e P absorvíveis que não dependem do consumo: crescimento, gestação e leite (g/d)
escala = (PC_MAT / PV) ** 0.22
g1 = GESTACAO - 1
CA_FIXO = (9.83 * escala * GANHO
           + 0.02456 * (exp((0.05581 - 0.00007 * GESTACAO) * GESTACAO) - exp((0.05581 - 0.00007 * g1) * g1)) * PV / 715
           + (0.295 + 0.239 * PROTEINA) * LEITE)
P_FIXO = 0.0006 * PV + (1.2 + 4.635 * escala) * GANHO + (0.49 + 0.13 * PROTEINA) * LEITE

# Consumo previsto pela Eq. 2-1 (multípara) e faixa permitida
IMS_EQ = ((3.7 + 5.7) + 0.305 * ell_por_kg_leite * LEITE + 0.022 * PV + (-0.689 - 1.87) * ECC) \
    * (1 - (0.212 + 0.136) * exp(-0.053 * DEL))
IMS_MIN, IMS_MAX = min(IMS_EQ, IMS_TABELA), max(IMS_EQ, IMS_TABELA)
PB_LEITE = LEITE * PROTEINA / 100 / 0.93    # kg de PB no leite

# ---------------------------------------------------------------- 3. Alimentos (preços + biblioteca NASEM do RuFaS)
precos = pd.read_csv(PASTA.parent / "nrc2001_dieta_lp" / "alimentos_precos.csv")
precos["preco_natural"] = precos.preco_cotado / precos.kg_por_unidade
PRECO_PREMIX = precos[precos.fixo_kg.notna()].preco_natural.iloc[0]
precos = precos[precos.fixo_kg.isna()].copy()
precos["id"] = precos.rufas_id.astype(int)
precos["id_biblioteca"] = precos.id.replace({19: 18})   # Tifton 85 -> "Bermudagrass hay" (não há Tifton no NASEM)

lib = pd.read_csv(PASTA.parents[1] / "input" / "data" / "feed" / "NASEM_Comp_with_TDN.csv").set_index("rufas_id")
F = lib.loc[precos.id_biblioteca].reset_index(drop=True).fillna(0)
F.index = precos.alimento.values
F["preco"] = precos.preco_natural.values / (F.DM.values / 100)   # R$ por kg de MS
F.loc["Fosfato bicálcico", ["Abs_calcium", "Abs_phosphorus"]] = [0.60, 0.75]   # Tabela 19-3
F.loc["Sabões de cálcio", "calcium"] = 12.0                                   # a Tabela 19-1 não traz o Ca

F["forragem"] = (F.feed_type == "Forage").astype(int)
F["umida"] = F.forragem * (F.DM < 50)                                         # silagens
F["fdn_forragem"] = F.NDF * F.forragem
F["gordura_sup"] = F.EE * F.index.isin(["Caroço de algodão", "Soja grão", "Sabões de cálcio"])
F["pdr"] = F.CP / 100 * (1 - F.RUP / 100)                                     # kg de PDR por kg de MS
F["pndr_dig"] = F.CP / 100 * F.RUP / 100 * F.dRUP / 100                       # kg de PNDR digestível por kg
tem_fdn = (F.NDF > 0) & (F.lignin > 0)
F["dfdn_base"] = (0.75 * (F.NDF - F.lignin) * (1 - (F.lignin / F.NDF) ** 0.667) / F.NDF).where(tem_fdn, 0)  # Eq. 3-3a
F["ed_verdadeira"] = (F.DE_Base + 0.318).where(F.DE_Base > 0, 0)              # ED sem o desconto endógeno fixo

alimentos = list(F.index)
MINERAIS = {"magnesium": 0.18, "potassium": 1.00, "sodium": 0.22, "chlorine": 0.32, "sulfur": 0.20}  # % (21-1)


# ---------------------------------------------------------------- 4. Rodadas
consumo, amido_pct, g, pb_mic = IMS_TABELA, 26.0, 0.97, 2100.0   # chute inicial
for rodada in range(1, 101):
    # Energia (ELL) de 1 kg de cada alimento nesta rodada (Eq. 3-3 a 3-12)
    aj_fdn = -0.0059 * (amido_pct - 26) - 1.1 * (consumo / PV - 0.035)       # Eq. 3-5a
    aj_amido = -1.0 * (consumo / PV - 0.035)                                  # Eq. 3-5b
    pbmf = (11.62 + 13.4 * F.NDF / 100) / 1000                                # PB metabólica fecal (kg/kg)
    ed = F.ed_verdadeira + 0.042 * F.NDF * aj_fdn + 0.0423 * F.starch * aj_amido
    metano = 0.294 - 0.347 * F.FA / consumo + 0.0409 * F.NDF * (F.dfdn_base + aj_fdn) / consumo   # Eq. 3-9
    urina = 0.0146 * 160 * (F.pdr + F.pndr_dig - pbmf)                        # Eq. 3-10
    ell = 0.66 * (ed - (5.65 * pbmf + 0.0040 * 34.3) - metano - urina)        # Eq. 3-12
    c_ell = 0.66 * (-PREMIX * (5.65 * 0.01162 + 0.0040 * 34.3 + 0.294 - 0.0146 * 160 * 0.01162)
                    - 0.00565 * 0.2 * pb_mic + 0.0146 * 160 * (0.2 * pb_mic / 1000 + PB_LEITE))
    pm_mic_base = 0.824 * 0.80 * 6.25 * 101 * g      # PM microbiana fixa (Eq. 6-3)
    pm_por_kg_pdr = 0.824 * 0.80 * 6.25 * 82.6 * g   # PM microbiana por kg de PDR útil

    # Modelo
    model = pulp.LpProblem("Dieta_NASEM", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("x", alimentos, lowBound=0)      # kg de MS de cada alimento
    pdr_util = pulp.LpVariable("pdr_util", lowBound=0)          # PDR aproveitada pelos micróbios (kg)
    T = pulp.lpSum(x[i] for i in alimentos) + PREMIX            # consumo total (kg MS)

    # Função objetivo: custo da dieta (R$/dia)
    model.setObjective(pulp.lpSum(F.preco[i] * x[i] for i in alimentos) + PREMIX * PRECO_PREMIX)

    # Grupo 1: consumo
    model.addConstraint(T >= IMS_MIN, name="consumo_min")
    model.addConstraint(T <= IMS_MAX, name="consumo_max")

    # Grupo 2: energia
    model.addConstraint(pulp.lpSum(ell[i] * x[i] for i in alimentos) + c_ell >= EXIG_ELL, name="energia")

    # Grupo 3: proteína
    model.addConstraint(pm_mic_base + pm_por_kg_pdr * pdr_util
                        + pulp.lpSum(1000 * F.pndr_dig[i] * x[i] for i in alimentos)
                        >= PM_FIXA + 0.73 / 0.69 * (11.62 * T + pulp.lpSum(0.134 * F.NDF[i] * x[i] for i in alimentos)),
                        name="pm")
    model.addConstraint(pdr_util <= pulp.lpSum(F.pdr[i] * x[i] for i in alimentos), name="pdr_util_ate_pdr")
    model.addConstraint(pdr_util <= 0.12 * T, name="pdr_util_ate_12")
    model.addConstraint(pulp.lpSum(100 * F.pdr[i] * x[i] for i in alimentos) >= 10 * T, name="pdr_min")
    model.addConstraint(pulp.lpSum(F.CP[i] * x[i] for i in alimentos) <= 19 * T, name="pb_max")

    # Grupo 4: fibra e amido (Tabela 5-1)
    model.addConstraint(pulp.lpSum(F.fdn_forragem[i] * x[i] for i in alimentos) >= 15 * T, name="fdn_forragem_min")
    model.addConstraint(pulp.lpSum(F.NDF[i] * x[i] for i in alimentos) >= 25 * T, name="fdn_min")
    model.addConstraint(pulp.lpSum(F.starch[i] * x[i] for i in alimentos) <= 30 * T, name="amido_max")
    model.addConstraint(pulp.lpSum((F.NDF[i] + 2 * F.fdn_forragem[i]) * x[i] for i in alimentos) >= 63 * T,
                        name="fdn_mais_2fdnf")
    model.addConstraint(pulp.lpSum((F.starch[i] - 2 * F.fdn_forragem[i]) * x[i] for i in alimentos) <= -8 * T,
                        name="amido_menos_2fdnf")

    # Grupo 5: gordura
    model.addConstraint(pulp.lpSum(F.EE[i] * x[i] for i in alimentos) <= 7 * T, name="ee_max")
    model.addConstraint(pulp.lpSum(F.gordura_sup[i] * x[i] for i in alimentos) <= 4 * T, name="gordura_sup_max")

    # Grupo 6: minerais
    model.addConstraint(pulp.lpSum(F.calcium[i] * 10 * F.Abs_calcium[i] * x[i] for i in alimentos)
                        >= CA_FIXO + 0.90 * T, name="ca_absorvivel")
    model.addConstraint(pulp.lpSum(F.phosphorus[i] * 10 * F.Abs_phosphorus[i] * x[i] for i in alimentos)
                        >= P_FIXO + 1.0 * T, name="p_absorvivel")
    model.addConstraint(pulp.lpSum(F.calcium[i] * x[i] for i in alimentos) <= 1.0 * T, name="ca_max")
    model.addConstraint(pulp.lpSum(F.phosphorus[i] * x[i] for i in alimentos) <= 0.42 * T, name="p_max")
    model.addConstraint(pulp.lpSum((F.calcium[i] - F.phosphorus[i]) * x[i] for i in alimentos) >= 0, name="ca_maior_p")
    model.addConstraint(pulp.lpSum((7 * F.phosphorus[i] - F.calcium[i]) * x[i] for i in alimentos) >= 0,
                        name="ca_ate_7p")
    for mineral, minimo in MINERAIS.items():
        model.addConstraint(pulp.lpSum(F[mineral][i] * x[i] for i in alimentos) >= minimo * T, name=f"{mineral}_min")

    model.solve(pulp.PULP_CBC_CMD(msg=False))

    # Mede a dieta escolhida (Eq. 6-3 e 6-4) e compara com o que foi suposto
    kg = pd.Series({i: x[i].value() for i in alimentos})
    total = kg.sum() + PREMIX
    pct = {c: (kg * F[c]).sum() / total for c in ("NDF", "ADF", "starch", "CP", "fdn_forragem", "umida")}
    pct["umida"] *= 100
    dig_fdn = (-31.9 + 0.721 * pct["NDF"] - 0.247 * pct["starch"] + 6.63 * pct["CP"] - 0.211 * pct["CP"] ** 2
               - 38.7 * pct["ADF"] / pct["NDF"] - 0.121 * pct["umida"] + 1.51 * total)
    dig_amido = (71.2 - 1.45 * total + 0.424 * pct["fdn_forragem"] + 1.39 * pct["starch"]
                 - 0.0219 * pct["starch"] ** 2 - 0.154 * pct["umida"])
    fdn_rumen = dig_fdn * pct["NDF"] / 100 * total / 100        # kg de FDN degradada no rúmen
    amido_rumen = dig_amido * pct["starch"] / 100 * total / 100  # kg de amido degradado no rúmen
    g_novo = 1 / ((1 + 0.094 / fdn_rumen) * (1 + 0.027 / amido_rumen))
    pb_mic_novo = 6.25 * g_novo * (101 + 82.6 * min((kg * F.pdr).sum(), 0.12 * total))
    novo = (total, pct["starch"], g_novo, pb_mic_novo)
    if max(abs(a - b) / max(abs(b), 1.0) for a, b in zip(novo, (consumo, amido_pct, g, pb_mic))) < 1e-8:
        break
    consumo, amido_pct, g, pb_mic = novo

# ---------------------------------------------------------------- 5. Resultado
custo = pulp.value(model.objective)
print(f"Status: {pulp.LpStatus[model.status]} | rodadas: {rodada}")
print(f"Custo: R$ {custo:.2f}/dia (R$ {custo / LEITE:.3f}/kg de leite) | consumo {total:.2f} kg MS")
print(f"\n{'Alimento':<22}{'kg MS':>8}{'kg natural':>12}{'R$':>8}")
for i in alimentos:
    if kg[i] > 1e-4:
        print(f"{i:<22}{kg[i]:8.2f}{kg[i] / (F.DM[i] / 100):12.2f}{kg[i] * F.preco[i]:8.2f}")
print(f"{'Premix (fixo)':<22}{PREMIX:8.2f}{PREMIX:12.2f}{PREMIX * PRECO_PREMIX:8.2f}")
pm_fornecida = 0.824 * 0.80 * pb_mic + 1000 * (kg * F.pndr_dig).sum()
print(f"\nELL: {(kg * ell).sum() + c_ell:.2f} de {EXIG_ELL:.2f} Mcal | PM: {pm_fornecida:.0f} g | "
      f"amido {pct['starch']:.1f}% | PB {pct['CP']:.1f}% | FDN {pct['NDF']:.1f}%")
print("No limite:", ", ".join(n for n, c in model.constraints.items() if abs(c.slack) < 1e-3))
