# Planejamento local NRC / NASEM

## Executar localmente

Na raiz do RuFaS: `../venv/bin/python abrir_interface.py`. Abra http://127.0.0.1:8080. Opcional: `--port 8090`. A interface usa arquivos locais, sem CDN ou serviços externos. O servidor permanece restrito ao próprio computador.

O NRC usa o ambiente original. O NASEM roda como processo separado em `helpful_scripts/interface_rufas/.venv_nasem/bin/python`, para preservar as dependências do RuFaS. A versão utilizada é nasem_dairy 1.0.2. Dependências exatas: requirements-nasem.lock.txt. Para recriar em outro computador Linux: criar um venv nesse caminho e instalar o arquivo de dependências. Não é necessário reinstalar para a execução local atual.

## Restrições do fork

O núcleo RUFAS/, os arquivos input/ e o estudo original helpful_scripts/nrc2001_dieta_lp/ são preservados. A camada de planejamento é independente. Ela não altera a fazenda exemplo, nem afirma executar o ciclo biológico completo de uma fazenda RuFaS.

## NASEM 2021

Motor: implementação acadêmica nasem_dairy, baseada no código R que acompanha a 8ª edição. Site: https://github.com/CNM-University-of-Guelph/NASEM-Model-Python . Documentação: https://nasem-model-python.readthedocs.io/ . Livro: https://doi.org/10.17226/25806 . Uso acadêmico com atribuição ao CNM/University of Guelph e aos autores das equações NASEM/R. A licença do código R exige liberação da NASEM para uso comercial. As licenças MIT e do código R original permanecem na distribuição instalada; esta camada não reivindica autoria das equações.

Oferta e exigência são recomputadas em cada avaliação da dieta: energia, proteína metabolizável, RDP, nove aminoácidos essenciais e macrominerais. Não utiliza a rotina NASEM de oferta do núcleo RuFaS auditada anteriormente. A biblioteca canônica do pacote fornece composição completa, associada por nome exato aos IDs NASEM locais. Nenhum equivalente arbitrário é atribuído ao Tifton; ele é excluído. O catálogo da tela é gerado da mesma biblioteca. O hash da biblioteca efetivamente usada é salvo.

Variáveis de decisão: kg MS/vaca/dia de cada alimento e kg leite/vaca/dia. Objetivo principal: maximizar a produção diária constante de cada período. Objetivo alternativo: maximizar receita menos alimentação. Havendo convergência no objetivo produção, uma segunda otimização tenta minimizar custo mantendo o leite ótimo encontrado. As soluções são locais (SLSQP), sem certificado global.

Restrições: orçamento alimentar diário, CMS máximo pela equação NASEM 2-1 (peso, BCS, paridade, DEL e energia do leite), energia da meta, PM, RDP, nove aminoácidos por exigências-alvo, macrominerais, FDN>=25%, FDN de forragem>=15%, gordura<=7%, PB<=19%, Ca<=1%, P<=0,42%, exclusões, teto de caroço e estoque. Os limites percentuais são escolhas experimentais do estudo; não são regras universais NASEM. Não há relaxamento silencioso. Convergência e resíduos finais são necessários para sucesso.

O leite não é imposto como produção fixa na formulação NASEM: é limitado pelo potencial e pelas restrições. Potencial inicial é uma hipótese fornecida pelo usuário, não estimativa genética. Curva de Wood normalizada: Ypot(d)=Y0*((DEL0+d)/DEL0)^b*exp(-b*d/pico). Em cada bloco, o leite constante não excede o menor potencial diário. A formulação verifica simultaneamente os extremos do bloco e a transição de DEL 100 nas equações do motor. A dieta calculada passa por verificação nutricional em todos os dias; se falhar, o plano é rejeitado e deve-se reduzir o intervalo. A temperatura informada entra no motor como condição constante, não previsão climática.

## Horizonte e rebanho

Entradas: data inicial, dias de planejamento, intervalo de reformulação, total de animais, vacas em lactação, DEL, paridade, escore corporal, peso adulto, gestação, temperatura, potencial, composição do leite, orçamento, preços e estoques. Os resultados totalizam produção, custo e margem das vacas em lactação; não incluem alimentação dos demais animais.

Escopo: lote homogêneo em uma lactação, com peso/BCS constantes e sem mobilização de reservas, ganho corporal, reprodução, mortalidade ou secagem. Horizonte máximo DEL 305 e gestação até 250 dias. Máximo 31 períodos por cálculo. Não confundir DEL inicial com dias de planejamento. Para estudar anos, reposição e lotes secos/jovens é necessário o simulador completo e integração específica.

Estoques em kg MS totais são distribuídos uniformemente: limite diário por vaca = estoque/(vacas em lactação * dias). Isso garante consumo agregado dentro da disponibilidade, mas é uma política conservadora, sem transferência ótima de estoques entre períodos. O total do rebanho é contexto; somente vacas em lactação determinam a escala dos totais.

## Premix e adequação completa

Premix fixo 0,49 kg MS/vaca/dia, pelo preço histórico do estudo. Composição inicial vazia: contribuição nutricional zero. Garantias podem ser fornecidas em JSON. Macrominerais Ca/P/Mg/Na/Cl/K/S: g/kg MS; microminerais Co/Cu/Fe/I/Mn/Se/Zn: mg/kg MS; VitA/VitD/VitE: UI/kg MS. Apenas microminerais/vitaminas declarados são impostos como restrições. Usar a garantia real do produto, não valores inventados. Sem essa informação, não é possível certificar dieta completa. Coeficientes de absorção do premix são hipóteses da biblioteca e da implementação: verificar adequação às fontes químicas reais.

## NRC e comparabilidade

A opção NRC preserva formulação de custo para meta fixa. O caso 680 kg, 54,4 kg leite, gordura 3,5%, proteína 3%, DEL90 reproduz R$34,54 com 27 restrições. Fora do caso, exigências aproximadas calibradas, CMS sensível ao DEL e NEL-4X fixa. A comparação NRC custo-fixo versus NASEM produção-variável não isola efeito do padrão: objetivos e bibliotecas são diferentes. Comparações científicas devem controlar esses fatores.

## Resultados, fila e reprodução

NASEM roda em fila local, um cenário por vez, com progresso; limite de 30 minutos. Exportação automática para output/estudo_dieta/nasem_<id>.json contém parâmetros, dietas por período, balanços, aminoácidos, série diária, totais e hashes. A tela também baixa o JSON. Preços históricos não são cotações atuais. Alterar os controles invalida os resultados da tela. Fila volátil: reiniciar servidor perde o estado da fila, mas preserva exportações concluídas.

Testes NRC: `../venv/bin/python -m unittest discover -s helpful_scripts/interface_rufas -p test_local.py -v` (na raiz, ajustar o caminho do ambiente se necessário).
Testes NASEM: `helpful_scripts/interface_rufas/.venv_nasem/bin/python -m unittest discover -s helpful_scripts/interface_rufas -p test_nasem.py -v`.

Os testes NASEM incluem o exemplo publicado pelo pacote, unidades do premix, mapeamento exato, aminoácidos-alvo, bloqueios, estoques e cenários inválidos. Isso valida o adaptador no escopo testado; não substitui validação zootécnica em campo ou comparação integral com o software oficial.
