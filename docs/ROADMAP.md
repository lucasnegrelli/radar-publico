# Roadmap (estado em 03/11/2026)

Legenda: ✅ feito · 🟡 parcial · ⬜ a fazer

## Cobertura de dados
| Item | Estado | Observação |
|---|---|---|
| Contratos PNCP (federal, estadual, municipal) | ✅ | semanal |
| Licitações (modalidade, valores) | ✅ | cruza com contratos e derruba valor incoerente |
| Emendas (R09) e por cidade | ✅ | aba Cidade |
| Pagamentos federais a sancionadas (R11) | ✅ | |
| Servidor federal × fornecedor (R12) | ✅ | cadastro SIAPE |
| TSE 2014–2026 (candidaturas, patrimônio, campanha) | ✅ | patrimônio com série e variação |
| Câmara: foto, projetos, comissões, frentes | ✅ | |
| Senado: projetos, comissões, votos | ✅ | |
| Offshore Leaks, OFAC e União Europeia (por nome, a confirmar) | ✅ | poucas coincidências, de propósito |
| Casos com fonte | 🟡 | 38; seguir adicionando |
| Votações nominais da Câmara por deputado | ✅ | arquivos abertos 2023+; alinhamento com a orientação do Governo na ficha |
| Quadro de assessores da Câmara e do Senado | ⬜ | arquivos próprios das Casas |
| Remuneração de servidores (teto, acúmulo) | ✅ | lista de conferência, não alerta: teto inferido dos dados, bruta+abate acima dele (`remuneracao.py`) |
| Tribunais de Contas estaduais | ⬜ | começar por SP, RJ, MG, PE (dados abertos em lote) |
| Portais de transparência municipais | ⬜ | via TCE e Querido Diário primeiro |
| Folha estadual e municipal | ⬜ | depende dos TCEs |
| Licitação por dentro (participantes, propostas) | ⬜ | PNCP bloqueia item a item (503): coletar **devagar, em várias rodadas e pela rota oficial**, sem driblar o bloqueio |
| Outros países (ONU, registros de empresas) | 🟡 | UE já entra; ONU: URL consolidada deu 404, rever |

## Produto
| Item | Estado |
|---|---|
| Filtros por esfera, poder, estado e valor | ✅ |
| Aba Investigar (empresas, rede de ligações, trilha, link compartilhável) | ✅ |
| Glossário clicável e boas-vindas | ✅ |
| Layout para celular | ✅ (testar em aparelho real) |
| Tabela filtrável com exportação (CSV, Excel, Parquet) | 🟡 (CSV existe; falta Excel/Parquet e colunas escolhidas) |
| API documentada e dicionário de campos | ⬜ |
| Alertas pessoais (aviso quando algo muda) | ⬜ |
| Página de metodologia por regra dentro do site | ⬜ (texto está em `docs/REGRAS.md`) |
| Recalibrar prioridade (hoje 63% são "alta") | ⬜ depois da cobertura |
| Página de status das fontes | ⬜ |
| Cards para redes sociais | 🟡 pausado: refinar o impacto visual |

## Princípio de ordem
Primeiro **cobertura**, depois **calibração** (limiares dependem da distribuição dos dados), depois **polimento**.
