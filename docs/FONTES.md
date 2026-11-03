# Catálogo de fontes

Tudo é dado aberto. Colunas: **Fonte** · **O que usamos** · **Script** · **Atualização** · **Limites**.

## Dinheiro e contratos
| Fonte | Uso | Script | Atualização | Limites |
|---|---|---|---|---|
| PNCP (contratos) | todos os contratos de órgãos federais, estaduais e municipais desde 2025 | `pncp_janela.py`, `pncp.yml` | semanal | valores digitados errados na origem (filtros `erro_valor`); consulta item a item é bloqueada com 503: **não** burlar |
| PNCP (licitações) | modalidade, valor estimado e homologado | `pncp_compras_janela.py` | semanal | cobre licitações publicadas desde 2025-01 |
| Portal da Transparência: emendas | autor, favorecido (CNPJ), valor pago | `emendas.py`, `municipios.py` | semanal | bancadas e comissões não têm autor individual |
| Portal da Transparência: pagamentos por favorecido | todo pagamento federal a empresas, 12 meses | `despesas_federais.py` | mensal | o portal às vezes não responde: o script mantém o resultado anterior |
| Cota parlamentar (Câmara, Senado) | notas de gasto por parlamentar | `baixar.py`, `atualizar_fontes.py` | diária | — |
| SICONFI | população e finanças de entes | `siconfi.py` | manual | — |

## Pessoas e eleições
| Fonte | Uso | Script |
|---|---|---|
| TSE candidaturas, bens, receitas e despesas (2014 a 2026) | fichas de pessoa, patrimônio, doadores, fornecedores | `tse_historico.py`, `pessoas.py` |
| Câmara dos Deputados (API) | foto, projetos, comissões, frentes | `camara_atividade.py` |
| Senado (API) | foto, projetos de autoria, comissões, votos nominais | `senado_atividade.py` |
| SIAPE (servidores federais) | R12 | `servidores.py` |
| ICIJ Offshore Leaks | coincidência de nome (confirmar) | `offshore.py` |
| OFAC (lista SDN, EUA) | coincidência de nome (confirmar) | `ofac.py` |

## Empresas
| Fonte | Uso | Script |
|---|---|---|
| Receita Federal (CNPJ: empresas, estabelecimentos, sócios) | cadastro, quadro societário, cruzamentos por nome + 6 dígitos do CPF | `cnpj.py`, `empresas.py` |
| CEIS, CNEP, CEPIM, acordos de leniência | sanções e impedimentos | `atualizar_fontes.py` |
| Banco Central IF.data | balanço de bancos (RF01) | `bcb_ifdata.py` |
| CVM (carteira de fundos, FIDC) | quem segura papel de banco; FIDC com RPPS | `risco_*.py`, `fidc.py` |

## Contexto e notícias
Querido Diário (diários municipais), Google Notícias (RSS), DataJud (CNJ), Wikipédia (resumo CC BY-SA).

## Ainda não coberto (ver `ROADMAP.md`)
Tribunais de Contas estaduais, portais municipais, folha de pagamento estadual e municipal, licitação por dentro (participantes), quadro de assessores, votações da Câmara por parlamentar.

## Regra de ouro de coleta
Identificar-se com `User-Agent` honesto, respeitar limites, repetir com pausa e nunca disfarçar o cliente nem driblar bloqueio. Quando uma fonte bloqueia, o caminho é coletar **mais devagar e em várias rodadas**, usar a rota oficial (API com chave, arquivo em lote) ou pedir por Lei de Acesso à Informação.
