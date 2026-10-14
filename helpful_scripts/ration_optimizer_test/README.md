# Teste isolado do otimizador de rações

Na raiz do repositório, em um ambiente com as dependências do RuFaS instaladas:

```bash
python helpful_scripts/ration_optimizer_test/main.py
```

Não é necessário configurar `PYTHONPATH`, passar argumentos, executar o simulador,
carregar resultados anteriores ou fazer downloads. Os caminhos são resolvidos a
partir dos scripts; também é possível executar `main.py` por caminho absoluto.
Python e dependências seguem `pyproject.toml` (incluindo NumPy 2.2.0).

## Onde editar

- `scenario.json`: necessidades do lote, padrão nutricional, médias, dieta
  anterior/manual, semente, tolerâncias e configurações globais.
- `feeds.json`: todos os atributos dos ingredientes, preços e limites. Não é uma
  referência dinâmica aos CSVs: todos os dados necessários estão copiados aqui.
- `user_optimizer.py`: substitua a delegação dentro de
  `UserRationOptimizer.attempt_optimization()` pela sua modelagem e algoritmo.
  Atualize também `STRATEGY_DESCRIPTION`. Inicialmente **não existe estratégia
  diferente**: o método delega ao original para validar o ambiente.

Os demais arquivos cuidam do carregamento (`input_loader.py`), execução isolada e
contrato (`worker.py`), avaliação e relatório (`comparison.py`), entrada (`main.py`)
e verificações (`test_harness.py`). Nenhum arquivo da simulação foi alterado.

A função do usuário recebe objetos reais do RuFaS. Você pode usar os calculadores
nutricionais e métodos auxiliares do `RationOptimizer`, criar uma subclasse local,
ou usar outro solver. Não altere o arquivo original para experimentar: isso
mudaria a referência. Conserve todos os ingredientes no vetor, inclusive os de
quantidade zero, na ordem crescente de `rufas_id`.

## Entradas, tipos e unidades

Todas as quantidades se referem a **um animal médio do lote, por dia**; não são
quantidades totais do lote. O JSON preserva necessidades iniciais e atuais
separadas, inclusive no exemplo.

| Argumento | Tipo reconstruído / unidade |
| --- | --- |
| `nutrient_standard` | `NutrientStandard`, valor JSON `NASEM` ou `NRC` |
| `pen_average_body_weight` | kg de peso corporal |
| `pen_average_enteric_methane` | g/dia; `null` permitido para NRC |
| `pen_average_urine_nitrogen` | kg de N/dia; `null` permitido para NRC |
| `requirements` | `NutritionRequirements` |
| Campos `*_energy` | energia líquida, Mcal/animal/dia |
| `metabolizable_protein`, `calcium`, `phosphorus`, `process_based_phosphorus` | g/animal/dia |
| `requirements.dry_matter` | kg MS/animal/dia da tentativa atual |
| `essential_amino_acids` | `EssentialAminoAcidRequirements`, g/animal/dia; grafia do modelo `thryptophan` |
| `initial_dry_matter_requirement` | kg MS/animal/dia antes de reformulações |
| `initial_protein_requirement` | g de proteína metabolizável/animal/dia antes de reformulações |
| `pen_available_feeds` | `list[NASEMFeed]` ou `list[NRCFeed]`, construída de `feeds.json` |
| `animal_combination` | `AnimalCombination`; valores `lac_cow`, `growing`, `close_up`, `growing and close_up` |
| `previous_ration` | `null` ou mapa ID → kg MS/animal/dia |
| `user_defined_ration_dictionary` | `null` ou mapa ID → percentual da MS, soma 100 |
| `user_defined_ration_tolerance` | `null` sem dieta manual, ou fração 0–1 (0.1 = ±10%) |

Para dietas anterior/manual, forneça exatamente todos os IDs de `feeds.json`,
incluindo zeros. Chaves JSON como `"44"` tornam-se inteiros. Metadados `status` e
`objective` da dieta anterior são removidos antes da chamada: o original ordena
as chaves antes de descartá-los, e Python não ordena chaves mistas `str`/`int`.
Dicionários incompletos ou IDs duplicados são rejeitados, evitando deslocamento
silencioso de posições. O otimizador não aceita `calf` nesta rota.

### Composição dos ingredientes

Os campos seguem as dataclasses reais `Feed`, `NASEMFeed` e `NRCFeed`, não um
esquema reduzido. Ao trocar o padrão, forneça também todos os campos da classe
correspondente: NRC inclui `non_fiber_carb` e `PAF`; NASEM tem campos adicionais.
`Fd_Category`, `feed_type` e `units` são convertidos em seus respectivos enums.

- `DM`: percentual de MS na massa fresca. O vetor de decisão já está em MS:
  não multiplicar suas quantidades novamente por `DM/100`.
- `CP`, `NDF`, `ADF`, `EE`, `ash`, `lignin`, `starch`, minerais principais e
  `TDN`: percentuais na MS, não frações nem g/kg. Por exemplo, `CP=20` significa
  20% da MS. `DE` e `DE_Base`: Mcal/kg MS.
- `N_A`, `N_B`, `N_C`, `RUP`, `sol_prot`: percentuais da proteína bruta;
  `dRUP`: percentual da RUP; `Kd`: %/hora; `NDF48`: % da NDF;
  aminoácidos do ingrediente: % da proteína; `C*_FA`: % dos ácidos graxos.
- Os demais campos NASEM preservam as bases do CSV original. **Não aplique uma
  conversão global de percentuais**: há coeficientes fracionários, como
  `Abs_calcium` e `Abs_phosphorus`, e microminerais em mg/kg MS no CSV, apesar de
  alguns docstrings genéricos do modelo descreverem esses campos como `%`.
  O carregador não recalcula nem reinterpreta a composição.
- `lower_limit` e `limit`: kg MS/animal/dia. São os limites de inclusão do solver;
  `amount_available` não é usado como limite de estoque por esta otimização.
- `purchase_cost`: $/kg MS, usado no objetivo original e na comparação comum;
  `on_farm_cost` também é $/kg, mas não é usado no objetivo desta rota.
  `buffer`: fração. `is_fat`/`is_wetforage`: booleanos JSON.

## Estado global e isolamento

Cada estratégia é executada **uma vez em um novo processo Python**. O baseline
não importa `user_optimizer.py`. Os dois processos recebem o mesmo snapshot JSON
lido no começo, reconstruindo seus próprios objetos. Alterações em objetos,
classes, RNGs e singletons dentro de uma estratégia não afetam a outra nem o
avaliador. Isso não é um sandbox para código malicioso que escreva arquivos.

Antes da tentativa, definem-se:

- `NutritionSupplyCalculator.nutrient_standard`, igual ao argumento do cenário.
- `RationManager.intake_options` e `intake_values`, a partir de `globals`.
- `RationManager.ration_feeds`, `user_defined_rations` e `tolerance`, a partir dos
  argumentos. Não há ciclo de reformulação; seu limite de tentativas não é usado.
- Sementes de `random` e NumPy, ambas iguais a `seed`.

Os valores padrão dos `AnimalModuleConstants` do branch permanecem intactos:
DMI ±30%, boost de MS da dieta manual 1.1, proteína superior 1.5 vezes a inicial,
NDF 25–45%, NDF de forragem ≥15% e gordura ≤7%. Opções de DMI informado fazem os
métodos originais usarem fração de DMI 0 e boost 1. O `intake_value` é registrado
como contexto, mas não recalcula requisitos aqui: ao mudar de modo, ajuste
explicitamente os requisitos iniciais/atuais no cenário.

`OutputManager` existe por dependência de importação, com seus pools locais; não
se inicializa calendário, clima, rebanho, `Pen` ou ciclo de simulação. Avisos do
modelo são incluídos no relatório. O timeout por processo é configurável no JSON.
O tempo exibido mede a chamada do otimizador, excluindo inicialização/importações.

## Retorno e avaliação independente

O retorno deve ser exatamente:

```python
from scipy.optimize import OptimizeResult
from RUFAS.biophysical.animal.ration.ration_optimizer import RationConfig

# config.feeds_used deve corresponder ao vetor em ordem crescente de ID.
return OptimizeResult(x=quantidades, success=True, fun=objetivo,
                      status=0, message="Descrição"), config
```

Use a `RationConfig` de **ration_optimizer.py**. Há outra classe homônima no
projeto. O vetor deve ser unidimensional, real, finito, com um elemento por
ingrediente. `success` deve ser booleano; `fun`, `status` e `message` são opcionais.
A correspondência entre posições e IDs deve constar de `config.feeds_used`.

A tolerância de não negatividade é `1e-8` kg MS. Valores menores que `-1e-8`
invalidam o retorno; negativos entre `-1e-8` e zero são preservados, não truncados.
O avaliador usa outra `RationConfig`, ingredientes/preços originais e uma instância
nova de `RationOptimizer.set_constraints()`/`_select_constraints()`. Não utiliza
listas de restrições, preços ou requisitos devolvidos pela estratégia do usuário.

O relatório distingue:

1. Sucesso informado pelo solver.
2. Validade estrutural do retorno.
3. Atendimento independente às restrições originais e limites de ingredientes.

Um vetor válido pode ser inviável mesmo com `success=True`, ou viável mesmo com
`success=False`. Retornos ausentes/inválidos não recebem vetor substituto. Erros
são mostrados e a outra estratégia continua. O custo é sempre recalculado como
`sum(x * purchase_cost)`; `fun` é mostrado separadamente. A diferença percentual
não é calculada quando o custo baseline é zero. Dietas inviáveis não são
classificadas como melhores pelo custo.

Cada resíduo de desigualdade passa se for ≥ `-1e-6`, tolerância absoluta na unidade
nativa: Mcal para energia; g para proteína/Ca/P; kg para DMI e ingredientes; pontos
percentuais para NDF, NDF de forragem e gordura. Não é uma tolerância relativa nem
uma alteração nas restrições do solver. Resíduos não finitos ou erros de cálculo
falham na avaliação. A tabela informa resíduo, atendimento e tolerância.

São preservadas as regras do código, inclusive:

- Fósforo exigido = `max(phosphorus, process_based_phosphorus)`.
- Proteína inferior usa necessidade atual; superior usa `1.5 * initial_protein_requirement`.
- DMI inferior usa necessidade atual; superior usa necessidade inicial.
- Limites manuais usam porcentagem × DMI inicial × boost × `(1 ± tolerância)`.
  O método original intersecta esses alvos com limites dos ingredientes; se o
  intervalo for inteiramente externo, **fixa no limite mais próximo e registra
  aviso**. O relatório segue esses limites efetivos, não promete atingir um alvo
  manual impossível. Essa regra é herdada do branch, não criada pelo teste.
- Aminoácidos são reconstruídos, mas o otimizador original não impõe restrições
  individuais de aminoácidos nessa rota.

Código de saída: 0 se ambas as estratégias tiverem retorno válido, sucesso e
viabilidade; 1 se alguma falhar; 2 para erro de cenário/comparação.

## Origem do exemplo e limites

Referência: `WedersonCD/RuFaS`, branch `optimizer_tester`, commit
`c59d8651cb54e8d1de7f267dcb0510c5fca4cce4`.

- Composição e limites copiados de `input/data/feed/NASEM_Comp_with_TDN.csv`.
- IDs 44, 51, 100, 110, 301 e 303 selecionados do lote `lac_cow` de
  `input/data/feed/example_Northeast_feed.json`; preços e buffer copiados do mesmo
  arquivo; `on_farm_cost = purchase_cost * 0.01`, como no builder original.
- `amount_available=0`, como na construção original de alimentos disponíveis.
- Necessidades, peso, metano e N urinário **são sintéticos e ilustrativos**.
  Aminoácidos zerados são placeholders, não necessidades biológicas estimadas.
  A dieta manual não é ativada no cenário padrão.

Com Python 3.12, NumPy 2.2.0 e SciPy 1.17.0, o cenário padrão foi validado com
sucesso e viabilidade em ambas as estratégias. Elas retornam o mesmo vetor e
custo (~$0.273813/animal/dia) e ~27.38131 kg MS/animal/dia; diferenças numéricas
pequenas entre versões de solver/plataformas são possíveis.

Os preços de exemplo incluem $0.01/kg e limites muito amplos. Por isso, a solução
pode concentrar praticamente toda a MS na silagem de leguminosa (ID 110).
**Não é uma recomendação de manejo ou uma cotação comercial.** Os limites e preços
não foram ajustados silenciosamente para produzir uma dieta visualmente variada.

Este teste representa uma tentativa em um único momento. Não mede produção futura,
estoques, agrupamento, mudança de exigências, feedback de metano/N, nem efeitos
acumulados da simulação. Não reduz leite, aumenta DMI, tenta novamente nem aplica
fallback automático/manual.

## Verificações direcionadas

```bash
python helpful_scripts/ration_optimizer_test/test_harness.py
```

Testa execução real e equivalência inicial, assinatura, enums/IDs/objetos,
reconstrução NRC, nulos, vetores inválidos, tolerâncias, inviabilidade apesar de
sucesso, objetivo independente, regras de fósforo/proteína, limites manuais,
configuração DMI e continuidade após exceção com mutações deliberadas no processo
do usuário. Não exige dependências de testes adicionais.
