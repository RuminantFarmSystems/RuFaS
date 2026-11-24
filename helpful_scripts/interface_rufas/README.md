# Dietas de custo mínimo para produção de leite informada

## Objetivo do trabalho

O foco é otimizar a produção leiteira por formulação alimentar: encontrar a dieta de menor custo que atenda às exigências da produção informada. Em ambos os padrões, leite é parâmetro. No NASEM, as únicas variáveis de decisão são kg de matéria seca de cada alimento por vaca/dia. Função objetivo: min(soma(preço_MS * quantidade_MS) + custo_premix). Não há redução automática de leite, maximização de volume ou maximização de margem.

## Rodar localmente

Use Linux/Python 3.12. Na instalação antiga: `../venv/bin/python abrir_interface.py`. No clone, use um ambiente com NumPy, pandas e SciPy: `python abrir_interface.py`, com esse ambiente ativado. Endereço http://127.0.0.1:8080; outra porta: `--port 8090`. Não é necessário serviço externo durante o cálculo.

O NASEM é executado separadamente em helpful_scripts/interface_rufas/.venv_nasem/bin/python. Para preparar esse ambiente em outro computador: criar venv nesse caminho e instalar requirements-nasem.lock.txt. O servidor usa o ambiente do projeto; não instale versões NASEM/NumPy 1.26 no ambiente RuFaS/NumPy 2. Windows nativo exige adaptar o caminho bin/python; WSL/Linux é compatível.

## Modelagem e restrições

O NRC da interface preserva as 27 desigualdades do estudo original: meta fixa, energia NEL-4X tabular, proteína, fibra, minerais e consumo. Fora do caso de referência, existem aproximações de exigências calibradas. A referência 680 kg, 54,4 kg leite/dia, gordura 3,5%, proteína 3%, DEL90 reproduz R$34,54/vaca/dia.

O NASEM usa nasem_dairy 1.0.2, biblioteca canônica do pacote associada por nome aos IDs locais, e SLSQP para custo mínimo. A meta fica constante no horizonte. Capacidade de ingestão depende do peso, escore, paridade, DEL e energia dessa produção. Oferta e exigência são avaliadas para cada dieta candidata: energia, PM, RDP, nove aminoácidos essenciais e Ca/P/Mg/Na/Cl/K/S. Impõem-se ainda FDN>=25%, FDN forrageira>=15%, gordura<=7%, PB<=19%, Ca<=1% e P<=0,42%. Esses limites percentuais são escolhas do estudo, não regras universais NASEM. Há bloqueios, teto de caroço e estoques. Quantidade de alimento limitada também a 40 kg MS/dia como limite operacional.

Teto de custo é opcional (nulo = sem teto). Se informado, é restrição adicional, nunca um objetivo. O preço do leite é usado para calcular receita e margem, não para escolher a dieta. O mínimo de custo também maximiza a margem alimentar para a mesma produção e preço, mas não é lucro líquido da fazenda.

SLSQP: até60 iterações, ftol=1e-7, eps=1e-4. Restrições escaladas aceitas com resíduo>=-1e-5. Exige convergência e recomputação final. É uma solução local, sem certificado global. Nas versões originais dos estudos NRC e NASEM/PuLP, preservadas, há rodadas externas de LP: congelar coeficientes, otimizar, recalcular consumo/composição e repetir até estabilizar. No adaptador NASEM da interface, as relações não lineares são reavaliadas a cada dieta candidata dentro do SLSQP; não confundir os dois algoritmos.

## Tempo e rebanho

DEL é o estágio inicial; dias_simulacao é a duração do planejamento; intervalo_dieta é o número de dias com a mesma dieta. Só as dietas variam entre períodos; a meta informada não muda. DEL, idade e gestação positiva avançam no tempo. Dietas são formuladas nos extremos do bloco e na transição DEL100, e verificadas depois em todos os dias. Falha em qualquer dia rejeita o plano e recomenda rever intervalo/dados.

O planejamento abrange um lote homogêneo de vacas em lactação, com peso/escore constantes, sem reprodução, mortalidade, secagem, variação corporal ou estimativa genética. Limites: DEL inicial+duração<=305, gestação positiva+duração<=250, no máximo31 períodos. Total do rebanho é contexto; somente vacas_lactacao determina a escala de produção e custos. Produção total exibida é a meta agregada, não uma previsão observada ou variável otimizada.

Estoques: kg MS totais para o horizonte; teto diário uniforme por vaca = estoque/(lactantes*dias). Não há alocação temporal livre. Premix0,49 kg MS/dia fixo, sem estoque próprio. Tifton não é substituído por outro alimento no adaptador: não tem correspondência NASEM validada.

## Premix e limites de adequação

Garantia em JSON: macrominerais Ca/P/Mg/Na/Cl/K/S em g/kg MS; Co/Cu/Fe/I/Mn/Se/Zn em mg/kg MS; VitA/VitD/VitE em UI/kg MS. Composição vazia significa contribuição zero. Macrominerais são sempre restrições; micros/vitaminas só são impostos se declarados. Dose fixa não garante dieta completa.

Há uma pendência conhecida, não alterada nesta mudança de objetivo: o portador mineral zera campos numéricos e restabelece algumas absorções (Ca0,70; P0,75; Cl0,92; Na/K1). Absorções de Cu,Fe,Mn,Zn permanecem zero. Declarar teor não comprova fornecimento absorvido. Corrigir e validar essas fontes antes de interpretar o premix como garantia nutricional completa. O portador tem cinzas100% para não criar energia orgânica fictícia.

## Arquivos e reprodução

Código principal: nasem_solver.py (validate, library, Formulator.evaluate/solve, planejar), solver_dinamico.py (NRC), jobs_nasem.py/worker_nasem.py (fila/processo), abrir_interface.py (API), interface/ (tela). nasem_seed.json fornece apenas uma partida numérica. alimentos_nasem.json é catálogo serializado: alterações externas de preços/biblioteca exigem regeneração. requirements-nasem.lock.txt fixa as versões.

Exportação NASEM: output/estudo_dieta/nasem_<id>.json, com objetivo=custo, cenário, leite_meta por período, dietas, folgas, AA, série diária, totais e proveniência modelo=custo-minimo-meta-fixa-v3. Cenários antigos de produção/margem e pico_del/declinio_curva são rejeitados, evitando reinterpretar silenciosamente estudos antigos. Os campos leite_otimizado/potencial foram retirados.

Fila local, um cenário por vez, até3 ativos/aguardando; timeout10 minutos para a tarefa; busca limitada a120 segundos por período. Fila volátil; exportações concluídas permanecem. Valores monetários usam R$/kg de leite, sem conversão implícita para litro. Preços iniciais são históricos.

Testes: `python -m unittest discover -s helpful_scripts/interface_rufas -p test_local.py -v` com ambiente da interface; `.venv_nasem/bin/python -m unittest discover -s helpful_scripts/interface_rufas -p test_nasem.py -v` com caminho completo a partir da raiz. Incluem regressões de objetivo e preservação da meta. Esses testes não equivalem à validação integral do livro ou à simulação de fazenda.

## Relação com RuFaS e licenças

Núcleo RUFAS/, input/ e estudos originais helpful_scripts/nrc2001_dieta_lp/ e helpful_scripts/nasem2021_dieta_lp/ são preservados. A camada não aplica dietas ao simulador completo de fazenda. Atribuir o motor ao CNM/University of Guelph: https://github.com/CNM-University-of-Guelph/NASEM-Model-Python ; livro https://doi.org/10.17226/25806 . RuFaS GPLv3; pacote MIT e código R com termos próprios, incluindo liberação NASEM para uso comercial.

## Confiabilidade e diagnóstico — revisão 24/11/2026

Preços e estoques aceitam ponto ou vírgula decimal, sem separador de milhar. A tela mostra a conversão do estoque total para kg MS/vaca/dia. Exemplos: 10.000 kg MS para100 vacas e30 dias impõem3,3333 kg/vaca/dia. Estoque vazio é sem limite; zero é proibição de usar aquele alimento. Valores pequenos podem tornar a dieta inviável, mesmo com o sistema funcionando.

Antes da busca não linear, um LP verifica condições lineares necessárias de fibra, limites, consumo e teto de custo. Um cenário impossível nessas condições é rejeitado imediatamente, sem relaxar regras. Uma dieta inicial é escolhida considerando os limites atuais; quando distante da viabilidade, uma fase auxiliar de mínimos quadrados tenta reduzir violações antes da minimização de custo. Essa fase não é aceita como resultado final, e nenhuma violação é escondida. Sucesso ainda exige término SLSQP e reavaliação nutricional. Não há prova de ótimo global.

O progresso informa fase, tempo e avaliações nutricionais aproximadamente a cada2 segundos, além das iterações de custo. Há cancelamento de tarefas ativas ou aguardando. Durante o cálculo, entradas ficam bloqueadas para evitar mistura de cenários; cancele antes de editar. O worker é encerrado ao cancelar ou atingir seu tempo máximo. Falhas também são salvas em output/estudo_dieta/ para diagnóstico local.

A tabela de iterações inclui custo, consumo, amido e energia digestível estimada do amido (Mcal/kg de amido ingerido), além do resíduo normalizado. Ela mostra avaliações SLSQP; não representa as rodadas externas de LP dos scripts originais. Energia estimada pela equação não é energia medida em laboratório.

NutriPlan foi consultado como comparação de desenho e validação: partida coerente com limites, validação numérica e diagnóstico são necessários aqui. Não foram incorporados seu motor, categorias adicionais, busca de maior produção, emissões ou catálogo ampliado. Os modelos têm bibliotecas e restrições diferentes; resultados não são diretamente intercambiáveis.

Testes de confiabilidade: executar `test_reliability.py` no ambiente NASEM. Cobrem estoques na escala do horizonte, impossibilidade linear, relógio, cancelamento e término por timeout. Testes de navegador também verificam números com vírgula, alteração de preço, exclusão, estoque, inviabilidade e liberação do formulário após cancelar.
