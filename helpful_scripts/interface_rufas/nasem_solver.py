"""NASEM 2021 via nasem_dairy 1.0.2; nonlinear least-cost feeding for a specified milk target.

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
from scipy.optimize import minimize, linprog, least_squares

ROOT = Path(__file__).resolve().parents[2]
VERSION = 'nasem_dairy ' + nd.__version__
MAX_PERIOD_SECONDS = 120

class SearchTimeout(RuntimeError):
    pass


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
    defaults = dict(peso_vivo=680, leite_kg=40, gordura_pct=3.5, proteina_pct=3,
                    lactose_pct=4.8, del_dias=90, preco_leite_kg=2.75, teto_caroco=2.53,
                    dias_simulacao=30, intervalo_dieta=30, vacas_lactacao=100,
                    tamanho_rebanho=100, paridade=2, escore_corporal=3,
                    peso_adulto=700, dias_gestacao=0, temperatura=22, idade_dias=1100,
                    orcamento_dia=None,
                    objetivo='custo', precos_custom={}, alimentos_bloqueados=[], estoques={},
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
                  temperatura=(-10,40),idade_dias=(500,6000))
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
    if c['objetivo'] != 'custo':
        raise ValueError('O objetivo deste estudo é custo mínimo para produção informada.')
    if c['orcamento_dia'] is not None:
        c['orcamento_dia']=float(c['orcamento_dia'])
        if not math.isfinite(c['orcamento_dia']) or c['orcamento_dia']<=0:
            raise ValueError('Orçamento opcional deve ser positivo.')
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
        self.deadline=math.inf
        self.progress=None
        self.last_notice=0.
        self.phase='preparação'
        self.period_started=0.
        self.history=[]

    def evaluate(self,z,day):
        now=time.monotonic()
        if now>self.deadline:
            raise SearchTimeout('Limite de tempo do período atingido; nenhuma dieta não validada foi aceita.')
        if self.progress and now-self.last_notice>=2:
            self.progress(f'{self.phase}: {self.calls} avaliações nutricionais; {max(0,now-self.period_started):.0f}s no período.')
            self.last_notice=now
        key=(day,np.asarray(z).tobytes())
        if key in self.point_cache:
            return self.point_cache[key]
        x=np.asarray(z);s=self.s;y=s['leite_kg'];dmi=float(x.sum()+self.q)
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
        if s['orcamento_dia'] is not None:
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

    def _linear_seed(self, days):
        """Necessary linear checks plus a bounds-aware candidate, never a substitute for nutrition validation."""
        s=self.s
        milk_energy=.0929*s['gordura_pct']+.0547/.93*s['proteina_pct']+.0395*s['lactose_pct']
        capacity=min(nd.calculate_Dt_DMIn_Lact1(s['peso_vivo'],s['escore_corporal'],s['del_dias']+d,s['paridade'],milk_energy*s['leite_kg']) for d in days)
        a=[];b=[]
        # All are the same concentration inequalities used by evaluate().
        for col,limit,lower in [('Fd_NDF',25,True),('Fd_CFat',7,False),('Fd_CP',19,False),('Fd_Ca',1,False),('Fd_P',.42,False)]:
            coeff=self.f[col].to_numpy()-limit
            rhs=(limit-float(self.premix[col]))*self.q
            a.append(-coeff if lower else coeff);b.append(-rhs if lower else rhs)
        coeff=(self.f.Fd_NDF*(1-self.f.Fd_Conc/100)).to_numpy()-15
        a.append(-coeff);b.append(-15*self.q)
        a.append(np.ones(len(self.f)));b.append(capacity-self.q)
        if s['orcamento_dia'] is not None:
            a.append(self.prices);b.append(s['orcamento_dia']-self.q*self.qprice)
        linear=linprog(self.prices,A_ub=np.array(a),b_ub=np.array(b),bounds=self.bounds,method='highs')
        if not linear.success:
            return None,dict(sucesso=False,status='inviavel_linear',mensagem='Os estoques, alimentos, teto de custo ou limites de fibra/minerais são incompatíveis. Confira as quantidades por vaca/dia.',limites=self.limit_report())
        # Use a near-capacity seed if compatible with the linear restrictions.
        target=min(.95*capacity-self.q,sum(hi for _,hi in self.bounds))
        balanced=linprog(self.prices,A_ub=np.array(a),b_ub=np.array(b),A_eq=np.ones((1,len(self.f))),b_eq=[max(.01,target)],bounds=self.bounds,method='highs')
        return balanced.x if balanced.success else linear.x,None

    def limit_report(self):
        return [dict(id=int(r.id),nome=r.nome,kg_ms_vaca_dia=float(self.bounds[j][1]),estoque_total_ms=self.s['estoques'].get(str(int(r.id)))) for j,(_,r) in enumerate(self.f.iterrows())]

    @staticmethod
    def violations(checks):
        return sorted([dict(c,violacao=-c['folga']) for c in checks if c['folga'] < -1e-5*c['escala']],key=lambda c:c['folga']/c['escala'])[:8]

    def solve(self,day,initial=None,span=1,progress=None):
        s=self.s
        started=time.monotonic();self.period_started=started;self.deadline=started+MAX_PERIOD_SECONDS
        self.progress=progress;self.last_notice=0;self.history=[]
        self.phase='Preparando dieta para os alimentos disponíveis'
        checkdays=sorted({day,day+span-1,*[d for d in range(day,day+span) if s['del_dias']+d == 100]})
        z,failure=self._linear_seed(checkdays)
        if failure:return failure,None
        bounds=self.bounds
        all_constraints=lambda x:np.concatenate([self.evaluate(x,d)[0] for d in checkdays])
        def objective(x):return float(self.prices@x+self.q*self.qprice)
        try:
            candidates=[z]
            seed=json.loads(Path(__file__).with_name('nasem_seed.json').read_text())
            candidates.append(np.array([min(max(seed.get(str(int(r.id)),.01),0),hi) for (_,r),(_,hi) in zip(self.f.iterrows(),bounds)]))
            if initial is not None:candidates.append(np.clip(initial,[lo for lo,hi in bounds],[hi for lo,hi in bounds]))
            def merit(x):return float(np.maximum(-all_constraints(x),0)@np.maximum(-all_constraints(x),0))
            z=min(candidates,key=merit)
            # Restore feasibility before asking cost minimization to work from a changed catalogue.
            if min(all_constraints(z)) < -.1:
                self.phase='Buscando uma dieta viável'
                free=np.array([j for j,(lo,hi) in enumerate(bounds) if hi>lo+1e-10])
                if not len(free):
                    return dict(sucesso=False,status='sem_dieta',mensagem='Todos os ingredientes estão bloqueados por limites/estoques.',limites=self.limit_report()),None
                fixed=z.copy()
                def unpack(u):
                    x=fixed.copy();x[free]=u;return x
                restore=least_squares(lambda u:np.minimum(all_constraints(unpack(u)),0),z[free],
                                      bounds=([bounds[j][0] for j in free],[bounds[j][1] for j in free]),
                                      max_nfev=20,ftol=1e-6,xtol=1e-6,gtol=1e-6,diff_step=1e-4)
                z=unpack(restore.x)
            self.phase='Minimizando custo'
            iteration=[0]
            def tick(x):
                iteration[0]+=1
                residual=all_constraints(x)
                _,_,nutr,cost,dmi=self.evaluate(x,day)
                starch=float(nutr.get_value('An_StIn'))
                starch_energy=float(nutr.get_value('An_DEStIn'))
                self.history.append(dict(iteracao=iteration[0],custo=float(cost),menor_residuo=float(min(residual)),
                                         consumo_ms=float(dmi),amido_pct=100*starch/dmi,
                                         ed_amido_mcal_dia=starch_energy,
                                         ed_amido_mcal_kg_amido=starch_energy/starch if starch>1e-10 else None))
                if progress:progress(f'Iteração {iteration[0]}: custo R$ {objective(x):.2f}/vaca/dia; meta fixa {s["leite_kg"]:.2f} kg; maior violação normalizada {max(0,-min(residual)):.3g}.')
            result=minimize(objective,z,method='SLSQP',jac=lambda x:self.prices,bounds=bounds,
                            constraints=[{'type':'ineq','fun':all_constraints}],callback=tick,
                            options={'maxiter':60,'ftol':1e-7,'eps':1e-4})
        except SearchTimeout as exc:
            return dict(sucesso=False,status='limite_tempo',mensagem=str(exc),historico=self.history,limites=self.limit_report()),None
        self.deadline=math.inf
        self.cachekey=None
        self.point_cache.clear()
        residual,checks,out,cost,dmi=self.evaluate(result.x,day)
        for c in checks:c['atendida']=c['folga']>=-1e-5*c['escala']
        success=bool(result.success and min(all_constraints(result.x))>=-1e-5)
        if not success:
            return dict(sucesso=False,status='sem_convergencia',mensagem='Não foi encontrada dieta convergida e validada para esta meta. Reveja os limites indicados ou reduza o intervalo de reformulação.',detalhe_solver=str(result.message),restricoes=checks,violacoes=self.violations(checks),menor_residuo=float(min(residual)),historico=self.history,limites=self.limit_report()),None
        items=[dict(id=int(r.id),nome=r.nome,kg_ms=float(result.x[j]),kg_natural=float(result.x[j]/(r.Fd_DM/100)),custo_dia=float(result.x[j]*self.prices[j])) for j,(_,r) in enumerate(self.f.iterrows()) if result.x[j]>1e-7]
        items.append(dict(id=999,nome='Premix declarado',kg_ms=self.q,kg_natural=self.q,custo_dia=self.q*self.qprice))
        aa=out.get_value('Abs_AA_g');req=out.get_value('Trg_AbsAA_g')
        output=dict(sucesso=True,padrao='NASEM 2021',motor=VERSION,objetivo=s['objetivo'],
                    leite_meta=s['leite_kg'],custo_total_dia=cost,
                    iofc_margem_dia=float(s['preco_leite_kg']*s['leite_kg']-cost),consumo_total_ms=dmi,
                    ingredientes=items,restricoes=checks,iteracoes=int(result.nit),tempo_segundos=time.monotonic()-started,historico=self.history,limites=self.limit_report(),
                    aminoacidos={k:{'oferta':float(aa[k]),'exigencia':float(req[k])} for k in req.index if k!='Arg'},
                    diagnosticos={k:float(out.get_value(k)) for k in ('Trg_NELbal','Mlk_Prod_NEalow','Mlk_Prod_MPalow','An_MPIn_g','Trg_MPIn_req')})
        return output,result.x


def planejar(scenario,progress=None):
    f=Formulator(scenario);s=f.s
    periods=[];initial=None
    for day in range(0,s['dias_simulacao'],s['intervalo_dieta']):
        length=min(s['intervalo_dieta'],s['dias_simulacao']-day)
        if progress:progress(f'Formulando período {len(periods)+1}: dias {day+1}–{day+length}.')
        # Fixed exogenous milk target; only feed quantities are optimized.
        result,solution=f.solve(day,initial,span=length,progress=progress)
        if not result['sucesso']:return dict(result,periodo=day+1)
        # Keep one ration per block and preserve the specified milk target;
        # daily nutrient checks reject invalid blocks rather than hide violations.
        f.deadline=time.monotonic()+MAX_PERIOD_SECONDS
        f.phase='Verificando todos os dias do período'
        daily=[]
        for offset in range(length):
            current=day+offset
            dim=s['del_dias']
            z=solution.copy()
            residual,checks,out,cost,dmi=f.evaluate(z,current)
            if min(residual)<-1e-5:
                return dict(sucesso=False,mensagem='A dieta não atende todos os dias do bloco. Reduza o intervalo de reformulação.',dia=current+1,restricoes=checks)
            daily.append(dict(dia=current+1,data=(datetime.date.fromisoformat(s['data_inicio'])+datetime.timedelta(days=current)).isoformat(),del_dias=dim+current,leite_vaca=s['leite_kg'],leite_rebanho=s['leite_kg']*s['vacas_lactacao'],custo_rebanho=cost*s['vacas_lactacao']))
        periods.append(dict(inicio=day+1,fim=day+length,dias=length,resultado=result,diario=daily))
        initial=solution
    daily=[d for p in periods for d in p['diario']]
    milk=sum(d['leite_rebanho'] for d in daily);cost=sum(d['custo_rebanho'] for d in daily)
    return dict(sucesso=True,padrao='NASEM 2021',motor=VERSION,cenario=s,periodos=periods,
                leite_total_kg=milk,custo_total=cost,margem_total=milk*s['preco_leite_kg']-cost,
                media_leite_vaca=milk/s['vacas_lactacao']/s['dias_simulacao'],
                escopo='Planejamento nutricional por lote homogêneo; não é simulação de fazenda completa.',
                avisos=['Ótimo local SLSQP; sem certificado de ótimo global.',
                         'Produção é uma meta fixa informada; o solver minimiza o custo sem reduzi-la.',
                         'Sem reprodução, secagem, mortalidade ou variação de reservas corporais; horizonte limitado à lactação.',
                         'Custos e produção abrangem somente as vacas em lactação.',
                         'A meta de leite é constante no horizonte; somente as dietas são otimizadas.',
                         'Microminerais/vitaminas só são restrições quando declarados na composição do premix; adequação completa não garantida.',
                         'Estoques são distribuídos como limites diários uniformes para todo o horizonte.'],
                proveniencia={'modelo':'custo-minimo-meta-fixa-v3','versao':VERSION,'numpy':np.__version__,
                              'implementacao_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'partida_sha256':hashlib.sha256(Path(__file__).with_name('nasem_seed.json').read_bytes()).hexdigest(),'biblioteca_sha256':hashlib.sha256(Path(f.source).read_bytes()).hexdigest(),
                              'precos_sha256':hashlib.sha256((ROOT/'helpful_scripts/nrc2001_dieta_lp/alimentos_precos.csv').read_bytes()).hexdigest()})
