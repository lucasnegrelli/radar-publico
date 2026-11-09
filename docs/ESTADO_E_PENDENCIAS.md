# Radar Público: o que foi feito, o que está no ar e o que ficou pendente

Registro de passagem de bastão em **08/11/2026** (fim do dia). Para retomar amanhã com uma direção nova do cliente.

## 1. Em uma página
- **Produto:** monitor do dinheiro público do Brasil, em `https://radar.lucasnegrelli.com`, repositório `C:\Users\lucas\Desktop\Negrelli\GitHub\radar-publico`, branch `main`.
- **Rumo:** a sessão foi se espalhando (muitas fontes, muitas abas, várias tentativas de visual). O cliente pediu para parar e redefinir a direção amanhã. **A síntese da pesquisa da equipe está em `docs/pesquisa/08_SINTESE.md`** e é o melhor ponto de partida.
- **Achado mais importante:** a auditoria de 60 alertas mostrou que só **32%** merecem atenção de verdade (10% falsos positivos; "prioridade máxima" 50%). **Credibilidade vem antes de qualquer tela nova.** Há dado duplicado por junção em 38% dos alertas R02.
- **Os "12 trilhões" são o PIB.** O gasto público é outro número (LOA 2026: R$ 6,54 tri, dos quais R$ 1,8 tri é rolagem da dívida). O Radar vê ~R$ 1,5 tri em compras.

## 2. O que está NO AR (conferido hoje)
- `radar.lucasnegrelli.com` com o painel completo: tela inicial (busca, manchete do dia, "por que importa"), alertas em camadas (máxima ~3%, relevante ~18%, contexto), painel direito interativo, menu de 7 itens (Hoje, Cidade, Pessoas, Empresas, Dinheiro, Casos, Ajuda), sub-abas (Salários, Agenda dos ministros, Viagens, Comércio exterior; Investigações, Notícias, Justiça; Como ler, Fontes).
- `/v2/`: protótipo novo em Vue com a "faixa da coincidência" (cordel/xilogravura). **Está em teste e não é aprovado pelo cliente.**
- Dados no ar: alertas, comex, salários, agenda, viagens, leniência, PGFN, Banco Central, notícias e apurações. **Ainda não no ar: `cartoes.json` (404)**; a coleta dos cartões corporativos roda à noite e a agregação depende do cache.
- Último workflow "Atualização leve diária" (20:38 UTC) **falhou**; o site continuou com a publicação anterior.

## 3. O que foi feito nesta sessão (por tema)
**Dados e fontes novas**
- Viagens ao exterior do Executivo (Portal da Transparência): 10.114 viagens, nomes só de cargos de direção (`ingestao/viagens_servico.py`).
- Ranking de remunerações (Justiça/MP via DadosJusBr, Executivo via SIAPE), rubricas ("penduricalhos") por tipo, fotos de ministros da Wikipédia (`ingestao/remuneracoes.py`).
- Agenda de ministros (e-Agendas/CGU), 49 autoridades, ~961 compromissos (`ingestao/eagendas.py`).
- API do Portal da Transparência: cliente com limite de taxa, acordos de leniência (57), expulsões CEAF (280) (`portal_api.py`, `portal_fontes.py`).
- Cartões corporativos (CPGF): coleta noturna retomável (`portal_cartoes.py`, workflow `portal-noturno.yml`).
- PGFN dívida ativa (`pgfn.py` + workflow mensal `pgfn-mensal.yml`), regimes especiais do Banco Central (`bcb_regimes.py`), Comex Stat (`comex.py`).
- Notícias com valor extraídas automaticamente por regras (`casos_noticias.py`) e apurações de veículos investigativos (`apuracoes.py`).
- Ajustes de R09/R11 (feitos pela outra janela): gravidade pelo contrato novo na punição.
**Painel**
- Redesenho da tela única, painel direito interativo, menu enxuto com sub-abas, filtros em sanfona nos Salários, Agenda/Justiça interativas, camadas do mapa, tela inicial com busca e "por que importa", alertas em camadas (credibilidade), correção do pop-up no celular.
**Pesquisa (equipe de 7)**: `docs/pesquisa/00` a `08` (design, ecossistema, metodologia, fontes, jurídico, auditoria, arquitetura, síntese).

## 4. O que ficou PENDENTE
**Decisões do cliente (não tomadas)**
1. Congelar novos recursos até a fase de credibilidade acabar?
2. Remover a **data de nascimento** (campo `nasc`) do JSON público de pessoas?
3. Trocar a meta "os 12 trilhões" por "o que o Radar enxerga do gasto público"?
4. Escolher o território visual (recomendado: Sobreposição) e fazer teste com 6 a 8 pessoas.
5. Estrutura jurídica (associação sem fins lucrativos recomendada) e revisão por advogado.
**Correções de credibilidade (da auditoria 06 e metodologia 03)**: dado duplicado por junção (R02 38%, R05 21%, R08 27%); usar a data de registro da sanção, não só o início; R03 filial vs empresa nova; R09 "empresa nova" por pagamento antigo; R10 ignora fim do mandato; R01 aceita sanção de um único órgão; R04 sem dividir pelo prazo; R04 e R08 com 0 acertos (rebaixar ou remover); atualizar a faixa da R06 (limites de dispensa mudaram em 2026, Decreto 12.807/2025); ajustar o texto da R12 (servidor pode ser sócio cotista); pontuação conta em dobro (R01/R02/R11); placar de qualidade público.
**Técnico**: JS de 1,72 MB; pipeline frágil (risco financeiro quebrou por mudança do BC; janela futura do PNCP falha; timeouts do Pages; cron atrasa horas); sem URL por entidade; falta CSP e foco por teclado; o CNPJ vem de espelho de terceiro; id de pessoa de 32 bits com risco de colisão.
**Produto/dados (roadmap)**: Meu município, "Pergunte ao órgão" (pedido de LAI), fichas com URL permanente e imagem para WhatsApp; Siconfi, TransfereGov, TCE-SP/PE/RS, dados de licitantes; quadro de assessores; agenda do presidente; viagens do Senado/Judiciário; FGC e CNJ improbidade sem fonte aberta; TCU só por CNPJ.
**Segredos e acessos**: `EAGENDAS_TOKEN`, `PORTAL_TOKEN`, `HF_TOKEN` existem no GitHub. A chave `PORTAL_TOKEN` apareceu em texto na conversa (considerar gerar outra). `ANTHROPIC_API_KEY` não foi criada (opcional, para extrair títulos de notícias).
**Em aberto no repositório**: `stash@{0}` guarda JSONs gerados pela outra janela (R09/R11); a pasta `docs/pesquisa` está commitada; o protótipo `web/v2` ainda importa fontes do cordel.

## 5. Sugestão de primeiro passo amanhã
Ler `docs/pesquisa/08_SINTESE.md` (5 min), decidir as 5 perguntas acima e começar pela **Fase 1 (credibilidade e segurança)**, que protege o produto antes de qualquer visual.
