# Interface local: RuFaS + solver, NRC 2001 / NASEM 2021

## Versão ativa: integração nativa, holandesa HO

A interface chama `rufas_solver.py`. Este importa e executa os módulos do próprio
`RUFAS/`: `NRCRequirementsCalculator`, `NASEMRequirementsCalculator`,
`NutritionSupplyCalculator`, `RationConfig` e as restrições de `RationOptimizer`.
O solver é `scipy.optimize.minimize(method='SLSQP')`. Não é um pacote de equações
nutricionais: as dietas candidatas são avaliadas pelo RuFaS.

`nasem_dairy` e o arquivo antigo `nasem_solver.py` não participam desse fluxo.
Os scripts `nrc2001_dieta_lp/` e `nasem2021_dieta_lp/` permanecem como estudos
independentes de referência, sem alterações. A rota antiga `/api/otimizar` também
permanece como referência NRC simplificada; a interface atual não a utiliza.
Não confundir resultados anteriores com os da integração nativa v4.

## Rodar localmente

Python 3.12 ou 3.13. Na raiz do clone:

```bash
python3.12 -m venv .venv-rufas
.venv-rufas/bin/python -m pip install -e .
.venv-rufas/bin/python abrir_interface.py
```

Abrir `http://127.0.0.1:8080`. Encerrar com Ctrl+C. O worker usa o mesmo Python
do servidor, com as dependências do RuFaS. O antigo `.venv_nasem` não é necessário
para a interface atual. No Windows, usar `.venv-rufas\Scripts\python.exe`.
Para outra porta: `abrir_interface.py --port 8081`.
Não abrir somente o HTML: ele depende da API local. Nada depende de serviço na
nuvem depois da instalação. Se já houver um servidor antigo, encerre-o antes
de reutilizar a porta e atualize o navegador com Ctrl+Shift+R.

## Holandesa fornecida pelo RuFaS

`rufas_data.holstein_profile()` lê `input/data/animal/animal_population.json`.
Seleciona de forma determinística uma vaca `HO`, lactante, próxima de DEL 90 e
segunda lactação: animal 115561 nos dados desta revisão. Peso vivo
612,714865 kg, peso adulto 758,926298 kg, DEL 90, paridade 2, gestação 18 dias,
idade 1178 dias e intervalo entre partos 419 dias vêm desse registro.
Gordura 4% e proteína 3,2% vêm de `example_freestall_animal.json`, não de uma
medição dessa vaca. Escore 3, lactose 4,8%, meta 40 kg/dia, alojamento Barn,
distância zero e variação de tecidos zero são hipóteses explícitas.
Os calculadores recebem essas características; não existe um único coeficiente
mágico de raça. A interface permite ajustes e o JSON registra os valores usados.
A referência animal original é preservada junto com o cenário efetivo.

## Formulação

Variáveis contínuas: x_i, kg MS/vaca/dia dos alimentos selecionados. Meta de leite
Y fixa. Premix q=0,49 kg MS/dia fixo, com seu custo. Objetivo por bloco:
`min sum(preco_MS_i*x_i) + preco_premix*q`.

Cada avaliação calcula os requisitos nativos para o DEL e a gestação do dia,
e a oferta da dieta candidata. NASEM recebe a FDN percentual da candidata;
NRC recebe a concentração energética e o TDN fracionário da candidata.
As restrições nativas são 14 no NRC e 11 no NASEM: energia, proteína, Ca/P,
FDN, FDN de forragem, gordura e consumo (com os limites próprios de cada padrão).
Usam-se as funções nativas de `RationOptimizer`, exceto o chamador energético
NASEM substituído localmente conforme a correção de unidades descrita abaixo.
Somam-se os tetos operacionais já adotados no estudo (PB 19%, Ca 1%, P 0,42%),
teto de custo opcional e limites por ingrediente/estoque. Esses tetos são escolhas
do estudo e não devem ser apresentados como exigências completas de um livro.

Estoques totais são divididos por lactantes × dias e usados como teto diário
uniforme. Vazio = sem limite; zero = sem consumo. Exclusões retiram variáveis.
Preços entram em R$/kg natural, convertidos pelo teor de MS do padrão selecionado.
O orçamento vazio não impõe teto. O preço do leite só altera a margem informativa.

LP/HiGHS faz a pré-checagem de condições lineares necessárias e prepara a partida.
Uma etapa auxiliar de mínimos quadrados pode reduzir violações. Nenhuma dessas
etapas é aceita como solução final. SLSQP minimiza custo e exige sucesso e
resíduo normalizado >= -1e-5. Gradiente do objetivo: preços. Derivadas das
restrições: diferenças finitas. Até 100 iterações por tentativa, até três
partidas numéricas determinísticas do mesmo problema, sem relaxar restrições;
passos numéricos/escala positiva do custo podem variar quando uma tentativa falha.
120 s de busca por bloco; 600 s por tarefa. Escalas convertem unidades heterogêneas
antes da busca; `ftol` não substitui a conferência externa das restrições.

## Energia NASEM e fronteira com o núcleo

A chamada nativa original passa kg de amido/dia à correção dNDF, que subtrai a
referência 26 (% MS). O adaptador passa `100*amido_kg/DMI`, mantendo os métodos
nativos de digestibilidade, ED, EM e EL intactos. Teste verifica o argumento
recebido pelo método RuFaS. Metano e N urinário são recalculados para a candidata
pelos métodos nativos IPCC e de excreção da vaca lactante, com unidades g/dia e
kg/dia respectivamente. Não são inventados como constantes zero.

O histórico mostra as iterações do SLSQP, não as rodadas externas do PuLP. ED do
amido (Mcal/kg de amido ingerido) é calculada com `calculate_NASEM_dstarch`.
No NRC esse indicador não é calculado; a tabela sinaliza sua ausência.

## Horizonte e limites científicos

Uma dieta por bloco, frequência configurável. DEL, idade e gestação avançam;
requisitos são recalculados em cada dia. A busca amostra início/fim e DEL 100
quando presente; a aprovação final confere todos os dias do bloco. Violação
intermediária rejeita o plano e solicita intervalo menor. Até DEL 305 e antes
da secagem do perfil (gestação 218 dias); no máximo 31 blocos.

Integração real aos componentes nutricionais do RuFaS não significa simulação
completa da fazenda: não se executam TaskManager, reprodução, doenças, mortalidade
ou evolução de peso. Lote homogêneo, peso/escore constantes. Leite total é a meta
× lactantes × dias, identificado como produção planejada. Não é leite previsto
pela simulação nem garantia de produção observada. Animais não lactantes não
entram nos custos/produção. Não há certificado de ótimo global nem de inviabilidade
quando a falha é apenas numérica. Pré-checagem linear inviável é uma condição
necessária incompatível; ela não certifica viabilidade nutricional quando passa.

As ofertas de Ca/P nativas usam absorções descritas no RuFaS, inclusive referências
NRC no fluxo NASEM. O conjunto nativo não verifica os nove aminoácidos essenciais,
todos os minerais ou vitaminas. Não herdar a alegação de cobertura do adaptador
independente anterior. Premix aceita apenas Ca/P declarados em g/kg MS; outros
componentes são rejeitados explicitamente. Sem declaração, Ca/P do premix são zero.

## Código e API

- `rufas_data.py`: perfil real HO, catálogos NRC/NASEM e preços, sem importar motor no servidor.
- `rufas_solver.py`: validação, objetos Feed nativos, exigências/oferta/restrições, solver e planejamento.
- `worker_rufas.py`: processo sem gráficos; protocolo JSON-lines; diagnósticos em stderr.
- `jobs_nasem.py`: nome histórico da fila, agora atende os dois padrões com worker nativo.
- `abrir_interface.py`: API loopback e arquivos da interface. POST exige mesma origem.
- `interface/app.js`: cenário, tabela de alimentos, fila, cancelamento e resultados.
- `test_rufas.py`: integração com módulos e dados reais, dois padrões, horizonte, preços, estoques e exclusões.

GET `/api/rufas/perfil`; GET `/api/rufas/alimentos?padrao=NRC|NASEM`;
POST `/api/rufas/jobs`; GET `/api/rufas/jobs/<id>`;
POST `/api/rufas/jobs/<id>/cancel`.

Uma tarefa executa por vez, até três ativas/aguardando. Cancelamento encerra o
worker. Fila em memória não é recuperada após reinício. Resultados e falhas vão
para `output/estudo_dieta/rufas_<id>.json`, com cenário, perfil, versões e hashes
dos módulos e dados usados. Download inclui o plano. Teste local:

```bash
env -u DISPLAY MPLCONFIGDIR=/tmp/rufas-mpl .venv-rufas/bin/python -m unittest discover -s helpful_scripts/interface_rufas -p test_rufas.py -v
```

A interface é um cliente local dos componentes científicos; `RUFAS/`, `input/`
e os estudos originais não foram modificados. Documentação do motor anterior é
histórica: o identificador atual é `rufas-nativo-holandesa-custo-v4`.

## Correção v4.1: não gestante antes de DEL 100

No cenário de 150 dias, gestação zero e DEL inicial 90, o núcleo recebia
`day_of_pregnancy=None`. A manutenção nativa devolve pesos uterinos zero para
esse caso; o método de gestação interpreta `(0 - 0,204)` como crescimento uterino
positivo antes de DEL 100. No DEL 90 isso gerava 15,268176 Mcal/dia e proteína
associada a um crescimento gestacional inexistente, impedindo a formulação.

`NASEMRequirementsAdapter` especializa o calculador nativo somente nessa fronteira:
quando não há gestação e ambos os pesos uterinos estão ausentes/zerados, não se
infere crescimento de tecidos gestacionais (energia e ganho são zero). Este
planejamento não possui estado de involução uterina pós-parto. Não se assume
uma vaca grávida para fazê-la convergir. Casos gestantes e casos com pesos
uterinos conhecidos seguem o método original. Nenhum arquivo do núcleo foi
modificado, nenhuma restrição foi relaxada e a meta de leite foi preservada.

Regressões adicionais: estado não gestante nos dois lados do DEL 100, preservação
dos casos gestantes/com estado uterino, e cenário de 150 dias com cinco blocos e
conferência diária. Identificador: `rufas-nativo-holandesa-custo-v4.1`.
A interface serve HTML/JS sem cache para evitar reutilização de textos antigos.
