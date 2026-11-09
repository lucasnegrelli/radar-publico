# 04. Mapa verificado das fontes de dados abertos para cobrir todos os poderes e esferas

Data: 08/11/2026. Autoria: engenharia de dados (pesquisa para o Radar Público). Não alterei código do produto.

## 0. Como ler e como foi testado

- Marcações: **VERIFICADO** (eu testei hoje, 08/11/2026), **FONTE** (afirmado por fonte citada), **INFERÊNCIA** (raciocínio meu), **NÃO VERIFICADO** (rede/DNS falhou ou não testei; o que escrevo vem de conhecimento prévio e precisa de confirmação).
- Método de teste: `curl -s -L -m 20 -A "RadarPublico/1.0 (projeto civico; github.com/lucasnegrelli/radar-publico)" <URL>`, com GET curto (poucos KB) ou HEAD. Nenhum arquivo acima de 50 MB foi baixado; nenhuma conta, login ou chave foi usada. Os resultados brutos de ~110 URLs estão só no meu rascunho (fora do repositório).
- "000" significa que a conexão falhou (DNS ou timeout) **a partir da minha rede, hoje**; não prova que a fonte está fora do ar.
- Esforço de integração: P (até 2 dias), M (até 2 semanas), G (mais de 2 semanas). Valor para o Radar: 1 a 5.
- Aviso de método: "12 trilhões" não é gasto público. **R$ 12,7 tri é o PIB de 2025** (IBGE, via [Poder360](https://www.poder360.com.br/poder-economia/pib-do-brasil-cresce-23-em-2025/), acesso 08/11/2026). O dinheiro que o Estado brasileiro efetivamente movimenta é bem menor (seção 3). Recomendo que o produto fale em "dinheiro público rastreável" e mostre a cobertura em % de um denominador honesto.

## 1. Resumo executivo (os 8 achados que mudam decisões)

1. **A cobertura de maior retorno por esforço já tem API aberta e funcionando**: Siconfi (apidatalake.tesouro.gov.br), TransfereGov (API PostgREST) e a API Compras.gov.br. Todas responderam 200 sem chave (VERIFICADO).
2. **O maior "buraco" fora do PNCP é o município**. Os TCEs que publicam dado em lote/API (SP, PE, RS, MG, PR, SC, CE, PB, RN) cobrem a maior parte dos municípios grandes. O TCE-SP responde `despesas/{município}/{ano}/{mês}` com empenho, fornecedor com CNPJ e valor (VERIFICADO).
3. **Quadro de assessores do Senado**: existe API pública `adm.senado.gov.br/adm-dadosabertos/api/v1/servidores/servidores` que responde JSON com nome, vínculo, cargo, lotação e categoria (VERIFICADO). Isso fecha parte da lacuna do ROADMAP ("quadro de assessores").
4. **UN Comtrade (prévia), GLEIF e Wikidata respondem sem chave** (VERIFICADO), mas Comex Stat API, OpenCorporates e DataJud exigem chave/token (401 sem ela).
5. **A ONU deixou de dar 404**: a URL consolidada `scsanctions.un.org/resources/xml/en/consolidated.xml` hoje redireciona para um arquivo no blob da ONU e entrega XML (VERIFICADO, HTTP 206). O item do ROADMAP ("ONU: 404, rever") pode ser reaberto. A lista da UE com o token antigo devolveu **500** (VERIFICADO): conferir o `ingestao` antes de confiar.
6. **Risco de dependência**: `ingestao/cnpj.py` e `socios_exterior.py` leem o CNPJ de um **espelho de terceiro** (`dados-abertos-rf-cnpj.casadosdados.com.br`), e não da Receita (VERIFICADO no código). O host oficial `dadosabertos.rfb.gov.br` não conectou da minha rede (000, 21 s) e `arquivos.receitafederal.gov.br/.../dados_abertos_cnpj/` deu 404; as fontes que achei divergem sobre a URL oficial atual (NÃO VERIFICADO). Além disso, a Receita emitiu o primeiro **CNPJ alfanumérico** (FONTE: notícias do Ministério da Fazenda de 07/2026 achadas por busca): o pipeline precisa aceitar letras em CNPJ para empresas novas.
7. **Instabilidade real das fontes**: Querido Diário respondeu 520 após 30 s (e "no available server" na primeira tentativa), `contas.tcu.gov.br` respondeu 503 na raiz, TCM-SP respondeu 429 na primeira requisição, STF e ANP responderam 403 ao curl. Toda coleta precisa de cache, retomada e estado "fonte indisponível" visível ao usuário.
8. **Denominador honesto**: LOA 2026 = R$ 6,54 tri (R$ 1,8 tri só de refinanciamento da dívida); governos estaduais empenharam **R$ 1,416 tri** em 2024 (soma que eu calculei com a API do Siconfi, VERIFICADO). O PNCP registrou ~R$ 1 tri homologado em 2025. O Radar cita ~R$ 1,5 tri no PNCP; isso é cobertura de **contratação**, não de **gasto**.

## 2. Catálogo de fontes por bloco

Colunas comuns: **Formato / Auth / Licença** · **Atualização, volume, cobertura** · **Chaves de ligação** · **Teste 08/11/2026** · **Esf./Valor** · **Habilita**. Onde escrevo só "dado aberto (LAI, Dec. 8.777/2016)" como licença, é INFERÊNCIA: a maioria dos portais públicos não publica licença explícita.

### (a) Tribunais de Contas

| Fonte | Formato / Auth / Licença | Atualização, volume, cobertura | Chaves | Teste | Esf./Valor | Habilita |
|---|---|---|---|---|---|---|
| **TCU: acórdãos (API)** `https://dados-abertos.apps.tcu.gov.br/api/acordao/recupera-acordaos?inicio=0&quantidade=1` | JSON, sem chave | Acórdão 3037/2026 de 04/11/2026 no topo: defasagem de dias (VERIFICADO). Paginação por `inicio`/`quantidade` | número/ano do acórdão; texto livre com CNPJ/CPF no sumário | **OK** (200, JSON) | P / 4 | contas irregulares, inabilitação para cargo, débito e multa; ligar a gestor/empresa por texto |
| TCU: portal de dados abertos `https://sites.tcu.gov.br/dados-abertos/` | HTML com catálogo | — | — | **OK** (206, HTML). `dadosabertos.tcu.gov.br` não resolve (DNS) | P / 3 | catálogo para achar inidôneos, certidões, contas julgadas |
| TCU: contas e inidôneos `https://contas.tcu.gov.br/` | consulta web (Oracle APEX) | — | CNPJ/CPF | **503 na raiz hoje**; NÃO VERIFICADO se há lote | M / 4 | empresa inidônea (extensão natural da R01/R02) |
| **TCE-SP** (Audesp) `https://transparencia.tce.sp.gov.br/api/json/municipios` e `.../despesas/{muni}/{ano}/{mês}` | JSON, sem chave | VERIFICADO: lista de municípios e despesas de Adamantina jun/2024 com `nr_empenho`, `evento` (Empenhado/Liquidado/Pago), `id_fornecedor` ("CNPJ - PESSOA JURÍDICA - 43008291000177"), `nm_fornecedor`, `dt_emissao_despesa`, `vl_despesa` ("17000,00" texto com vírgula) | CNPJ do fornecedor; slug do município (não é código IBGE) | **OK** | M / 5 | R01/R02/R11 em nível municipal; fracionamento; concentração; "prefeitura paga empresa punida" |
| TCE-SP: Audesp (documentação) `https://www.tce.sp.gov.br/audesp` | HTML | página atualizada hoje (Last-Modified 08/11/2026) | — | OK (200) | — | contexto e layout |
| **TCE-PE** `https://sistemas.tce.pe.gov.br/DadosAbertos/` | API REST com página de métodos | VERIFICADO: métodos ReceitasEstaduais/Municipais/Previstas, DespesasEstaduais/Municipais (chave composta) e outros | CNPJ/CPF do credor (campo não conferido), código do município do TCE | **OK** (200). Exemplos em `Exemplo!listar` | M / 5 | despesas municipais e estaduais PE (R11, R01) |
| **TCE-RS** `https://dados.tce.rs.gov.br/` | CKAN (`/api/3/action/package_list`, resposta de ~4 MB) com milhares de conjuntos (ex.: "balancete-de-despesa-...-2013") | VERIFICADO: lista enorme de datasets por entidade e ano; LicitaCon é a base de licitações municipais do RS (FONTE: conhecimento prévio, não reverificado) | CNPJ nos datasets de licitação (NÃO VERIFICADO) | **OK** | M / 5 | licitação "por dentro" (participantes) em RS; empresa punida vencedora |
| **TCE-MG** `https://dadosabertos.tce.mg.gov.br/` | portal HTML (conteúdo carregado por script); SICOM/Fiscap são os sistemas de origem (FONTE: conhecimento prévio) | portal responde 200 hoje | CNPJ (NÃO VERIFICADO) | **OK** (200) página; **conteúdo e formato NÃO VERIFICADOS** | M / 5 | MG tem 853 municípios (INFERÊNCIA: número que conheço, não reverificado) |
| **TCE-PR** (SIM-AM) regras `https://servicos.tce.pr.gov.br/servicos/arquivos/dadosabertos/dados_abertos_tcepr_regras_de_utilizacao.pdf` | dados em XML/CSV; BigQuery de terceiro (FONTE: catálogo dataportals.org) | PDF de regras de 2018 (VERIFICADO 200, 257 KB): uso livre dentro da lei (FONTE: resultado de busca, não li o PDF inteiro) | CNPJ | **PDF OK**; `dadosabertos.tce.pr.gov.br` não resolve (DNS). **Endpoint real NÃO VERIFICADO** | M / 5 | PR: licitações e despesas municipais |
| **TCE-SC** `https://www.tcesc.tc.br/apis-dados-abertos` | APIs (e-Sfinge) | página existe (VERIFICADO 200); `servicos.tcesc.tc.br/endpoints-portal-transparencia/` deu **403** na raiz | CNPJ (NÃO VERIFICADO) | OK página; API **NÃO VERIFICADA** | M / 4 | SC |
| **TCE-CE** `https://api-dados-abertos.tce.ce.gov.br/` | API (SIM) | host existe e responde 200, mas na raiz devolve a página padrão do nginx: caminhos reais NÃO VERIFICADOS | CNPJ | parcial | M / 4 | CE |
| TCE-PB `https://dados-abertos.tce.pb.gov.br/` | portal | responde 200 (VERIFICADO), conteúdo não inspecionado | — | parcial | M / 3 | PB |
| TCE-RN (portal de dados abertos) | portal | aparece em catálogo (FONTE: dataportals.org); `www.tce.rn.gov.br` responde 200 | — | NÃO VERIFICADO | M / 3 | RN |
| TCE-ES (CidadES), TCE-MT, TCE-MS, TCE-GO, TCM-GO, TCM-BA, TCE-BA, TCE-PA, TCM-PA, TCE-AM, TCE-AL, TCE-SE, TCE-MA, TCE-PI, TCE-RO, TCE-TO, TCE-AC, TCE-AP, TCE-RR, TCDF, TCM-SP, TCM-RJ, **TCE-RJ** | sites institucionais | Respondem 200 as páginas iniciais de: GO (`portal.tce.go.gov.br`), BA (TCM), AM (`tceam.tc.br`), AP, MT, PA (`tcepa.tc.br`), RN, SE, AL, RR, DF (`www2.tc.df.gov.br`), TCM-PA, TCM-RJ (`tcmrio.tc.br`), RO (`tcero.tc.br`), TO (`tceto.tc.br`), MA. **Falharam (000)**: `www.tce.ac.gov.br`, `dados.tce.rj.gov.br` (não resolve), `dados.tcees.tc.br`, `dadosabertos.tce.ms.gov.br`, `dadosabertos.tce.pi.gov.br` (domínios que eu chutei; INFERÊNCIA de que o domínio real é outro). **TCM-SP: 429** na primeira requisição | — | **Dado em lote/API NÃO VERIFICADO** para todos. Para o RJ, uma busca só achou menção de "raspagem" de terceiros (FONTE fraca) | G (fazer um por vez) / 3 | cobertura nacional por TCE |

**Leitura**: dos ~34 órgãos (TCU, 26 TCEs, TCDF, 4 TCMs de capitais/ex-capitais e TCM-GO/BA/PA), **só 4 tiveram API ou dado em lote comprovados hoje (TCU acórdãos, TCE-SP, TCE-PE, TCE-RS)**, mais 3 com porta de entrada plausível (MG, PR, SC) e 1 (CE) com host sem rota documentada. O restante precisa de pesquisa de URL e, se não houver lote, de pedido LAI. Pelo princípio "mais dinheiro com menos esforço": **SP, MG, PR, RS, PE, SC, CE e BA (TCM+TCE)** cobrem a maior parte dos municípios por população (INFERÊNCIA; conferir com a população do Siconfi).

### (b) Estados (portais de transparência e dados abertos)

Todos os testes abaixo só provam que a **página inicial responde**; o conteúdo (API ou arquivo) não foi inspecionado, salvo onde indico.

| Estado | URL testada | Resultado | O que existe (FONTE: conhecimento prévio, NÃO VERIFICADO salvo indicação) | Esf./Valor |
|---|---|---|---|---|
| SP | `https://www.transparencia.sp.gov.br/` e `https://dadosabertos.sp.gov.br/` | 200 e 200 | despesas, receitas, folha (por servidor), contratos; compras em sistema próprio | M / 5 (maior orçamento estadual: R$ 363,5 bi empenhados em 2024, VERIFICADO no Siconfi) |
| RJ | `https://www.transparencia.rj.gov.br/` | 200 | despesas, contratos, folha | M / 4 |
| MG | `https://www.transparencia.mg.gov.br/`, CKAN `https://dados.mg.gov.br/api/3/action/package_list` | 206/200 (CKAN responde JSON) | portal com arquivos; CKAN do estado | M / 4 |
| BA | `https://www.transparencia.ba.gov.br/` | 200 | despesas, contratos, convênios | M / 4 |
| PR | `https://www.transparencia.pr.gov.br/` | 200 (sessão com `jsessionid`: cuidado ao coletar) | despesas, folha, contratos | M / 4 |
| RS | CKAN `https://dados.rs.gov.br/api/3/action/package_list` | 200, JSON | CKAN do estado | M / 4 |
| PE | `https://transparencia.pe.gov.br/` e `https://dados.pe.gov.br/` | 200 e 200 | despesas, contratos, folha; `dadosabertos.pe.gov.br` não resolveu | M / 4 |
| CE | `https://cearatransparente.ce.gov.br/` | 200; `dados.ce.gov.br` sem resposta | despesas, contratos, folha | M / 4 |
| PA | `https://www.transparencia.pa.gov.br/` | 000 | — | NÃO VERIFICADO |
| GO | `https://transparencia.go.gov.br/` | 200 (redireciona) | despesas, contratos | M / 3 |
| SC | `https://www.transparencia.sc.gov.br/` | 206 | despesas, contratos, folha | M / 3 |

**Observação importante (INFERÊNCIA)**: cada estado tem SIAFE/SIAD próprio, então os campos mudam por estado. Para o mínimo esforço, **prefira o feed do Tribunal de Contas (padrão único por estado)** e use o portal estadual só para folha e convênios. Contratos estaduais acima do limite de publicação já chegam pelo PNCP (Lei 14.133).

### (c) Municípios

| Fonte | Formato / Auth / Licença | Atualização, volume, cobertura | Chaves | Teste | Esf./Valor | Habilita |
|---|---|---|---|---|---|---|
| **Siconfi API (Tesouro)** `https://apidatalake.tesouro.gov.br/ords/siconfi/tt/entes`, `/dca`, `/rreo`, `/rgf`, `/extrato_entregas`, `/msc_*` | JSON REST (Oracle ORDS), sem chave. Catálogo no [Tesouro Transparente](https://www.tesourotransparente.gov.br/ckan/api/3/action/package_list) (conjuntos `api-dca-entes`, `api-rreo-entes`, `api-rgf-entes`, `api-msc-*`, `capag-municipios`, `cauc`) | VERIFICADO: `entes` ~866 KB numa chamada; `dca` com `an_exercicio=2024&no_anexo=DCA-Anexo I-D&id_ente=35` devolveu "Total Geral da Despesa" empenhada/liquidada de SP; `extrato_entregas` mostra quem entregou e quando. Cobertura: 5.266 municípios (94%) entregaram contas de 2024 (FONTE: publicação do Tesouro achada por busca) | `cod_ibge` (7 dígitos municípios, 2 dígitos UFs) | **OK** | P / 5 | denominador de cada município; "quanto o município gasta vs quanto o Radar enxerga"; despesa por função; CAPAG |
| **TransfereGov (ex-SICONV)** `https://api.transferegov.gestao.gov.br/{transferenciasespeciais,ted,fundoafundo}/` | PostgREST (JSON, sem chave, swagger na raiz) | VERIFICADO: swagger 200 nas três; `transferenciasespeciais/plano_acao_especial?limit=1` devolveu plano com `cnpj_beneficiario_plano_acao`, `nome_beneficiario_plano_acao`, `uf_...`, banco e agência. `.../transferenciasabertas/` deu **404**. Meu chute de tabela `programa_fundo_a_fundo` deu erro `42P01` (nome de relação diferente: consultar o swagger) | CNPJ beneficiário, código do plano | **OK** | P / 5 | R09 (emendas) com execução; convênios com município; transferência Pix especial (alto risco, pouca prestação de contas, INFERÊNCIA) |
| **Portal da Transparência: convênios** (download) | CSV/ZIP mensal | página `download-de-dados/` 200 (VERIFICADO); convênios em arquivos | CNPJ, nº do convênio | OK | P / 4 | convênio com entidade punida (CEIS/CEPIM) |
| **Querido Diário** `https://queridodiario.ok.org.br/api/...` → `https://api.queridodiario.org.br/gazettes` | JSON, sem chave; CC BY (FONTE: projeto OKBR, não reverificado) | **Hoje**: redirecionamento 302 OK, mas `api.queridodiario.org.br` respondeu **520** (timeout 30 s) e "no available server" | `territory_ids` (IBGE) | **instável** | M / 4 | texto de diário municipal (dispensa, ata, contrato, extrato) para alertas e para "buscar o contrato" |
| **PNCP municipal** `https://pncp.gov.br/api/consulta/v1/contratos?...` | JSON, sem chave | VERIFICADO: 10 contratos de 01 a 02/11/2026 vieram em 200 (16,7 KB). Já usado no Radar | CNPJ do órgão e do fornecedor; `numeroControlePNCP` | **OK** | — (já feito) | base atual; ver cobertura abaixo |
| **Compras.gov.br dados abertos** `https://dadosabertos.compras.gov.br/` (OpenAPI em `/v3/api-docs`) | JSON, sem chave (OpenAPI 3.1). Módulos: 07 CONTRATAÇÕES (Lei 14.133), 08 ARP, 04 PGC, 03 preços praticados, 05 UASG, 06 LEGADO, 01/02 CATMAT/CATSER | VERIFICADO: spec responde; uma consulta de 01 a 02/11 devolveu 0 resultados (fim de semana/filtro: inconclusivo) | UASG, CNPJ, `numeroControlePNCP` | **OK (spec)** | P / 4 | licitação federal "por dentro"; **preço de referência por item (CATMAT)**: sobrepreço/preço fora da curva (nova regra) |
| **Tesouro Transparente** `https://www.tesourotransparente.gov.br/ckan/` | CKAN JSON | VERIFICADO: `package_list` 200 | — | OK | P / 3 | catálogo de transferências constitucionais (FPM, FUNDEB), CAUC, CAPAG |
| **FNDE / FUNDEB / PNAE / PNATE** | CSV/painéis | `fnde.gov.br/dadosabertos` redireciona para a organização no dados.gov.br (VERIFICADO) | CNPJ da entidade executora | **conteúdo NÃO VERIFICADO** | M / 4 | merenda e transporte escolar: fornecedor × município |
| **SIOPS (saúde)** | painel/ASP | `siops-asp.datasus.gov.br` não conectou (000) | cod_ibge | NÃO VERIFICADO | M / 3 | cumprimento do piso de saúde |
| **FNS (Fundo Nacional de Saúde) / dadosabertos.saude.gov.br** | CSV/APIs | `dadosabertos.saude.gov.br` 200 (VERIFICADO) | CNPJ do fundo, IBGE | portal OK; conjuntos NÃO inspecionados | M / 4 | repasses SUS a município |
| **SIOP (Planejamento/orçamento federal)** `http://www1.siop.planejamento.gov.br/acessopublico/` | consulta web; extração por "Acesso Público" | 200 (VERIFICADO) | ação, UO, localizador | só consulta; lote **NÃO VERIFICADO** | M / 3 | LOA por programa/ação e UF; executar "orçado vs. pago" |
| **e-SIC / Fala.BR** | pedidos individuais; **não há base aberta de pedidos** (INFERÊNCIA; não achei) | — | — | NÃO VERIFICADO | — | só como canal LAI (seção 5) |
| **Portais municipais comuns**: IPM (Atende.net/IPM), Betha, Elotech, Atende.net | HTML por prefeitura; nenhum padrão nacional de API (INFERÊNCIA) | não testei: milhares de portais, cada um com layout e Termos próprios | CNPJ/empenho | **NÃO VERIFICADO**. Recomendação: não raspar em massa; só os 100 maiores municípios, com pedido de autorização | G / 3 | folha e despesa de municípios fora dos TCEs com lote |
| **dados.gov.br** `https://dados.gov.br/` | CKAN do governo federal; API pública pede token (a chamada sem token voltou vazia) | home 200 (VERIFICADO) | — | OK home | P / 3 | descoberta de conjuntos |

### (d) Legislativo

| Fonte | Formato / Auth / Licença | Atualização, volume, cobertura | Chaves | Teste | Esf./Valor | Habilita |
|---|---|---|---|---|---|---|
| **Câmara: API v2** `https://dadosabertos.camara.leg.br/api/v2/` | JSON/XML, sem chave | `deputados?itens=1` 200 (VERIFICADO); `deputados/204554/despesas` voltou `dados: []` (id usado não tinha despesa; inconclusivo) | id do deputado; CNPJ/CPF do fornecedor nas despesas | **OK** | P / 5 (já usado) | cota parlamentar, presença, votações, discursos |
| **Câmara: cota (arquivo anual)** `https://www.camara.leg.br/cotas/Ano-2026.csv.zip` | ZIP/CSV | VERIFICADO: 4,58 MB, `Last-Modified 08/11/2026 06:31`: atualiza diariamente | CNPJ/CPF do fornecedor; `numDeputadoID` | **OK** | P / 5 | R01-type, fracionamento de cota |
| **Câmara: pessoal (verba de gabinete, secretários parlamentares)** | arquivos próprios | NÃO VERIFICADO (ROADMAP marca ⬜) | — | — | M / 4 | R12 parlamentar × servidor; nepotismo cruzado (INFERÊNCIA) |
| **Senado: Dados Abertos Legis** `https://legis.senado.leg.br/dadosabertos/` | XML/JSON, sem chave | `senador/lista/atual.json` 200, versão "08/11/2026 17:44" (VERIFICADO) | código do parlamentar | **OK** | P / 5 (já usado) | votos, comissões, autoria |
| **Senado: CEAPS** `https://www.senado.leg.br/transparencia/LAI/verba/despesa_ceaps_2026.csv` | CSV | VERIFICADO: 3,9 MB, `Last-Modified 08/11/2026 05:25` | CNPJ/CPF fornecedor | **OK** | P / 5 | cota senadores |
| **Senado: servidores/administrativo** `https://adm.senado.gov.br/adm-dadosabertos/api/v1/servidores/servidores` | JSON, sem chave | VERIFICADO: lista com `nome`, `vinculo`, `situacao`, `cargo`, `funcao`, `lotacao`, `categoria`, `cedido`. **Remuneração e sub-endpoints (lotação por gabinete): NÃO VERIFICADO** | `sequencial`; nome (sem CPF) | **OK** | P / 4 | quadro de assessores e lotação por gabinete; R12 |
| **ALESP** `https://www.al.sp.gov.br/dados-abertos/` | HTML/arquivos | 200 (VERIFICADO); conjuntos não inspecionados | — | OK | M / 3 | despesas e gabinetes deputados SP |
| **ALMG** `https://dadosabertos.almg.gov.br/` | API documentada | 200, página de documentação (VERIFICADO) | id do deputado | OK | M / 4 | verba indenizatória de MG (a ALMG tem fama de ser a mais aberta; INFERÊNCIA) |
| **ALERJ** `http://dadosabertos.alerj.rj.gov.br/` | — | 000 | — | NÃO VERIFICADO | M / 3 | — |
| **Câmara Municipal de SP** `https://splegisws.saopaulo.sp.leg.br/ws/ws2.asmx` | SOAP/WS | 200, serviço ativo (VERIFICADO) | — | OK | M / 3 | maior câmara municipal |
| Demais ALs (BA, PR, RS, PE, CE, PA, GO, SC) e câmaras municipais | — | **NÃO TESTADOS** | — | — | G / 3 | verba indenizatória, folha |

### (e) Judiciário e Ministério Público

| Fonte | Formato / Auth / Licença | Atualização, volume, cobertura | Chaves | Teste | Esf./Valor | Habilita |
|---|---|---|---|---|---|---|
| **DataJud (CNJ)** `https://api-publica.datajud.cnj.jus.br/api_publica_{tribunal}/_search` | Elasticsearch DSL; **chave pública publicada pelo CNJ na wiki do DataJud**, enviada em `Authorization` | VERIFICADO: sem chave → **401** (507 bytes). Já usado em `ingestao/datajud.py`. Limites de paginação/teto por consulta: o CNJ documenta; NÃO reverifiquei hoje | número CNJ do processo; classe, assunto, órgão julgador; **sem nome de parte** (dados de partes limitados por LGPD; FONTE: conhecimento prévio) | 401 sem chave (esperado) | M / 3 | contexto de ações de improbidade por número de processo; não serve para "buscar por empresa" |
| **CNJ: Cadastro Nacional de Condenados por Improbidade** `https://www.cnj.jus.br/improbidade_adm/consultar_requerido.php` | formulário HTML (200) | consulta por requerido; **lote não achado** | CPF/CNPJ | OK página; sem lote NÃO VERIFICADO | G / 4 | R?? "sancionado por improbidade, mas fornecedor"; hoje por consulta; candidato a LAI/ofício |
| **CNIB** `https://www.cnib.org.br/` | acesso restrito (FONTE: conhecimento prévio) | DNS falhou | — | NÃO VERIFICADO | — | não é dado aberto (INFERÊNCIA) |
| **DadosJusBr** `https://api.dadosjusbr.org/v2/orgaos` | JSON, sem chave | VERIFICADO: lista de órgãos com `id_orgao`, `jurisdicao`, `entidade`, `uf`. Já usado | id do órgão + mês | **OK** | P / 4 | remuneração acima do teto, acúmulos (lista de conferência) |
| **STJ dados abertos** `https://dadosabertos.web.stj.jus.br/` | CKAN/arquivos | 200 (VERIFICADO) | nº do processo | OK; conjuntos não inspecionados | M / 3 | contratos e gestão STJ |
| **STF transparência** `https://transparencia.stf.jus.br/` | painel | **403** ao curl (VERIFICADO) | — | bloqueado | M / 2 | tentar a rota do dados.gov.br ou LAI |
| **CNMP / MPs estaduais / TRFs / TRTs / TRE-TSE** | cada órgão publica; DadosJusBr cobre parte (MPs e tribunais) | `cnmp.mp.br/portal/transparencia` deu 404 (URL chutada) | — | NÃO VERIFICADO | G / 3 | salários e verbas indenizatórias do MP/Judiciário |

### (f) Executivo federal

| Fonte | Formato / Auth / Licença | Atualização, volume, cobertura | Chaves | Teste | Esf./Valor | Habilita |
|---|---|---|---|---|---|---|
| **Portal da Transparência: download de dados** `https://portaldatransparencia.gov.br/download-de-dados/` (`ceis`, `despesas-execucao`, `servidores`, `cpgf`, `pep`, ...) | CSV em ZIP, sem chave | páginas 200 (VERIFICADO); arquivos grandes (centenas de MB) não baixados | CNPJ, CPF mascarado, código do órgão, nº do empenho | **OK** | P-M / 5 (já usado) | R11, R12, CEIS/CNEP/CEAF, **CPGF (cartão corporativo)**, PEP |
| **Portal da Transparência: API** `https://api.portaldatransparencia.gov.br/swagger-ui/index.html` | REST; **exige chave gratuita por e-mail** (FONTE: documentação do portal) | swagger 200 (VERIFICADO) | — | OK swagger | P / 4 | consultas pontuais; cuidado com cota por minuto |
| **SIAFI / Tesouro Gerencial** | Tesouro Gerencial exige **login** (FONTE) | — | — | NÃO VERIFICADO. O Portal da Transparência entrega a execução (empenho/liquidação/pagamento) em CSV | — | use o Portal; não dependa do SIAFI direto |
| **SIAPE (Portal): servidores** | CSV mensal (cadastro e remuneração) | já usado em `servidores.py`; páginas 200 | CPF mascarado + nome | OK | P / 5 | R12 |
| **PNCP / Compras.gov.br / SIASG** | ver (c) | — | — | OK | P / 5 | base de contratos |
| **CGU e-Agendas** `https://eagendas.cgu.gov.br/` | HTML/CSV (já usado) | 200 (VERIFICADO). `dadosabertos.cgu.gov.br` não resolveu | agente público, órgão | OK | P / 4 | cruzar reunião × contrato |
| **CGU: CEIS, CNEP, CEAF, Leniência, CEPIM** | via Portal (download) | já usado | CNPJ/CPF | OK | — | núcleo das regras R01–R11 |
| **TCU: inidôneos, contas irregulares, certidões** | ver (a) | — | — | parcial | M / 4 | extensão das sanções |
| **COAF** | **RIF não é público** (FONTE: legislação; INFERÊNCIA) | — | — | não aplicável | — | só PEP (via Portal) e "comunicações" agregadas. Nada nominal sem decisão judicial |
| **Receita: CNPJ (empresas, estabelecimentos, sócios, Simples, regime)** | CSV/ZIP mensal | O Radar lê do espelho `dados-abertos-rf-cnpj.casadosdados.com.br` (VERIFICADO no código). O host oficial não conectou (000) e a rota de `arquivos.receitafederal.gov.br` deu 404; **URL oficial atual NÃO VERIFICADA** (fontes divergem) | CNPJ básico (8), nome do sócio + 6 dígitos do CPF mascarado | **não verificado** | M / 5 | R03/R04/R08/R12; capital social; data de abertura. **Risco**: espelho de terceiro e CNPJ alfanumérico |
| **PGFN (dívida ativa)** `https://dadosabertos.pgfn.gov.br/` | CSV por trimestre | VERIFICADO: índice com pastas `2020_trimestre_01/` em diante (HTTP 200) | CNPJ/CPF (mascarado) | **OK** | P / 4 (já usado) | devedor com contrato |
| **Comex Stat (MDIC)** `https://api-comexstat.mdic.gov.br/` e `balanca.economia.gov.br/.../EXP_2025.csv` | API REST (JWT) e CSV anual | API: **401 "JWT Token not found"**; o CSV `ncm/EXP_2025.csv` não respondeu no teste (vazio) | NCM, país, UF, CNPJ raiz (nos microdados por empresa só agregado; NÃO VERIFICADO) | **API exige token; CSV NÃO VERIFICADO** | M / 3 | já usado; verificar a URL do CSV |
| **ANTT** `https://dados.antt.gov.br/api/3/action/package_list` | CKAN, sem chave | 200 (VERIFICADO) | CNPJ concessionária | OK | M / 3 | concessões rodoviárias/ferroviárias (contratos de longo prazo) |
| **ANEEL** `https://dadosabertos.aneel.gov.br/api/3/action/package_list` | CKAN | 200 (VERIFICADO) | CNPJ | OK | M / 3 | concessões de energia, tarifas, leilões |
| **ANP** `https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos` | CSV | **403** ao curl | CNPJ do posto/distribuidora | bloqueado | M / 2 | preços/combustível |
| **ANAC** | CSV | NÃO TESTADO | — | — | M / 2 | concessões de aeroportos |
| **BNDES operações** `https://dadosabertos.bndes.gov.br/` (CKAN) | CSV/CKAN, sem chave | VERIFICADO: `package_list` 200 (JSON); dataset `operacoes-financiamento` 200 | CNPJ do cliente, município | **OK** | P / 4 | crédito público a empresa × sancionada × doador |
| **Caixa / FNDE / SUS** | ver (c) | — | — | parcial | M / 3 | — |

### (g) Financeiro

| Fonte | Formato / Auth / Licença | Atualização, volume, cobertura | Chaves | Teste | Esf./Valor | Habilita |
|---|---|---|---|---|---|---|
| **Banco Central: SGS** `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{N}/dados?formato=json` | JSON, sem chave | VERIFICADO: série 11 (Selic diária) devolveu `06/11/2026 → 0.050788` | código da série | **OK** | P / 2 | contexto (juros, câmbio) |
| **BCB IF.data** `https://www3.bcb.gov.br/ifdata/` | painel + CSV/Olinda (já usado) | página 200 | CNPJ da IF, código IF | OK | — | RF01 |
| **BCB Olinda** `https://olinda.bcb.gov.br/olinda/servico/.../versao/v1/odata/` | OData | meu serviço de teste deu 404 (nome do serviço chutado; **não conclui nada**) | — | NÃO VERIFICADO | P / 3 | regimes especiais, tarifas |
| **CVM** `https://dados.cvm.gov.br/` (CKAN `api/3/action/package_list`) | CSV, sem chave. Datasets listados: `cia_aberta-cad`, `cia_aberta-doc-*`, `adm_fii-cad`, `adm_cart-cad`, `auditor-cad`, `arrecadacao-receita-publica`... | VERIFICADO: lista 200; diretório `FI/DOC/CDA/DADOS/` 200 (carteira de fundos) | CNPJ do fundo/companhia | **OK** (já usado) | P / 4 | FIDC, fundos com RPPS, companhias; processo sancionador (existe em `dados.cvm.gov.br`; dataset exato NÃO VERIFICADO) |
| **PREVIC / RPPS (CADPREV, DAIR)** `https://cadprev.previdencia.gov.br/` | consulta web | `cadprev` 200 (redireciona); página da PREVIC no gov.br respondeu **401** ao curl | CNPJ do RPPS, IBGE | NÃO VERIFICADO | M / 5 | **investimento de RPPS em fundos de banco ruim (Master/Banco Pleno)**: prioridade, ver abaixo |
| **SUSEP** `https://dados.susep.gov.br/` | — | 404 no host chutado | — | NÃO VERIFICADO | M / 2 | — |
| **FGC, B3** | páginas institucionais | NÃO TESTADOS | — | — | M / 2 | — |

### (h) Internacional

| Fonte | Formato / Auth / Licença | Atualização, volume, cobertura | Chaves | Teste | Esf./Valor | Habilita |
|---|---|---|---|---|---|---|
| **ICIJ Offshore Leaks** `https://offshoreleaks-data.icij.org/offshoreleaks/csv/full-oldb.LATEST.zip` | ZIP/CSV, sem chave; licença ODbL/CC BY-SA (FONTE: ICIJ, não reverificado hoje) | VERIFICADO: **71,9 MB** (HEAD), `Last-Modified 09/09/2026` (não baixado, acima do limite de 50 MB) | nome (e endereço); sem CNPJ | **OK** | P / 3 (já usado) | R? sócio no exterior (a confirmar) |
| **OpenSanctions** `https://data.opensanctions.org/datasets/latest/default/index.json` | JSON FtM; bulk gratuito para uso não comercial (CC BY-NC); **uso comercial exige licença** (FONTE: política do OpenSanctions, não reverificada) | VERIFICADO: índice atualizado em 08/11/2026 18:54; `entities.ftm.json` = **2,58 GB** (não baixado) | `id` FtM, CNPJ em parte | **OK** | M / 4 | PEP internacional, sanções, empresas ligadas; usar subconjuntos por país |
| **OFAC SDN** `https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV` | CSV (redireciona a bucket S3) | VERIFICADO: 206 e arquivo com data de publicação 05/11/2026 na URL | nome | **OK** | P / 3 (já usado) | confirmar manualmente |
| **UE sanções** `https://webgate.ec.europa.eu/fsd/fsf/public/files/csvFullSanctionsList_1_1/content?token=...` | CSV | token que eu usei devolveu **500** (VERIFICADO) | — | **falhou** | P / 3 | conferir `ingestao/` |
| **ONU (Conselho de Segurança)** `https://scsanctions.un.org/resources/xml/en/consolidated.xml` | XML | VERIFICADO: 206, redireciona para `unsolprodfiles.blob.core.windows.net/...consolidatedLegacyByPRN.xml?...` (URL com assinatura temporária: **sempre seguir o redirect**, não gravar a URL final) | nome | **OK** | P / 3 | fecha a lacuna ONU do ROADMAP |
| **GLEIF (LEI)** `https://api.gleif.org/api/v1/lei-records?filter[entity.legalAddress.country]=BR&page[size]=1` | JSON, sem chave, CC0 (FONTE: GLEIF) | VERIFICADO: 4.496 registros BR, cópia dourada de 08/11/2026 08:00Z | LEI; CNPJ em `registeredAs` (NÃO VERIFICADO) | **OK** | P / 3 | ligar empresa brasileira à matriz estrangeira (cadeia de controle) |
| **OpenCorporates** `https://api.opencorporates.com/v0.4/companies/search?q=...` | API com chave (e dados abertos só com condições) | **401 sem chave** (VERIFICADO) | — | exige chave | — / 2 | evitar como dependência (INFERÊNCIA: limites e custo) |
| **OpenOwnership** `https://register.openownership.org/` | registro | **403** e redirecionamento para página institucional (VERIFICADO); cobertura Brasil NÃO VERIFICADA | — | bloqueado | — / 2 | beneficiário final (o Brasil não tem registro público de beneficiário final: INFERÊNCIA) |
| **Wikidata** `https://query.wikidata.org/sparql` | SPARQL, sem chave | VERIFICADO: consulta mínima respondeu 200 | QID; CNPJ (P? NÃO VERIFICADO) | **OK** | P / 2 | PEP, partidos, parentescos (CC0) |
| **UN Comtrade (prévia)** `https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=76&period=2023&partnerCode=0&cmdCode=TOTAL&flowCode=X` | JSON, sem chave na versão "preview" (limite de linhas; chave gratuita para mais) | VERIFICADO: 200, linha `reporterCode 76`, ano 2023, exportações totais | HS, país | **OK** | P / 2 | espelho de comércio (diferença Brasil×parceiro) |
| **FATF** (listas cinza/preta) | PDF/HTML | NÃO TESTADO | — | — | P / 2 | contexto de jurisdição (lista manual de ~20 países) |

## 3. Denominador: quanto custa o Estado e quanto o Radar enxerga

**O que são os "R$ 12 trilhões"**: o PIB brasileiro de 2025 foi de **R$ 12,7 tri** (FONTE: [Poder360](https://www.poder360.com.br/poder-economia/pib-do-brasil-cresce-23-em-2025/), [Metrópoles](https://www.metropoles.com/brasil/pib-2025-ibge), 08/11/2026). Gasto público é uma fração do PIB e há dupla contagem entre esferas (transferências). Sugiro nunca escrever "12 trilhões de dinheiro público".

| Esfera / poder | Valor | Fonte e grau de certeza |
|---|---|---|
| **União: LOA 2026** | **R$ 6,54 tri** totais, dos quais **R$ 1,8 tri refinanciamento da dívida**; R$ 4,5 tri nos Orçamentos Fiscal e da Seguridade (+ R$ 197,9 bi de investimento das estatais) | FONTE: [Agência Senado, 15/01/2026](https://www12.senado.leg.br/noticias/materias/2026/01/15/orcamento-2026-e-sancionado-com-previsao-de-superavit-de-rs-34-2-bi) |
| União: juros e déficit 2025 | juros orçamentários pagos ~R$ 363,6 bi; déficit nominal ~R$ 1,06 tri; déficit primário R$ 55 bi a R$ 62 bi conforme a metodologia | FONTE: buscas (BGU 2025; Tesouro; BC); metodologias diferentes, **não somar** |
| **27 governos estaduais (UFs + DF), 2024** | **R$ 1,416 tri empenhados** (soma de `TotalDespesas` da DCA Anexo I-D, 27 chamadas) | **VERIFICADO** hoje na API Siconfi. SP: R$ 363,5 bi. Pode conter despesas intraorçamentárias (INFERÊNCIA) |
| **Municípios (5.570)** | **Não obtive o total.** 5.266 (94%) entregaram contas de 2024 (FONTE: publicação do Tesouro) | Método: somar `DCA Anexo I-D` ou `FINBRA` de cada município pela API Siconfi (~5.300 chamadas, factível em uma noite). Ordem de grandeza provável acima de R$ 1 tri (**INFERÊNCIA, a confirmar**) |
| **Compras e contratações (todas as esferas)** | **~R$ 1 tri homologado no PNCP em 2025**; o governo estima 16% do PIB (OCDE 2021) | FONTE: Ministério da Gestão via portal de licitações (não oficial); atenção: o texto diz que 16% do PIB seriam 22,7% das despesas do governo geral, o que implica um total de despesas de ~70% do PIB, valor que me parece alto: **INFERÊNCIA de que os números usam bases diferentes; não citar sem conferir** |
| **Legislativo, Judiciário, MP, TCs** | **Não obtive os totais por poder** | Obter na LOA/SIOP por Órgão Superior (Câmara, Senado, TCU, Judiciário, MPU) e nos Siconfi estaduais por função "Legislativa/Judiciária". Fica como tarefa de onda 1 |

**Cobertura atual do Radar (INFERÊNCIA a partir do briefing)**: ~R$ 1,5 tri em contratos PNCP + pagamentos federais a empresas + emendas + cota + servidores. O que ainda **não** vê: despesa executada em município e estado fora do PNCP (empenho, liquidação, pagamento), folha estadual e municipal, transferências Pix, e execução de contratos antigos (pré-2025).

**Fração aproximada por bloco, em termos de "dinheiro que dá para cruzar com CNPJ"** (INFERÊNCIA, a fechar com a soma municipal):

| Bloco | Ordem de grandeza | Observação |
|---|---|---|
| União (Portal da Transparência: empenho a favorecido) | R$ 4+ tri (6,54 tri − 1,8 tri de rolagem = ~4,7 tri) | parte é transferência obrigatória/benefício (sem CNPJ) |
| Estados | R$ 1,4 tri | VERIFICADO (2024) |
| Municípios | provavelmente R$ 1 tri+ | NÃO VERIFICADO |
| Legislativo/Judiciário/MP/TCs | pequeno frente ao total (INFERÊNCIA), mas de alto valor de confiança política | totais não obtidos |

## 4. Ordem de integração (mais dinheiro com menos esforço)

Critério: dinheiro coberto × alertas habilitados ÷ esforço, favorecendo fontes oficiais com API estável.

| # | Integração | Esforço | Dinheiro / ganho | Por quê agora |
|---|---|---|---|---|
| 1 | **Siconfi: DCA/RREO/FINBRA de todos os entes** | P | denominador de 100% dos municípios e estados; ranking "cobertura do Radar por município" | API aberta e estável (VERIFICADO); sem isto não há "denominador honesto" |
| 2 | **TransfereGov API** (especiais, fundo a fundo, TED) | P | emendas e Pix a município com CNPJ do beneficiário | PostgREST com swagger (VERIFICADO); fecha o R09 com execução |
| 3 | **Portal da Transparência: despesas-execucao (empenho/pagamento por favorecido), convênios, CPGF** | P-M | gasto federal completo com CNPJ | já coletado em parte (R11) |
| 4 | **TCE-SP (Audesp)** | M | município paulista: maior despesa municipal do país (INFERÊNCIA) | JSON limpo com CNPJ (VERIFICADO) |
| 5 | **TCE-PE, TCE-RS (LicitaCon), TCE-MG, TCE-PR, TCE-SC, TCE-CE** | M cada | municípios + licitação por dentro | APIs ou CKAN vivos ou prováveis |
| 6 | **Compras.gov.br API (contratações, ARP, preço praticado)** | P-M | licitação federal por dentro; nova regra de **preço fora da curva** por item CATMAT | OpenAPI VERIFICADO |
| 7 | **TCU acórdãos (API) + inidôneos** | P-M | amplia as sanções (R01/R02/R11) | API viva (VERIFICADO) |
| 8 | **RPPS: CADPREV/DAIR + CVM fundos** | M | fundos de pensão de servidores em fundos de banco em risco; pauta de maior apelo público | CVM já usado; DAIR é o elo novo |
| 9 | **Senado: servidores/lotação; Câmara: secretários parlamentares** | P-M | quadro de assessores; R12 estendida | API Senado VERIFICADA |
| 10 | **Estados: folha e convênios dos 11 priorizados** | M cada | folha estadual | portais respondem, conteúdo não inspecionado |
| 11 | **Município grande (100 maiores) via portal próprio ou LAI** | G | cobre o que os TCEs não dão | último recurso |
| 12 | **Internacional**: ONU, GLEIF, OpenSanctions (subconjunto) | P | confirmação de nome; não é dinheiro | valor de credibilidade, não de cobertura |

## 5. Armadilhas, ética de coleta e LAI

**Bloqueios e instabilidade observados hoje (VERIFICADO)**
- `contas.tcu.gov.br`: 503 na raiz.
- `portal.tcm.sp.gov.br`: **429** na primeira requisição (limite agressivo): coletar com intervalo de segundos e backoff exponencial.
- `api.queridodiario.org.br`: 520 após 30 s; primeira chamada deu "no available server".
- `transparencia.stf.jus.br` e `gov.br/anp/...`: 403 ao curl. `gov.br/receitafederal/dados`: 403. Não burlar com disfarce de navegador: usar a rota alternativa (dados.gov.br, arquivo em lote) ou LAI.
- `pncp.gov.br`: o Radar já conhece o 503 em consulta item a item (FONTES.md); manter a regra de não driblar.
- `servicos.tcesc.tc.br/endpoints-portal-transparencia/`: 403 na raiz.
- Hosts que não resolveram ou não conectaram da minha rede: `dadosabertos.rfb.gov.br`, `dados.tce.rj.gov.br`, `dados.tcees.tc.br`, `siops-asp.datasus.gov.br`, `www.cnib.org.br`, `dadosabertos.cgu.gov.br`, `dadosabertos.alerj.rj.gov.br`, `www.transparencia.pa.gov.br`, `dados.ce.gov.br`. Podem ser falha de DNS/IP bloqueado fora do Brasil (INFERÊNCIA). **Reteste de dentro do GitHub Actions** (IPs dos EUA) e de um IP brasileiro antes de concluir "fora do ar".

**Qualidade e pegadinhas de dados**
- TCE-SP: valores em texto com vírgula decimal ("17000,00"); o mesmo gasto aparece como `Empenhado`, `Liquidado` e `Pago`: somar só um evento, senão há dupla ou tripla contagem. O fornecedor às vezes é o próprio município (transferência interna). O identificador é "CNPJ - PESSOA JURÍDICA - 430...": exige parsing, e pessoa física aparece com CPF (mascarar).
- Siconfi: `valor` em float (usar Decimal); mesmo exercício tem colunas "empenhadas", "liquidadas", "pagas" e "inscritas em restos"; cobertura de 94% dos municípios: tratar "não entregou" como dado ausente, não zero.
- TransfereGov: PostgREST com esquemas que mudam; meu chute de tabela voltou `42P01`. Ler o swagger a cada execução e falhar de forma explícita.
- **CNPJ alfanumérico** (FONTE: Fazenda, 07/2026): validação e chaves que assumem só dígitos vão quebrar para empresas novas.
- Espelho de terceiro para o CNPJ: se sair do ar ou mudar o layout, perde-se R03/R04/R08/R12. Planejar a migração para a fonte oficial (confirmar URL atual) e comparar um mês de ambas.
- Valores digitados errados na origem (PNCP): já filtrados em `erro_valor`; replicar essa higiene em TCEs.
- Licença: **OpenSanctions é CC BY-NC para bulk**; se o Radar tiver receita (patrocínio, plano pago), pedir licença comercial ou usar só as listas primárias (OFAC, UE, ONU) (FONTE: política deles, não reverificada).
- Dados de pessoa: CPF só mascarado; nome só de agente público no exercício; folha municipal e salário de servidor entram só com a base legal de transparência ativa e com a função pública exibida. Sem raspagem de portal que proíba em Termos.

**Coleta ética e sustentável**
- `User-Agent: RadarPublico/1.0 (projeto civico; github.com/lucasnegrelli/radar-publico)` em todas as chamadas; contato no cabeçalho `From` (sugestão).
- Janela noturna (00h–06h, horário de Brasília) para fontes pesadas (PNCP, Siconfi em massa, TCEs); 1 requisição por segundo por host como teto padrão, 1 a cada 3–5 s para portais de TCE.
- Cache por URL com `ETag`/`Last-Modified` (a Câmara e o Senado publicam `Last-Modified`, VERIFICADO), e `If-Modified-Since` para evitar re-baixar CSV de 4 MB todo dia.
- Idempotência: gravar `fonte + chave natural + período` e usar upsert; manter o resultado anterior quando a fonte falhar (já é prática no `despesas_federais.py`).
- Retomada por checkpoint (município × mês); **registro de saúde por fonte** (data do último sucesso, linhas, defasagem), que alimenta a "página de status das fontes" do ROADMAP.
- Robots/Termos: ler antes de cada portal novo; se proibir automação, pedir autorização ou LAI.
- URLs com assinatura temporária (ONU, OFAC) nunca devem ser gravadas: seguir o redirect de cada execução.

**O que exige pedido por LAI (Lei 12.527/2011)** (INFERÊNCIA, a validar caso a caso)
1. Microdados de licitação (participantes e propostas) dos TCEs que só têm consulta.
2. Folha de pagamento de municípios sem portal em lote e de tribunais/MPs estaduais sem API.
3. Quadro de assessores e lotação de assembleias legislativas sem dado aberto.
4. Viagens e diárias do Judiciário e do Senado em lote.
5. Agenda do Presidente da República (hoje só consulta parcial).
6. Lista de condenados por improbidade em formato de dados (CNJ) com CPF/CNPJ.
7. Valores detalhados de operações de caso específico (ex.: Banco Master): só notícias hoje; LAI ao BCB/FGC/PREVIC com limites de sigilo bancário (muito provável resposta restritiva).
8. **Não adianta pedir**: RIF do COAF (sigilo legal), CNIB (acesso restrito).

## 6. Plano de coleta em 3 ondas

**Onda 1: 30 dias (denominador e transferências)**
1. Siconfi: carregar `entes`, DCA Anexo I-D e I-C (despesa por função) e RREO de todos os entes; publicar "cobertura por município" (quanto do gasto o Radar enxerga).
2. TransfereGov: `transferenciasespeciais`, `ted`, `fundoafundo` por API; ligar ao R09.
3. Portal da Transparência: confirmar `despesas-execucao`, convênios, CPGF e PEP em CSV mensal.
4. Reabrir ONU (redirect), corrigir UE, mapear a URL oficial do CNPJ e preparar o CNPJ alfanumérico.
5. Senado `servidores`: explorar sub-endpoints (lotação, remuneração) e carregar quadro de assessores.
6. Página de status das fontes (já no ROADMAP) com os códigos de teste desta pesquisa.
7. Obter totais por poder (LOA/SIOP) e fechar o denominador municipal.

**Onda 2: 90 dias (municípios e licitação por dentro)**
1. TCE-SP (Audesp) completo; depois TCE-PE e TCE-RS (CKAN/LicitaCon), em seguida TCE-MG, PR, SC, CE. Um TCE por sprint, com validação cruzada contra o Siconfi.
2. Compras.gov.br: contratações 14.133, ARP e preços praticados; nova regra de preço por item.
3. TCU: acórdãos e inidôneos; certidões.
4. RPPS (CADPREV/DAIR) × CVM: fundos de pensão em ativos de banco em risco.
5. Câmara: secretários parlamentares; ALMG/ALESP/ALERJ (verba indenizatória).
6. Primeiros pedidos LAI (itens 1 a 4 da seção 5) com acompanhamento de prazo.
7. Querido Diário em modo "melhor esforço", com fila de re-tentativa.

**Onda 3: 12 meses (cobertura nacional e confiabilidade)**
1. Os demais TCEs e TCMs (RJ, ES, MT, MS, GO, BA, PA, AM...), um por vez, ou por LAI quando não houver lote.
2. Folha estadual dos 11 estados priorizados e das 100 maiores prefeituras.
3. Judiciário/MP via DadosJusBr + tribunais; DataJud para contexto por número de processo.
4. Fontes internacionais de enriquecimento: OpenSanctions (subconjunto, licença), GLEIF, Wikidata, Comtrade.
5. Migração do CNPJ para fonte oficial + regressão comparando um mês; plano de contingência se a fonte mudar.
6. Meta de qualidade: cada fonte com data do último sucesso, defasagem aceitável e dono; cobertura publicada como **% do gasto de cada esfera**.

## 7. Fontes consultadas (acesso em 08/11/2026)

- Siconfi API: https://apidatalake.tesouro.gov.br/ords/siconfi/tt/ (entes, dca, extrato_entregas) e catálogo https://www.tesourotransparente.gov.br/ckan/api/3/action/package_list
- TransfereGov: https://api.transferegov.gestao.gov.br/
- TCU acórdãos: https://dados-abertos.apps.tcu.gov.br/api/acordao/recupera-acordaos
- TCE-SP: https://transparencia.tce.sp.gov.br/api/json/municipios ; TCE-PE: https://sistemas.tce.pe.gov.br/DadosAbertos/ ; TCE-RS: https://dados.tce.rs.gov.br/
- Senado: https://legis.senado.leg.br/dadosabertos/ ; https://adm.senado.gov.br/adm-dadosabertos/ ; Câmara: https://dadosabertos.camara.leg.br/
- Compras.gov.br: https://dadosabertos.compras.gov.br/v3/api-docs
- DadosJusBr: https://api.dadosjusbr.org/v2/orgaos ; DataJud: https://api-publica.datajud.cnj.jus.br/
- GLEIF: https://api.gleif.org/api/v1/ ; ICIJ: https://offshoreleaks-data.icij.org/ ; OpenSanctions: https://data.opensanctions.org/datasets/latest/default/index.json
- LOA 2026: https://www12.senado.leg.br/noticias/materias/2026/01/15/orcamento-2026-e-sancionado-com-previsao-de-superavit-de-rs-34-2-bi
- PIB 2025: https://www.poder360.com.br/poder-economia/pib-do-brasil-cresce-23-em-2025/ e https://www.metropoles.com/brasil/pib-2025-ibge
- Atricon / Radar da Transparência (contexto TCEs): https://www.tcesc.tc.br/atricon-e-tcesc-divulgam-cenario-da-transparencia-publica-em-santa-catarina-e-no-pais
- Código do repositório (`ingestao/cnpj.py`, `socios_exterior.py`, `datajud.py`) para identificar o espelho do CNPJ e o uso do DataJud.

**Limites desta pesquisa**: testei o acesso, não o conteúdo, de muitas páginas; vários domínios de TCEs foram palpites meus e falharam; não li os dicionários de dados; não baixei arquivos grandes; o total municipal e os totais por poder ficaram pendentes (listados na Onda 1).
