# Dieta de custo mínimo para vaca leiteira (NRC 2001, preços de Goiás)

Modelo de programação linear que encontra a combinação de alimentos **mais barata** capaz de atender às
exigências nutricionais de uma vaca leiteira, segundo o *Nutrient Requirements of Dairy Cattle*
(NRC, 7ª ed. revisada, 2001), com preços de alimentos cotados para Goiás.

**Resultado:** R$ 34,54 por vaca por dia (R$ 0,63 por kg de leite), na versão recomendada.

---

## 1. Como a dieta foi definida

O solver escolhe as quantidades. As decisões humanas estão em **quais exigências** a dieta deve atender e
**quais alimentos** podem ser usados.

### 1.1 Vaca de referência e exigências

Usamos a coluna Holandesa de **54,4 kg de leite/dia** da Tabela 14-7 do NRC (680 kg de peso vivo, 90 dias em
lactação, leite com 3,5% de gordura e 3,0% de proteína). Ela foi escolhida por dois motivos: é a única tabela
que traz, para a mesma vaca, consumo, energia, proteína, fibra e minerais; e a produção fica próxima do pico
de uma vaca simulada no RuFaS (54,8 kg/dia).

A produção de leite é **fixa**: o modelo não decide quanto a vaca produz, ele busca a dieta mais barata que
atende às exigências dessa produção.

### 1.2 Alimentos candidatos

1. **Ponto de partida:** os ingredientes da dieta de exemplo da própria Tabela 14-7.
2. **Adaptação à legislação brasileira:** farinha de sangue e sebo foram retirados. A IN MAPA 8/2004 proíbe
   proteínas e gorduras de origem animal na alimentação de ruminantes, e a lista da IN 110/2020 cita os dois.
3. **Adaptação ao mercado:** milho floculado → milho moído; fosfato monossódico → fosfato bicálcico;
   feno de gramínea de clima temperado → feno de Tifton 85 (por falta de preço ou de produção em Goiás).
4. **Ampliação:** entraram todos os alimentos da biblioteca do RuFaS que são comuns em Goiás e para os quais
   foi encontrado preço. Total: **17 candidatos** (lista em `alimentos_precos.csv`).
5. **Premix vitamínico e mineral:** fixo em 0,49 kg/dia, quantidade da dieta do livro. A biblioteca não tem
   teores de vitaminas e microminerais, então essas exigências não entram no solver e são garantidas pelo premix.

Se um alimento não compensar, o solver o deixa em zero. Por isso, acrescentar candidatos nunca aumenta o custo.

### 1.3 Composição e preços

- **Composição:** biblioteca NRC do RuFaS (`input/data/feed/NRC_comp.csv`). Nos alimentos conferidos,
  os valores são iguais aos das Tabelas 15-1, 15-2a e 15-3 do livro.
- **Energia (NEL-4X):** Tabela 15-1, porque a biblioteca não tem essa coluna.
- **Preços:** cotações de 04 a 06/11/2026 (IFAG, Agrolink, Notícias Agrícolas, MF Rural e um pregão público),
  com fonte, link e data por alimento em `alimentos_precos.csv`.
- **Conversão:** o modelo trabalha em matéria seca (MS), que é o alimento sem a água; é na MS que estão os
  nutrientes. Preço por kg de MS = preço por kg natural ÷ (MS% / 100).

---

## 2. Modelagem

### 2.1 Notação

| Símbolo | Significado | Unidade |
|---|---|---|
| $i$ | alimento candidato (17 no total) | – |
| $x_i$ | **variável de decisão**: quantidade do alimento $i$ na dieta | kg de MS/dia |
| $c_i$ | preço do alimento $i$ | R$/kg de MS |
| $q$, $c_q$ | premix fixo: 0,49 kg/dia a R$ 11,94/kg | kg, R$/kg |
| $T = \sum_i x_i + q$ | consumo total de matéria seca | kg/dia |
| $a_{ik}$ | teor do nutriente $k$ no alimento $i$ | g/kg ou % da MS |

### 2.2 Função objetivo

$$\min Z = \sum_i c_i\,x_i + c_q\,q$$

Custo diário da dieta. O termo do premix é constante (R$ 5,85) e não altera a escolha dos demais alimentos.

### 2.3 Restrições

**Exigências em quantidade** (forma $\sum_i a_{ik}\,x_i \ge b_k$; exigências da Tabela 14-7):

| Restrição | Limite | O que é |
|---|---|---|
| Energia líquida de lactação (NEL) | ≥ 48,3 Mcal | Energia para mantença e produção de leite |
| Proteína degradável no rúmen (RDP) | ≥ 2947 g | Proteína que alimenta os microrganismos do rúmen |
| Proteína metabolizável (PM), duas formas | ≥ 3476 g | Proteína que a vaca de fato absorve (ver 2.4) |
| Cálcio absorvível | ≥ 88 g | Ca do alimento × coeficiente de absorção |
| Fósforo absorvível | ≥ 80,3 g | P do alimento × coeficiente de absorção |
| Mg, K, Na, Cl, S | ≥ 63, 321, 66, 87, 60 g | % exigido na dieta × 30 kg de MS |
| Relação Ca:P | P ≤ Ca ≤ 7 P | Faixa considerada segura (cap. 6) |

**Limites em % da dieta** (forma $\sum_i a_{ik}\,x_i \ge b_k\,T$, que vira $\sum_i (a_{ik} - b_k)\,x_i \ge b_k\,q$,
uma restrição linear):

| Restrição | Limite | O que é / fonte |
|---|---|---|
| NDF de forragem (NDFf) | ≥ 15% | Fibra vinda de volumosos; mantém a ruminação (Tab. 4-3) |
| NDF total | ≥ 25% | Fibra em detergente neutro (Tab. 4-3) |
| ADF | ≥ 17% | Fibra em detergente ácido (Tab. 4-3) |
| NFC | ≤ 44% | Carboidratos não fibrosos (amido, açúcares); excesso causa acidose (Tab. 4-3) |
| NDF + 2 NDFf | ≥ 63% | Combinação de NDF e NDFf da Tab. 4-3 (ver abaixo) |
| ADF + NDFf | ≥ 36% | Idem |
| NFC − 2 NDFf | ≤ 6% | Idem |
| Extrato etéreo (gordura total) | ≤ 7% | Cap. 3, p. 32 |
| Gordura suplementar | ≤ 4% | Caroço de algodão, soja grão e sabões de cálcio (cap. 3) |
| Ca | ≤ 1% | Acima disso, menor consumo e desempenho (cap. 6) |
| P | ≤ 0,42% | Sem benefício acima disso (cap. 6); usado como teto por escolha nossa |
| Proteína bruta (PB) | ≤ 19% | Associada a menor fertilidade (cap. 5, p. 52); escolha nossa |

**Consumo e domínio:**

$$30 \le T \le 30{,}95 \qquad x_i \ge 0$$

A Tabela 14-7 prevê 30 kg de MS/dia, e a dieta de exemplo do livro soma 30,95 kg. Na versão recomendada (B),
o caroço de algodão tem teto de 2,53 kg/dia, a maior quantidade usada nas dietas da Tabela 14-7.

**Tabela 4-3 em forma linear.** A tabela combina os limites: para cada ponto a menos de NDF de forragem
(de 19% até 15%), o NDF mínimo sobe 2 pontos, o ADF mínimo sobe 1 e o NFC máximo cai 2. Isso equivale a:
NDF ≥ 25 + 2(19 − NDFf), ADF ≥ 17 + (19 − NDFf) e NFC ≤ 44 − 2(19 − NDFf), que são as três restrições combinadas acima.

### 2.4 Como os coeficientes são calculados

**Proteína (cap. 5).** Cada alimento tem frações de proteína: A (degradada na hora), B (degradada aos poucos,
à taxa $K_d$) e C (não degradável). A parte que escapa do rúmen (RUP) depende da taxa de passagem $K_p$:

$$\text{RUP}_i = B_i \frac{K_p}{K_{d,i} + K_p} + C_i \qquad \text{RDP}_i = \text{PB}_i - \text{RUP}_i$$

| Tipo de alimento | $K_p$ (%/h) |
|---|---|
| Forragem úmida (silagem) | $3{,}054 + 0{,}614\,X_1$ |
| Forragem seca (feno) | $3{,}362 + 0{,}479\,X_1 - 0{,}007\,X_2 - 0{,}017\,\text{NDF}_i$ |
| Concentrado | $2{,}904 + 1{,}375\,X_1 - 0{,}020\,X_2$ |

$X_1$ = consumo em % do peso vivo; $X_2$ = % de concentrado na dieta.

**Proteína metabolizável (cap. 5, p. 58 e 67–68).** Soma da proteína microbiana digerida, do RUP digerido e
da proteína endógena:

$$\text{PM}_i = 0{,}64\,\text{PCM}_i + \text{dRUP}_i\,\text{RUP}_i + 0{,}4 \times 11{,}8$$

A proteína microbiana (PCM) é o **menor** entre $0{,}13 \times \text{NDT descontado}$ e $0{,}85 \times \text{RDP}$.
Como "o menor de dois valores" não é linear, o modelo exige que as duas versões atendam à exigência (duas
restrições), o que é equivalente.

**Desconto do NDT.** Vacas que comem muito digerem um pouco menos; o NDT é corrigido pelo nível de consumo
(fórmula do RuFaS).

**Cálcio e fósforo absorvíveis (cap. 6 e Tab. 15-4).** Teor × coeficiente de absorção: Ca 0,30 em forragens,
0,60 nos demais alimentos, 0,80 nos sabões de cálcio, 0,70 no calcário e 0,94 no bicálcico; P 0,64 em
forragens, 0,70 nos demais e 0,75 no bicálcico.

### 2.5 Ponto fixo

$K_p$ e o desconto do NDT dependem da própria dieta (consumo e % de concentrado), o que tornaria o problema
não linear. O solver resolve isso por iteração: fixa esses valores (partindo da dieta do livro), resolve o
problema linear, recalcula $K_p$ e o desconto com a dieta obtida e repete até a diferença ficar abaixo de
$10^{-6}$. Na prática, converge em 2 a 7 rodadas.

---

## 3. Como o solver foi construído

- **Linguagem e biblioteca:** Python, com `scipy.optimize.linprog` no método simplex dual do HiGHS (`highs-ds`).
- **Entrada:** `alimentos_precos.csv` (alimentos, NEL-4X, preços e fontes) e a biblioteca de alimentos do RuFaS.
- **Fluxo em `solver.py`:**
  1. `carregar_alimentos`: junta preços e composição e converte o preço para R$/kg de MS.
  2. `coeficientes_proteina`: calcula RUP, RDP e PM de cada alimento para o $K_p$ e o desconto atuais.
  3. `montar_restricoes`: monta as 27 restrições na forma matricial $A x \le b$.
  4. `resolver`: roda o simplex e o ponto fixo da seção 2.5.
  5. `relatorio`: mostra a dieta, o custo por alimento, as restrições no limite e, para cada alimento fora
     da dieta, quanto o preço teria de cair para ele entrar (custo reduzido).

**Verificações feitas:**

- **Leitura das tabelas:** recalculando a dieta de exemplo do livro, obteve-se NDT de 73,8% (livro: 74%) e PB
  de 16,6% (livro: 16,7%).
- **Exigência de proteína metabolizável:** a fórmula do cap. 5 reproduz as 10 colunas da Tabela 14-7 com erro
  máximo de 0,19%.
- **Exigência de fósforo:** a fórmula do cap. 6 dá 80,32 g (tabela: 80,3 g).
- **Solução:** nenhuma das 27 restrições é violada, e o método de pontos interiores chega ao mesmo custo do simplex.
- **Inconsistência encontrada no livro:** os valores de RUP de exemplo da Tabela 15-2a para fenos só são
  reproduzidos com $+0{,}007\,X_2$ na equação de $K_p$, mas o texto (p. 61) traz $-0{,}007\,X_2$. O modelo usa
  o texto; o efeito na dieta é de cerca de 14 g de RUP.

---

## 4. Resultados

| kg de MS/dia | A. Sem teto | B. Caroço ≤ 2,53 kg (recomendada) |
|---|---|---|
| Silagem de milho | 16,58 | 19,82 |
| Milho moído | 1,96 | 0,43 |
| Farelo de soja | 3,61 | 0,67 |
| Soja grão | 0 | 3,41 |
| Caroço de algodão | 6,41 | 2,53 |
| Farelo de algodão | 1,50 | 3,20 |
| Calcário calcítico | 0,24 | 0,24 |
| Cloreto de sódio | 0,15 | 0,15 |
| Premix (fixo) | 0,49 | 0,49 |
| **Custo** | **R$ 33,48/dia** | **R$ 34,54/dia** |

A versão A usa quase 3 vezes o caroço da dieta do livro, limitada apenas pela gordura suplementar, e o modelo
não considera o gossipol; por isso a recomendada é a B. Nela ficam no limite: energia, Ca absorvível, Na, S,
proteína metabolizável, teto de P e consumo máximo.

**Sensibilidade (versão B):** silagem de milho a R$ 380/t → R$ 40,54/dia, com mudança da dieta; farelo de
algodão a R$ 1.400/t → R$ 35,42/dia; casca de soja a R$ 1.300/t ou polpa cítrica a R$ 1,45/kg → sem mudança;
sem premix → R$ 27,91/dia, mas com a dieta incompleta em vitaminas e microminerais.

## 5. Limitações

- **Silagem:** é o preço que mais pesa no custo, e o disponível é de jan/2025.
- **Farelo de algodão:** o preço é do produto com 38% de PB, e a composição do livro tem 44,9%, o que o favorece.
- **Preços de outros estados** (alfafa, polpa cítrica, farelo de trigo, sabões, sal): não incluem frete até Goiás.
- **Fora do modelo por falta de preço:** DDG, melaço, farelo de arroz, refinazil, farelo de girassol, entre outros.
- **Fora da biblioteca:** cana-de-açúcar, capins tropicais, milheto e ureia não estão nas tabelas do NRC.
- **Premix:** seus nutrientes (Ca, P, Na, S) contam como zero, o que é conservador.

## 6. Como rodar

O solver lê a biblioteca de alimentos do RuFaS (`input/data/feed/NRC_comp.csv`), então deve ficar dentro do
repositório do RuFaS. A partir da raiz:

```bash
python helpful_scripts/nrc2001_dieta_lp/solver.py                  # versões A e B
python helpful_scripts/nrc2001_dieta_lp/solver.py --sensibilidade  # mais os testes de sensibilidade
```

Requer Python 3 com `numpy`, `pandas` e `scipy`. Para mudar preços ou acrescentar alimentos da biblioteca,
edite `alimentos_precos.csv`.

## Referências

- National Research Council. *Nutrient Requirements of Dairy Cattle*, 7ª ed. revisada. National Academy Press, 2001.
  Tabelas 4-3, 14-7, 15-1, 15-2a, 15-3, 15-4 e capítulos 3, 5 e 6.
- Brasil, MAPA. Instrução Normativa nº 8, de 25/03/2004, e Instrução Normativa nº 110, de 24/11/2020.
- Fontes de preço: ver `alimentos_precos.csv`.
