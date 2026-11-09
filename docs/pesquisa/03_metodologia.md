# Radar Público: metodologia de sinais de integridade (versão de pesquisa)

Data: 08/11/2026. Autoria: especialista em integridade de compras públicas (pesquisa para o Radar Público). Escopo: leitura de `docs/` e `alertas/*.sql` e `ingestao/*.py`; nenhum código do produto foi alterado.

## 0. Convenções, limites e o que foi (e não foi) verificado

- **VERIFICADO** = li o código/documento do repositório ou abri a página citada. **FONTE** = afirmado por fonte citada (nem sempre li o texto integral). **INFERÊNCIA** = meu raciocínio, a validar. **A CONFERIR** = dependo de memória profissional; checar antes de publicar.
- **Limite da pesquisa web (honestidade):** consegui abrir apenas listagens e resumos. NÃO li o texto integral dos guias OCP 2024, OCDE 2025, Banco Mundial e FATF. Os indicadores atribuídos a eles abaixo vêm do conhecimento prévio do autor sobre esses guias e estão marcados **FONTE/A CONFERIR**. Não inventei números de acórdão do TCU: onde a menção é genérica, está dito.
- **Convenção de campos:** campos reais do Radar vistos no código = `compra`, `valor_global`, `valor_inicial`, `fornecedor_doc`/`doc14`, `orgao_cnpj`, `data_assinatura`, `esfera`, `uf`, `municipio`, `ibge`, `objeto`, `tipo_contrato`, `categoria`, `modalidade`, `amparo`, `valor_estimado`, `valor_homologado`, `capital_social`, `porte`, `natureza`, `abertura`, `situacao`, `cnae`, `matriz`, `socios_pf (nome, mid6, qualificacao)`, `socios_ext`, tabelas `ceis`, `cnep`, `tse_cand`, `tse_receitas`, `siconfi_entes` (VERIFICADO em `alertas/00_base_contratos.sql` e regras). Campos não vistos no código (ex.: logradouro, telefone, e-mail, `data_entrada_sociedade`, `data_situacao_cadastral`) existem no layout público da Receita (A CONFERIR se o `cnpj.py` os preserva).

### Fontes consultadas (acesso em 08/11/2026)
| Fonte | URL | Status |
|---|---|---|
| OCP, *Red Flags in Public Procurement: a guide to using data to detect and mitigate risks* (2024; 73 indicadores; mapeamento OCDS; biblioteca Cardinal) | https://www.open-contracting.org/resources/red-flags-in-public-procurement-a-guide-to-using-data-to-detect-and-mitigate-risks/ ; PDF https://open-contracting.org/wp-content/uploads/2024/12/OCP2024-RedFlagProcurement-1.pdf ; Cardinal https://open-contracting.org/?p=24853 | FONTE (resumo lido; PDF não lido) |
| OCP, *Red flags for integrity* (2016, 1ª versão) | https://www.open-contracting.org/2016/11/30/red-flags-integrity-giving-green-light-open-data-solutions/ | FONTE |
| OCDE, *Guidelines for Fighting Bid Rigging in Public Procurement* (2009; revisão 2025; dois checklists: detecção e desenho) | https://oecd-ilibrary.org/finance-and-investment/guidelines-for-fighting-bid-rigging-in-public-procurement_8cfeafbb-en | FONTE (estrutura confirmada; lista integral não lida) |
| Banco Mundial (Integrity Vice Presidency), *Warning Signs of Fraud and Corruption in Procurement* (antes *Common Red Flags*) | https://documents.worldbank.org/curated/en/223241573576857116 | FONTE (existência e escopo; texto não lido) |
| Fazekas, Tóth & King (2016), *An Objective Corruption Risk Index Using Public Procurement Data*, Eur. J. Criminal Policy and Research | https://link.springer.com/10.1007/s10610-016-9308-z | FONTE (resumo: índice composto com proposta única; empresas de maior risco mais ligadas a paraísos fiscais e a políticos) |
| Fazekas & Tóth (2017), U4 brief sobre indicadores de uso corrupto de empresas (idade, registro, dados financeiros, propriedade) | https://nbdy.chickenkiller.com/publications/proxy-indicators-for-the-corrupt-misuse-of-corporations.pdf (espelho não oficial; procurar a versão em u4.no) | FONTE (resumo) |
| Fazekas & Kocsis (2020), *Uncovering High-Level Corruption*, British J. Political Science | https://econpapers.repec.org/RePEc:cup:bjposi:v:50:y:2020:i:1:p:155-164_7 | FONTE |
| FATF, *Guidance: Politically Exposed Persons (Rec. 12 e 22)*, 2013 | https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Peps-r12-r22.html | FONTE (resumo) |
| FATF, *Guidance on Beneficial Ownership of Legal Persons* (Rec. 24, mar/2023) | https://www.fatf-gafi.org/content/fatf-gafi/en/publications/Fatfrecommendations/Guidance-Beneficial-Ownership-Legal-Persons.html | FONTE (resumo) |
| Literatura citada de memória, sem URL verificada (A CONFERIR): Decarolis & Giorgiantonio (2022, *Corruption red flags in public procurement*, EPJ Data Science); Conley & Decarolis (2016, *Detecting bidders groups in collusive auctions*, AEJ Micro); Imhof, Karagök & Rutz (2018, *Screening for bid rigging: does it work?*, J. Competition Law & Econ.); Ferraz & Finan (2008, auditorias aleatórias da CGU, QJE); Boas, Hidalgo & Richardson (2014, doações de campanha e contratos no Brasil, J. of Politics); Colonnelli & Prem (2022, *Corruption and Firms*, Rev. Econ. Studies); Bandiera, Prat & Valletti (2009, *Active and passive waste*, AER); Fisman & Wei (2004, importações "faltantes" na China, JPE); Global Financial Integrity (relatórios de *trade misinvoicing*). | — | A CONFERIR |
| Marco legal brasileiro citado de memória (A CONFERIR): Lei 14.133/2021 (arts. 55, 75, 94, 125), Lei 12.846/2013 (art. 14, desconsideração da personalidade), Lei 12.813/2013 (conflito de interesses; quarentena), Código Penal art. 359-C, LC 123/2006 (limites ME/EPP/MEI), Lei 9.504/1997 (art. 73). | — | A CONFERIR |
| TCU e CGU: sistemas e matrizes (ALICE, análises de risco em convênios e emendas) conhecidos por prática profissional; **não verifiquei** URLs nem números de acórdão. Recomendação: pedir ao time uma busca dirigida em pesquisa de jurisprudência do TCU e em `https://www.gov.br/cgu` antes de citar. | — | A CONFERIR |

---

## 1. Catálogo de red flags, por fase

Legenda de **Radar hoje**: Sim = regra existente; Parcial = há dado ou regra aproximada; Não = lacuna. **Dado** = onde o sinal é medido. Cada sinal aponta para as regras novas (N01–N30) da seção 3.

### 1.1 Orçamento e emenda
| # | Sinal | Racional / fonte | Dado | Radar hoje |
|---|---|---|---|---|
| F01 | Entidade privada sem fins lucrativos recém-criada ou sem histórico recebe emenda | Capacidade técnica/operacional insuficiente (OCP planejamento; prática TCU/CGU em transferências) FONTE/A CONFERIR | CNPJ (abertura, natureza, capital), Portal Transparência (emendas) | Sim (R09) |
| F02 | Entidade impedida (CEPIM) ou sancionada recebe emenda | Transferência a quem não pode receber | CEPIM, CEIS | Sim (R09) |
| F03 | Mesma entidade recebe de muitos autores/anos ("entidade cativa") | Padrão de captura / intermediação | Emendas (autor, favorecido, ano) | Parcial (`n_autores` coletado, não usado como sinal) → N16 |
| F04 | Parlamentar concentra parcela alta de suas emendas num só favorecido/município | Direcionamento | Emendas | Não → N17 |
| F05 | Município recebe emenda desproporcional à sua capacidade fiscal | Absorção/execução duvidosa | Siconfi + emendas | Não → N18 |
| F06 | Emenda paga, objeto contratado por dispensa/ata logo depois, com fornecedor recorrente | Cadeia emenda→contrato→fornecedor | Emendas + PNCP (município) | Não (A CONFERIR vínculo) → N19 |
| F07 | Valor liberado concentrado no fim de exercício/semana eleitoral | Pressão de calendário; Lei 9.504 art. 73 A CONFERIR | Datas de pagamento | Não |

### 1.2 Licitação (edital e disputa)
| # | Sinal | Racional / fonte | Dado | Radar hoje |
|---|---|---|---|---|
| F10 | Proposta única / poucos licitantes em mercado competitivo | Indicador-âncora do índice de Fazekas e do OCP FONTE | PNCP resultado/propostas, ComprasGov | Não (licitantes não ingeridos) → N01 |
| F11 | Valor homologado ≈ estimado (desconto ≈ 0) | Ausência de competição de preço (OCP, OCDE: propostas próximas) FONTE/A CONFERIR | `valor_estimado`, `valor_homologado` | Parcial (dado existe) → N02 |
| F12 | Prazo curto entre publicação e abertura | Restringe participação; limites legais Lei 14.133 art. 55 A CONFERIR; OCP FONTE | PNCP compras (datas de publicação/abertura) | Não → N03 |
| F13 | Especificação restritiva / marca / "objeto genérico" | OCP, Banco Mundial FONTE/A CONFERIR | Texto do objeto/itens | Não → N24 |
| F14 | Uso recorrente de dispensa/inexigibilidade por órgão acima dos pares | OCP, TCU A CONFERIR | `modalidade`, `amparo` | Parcial (campo existe) → N04 |
| F15 | Licitações com propostas muito próximas, padrões de lance (cover bidding), propostas perdedoras com erros idênticos | Checklist OCDE FONTE | Atas/propostas (não abertos no PNCP em massa) | Não → N07 (fase 6 meses) |
| F16 | Mesmo licitante/empresa relacionada apresenta várias propostas; licitantes que desistem sistematicamente | Checklist OCDE FONTE | Participantes | Não → N07 |
| F17 | Edital publicado/aberto antes da empresa existir ou logo após sua abertura | Tempo: abertura × edital | `abertura` × data publicação da compra | Parcial (R03 usa assinatura) → N10 |

### 1.3 Contratação
| # | Sinal | Racional / fonte | Dado | Radar hoje |
|---|---|---|---|---|
| F20 | Fornecedor sancionado (CEIS/CNEP) com alcance sobre o ente na data | Fato jurídico verificável | CEIS/CNEP + PNCP | Sim (R02, R01) |
| F21 | Fornecedor inapto/baixado/suspenso na data do contrato | Fato cadastral | Situação cadastral RFB + `data_situacao` | Não → N11 |
| F22 | Fracionamento (várias dispensas somando acima do limite) | Burla de licitação (TCU, OCP) FONTE/A CONFERIR | PNCP contratos | Sim (R06, com limiares a revisar) |
| F23 | Aditivos acima do limite legal (25%/50%, Lei 14.133 art. 125 A CONFERIR) | Jogo do "contrato barato, aditivo caro" (OCP/Banco Mundial FONTE) | `valor_inicial`, `valor_global` | Parcial: razão >20 hoje descarta como erro; faixa 1,25–20 não olhada → N05 |
| F24 | Contratação direta de grande valor | Ausência de competição | `modalidade`, `valor_global` | Parcial → N04 |
| F25 | Contrato assinado antes da homologação / publicado no PNCP com atraso | Lei 14.133 art. 94 (publicação como condição de eficácia) A CONFERIR | datas | Não → N12 |
| F26 | Sobrepreço contra referência | Preço unitário > mediana de itens comparáveis (Banco Mundial, TCU, OCP) FONTE | Itens (PNCP bloqueia 503) / Painel de Preços / Banco de Preços em Saúde | Não → N06 |
| F27 | Pico de contratos no fim de mandato | Bem tutelado por CP art. 359-C A CONFERIR | `data_assinatura`, mandato (TSE) | Não → N27 |

### 1.4 Execução e pagamento
| # | Sinal | Racional | Dado | Radar hoje |
|---|---|---|---|---|
| F30 | Pagamento a empresa sancionada | Fato jurídico | Portal Transparência (favorecido) | Sim (R11, R01) |
| F31 | Pagamento > contratado, ou pagamento concentrado após mudança contratual | Execução irregular | Empenho, liquidação, pagamento × contrato | Não → N13 |
| F32 | Pagamento sem entrega comprovada (obra paralisada) | CGU/TCU (obras paralisadas) A CONFERIR | Obras (Transferegov/ObrasGov) | Não |
| F33 | Prorrogações sucessivas de contratos de dispensa | OCP FONTE/A CONFERIR | Vigência | Não |

### 1.5 Empresa
| # | Sinal | Racional / fonte | Dado | Radar hoje |
|---|---|---|---|---|
| F40 | Empresa jovem, capital minúsculo vs contrato | Fazekas e Tóth (idade da empresa) FONTE | `abertura`, `capital_social` | Sim (R03, R04) |
| F41 | MEI/ME/EPP com contratos acima do teto do porte | Lei Complementar 123/2006 A CONFERIR; sinal objetivo | porte, opção MEI/Simples, contratos | Parcial (`porte` existe) → N09 |
| F42 | CNAE incompatível com objeto contratado | Empresa de fachada (T6 em `TIPOLOGIAS.md`) | `cnae` × `objeto` | Não → N23 |
| F43 | Endereço, telefone ou e-mail compartilhados entre licitantes/fornecedores do mesmo órgão | Checklist OCDE; Banco Mundial FONTE | Estabelecimentos RFB | Não → N08 |
| F44 | Dívida ativa/tributária elevada | PGFN (não impede contratar necessariamente) | PGFN | Parcial (PGFN ingerido) → N14 |
| F45 | Empresa sancionada reabre sob outro CNPJ (mesmo sócio/endereço) | Desconsideração da personalidade jurídica (Lei 12.846 art. 14 A CONFERIR) | CEIS + QSA + `abertura` | Não → N15 |

### 1.6 Pessoas
| # | Sinal | Racional / fonte | Dado | Radar hoje |
|---|---|---|---|---|
| F50 | Sócio é agente político eleito | PEP (FATF Rec. 12) FONTE | TSE × QSA | Sim (R10) |
| F51 | Sócio é servidor federal | Conflito de interesses | SIAPE × QSA | Sim (R12) |
| F52 | Doador de campanha vira fornecedor | Boas et al. 2014 (FONTE/A CONFERIR) | TSE receitas × PNCP | Sim (R05, só prefeito 2024) → N20 |
| F53 | Parentesco entre sócio/administrador e agente | OCP/Banco Mundial FONTE | TSE (candidatos), SIAPE (nomes), sobrenome raro | Não → N22 |
| F54 | Patrimônio declarado incompatível com renda pública | Prática de enriquecimento ilícito | TSE bens × remuneração | Não → N26 |
| F55 | Ex-ocupante de cargo de alto escalão vira sócio/fornecedor dentro da quarentena | Lei 12.813 A CONFERIR | e-Agendas, SIAPE | Não → N25 |

### 1.7 Rede
| # | Sinal | Racional | Dado | Radar hoje |
|---|---|---|---|---|
| F60 | Sócios em comum entre licitantes/vencedores da mesma compra | Colusão (OCDE) | QSA | Parcial (`socios_pf` existe) → N08/N21 |
| F61 | Grupo oculto de empresas concentra o órgão | R07 olhando só o CNPJ subestima | QSA + PNCP | Não → N21 |
| F62 | Rodízio de vencedores entre mesmas empresas | OCDE: "bid rotation" FONTE; Conley & Decarolis 2016 A CONFERIR | Participantes ou proxy de vencedores | Não → N07 |
| F63 | Empresas "gêmeas" (mesmo contador, endereço, e-mail) | Fachada | RFB | Não → N08 |

### 1.8 Exterior
| # | Sinal | Racional | Dado | Radar hoje |
|---|---|---|---|---|
| F70 | Sócio em jurisdição de sigilo | FATF Rec. 24 FONTE; Fazekas 2016 (risco ↔ paraíso) FONTE | `socios_ext` | Sim (R08) |
| F71 | Cadeia de controle opaca (sócio PJ de PJ, nominee) | FATF Rec. 24 FONTE | QSA (tipo_socio) | Parcial → N28 |
| F72 | Coincidência de nome com Offshore Leaks / OFAC | Só "confirmar" | `offshore.py`, `ofac.py` | Parcial |
| F73 | Mis-invoicing em comércio exterior (sub/superfaturamento de NCM×país) | Fisman & Wei 2004; GFI A CONFERIR | Comex Stat (NCM, país, kg, FOB) | Parcial (ingerido) → N29 |
| F74 | Fluxos agregados anômalos para paraísos | Contexto, não acusação | Comex, BCB | Parcial → N29/N30 |

---

## 2. Avaliação das regras atuais (R01–R12, RF01)

Escala: **Validade** (alta/média/baixa), **Poder discriminatório** (capacidade de separar caso de interesse de ruído), **Decisão** (manter, mudar, sair). "Como medir precisão" sempre usa o protocolo da seção 4 (rótulo A "dado correto" e rótulo B "atenção justificada").

| Regra | Validade conceitual | Falsos positivos prováveis | Dados necessários / lacuna | Poder discriminatório | Medir precisão | Decisão |
|---|---|---|---|---|---|---|
| **R01** cota paga a sancionada | Alta: fato jurídico (sanção que impede de contratar + alcance) | Alcance mal modelado (sanção só de um órgão); sanção suspensa judicialmente; homônimo se casar por nome | CEIS/CNEP com `abr`, datas; cota Câmara/Senado (CNPJ) | Muito alto (evento raro, binário) | Rótulo A: conferir sanção na página CGU na data do pagamento. n pequeno: revisar 100% | **Manter** |
| **R02** contrato com sancionada | Alta, e o código trata alcance por esfera/UF (VERIFICADO) | Sanção suspensa; republicação de contrato anterior; sanção "Na Esfera e no Poder" ainda gera "baixa/media" mesmo se o Poder diverge (o SQL não checa Poder) | CEIS, PNCP | Alto | Amostra estratificada por `gravidade` | **Manter**; **mudar**: checar Poder (Executivo/Legislativo/Judiciário) e data de publicação no PNCP vs. data de início da sanção (assinatura anterior à publicação da sanção não é irregularidade) |
| **R03** empresa nova com contrato grande | Média: idade é preditor documentado (Fazekas e Tóth), mas fraco isolado | Empresa aberta para obra/ata (parte excluída por `tipo_especial`); filial nova de grupo (usa `estab.abertura` do estabelecimento, não da matriz: **filial nova de empresa antiga dispara** — A CONFERIR) ; MEI/ME que apenas migrou CNPJ | `abertura` da **matriz**/primeiro estabelecimento, QSA histórico | Baixo a médio sozinho; sobe muito com N09/N10/N15 | Precisão rótulo B por faixa (<90 d, 90–180 d) | **Mudar**: usar data de abertura da matriz (menor `abertura` por `cnpj_basico`); incluir sinais combinados; reduzir peso isolado |
| **R04** contrato ≫ capital | Média-baixa: capital social não é lastro de capacidade (capital pode ser baixo em empresas legítimas de serviços); razão 50–1000× | Contratos plurianuais, atas de registro de preço (valor teto), erro de escala; PNCP `valor_global` é estimado | `capital_social`, `valor_global`, prazo | Baixo (a pontuação já dá -25) | Rótulo B | **Mudar**: normalizar por vigência (valor anual) e só combinar com idade/porte. Se não houver ganho de precisão em amostra de 100, **sair** como regra independente e virar atributo de R03 |
| **R05** doador virou fornecedor | Alta como hipótese de captura (FONTE: Boas et al. 2014 A CONFERIR), mas só para prefeito eleito 2024 | Doador que já era fornecedor; **homônimo**: casamento por nome + 6 dígitos centrais do CPF. INFERÊNCIA: para nomes muito comuns (centenas de milhares de pessoas) a chance de colisão de 6 dígitos (10⁶ combinações) deixa de ser desprezível | TSE receitas, QSA, PNCP; **frequência do nome** | Médio | Rótulo A (identidade) é o ponto crítico: checar CPF integral na fonte TSE para amostra | **Manter e mudar**: penalizar nomes frequentes, exigir `qualificacao`+município/UF coerentes, estender a governador/deputados (N20), exigir que a empresa não tivesse contrato com o ente **antes** da eleição como atenuante |
| **R06** fracionamento | Média: conceito sólido (TCU), mas parametrização duvidosa. O SQL usa faixa R$ 15–70 mil como "faixa da dispensa" (VERIFICADO). INFERÊNCIA/A CONFERIR: o limite de dispensa por valor na Lei 14.133 (art. 75, I e II) é ~R$ 125 mil para compras e serviços e ~R$ 62 mil para obras e serviços de engenharia (atualizado por decreto) | Compras sucessivas legítimas de itens distintos; itens de natureza diferente; atas | `objeto`, `categoria`, dispensa por `modalidade` | Médio-baixo com os limiares atuais | Rótulo B por amostra de grupos; verificar se o objeto é o mesmo | **Mudar**: limite por tipo (engenharia × demais) e vigente por ano; agrupar por objeto similar (similaridade textual), não só por órgão×fornecedor×trimestre; usar soma anual vs. limite |
| **R07** concentração | Baixa-média: concentração em município pequeno é frequente | Mercado local pequeno; serviços contínuos; só vê contratos do PNCP (cobertura parcial em municípios que não migraram) | Cobertura de PNCP por município | Baixo (peso -30 já o reduz) | Rótulo B | **Mudar**: usar índice de Herfindahl por categoria e município, comparar com pares de população semelhante (z-score); elevar ao nível de **grupo** (N21); senão rebaixar para contexto permanente |
| **R08** sócio em jurisdição favorecida | Média: FATF/Fazekas tratam paraíso como risco; mas holding legítima é comum | Multinacionais; Luxemburgo/Suíça/Singapura no nível 2 são centros legítimos; lista é estática | `socios_ext`, lista de países | Baixo no nível 2; médio no nível 1 | Rótulo B | **Mudar**: só nível 1 pontua; nível 2 vira "contexto"; combinar com cadeia opaca (N28) e ausência de beneficiário final divulgado |
| **R09** emendas para entidade | Alta para CEPIM/sanção; média para "nova"/"capital baixo" | ONG nova legítima; sanção posterior ao pagamento (já tratada: "na data") | emendas, CEPIM, CEIS, CNPJ | Alto para CEPIM; baixo para capital | Rótulo A (CEPIM/CEIS na data), B (demais) | **Manter**; **mudar**: separar sinais (CEPIM = ancora, capital = apoio); incorporar N16–N18 |
| **R10** político eleito sócio | Média-alta: PEP é sinal clássico (FATF), mas sócio de empresa privada é legal; a regra exige contratos ≥ R$ 100 mil | Sócio que já saiu (base não tem data de saída, VERIFICADO em `REGRAS.md`); homônimo (nome + 6 dígitos); vereador/pequeno município é rotina | QSA, TSE, `data_entrada_sociedade` | Médio | Rótulo A crítico; B por cargo | **Manter**; **mudar**: usar data de entrada na sociedade e mandato; hierarquizar por cargo e ente do contrato (mesmo ente do mandato = mais forte) |
| **R11** pagamento federal a sancionada | Alta (fato jurídico) | Pagamento por entrega anterior à sanção; alcance | Portal Transparência (mensal, sem dia), CEIS | Alto | Rótulo A: conferir data de empenho/ordem bancária vs. sanção | **Manter**; **mudar**: usar data da ordem bancária e a data do empenho, não o mês |
| **R12** servidor sócio de fornecedor | Média: pode haver atividade privada permitida | Atividade privada autorizada, sócio sem administração (regra pondera: alta se administra), homônimo (nome + CPF parcial) | SIAPE (cargo, regime, jornada), QSA | Médio | A e B | **Manter**; **mudar**: dedicação exclusiva/cargo comissionado e contrato com o **mesmo órgão** de lotação = prioridade; servidor em outra área = contexto |
| **RF01** banco em crescimento acelerado | Média: sinal de risco financeiro, **não** de fraude em compras; tipologia T1 | Expansão legítima; fintechs; capta de investidores qualificados (sem relação com dinheiro público) | IF.data, CVM, RPPS (CADPREV) | Baixo no isolamento; sobe quando liga a RPPS/FIDC com recursos públicos | Backtest histórico (ex.: casos de liquidação) | **Mudar**: exigir exposição de dinheiro público (RPPS, fundos, depósitos) para entrar em "alertas"; sem isso, "monitor de risco" separado, fora da contagem de alertas |

### Achados críticos sobre o sistema atual (VERIFICADO no código)
1. **`erro_valor` descarta o que talvez seja o sinal.** `f_global_vs_inicial` marca razão `valor_global > 20 × valor_inicial` como erro de digitação, mas a faixa 1,25–20 (aditivos acima do limite legal) nunca é examinada. → N05.
2. **Pontuação de destaque mistura eixos.** A fórmula `100/40/0 + 14·log10(valor) + 45 (sinais combinados) + peso do tipo + bônus` (VERIFICADO em `web/main.js`: `pontuar`) soma força do sinal, materialidade e interesse noticioso. O bônus de 45 para "correlação" conta duas vezes quando as regras são correlacionadas por construção (R03 e R04 olham "pequena e nova"; R06 e R07 olham concentração; R01, R02 e R11 podem descrever a mesma sanção). `PESO_R` é definido à mão (R07 = -30; R10 = +40) sem calibração.
3. **Três regras para um fato.** Uma sanção produz R01+R02+R11 sobre o mesmo CNPJ; sem agrupar por "fato gerador" a contagem de alertas e a pontuação inflam.
4. **R03 usa `estab.abertura` por estabelecimento** (`JOIN estab e ON e.cnpj = p.doc14`): se o contrato for assinado com o CNPJ completo de uma filial recente, a empresa parece nova. INFERÊNCIA (confirmar com o dado).
5. **Cobertura PNCP:** `FONTES.md` diz "desde 2025", mas a base aceita 2020 em diante; a cobertura por município varia. Concentração e fracionamento sofrem com a **ausência de contratos** em municípios que não publicam.
6. **Match por nome + 6 dígitos de CPF** (R05, R10, R12) é a maior fonte de risco jurídico, pois afeta pessoa física. Precisa de métrica de colisão.

---

## 3. Novas regras (N01–N30)

**Prioridade (P)** = Força (F, 1–5) × Disponibilidade do dado (D, 1–5) ÷ Custo (C, 1–5); classes: P1 ≥ 6, P2 3–6, P3 < 3. **Nível de evidência (NE):** NE1 = coincidência de dados; NE2 = fato documental em fonte primária; NE3 = fato confirmado por decisão de órgão competente (ver seção 5). Todos os valores de limiar são **provisórios** até a calibração (seção 4). "Dado" lista campos reais (R) = vistos no código; (RFB) = layout público da Receita, A CONFERIR se ingerido; (PNCP) = campos da API do PNCP, A CONFERIR; (PT) = Portal da Transparência.

### 3.1 Competição e licitação
| ID | Nome / hipótese | Definição operacional e limiar | Falsos positivos | NE | "O que isto não prova" | F·D/C → P |
|---|---|---|---|---|---|---|
| **N01** | **Proposta única em disputa competitiva.** Hipótese: um único licitante em objeto de mercado amplo sugere restrição de competição (indicador-âncora de Fazekas e OCP). | Nº de licitantes por compra (PNCP resultado/propostas ou ComprasGov: fornecedores participantes). Sinal: `n_licitantes = 1` em pregão/concorrência com `valor_estimado ≥ R$ 200 mil`; comparar com mediana do órgão e da categoria (z-score). | Objetos de nicho; sessão deserta; licitação por item onde só um item atraiu 1 proposta | 1 | Não prova direcionamento nem conluio; pode ser mercado fraco ou edital mal divulgado. | F4·D2÷C3 = 2,7 → **P3 agora, P1 quando houver dado de licitantes** |
| **N02** | **Desconto próximo de zero.** Hipótese: homologado ≈ estimado em modalidade competitiva sugere ausência de competição de preço (OCDE: propostas próximas). | `valor_homologado / valor_estimado ≥ 0,99` em pregão/concorrência com ≥ R$ 500 mil, e o órgão tem mediana de desconto ≥ 10% (R: `cmp.valor_estimado`, `valor_homologado`). | Estimado baseado em orçamento apertado; itens tabelados; tabela oficial (ex.: medicamentos CMED) | 1 | Não prova combinação de preços; o preço de referência pode estar correto. | F3·D5÷C1 = 15 → **P1 (apoio)** |
| **N03** | **Prazo de disputa abaixo do mínimo legal.** Hipótese: prazo curto restringe participação. | Dias úteis entre publicação do edital e abertura de propostas < mínimo do art. 55 da Lei 14.133 por tipo de objeto (8 d bens comuns; 10 d serviços/obras comuns; maiores para especiais; A CONFERIR) (PNCP: datas de publicação e abertura). | Erro de data; republicação; modalidades com prazo diferente | 2 (violação objetiva se o tipo estiver certo) | Não prova intenção de favorecer; pode ser erro de preenchimento. | F3·D3÷C2 = 4,5 → **P2** |
| **N04** | **Uso de contratação direta acima dos pares.** Hipótese: órgão que contrata sem licitação em fatia anormal do gasto. | `% do valor` por dispensa/inexigibilidade (R: `contratacao_direta`) ≥ P95 dos órgãos de mesma esfera/porte, com ≥ R$ 5 mi no ano; excluir emergência decretada (`amparo`). | Calamidade; objeto exclusivo (saúde, cultura, inexigibilidade legítima) | 1 | Não prova irregularidade; a lei permite contratação direta em casos listados. | F3·D4÷C1 = 12 → **P1 (contexto + apoio)** |
| **N05** | **Aditivo acima do limite legal.** Hipótese: contrato nasce com valor menor e cresce por aditivos além de 25% (50% em reforma; A CONFERIR). | `valor_global / valor_inicial` entre 1,25 e 20 (hoje descartado como erro) (R). Excluir reajuste/repactuação (não contam para o limite) quando houver tipo de termo (PNCP: termos aditivos, A CONFERIR). | Reajuste; valor global incluir prorrogação; supressão+acréscimo compensados | 2 se houver termos aditivos; 1 se só comparar valores | Não prova burla; o acréscimo pode ter sido justificado ou ser mero reajuste. | F4·D4÷C2 = 8 → **P1** |
| **N06** | **Sobrepreço contra referência.** Hipótese: preço unitário muito acima da mediana de itens equivalentes (TCU/Banco Mundial; OCP). | Preço unitário por item (CATMAT/CATSER) vs mediana móvel 12 meses (Painel de Preços, Banco de Preços em Saúde; PNCP item a item é bloqueado com 503, VERIFICADO em `FONTES.md`: não burlar). Limiar: > 1,5× mediana e ≥ 3 observações. | Especificações diferentes; frete; região; marca; quantidade | 1–2 | Não prova superfaturamento: preço de referência não é o preço certo; a comparação é de itens parecidos. | F4·D2÷C4 = 2 → **P3 (fase de 6 meses)** |
| **N07** | **Rodízio de vencedores / grupos de licitantes.** Hipótese: um conjunto fixo de empresas alterna vitórias no mesmo órgão/objeto (OCDE; Conley & Decarolis). | Com participantes: matriz licitante×licitação; coeficiente de alternância e co-participação. Sem participantes (proxy fraco): ≥ 3 CNPJs que se revezam como vencedores em ≥ 6 compras do mesmo órgão/categoria. | Poucos fornecedores no mercado; licitações por item | 1 | Não prova combinação; mercados concentrados produzem rodízio aparente. | F4·D1÷C4 = 1 → **P3 (depende de dado de licitantes)** |

### 3.2 Rede, empresa e tempo
| ID | Nome / hipótese | Definição operacional e limiar | Falsos positivos | NE | "O que isto não prova" | F·D/C → P |
|---|---|---|---|---|---|---|
| **N08** | **Endereço, telefone ou e-mail compartilhado.** Hipótese: empresas que disputam o mesmo órgão e dividem endereço/contato podem não ser independentes (OCDE, Banco Mundial). | ≥ 2 fornecedores do **mesmo órgão no mesmo ano** com mesmo logradouro+número+CEP **ou** mesmo telefone **ou** mesmo e-mail (RFB: logradouro, número, CEP, ddd/telefone, correio eletrônico). **Remover** e-mails de contabilidade (domínio/e-mail que aparece em > 10 CNPJs) e endereços que abrigam > 20 CNPJs (edifícios, coworking). | Escritórios de contabilidade; prédios comerciais; grupos econômicos legítimos | 1 (2 se ambos disputaram a mesma licitação) | Não prova conluio: empresas vizinhas ou do mesmo contador são comuns. | F4·D4÷C2 = 8 → **P1** |
| **N09** | **Teto de porte superado.** Hipótese: MEI (teto anual de faturamento R$ 81 mil) ou ME/EPP (R$ 4,8 mi) com contratos públicos muito acima do teto. | Soma anual de `valor_global` por CNPJ (R) > 1× teto do porte (RFB/Simples: opção MEI, `porte`; A CONFERIR teto vigente). Limiar: soma anual > R$ 150 mil para MEI; > R$ 4,8 mi para ME/EPP, fora ata/teto. | Valor global é teto/estimativa, não faturamento; contrato plurianual; reenquadramento | 1–2 | Não prova fraude: o valor registrado pode não ter sido faturado e a empresa pode ter sido reenquadrada. | F4·D4÷C1 = 16 → **P1** |
| **N10** | **Empresa nasce depois do edital / mudança societária recente.** Hipótese: empresa aberta ou com sócio novo logo antes de ganhar. | (a) `abertura` (matriz) posterior à data de publicação da licitação (`cmp.publicado`) (R). (b) sócio PF com `data_entrada_sociedade` < 90 dias antes da assinatura (RFB). Valor ≥ R$ 200 mil. | Filial; sucessão; compra de cotas legítima | 2 (a) / 1 (b) | Não prova laranja: empresas nascem para atender chamamentos públicos. | F4·D4÷C1 = 16 → **P1** |
| **N11** | **Fornecedor inapto/baixado/suspenso na data.** | Contrato com `data_assinatura` posterior à `data_situacao_cadastral` de situação 03/04/08 (suspensa, inapta, baixada) (RFB; A CONFERIR; só existe a situação atual: sinal conservador). | Regularização posterior (só situação atual é conhecida); erro no cadastro | 2 | Não prova irregularidade do contrato: a situação pode ter mudado depois; é preciso confirmar na data. | F4·D4÷C1 = 16 → **P1** |
| **N12** | **Contrato assinado antes da homologação / publicado tarde.** | `data_assinatura < homologação` da compra; ou `publicação no PNCP − assinatura > 20 dias úteis` (Lei 14.133 art. 94; A CONFERIR) (PNCP: data de publicação). | Datas inseridas depois; lote retroativo | 2 | Não prova ato ilegal nem ocultação; pode ser atraso de sistema. | F3·D4÷C1 = 12 → **P1 (apoio)** |
| **N13** | **Pagamento acima do contratado / concentrado.** | Soma de pagamentos (PT, favorecido×órgão) > `valor_global` do contrato vinculado; vínculo por documento/número do contrato (A CONFERIR). Limiar: > 110%. | Reajuste; contratos múltiplos; vínculo errado | 2 | Não prova pagamento indevido; reajustes e aditivos explicam diferenças. | F4·D2÷C3 = 2,7 → **P3** |
| **N14** | **Fornecedor com dívida ativa elevada.** | PGFN (`dívida total`) ≥ 10× `capital_social` ou ≥ 50% do valor do contrato, em contrato ≥ R$ 500 mil (PGFN ingerido). Não considerar parcelada/garantida se houver campo. | Dívida discutida judicialmente; parcelamento; grande empresa com dívida administrada | 1 | Não prova inidoneidade; a dívida ativa não impede, por si só, contratar. | F2·D4÷C1 = 8 → **P1 (apenas amplificador)** |
| **N15** | **Sucessora de empresa sancionada.** Hipótese: empresa sancionada em CEIS/CNEP é sucedida por outro CNPJ com o mesmo sócio/endereço (Lei 12.846 art. 14, desconsideração; A CONFERIR). | CNPJ B com `abertura` posterior à `ini` da sanção do CNPJ A **e** ≥ 1 sócio PF (nome+6 dígitos) em comum **ou** mesmo endereço; B contrata dentro da vigência da sanção de A. | Sócio comum em grupos legítimos; homônimo; sanção só de órgão | 1–2 | Não prova burla da sanção: apenas que as empresas têm sócio/endereço em comum. Só pode ser publicado como "coincidência" até confirmação na fonte. | F5·D4÷C2 = 10 → **P1** |
| **N16** | **Entidade cativa (emendas).** | Entidade privada com emendas de ≥ 3 autores distintos ou ≥ 3 anos seguidos e total ≥ R$ 1 mi; combinar com idade, capital, CNAE (R: `n_autores`, `abertura`, `capital_social`). | ONGs reconhecidas com atuação nacional; hospitais | 1 | Não prova desvio: entidades sérias recebem de vários parlamentares. | F3·D5÷C1 = 15 → **P1 (apoio)** |
| **N17** | **Concentração do parlamentar.** | % das emendas individuais de um autor num único favorecido/município ≥ 50% e ≥ R$ 2 mi, por ano; comparar com a distribuição dos pares. | Base eleitoral; saúde de município pequeno | 1 | Não prova troca de favor; direcionamento a uma base é prática política legal. | F2·D5÷C1 = 10 → **P1 (contexto)** |
| **N18** | **Município com emenda desproporcional à capacidade.** | Emenda total no ano / receita total do município (Siconfi FINBRA/RREO; R: `siconfi_entes`) > P95 do estado; e valor per capita > 5× mediana. | Município pequeno com transferência federal rotineira | 1 | Não prova mau uso: capacidade de absorção é uma hipótese. | F2·D4÷C2 = 4 → **P2** |
| **N19** | **Emenda → dispensa → fornecedor recorrente.** | Município recebe pagamento de emenda e contrata, em ≤ 90 dias, com dispensa ou ata, fornecedor que concentra ≥ 40% do período; vínculo pelo objeto (A CONFERIR; dado de vínculo emenda–contrato não é aberto). | Vínculo temporal sem relação causal | 1 | Não prova que o contrato foi pago com a emenda. | F3·D2÷C4 = 1,5 → **P3** |

### 3.3 Pessoas, tempo e contexto
| ID | Nome / hipótese | Definição operacional e limiar | Falsos positivos | NE | "O que isto não prova" | F·D/C → P |
|---|---|---|---|---|---|---|
| **N20** | **Doador de campanha → contrato (extensão de R05).** | Estender: governador/deputado estadual eleito em 2022 × contrato do governo estadual; prefeito 2024 × prefeitura (existente). Razão `contrato / doação`; contrato ≤ 12 meses após a eleição. Exigir frequência de nome baixa ou CPF integral confirmado por TSE. | Empresa fornecedora antiga; doação pequena; homônimo | 1 | Não prova troca de favor: a doação foi legal, e o contrato pode ter sido licitado. | F4·D4÷C2 = 8 → **P1** |
| **N21** | **Grupo oculto que concentra o órgão.** | Componentes conexos de fornecedores ligados por sócio PF (nome+6 dígitos, com filtro de nomes frequentes) ou endereço/e-mail (N08); concentração do **grupo** ≥ 50% do órgão (substitui/complementa R07). | Grupos econômicos legítimos; homônimos | 1 | Não prova combinação: um grupo pode legitimamente ter várias empresas. | F4·D4÷C3 = 5,3 → **P2** |
| **N22** | **Parentesco provável.** | Sócio/administrador com sobrenome **raro** (frequência < 1 em 100 mil) igual ao de agente político/servidor do **mesmo município**, e vínculo funcional com o órgão contratante (TSE candidatos, SIAPE, QSA). **Nunca publicar com nome de PF**; uso interno e para pauta. | Homonímia de sobrenome; famílias numerosas | 0–1 | Não prova parentesco, nem favorecimento. | F3·D3÷C3 = 3 → **P2 (uso interno)** |
| **N23** | **CNAE incompatível com o objeto.** | Classificação do `objeto` (texto → CATMAT/CNAE esperados) vs `cnae` principal e secundários; incompatibilidade em contrato ≥ R$ 300 mil. | CNAE secundário não cadastrado; objeto genérico | 1 | Não prova prestação inexistente: o cadastro pode estar desatualizado. | F3·D3÷C3 = 3 → **P2** |
| **N24** | **Objeto genérico com valor alto.** | Objeto em lista de termos vagos ("serviços diversos", "apoio", "consultoria") ou comprimento < 40 caracteres, valor ≥ R$ 500 mil (R: `objeto`). | Resumo do PNCP truncado | 1 | Não prova direcionamento; descrição vaga pode ser só preenchimento pobre. | F2·D5÷C1 = 10 → **P1 (apoio)** |
| **N25** | **Quarentena de ex-agente.** | Ex-ocupante de cargo de alto escalão (e-Agendas, SIAPE: cargo e data de saída) torna-se sócio/fornecedor do setor regulado ≤ 6 meses após saída (Lei 12.813; A CONFERIR). | Cargos sem impedimento; saída sem acesso a informação privilegiada | 1–2 | Não prova violação: a quarentena depende do cargo e do setor. | F3·D3÷C3 = 3 → **P2** |
| **N26** | **Patrimônio × renda declarados.** | Variação de `bens declarados` (TSE, entre duas eleições) / (remuneração acumulada no cargo) > 5×. Apenas agentes políticos. | Herança; valorização; venda; regime de bens; erro de declaração | 0–1 | Não prova enriquecimento ilícito: bens são declarados ao custo histórico e variam por razões legítimas. **Não publicar como alerta**; só em ficha de contexto. | F2·D4÷C2 = 4 → **P2 (contexto)** |
| **N27** | **Pico de contratos no fim de mandato.** | Valor assinado nos últimos 120 dias do mandato (TSE: eleito, mandato; PNCP) > 2× a média quadrimestral do próprio ente e do grupo de pares (CP art. 359-C, A CONFERIR). | Sazonalidade; obras já licitadas | 1 | Não prova assunção irregular de obrigação: o gasto pode ter sido planejado. | F3·D4÷C2 = 6 → **P2** |

### 3.4 Exterior
| ID | Nome / hipótese | Definição operacional e limiar | Falsos positivos | NE | "O que isto não prova" | F·D/C → P |
|---|---|---|---|---|---|---|
| **N28** | **Cadeia de controle opaca.** | Fornecedor com sócio **PJ** (tipo_socio=1) que por sua vez tem sócio estrangeiro/jurisdição nível 1, ≥ 2 camadas, e **nenhuma PF identificada no QSA** (FATF Rec. 24: beneficiário final) (R: `socios_ext`, `socios_pf`; RFB: tipo de sócio). | Holdings regulares; fundos; estruturas de multinacionais | 1 | Não prova ocultação: o beneficiário final pode estar publicado em outro registro. | F3·D3÷C3 = 3 → **P2** |
| **N29** | **Preço de comércio exterior fora da curva.** | Valor/kg (Comex Stat: FOB, kg, NCM, país) por NCM×país vs. mediana mundial (UN Comtrade; A CONFERIR) e simetria exportação×importação espelho; só **nível país×NCM**, não empresa (MDIC não publica a transação por CNPJ). | Mix de produtos; unidades; câmbio; contêineres | 1 | Não prova sub/superfaturamento nem lavagem: é padrão estatístico agregado; nenhuma empresa é identificada. | F2·D3÷C3 = 2 → **P3 (contexto)** |
| **N30** | **Fluxo para jurisdições de sigilo.** | Participação de exportações/importações com países da lista nível 1 por UF/NCM, em t vs. 3 anos antes (Comex Stat; BCB agregado, A CONFERIR). | Logística; trânsito; commodities por tradings | 1 | Não prova evasão; apenas mostra fluxo agregado incomum. | F2·D3÷C3 = 2 → **P3 (contexto)** |

### 3.5 Ordem de implantação sugerida das novas regras
**P1 com dado já disponível (fazer primeiro):** N02, N04, N05, N09, N10, N11, N12, N14, N16, N17, N20, N24. **P1 que exige ingestão extra:** N08 (colunas de endereço/e-mail do RFB), N15 (QSA + CEIS cruzados), N21. **P2:** N03, N18, N21, N22 (interno), N23, N25, N26, N27, N28. **P3:** N01 e N07 (dependem de licitantes), N06, N13, N19, N29, N30.

---

## 4. Modelo de pontuação, confiança e validação

### 4.1 Princípios
1. **Dois eixos separados, não uma nota única:** **Força do sinal** (quão provável é que o ponto de atenção seja um fato real e relevante para um auditor) e **Materialidade** (quanto dinheiro, quanto do orçamento do ente). Hoje a fórmula soma tudo e `14·log10(valor)` dá ao valor um papel na "força".
2. **Chave do fato gerador.** Cada sinal carrega um `fato_id` (ex.: `sancao:{cnpj}:{id_sancao}`, `socio:{cnpj}:{cpf_hash}`, `concentracao:{orgao}:{ano}`). Regras que descrevem o mesmo fato (R01, R02, R11) contam **uma vez** por entidade/fato.
3. **Famílias de sinais.** Famílias: Jurídica (sanção, inaptidão), Temporal (abertura, entrada de sócio, prazo), Competição (licitantes, desconto), Preço, Rede, Pessoa (PEP, doação, servidor), Exterior, Contexto. **Dentro da família: máximo; entre famílias: soma limitada.** Isso evita que R03+R04 (ambas "pequena e nova") contem como dois sinais independentes.
4. **Âncoras vs. apoios.** Âncora = fato documental (NE2): sanção vigente com alcance, CEPIM, situação inapta, aditivo > limite com termo, pagamento a sancionada. Apoio = estatístico/contextual (NE1): concentração, objeto genérico, desconto ≈ 0. **Apoio não gera "prioridade máxima" sozinho.**
5. **Sem probabilidade ao cidadão até calibrar.** Enquanto não houver rótulos, usar **classes ordinais**. Quando houver, publicar apenas a faixa de precisão da classe, não a "chance de fraude".

### 4.2 Cálculo proposto (versão 1, sem rótulos)
- **Força (0–100):** `F = 100 · (1 − ∏_f (1 − p_f))`, soma "noisy-OR" entre famílias, com `p_f` ordinal inicial por tipo de fato: âncora documental 0,60; estatístico forte 0,30; estatístico moderado 0,15; contexto 0,05; `p_f` da família = máximo dentro dela. (INFERÊNCIA: valores iniciais sem calibração; são apenas uma escala ordinal.)
- **Ajustes de confiança do cruzamento (multiplicativos):** match por CNPJ exato = 1,0; por nome + 6 dígitos de CPF = 0,8, reduzido a 0,5 se o nome estiver entre os mais frequentes; `erro_valor` = 0 (descarta); cobertura PNCP baixa no município = 0,8; sanção com alcance incerto = 0,7.
- **Materialidade (0–3):** M0 < R$ 200 mil; M1 até R$ 1 mi; M2 até R$ 10 mi ou ≥ 1% do orçamento do ente; M3 ≥ R$ 10 mi ou ≥ 5% do orçamento do ente (Siconfi). Usar valor **anualizado** e relativo ao ente (percentil), não `log10(valor)`.
- **Classes (matriz):**

| | M0 | M1 | M2 | M3 |
|---|---|---|---|---|
| **F ≥ 60 e ≥ 1 âncora** | Relevante | **Máxima** | **Máxima** | **Máxima** |
| **40 ≤ F < 60** | Contexto | Relevante | Relevante | **Máxima se ≥ 2 famílias** |
| **20 ≤ F < 40** | Contexto | Contexto | Relevante se ≥ 2 famílias | Relevante |
| **F < 20** | Contexto | Contexto | Contexto | Contexto |

- **Meta de capacidade:** "Máxima" deve ser pequena o suficiente para ser **revisada por humano antes de publicar** (hoje ~3% de 1.581 = ~47 alertas; VERIFICADO em `00_BRIEF.md`). Definir a classe pelo limiar de F **e** por um teto de capacidade (precision@k), não só por limiar absoluto.
- **Explicação ao cidadão:** mostrar os sinais acesos em palavras, não o número: "Acendeu por 3 motivos independentes (A, B, C); o motivo A é um fato documental, os outros são coincidências". Mostrar o que **diminui** o alerta (atenuantes: contrato anterior à eleição, órgão estatal, sanção só de um órgão).
- **Incerteza exposta:** (a) rótulo de **confiança do cruzamento** (Alta/Média/Baixa) separado da prioridade; (b) faixa de classe quando a confirmação mudaria a classe ("Relevante; seria Máxima se a sanção alcançar este órgão"); (c) selo "confirmado em fonte primária em dd/mm/aaaa" (NE2); (d) "dado com limitação" quando há `erro_valor` próximo ou cobertura PNCP parcial.

### 4.3 Calibração com amostras rotuladas
1. **Esquema de rótulos (por alerta):** (A) *Dado correto?* (identidade, data, valor, alcance verificados na fonte primária): sim/não/indeterminado. (B) *Atenção justificada?* (um auditor abriria verificação): sim/não. (C) *Explicação benigna encontrada?* (tipo: erro de dado, homônimo, ente estatal, atividade autorizada, outro). (D) *Desfecho posterior* (quando observável: sanção posterior, operação, decisão de tribunal de contas).
2. **Amostragem estratificada** por regra × classe × esfera. Para estimar precisão com margem de ±10 pontos em 95% (pior caso p = 0,5), são necessários ≈ 96 alertas por célula; com ±15 pontos, ≈ 43. Para regras raras (R01, R11, N15) revisar **100%**. Usar intervalo de Wilson.
3. **Dois revisores independentes** em 20% da amostra; meta de concordância kappa ≥ 0,6; divergências decididas por terceiro.
4. **Métricas:** precisão A (qualidade do dado) por regra, precisão B por regra e classe, precision@k da lista "Máxima", taxa de **erro de identidade** (homônimo) por regra de nome+CPF parcial, taxa de benignos por tipo, **sobreposição entre regras** (Jaccard) para detectar dupla contagem.
5. **Revalidação temporal (backtest):** com os dados de data t0, medir se entidades marcadas têm mais chance de desfecho (D) em t0+12 meses que o grupo de controle pareado (mesmo órgão, categoria, porte). Cuidado: o desfecho é censurado e enviesado (só se vê o que se fiscaliza). Usar como indicador, não como verdade.
6. **Calibração:** com ≥ 200 rótulos por regra, ajustar por regra um calibrador monotônico (isotônico ou beta-binomial por classe). Com poucos rótulos, manter as classes ordinais e publicar só o intervalo de precisão por classe (agregado).
7. **Meta de qualidade por classe antes de publicar com destaque:** precisão A ≥ 95% (identidade e fato); precisão B da "Máxima" ≥ 70% (meta provisória, INFERÊNCIA); regra com precisão B < 30% numa classe sobe de "alerta" para "contexto" ou sai.
8. **Congelar definições:** cada regra tem versão semântica (ex.: `R03@2.1`), SQL com hash, parâmetros em arquivo versionado, **janela de congelamento trimestral** (mudanças só entre janelas, exceto correção de erro), `CHANGELOG` público, e conjunto de avaliação travado (amostra rotulada de um trimestre não é usada para ajustar a regra que ela avalia). Cada alerta publicado guarda `regra@versão` e data dos dados.
9. **Revisão periódica:** reavaliar precisão por regra a cada trimestre (n mínimo 43 por regra principal); regra em queda de precisão > 10 pontos entra em revisão; publicar "relatório de qualidade" resumido na página de metodologia.

---

## 5. Padrão de evidência e linguagem

### 5.1 Níveis de evidência e o que a ficha mostra
| Nível | Definição | Exemplos | O que a ficha mostra | Rótulo ao leitor |
|---|---|---|---|---|
| **NE0** Contexto | Dado público sem relação direta com irregularidade | Valor/kg fora da curva agregado; fluxo para paraíso (N29/N30) | Dado, fonte, gráfico, limites | "Contexto" |
| **NE1** Coincidência | Cruzamento de dados que pode ter explicação benigna | Mesmo endereço (N08), sócio com nome+6 dígitos (R10/R12), proposta única | Fonte de cada dado; **critério** que acendeu; **o que foi descartado**; "o que isto não prova"; link direto à fonte primária; confiança do cruzamento | "Coincidência de dados" |
| **NE2** Fato documental | Fato verificável em fonte oficial e datado | Sanção vigente (R02), CEPIM, pagamento (R11), situação inapta | Tudo do NE1 **mais** captura do registro (data de acesso), alcance jurídico e o raciocínio da data | "Fato registrado na fonte" |
| **NE3** Decisão de órgão competente | Existe decisão (TCU, CGU, tribunal de contas, Justiça) | Acórdão, sanção administrativa, sentença | Número e link da decisão, status (recorrível?), resumo neutro, contraditório | "Há decisão de [órgão]" |

**Regras de ficha (todas):** (1) título **descritivo e neutro** (não "fraude", "esquema", "irregular"); (2) frase de uma linha com o fato ("O pagamento de R$ X ocorreu em mm/aaaa; nesse mês, a empresa constava no CEIS com sanção que alcança a União"); (3) **por que acendeu** com cada critério; (4) **o que foi descartado**; (5) **O que isto não prova** (texto específico, não genérico); (6) **fonte com link e data de acesso**; (7) **possíveis explicações benignas**; (8) **como contestar/corrigir** (e-mail e prazo de resposta); (9) versão da regra e data dos dados.

### 5.2 Redação (para não afirmar culpa)
| Evitar | Usar |
|---|---|
| "Empresa fraudou", "esquema", "laranja", "propina", "desvio" | "coincidência", "ponto de atenção", "dado a verificar" |
| "A empresa é de fachada" | "A empresa tem endereço em comum com X; o cadastro não mostra funcionários (dado não disponível)" |
| "Político X é dono de empresa" | "O nome e 6 dígitos do CPF de X coincidem com um sócio; pode ser homônimo" (sempre que o cruzamento for parcial) |
| Voz ativa que atribui intenção ("favoreceu", "escondeu") | Voz neutra e temporal ("o contrato foi assinado 12 dias após…") |
| Superlativos e adjetivos de risco | Números com fonte; comparação com pares |
| Dizer "alerta de corrupção" | "Alerta" = "ponto de atenção" (conforme `REGRAS.md`) |

Regras adicionais: sempre incluir **denominador/comparação** ("1 de 120 contratos do órgão"); nunca usar mapas de calor ou rankings que sugiram culpa de pessoa; separar **fato** (data, valor, fonte) de **interpretação** (marcada como hipótese); **corrigir** em ≤ 5 dias úteis quando houver erro comprovado, com nota de correção visível.

### 5.3 Quando um sinal pode ser publicado com nome de pessoa física
Critérios cumulativos (todos):
1. **Função pública** ou **dado de transparência ativa** ligado ao exercício do cargo (eleito, ocupante de cargo, servidor com remuneração publicada) — conforme regra 3 do briefing. Pessoa privada (sócio, doador comum) **nunca** é nomeada: usa-se "sócio da empresa" ou iniciais.
2. **Identidade confirmada:** CPF completo em fonte primária (TSE, portal), **não** só nome + 6 dígitos; se só há match parcial, publicar como "coincidência de nome" sem afirmar identidade, ou não publicar.
3. **Fato NE2 ou NE3** (não NE1) para destaque; NE1 só em ficha de contexto sem prioridade máxima.
4. **Relevância pública** do sinal (cargo, contrato, ente em que atua) e **materialidade** (≥ M1).
5. **Revisão humana** de um segundo revisor antes de publicar; registro da revisão.
6. **Canal de resposta** e prazo; **linguagem neutra** (5.2); **mascarar CPF**.
7. Nunca publicar sinais baseados em parentesco presumido (N22), patrimônio × renda (N26) ou sócio sem função pública com nome.
8. Retirada ou correção imediata se o titular comprovar erro (homônimo, saída da sociedade, decisão judicial).
Observação (INFERÊNCIA, A CONFERIR com assessoria jurídica): a LGPD admite tratamento de dados públicos, mas exige finalidade, necessidade e proporcionalidade; recomendo parecer jurídico sobre o fluxo acima.

---

## 6. Roadmap

| Fase | Entregas | Dependências de dados | Critério de aceite |
|---|---|---|---|
| **2 semanas** | (1) Separar **força × materialidade** e implantar a **chave do fato gerador** (agrupa R01/R02/R11, R03/R04, R06/R07) sem mudar o SQL; (2) corrigir **R03** para usar abertura da matriz; (3) revisar **R06** (limites por tipo, ano e objeto); (4) **penalidade por frequência de nome** em R05/R10/R12; (5) novas regras que usam dado já ingerido: **N02, N04, N05, N09 (se `opção MEI` existe), N12, N24**; (6) modelo de **ficha** NE0–NE3 e texto de "não prova" por regra; (7) planilha de **rótulos** (100 alertas, 2 revisores) para R02, R03, R05, R10; (8) **congelar** versões `regra@versão` e CHANGELOG. | Nenhum dado novo (usa `pncp`, `compras`, `ceis`, `tse_*`, `socios_pf`) | Relatório inicial de precisão A/B por regra; duplicatas por fato eliminadas; mudança de contagem de "Máxima" documentada |
| **2 meses** | (1) Ingerir colunas de endereço/telefone/e-mail e `data_entrada_sociedade`, `data_situacao_cadastral`, opção MEI/Simples do RFB (A CONFERIR); (2) **N08, N10, N11, N15, N21** (rede e tempo); (3) **N16, N17, N18** (emendas; Siconfi) ; (4) **N20** (doação estendida a governador/deputados 2022); (5) calibração por regra com ≥ 200 rótulos e relatório de qualidade; (6) **R02** com checagem de Poder; **RF01** separado em "monitor de risco financeiro"; (7) backtest de desfechos (sanções posteriores). | Receita (reprocessar `cnpj.py`), TSE 2022/2024, Siconfi (FINBRA/RREO), CEIS | Precisão B da "Máxima" ≥ meta; kappa ≥ 0,6; N08 com filtro de contabilidade validado em amostra |
| **6 meses** | (1) **Licitantes/participantes**: ComprasGov/PNCP resultado, atas, e TCEs com dados abertos → **N01, N07**, rodízio e desistências; (2) **N03** (prazo) e **N06** (preço) com itens (CATMAT/CATSER) e bases de preço de referência; (3) **N13** (pagamento × contrato) com Portal da Transparência e vínculo; (4) **N25** (quarentena), **N27** (fim de mandato), **N28** (cadeia opaca); (5) **Tribunais de Contas estaduais e portais municipais** (lacunas de `00_BRIEF.md`); (6) **N29/N30** como camada de contexto; (7) auditoria externa da metodologia (acadêmico/CGU/TCU) e publicação do relatório de qualidade trimestral. | Dado de licitantes (maior risco: PNCP bloqueia item a item; usar rota oficial/LAI/API), TCEs, ObrasGov, UN Comtrade | Revisão externa feita; congelamento trimestral em operação; ≥ 3 regras de competição/rede validadas com rótulos |

### Riscos e decisões que o cliente precisa tomar
1. **Colocar a "Máxima" sob revisão humana obrigatória** antes de publicar (custo: tempo semanal).
2. **Retirar o bônus de 45 pontos e o `PESO_R` manual** em favor do modelo de famílias; aceitar que a contagem de "alertas" caia.
3. **Parecer jurídico** sobre publicação com nome de PF e sobre o canal de contestação.
4. **Priorizar N01/N07 (licitantes)** como investimento de dados: é o sinal de maior poder discriminatório na literatura (proposta única), mas depende de coleta que hoje está bloqueada item a item no PNCP.
5. **Verificar as lacunas A CONFERIR** (limites legais de dispensa e prazos; colunas da Receita; fontes TCU/CGU) antes de publicar regras novas.
