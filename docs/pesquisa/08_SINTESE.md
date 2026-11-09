# Síntese da missão (direção de produto e investigação)

Data: 08/11/2026. Base: relatórios 01 a 07 desta pasta. Conferi por conta própria os pontos marcados "conferido".

## 1. Diagnóstico em uma frase
O Radar já enxerga bastante, mas **ainda não pode afirmar que é confiável**: a primeira medição de precisão mostrou que só um terço dos alertas auditados merece atenção, e a interface e a base técnica ainda não servem bem ao celular nem à privacidade das pessoas.

## 2. Fatos que mudam o plano
1. **Precisão (auditoria 06, amostra de 60):** fato correto em 87%; conclusão de atenção sustentada em 32% (IC 21–44%); falso positivo 10%. Prioridade máxima: 50% (IC 27–73%). Regras mais fracas: R04 e R08 (0/4), R05 e R10 (1/6). Amostra pequena por regra, os intervalos são largos. Conferido: **linhas idênticas repetidas** em 43 de 113 alertas R02 (38%), 17 de 81 R05 e 21 de 79 R08, ou seja, dado duplicado por junção inflando valor. R11 não tem esse problema.
2. **"12 trilhões" é o PIB, não o gasto público (04).** LOA 2026: R$ 6,54 tri (R$ 1,8 tri é rolagem da dívida). Estados empenharam R$ 1,416 tri em 2024. O Radar vê hoje ~R$ 1,5 tri em compras (PNCP). A meta honesta é "quanto do gasto público o Radar enxerga".
3. **Mercado (02):** o Achados e Pedidos (ponte LAI, Transparência Brasil + Abraji) encerrou em 31/01/2026 (conferido): vaga aberta. Usuário: 65% só celular, 39% já ficaram sem pacote de dados, 29% analfabetos funcionais; YouTube, Instagram e WhatsApp como fonte de notícia. A autoria do Politicômetro citada no relatório **não foi confirmada**.
4. **Jurídico (05, revisão por advogado ainda necessária):** o risco está no que o Radar afirma, não em publicar dado público; pior risco = homonímia e o alerta virar manchete de WhatsApp. R12: servidor pode ser sócio cotista (Lei 8.112, art. 117, X); só administrar é vedado. Sem ficha de pessoa privada, sem foto de pessoa, sem fragmento de CPF.
5. **Técnica (07):** JS do painel de 1,72 MB (conferido); data de nascimento completa no JSON público de pessoas (conferido: campo `nasc`); pipeline com falhas recorrentes; sem URL por entidade.
6. **Metodologia (03):** pontuação mistura eixos e conta em dobro (R01/R02/R11 são o mesmo fato); sinal de maior poder (proposta única) exige dado de licitantes que não temos. O limite de dispensa da R06 não é um erro: o inciso de compras era R$ 62.725,59 em 2025, mas os limites mudaram em 2026 (Decreto 12.807/2025) e a faixa precisa ser atualizada.
7. **Design (01):** o júri do Sigma premia método à mostra, caso concreto e forma própria do dado. Recomendação do pesquisador (Extrato) repete o cinza já rejeitado; a escolha defendida aqui é **Sobreposição** (cor com função: restrição = azul, pagamento = amarelo, interseção escura, vermelho só no que coincide) com a disciplina do Extrato.

## 3. Proposta de rota (ordem importa)
**Fase 1 (2 semanas): credibilidade e segurança.** Corrigir os bugs da auditoria (duplicação por junção; usar data de registro/publicação da sanção e não só o início; filial ≠ empresa nova; "empresa nova" da R09; fim do mandato na R10; alcance restrito na R01; valor/prazo na R04); remover ou rebaixar R04/R08 até corrigir; reduzir "prioridade máxima" ao que a amostra sustenta; publicar um **placar de qualidade** por regra; tirar `nasc` do JSON público; ajustar o texto da R12; aplicar a política de linguagem do jurídico.
**Fase 2 (2 meses): produto.** Posicionamento "extrato do dinheiro público": **Meu município** primeiro (emendas, contratos, convênios, Siconfi), ficha com URL permanente e imagem para WhatsApp, "Pergunte ao órgão" (pedido de LAI pronto), cartão de prova com "o que isto não prova". Peso de abertura abaixo de 300 KB por rota e pipeline confiável (fontes instáveis, retries, painel de frescor). Primeiras fontes novas: Siconfi, TransfereGov, TCE-SP/PE/RS, dados de licitantes.
**Fase 3 (6 meses): escala.** Prototipar a Sobreposição, testar com 6 a 8 pessoas (Android de entrada: tempo até achar a cidade ≤ 30 s, SUS ≥ 80, ≥ 90% entendem o "não prova"); PWA instalável; associação sem fins lucrativos com seguro e conselho; só então ampliar para outros países.

## 4. Decisões que dependem do cliente
1. Aprovar **credibilidade antes de novos recursos** (congelar novas telas e fontes até a Fase 1 terminar).
2. Autorizar a **remoção da data de nascimento** do site público.
3. Aceitar a **meta honesta** ("o que o Radar enxerga do gasto público") no lugar de "os 12 trilhões".
4. Escolher o território visual a prototipar (recomendado: Sobreposição) e o teste com usuários.
5. Definir a estrutura jurídica (pessoa física hoje; associação sem fins lucrativos recomendada).

## 5. Limites desta síntese
Relatórios dependem de pesquisa na web com bloqueios (vários sites 429/403), amostras pequenas na auditoria, números de custo jurídico sem cotação e personas sem entrevistas. Tudo marcado "A CONFERIR" nos relatórios continua a conferir.
