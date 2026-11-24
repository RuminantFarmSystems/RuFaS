"""Native RuFaS NRC/NASEM nutrition coupled to a local least-cost SLSQP solver.

Only this adapter is extended: native RUFAS/, input/ and the original LP studies
remain intact. Temporal scope is a representative lactating Holstein cohort,
not a replacement for RuFaS's complete herd/disease/reproduction simulation.
"""
import datetime
import hashlib
import json
import math
import sys
import time
from dataclasses import fields

import numpy as np
from scipy.optimize import least_squares, linprog, minimize

try:
    from .rufas_data import ROOT, LIBRARIES, PRICES, POPULATION, MANAGEMENT, catalog, holstein_profile
except ImportError:
    from rufas_data import ROOT, LIBRARIES, PRICES, POPULATION, MANAGEMENT, catalog, holstein_profile
sys.path.insert(0, str(ROOT))
from RUFAS.biophysical.animal.data_types.animal_enums import Breed
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply
from RUFAS.biophysical.animal.nutrients.nrc_requirements_calculator import NRCRequirementsCalculator
from RUFAS.biophysical.animal.nutrients.nasem_requirements_calculator import NASEMRequirementsCalculator
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator as Supply, FeedInRation
from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer, RationConfig
from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.biophysical.animal.digestive_system.manure_excretion_calculator import ManureExcretionCalculator
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    NRCFeed, NASEMFeed, FeedCategorization, FeedComponentType, NutrientStandard,
)
from RUFAS.units import MeasurementUnits

MODEL = 'rufas-nativo-holandesa-custo-v4.1'
MAX_PERIOD_SECONDS = 120
TOLERANCE = 1e-5


class SearchTimeout(RuntimeError):
    pass


class NASEMRequirementsAdapter(NASEMRequirementsCalculator):
    """Guard the native no-pregnancy / missing uterine-state boundary.

    Native maintenance returns zero uterine weights for a nonpregnant cow.
    Native pregnancy then interprets that missing weight as postpartum growth
    before DIM 100, inventing a positive pregnancy burden. This cohort model
    has no postpartum uterine state: do not infer growth from missing zeros.
    All pregnant cases and all other native calculations are unchanged.
    """

    @classmethod
    def _calculate_pregnancy_energy_requirements(
        cls, lactating, day_of_pregnancy, days_in_milk,
        gravid_uterine_weight, uterine_weight,
    ):
        if day_of_pregnancy is None and gravid_uterine_weight == 0 and uterine_weight == 0:
            return 0.0, 0.0
        return super()._calculate_pregnancy_energy_requirements(
            lactating, day_of_pregnancy, days_in_milk,
            gravid_uterine_weight, uterine_weight,
        )


def validate(scenario):
    if not isinstance(scenario, dict):
        raise ValueError('Cenário deve ser um objeto.')
    profile = holstein_profile()
    defaults = dict(**profile['parametros'], **profile['hipoteses'], padrao='NASEM', raca='HO',
                    preco_leite_kg=2.75, teto_caroco=2.53, dias_simulacao=30, intervalo_dieta=30,
                    vacas_lactacao=100, tamanho_rebanho=100, temperatura=22., orcamento_dia=None,
                    objetivo='custo', precos_custom={}, alimentos_bloqueados=[], estoques={},
                    premix_composicao={}, data_inicio=datetime.date.today().isoformat())
    unknown = set(scenario) - set(defaults)
    if unknown:
        raise ValueError('Parâmetros desconhecidos: ' + ', '.join(sorted(unknown)))
    s = {**defaults, **scenario}
    if s['padrao'] not in LIBRARIES or s['raca'] != 'HO' or s['objetivo'] != 'custo':
        raise ValueError('Use NRC/NASEM, raça HO e objetivo custo.')
    datetime.date.fromisoformat(s['data_inicio'])
    limits = dict(peso_vivo=(300,1000), peso_adulto=(300,1100), leite_kg=(5,80),
                  gordura_pct=(1,8), proteina_pct=(1,6), lactose_pct=(3,6),
                  del_dias=(1,304), paridade=(1,10), dias_gestacao=(0,220),
                  idade_dias=(500,6000), intervalo_partos=(280,800),
                  escore_corporal=(1,5), dias_simulacao=(1,304), intervalo_dieta=(1,30),
                  vacas_lactacao=(1,100000), tamanho_rebanho=(1,100000),
                  preco_leite_kg=(0,30), temperatura=(-10,40), distancia=(0,10000), variacao_tecido=(0,0))
    integers = {'del_dias','paridade','dias_gestacao','idade_dias','intervalo_partos',
                'dias_simulacao','intervalo_dieta','vacas_lactacao','tamanho_rebanho'}
    for key, (lo,hi) in limits.items():
        if isinstance(s[key], bool):raise ValueError('Valor inválido: ' + key)
        v = float(s[key])
        if not math.isfinite(v) or not lo <= v <= hi or (key in integers and v != int(v)):
            raise ValueError(f'{key}: fora do domínio {lo}–{hi}.')
        s[key] = int(v) if key in integers else v
    if s['alojamento'] not in ('Barn','Grazing'):raise ValueError('Alojamento inválido.')
    if s['gordura_pct']+s['proteina_pct']+s['lactose_pct'] > 100:raise ValueError('Composição do leite inválida.')
    if s['vacas_lactacao'] > s['tamanho_rebanho']:raise ValueError('Lactantes excedem rebanho.')
    if s['del_dias']+s['dias_simulacao'] > 305:raise ValueError('Horizonte deve permanecer até DEL 305.')
    if s['dias_gestacao'] and s['dias_gestacao']+s['dias_simulacao'] > 218:
        raise ValueError('Horizonte alcança a secagem do perfil RuFaS (gestação de 218 dias).')
    if math.ceil(s['dias_simulacao']/s['intervalo_dieta']) > 31:raise ValueError('Máximo de 31 períodos.')
    for key in ('teto_caroco','orcamento_dia'):
        if s[key] is not None:
            s[key] = float(s[key])
            if not math.isfinite(s[key]) or s[key] < 0:raise ValueError('Limite inválido: '+key)
    for key in ('precos_custom','estoques','premix_composicao'):
        if not isinstance(s[key],dict):raise ValueError(key+' deve ser um objeto.')
        s[key] = {str(k):float(v) for k,v in s[key].items()}
        if any(not math.isfinite(v) or v < 0 for v in s[key].values()):raise ValueError('Valores inválidos: '+key)
    # Native RationOptimizer only enforces Ca/P. Do not imply trace-vitamin validation.
    if set(s['premix_composicao'])-{'Ca','P'}:
        raise ValueError('O fluxo nativo verifica apenas Ca e P do premix, em g/kg MS. Outros componentes não são validados.')
    if sum(s['premix_composicao'].values()) > 1000:raise ValueError('Premix excede 1.000 g/kg.')
    if not isinstance(s['alimentos_bloqueados'],list):raise ValueError('Bloqueios inválidos.')
    s['alimentos_bloqueados'] = list(map(int,s['alimentos_bloqueados']))
    return s


def build_feed(raw, standard, price, maximum, minimum=0.):
    """Construct the real native dataclass, keeping all original composition fields."""
    cls = NASEMFeed if standard == 'NASEM' else NRCFeed
    enums = {'Fd_Category':FeedCategorization,'feed_type':FeedComponentType,'units':MeasurementUnits}
    data = dict(purchase_cost=price, on_farm_cost=0., amount_available=0., buffer=0.,
                limit=maximum, lower_limit=minimum)
    for field in fields(cls):
        key = field.name
        if key in data:continue
        value = raw.get(key)
        if value in ('',None):raise ValueError(f'Campo nativo ausente: {key}, alimento {raw.get("rufas_id")}')
        if key in enums:data[key] = enums[key](value)
        elif key in ('is_fat','is_wetforage'):
            if str(value).upper() not in ('TRUE','FALSE'):raise ValueError('Booleano nativo inválido.')
            data[key] = str(value).upper() == 'TRUE'
        elif key == 'Name':data[key] = value
        elif key == 'rufas_id':data[key] = int(value)
        else:
            data[key] = float(value)
            if not math.isfinite(data[key]):raise ValueError('Composição nativa não finita: '+key)
    return cls(**data)


class Formulator:
    def __init__(self, scenario):
        self.s = validate(scenario)
        self.standard = NutrientStandard(self.s['padrao'])
        self.profile = holstein_profile()
        self.breed = Breed.HO
        self.catalog = catalog(self.s['padrao'])
        self.q = self.catalog['premix']['kg_ms']
        self.qprice = self.catalog['premix']['preco']
        all_ids = {r['id'] for r in self.catalog['alimentos']}
        if set(map(int,self.s['precos_custom']))-all_ids or set(map(int,self.s['estoques']))-all_ids:
            raise ValueError('Preço/estoque informado para alimento sem correspondência no padrão.')
        if set(self.s['alimentos_bloqueados'])-all_ids:raise ValueError('Alimento bloqueado desconhecido no padrão.')
        self.records = sorted([r for r in self.catalog['alimentos'] if r['id'] not in self.s['alimentos_bloqueados']], key=lambda r:r['id'])
        if len(self.records)<2:raise ValueError('Selecione pelo menos dois alimentos.')
        self.feeds = []
        for r in self.records:
            hi = min(40., self.s['estoques'].get(str(r['id']),math.inf)/(self.s['vacas_lactacao']*self.s['dias_simulacao']),
                     float(r['composicao']['limit']))
            if r['id']==58 and self.s['teto_caroco'] is not None:hi=min(hi,self.s['teto_caroco'])
            price = self.s['precos_custom'].get(str(r['id']),r['preco_natural'])/(r['MS']/100)
            self.feeds.append(build_feed(r['composicao'],self.s['padrao'],price,hi))
        # Fixed mineral carrier. No undeclared energy or macro-mineral contributions.
        cls = type(self.feeds[0]);premix = {}
        for f in fields(cls):
            if f.name == 'Name':premix[f.name]='Premix declarado'
            elif f.name=='Fd_Category':premix[f.name]=FeedCategorization.VITAMIN_MINERAL
            elif f.name=='feed_type':premix[f.name]=FeedComponentType.MINERAL
            elif f.name=='units':premix[f.name]=MeasurementUnits.KILOGRAMS
            elif f.name in ('is_fat','is_wetforage'):premix[f.name]=False
            else:premix[f.name]=0.
        premix.update(rufas_id=999,DM=100.,ash=100.,lower_limit=self.q,limit=self.q,purchase_cost=self.qprice,
                      calcium=self.s['premix_composicao'].get('Ca',0.)/10,
                      phosphorus=self.s['premix_composicao'].get('P',0.)/10)
        self.feeds.append(cls(**premix))
        self.bounds=[(0.,f.limit) for f in self.feeds[:-1]]
        self.prices=np.array([f.purchase_cost for f in self.feeds[:-1]])
        self.native=RationOptimizer()
        self.cache={};self.calls=0;self.deadline=math.inf;self.history=[]
        self.progress=None;self.last_notice=0;self.phase='Preparando';self.started=0

    def requirements(self, day, ndf=30., energy=1.6, tdn=.65):
        s=self.s
        params=dict(body_weight=s['peso_vivo'],mature_body_weight=s['peso_adulto'],
                    day_of_pregnancy=s['dias_gestacao']+day if s['dias_gestacao'] else None,
                    body_condition_score_5=s['escore_corporal'],days_in_milk=s['del_dias']+day,
                    average_daily_gain_heifer=None,animal_type=AnimalType.LAC_COW,parity=s['paridade'],
                    calving_interval=s['intervalo_partos'],milk_fat=s['gordura_pct'],milk_true_protein=s['proteina_pct'],
                    milk_lactose=s['lactose_pct'],milk_production=s['leite_kg'],housing=s['alojamento'],
                    distance=s['distancia'],process_based_phosphorus_requirement=0.)
        if self.standard is NutrientStandard.NASEM:
            return NASEMRequirementsAdapter.calculate_requirements(**params,lactating=True,
                           ndf_percentage=ndf,tissue_weight_change=s['variacao_tecido'])
        return NRCRequirementsCalculator.calculate_requirements(**params,previous_temperature=s['temperatura'],
                           net_energy_diet_concentration=energy,days_born=s['idade_dias']+day,TDN_fraction=tdn)

    def config(self, requirement):
        return RationConfig(self.standard,requirement,self.feeds,requirement.dry_matter,
                            requirement.metabolizable_protein,self.s['peso_vivo'],None,None,AnimalCombination.LAC_COW)

    def emissions(self, ration, dmi, day):
        """Only the native IPCC and lactating-manure inputs used for energetic losses."""
        nutrient={k:Supply._calculate_nutritive_content(ration,k) for k in ('NDF','EE','CP','ADF','ash','potassium','starch')}
        supply=NutritionSupply(**{f.name:0. for f in fields(NutritionSupply) if f.init})
        supply.dry_matter=dmi;supply.wet_matter=sum(f.amount/(f.info.DM/100) for f in ration)
        for key,attr in [('NDF','ndf_supply'),('EE','fat_supply'),('CP','crude_protein'),('ADF','adf_supply'),
                         ('ash','ash_supply'),('potassium','potassium_supply'),('starch','starch_supply')]:setattr(supply,attr,nutrient[key])
        # __post_init__ ran before assignments, so refresh its derived field.
        supply.nitrogen_supply=supply.crude_protein/6.25
        methane,_=EntericMethaneCalculator.calculate_cow_methane(True,self.s['peso_vivo'],self.s['gordura_pct'],
                         0.,supply,'',0.,{'cows':{'lactating cows':'IPCC'}})
        _,manure=ManureExcretionCalculator.calculate_cow_manure(True,self.s['peso_vivo'],self.s['del_dias']+day,
                         self.s['proteina_pct'],self.s['leite_kg'],0.,0.,supply)
        if not all(math.isfinite(v) and v>=0 for v in (methane,manure.urine_nitrogen)):
            raise ValueError('Perdas energéticas fora do domínio das equações nativas.')
        return methane,manure.urine_nitrogen

    def evaluate(self, x, day):
        now=time.monotonic()
        if now>self.deadline:raise SearchTimeout('Tempo do período esgotado; nenhuma dieta não validada foi aceita.')
        if self.progress and now-self.last_notice>2:
            self.progress(f'{self.phase}: {self.calls} avaliações nativas RuFaS; {now-self.started:.0f}s.');self.last_notice=now
        key=(day,np.asarray(x).tobytes())
        if key in self.cache:return self.cache[key]
        z=np.append(x,self.q);dmi=float(sum(z))
        ration=RationOptimizer.convert_decision_vec_to_feeds(self.config(self.requirements(day)),z)
        ndf=100*Supply._calculate_nutritive_content(ration,'NDF')/dmi
        tdn=Supply._calculate_nutritive_content(ration,'TDN')/dmi
        if self.standard is NutrientStandard.NRC:
            discount=Supply.calculate_nutrient_intake_discount(ration,self.s['peso_vivo'])
            de={f.info.rufas_id:f.info.DE*discount for f in ration}
            me=Supply.calculate_actual_metabolizable_energy(ration,de)
            energy=Supply.calculate_actual_lactation_net_energy(ration,me,de)/dmi
        else:energy=1.6
        req=self.requirements(day,ndf,energy,tdn);config=self.config(req)
        self.native.set_constraints(config)
        checks=[]
        def add(name,slack,scale,unit):
            if not math.isfinite(float(slack)):raise ValueError('Resultado nativo não finito: '+name)
            checks.append(dict(nome=name,folga=float(slack),escala=scale,unidade=unit,
                               atendida=float(slack)>=-TOLERANCE*scale))
        meta={
            'NE_total_constraint':('Energia líquida total',10.,'Mcal/dia'),
            'NE_maintenance_and_activity_constraint':('Energia de manutenção e atividade',10.,'Mcal/dia'),
            'NE_lactation_constraint':('Energia de lactação e gestação',10.,'Mcal/dia'),
            'NE_growth_constraint':('Energia de crescimento',10.,'Mcal/dia'),
            'protein_constraint_lower':('Proteína metabolizável mínima',1000.,'g/dia'),
            'protein_constraint_upper':('Proteína metabolizável máxima',1000.,'g/dia'),
            'calcium_constraint':('Cálcio absorvível',100.,'g/dia'),
            'phosphorus_constraint':('Fósforo absorvível',100.,'g/dia'),
            'NDF_constraint_lower':('FDN mínima',25.,'% MS'),
            'NDF_constraint_upper':('FDN máxima',25.,'% MS'),
            'forage_NDF_constraint':('FDN de forragem mínima',15.,'% MS'),
            'fat_constraint':('Gordura máxima',7.,'% MS'),
            'DMI_constraint_lower':('Consumo mínimo RuFaS',10.,'kg MS/dia'),
            'DMI_constraint_upper':('Consumo máximo RuFaS',10.,'kg MS/dia')}
        starch=Supply._calculate_nutritive_content(ration,'starch')
        starch_energy=None;losses=None
        for c in self.native._select_constraints(AnimalCombination.LAC_COW):
            fn=c['fun']
            if fn.__name__=='NASEM_net_energy_constraint':
                # Upstream mixes kg starch/day with a reference of 26 (% DM).
                # Correct the boundary unit locally, keeping native scientific code untouched.
                losses=self.emissions(ration,dmi,day)
                me=Supply.calculate_NASEM_metabolizable_energy(ration,dmi,self.s['peso_vivo'],100*starch/dmi,*losses)
                energy=Supply.calculate_NASEM_net_energy(me)
                add('Energia líquida NASEM',energy-req.total_energy_requirement,10.,'Mcal/dia')
                starch_energy=sum(f.amount*.0423*f.info.starch*Supply.calculate_NASEM_dstarch(f,dmi,self.s['peso_vivo']) for f in ration)
            else:
                name,scale,unit=meta[fn.__name__];add(name,fn(z,config),scale,unit)
        cost=RationOptimizer.objective(z,config)
        # Operational caps retained from the previous formulation, in addition
        # to the native RuFaS constraints. They are explicit study choices.
        for nutrient,cap,label in [('CP',19.,'PB máxima 19%'),('calcium',1.,'Ca máximo 1%'),('phosphorus',.42,'P máximo 0,42%')]:
            amount=Supply._calculate_nutritive_content(ration,nutrient)
            add(label,cap-100*amount/dmi,cap,'% MS')
        if self.s['orcamento_dia'] is not None:add('Teto de custo',self.s['orcamento_dia']-cost,10.,'R$/dia')
        for r,f,v in zip(self.records,self.feeds,x):add('Limite '+r['nome'],f.limit-v,10.,'kg MS/dia')
        residual=np.array([c['folga']/c['escala'] for c in checks])
        diagnostics=dict(exigencias={k:float(getattr(req,k)) for k in ('dry_matter','metabolizable_protein','calcium','phosphorus','total_energy_requirement')},
                         amido_kg=float(starch),amido_pct=float(100*starch/dmi),
                         ed_amido_mcal_dia=starch_energy,perdas=None if losses is None else dict(metano_g_dia=float(losses[0]),nitrogenio_urina_kg_dia=float(losses[1])))
        if len(self.cache)>256:self.cache.clear()
        value=(residual,checks,diagnostics,float(cost),dmi);self.cache[key]=value;self.calls+=1
        return value

    def limit_report(self):
        return [dict(id=r['id'],nome=r['nome'],kg_ms_vaca_dia=f.limit,
                     estoque_total_ms=self.s['estoques'].get(str(r['id']))) for r,f in zip(self.records,self.feeds)]

    def seed(self, days):
        """Necessary linear native fibre/intake/fat checks; no nutrient relaxation."""
        config=self.config(self.requirements(days[0]));fraction=config.dmi_constraint_fraction
        dmin=max(self.requirements(d).dry_matter*(1-fraction) for d in days)
        dmax=min(self.requirements(d).dry_matter*(1+fraction) for d in days)
        n=len(self.bounds);ones=np.ones(n)
        from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants as C
        ndf=np.array([f.NDF for f in self.feeds[:-1]])
        fn=np.array([f.NDF if f.feed_type is FeedComponentType.FORAGE else 0 for f in self.feeds[:-1]])
        fat=np.array([f.EE for f in self.feeds[:-1]])
        a=[-ones,ones,C.MINIMUM_RATION_NDF-ndf,ndf-C.MAXIMUM_RATION_NDF,
           C.MINIMUM_RATION_FORAGE_NDF-fn,fat-C.MAXIMUM_RATION_FAT]
        b=[self.q-dmin,dmax-self.q,-C.MINIMUM_RATION_NDF*self.q,C.MAXIMUM_RATION_NDF*self.q,
           -C.MINIMUM_RATION_FORAGE_NDF*self.q,C.MAXIMUM_RATION_FAT*self.q]
        if self.s['orcamento_dia'] is not None:a.append(self.prices);b.append(self.s['orcamento_dia']-self.q*self.qprice)
        for nutrient,cap in [('CP',19.),('calcium',1.),('phosphorus',.42)]:
            a.append(np.array([getattr(f,nutrient)-cap for f in self.feeds[:-1]]))
            b.append((cap-getattr(self.feeds[-1],nutrient))*self.q)
        res=linprog(self.prices,A_ub=np.array(a),b_ub=np.array(b),bounds=self.bounds,method='highs')
        if not res.success:return None
        target=min(dmax-self.q,max(dmin-self.q,config.initial_dry_matter_requirement-self.q))
        balanced=linprog(self.prices,A_ub=np.array(a),b_ub=np.array(b),A_eq=np.ones((1,n)),b_eq=[target],bounds=self.bounds,method='highs')
        return balanced.x if balanced.success else res.x

    def solve(self, day, span=1, initial=None, progress=None):
        self.started=time.monotonic();self.deadline=self.started+MAX_PERIOD_SECONDS
        self.progress=progress;self.history=[];self.phase='Preparando a dieta';self.cache.clear()
        days=sorted({day,day+span-1,*[d for d in range(day,day+span) if self.s['del_dias']+d==100]})
        x=self.seed(days)
        failure=lambda status,msg,**kw:dict(sucesso=False,status=status,mensagem=msg,limites=self.limit_report(),historico=self.history,**kw)
        if x is None:return failure('inviavel_linear','Os limites de alimentos, consumo, fibra ou custo são incompatíveis.'),None
        g=lambda z:np.concatenate([self.evaluate(z,d)[0] for d in days])
        objective=lambda z:float(self.prices@z+self.q*self.qprice)
        try:
            if initial is not None:
                candidate=np.clip(initial,0,[hi for _,hi in self.bounds])
                if np.linalg.norm(np.minimum(g(candidate),0))<np.linalg.norm(np.minimum(g(x),0)):x=candidate
            free=np.array([i for i,(lo,hi) in enumerate(self.bounds) if hi>1e-10])
            if min(g(x)) < -.01 and len(free):
                self.phase='Buscando viabilidade';fixed=x.copy()
                def unpack(u):
                    z=fixed.copy();z[free]=u;return z
                restored=least_squares(lambda u:np.minimum(g(unpack(u)),0),x[free],
                                      bounds=(np.zeros(len(free)),np.array([self.bounds[i][1] for i in free])),
                                      max_nfev=40,ftol=1e-7,xtol=1e-7,gtol=1e-7,diff_step=1e-4)
                x=unpack(restored.x)
            self.phase='Minimizando custo com RuFaS'
            def tick(z):
                residual=g(z);_,_,diag,cost,dmi=self.evaluate(z,day)
                starch=diag['amido_kg'];ed=diag['ed_amido_mcal_dia']
                self.history.append(dict(iteracao=len(self.history)+1,custo=cost,consumo_ms=dmi,
                        amido_pct=diag['amido_pct'],ed_amido_mcal_dia=ed,
                        ed_amido_mcal_kg_amido=ed/starch if ed is not None and starch>1e-10 else None,
                        menor_residuo=float(min(residual))))
                if progress:progress(f'RuFaS {self.s["padrao"]}: iteração {len(self.history)}, custo R$ {cost:.2f}/vaca/dia.')
            # The native NRC model contains min/max branches. If one local
            # search fails, retry deterministically from the restored point
            # with another numerical step/positive cost scale. Constraints,
            # physical units and final acceptance stay exactly the same.
            attempts=[(1.,1e-7 if self.standard is NutrientStandard.NRC else 1e-5),
                      (10.,1e-6),(1.,1e-8)]
            for attempt,(scale,step) in enumerate(attempts,1):
                self.phase=f'Minimizando custo com RuFaS (tentativa {attempt})'
                result=minimize(lambda z:objective(z)/scale,x,jac=lambda z:self.prices/scale,
                                method='SLSQP',bounds=self.bounds,
                                constraints=[{'type':'ineq','fun':g}],callback=tick,
                                options={'maxiter':100,'ftol':1e-7,'eps':step})
                if result.success and min(g(result.x))>=-TOLERANCE:break
            self.cache.clear()
            residual=g(result.x)
            if not result.success or min(residual)<-TOLERANCE:
                _,checks,_,_,_=self.evaluate(result.x,day)
                return failure('sem_convergencia','Não foi encontrada uma dieta convergida e validada para esta meta.',
                               detalhe_solver=str(result.message),restricoes=checks,
                               violacoes=[c for c in checks if not c['atendida']]),None
            _,checks,diag,cost,dmi=self.evaluate(result.x,day)
        except SearchTimeout as exc:return failure('limite_tempo',str(exc)),None
        finally:self.deadline=math.inf
        ingredients=[dict(id=r['id'],nome=r['nome'],kg_ms=float(v),kg_natural=float(v/(f.DM/100)),custo_dia=float(v*f.purchase_cost))
                     for r,f,v in zip(self.records,self.feeds,result.x) if v>1e-7]
        ingredients.append(dict(id=999,nome='Premix declarado',kg_ms=self.q,kg_natural=self.q,custo_dia=self.q*self.qprice))
        return dict(sucesso=True,padrao=self.s['padrao'],motor='RuFaS nativo + SciPy/SLSQP',objetivo='custo',
                    leite_meta=self.s['leite_kg'],custo_total_dia=cost,iofc_margem_dia=self.s['leite_kg']*self.s['preco_leite_kg']-cost,
                    consumo_total_ms=dmi,ingredientes=ingredients,restricoes=checks,diagnosticos=diag,
                    iteracoes=int(result.nit),tempo_segundos=time.monotonic()-self.started,historico=self.history,
                    limites=self.limit_report(),animal=self.profile,aminoacidos={},avisos=warnings_for(self.s)),result.x


def warnings_for(s):
    return ['Integração aos calculadores e restrições nativos RuFaS; não executa a simulação completa de fazenda.',
            'Meta fixa de leite; produção agregada é planejada, não previsão animal.',
            'Não gestantes sem estado uterino pós-parto: o adaptador não infere crescimento gestacional a partir de pesos uterinos ausentes.',
            'Lote homogêneo, peso/escore constantes e estoque distribuído uniformemente. Solução local, sem certificado global.',
            'Tetos operacionais adicionais: PB 19%, Ca 1%, P 0,42% da MS; escolhas do estudo.',
            'Conjunto nativo de restrições: não garante nove aminoácidos, vitaminas ou todos os minerais. Ca/P usam a oferta nativa RuFaS.',
            'Premix sem composição declarada não fornece Ca/P no cálculo. Sua adequação completa não é certificada.',
            'NASEM: o adaptador passa amido em % MS à correção dNDF (referência 26); o núcleo original permanece intacto.']


def provenance(s):
    paths=[LIBRARIES[s['padrao']],PRICES,POPULATION,MANAGEMENT,
           'RUFAS/biophysical/animal/nutrients/nutrition_supply_calculator.py',
           'RUFAS/biophysical/animal/nutrients/'+('nasem' if s['padrao']=='NASEM' else 'nrc')+'_requirements_calculator.py',
           'RUFAS/biophysical/animal/ration/ration_optimizer.py',
           'helpful_scripts/interface_rufas/rufas_solver.py','helpful_scripts/interface_rufas/rufas_data.py']
    import scipy
    return dict(modelo=MODEL,motor='RUFAS',python=sys.version.split()[0],scipy=scipy.__version__,
                arquivos={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths})


def planejar(scenario, progress=None):
    f=Formulator(scenario);s=f.s;periods=[];initial=None
    for day in range(0,s['dias_simulacao'],s['intervalo_dieta']):
        length=min(s['intervalo_dieta'],s['dias_simulacao']-day)
        if progress:progress(f'RuFaS {s["padrao"]}: período {day+1}–{day+length}.')
        result,solution=f.solve(day,span=length,initial=initial,progress=progress)
        if not result['sucesso']:return dict(result,periodo=day+1,cenario=s,motor='RuFaS nativo',proveniencia=provenance(s))
        daily=[];f.cache.clear();f.deadline=time.monotonic()+MAX_PERIOD_SECONDS
        try:
            for offset in range(length):
                current=day+offset
                residual,checks,diag,cost,dmi=f.evaluate(solution,current)
                if min(residual)<-TOLERANCE:
                    return dict(sucesso=False,status='bloco_invalido',mensagem='Dieta não atende todos os dias. Reduza o intervalo de reformulação.',dia=current+1,restricoes=checks,cenario=s)
                daily.append(dict(dia=current+1,data=(datetime.date.fromisoformat(s['data_inicio'])+datetime.timedelta(days=current)).isoformat(),
                                  del_dias=s['del_dias']+current,leite_vaca=s['leite_kg'],leite_rebanho=s['leite_kg']*s['vacas_lactacao'],
                                  custo_rebanho=cost*s['vacas_lactacao'],menor_residuo=float(min(residual)),
                                  exigencias=diag['exigencias']))
        except SearchTimeout as exc:return dict(sucesso=False,status='limite_tempo',mensagem=str(exc),cenario=s)
        finally:f.deadline=math.inf
        periods.append(dict(inicio=day+1,fim=day+length,dias=length,resultado=result,diario=daily));initial=solution
    daily=[d for p in periods for d in p['diario']];milk=sum(d['leite_rebanho'] for d in daily);cost=sum(d['custo_rebanho'] for d in daily)
    return dict(sucesso=True,padrao=s['padrao'],motor='RuFaS nativo + SciPy/SLSQP',cenario=s,animal=f.profile,
                periodos=periods,leite_total_kg=milk,custo_total=cost,margem_total=milk*s['preco_leite_kg']-cost,
                media_leite_vaca=s['leite_kg'],avisos=warnings_for(s),proveniencia=provenance(s))
