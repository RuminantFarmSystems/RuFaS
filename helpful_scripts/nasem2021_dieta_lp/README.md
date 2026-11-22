# Dieta de custo mínimo pelo NASEM (2021), com PuLP

Formula a dieta mais barata para uma vaca leiteira atendendo às exigências do **NASEM (2021)**, *Nutrient
Requirements of Dairy Cattle*, 8ª edição (versão traduzida, *Exigências Nutricionais de Bovinos Leiteiros*),
com preços de alimentos de Goiás e a biblioteca de alimentos do RuFaS. O modelo é de programação linear,
resolvido pelo simplex (CBC, via PuLP), e as não linearidades do NASEM são tratadas por rodadas.

**Resultado para a vaca de referência:** R$ 40,35 por dia (R$ 0,73 por kg de leite), com 29,4 kg de matéria seca.

O código está em um arquivo só, [`dieta_pulp.py`](dieta_pulp.py), escrito de cima para baixo, sem funções.

## Sumário

1. [Como rodar](#1-como-rodar)
2. [Visão geral](#2-visão-geral)
3. [Dados de entrada](#3-dados-de-entrada)
4. [Exigências da vaca](#4-exigências-da-vaca)
5. [O modelo de programação linear](#5-o-modelo-de-programação-linear)
6. [Não linearidades e rodadas](#6-não-linearidades-e-rodadas)
7. [Resultado](#7-resultado)
8. [Limitações](#8-limitações)
9. [Uso da dieta no RuFaS](#9-uso-da-dieta-no-rufas)
10. [Glossário](#10-glossário)
11. [Referências](#11-referências)

---

## 1. Como rodar

O script usa arquivos do repositório do RuFaS, então precisa ser rodado a partir da raiz dele:

```bash
pip install pulp==2.9.0 pandas
python helpful_scripts/nasem2021_dieta_lp/dieta_pulp.py
```

Arquivos lidos:

| Arquivo | Conteúdo |
|---|---|
| `input/data/feed/NASEM_Comp_with_TDN.csv` | Biblioteca NASEM do RuFaS: composição dos alimentos (Tabela 19-1 do NASEM em formato digital) |
| `helpful_scripts/nrc2001_dieta_lp/alimentos_precos.csv` | Alimentos candidatos e preços em Goiás, com fonte e data de cada cotação |

**Versão do PuLP:** a 2.9.0 já traz o solver CBC. A partir da versão 3, a interface mudou (não existe mais
`LpVariable.dicts`) e o solver não vem incluído.

A saída mostra o status, o número de rodadas, o custo, a dieta em kg de matéria seca e de matéria natural, a
energia e a PM fornecidas e a lista de restrições que ficaram no limite. Roda em menos de 1 segundo.

---

## 2. Visão geral

O arquivo tem cinco blocos:

| Bloco | O que faz |
|---|---|
| **1. Vaca** | Define o animal de referência (peso, leite, composição do leite, dias de lactação, gestação) |
| **2. Exigências** | Calcula o que não depende da dieta: energia, PM, Ca, P e faixa de consumo |
| **3. Alimentos** | Junta preços e composição, aplica correções e calcula as colunas usadas no modelo |
| **4. Rodadas** | Calcula a energia de 1 kg de cada alimento, monta o modelo, resolve, mede a dieta escolhida e repete até a conta ficar coerente |
| **5. Resultado** | Imprime a dieta e as restrições no limite |

As rodadas existem porque, no NASEM, a energia e a proteína que um alimento fornece dependem da dieta inteira
(seção 6). O simplex só trabalha com números fixos, então cada rodada fixa esses números com a dieta anterior.

---

## 3. Dados de entrada

### 3.1 Vaca de referência

Vaca adulta com 100 dias em lactação da Tabela 21-1 (raça Holandesa):

| Parâmetro | Valor | Variável no código |
|---|---|---|
| Peso corporal e peso adulto | 700 kg | `PV`, `PC_MAT` |
| Dias em lactação | 100 | `DEL` |
| Dia de gestação | 10 | `GESTACAO` |
| Leite | 55 kg/dia | `LEITE` |
| Gordura, proteína verdadeira e lactose do leite | 3,5%, 2,83% e 4,85% | `GORDURA`, `PROTEINA`, `LACTOSE` |
| Ganho de peso (crescimento) | 0,10 kg/dia | `GANHO` |
| Ganho de reservas corporais | 0,21 kg/dia | `RESERVAS` |
| Escore de condição corporal | 3,0 | `ECC` |
| Consumo da tabela | 29,4 kg MS/dia | `IMS_TABELA` |
| Premix vitamínico e mineral (fixo) | 0,49 kg/dia | `PREMIX` |

### 3.2 Alimentos e preços

17 candidatos comercializados em Goiás: silagens de milho e de sorgo, fenos de Tifton 85 e de alfafa, milho e
sorgo moídos, farelo e grão de soja, caroço e farelo de algodão, casca de soja, polpa cítrica, farelo de trigo,
sabões de cálcio, calcário, fosfato bicálcico e sal. O premix entra com quantidade fixa, porque microminerais e
vitaminas não estão no modelo.

O preço por kg de matéria seca é o preço cotado dividido pela matéria seca do alimento.

**Correções aplicadas à biblioteca:**

| Item | Correção | Motivo |
|---|---|---|
| Feno de Tifton 85 | Usa a linha "Bermudagrass hay" (id 18) | Não há Tifton na biblioteca NASEM; Tifton 85 é um capim-bermuda |
| Fosfato bicálcico | Absorção de Ca 0,60 e de P 0,75 | Valores da Tabela 19-3 (a biblioteca tem 0,75 e 0,80) |
| Sabões de cálcio | Ca de 12% | A Tabela 19-1 não traz o Ca, e a biblioteca grava 0 |

**Colunas calculadas por alimento:**

| Coluna | O que é | Fórmula |
|---|---|---|
| `forragem` | 1 para forragens | tipo "Forage" na biblioteca |
| `umida` | 1 para silagens | forragem com menos de 50% de MS |
| `fdn_forragem` | FDN vindo de forragem (% da MS) | FDN × forragem |
| `gordura_sup` | Gordura suplementar (% da MS) | EE de caroço de algodão, soja grão e sabões de cálcio |
| `pdr` | PDR por kg de MS | PB × (1 − PNDR) |
| `pndr_dig` | PNDR digestível por kg de MS | PB × PNDR × digestibilidade da PNDR |
| `dfdn_base` | Digestibilidade base do FDN | 0,75 × (FDN − lignina) × [1 − (lignina/FDN)^0,667] ÷ FDN (Eq. 3-3a) |
| `ed_verdadeira` | Energia digestível sem o desconto endógeno fixo | ED base + 0,318 (zero para minerais) |

A PNDR da biblioteca bate com a Eq. 6-1 do NASEM (taxa de passagem fixa: 4,87 %/h em forragens e 5,28 %/h em
concentrados), e a ED base bate com a Eq. 3-8 em 13 dos 14 alimentos orgânicos.

---

## 4. Exigências da vaca

Calculadas uma vez, no bloco 2. A parte que depende da dieta (perdas fecais e mantença de Ca e P, que crescem
com o consumo) entra direto nas restrições.

**Energia (ELL), 53,04 Mcal/dia:**

| Parte | Mcal/dia | Fórmula |
|---|---|---|
| Leite | 37,58 | (0,0929 × gordura + 0,0547/0,93 × proteína + 0,0395 × lactose) × leite = 0,683 Mcal/kg × 55 kg |
| Mantença | 13,61 | 0,10 × (peso − útero gravídico)^0,75 |
| Reservas corporais | 1,18 | 5,6 × ganho de reservas |
| Crescimento | 0,67 | (9,4 × gordura do ganho + 5,55 × proteína do ganho) × 0,85 × ganho ÷ 0,61 |
| Gestação | ≈ 0 | ganho do útero × 0,882 ÷ 0,14 × 0,66 |

**PM:** 2.514 g/dia fixos (descamação, leite, crescimento, urina endógena e gestação), mais a PM perdida nas
fezes, que depende do consumo e do FDN: 1,058 × (11,62 × consumo + 13,4 × kg de FDN). Dos 2.514 g, 2.256 g
são a proteína do leite (1.557 g ÷ 0,69).

**Cálcio e fósforo absorvíveis:** 54,4 g de Ca e 48,2 g de P fixos (crescimento, gestação e leite), mais a
mantença, que cresce com o consumo: 0,90 g de Ca e 1,0 g de P por kg de MS.

**Consumo:** entre 28,53 kg (Eq. 2-1 do NASEM, pelo peso, energia do leite, escore e dias de lactação) e
29,40 kg (Tabela 21-1).

As fórmulas de energia e PM foram conferidas contra as Tabelas 21-1 e 21-3: a PM bate até 0,1% para as cinco
vacas em lactação, e a energia até 0,7% para as três que não estão perdendo peso (nas duas que perdem peso no
início da lactação, a energia fica cerca de 6% abaixo, pelo coeficiente da energia das reservas).

---

## 5. O modelo de programação linear

### 5.1 Variáveis de decisão

| Variável | O que é |
|---|---|
| `x[i]` | kg de matéria seca do alimento *i* por dia (17 variáveis, ≥ 0) |
| `pdr_util` | kg de PDR aproveitada pelos micróbios do rúmen (≥ 0), variável auxiliar da proteína microbiana |

O consumo total é **T = Σ x[i] + 0,49** (premix).

### 5.2 Função objetivo

Minimizar o custo diário da dieta:

$$\min \; \sum_i \text{preço}_i \, x_i + 0{,}49 \times \text{preço do premix}$$

### 5.3 Restrições

São **26 restrições**, em **6 grupos**. Os grupos 1, 2, 3 e 6 garantem que a dieta atende à necessidade da vaca;
os grupos 4 e 5 protegem a saúde do rúmen. Notação: "% de algo" = Σ (x[i] × teor do alimento) ÷ T.

#### Grupo 1: consumo (2)

**Por que existe:** a vaca tem um limite de quanto consegue comer. A dieta precisa caber nesse volume.

| Nome no código | Restrição | Origem |
|---|---|---|
| `consumo_min` | T ≥ 28,53 kg | Eq. 2-1 do NASEM |
| `consumo_max` | T ≤ 29,40 kg | Tabela 21-1 |

#### Grupo 2: energia (1)

**Por que existe:** é a maior exigência da vaca. Sem energia suficiente, ela perde peso e produz menos leite.

| Nome no código | Restrição | Origem |
|---|---|---|
| `energia` | Σ ELL<sub>i</sub> × x[i] + c<sub>ELL</sub> ≥ 53,04 Mcal | Cap. 3 (exigência e oferta) |

ELL<sub>i</sub> é a energia que 1 kg do alimento entrega à vaca, recalculada a cada rodada (seção 6.4).
c<sub>ELL</sub> é a parte que não depende dos alimentos (premix e perdas ligadas ao leite e à proteína
microbiana).

#### Grupo 3: proteína (5)

**Por que existe:** a proteína vira leite, tecido e enzimas. A falta reduz a produção; o excesso custa caro e sai
na urina como nitrogênio.

| Nome no código | Restrição | Origem |
|---|---|---|
| `pm` | PM microbiana + PNDR digestível ≥ 2.514 + 1,058 × (11,62 × T + 13,4 × kg de FDN) g | Cap. 6 (Eq. 6-1 a 6-4) |
| `pdr_util_ate_pdr` | PDR útil ≤ Σ PDR<sub>i</sub> × x[i] | Auxiliar: os micróbios só usam a PDR que existe |
| `pdr_util_ate_12` | PDR útil ≤ 0,12 × T | Auxiliar: acima de 12% da dieta, a PDR não vira mais proteína microbiana (p. 82) |
| `pdr_min` | % PDR ≥ 10 | Mínimo para os micróbios (p. 82) |
| `pb_max` | % PB ≤ 19 | Teto escolhido para evitar excesso de nitrogênio |

A PM microbiana é 404,2 + 330,5 × PDR útil (g), com o fator de energia dos micróbios recalculado a cada rodada
(seção 6.5).

#### Grupo 4: fibra e amido (5)

**Por que existe:** a fibra de forragem faz a vaca ruminar e produzir saliva, que neutraliza o ácido do rúmen. O
amido fermenta rápido e produz muito ácido; em excesso, causa acidose e baixa a gordura do leite.

A Tabela 5-1 é uma troca: quanto menos fibra de forragem, mais fibra total e menos amido a dieta precisa ter.

| FDN de forragem mínima | FDN total mínima | Amido máximo |
|---|---|---|
| 19% | 25% | 30% |
| 18% | 27% | 28% |
| 17% | 29% | 26% |
| 16% | 31% | 24% |
| 15% | 33% | 22% |

As linhas da tabela viram cinco restrições lineares:

| Nome no código | Restrição | O que significa |
|---|---|---|
| `fdn_forragem_min` | % FDN de forragem ≥ 15 | Mínimo absoluto de fibra de forragem |
| `fdn_min` | % FDN ≥ 25 | Mínimo absoluto de fibra total |
| `amido_max` | % amido ≤ 30 | Máximo absoluto de amido |
| `fdn_mais_2fdnf` | % FDN + 2 × % FDN de forragem ≥ 63 | A cada ponto a menos de fibra de forragem, 2 pontos a mais de fibra total |
| `amido_menos_2fdnf` | % amido − 2 × % FDN de forragem ≤ −8 | A cada ponto a menos de fibra de forragem, 2 pontos a menos de amido |

#### Grupo 5: gordura (2)

**Por que existe:** a gordura insaturada é tóxica para os micróbios que digerem fibra. Em excesso, reduz a
digestão da fibra e a gordura do leite.

| Nome no código | Restrição | Origem |
|---|---|---|
| `ee_max` | % EE ≤ 7 | NRC (2001), cap. 3 |
| `gordura_sup_max` | % gordura suplementar ≤ 4 | NRC (2001), cap. 3 (soja grão, caroço de algodão e sabões de cálcio) |

#### Grupo 6: minerais (11)

**Por que existe:** cada mineral tem uma função (osso, leite, nervos, equilíbrio de água), e o excesso de alguns
também faz mal.

| Nome no código | Restrição | O que significa |
|---|---|---|
| `ca_absorvivel` | Σ Ca<sub>i</sub> × 10 × absorção<sub>i</sub> × x[i] ≥ 54,4 + 0,90 × T g | Cálcio absorvido suficiente (53 g saem no leite) |
| `p_absorvivel` | Σ P<sub>i</sub> × 10 × absorção<sub>i</sub> × x[i] ≥ 48,2 + 1,0 × T g | Fósforo absorvido suficiente |
| `ca_max` | % Ca ≤ 1 | Teto de cálcio (NRC 2001) |
| `p_max` | % P ≤ 0,42 | Teto escolhido: excesso de P é desperdício e polui |
| `ca_maior_p` | Ca ≥ P | Relação Ca:P mínima de 1 |
| `ca_ate_7p` | Ca ≤ 7 × P | Relação Ca:P máxima de 7 |
| `magnesium_min` | % Mg ≥ 0,18 | Nervos e músculos (Tabela 21-1) |
| `potassium_min` | % K ≥ 1,00 | Equilíbrio de água (Tabela 21-1) |
| `sodium_min` | % Na ≥ 0,22 | Equilíbrio de água (Tabela 21-1) |
| `chlorine_min` | % Cl ≥ 0,32 | Equilíbrio de água (Tabela 21-1) |
| `sulfur_min` | % S ≥ 0,20 | Aminoácidos com enxofre dos micróbios (Tabela 21-1) |

Os absorvíveis consideram que a vaca aproveita só parte do mineral: cerca de 30–40% do Ca das forragens, 60% dos
concentrados e 45% do calcário (coeficientes da biblioteca e da Tabela 19-3).

### 5.4 Como as restrições em % ficam lineares

Uma restrição em % tem o consumo T no denominador, mas basta multiplicar os dois lados por T. No amido:

$$\frac{\sum_i x_i \,\text{amido}_i}{T} \le 30 \;\;\Longrightarrow\;\; \sum_i x_i \,\text{amido}_i \le 30\,T$$

Como T é a soma das variáveis mais o premix, a restrição fica linear e exata, sem aproximação. No código, ela
aparece assim:

```python
model.addConstraint(pulp.lpSum(F.starch[i] * x[i] for i in alimentos) <= 30 * T, name="amido_max")
```

Cada alimento entra com o seu amido menos 30: o milho moído (70%) empurra o amido para cima; a soja grão (4%)
dilui.

---

## 6. Não linearidades e rodadas

### 6.1 O que é não linear aqui

Uma restrição é linear quando só tem termos do tipo **número fixo × variável**, somados. Depender de outros
alimentos não basta para ser não linear: o amido total da dieta depende de todos os alimentos e é linear. A conta
deixa de ser linear quando as variáveis (os kg de cada alimento) aparecem **multiplicadas ou divididas entre si**.

Exemplo: a digestibilidade do amido cai quando a vaca come mais em relação ao peso (Eq. 3-5b):

digestibilidade = valor base − 1,0 × (consumo ÷ peso − 0,035)

A energia do amido do milho moído fica, chamando de M, F e S os kg de milho, feno e silagem:

energia = 0,70 × 4,23 × M × [0,925 − (M + F + S) ÷ 700] = 2,739·M − 0,00423·M·M − 0,00423·M·F − 0,00423·M·S

Aparecem um quadrado (M·M) e interações (M·F, M·S). Se a digestibilidade fosse fixa, só existiria o primeiro
termo.

### 6.2 Os sete casos

Todos têm a mesma causa (o que um alimento fornece depende da dieta inteira) e ficam em apenas três das 26
restrições.

| # | Caso | Equação | Forma da não linearidade | Restrição | Tratamento |
|---|---|---|---|---|---|
| 1 | Digestibilidade do amido | 3-5b | Produto (kg do alimento × consumo total) | `energia` | Rodadas: consumo fixado |
| 2 | Digestibilidade do FDN | 3-5a | Produto e divisão (depende do % de amido da dieta e do consumo) | `energia` | Rodadas: consumo e % de amido fixados |
| 3 | Metano | 3-9 | Divisão pelo consumo (% de gordura e % de fibra digerida) | `energia` | Rodadas: consumo fixado |
| 4 | Proteína microbiana | 6-3 | Saturação: (101 + 82,6 × PDR) ÷ [(1 + 0,094/FDNdr) × (1 + 0,027/AMDr)] | `pm` | Rodadas: fator de energia dos micróbios fixado |
| 5 | Fibra e amido degradados no rúmen | 6-4a, 6-4b | Quadrados (PB², amido²), razão FDA/FDN, produto pelo consumo | `pm` (via caso 4) | Rodadas, junto com o caso 4 |
| 6 | Perdas nas fezes e energia da urina | 3-6b, 3-10 | Herdada do caso 4 | `energia` | Rodadas: PB microbiana fixada |
| 7 | PDR útil até 12% da dieta | p. 82 | Mínimo entre dois valores | `pdr_util_ate_pdr`, `pdr_util_ate_12` | Exato: variável auxiliar `pdr_util` |

As exponenciais e potências do lado do animal (peso^0,75, curvas de gestação) não tornam o problema não linear,
porque peso e dia de gestação são dados fixos: para o solver, viram números.

### 6.3 O círculo e as rodadas

O simplex precisa saber, antes de começar, quanta energia 1 kg de cada alimento fornece. Mas:

- para saber o % de amido da dieta, é preciso saber quais alimentos entram;
- para escolher os alimentos, é preciso saber a energia de cada um;
- para saber a energia, é preciso saber o % de amido.

O código quebra o círculo assim:

1. **Supõe** consumo, % de amido, fator microbiano e PB microbiana (chute inicial: 29,4 kg, 26%, 0,97 e
   2.100 g; 26% é a referência do livro, onde a correção é zero).
2. **Calcula** a energia de 1 kg de cada alimento com esses valores.
3. **Resolve** o modelo: para o simplex, os números são fixos.
4. **Mede** os quatro valores na dieta escolhida.
5. Se a diferença relativa for maior que 10⁻⁸, **volta ao passo 2** com os valores medidos.

| Rodada | Amido suposto | Amido da dieta escolhida | Energia de 1 kg de silagem | Custo |
|---|---|---|---|---|
| 1 | 26,00% (chute) | 29,02% | 1,698 Mcal | R$ 39,33 |
| 2 | 29,02% | 29,96% | 1,678 Mcal | R$ 40,16 |
| 3 | 29,96% | 30,00% | 1,672 Mcal | R$ 40,35 |
| 4 | 30,00% | 30,00% | 1,672 Mcal | R$ 40,35 |

O custo sobe porque cada rodada mostra que os alimentos davam um pouco menos de energia do que o suposto: na
rodada 1, a dieta de R$ 39,33 parecia entregar 53,04 Mcal, mas, com o amido real de 29%, entregava 52,52. Com
outros chutes iniciais (15% e 35% de amido), as rodadas chegam à mesma dieta. A convergência completa, com os
quatro valores, leva 7 rodadas.

### 6.4 A restrição de energia por dentro

A energia que 1 kg de cada alimento entrega é (Eq. 3-3 a 3-12):

**ELL por kg = 0,66 × (energia digestível − perdas endógenas − metano − urina)**

| Termo | Fórmula por kg de MS |
|---|---|
| Energia digestível | ED verdadeira + 0,042 × FDN × ajuste do FDN + 0,0423 × amido × ajuste do amido |
| Perdas endógenas | 5,65 × PB metabólica fecal + 0,0040 × 34,3 |
| Metano | 0,294 − 0,347 × % gordura ÷ consumo + 0,0409 × FDN × digestibilidade do FDN ÷ consumo |
| Urina | 0,0146 × 160 × (PDR + PNDR digestível − PB metabólica fecal) |

Na dieta final:

| Por kg de MS | Silagem de milho | Milho moído | Soja grão |
|---|---|---|---|
| Energia digestível | 3,186 | 3,736 | 4,614 |
| − perdas endógenas | 0,234 | 0,210 | 0,212 |
| − metano | 0,297 | 0,255 | 0,101 |
| − urina | 0,122 | 0,146 | 0,875 |
| **= ELL (× 0,66)** | **1,672** | **2,063** | **2,261** |

A soja grão perde pouco em metano porque tem 17% de gordura. O simplex recebe só a linha final:
1,672 × kg de silagem + 2,063 × kg de milho + 2,261 × kg de soja grão + … + 1,41 ≥ 53,04.

### 6.5 A restrição de PM por dentro

A PM fornecida é a proteína microbiana digerida mais a PNDR digerida. Os micróbios produzem N a partir da PDR,
com retorno decrescente conforme a energia que fermentam (Eq. 6-3):

N microbiano = (101 + 82,6 × PDR útil) × fator de energia, com fator = 1 ÷ [(1 + 0,094/FDNdr) × (1 + 0,027/AMDr)]

FDNdr e AMDr são o FDN e o amido degradados no rúmen (Eq. 6-4a e 6-4b). A PM microbiana é
N × 6,25 × 0,824 × 0,80. Com o fator fixado na rodada (0,971 na dieta final), cada kg de PDR útil rende 330,5 g
de PM, e a restrição fica linear:

| Alimento | PNDR digestível (g/kg) | − PM extra perdida nas fezes (g/kg) | = número na restrição |
|---|---|---|---|
| Silagem de milho | 17,8 | 18,1 | −0,3 |
| Milho moído | 26,9 | 13,7 | 13,2 |
| Soja grão | 101,8 | 14,0 | 87,8 |
| Farelo de algodão | 170,9 | 16,3 | 154,6 |
| Farelo de soja | 156,9 | 13,9 | 143,0 |

Na dieta final, os fatores de energia dos micróbios estão perto de 1 (0,977 para o FDN e 0,994 para o amido): o
que limita a proteína microbiana é a PDR, e por isso `pdr_util_ate_pdr` fica no limite.

---

## 7. Resultado

| Alimento | kg MS | kg natural | R$/dia |
|---|---|---|---|
| Silagem de milho | 11,11 | 31,43 | 6,14 |
| Milho moído | 6,86 | 7,90 | 7,07 |
| Soja grão | 4,98 | 5,59 | 13,13 |
| Farelo de algodão | 2,45 | 2,72 | 3,13 |
| Feno de Tifton 85 | 1,77 | 1,89 | 2,71 |
| Caroço de algodão | 0,77 | 0,85 | 0,71 |
| Farelo de soja | 0,50 | 0,56 | 1,13 |
| Calcário calcítico | 0,33 | 0,33 | 0,45 |
| Cloreto de sódio | 0,13 | 0,13 | 0,04 |
| Premix (fixo) | 0,49 | 0,49 | 5,85 |
| **Total** | **29,40** | **51,89** | **40,35** |

**Nutrientes:** ELL de 1,80 Mcal/kg (53,04 Mcal), PM de 2.990 g (1.532 g microbiana e 1.458 g de PNDR), PB de
17,7%, PDR de 11,6%, FDN de 27,6%, FDN de forragem de 19,4%, amido de 30,0% e EE de 6,45%. Os valores da Tabela
21-1 para essa vaca são ELL de 1,80 Mcal/kg, PB de 17,4% e PDR de 10,0%.

**Restrições no limite (10 das 26):** consumo máximo, energia, PM, PDR útil ≤ PDR, amido máximo, gordura
suplementar, Ca absorvível, P máximo, Na e S. São elas que definem a dieta e o custo; as outras 16 são atendidas
com folga, e afrouxá-las não mudaria o resultado.

O amido vai ao teto porque a energia mais barata vem junto com amido (silagem a R$ 0,33 por Mcal e milho a
R$ 0,50, contra R$ 1,17 da soja grão). Com o amido no teto, a energia que falta vem da gordura da soja grão,
até o teto de gordura suplementar.

---

## 8. Limitações

- **A dieta encontrada é coerente, mas não necessariamente a mais barata.** As rodadas param quando os valores
  supostos batem com a dieta escolhida, mas em cada rodada o simplex não sabe que escolher menos amido aumentaria
  a energia da fibra. Fixando o amido da dieta em vários valores, há uma dieta com 21,5% de amido que atende a
  tudo e custa R$ 39,86, R$ 0,49 a menos. Uma busca externa pelo % de amido (ou uma conferência com um solver não
  linear) resolveria isso.
- **Um animal só:** a vaca adulta com 100 dias de lactação. Vacas secas, novilhas e outros momentos da lactação
  têm exigências e limites diferentes.
- **Raça Holandesa e alta produção.** As equações do NASEM servem para outras raças mudando peso adulto e
  composição do leite, mas não foram calibradas para cruzamentos com zebu (Girolando), comuns em Goiás, nem para
  estresse térmico.
- **Limites escolhidos:** PB ≤ 19%, P ≤ 0,42%, Ca ≤ 1% e os limites de gordura vêm do NRC (2001) ou foram
  escolhidos; o capítulo de gordura do NASEM não foi usado.
- **Preços** de várias fontes e datas (ver o CSV de preços); alguns sem cotação em Goiás.

---

## 9. Uso da dieta no RuFaS

O RuFaS aceita uma dieta definida pelo usuário no arquivo de alimentos (por exemplo,
`input/data/feed/example_Midwest_feed.json`), em **% da matéria seca** de cada alimento, uma lista por tipo de
lote (`calf`, `growing`, `close_up`, `lac_cow`), com `"user_input": true` no arquivo do animal. Para converter, basta
dividir os kg de cada alimento pelo consumo total (silagem de milho: 11,11 ÷ 29,40 = 37,8%).

Cuidados:

- **O RuFaS não usa a % fixa:** multiplica cada % por 110% do consumo que ele prevê
  (`DMI_REQUIREMENT_BOOST = 1,1`), deixa cada alimento variar ±10% (`user_defined_ration_tolerance`) e roda o
  otimizador dele dentro desses limites, com consumo entre 70% e 130% do previsto.
- **Uma dieta por lote:** todas as vacas do lote de lactação recebem a mesma mistura, em fases diferentes da
  lactação. A dieta precisa ser formulada para um animal representativo do lote, com alguma margem.
- **O RuFaS avalia a dieta com as próprias contas,** que diferem das equações do NASEM em alguns pontos e podem
  levá-lo a cortar o leite simulado mesmo com uma dieta adequada.

---

## 10. Glossário

| Sigla | Nome | O que é |
|---|---|---|
| MS | Matéria seca | O alimento sem a água; todas as % da dieta são sobre ela |
| ELL | Energia líquida de lactação | A energia que a vaca realmente usa, já descontadas as perdas (Mcal) |
| EM | Energia metabolizável | Energia digestível menos as perdas em metano e urina |
| ED | Energia digestível | Energia do alimento menos a que sai nas fezes |
| PB | Proteína bruta | Toda a proteína do alimento (N × 6,25) |
| PDR | Proteína degradável no rúmen | A parte da PB que os micróbios do rúmen usam |
| PNDR | Proteína não degradável no rúmen | A parte da PB que passa direto para o intestino |
| PM | Proteína metabolizável | A proteína absorvida no intestino: microbiana digerida + PNDR digerida |
| FDN | Fibra em detergente neutro | A fibra total da dieta |
| FDNf | FDN de forragem | A parte da fibra que vem de forragem |
| FDA | Fibra em detergente ácido | A fração mais resistente da fibra |
| EE | Extrato etéreo | A gordura total |
| AG | Ácidos graxos | A parte da gordura que fornece energia |
| DEL | Dias em lactação | Dias desde o parto |
| FDNdr, AMDr | FDN e amido degradados no rúmen | A "matéria-prima de energia" da proteína microbiana (kg/dia) |

Siglas em inglês, usadas no RuFaS e em artigos: MS = DM, PB = CP, PDR = RDP, PNDR = RUP, PM = MP, ELL = NEL,
FDN = NDF.

---

## 11. Referências

- NASEM (National Academies of Sciences, Engineering, and Medicine). *Nutrient Requirements of Dairy Cattle*,
  8ª ed. Washington, DC: The National Academies Press, 2021. Versão traduzida: *Exigências Nutricionais de
  Bovinos Leiteiros*. Capítulos 2 (consumo), 3 (energia), 5 (carboidratos, Tabela 5-1), 6 (proteína), 7
  (minerais), 19 (composição dos alimentos, Tabelas 19-1 e 19-3) e 21 (Tabelas 21-1 e 21-3).
- NRC (National Research Council). *Nutrient Requirements of Dairy Cattle*, 7ª ed. rev. Washington, DC: National
  Academy Press, 2001. Capítulo 3 (limites de gordura).
- RuFaS (Ruminant Farm Systems), versão 1.0.5: biblioteca de alimentos NASEM
  (`input/data/feed/NASEM_Comp_with_TDN.csv`).
- Preços: fontes e datas em `helpful_scripts/nrc2001_dieta_lp/alimentos_precos.csv`.
