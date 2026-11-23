"""NASEM 2021 via nasem_dairy 1.0.2; nonlinear milk-production planning.

The original RuFaS engine and inputs are not modified. Model scope: a homogeneous
lactating cohort, fixed BW/BCS, no reserve mobilization, reoptimized time blocks.
"""
import datetime
import hashlib
import importlib.resources
import json
import math
import time
from pathlib import Path
import warnings

import nasem_dairy as nd
import numpy as np
import pandas as pd
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[2]
VERSION = 'nasem_dairy ' + nd.__version__


def library():
    prices = pd.read_csv(ROOT/'helpful_scripts/nrc2001_dieta_lp/alimentos_precos.csv')
    names = pd.read_csv(ROOT/'input/data/feed/NASEM_Comp_with_TDN_urea.csv').set_index('rufas_id')
    source = importlib.resources.files('nasem_dairy.data.feed_library').joinpath('NASEM_feed_library.csv')
    lib = pd.read_csv(source)
    rows = []
    for _, p in prices[prices.rufas_id.notna()].iterrows():
        if int(p.rufas_id) not in names.index:
            continue
        name = names.loc[int(p.rufas_id), 'Name']
        match = lib[lib.Fd_Name == name]
        if len(match) != 1:
            raise ValueError('Mapeamento NASEM ambíguo: '+name)
        r = match.iloc[0].to_dict()
        r.update(id=int(p.rufas_id), nome=p.alimento, preco_natural=float(p.preco_cotado/p.kg_por_unidade))
        rows.append(r)
    premix = prices[prices.fixo_kg.notna()].iloc[0]
    return pd.DataFrame(rows), lib, float(premix.fixo_kg), float(premix.preco_cotado/premix.kg_por_unidade), str(source)


def validate(s):
    defaults = dict(peso_vivo=680, leite_kg=45, gordura_pct=3.5, proteina_pct=3,
                    lactose_pct=4.8, del_dias=90, preco_leite_kg=2.75, teto_caroco=2.53,
                    dias_simulacao=30, intervalo_dieta=30, vacas_lactacao=100,
                    tamanho_rebanho=100, paridade=2, escore_corporal=3,
                    peso_adulto=700, dias_gestacao=0, temperatura=22, idade_dias=1100,
                    orcamento_dia=45, pico_del=60, declinio_curva=.2,
                    objetivo='producao', precos_custom={}, alimentos_bloqueados=[], estoques={},
                    premix_composicao={}, data_inicio='2026-11-23')
    unknown = set(s)-set(defaults)
    if unknown:
        raise ValueError('Parâmetros desconhecidos: '+', '.join(sorted(unknown)))
    c = {**defaults, **s}
    datetime.date.fromisoformat(c['data_inicio'])
    limits = dict(peso_vivo=(300,1000),leite_kg=(5,80),gordura_pct=(1,8),proteina_pct=(1,6),
                  lactose_pct=(3,6),del_dias=(1,304),preco_leite_kg=(0,30),dias_simulacao=(1,304),
                  intervalo_dieta=(1,30),vacas_lactacao=(1,100000),tamanho_rebanho=(1,100000),
                  paridade=(1,10),escore_corporal=(1,5),peso_adulto=(300,1000),dias_gestacao=(0,220),
                  temperatura=(-10,40),idade_dias=(500,6000),orcamento_dia=(1,1000),pico_del=(20,100),declinio_curva=(.05,.5))
    integers={'dias_simulacao','intervalo_dieta','vacas_lactacao','tamanho_rebanho','paridade','del_dias','dias_gestacao'}
    for key,(lo,hi) in limits.items():
        v=float(c[key])
        if not math.isfinite(v) or not lo <= v <= hi or (key in integers and v != int(v)):
            raise ValueError(f'{key}: valor fora do domínio {lo}–{hi}.')
        c[key]=int(v) if key in integers else v
    if c['vacas_lactacao']>c['tamanho_rebanho']:
        raise ValueError('Vacas em lactação excedem o rebanho.')
    if c['del_dias']+c['dias_simulacao']>305:
        raise ValueError('Este estudo acompanha uma lactação até DEL 305. Reduza o horizonte ou o DEL inicial.')
    if math.ceil(c['dias_simulacao']/c['intervalo_dieta'])>31:
        raise ValueError('Máximo de 31 períodos por cenário. Aumente o intervalo de reformulação.')
    if c['dias_gestacao'] and c['dias_gestacao']+c['dias_simulacao']>250:
        raise ValueError('O horizonte alcança o período seco: use um cenário específico para vacas secas.')
    if c['objetivo'] not in ('producao','margem'):
        raise ValueError('Objetivo inválido.')
    if c['teto_caroco'] is not None:
        c['teto_caroco']=float(c['teto_caroco'])
        if not math.isfinite(c['teto_caroco']) or c['teto_caroco']<0:
            raise ValueError('Teto inválido.')
    for key in ('precos_custom','estoques','premix_composicao'):
        if not isinstance(c[key],dict):
            raise ValueError(key+' deve ser um objeto.')
        c[key]={str(k):float(v) for k,v in c[key].items()}
        if any(not math.isfinite(v) or v<0 for v in c[key].values()):
            raise ValueError(key+': valores não negativos e finitos são necessários.')
    return c


class Formulator:
    def __init__(self, scenario):
        self.s=validate(scenario)
        f,self.lib,self.q,self.qprice,self.source=library()
        ids=set(f.id.astype(str))
        if set(self.s['precos_custom'])-ids or set(self.s['estoques'])-ids:
            raise ValueError('Preço ou estoque para ingrediente sem correspondência NASEM (Tifton não mapeado).')
        if not isinstance(self.s['alimentos_bloqueados'],list):raise ValueError('Bloqueios devem ser uma lista.')
        blocked=set(map(str,self.s['alimentos_bloqueados']))
        if blocked-(ids|{'19'}):
            raise ValueError('Ingrediente bloqueado desconhecido.')
        self.f=f[~f.id.astype(str).isin(blocked)].reset_index(drop=True)
        # Library blanks in mineral concentration fields mean zero contribution.
        for column in ('Fd_Ca','Fd_P','Fd_NDF','Fd_CFat','Fd_CP'):
            self.f[column]=self.f[column].fillna(0.)
        if len(self.f)<2:
            raise ValueError('Ingredientes insuficientes para formular.')
        self.prices=np.array([self.s['precos_custom'].get(str(r.id),r.preco_natural)/(r.Fd_DM/100) for _,r in self.f.iterrows()])
        self.premix=self.lib[self.lib.Fd_Name=='Sodium chloride (salt)'].iloc[0].copy()
        # Full numeric profile for optional user-supplied guarantee per kg DM.
        for key in self.premix.index:
            if key.startswith('Fd_') and key not in ('Fd_Name','Fd_Category','Fd_Type','Fd_Libr'):
                self.premix[key]=0.0
        self.premix['Fd_Name']='Premix declarado';self.premix['Fd_DM']=100.;self.premix['Fd_Conc']=100.
        self.premix['Fd_Ash']=100. # Mineral carrier: do not invent residual organic matter/energy.
        self.premix['Fd_Category']='Vitamin/Mineral';self.premix['Fd_Type']='Concentrate'
        for key in ['Fd_acCa_input','Fd_acPtot_input','Fd_acNa_input','Fd_acCl_input','Fd_acK_input']:
            self.premix[key]=1.
        self.premix['Fd_acCa_input']=.70
        self.premix['Fd_acPtot_input']=.75
        self.premix['Fd_acCl_input']=.92
        allowed={'Ca':'Fd_Ca','P':'Fd_P','Mg':'Fd_Mg','Na':'Fd_Na','Cl':'Fd_Cl','K':'Fd_K','S':'Fd_S',
                 'Co':'Fd_Co','Cu':'Fd_Cu','Fe':'Fd_Fe','I':'Fd_I','Mn':'Fd_Mn','Se':'Fd_Se','Zn':'Fd_Zn',
                 'VitA':'Fd_VitA','VitD':'Fd_VitD','VitE':'Fd_VitE'}
        if set(self.s['premix_composicao'])-set(allowed):
            raise ValueError('Componente do premix desconhecido.')
        for k,v in self.s['premix_composicao'].items():
            # Macro minerals g/kg -> %DM; trace minerals mg/kg and vitamins IU/kg as library.
            self.premix[allowed[k]]=v/10 if k in ('Ca','P','Mg','Na','Cl','K','S') else v
        if sum(self.s['premix_composicao'].get(k,0) for k in ('Ca','P','Mg','Na','Cl','K','S'))>1000:
            raise ValueError('Macrominerais do premix excedem 1.000 g/kg.')
        self.lib=pd.concat([self.lib,pd.DataFrame([self.premix])],ignore_index=True)
        self.names=self.f.Fd_Name.tolist()+['Premix declarado']
        self.base_animal=nd.demo('lactating_cow_test')[1]
        self.eq=nd.demo('lactating_cow_test')[2]
        self.eq.update(DMIn_eqn=0,mProd_eqn=0)
        self.bounds=[(0,min(40.,self.s['estoques'].get(str(r.id),math.inf)/(self.s['vacas_lactacao']*self.s['dias_simulacao']),self.s['teto_caroco'] if r.id==58 and self.s['teto_caroco'] is not None else 40.)) for _,r in self.f.iterrows()]
        self.cachekey=None
        self.point_cache={}
        self.calls=0

    def evaluate(self,z,day):
        key=(day,np.asarray(z).tobytes())
        if key in self.point_cache:
            return self.point_cache[key]
        x=z[:-1];y=float(z[-1]);dmi=float(x.sum()+self.q);s=self.s
        a=dict(self.base_animal,An_BW=s['peso_vivo'],An_BW_mature=s['peso_adulto'],An_BCS=s['escore_corporal'],
               An_Parity_rl=s['paridade'],An_LactDay=s['del_dias']+day,Trg_MilkProd=y,
               Trg_MilkFatp=s['gordura_pct'],Trg_MilkTPp=s['proteina_pct'],Trg_MilkLacp=s['lactose_pct'],
               Trg_Dt_DMIn=dmi,An_GestDay=s['dias_gestacao']+day if s['dias_gestacao'] else 0,
               An_AgeDay=s['idade_dias']+day,Trg_FrmGain=0.,Trg_RsrvGain=0.,Env_TempCurr=s['temperatura'])
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',RuntimeWarning)
            out=nd.nasem(pd.DataFrame({'Feedstuff':self.names,'kg_user':list(x)+[self.q]}),a,self.eq,feed_library=self.lib)
        val=lambda k:float(out.get_value(k))
        capacity=nd.calculate_Dt_DMIn_Lact1(s['peso_vivo'],s['escore_corporal'],s['del_dias']+day,s['paridade'],val('Trg_NEmilk_Milk')*y)
        checks=[]
        def add(name,slack,scale,unit):checks.append(dict(nome=name,folga=float(slack),escala=scale,unidade=unit))
        cost=float(self.prices@x+self.q*self.qprice)
        add('Orçamento alimentar',s['orcamento_dia']-cost,10.,'R$/vaca/dia')
        add('Capacidade de ingestão NASEM',capacity-dmi,10.,'kg MS/dia')
        add('Energia para a produção escolhida',val('Trg_NELbal'),10.,'Mcal/dia')
        add('Proteína metabolizável',val('An_MPIn_g')-val('Trg_MPIn_req'),1000.,'g/dia')
        add('Balanço de proteína degradável',val('An_RDPbal_g'),1000.,'g/dia')
        aa=out.get_value('Abs_AA_g')-out.get_value('Trg_AbsAA_g')
        for k,v in aa.items():
            if k!='Arg':add('Aminoácido '+k,v,100.,'g/dia')
        macro=('Ca','P','Mg','Na','Cl','K','S')
        for k in macro:add('Mineral '+k,val('An_'+k+'_bal'),100.,'g/dia')
        for k in ('Co','Cu','Fe','I','Mn','Se','Zn','VitA','VitD','VitE'):
            if k in s['premix_composicao']:
                add('Garantia '+k,val('An_'+k+'_bal'),max(1,abs(val('An_'+k+'_req'))),'UI/dia' if k.startswith('Vit') else 'mg/dia')
        def pct(column):return float(self.f[column].to_numpy()@x+self.q*self.premix[column])/dmi
        ndf=pct('Fd_NDF');ndff=float((self.f.Fd_NDF*(1-self.f.Fd_Conc/100)).to_numpy()@x)/dmi
        add('FDN mínimo 25%',ndf-25,25.,'% MS');add('FDN de forragem mínimo 15%',ndff-15,15.,'% MS')
        add('Gordura máxima 7%',7-pct('Fd_CFat'),7.,'% MS')
        add('PB máxima 19%',19-pct('Fd_CP'),19.,'% MS')
        add('Ca máximo 1%',1-pct('Fd_Ca'),1.,'% MS')
        add('P máximo 0,42%',.42-pct('Fd_P'),.42,'% MS')
        for j,(_,r) in enumerate(self.f.iterrows()):
            add('Limite '+r.nome,self.bounds[j][1]-x[j],10.,'kg MS/dia')
        residual=np.array([c['folga']/c['escala'] for c in checks])
        if not np.all(np.isfinite(residual)):
            raise ValueError('Resultado nutricional não finito: '+str([(c['nome'],c['folga']) for c in checks if not math.isfinite(c['folga'])]))
        self.calls+=1
        if len(self.point_cache)>128:self.point_cache.clear()
        self.cachekey=key;self.cached=(residual,checks,out,cost,dmi)
        self.point_cache[key]=self.cached
        return self.cached

    def solve(self,day,initial=None,span=1,progress=None):
        s=self.s
        b=s['declinio_curva'];peak=s['pico_del'];dim=s['del_dias']
        potential=min(min(80.,s['leite_kg']*((dim+d)/dim)**b*math.exp(-b/peak*d)) for d in range(day,day+span))
        seed=json.loads(Path(__file__).with_name('nasem_seed.json').read_text())
        x=np.array([seed.get(str(int(r.id)),.01) for _,r in self.f.iterrows()])
        if initial is not None:x=initial[:-1].copy()
        x=np.array([min(max(v,.0001),hi) for v,(_,hi) in zip(x,self.bounds)])
        z=np.r_[x,min(potential,42.) if initial is None else min(potential,initial[-1])]
        bounds=self.bounds+[(1.,potential)]
        def objective(z):
            cost=self.prices@z[:-1]+self.q*self.qprice
            return -z[-1] if s['objetivo']=='producao' else (cost-s['preco_leite_kg']*z[-1])
        checkdays=sorted({day,day+span-1,*[d for d in range(day,day+span) if s['del_dias']+d in (99,100,101)]})
        cons={'type':'ineq','fun':lambda z:np.concatenate([self.evaluate(z,d)[0] for d in checkdays])}
        started=time.monotonic()
        iteration=[0]
        def tick(z):
            iteration[0]+=1
            if progress and iteration[0]%10==0:progress(f'Iteração {iteration[0]}: leite {z[-1]:.2f} kg/vaca/dia; conferindo restrições.')
        result=minimize(objective,z,method='SLSQP',bounds=bounds,constraints=[cons],callback=tick,
                        options={'maxiter':150,'ftol':1e-5,'eps':1e-4})
        # Lexicographic tie-break: minimum feed cost at the attained milk optimum.
        if result.success and s['objetivo']=='producao' and result.x[-1]>=potential-1e-3:
            target=float(result.x[-1])
            second=minimize(lambda z:float(self.prices@z[:-1]),result.x,method='SLSQP',
                            bounds=self.bounds+[(target,target)],constraints=[cons],
                            options={'maxiter':80,'ftol':1e-5,'eps':1e-4})
            if second.success and min(cons['fun'](second.x))>=-1e-5:
                result=second
        self.cachekey=None
        self.point_cache.clear()
        residual,checks,out,cost,dmi=self.evaluate(result.x,day)
        for c in checks:c['atendida']=c['folga']>=-1e-5*c['escala']
        success=bool(result.success and min(cons['fun'](result.x))>=-1e-5)
        if not success:
            return dict(sucesso=False,mensagem='Sem ótimo local convergido e validado: '+result.message,
                        restricoes=checks,menor_residuo=float(min(residual))),None
        items=[dict(id=int(r.id),nome=r.nome,kg_ms=float(result.x[j]),kg_natural=float(result.x[j]/(r.Fd_DM/100)),custo_dia=float(result.x[j]*self.prices[j])) for j,(_,r) in enumerate(self.f.iterrows()) if result.x[j]>1e-7]
        items.append(dict(id=999,nome='Premix declarado',kg_ms=self.q,kg_natural=self.q,custo_dia=self.q*self.qprice))
        aa=out.get_value('Abs_AA_g');req=out.get_value('Trg_AbsAA_g')
        output=dict(sucesso=True,padrao='NASEM 2021',motor=VERSION,objetivo=s['objetivo'],
                    leite_otimizado=float(result.x[-1]),potencial=potential,custo_total_dia=cost,
                    iofc_margem_dia=float(s['preco_leite_kg']*result.x[-1]-cost),consumo_total_ms=dmi,
                    ingredientes=items,restricoes=checks,iteracoes=int(result.nit),tempo_segundos=time.monotonic()-started,
                    aminoacidos={k:{'oferta':float(aa[k]),'exigencia':float(req[k])} for k in req.index if k!='Arg'},
                    diagnosticos={k:float(out.get_value(k)) for k in ('Trg_NELbal','Mlk_Prod_NEalow','Mlk_Prod_MPalow','An_MPIn_g','Trg_MPIn_req')})
        return output,result.x


def planejar(scenario,progress=None):
    f=Formulator(scenario);s=f.s
    periods=[];initial=None
    for day in range(0,s['dias_simulacao'],s['intervalo_dieta']):
        length=min(s['intervalo_dieta'],s['dias_simulacao']-day)
        if progress:progress(f'Formulando período {len(periods)+1}: dias {day+1}–{day+length}.')
        # Constant milk target bounded by the minimum potential over each block; verify daily.
        result,solution=f.solve(day,initial,span=length,progress=progress)
        if not result['sucesso']:return dict(sucesso=False,mensagem=result['mensagem'],periodo=day+1,restricoes=result.get('restricoes'))
        # Keep a single ration and conservative milk target per block;
        # daily capacity and potential checks can reject coarse blocks rather than hide violations.
        daily=[]
        for offset in range(length):
            current=day+offset
            b=s['declinio_curva'];dim=s['del_dias'];cap=min(80.,s['leite_kg']*((dim+current)/dim)**b*math.exp(-b/s['pico_del']*current))
            z=solution.copy();z[-1]=min(z[-1],cap)
            residual,checks,out,cost,dmi=f.evaluate(z,current)
            if min(residual)<-1e-5:
                return dict(sucesso=False,mensagem='A dieta não atende todos os dias do bloco. Reduza o intervalo de reformulação.',dia=current+1,restricoes=checks)
            daily.append(dict(dia=current+1,data=(datetime.date.fromisoformat(s['data_inicio'])+datetime.timedelta(days=current)).isoformat(),del_dias=dim+current,leite_vaca=float(z[-1]),leite_rebanho=float(z[-1]*s['vacas_lactacao']),custo_rebanho=cost*s['vacas_lactacao']))
        periods.append(dict(inicio=day+1,fim=day+length,dias=length,resultado=result,diario=daily))
        initial=solution
    daily=[d for p in periods for d in p['diario']]
    milk=sum(d['leite_rebanho'] for d in daily);cost=sum(d['custo_rebanho'] for d in daily)
    return dict(sucesso=True,padrao='NASEM 2021',motor=VERSION,cenario=s,periodos=periods,
                leite_total_kg=milk,custo_total=cost,margem_total=milk*s['preco_leite_kg']-cost,
                media_leite_vaca=milk/s['vacas_lactacao']/s['dias_simulacao'],
                escopo='Planejamento nutricional por lote homogêneo; não é simulação de fazenda completa.',
                avisos=['Ótimo local SLSQP; sem certificado de ótimo global.',
                         'Potencial e curva de lactação são hipóteses informadas, não genética estimada.',
                         'Sem reprodução, secagem, mortalidade ou variação de reservas corporais; horizonte limitado à lactação.',
                         'Custos e produção abrangem somente as vacas em lactação.',
                         'Cada bloco maximiza uma produção diária constante limitada ao menor potencial do período.',
                         'Microminerais/vitaminas só são restrições quando declarados na composição do premix; adequação completa não garantida.',
                         'Estoques são distribuídos como limites diários uniformes para todo o horizonte.'],
                proveniencia={'versao':VERSION,'numpy':np.__version__,
                              'implementacao_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'biblioteca_sha256':hashlib.sha256(Path(f.source).read_bytes()).hexdigest(),
                              'precos_sha256':hashlib.sha256((ROOT/'helpful_scripts/nrc2001_dieta_lp/alimentos_precos.csv').read_bytes()).hexdigest()})
