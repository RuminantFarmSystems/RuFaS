"""Modelo dinâmico de dieta de custo mínimo e otimização da produção de leite (NRC 2001).

Permite variar:
- Raça e Peso Vivo (PV em kg)
- Produção de leite (kg/dia), teor de gordura e proteína
- Preços dos alimentos e seleção de candidatos
- Cálculo de IOFC (Income Over Feed Cost) e curva de maximização do lucro.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from scipy.optimize import linprog

PASTA = Path(__file__).resolve().parent
PASTA_NRC = PASTA.parent / "nrc2001_dieta_lp"
BIBLIOTECA = PASTA.parents[1] / "input" / "data" / "feed" / "NRC_comp.csv"
PRECOS_PADRAO = PASTA_NRC / "alimentos_precos.csv"

# Coeficientes de absorção (Ca, P) por fonte
ABSORCAO = {234: (0.70, 0.0), 231: (0.94, 0.75), 239: (0.0, 0.0), 67: (0.80, 0.70)}
GORDURA_SUPLEMENTAR = {58, 169, 67}
FONTES_MINERAIS = set(range(229, 252))

COLUNAS_BIBLIOTECA = {
    "DM": "MS", "TDN": "TDN", "CP": "PB", "EE": "EE", "NDF": "NDF", "ADF": "ADF", "ash": "cinzas",
    "calcium": "Ca", "phosphorus": "P", "magnesium": "Mg", "potassium": "K", "sodium": "Na",
    "chlorine": "Cl", "sulfur": "S", "N_B": "B", "N_C": "C",
}


def calcular_exigencias_nrc(
    peso_vivo: float = 680.0,
    leite_kg: float = 54.4,
    gordura_pct: float = 3.5,
    proteina_pct: float = 3.0,
    del_dias: int = 90,
) -> Dict[str, float]:
    """Calcula exigências nutricionais calibradas pelo NRC (2001) e Tabela 14-7."""
    values = [peso_vivo, leite_kg, gordura_pct, proteina_pct, del_dias]
    if not all(np.isfinite(v) for v in values):
        raise ValueError("Entradas devem ser finitas.")
    if not (300 <= peso_vivo <= 1000 and 0 <= leite_kg <= 80 and
            1 <= gordura_pct <= 8 and 1 <= proteina_pct <= 6 and 1 <= del_dias <= 500):
        raise ValueError("Animal fora do domínio de entrada do estudo.")
    f_pv, f_leite = peso_vivo / 680.0, leite_kg / 54.4
    # Exigências aproximadas: caso NRC tabular calibrado; não substituem o livro.
    f_gord, f_prot = gordura_pct / 3.5, proteina_pct / 3.0
    referencia = (peso_vivo, leite_kg, gordura_pct, proteina_pct, del_dias) == (680, 54.4, 3.5, 3.0, 90)
    cms = (0.372 * (0.4 * leite_kg + 15 * leite_kg * gordura_pct / 100) +
           0.0968 * peso_vivo ** 0.75) * (1 - np.exp(-0.192 * (del_dias / 7 + 3.67)))
    return dict(peso_vivo=peso_vivo, leite_kg=leite_kg,
                exig_nel=10.64 * f_pv ** 0.75 + 37.66 * f_leite * (0.5*f_gord+0.5*f_prot),
                exig_pm=400*f_pv**0.75+3076*f_leite*f_prot,
                exig_rdp=650*f_pv+2297*f_leite,
                exig_ca_abs=18*f_pv+70*f_leite*f_gord,
                exig_p_abs=15*f_pv+65.3*f_leite,
                ms_esperado=30.0 if referencia else float(cms),
                ms_min=30.0 if referencia else float(cms*0.98),
                ms_max=30.95 if referencia else float(cms*1.032),
                cobertura="NRC 2001 tabular" if referencia else "NRC aproximado; exigências calibradas, CMS por DEL")


def carregar_dataframe_alimentos(precos_custom: Optional[Dict[int, float]] = None) -> tuple:
    """Carrega dados dos alimentos com preços atualizados ou customizados."""
    precos = pd.read_csv(PRECOS_PADRAO)
    precos["preco_kg_natural"] = precos.preco_cotado / precos.kg_por_unidade

    if precos_custom:
        if any(not np.isfinite(v) or v < 0 for v in precos_custom.values()):
            raise ValueError("Preços devem ser finitos e não negativos.")
        if set(precos_custom) - set(precos.rufas_id.dropna().astype(int)):
            raise ValueError("Identificador de alimento desconhecido.")
        for rid, p_nat in precos_custom.items():
            precos.loc[precos.rufas_id == rid, "preco_kg_natural"] = float(p_nat)

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
        linha.update(
            id=int(c.rufas_id),
            nome=c.alimento,
            forragem=forragem,
            tipo_kp=tipo_kp,
            NEL=c.nel4x_tab15_1,
            Kd=max(r.Kd, 1e-9) if r.N_B > 0 else 1.0,
            dRUP=r.dRUP if r.CP > 0 else 0.0,
            ac_ca=ac_ca,
            ac_p=ac_p,
            preco_natural=float(c.preco_kg_natural),
        )
        linhas.append(linha)

    F = pd.DataFrame(linhas).fillna(0)
    F.loc[F.id.isin(FONTES_MINERAIS), "cinzas"] = 100.0
    F["preco"] = F.preco_natural / (F.MS / 100.0)  # R$/kg de MS
    return F, float(premix.fixo_kg), float(premix.preco_kg_natural)


def otimizar_dieta(
    peso_vivo: float = 680.0,
    leite_kg: float = 54.4,
    gordura_pct: float = 3.5,
    proteina_pct: float = 3.0,
    del_dias: int = 90,
    precos_custom: Optional[Dict[int, float]] = None,
    alimentos_bloqueados: Optional[List[int]] = None,
    teto_caroco: Optional[float] = 2.53,
    preco_leite_kg: float = 2.75,
) -> Dict[str, Any]:
    """Resolve a dieta de custo mínimo e calcula indicadores econômicos."""
    if not np.isfinite(preco_leite_kg) or preco_leite_kg < 0:
        raise ValueError("Preço do leite inválido.")
    if teto_caroco is not None and (not np.isfinite(teto_caroco) or teto_caroco < 0):
        raise ValueError("Teto do caroço inválido.")
    exig = calcular_exigencias_nrc(peso_vivo, leite_kg, gordura_pct, proteina_pct, del_dias)
    F_full, premix_kg, premix_preco = carregar_dataframe_alimentos(precos_custom)

    # Filtrar alimentos excluídos
    alimentos_bloqueados = alimentos_bloqueados or []
    if set(alimentos_bloqueados) - set(F_full.id):
        raise ValueError("Ingrediente bloqueado desconhecido ou premix fixo.")
    F = F_full[~F_full.id.isin(alimentos_bloqueados)].reset_index(drop=True)
    if F.empty:
        return {"sucesso": False, "mensagem": "Nenhum alimento disponível."}

    def coef_prot(F_df, pv_pct, conc_pct, desconto):
        def kp(tipo, ndf):
            if tipo == "umida":
                return 3.054 + 0.614 * pv_pct
            if tipo == "seca":
                return 3.362 + 0.479 * pv_pct - 0.007 * conc_pct - 0.017 * ndf
            return 2.904 + 1.375 * pv_pct - 0.020 * conc_pct

        k = np.array([kp(t, n) for t, n in zip(F_df.tipo_kp, F_df.NDF)])
        rup_pct = F_df.B.values * k / (F_df.Kd.values + k) + F_df.C.values
        rup = F_df.PB.values * rup_pct / 100.0 * 10.0
        rdp = F_df.PB.values * 10.0 - rup
        rup_dig = rup * F_df.dRUP.values / 100.0
        pm_ndt = 0.64 * 0.13 * F_df.TDN.values * desconto * 10.0 + rup_dig + 0.4 * 11.8
        pm_rdp = 0.64 * 0.85 * rdp + rup_dig + 0.4 * 11.8
        return rup, rdp, pm_ndt, pm_rdp

    def restricoes_pct(F_df):
        nfc = (100.0 - (F_df.NDF + F_df.PB + F_df.EE + F_df.cinzas)).clip(lower=0).values
        ndf_f = (F_df.NDF * F_df.forragem).values
        gord_sup = (F_df.EE * F_df.id.isin(GORDURA_SUPLEMENTAR)).values
        return [
            ("NDF de forragem >= 15%", "ge", ndf_f, 15.0),
            ("NDF >= 25%", "ge", F_df.NDF.values, 25.0),
            ("ADF >= 17%", "ge", F_df.ADF.values, 17.0),
            ("NDF + 2 NDFf >= 63%", "ge", F_df.NDF.values + 2*ndf_f, 63.0),
            ("ADF + NDFf >= 36%", "ge", F_df.ADF.values + ndf_f, 36.0),
            ("NFC - 2 NDFf <= 6%", "le", nfc - 2*ndf_f, 6.0),
            ("NFC <= 44%", "le", nfc, 44.0),
            ("EE <= 7%", "le", F_df.EE.values, 7.0),
            ("Gordura suplementar <= 4%", "le", gord_sup, 4.0),
            ("Ca <= 1%", "le", F_df.Ca.values, 1.0),
            ("P <= 0.42%", "le", F_df.P.values, 0.42),
            ("PB <= 19%", "le", F_df.PB.values, 19.0),
        ]

    def montar_sistema(F_df, coef):
        rup, rdp, pm_ndt, pm_rdp = coef
        em_gramas = [
            ("Energia (NEL)", F_df.NEL.values, exig["exig_nel"]),
            ("RDP", rdp, exig["exig_rdp"]),
            ("Ca absorvível", F_df.Ca.values * 10.0 * F_df.ac_ca.values, exig["exig_ca_abs"]),
            ("P absorvível", F_df.P.values * 10.0 * F_df.ac_p.values, exig["exig_p_abs"]),
            ("PM (microbiana por NDT)", pm_ndt, exig["exig_pm"]),
            ("PM (microbiana por RDP)", pm_rdp, exig["exig_pm"]),
        ]
        # Minerais em % da MS da tabela
        ms_ref = exig["ms_esperado"]
        exig_minerais = [("Mg", 0.21), ("K", 1.07), ("Na", 0.22), ("Cl", 0.29), ("S", 0.20)]
        em_gramas += [(nome, F_df[nome].values * 10.0, pct * ms_ref * 10.0) for nome, pct in exig_minerais]
        em_gramas += [
            ("Ca >= P", (F_df.Ca - F_df.P).values * 10.0, 0.0),
            ("Ca <= 7 P", (7.0 * F_df.P - F_df.Ca).values * 10.0, 0.0),
        ]

        A = [-a for _, a, _ in em_gramas]
        b = [-v for _, _, v in em_gramas]
        nomes = [n for n, _, _ in em_gramas]

        for nome, sentido, a, lim in restricoes_pct(F_df):
            A.append(-(a - lim) if sentido == "ge" else (a - lim))
            b.append(-lim * premix_kg if sentido == "ge" else lim * premix_kg)
            nomes.append(nome)

        n = len(F_df)
        A += [np.ones(n), -np.ones(n)]
        b += [exig["ms_max"] - premix_kg, -(exig["ms_min"] - premix_kg)]
        nomes += [f"Consumo <= {exig['ms_max']:.1f} kg", f"Consumo >= {exig['ms_min']:.1f} kg"]

        return np.array(A), np.array(b), nomes

    def calcular_ponto(F_df, x):
        tot = x.sum() + premix_kg
        ndt = float(F_df.TDN.values @ x) / 100.0
        ndt_pct = 100.0 * ndt / tot if tot > 0 else 60.0
        multiplo = ndt / max(0.001, (0.035 * (peso_vivo * 0.96) ** 0.75))
        desconto = (ndt_pct - (0.18 * ndt_pct - 10.3) * (multiplo - 1.0)) / ndt_pct if ndt_pct >= 60.0 else 1.0
        conc_pct = 100.0 * (1.0 - x[F_df.forragem.values == 1].sum() / tot) if tot > 0 else 40.0
        return 100.0 * tot / peso_vivo, conc_pct, desconto

    # Limites (bounds) por ingrediente
    teto_dict = {58: teto_caroco} if (teto_caroco is not None) else {}
    limites = [(0, teto_dict.get(int(i))) for i in F.id]

    ponto = (4.5, 40.0, 0.85)
    solucao_r = None
    ultimo_coef = None

    convergiu = False
    for iteracao in range(1, 101):
        ultimo_coef = coef_prot(F, *ponto)
        A, b, nomes = montar_sistema(F, ultimo_coef)
        res = linprog(F.preco.values, A_ub=A, b_ub=b, bounds=limites, method="highs-ds")
        if res.status != 0:
            # Segunda estratégia numérica; mantém todas as restrições
            res = linprog(F.preco.values, A_ub=A, b_ub=b, bounds=limites, method="highs")
            if res.status != 0:
                return {
                    "sucesso": False,
                    "mensagem": f"Não foi possível formular dieta viável: {res.message}",
                    "exigencias": exig,
                }
        novo_ponto = calcular_ponto(F, res.x)
        if max(abs(u - v) for u, v in zip(novo_ponto, ponto)) < 1e-8:
            convergiu = True
            solucao_r = res
            ponto = novo_ponto
            break
        ponto = novo_ponto
        solucao_r = res

    if not convergiu:
        return {"sucesso": False, "mensagem": "Iterações não convergiram; dieta rejeitada."}
    x = solucao_r.x
    ultimo_coef = coef_prot(F, *calcular_ponto(F, x))
    A, b, nomes = montar_sistema(F, ultimo_coef)
    folgas = b - A @ x
    validacao = [{"nome": n, "folga": float(f), "tolerancia": float(1e-6*max(1,abs(l))),
                  "atendida": bool(f >= -1e-6*max(1,abs(l)))} for n,f,l in zip(nomes,folgas,b)]
    if not all(v["atendida"] for v in validacao):
        return {"sucesso": False, "mensagem": "Validação final rejeitou a dieta.", "restricoes": validacao}
    total_ms = float(x.sum() + premix_kg)
    custo_alimentos = float(F.preco.values @ x)
    custo_premix = premix_kg * premix_preco
    custo_total = custo_alimentos + custo_premix

    # Indicadores Econômicos
    receita_leite = leite_kg * preco_leite_kg
    custo_por_kg_leite = custo_total / leite_kg if leite_kg > 0 else 0.0
    iofc_dia = receita_leite - custo_total  # Margem sobre Custo Alimentar (Income Over Feed Cost)

    # Detalhar ingredientes selecionados
    itens = []
    for i in np.where(x > 1e-4)[0]:
        ms_item = float(x[i])
        preco_ms = float(F.preco[i])
        ms_pct = float(F.MS[i])
        itens.append({
            "id": int(F.id[i]),
            "nome": str(F.nome[i]),
            "kg_ms": ms_item,
            "kg_natural": ms_item / (ms_pct / 100.0),
            "preco_kg_ms": round(preco_ms, 3),
            "custo_dia": ms_item * preco_ms,
            "pct_dieta": round((ms_item / total_ms) * 100.0, 1),
        })

    # Adicionar Premix fixo
    itens.append({
        "id": 999,
        "nome": "Premix vitamínico e mineral",
        "kg_ms": round(premix_kg, 2),
        "kg_natural": round(premix_kg, 2),
        "preco_kg_ms": round(premix_preco, 3),
        "custo_dia": round(custo_premix, 2),
        "pct_dieta": round((premix_kg / total_ms) * 100.0, 1),
    })

    # Balanço Nutricional
    rup, rdp, pm_ndt, pm_rdp = ultimo_coef
    nel_fornecida = float(F.NEL.values @ x)
    rdp_fornecido = float(rdp @ x)
    rup_fornecido = float(rup @ x)
    pm_fornecido = float(min(pm_ndt @ x, pm_rdp @ x))
    pb_fornecido = float(F.PB.values @ x)
    pb_pct = (pb_fornecido / total_ms) if total_ms > 0 else 0.0
    ee_pct = float(F.EE.values @ x) / total_ms
    ndf_pct = float(F.NDF.values @ x) / total_ms
    ndf_f_pct = float((F.NDF * F.forragem).values @ x) / total_ms

    return {
        "sucesso": True,
        "restricoes": validacao,
        "iteracoes": iteracao,
        "cobertura": exig["cobertura"],
        "avisos": ["Premix sem composição: vitaminas e microminerais não validados.",
                   "Produção é uma meta; não é previsão de leite realizado.",
                   "Ótimo dos LPs iterativos; sem certificado de ótimo global."],
        "custo_total_dia": round(custo_total, 2),
        "custo_por_kg_leite": round(custo_por_kg_leite, 3),
        "receita_leite_dia": round(receita_leite, 2),
        "iofc_margem_dia": round(iofc_dia, 2),
        "consumo_total_ms": round(total_ms, 2),
        "exigencias": exig,
        "ingredientes": sorted(itens, key=lambda it: it["custo_dia"], reverse=True),
        "balanco_nutricional": {
            "nel": {"fornecido": round(nel_fornecida, 2), "exigido": exig["exig_nel"], "unidade": "Mcal/dia"},
            "pm": {"fornecido": round(pm_fornecido, 0), "exigido": exig["exig_pm"], "unidade": "g/dia"},
            "rdp": {"fornecido": round(rdp_fornecido, 0), "exigido": exig["exig_rdp"], "unidade": "g/dia"},
            "rup": {"fornecido": round(rup_fornecido, 0), "unidade": "g/dia"},
            "pb_pct": {"fornecido": round(pb_pct, 1), "unidade": "%"},
            "ee_pct": {"fornecido": round(ee_pct, 2), "unidade": "%"},
            "ndf_pct": {"fornecido": round(ndf_pct, 1), "unidade": "%"},
            "ndf_forragem_pct": {"fornecido": round(ndf_f_pct, 1), "unidade": "%"},
        },
    }


def gerar_curva_otimizacao_leite(faixa_producao=None, **cenario):
    """Sensibilidade por metas; não afirma produção biologicamente atingível."""
    curva = []
    for leite in (faixa_producao or [20, 25, 30, 35, 40, 45, 50, 54.4]):
        parametros = dict(cenario, leite_kg=leite)
        res = otimizar_dieta(**parametros)
        curva.append(dict(leite_kg=leite, sucesso=res["sucesso"],
                          custo=res.get("custo_total_dia"), margem=res.get("iofc_margem_dia"),
                          mensagem=res.get("mensagem")))
    return curva
