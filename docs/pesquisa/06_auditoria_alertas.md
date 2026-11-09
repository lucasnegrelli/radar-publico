# Auditoria de precisão dos alertas do Radar Público

Data: 08/11/2026. Base auditada: `web/public/data/alertas.json` (gerado em 04/11/2026, 1.581 alertas R01 a R12; RF01 fora do escopo). Método: amostra estratificada de 60 alertas, conferida contra fontes primárias. Não foi alterado código nem dado do produto.

Convenção: **VERIFICADO** = conferi na fonte; **FONTE** = afirmado por fonte citada; **INFERÊNCIA** = raciocínio meu.

## 1. Resposta curta

Em 60 alertas conferidos (VERIFICADO):

| Resultado | N | % | IC 95% (Wilson) |
|---|---|---|---|
| VERDADEIRO-RELEVANTE | 19 | 32% | 21% a 44% |
| VERDADEIRO-BENIGNO | 33 | 55% | 43% a 67% |
| FALSO-POSITIVO | 6 | 10% | 5% a 20% |
| NÃO-VERIFICÁVEL | 2 | 3% | 1% a 11% |

- **O fato descrito está certo em 87% (52/60; IC 76% a 93%).** O produto raramente "inventa". Os dados de base (CEIS, PNCP, Receita, TSE, emendas) batem.
- **A conclusão de atenção só se sustenta em 32% (IC 21% a 44%).** A maior parte dos alertas é um fato real com explicação comum (contrato de vários anos, multinacional com holding, pregão com um único vencedor, sanção ainda não publicada quando o contrato foi assinado).
- **Prioridade máxima (14 alertas da amostra, 47 na base): 7 relevantes (50%, IC 27% a 73%), 6 benignos, 1 falso positivo.** Dois dos 14 são da mesma empresa (Solarterra: R09 e R11), então são 13 entidades distintas. Ou seja: o selo "prioridade máxima" hoje acerta cerca de metade das vezes. Isso não sustenta a promessa "quem faz algo errado tem medo de aparecer".
- **Gravidade "alta" da regra (975 alertas na base, 33 na amostra): 14 relevantes (42%, IC 27% a 59%).** Extrapolação (INFERÊNCIA): de ~975, algo entre 260 e 575 mereceriam ser "alta"; o ponto central é ~410. As regras R04 e R08 não acertaram nenhuma vez em 4.
- Dois problemas técnicos atingem número e não só julgamento: **valor duplicado** (a mesma linha contada 2 a 4 vezes) em 29% dos alertas R02, 11% dos R05 e 18% dos R08 da base; e **"empresa nova" calculada pelo estabelecimento, não pela empresa**.

Limite honesto: n por regra é 4 a 7. Os intervalos por regra são largos (ver seção 3). Servem para priorizar correção, não para publicar "precisão da R05 = 17%".

## 2. Método

**Amostra (reprodutível).** Semente `20261108` (`random.Random`), sobre os 1.581 alertas. A "prioridade máxima" foi reconstruída com a fórmula de `web/main.js` (`pontuar`, linhas 167 a 172): gravidade (100/40/0) + 14·log10(valor) + 45 se há sinais combinados + peso do tipo + bônus (novo, político, autor de emenda, sanção/CEPIM). Os 3% de maior nota (47 alertas) são "máxima"; os 18% seguintes (285) "relevante"; o resto (1.249) "contexto". Passos: (1) 12 da prioridade máxima sorteados por regra (R11: 5, R02: 4, R09: 3; só há máxima nessas três regras, mais 2 que o sorteio global trouxe); (2) 12 aleatórios globais; (3) completar cotas por regra: R01, R03, R04, R06, R07, R08, R12 = 4 cada; R09 = 7, R11 = 7, R02 = 6, R10 = 6, R05 = 6. Resultado: 60 alertas, 14 de prioridade máxima, 7 relevante, 39 contexto. Arquivos intermediários (amostra e dossiês) ficaram fora do repositório.

**Fontes usadas (VERIFICADO).**
- `[CEIS-CSV]` / `[CEIS-API]`: CEIS/CNEP do Portal da Transparência. CSV de 30/10/2026 (`dados/csv/20261030_CEIS.csv`, completo) e API `api-de-dados/ceis?codigoSancionado=` (consultada em 06/11/2026; a API devolve 15 por página, por isso o CSV foi a base de contagem). Chave só em cabeçalho, nunca gravada.
- `[PNCP]`: `https://pncp.gov.br/api/consulta/v1/contratos?cnpjOrgao=...` para 29 contratos (valor, data de assinatura, vigência, tipo). O endpoint individual `/api/pncp/v1/orgaos/.../contratos/ano/seq` devolveu 503 durante toda a sessão.
- `[RFB]`: BrasilAPI `https://brasilapi.com.br/api/cnpj/v1/{cnpj}` (situação, abertura, capital, matriz/filial, quadro societário) para 58 CNPJs, 1 chamada por CNPJ.
- `[DESP]`, `[EMD]`, `[CEPIM]`: arquivos do Portal da Transparência (recebimentos por favorecido, emendas por favorecido, CEPIM), conferidos linha a linha contra as tabelas dos alertas.
- `[TSE]`: `dados/tse/consulta_cand_*.parquet` (resultado "ELEITO" por ano). `[SIAPE]`, `[CAMARA]`: bases locais do projeto.

**O que NÃO consegui fazer (classificaria como NÃO-VERIFICÁVEL se decisivo).** (i) Decisão judicial suspendendo sanção: nem CEIS nem API trazem esse campo; não achei evidência de suspensão em nenhum caso, mas isso é ausência de prova, não prova de ausência. (ii) Licitantes e propostas de cada licitação ("licitação por dentro" não existe em dado aberto agregado). (iii) Notícias e TSE DivulgaCand web: não consultei; usei o dado TSE local. (iv) Homônimo em R10/R12: o casamento é por nome completo (R10) ou nome parcial (R12) mais CPF parcial; conferi o QSA da Receita em 100% dos R10, e o resultado bateu, mas não consigo ver o CPF completo (INFERÊNCIA de que são a mesma pessoa).

## 3. Métricas

Definição: precisão = VERDADEIRO-RELEVANTE / total. "Fato correto" = RELEVANTE + BENIGNO.

### Por regra (n pequeno; IC de Wilson 95%)

| Regra | n | Relev. | Benigno | Falso+ | NV | Precisão | IC 95% |
|---|---|---|---|---|---|---|---|
| R01 cota x punida | 4 | 2 | 0 | 2 | 0 | 50% | 15-85% |
| R02 contrato x punida | 6 | 4 | 2 | 0 | 0 | 67% | 30-90% |
| R03 empresa nova | 4 | 3 | 0 | 1 | 0 | 75% | 30-95% |
| R04 capital x contrato | 4 | 0 | 4 | 0 | 0 | 0% | 0-49% |
| R05 doador virou fornecedor | 6 | 1 | 3 | 1 | 1 | 17% | 3-56% |
| R06 fracionamento | 4 | 1 | 3 | 0 | 0 | 25% | 5-70% |
| R07 concentração | 4 | 1 | 3 | 0 | 0 | 25% | 5-70% |
| R08 sócio em paraíso fiscal | 4 | 0 | 4 | 0 | 0 | 0% | 0-49% |
| R09 emenda | 7 | 3 | 2 | 1 | 1 | 43% | 16-75% |
| R10 político sócio | 6 | 1 | 4 | 1 | 0 | 17% | 3-56% |
| R11 pagamento x punida | 7 | 2 | 5 | 0 | 0 | 29% | 8-64% |
| R12 servidor sócio | 4 | 1 | 3 | 0 | 0 | 25% | 5-70% |

Nota: dentro de R02 e R11, a leitura mais robusta é por subtipo: **nos casos R02/R11 em que há contrato ou pagamento posterior ao registro da sanção no CEIS, 6 de 6 foram relevantes; quando o único "contrato novo" está entre o início e o registro da sanção, 0 de 6 foram relevantes** (13 casos conferidos; Master Facilities, sem contrato novo, é o 13º, benigno). Interpretação: INFERÊNCIA.

### Por camada de prioridade

| Camada (reconstruída) | n | Relev. | Benigno | Falso+ | NV | Precisão | IC 95% |
|---|---|---|---|---|---|---|---|
| Prioridade máxima | 14 | 7 | 6 | 1 | 0 | 50% | 27-73% |
| Relevante | 7 | 3 | 1 | 2 | 1 | 43% | 16-75% |
| Contexto | 39 | 9 | 26 | 3 | 1 | 23% | 13-38% |
| (gravidade da regra) alta | 33 | 14 | 14 | 3 | 2 | 42% | 27-59% |
| (gravidade da regra) média | 22 | 5 | 16 | 1 | 0 | 23% | 10-43% |
| (gravidade da regra) baixa | 5 | 0 | 3 | 2 | 0 | 0% | 0-43% |

Leitura: há gradiente (máxima 50% > contexto 23%), mas a camada "relevante" não se separa do ruído, e a "máxima" só chega à metade. A amostra sorteia só 14 máximas; a diferença máxima x relevante não é estatisticamente distinguível.

### "Alta" que merece ser "alta"
Critério: relevante, magnitude coerente com o alerta e conclusão que um jornalista publicaria como ponto de partida. Das 7 "máxima" relevantes, 5 alertas passam sem ressalvas (Solarterra em R09 e R11, Vertical, Lafaeng, Julio Cezar); 2 têm ressalva de magnitude (Sanigran: só 3% do total na janela; Agil: total inflado). Logo: **de 5 a 7 de 14 (36% a 50%) merecem "máxima"**.

## 4. Principais causas de falso positivo e de benigno

Ordenadas pela contribuição nos 41 alertas não relevantes (VERIFICADO nos casos citados).

1. **Sanção ainda não publicada quando o contrato foi assinado (defasagem de registro).** R11 e R02 usam `DATA INÍCIO SANÇÃO`; o órgão comprador só vê a sanção quando ela entra no CEIS (`DATA ORIGEM INFORMAÇÃO`). Defasagens medidas: META 7,8 meses; BTZ Pay 3,5 meses; RKV 2 meses; Elloella 3 meses; DSM 1 dia (contrato 14/10, registro 15/10). As 6 "máximas" R11/R02 benignas da amostra vêm daqui (BTZ, Dubai, META, DSM, RKV, Elloella). A regra R02 diz "constava no CEIS na data da assinatura"; o SQL não verifica isso.
2. **Pagamento de contrato antigo tratado como sinal.** O próprio R11 admite "pagamento de entrega anterior". Os valores altos (R$375k a R$889k) são quase todos de contratos anteriores; o "contrato novo" é pequeno (R$8,7k, R$11k).
3. **Alcance da sanção ignorado.** R01 deixa passar "No órgão sancionador" e "Sem Informação" (`ILIKE`: `s.abr NOT ILIKE 'Em todos os Poderes%' AND NOT ILIKE 'Na Esfera e no Poder%'`), contrariando o critério escrito em `docs/REGRAS.md`. R09 conta qualquer sanção, inclusive "Suspensão, no órgão sancionador" (FCK, Trindade, Solarterra tem uma dessas além da forte).
4. **Valor global plurianual comparado ao capital (R04) e concentração por contrato único (R07).** 0/4 em R04: todos de 24 a 60 meses, empresas com 7 a 30 anos. R07: 3/4 eram 1 pregão/concorrência dominando um órgão pequeno.
5. **Holdings e multinacionais (R08).** 4/4 benignos: Suíça, Luxemburgo e Malta aparecem como "paraíso" para grupos globais ativos há décadas.
6. **Duplicação de linhas (bug de junção).** Mesma linha 2 a 4 vezes. Impacto no valor mostrado:
   - R02: 43 de 150 alertas (29%) com linhas repetidas; pelo menos R$12,7M de R$71,3M (18%) são repetição.
   - R05: 17 de 150 (11%); R$148,8M de R$256,8M (58%) são repetição. Quixadá aparece como R$34,9M; o contrato é de R$17,46M.
   - R08: 21 de 117 (18%); R$118M de R$697M (17%).
   (Cálculo sobre as linhas exibidas nas tabelas; é piso, não teto.) Causa provável (INFERÊNCIA): junção 1 contrato x N sanções (R02) ou 1 contrato x N sócios doadores/estrangeiros (R05, R08) sem `DISTINCT` antes da soma.
7. **"Empresa nova" pelo estabelecimento (R03).** `alertas/03_...sql` usa `estab.abertura` do CNPJ do contrato; filial de empresa antiga parece "nova" (PADTEC S/A, matriz de 1999, filial de 08/01/2026).
8. **"Nova" por 1 pagamento antigo (R09).** `emendas.py`: `a.abertura > a.ini - interval 365 day and a.total >= 200000`, onde `ini = min(data)` de todos os pagamentos. Um pagamento de R$15,8k em 12/2016 ativa a flag para uma empresa que recebeu R$60M em 2024-26 (Ferreira Santos).
9. **R10 sem fim de mandato.** `POSSE = {2018: "2019-02-01", ...}` e `apos = data >= posse`: contratos de 2025 contam como "após a posse" de um mandato 2019-2022 (Rogério Leão, vira sócio em 2023). Também sobe como "político eleito" quem só foi eleito em 2026 e ainda não tomou posse (3 dos 6 R10 da amostra); isso aparece no texto da regra como "alta se depois da posse", mas a lista fica poluída.
10. **R05 contratante errado e sem histórico.** Quixadá: contratante é a Câmara, não a prefeitura. O critério `data_assinatura >= 2025-01-01` não verifica se a empresa já era fornecedora (Tracomaq, Giorgette: sim). Doação de R$100 e de R$3.000 têm o mesmo peso que R$40.000.
11. **Fracionamento (R06) sem checar objeto.** Cada contrato é um idoso, uma escola ou um show diferente.
12. **Datas da sanção descartadas na exibição de R09.** `a["sancao"] = {..., "inicio": None, "fim": None}` esconde o período; o leitor não consegue comparar com os pagamentos, e o valor "total" soma pagamentos fora da janela (Sanigran: só 3% na janela).

## 5. Bugs sistemáticos (resumo com trecho)

| # | Onde | Trecho | Efeito |
|---|---|---|---|
| B1 | `alertas/02_*.sql`, `ingestao/despesas_federais.py` | `WHERE p.data_assinatura >= s.ini` / `p.mes >= date_trunc('month', s.ini)` (sem `s.data_origem <= data`) | Contrato/pagamento anterior à publicação da sanção vira alerta |
| B2 | `despesas_federais.py` | `contratos.sinal = contrato_novo` conta qualquer contrato assinado desde `ini` | "Novo" antes do registro; "máxima" sem base |
| B3 | `alertas/01_*.sql` | `OR s.abr NOT ILIKE 'Em todos os Poderes%' AND ... NOT ILIKE 'Na Esfera e no Poder%'` | R01 aceita sanção restrita ao órgão |
| B4 | `emendas.py` | `sc` inclui qualquer sanção; `"inicio": None` | R09 sem filtro de alcance, sem datas |
| B5 | `emendas.py` | `a.abertura > a.ini - interval 365 day` (`ini = min(data)`) | "Empresa nova" falsa |
| B6 | `alertas/03_*.sql` | `JOIN estab e ON e.cnpj = p.doc14 ... e.abertura` | Filial = empresa nova |
| B7 | `alertas/04_*.sql` | `p.valor_global >= 50 * em.capital_social` | Ignora prazo do contrato |
| B8 | `alertas/02,05,08` / exportador | junção 1:N sem `DISTINCT` por `p.id` antes de `sum()` | Valor e `n` inflados |
| B9 | `politicos_socios.py` | `POSSE[ano_min]` sem data de término | "Após a posse" para ex-mandatário |
| B10 | `alertas/05_*.sql` | `p.esfera = 'M'` sem excluir Câmara Municipal (`poder = 'L'`) | Contratante errado |

## 6. Recomendações por regra

Todas se aplicam em SQL ou Python, sem mudar a tese.

- **R01.** Exigir `abr ILIKE 'Todas as Esferas%'` ou (`abr ILIKE 'Em todos os Poderes%'` e `esf = FEDERAL`). Mover "No órgão sancionador" e "Sem Informação" para contexto. Mostrar a data de registro (`DATA ORIGEM INFORMAÇÃO`). Novo campo: "o que a sanção proíbe".
- **R02.** Gravidade só "alta" se `data_assinatura >= data_origem_informacao + 3 dias` e o contrato não é empenho de ata anterior à sanção; entre o início e o registro, rebaixar para "contexto" com texto "a sanção ainda não estava no CEIS". `SELECT DISTINCT` por contrato antes de somar. Mostrar nº de sanções ativas (AGIL: 71).
- **R03.** Usar a menor abertura do `cnpj_basico` (matriz). Excluir filiais de empresas com matriz > 180 dias. Manter os demais como "relevante", não "alta".
- **R04.** Dividir o valor global pela vigência em anos (`valor_global / greatest(1, meses/12)`) antes de comparar ao capital; exigir empresa com menos de 3 anos ou capital < R$100k; senão, contexto.
- **R05.** Excluir `poder = 'L'`; exigir doação ≥ R$ 5.000 ou ≥ 0,5% do contrato; marcar "já era fornecedora" com base em contratos anteriores ao 1º turno (PNCP desde 2021) e rebaixar; mostrar a modalidade (pregão x dispensa) como campo; elevar só direta/inexigibilidade com doação alta (ISLM).
- **R06.** Só alertar se o objeto (`objeto` normalizado) coincide em ≥ 70% de similaridade e o valor soma ≥ 1,2x o limite da dispensa; excluir Art. 75 VIII e objetos "idoso/aluno/escola/evento" por unidade; mostrar o mesmo objeto lado a lado.
- **R07.** Exigir ≥ 3 contratos distintos do fornecedor no órgão e modalidade direta ou aditivos; contrato único em pregão ou concorrência vai para contexto.
- **R08.** Remover como alerta. Virar rótulo no perfil da empresa ("cadeia societária inclui jurisdição X"). Se mantido, só nível 1 com contrato direto, sem multinacional com capital > R$100M.
- **R09.** (a) alcance: só "Todas as Esferas" ou "Em todos os Poderes" federal; (b) mostrar `inicio/fim` e `valor_na_janela`; (c) "nova" só se a empresa tem < 1 ano no **primeiro pagamento relevante** (≥ R$ 50 mil), não no menor valor; (d) CEPIM: exigir pagamento posterior à data do impedimento, ou texto "histórico".
- **R10.** Criar `fim_mandato`; "alta" só se contrato dentro do mandato; "eleito em 2026" vira "futuro conflito, mandato começa em 01/02/2027". Para presidente de associação (qualificação 16) usar texto próprio. Nomes com CPF parcial: manter, mas exibir "conferido por nome e 6 dígitos".
- **R11.** Dividir em dois alertas: (A) contrato novo assinado ≥ 3 dias após `data_origem_informacao` (candidato a "alta"); (B) pagamentos de contrato antigo (sempre "contexto", com texto "a sanção veda novos contratos"). Pagar no mês do início só conta se `mes > mes_inicio`.
- **R12.** Separar "administrador" (vedado, Lei 8.112 art.117 X) de "cotista" (permitido). Cotista vira contexto.
- **Transversal.** Campo novo `explicacao_benigna_provavel` (p. ex. "contrato de 36 meses", "holding de multinacional", "sanção publicada depois do contrato") para cada regra; "máxima" exige pelo menos uma checagem sem explicação benigna provável.

**O que deve virar "contexto" (não alerta):** R08 inteira, R04 e R07 com a explicação plurianual/contrato único, R06 por unidade, R10 pré-mandato, R11 só com contrato antigo, R12 cotista, R09 com sanção restrita.

**O que deve ser removido da lista pública:** casos em que o fato central é falso (R01 com sanção restrita, R03 filial, R05 com Câmara, R09 "nova" por pagamento de 2016, R10 pós-mandato). Em números, são 6 de 60 (10%).

## 7. Protocolo contínuo de validação

1. **Amostra mensal:** 60 alertas (5 por regra, mais 12 da camada máxima e 12 aleatórios), semente publicada (`AAAAMMDD`), sorteio por script versionado.
2. **Rotulagem dupla:** duas pessoas rotulam em planilha; terceira desempata. Cohen kappa ≥ 0,6 como meta. Rótulos fixos: RELEVANTE / BENIGNO / FALSO-POSITIVO / NÃO-VERIFICÁVEL + `causa` (lista da seção 4) + URL de evidência.
3. **Checklist mínimo por alerta:** (a) datas de início e de registro da sanção x datas do contrato/pagamento; (b) alcance; (c) contrato anterior à sanção; (d) valor no PNCP; (e) identidade; (f) situação cadastral; (g) decisão judicial (consulta ao processo quando houver número).
4. **Metas iniciais:** FP < 5% (hoje 10%); precisão da "máxima" ≥ 70% (hoje 50%); nenhum alerta com valor duplicado (hoje 18% de R02/R05/R08).
5. **Painel de qualidade público** (`/qualidade`): precisão por regra e camada com IC, lista de causas de FP, data da última amostra, nº de alertas retirados por erro, tempo médio de correção. Texto: "estimativa por amostra; não é prova de culpa".
6. **Regressão:** cada correção entra com um teste que reproduz o caso rotulado (p. ex. PADTEC como "não alerta" para R03). Rodar a amostra de 60 antes/depois de mudar limiar.
7. **Tamanho de amostra:** 60 dá IC de ±12 pontos na precisão total; 120 (a cada 2 meses) dá ±9; para medir uma regra com ±15 pontos são necessários ~40 alertas dela.
8. **Linha de retirada:** FP confirmado = alerta sai do ar em 24 h, com nota de correção pública.

## 8. Fichas-exemplo

### As 3 melhores

**1. Solarterra Ltda (R09 + R11 + R02).** A empresa foi declarada inidônea pelo TCU para contratar com qualquer órgão do país entre 09/07/2025 e 23/09/2027 (registro no CEIS em 25/11/2024; processo 008.102/2024-4). Mesmo assim, o governo federal continuou a pagá-la: o Exército pagou R$927 mil em junho de 2026, o Ministério da Saúde assinou três contratos novos (R$173 mil) em agosto e novembro de 2025, e R$412 mil de emendas parlamentares chegaram a ela no mesmo período. Conferido no CEIS, na planilha de despesas, no PNCP e no arquivo de emendas. O que não prova: que houve má-fé do órgão que pagou (a ata de registro de preços pode ter sido assinada antes), nem que a empresa fraudou nada de novo. O que merece apuração: por que o órgão não bloqueou o pagamento.

**2. AF Empreendimentos Ltda (R02).** Declarada inidônea pela Prefeitura de Enéas Marques (PR) em 11/12/2025, com efeito em todo o país, e registrada no CEIS no dia seguinte. Em 2026 assinou 9 contratos (R$3,08 milhões): Comando da Aeronáutica (R$1,5 milhão e R$452 mil, viaturas), Roraima, prefeituras e um conselho. Todos depois do registro. O que não prova: que os órgãos souberam da sanção (muitos compram por ata de registro anterior). Vale perguntar a cada comprador se consultou o CEIS.

**3. Lafaeng Soluções Corporativas (R09).** Inidônea pelo Ministério Público da União de 06/06/2025 a 05/06/2027, em todo o país. No mesmo período recebeu R$877 mil de emendas parlamentares (autores: Reginaldo Lopes, Duda Salabert e outros), em Conselheiro Lafaiete (MG). Conferido no CEIS e no arquivo de emendas. O que não prova: que o dinheiro foi desviado; pode ser pagamento de obra contratada antes da sanção.

### As 3 piores (como o Radar erra)

**1. Construtora Ferreira Santos (R09, "prioridade máxima").** O alerta diz que a empresa é "nova" e recebeu R$60 milhões em emendas. Mas a empresa foi aberta em 2016, tem 8 anos de atividade, não tem sanção nem CEPIM. O "nova" nasceu de um pagamento de R$15,8 mil em dezembro de 2016. Os R$60 milhões são pagamentos de obras de 2024 a 2026. Uma pessoa lendo ficaria alarmada; a base não sustenta.

**2. PADTEC S/A (R03).** Aparece como "empresa de 130 dias" com contrato de R$4,9 milhões no Ministério das Comunicações. Mas a PADTEC é uma fabricante de equipamentos com capital de R$162 milhões; o que abriu em janeiro de 2026 foi uma filial. O sistema leu a data de abertura da filial como se fosse da empresa.

**3. Rogério Araújo Leão e a Sedenge (R10, "alta").** O alerta diz que um deputado estadual é sócio de uma construtora que recebeu R$10,8 milhões do governo de Pernambuco. Mas ele foi eleito só em 2018, o mandato terminou em janeiro de 2023, e só entrou na empresa em 28/02/2023. O sistema trata "depois da posse de 2019" como "durante o mandato". Resultado: acusa um ex-deputado de algo que a lei não veda a ex-deputado. Mesma família de erro: três dos seis R10 da amostra são pessoas que só foram eleitas em 2026 e ainda não têm mandato.

## 9. Limites desta auditoria
- n = 60; IC de 12 pontos no agregado e de 30 a 60 pontos por regra.
- A amostra tem poucas "máximas" de R01 a R08 porque a base só tem máxima em R02, R09 e R11 (e R10/R01 abaixo). Não mede RF01.
- O "benigno" foi decidido com o dado aberto; um contrato rotulado benigno pode esconder irregularidade que só a licitação por dentro revelaria. Benigno aqui significa "o sinal sozinho não indica problema".
- Verificação de decisão judicial, licitantes e notícias ficou de fora.
- 2 alertas ficaram como NÃO-VERIFICÁVEL (BH/Bali, Fundação Hospitalar de São Gabriel); a sugestão é consultar a licitação de BH e o convênio SIAFI/SICONV da Fundação.

## 10. Tabela completa (60 alertas)

Camada = reconstruída por `pontuar` (maxima/relevante/contexto). Gravidade = a da regra. Siglas: ver seção 2.

| id (truncado) | Regra | Camada | Grav. | Resultado | Evidência |
|---|---|---|---|---|---|
| R01-00000022171983 | R01 | contexto | media | VERDADEIRO-RELEVANTE | CPF completo igual no CEIS (2 sanções, TJSC/MPSC, Lei 8.429 art.12, até 2028) e na Câmara (30 aluguéis de escritório de R$2.270, abr/2024 a out/2026). Ressalva: MPSC registra "abrangência estadual e municipal"; alcance federal é INFERÊNCIA. [CEIS-CSV][CAMARA] |
| R01-00870827000318 | R01 | contexto | alta | VERDADEIRO-RELEVANTE | CEIS: impedimento sem prazo, STF (PET 15.438), início 01/08/2026, registrado 14/08, todas as esferas; 2 pagamentos de combustível (R$750) em 17/08 e 06/09, após o registro. Valor ínfimo. [CEIS-CSV][CEIS-API] |
| R01-21183741000125 | R01 | contexto | baixa | FALSO-POSITIVO | Sanção da Câmara Municipal de Uberlândia, alcance "No órgão sancionador" (Lei 8.429). Não alcança a Câmara dos Deputados; contraria o critério da própria regra R01. [CEIS-CSV] |
| R01-35596258000187 | R01 | contexto | baixa | FALSO-POSITIVO | Suspensão do Estado do Amapá, "No órgão sancionador" (registrada só em 05/07/2024; pagamento em 11/2023). Não alcança o Congresso. [CEIS-CSV] |
| R02-19205451000193 | R02 | maxima | alta | VERDADEIRO-RELEVANTE | Impedimento (Min. Fazenda, federal, todos os Poderes) 29/07/2025 a 2028, registrado 23/09/2025. 4 contratos federais jun-set/2026 (ICMBio, Aeronáutica x2, INCRA R$5,76M/5 anos), todos "termo inicial" no PNCP. [CEIS-CSV][PNCP] |
| R02-20772709000112 | R02 | relevante | alta | VERDADEIRO-RELEVANTE | Inidoneidade (Pref. BH, todas as esferas) 20/01/2026, registrada 23/01. 5 empenhos da UFMG (R$1,1k a 66k, total R$102k) de 29/01 a 03/07. Fato certo, valor baixo. [CEIS-CSV][PNCP] |
| R02-26427482000154 | R02 | maxima | alta | VERDADEIRO-RELEVANTE | Empresa com 71 sanções no CEIS. Contratos de 22-29/01/2025 caem entre início (22/01) e registro (27/01), mas IFPR 07/03 e INCRA 18/03/2025 (R$366k) são posteriores ao registro. Total inflado: o contrato INCRA aparece 4 vezes (R$4,50M mostrados; ~R$3,40M reais). [CEIS-CSV][PNCP] |
| R02-29127216000102 | R02 | relevante | alta | VERDADEIRO-RELEVANTE | Inidoneidade (Pref. Enéas Marques/PR, todas as esferas) 11/12/2025, registrada 12/12. 9 contratos jan-mai/2026 (Aeronáutica R$1,5M e R$452k, Roraima, municípios), todos após o registro. [CEIS-CSV][PNCP] |
| R02-55596207000162 | R02 | maxima | alta | VERDADEIRO-BENIGNO | Inidoneidade (S. Jerônimo da Serra/PR) vigente desde 17/10/2025, mas só publicada no CEIS em 29/01/2026; os 9 contratos de Porto Belo (R$20,9M) são de 15/12/2025. O órgão não podia ver a sanção. Acompanhar pagamentos após 29/01/2026. [CEIS-CSV][PNCP] |
| R02-57902002000193 | R02 | maxima | alta | VERDADEIRO-BENIGNO | Inidoneidade vigente desde 30/06/2026, registrada 30/07; contrato de Cuiabá (R$5,3M) em 13/07. O outro impedimento (Pref. de Capitão, municipal) não alcança Cuiabá. Empresa aberta em 10/2024, ME. Sinal secundário. [CEIS-CSV][PNCP][RFB] |
| R03-03549807000923-37753638000103- | R03 | contexto | media | FALSO-POSITIVO | A filial 0009-23 abriu em 08/01/2026, mas a PADTEC S/A é matriz antiga (capital R$162M). A regra usa a abertura do estabelecimento, não da empresa. [RFB][PNCP] |
| R03-58060000000167-62823257000109- | R03 | contexto | alta | VERDADEIRO-RELEVANTE | Empresa aberta 11/11/2024, contrato de R$1,27M (limpeza escolar, Centro Paula Souza) em 27/12/2024 (46 dias). Fato certo; justificativa possível (spin-off) não verificada. Sinal fraco. [RFB][PNCP] |
| R03-58222933000103-34593541000192- | R03 | contexto | media | VERDADEIRO-RELEVANTE | Aberta 25/11/2024; contrato R$2,74M com Uruará/PA em 18/03/2025 (113 dias), locação de veículos. Fato certo; sinal fraco. [RFB][PNCP] |
| R03-59920794000154-06191001000147- | R03 | contexto | media | VERDADEIRO-RELEVANTE | Aberta 16/03/2025; contrato R$1,84M com Santa Luzia/MA em 18/08/2025 (155 dias), manutenção. Fato certo; sinal fraco. [RFB][PNCP] |
| R04-01211015000161-15126437000143- | R04 | contexto | alta | VERDADEIRO-BENIGNO | Empresa de 1996; contrato R$30M por 24 meses (EBSERH, obra). Capital baixo não indica incapacidade. [RFB][PNCP] |
| R04-05085461000128-07574449000102- | R04 | contexto | alta | VERDADEIRO-BENIGNO | Empresa de 2002, R$72M por 5 anos (2026-2031) em TI. A razão valor/capital ignora a duração. [RFB][PNCP] |
| R04-21921129000102-42498600000171- | R04 | contexto | alta | VERDADEIRO-BENIGNO | Empresa de 2015; R$16,4M por 31 meses (frota). Valor global plurianual. [RFB][PNCP] |
| R04-33184956000140-15126437000305- | R04 | contexto | alta | VERDADEIRO-BENIGNO | Empresa de 2019; R$13,75M por 36 meses (vigilância, EBSERH): mão de obra, capital baixo é comum. [RFB][PNCP] |
| R05-02060439000135-Chapecó-SC | R05 | contexto | media | VERDADEIRO-BENIGNO | Doação R$3.000 de sócia (Osmary Cezar da Silva, confere no QSA). Fornecedora já em 2025; contrato = ata de registro de preços. Valor mostrado em dobro (R$1,96M reais). [RFB][PNCP] |
| R05-04674632000272-Pirassununga-SP | R05 | contexto | media | VERDADEIRO-BENIGNO | Doação R$100; pregão eletrônico de combustível; o posto fornece à cidade desde 2025 (dezenas de contratos). [PNCP] |
| R05-18726947000140-Belo Horizonte- | R05 | contexto | alta | NÃO-VERIFICÁVEL | Doação R$5.000 do sócio; obra R$2,35M. Faltou modalidade e lista de licitantes; não dá para saber se houve competição. [RFB][PNCP] |
| R05-34757814000197-Goiás-GO | R05 | contexto | media | VERDADEIRO-BENIGNO | Doação R$7.500; contratos por concorrência/pregão eletrônicos nas amostras (R$415k, R$424k). Contratos mostrados em dobro (R$1,15M reais de R$2,29M). [PNCP] |
| R05-39934538000109-Araucária-PR | R05 | contexto | media | VERDADEIRO-RELEVANTE | Inexigibilidade (art.74 V) de aluguel R$420k à prefeitura; sócio doou R$40.000 ao prefeito. Contratação direta + doação alta. [PNCP][RFB] |
| R05-52178247000104-Quixadá-CE | R05 | relevante | alta | FALSO-POSITIVO | O contratante é a Câmara Municipal, não a prefeitura do prefeito doado; valor dobrado (R$34,9M mostrado, R$17,46M reais). Prédio sob medida de R$17M para o Legislativo merece atenção, mas por outro motivo. [PNCP] |
| R06-31e4d0b5e55aaad4bb659fe075fac4 | R06 | contexto | media | VERDADEIRO-BENIGNO | 10 contratos de R$39.468 em 3 semanas: cada um é o acolhimento de um idoso diferente. [PNCP] |
| R06-33c53dc7c2da618247c5d7a8227e26 | R06 | contexto | media | VERDADEIRO-BENIGNO | 16 compras de merenda para escolas distintas do Estado do CE (uma cotação por escola). Não é o mesmo objeto fracionado. [PNCP] |
| R06-3de833b877ae6566ffed8e80f60055 | R06 | contexto | media | VERDADEIRO-RELEVANTE | 8 inexigibilidades no mesmo dia (R$40,8k a 67,2k) à mesma banca para assessoria em contratações; inexigibilidade para consultoria é prática questionada. [PNCP] |
| R06-622f8f67cbde2767fdfba8cbe5c7d1 | R06 | contexto | media | VERDADEIRO-BENIGNO | 6 shows de R$65.000, cada um de data/evento distinto (inexigibilidade art.74 II, artista). [PNCP] |
| R07-82570cb70f8c1ceedb9d6f98817f91 | R07 | contexto | alta | VERDADEIRO-RELEVANTE | Inexigibilidade de R$23,98M por 5 anos (2025-2030) no Fundo de Urbanização de Curitiba, 78% do total do fundo. Direta e grande. [PNCP] |
| R07-9bdbbf4b28f3931b82883ff9879c9d | R07 | contexto | alta | VERDADEIRO-BENIGNO | Pregão eletrônico de gestão de mão de obra; 1 contrato domina o fundo por construção. [PNCP] |
| R07-b923071ad039670faff1e1fb008638 | R07 | contexto | alta | VERDADEIRO-BENIGNO | Pregão presencial anual de medicamentos (Mesquita/RJ); a concentração decorre de 1 contrato. [PNCP] |
| R07-e233ceb84939bae610d32cea51dd40 | R07 | contexto | alta | VERDADEIRO-BENIGNO | Concorrência de pavimentação R$12M em município de poucos habitantes; obra única. [PNCP] |
| R08-26a2b6887db9b2d18788668b808ccf | R08 | contexto | baixa | VERDADEIRO-BENIGNO | Sócia é holding suíça de grupo de eventos/viagens; empresa ativa desde 2009. [RFB] |
| R08-472fad7a80c1614efc1ea5409c4841 | R08 | contexto | baixa | VERDADEIRO-BENIGNO | Endress+Hauser: multinacional suíça, no Brasil desde 1982, capital R$169M. [RFB] |
| R08-adab55d140de87c3bcfdae5826978c | R08 | contexto | media | VERDADEIRO-BENIGNO | Filial de empresa de vales (capital R$838M) cuja sócia é holding de Malta do grupo Corpay. [RFB] |
| R08-eaa1179982eaa884138ac19b23a3d9 | R08 | contexto | media | VERDADEIRO-BENIGNO | Iron Mountain: multinacional listada; sócia em Luxemburgo; no Brasil desde 2000. [RFB] |
| R09-06943661000137 | R09 | maxima | alta | VERDADEIRO-RELEVANTE | TCU, inidoneidade todas as esferas 09/07/2025 a 23/09/2027, mais suspensão do Exército. R$412k de emendas na janela, contratos novos de saúde (R$173k) e R$927k do Exército. [CEIS-CSV][EMD][DESP] |
| R09-15153524000190 | R09 | maxima | alta | VERDADEIRO-RELEVANTE | Inidoneidade MPU (todas as esferas) 17/07/2025 a 2029 e 7 outras sanções. Mas só R$36,8k dos R$1,12M de emendas caem na janela. Magnitude baixa; "máxima" exagerada. [CEIS-CSV][EMD] |
| R09-24439931000159 | R09 | maxima | alta | FALSO-POSITIVO | Sem sanção nem CEPIM. A flag "nova" nasce de 1 pagamento de R$15,8k em 12/2016, 9 meses após a abertura (03/2016); os R$60M são de 2024-26 (empresa com 8 anos). [RFB][EMD] |
| R09-26624142000113 | R09 | contexto | media | VERDADEIRO-BENIGNO | Suspensão restrita à Fundação de Apoio de Sergipe (órgão sancionador); não afeta transferências federais. [CEIS-CSV][EMD] |
| R09-27503754000110 | R09 | relevante | alta | NÃO-VERIFICÁVEL | CEPIM por TCE e irregularidade em 3 convênios do Min. Saúde; emendas de 2016-17. Não se verificou se são os mesmos recursos; o CEPIM não tem data. Empresa inapta. [CEPIM][RFB] |
| R09-28786102000101 | R09 | maxima | alta | VERDADEIRO-RELEVANTE | Inidoneidade MPU (todas as esferas) 06/06/2025 a 05/06/2027; R$877k de emendas na janela. [CEIS-CSV][EMD] |
| R09-32972888000110 | R09 | contexto | media | VERDADEIRO-BENIGNO | Suspensão do Comando da Marinha restrita ao órgão; R$128k na janela. [CEIS-CSV][EMD] |
| R10-00627992-VILMARPERIN | R10 | relevante | alta | VERDADEIRO-BENIGNO | Vilmar Zanchin (dep. estadual RS) é presidente (não sócio) da associação UNALE desde 18/12/2025; o 1º contrato (03/12) é anterior. Associação de legisladores. [RFB][TSE] |
| R10-05187920-LEANDROSORG | R10 | contexto | media | VERDADEIRO-BENIGNO | Sorgato é sócio da UCEFF desde 2006; em 2022 foi suplente; eleito só em 2026. Contrato de 06/2025, sem mandato. [RFB][TSE] |
| R10-10718713-THIAGOGILLE | R10 | contexto | media | VERDADEIRO-BENIGNO | Eleito só em 2026; contratos 2025 a 01/2026 antes do mandato. Sem prova de cargo anterior. [RFB][TSE] |
| R10-18986213-EROSFERREIR | R10 | relevante | alta | VERDADEIRO-RELEVANTE | Eros Biondini, deputado federal 2019-2026, sócio-administrador da Louvarte desde 2013 (QSA); contratos de 2025 (R$130k) com Marabá e Estado do RJ. Constituição art.54 veda a parlamentar manter contrato com poder público. [RFB][PNCP][TSE] |
| R10-23762552-VITTORIOMED | R10 | contexto | media | VERDADEIRO-BENIGNO | Medioli, sócio-administrador da Deva desde 1997; eleito só em 2026; contratos de 2025-26 (R$143M) antes do mandato. Merece contexto, não alerta de conflito. [RFB][TSE] |
| R10-70082227-ROGERIOARAU | R10 | relevante | alta | FALSO-POSITIVO | Rogério Leão só foi eleito em 2018 (mandato 2019-2022) e virou sócio em 28/02/2023. "Alta, após a posse" ignora o fim do mandato. [RFB][TSE] |
| R11-05564043000113 | R11 | contexto | baixa | VERDADEIRO-BENIGNO | Impedimento Justiça Federal 18/08/2026 (reg. 20/08). Só contratos anteriores (24); pagamentos de entregas antigas. Gravidade já baixa. [CEIS-CSV][DESP] |
| R11-06943661000137 | R11 | maxima | alta | VERDADEIRO-RELEVANTE | Inidoneidade TCU (todas as esferas) 09/07/2025 a 2027, registrada 25/11/2024. 3 contratos novos do Min. Saúde (R$173k, até 19/11/2025) e pagamentos do Exército (R$927k, 06/2026). Confere com a planilha de despesas. [CEIS-CSV][DESP][PNCP] |
| R11-27518373000105 | R11 | maxima | alta | VERDADEIRO-BENIGNO | Sanção UFRO início 03/09/2025, registrada só 28/04/2026. Os 3 "contratos novos" (R$8,7k, 10/2025) são anteriores ao registro; o resto são pagamentos de contratos antigos. [CEIS-CSV][PNCP][DESP] |
| R11-28244608000180 | R11 | maxima | alta | VERDADEIRO-BENIGNO | Impedimento AGU início 07/10/2026, registrado 15/10. O contrato novo (R$928k, Exército) é de 14/10, um dia antes do registro; pagamentos de outubro são de contratos prévios. Acompanhar. [CEIS-CSV][PNCP][DESP] |
| R11-34652187000120 | R11 | maxima | alta | VERDADEIRO-BENIGNO | Sanção Exército início 23/06/2026, registrada 26/08. Contratos novos (23/06, 13/07) anteriores ao registro, dispensas pequenas. [CEIS-CSV][PNCP] |
| R11-53571459000101 | R11 | maxima | alta | VERDADEIRO-BENIGNO | Sanção Exército início 16/06/2026, registrada 15/09. Os 5 "novos" (R$11k) são empenhos de pregões antigos, anteriores ao registro. [CEIS-CSV][PNCP] |
| R11-64891053000122 | R11 | maxima | alta | VERDADEIRO-RELEVANTE | Empresário individual aberto em 02/2026, capital R$15k, com 4 impedimentos do Exército em 5 semanas e R$889k recebidos em 3 meses; dispensa de R$31k (29/09) após o registro. [CEIS-CSV][DESP][RFB][PNCP] |
| R12-01239170 | R12 | contexto | media | VERDADEIRO-BENIGNO | 2 médicos de universidade federal como cotistas de clínica (desde 1999 e 2009); dupla atividade médica é usual. Identidade por nome+CPF parcial. [RFB][SIAPE] |
| R12-02503493 | R12 | contexto | alta | VERDADEIRO-RELEVANTE | Perito Médico Federal administrador desde 1998 (QSA, mesma data do vínculo); clínica contratou o Exército (R$900k). Lei 8.112 art.117 X veda gerência privada. Identidade por nome parcial: INFERÊNCIA. [RFB][SIAPE] |
| R12-05914165 | R12 | contexto | media | VERDADEIRO-BENIGNO | Analista ambiental é cotista minoritário de indústria de gases (desde 2013); contratos com EBSERH/Fiocruz. [RFB] |
| R12-21255490 | R12 | contexto | media | VERDADEIRO-BENIGNO | 2 professores universitários cotistas de clínica cardiológica (2014). [RFB] |
