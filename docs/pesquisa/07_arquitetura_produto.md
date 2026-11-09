# 07 · Arquitetura e produto: auditoria técnica, arquitetura-alvo e roadmap

Radar Público · 08/11/2026 · Autoria: arquitetura de software e produto mobile (pesquisa para o Radar Público)

Convenção (briefing): **VERIFICADO** = vi ou medi nesta sessão; **FONTE** = afirmado por fonte citada; **INFERÊNCIA** = meu raciocínio. Não alterei código; o build (`npx vite build`) regenerou `web/dist`, que está fora do git. Não rodei Lighthouse nem `npm audit` (o segundo envia a lista de pacotes ao registro npm; a regra do briefing diz para não enviar dados a terceiros).

---

## 0. Resumo executivo

1. A base técnica **funciona e é barata**, mas o front do painel atual é pesado demais para celular (JS de 1,72 MB, 484 KB gzip; 1,4 a 1,5 MB comprimidos antes de qualquer pixel útil) e **não tem URL por entidade** (tudo em `#hash`), o que impede compartilhar, indexar e gerar imagem de compartilhamento.
2. O pipeline é o ponto mais frágil: **publica 158 MB por força (`git push -f` no `gh-pages`)**, o deploy do Pages já estourou o tempo limite duas vezes, os agendamentos atrasam de 4 a 8 horas, muitas etapas têm `|| true` (falha silenciosa = dado velho no ar) e só existe **um teste** de 23 linhas.
3. **Recomendação: opção (b)**, estático + índice de busca no cliente + API mínima na borda (Cloudflare Pages/Workers/R2), com dados em **Parquet particionado no R2** e JSON enxuto por entidade. Custo estimado de US$ 0 a 5 por mês até dezenas de milhares de visitantes. Postgres (opção c) só se aparecerem contas de usuário ou consultas ad hoc pesadas.
4. Front: **ficar em Vue 3 (já usado em `web/v2`)**, migrando o painel por rotas e não por reescrita total; mapa MapLibre carregado sob demanda, com mapa SVG leve no celular.
5. App: **PWA primeiro (fase 1)**, depois **Capacitor** para as lojas (fase 3) só se os dados de retorno justificarem. Push no iOS exige PWA instalada na tela inicial.

---

## 1. Auditoria do que existe

### 1.1 Inventário (VERIFICADO)

| Item | Medida |
|---|---|
| `web/main.js` | 1.352 linhas, 188.287 bytes (linhas muito longas: média ~139 bytes/linha; o briefing dizia ~1.600 linhas) |
| `web/investigar.js` / `pessoa.js` / `glossario.js` | 132 / 127 / 81 linhas |
| `web/style.css` | 606 linhas, 67.268 bytes (157 KB após o build, 38 KB gzip) |
| `web/v2/` | Vue 3: `App.vue` + 3 componentes + `style.css` + `textos.js`, ~27 KB de código-fonte |
| `ingestao/` | 70+ scripts Python, ~4.400 linhas; `alertas/*.sql` 9 arquivos |
| Testes | `ingestao/testes/test_deteccao_casos.py`, 23 linhas, **1 caso** (Banco Master), depende de `dados/bcb/*.parquet` locais |
| Workflows | 9 arquivos (`atualizar`, `atualizar-leve`, `pncp`, `compras`, `portal-noturno`, `cnpj-mensal`, `pgfn-mensal`, `diarios`, `caso`) |
| Repositório | público; `git count-objects`: pack de 177 MiB; `gh repo view`: 51 MB no GitHub |

### 1.2 Tamanho do que o navegador baixa (VERIFICADO: `npx vite build` em `web/`, 10,8 s; `gzip -9` nos JSON)

**JS/CSS do painel atual**

| Arquivo | Bruto | gzip |
|---|---|---|
| `assets/main-B0tpFSIB.js` (MapLibre + deck.gl + app) | 1.722,41 KB | **483,74 KB** |
| `assets/main-DLWO3tOW.css` | 157,15 KB | 38,39 KB |
| chunks do deck.gl (`webgl-device`, `arithmetic-expression`, `array-utils-flat`, `buffer-transform`…) | ~220 KB | ~70 KB |
| `assets/v2-CuMcVWSC.js` (Vue + v2) | 89,27 KB | 35,46 KB |
| `assets/v2-BRekJeh1.css` | 23,20 KB | 4,20 KB |

O Vite avisou: *"Some chunks are larger than 500 kB after minification"*. Não há `import()` dinâmico: o bundle único traz MapLibre e deck.gl mesmo para quem só quer ver uma lista.

**JSON carregados na abertura** (`web/main.js:876-881`, dentro de um `await Promise.all` de **nível superior**, ou seja, **nada é renderizado antes de todos chegarem**):

| Arquivo | Bruto | gzip |
|---|---|---|
| `alertas.json` | 4.926.462 B (4,9 MB) | 525.652 B |
| `mundo.geojson` | 838.726 B | 209.290 B |
| `uf.geojson` | 98.502 B | 28.058 B |
| `diarios.json` | 98.361 B | ~30 KB (estimativa) |
| `noticias.json`, `risco.json` | 22.633 B + 5.871 B | <10 KB |
| `pgfn.json` (busca assíncrona em `main.js:181`) | 728.058 B | 290.607 B |
| `casos.json`, `leniencia.json`, `bcb_regimes.json`, `noticias_alertas.json`, `escala.json` (`main.js:166-188, 1230-1231`) | ~0,5 MB | ~0,25 MB |

**Fontes (painel atual, `main.js:1-4`):** Inter variável (latin 48,3 KB + latin-ext 85,1 KB sob demanda), Space Grotesk variável (latin 22,3 KB), JetBrains Mono 400 e 500 (21,2 + 21,8 KB). Cerca de 114 KB no caminho típico. A v2 importa IBM Plex Sans 400/500/600 + Plex Mono 400/500/600 + Londrina Solid 400/900 (~180 KB no latin). `package.json` ainda lista `fraunces`, `archivo`, `instrument-serif`, `barlow-condensed` sem uso que eu encontrasse nos arquivos de estilo ou de entrada: dependência morta.

**Tudo o que está em `web/public/data/` (e portanto dentro de `dist`)**: 146 MB (`du -sh`): `pessoas/` 87 MB (258 arquivos), `empresas/` 49 MB (101 arquivos), JSON de topo ~11,9 MB, `cards/` 7,4 MB. `web/dist` inteiro = **158 MB**.

**Estimativa de carga em 4G lento (INFERÊNCIA, não medida):** caminho crítico da abertura ≈ 484 + 70 (JS) + 38 (CSS) + 526 + 209 + 28 + ~50 (JSON) + ~114 (fontes) ≈ **1,5 MB**. No perfil de 1,6 Mb/s e 150 ms de latência do Lighthouse móvel, só a transferência leva ~7 a 8 s; somada ao parse de 1,7 MB de JS num aparelho de entrada (CPU 4x mais lenta), e sem render antes do `await` de topo, espero **LCP entre 9 e 14 s e TTI acima de 10 s**. Meta realista para a arquitetura-alvo: LCP < 2,5 s com ≤ 150 KB na primeira tela. **Precisa ser confirmado com Lighthouse/WebPageTest num Moto G de verdade antes de qualquer promessa.**

Contexto relevante: o GitHub Pages serve gzip, não brotli (INFERÊNCIA, conhecimento geral; conferir). Brotli reduziria ~15 a 20% os JSON.

### 1.3 Dívida técnica do front (VERIFICADO)

- **Monólito**: `main.js` mistura carga de dados, mapa, 14 abas, glossário, paleta de busca e regras de pontuação (`pontuar`, reclassificação por percentil em `main.js:884-889`) no mesmo arquivo. Variáveis globais de módulo (`alertas`, `visiveis`, `_pessoas`, `_cx`, `_ag`, `_rem`, `_exec`…) fazem o papel de estado.
- **Templates em string**: 41 usos de `innerHTML` em `main.js`, 7 em `investigar.js`, 3 em `pessoa.js`, 2 em `glossario.js`. Estilo inline abundante (`style="color:#4cc9f0"`, `main.js:589`).
- **Regra de negócio no cliente**: a gravidade que o usuário vê **não é a do pipeline**. O navegador recalcula `score` e redistribui `alta/media/baixa` por percentil (`main.js:884-889`; 3% e 18% fixos). Resultado: o mesmo alerta pode mudar de gravidade conforme o conjunto carregado, e a v2 duplica a lógica em `v2/textos.js` (`pontuar`). **Fonte única de verdade deve ser o pipeline**, com a explicação do score gravada no dado.
- **Roteamento por hash frágil**: `main.js:925` abre ficha 1,8 s depois da carga (`setTimeout(..., 1800)`), formatos `#p-<id>`, `#e-<id>`, `#inv=…`. Não há `history.pushState`, não há URL canônica por entidade, e o `404.html` é cópia do `index.html` (`publicar-pages.sh`), o que devolve status 404 para qualquer rota.
- **Sem estado de erro real**: ~25 `fetch(...).catch(() => null)` engolem falhas e mostram "Dados ainda não carregados".
- **Duas interfaces em paralelo** (painel atual + `v2`) no mesmo build, sem compartilhar componentes nem tokens.
- **Texto de domínio espalhado**: manchetes, explicações e "o que isto não prova" escritos em JS (`main.js`, `v2/textos.js`) em vez de fazerem parte do dado versionado. Isso bloqueia i18n e auditoria editorial.

### 1.4 Acessibilidade (WCAG 2.2 AA) (VERIFICADO por leitura de código; sem teste com leitor de tela)

| Critério | Achado | Evidência |
|---|---|---|
| 2.4.7 Foco visível | **Zero** `:focus-visible` e **10 `outline:none`** em `style.css`; campos só mudam a cor da borda (`style.css:35,154,236,317,445-446,544,551,566`). Em `web/v2/style.css` também 0 `:focus-visible`. | grep |
| 2.3.3 / movimento | **Zero** `prefers-reduced-motion`, apesar de radar girando, animação `entra`, blur, ticker. | grep |
| 1.4.3 Contraste | Texto secundário `--mut #7a8da3` sobre `#070b11` = **5,79:1**, sobre `#111925` = 5,18:1 (passa AA). Passa nos números que calculei; **mas** há dezenas de regras com 9,5 a 11,5 px (`style.css:19,31,51,56`; 28 ocorrências de `font-size:9` ou `10`), o que falha a legibilidade mesmo com contraste ok. | cálculo + grep |
| 1.4.1 Cor como único indicador | Gravidade comunicada principalmente por cor (`--alta #ff2d55`, `--media`, `--baixa`); há texto, mas a barra de severidade (`hm-sev`) é só cor. | `main.js:1070` |
| 4.1.2 / 1.3.1 Nome, papel, valor | Só 4 `aria-*` em `main.js`, 0 `role=`/`tabindex`. Cartões de alerta são `<li>` com `onclick` (`main.js:362`): **não focáveis nem acionáveis por teclado**. Abas são `<button>` sem `role="tab"`, sem `aria-selected`. Painéis `#detalhe` não gerenciam foco ao abrir/fechar, sem `aria-live`. | `main.js:355-362` |
| 2.5.8 Alvo de toque (24 px mínimo no 2.2; 44 px recomendado) | Chips de filtro com `padding:4px 11px; font-size:12px` (~26 px de altura) (`style.css:36`); botões de aba 62 px (ok) mas `.sub` menores; `×` de fechar sem área definida; campos de 32 a 36 px. | `style.css:36,154,445` |
| Mapa | Canvas WebGL sem alternativa textual; a informação existe na lista, o que ajuda. | `main.js:144` |
| Estrutura | `<main id="centro">` existe, mas **não há `<h1>`**; `lang="pt-BR"` presente (bom); `viewport` sem `user-scalable=no` (bom). | `index.html` |
| Tema | Só escuro no painel; v2 declara `theme-color` claro, sem `prefers-color-scheme` (grep 0). | grep |

### 1.5 Segurança (VERIFICADO)

- **Segredos:** nenhum token no código; só `os.environ`/`.env` e `${{ secrets.* }}` (`HF_TOKEN`, `EAGENDAS_TOKEN`, `PORTAL_TOKEN`). `.env` está no `.gitignore`; `.env.example` só tem nomes. `git ls-files | grep .env` lista apenas `.env.example`. Não abri nenhum `.env` real. Bom.
- **Superfície**: `ingestao/casos_noticias.py` menciona `ANTHROPIC_API_KEY` opcional (gancho para LLM): se for ligado, os resumos viram dado gerado por modelo e precisam de marca "gerado automaticamente" e revisão (princípio de nunca afirmar culpa).
- **XSS por `innerHTML`:** existe função `esc` (`main.js:21`) e a maior parte dos campos de **texto livre vindos de fora** (títulos de notícia, trechos de diário, nomes) passa por ela, inclusive `href="${esc(n.url)}"` (11 ocorrências). Achados sem escape, por linha:
  - `main.js:355-362`: `RNOME[a.regra] || a.regra` e `a.local.uf` entram sem `esc`; `a.regra`/`uf` vêm do pipeline (confiável hoje), mas a cadeia **depende de o pipeline nunca emitir `<`**. Risco baixo, fragilidade alta.
  - `main.js:844`: `data-sub="${k}"`, `${l}` sem `esc` (constantes internas).
  - `main.js:589, 478`: `style="--r:${...}"` e cores interpoladas; `corCat(v.c)` depende do dado.
  - `main.js:1257`: legenda e lista de cards vêm de `cards/index.json`.
  - **`href` com `esc` não bloqueia `javascript:`**: `esc` escapa `& < > "` mas não valida o esquema. URLs de notícias/diários vêm de RSS e de API de terceiros (`main.js:622, 782, 1297`). Um item com `javascript:` ou `data:` executaria no clique. **Correção:** função `urlSegura()` que aceita só `https:`/`http:`. Gravidade média por ser conteúdo de terceiros externos (Google Notícias RSS, Querido Diário).
  - `investigar.js:102-123`: nota do usuário passa por `esc`; `${r[2]}` (município) e `r[0]` (id) entram sem `esc`, vindos de `idx.json` do pipeline.
  - **Importação de investigação por link** (`#inv=…`, `importaDoHash`, `main.js:925`): conteúdo vindo de um link de terceiros é desserializado e renderizado; os nomes passam por `esc`, mas vale fuzz e limite de tamanho. Principal vetor realista de XSS no produto hoje.
- **CSP:** nenhuma (`index.html` sem `<meta http-equiv="Content-Security-Policy">`). O GitHub Pages não permite cabeçalhos. Com Cloudflare Pages dá para usar `_headers` (CSP, `Referrer-Policy`, `X-Content-Type-Options`, `Permissions-Policy`).
- **Terceiros em runtime:** `glyphs: "https://demotiles.maplibre.org/font/..."` (`main.js:144`): requisição a terceiro por usuário (vaza IP/UA ao projeto MapLibre, depende de serviço de demonstração, ponto único de falha). Fontes são auto-hospedadas (bom). Trocar por glifos próprios ou remover rótulos do mapa.
- **Dependências:** `vue ^3.5.45`, `maplibre-gl ^5.0.0`, `deck.gl ^9.4.1`, `vite ^6.4.4`; `package-lock.json` presente e `npm ci` no CI (bom). `npm audit` não executado (ver nota inicial). Os runners avisam: *"Node.js 20 is deprecated... forced to run on Node.js 24"* (logs de 04/11 e 08/11): atualizar `actions/*` e `node-version`.
- **Privacidade (dado):** o JSON de pessoa expõe **data de nascimento completa** (`"nasc":"29/03/1960"`, `web/public/data/pessoas/s16.json`), ocupação e bens de **candidatos não eleitos** (inclusive de pessoas sem função pública atual). É dado aberto do TSE, mas a regra de ouro 3 diz "nome de pessoa só quando função pública e dado de transparência ativa". **Risco LGPD/reputacional: remover `nasc` do JSON publicado (usar só idade ou ano), e decidir política para candidatos que nunca exerceram cargo.** O id da pessoa usa o nascimento na chave (`pessoas.py:41-42`), então o dado fica no pipeline, não no site.
- **Colisão de id (INFERÊNCIA com cálculo):** `pid = sha1(chave)[:8]` (`pessoas.py:42`): 32 bits. Com **44.710 pessoas** (VERIFICADO em `idx.json`), a chance de pelo menos uma colisão é 1 - exp(-n²/2·2³²) ≈ **21%**. Duas pessoas fundidas numa ficha seria erro grave em produto de reputação. Usar ao menos 64 bits e checar unicidade no pipeline (falhar o build se houver colisão).
- **Homônimos:** a chave é nome normalizado + nascimento, ou `?UF` quando falta data (`pessoas.py:41`): homônimos sem data na mesma UF viram **a mesma pessoa**. Precisa de marca de "identidade provável" no dado.

### 1.6 Confiabilidade do pipeline (VERIFICADO com `gh run list`, 08/11/2026)

**Estrutura:** a rodada completa (`atualizar.yml`, 150 linhas, timeout 355 min) baixa ~7 GB do Hugging Face (dataset **privado**, `propagang/radar-publico-dados`), roda ~35 etapas em série num único job e publica. A leve (`atualizar-leve.yml`) baixa **do site em produção** o dado atual, atualiza notícias/diários/casos e republica. Ambas compartilham `concurrency: atualizar` com `cancel-in-progress: false`.

**Falhas observadas nos logs:**

1. **Execução completa de 04/11 01:03 UTC:** `risco_financeiro.py` linha 16 → `BinderException: Referenced column "CodInst" not found` (o JSON/Parquet do BCB mudou de formato). Falha em cadeia nas execuções de 03/11 e 04/11 (6 falhas `failure` entre 03/11 18:04 e 04/11 00:29). Etapas "não críticas" usam `|| true`, mas **`risco_financeiro.py` não** tem, e derrubou a rodada completa.
2. **`PNCP em massa` de 08/11 10:37 UTC:** a janela **`2026-11-16_2026-11-30` (futura, hoje é 08/11)** falha com `falhou a primeira página`, e como o job tem `fail-fast:false` só aquela janela falha, mas a **execução inteira fica vermelha**. O planejador (`pncp_pendentes.py`, `DE` = hoje-2 meses a `ATE` = mês atual) gera janelas quinzenais do mês inteiro, incluindo dias futuros. Bug trivial, ruído permanente que mascara falhas reais.
3. **`pages-build-deployment` falhou em 04/11 21:26 e 06/11 16:13**: log `##[error]Timeout reached, aborting!` (deploy de ~158 MB). Resultado: o site **fica no estado anterior** sem alerta algum. Cada rodada que passa publica sozinha de novo, mas não há verificação.
4. **Cancelamentos em cascata** (04/11 15:25 a 19:48, 6 `cancelled`) e `leve` de 08/11 20:23 e 20:33 cancelados: o grupo `atualizar` enfileira, e disparos manuais repetidos se atropelam; a execução em andamento nunca é cancelada, mas as pendentes sim (o GitHub mantém só 1 pendente por grupo).
5. **Atrasos de agendamento (VERIFICADO):** a `leve` está marcada para 08:17 UTC (05:17 em Brasília) e começou em **14:53 (07/11), 15:54 (06/11), 16:27 (05/11)**, isto é, **6 a 8 h depois**; a completa marcada para domingo 14:17 UTC começou às **18:52**. O `cron` do GitHub é "melhor esforço" e tem atraso conhecido em horários cheios/concorridos. O texto em `docs/ARQUITETURA.md` ("05:17 em Brasília") **não é verdade na prática**: o usuário vê dado "de ontem" até o início da tarde.
6. **Só um agendamento da completa registrado:** `gh run list --event schedule` para `atualizar.yml` retorna apenas a de 08/11; as anteriores foram manuais (`workflow_dispatch`). Não consegui confirmar se a de 01/11 falhou em disparar (INFERÊNCIA: o agendamento só vale a partir do commit que o habilitou/branch padrão).

**Pontos de falha e riscos de dado velho ou quebrado no ar:**

- **Sem porta de qualidade antes de publicar**: o único guarda é `test -s alertas.json` na leve. Não há validação de esquema, de contagem (ex.: "alertas não pode cair >30% sem aprovação"), nem de datas. Uma rodada completa que "passe" com `|| true` nas fontes publica um site silenciosamente incompleto.
- **Circularidade da leve:** ela baixa do site no ar e republica; se o dado no ar estiver corrompido, ela o perpetua e o espalha.
- **`git push -f` do `gh-pages` com 158 MB todo dia** (`publicar-pages.sh`): histórico órfão novo a cada deploy; 4 tentativas com backoff. Cresce o armazenamento do repositório (INFERÊNCIA) e é a causa provável dos timeouts de deploy.
- **Ponto único de falha de dados**: dataset privado no Hugging Face com token; sem espelho. Se a conta for suspensa ou o token expirar, a rodada completa **não baixa nada**.
- **Etapa única de ~35 passos em série**, timeout de 355 min (limite do GitHub é 360 min por job em runner hospedado, FONTE: documentação GitHub Actions, conhecimento geral; conferir). Falha tardia perde tudo (não há artefatos intermediários exceto cache de `portal` e `pessoas_extras`).
- **Execução em andamento hoje** (`42512176388`) está em "Pessoas mais conhecidas (Wikipédia e manchetes)" → "Montar o site" → "Publicar": ~1h30 em curso, coerente com os "~50 min" da documentação ficarem desatualizados.
- **Segredos de terceiros**: `PORTAL_TOKEN` limita 300 req/min só de 00h às 05h59 BRT; o coletor noturno é frágil, mas bem desenhado (retomável, cache).

**Custo (VERIFICADO/INFERÊNCIA):** repositório público ⇒ GitHub Actions e Pages **gratuitos** (FONTE: política do GitHub para repositórios públicos, conhecimento geral; conferir). Hugging Face privado: custo US$ 0 no plano gratuito até o limite (INFERÊNCIA; conferir cota de dataset privado). Domínio: único custo fixo. **Custo mensal hoje ≈ domínio.**

### 1.7 Testabilidade (VERIFICADO)

- 1 teste, local, não roda no CI, depende de arquivo em `dados/`.
- Regras R01-R12 (SQL em `alertas/*.sql` + lógica em `exportar_web.py`, 202 linhas; `pessoas.py` 314 linhas) **sem nenhum teste unitário**; nenhum teste de contrato do JSON (`alertas.json` é consumido por 3 interfaces).
- Sem testes de front, sem teste de acessibilidade automatizado, sem verificação do build no CI antes de publicar (o `vite build` é o próprio passo de publicação).
- Dado de verdade por regra: casos conhecidos (`casos/*.json`, 38) são um **ótimo conjunto de ouro** subaproveitado para testar regressão de detectores.

### 1.8 Estado dos dados e o que "70 mil pessoas" significa (VERIFICADO)

`pessoas/idx.json`: **44.710** pessoas (4,2 MB bruto, 1,16 MB gzip); `empresas/idx.json`: **84.292** empresas (6,2 MB bruto, 1,99 MB gzip). `meta.json`: PNCP 3.701.858 linhas; cota da Câmara 795.503 linhas; TSE doações 2024 2.041.048 linhas. Os 70 mil+ citados na missão não aparecem hoje no índice; tratar 44,7 mil pessoas e 84 mil empresas como linha de base, com folga para 10x.

O índice de busca atual baixa **o índice inteiro** (1,2 MB e 2,0 MB gzip) na primeira busca (`main.js:420, 1006`, `investigar.js`). Em 4G lento, só isso são ~6 a 10 s antes do primeiro resultado (INFERÊNCIA a partir de 3,2 MB ⇒ 1,6 Mb/s).

---

## 2. Arquitetura-alvo

### 2.1 Comparação das três opções

| Critério | (a) Estático + JSON evoluído | (b) Estático + índice no cliente + API leve na borda | (c) Backend Postgres/DuckDB + API |
|---|---|---|---|
| Custo mensal (INFERÊNCIA, preços de 08/11/2026) | US$ 0 a 1 (Pages/Cloudflare Pages + domínio) | US$ 0 a 5. R2: US$ 0,015/GB-mês, 10 GB grátis, egress grátis, 1 M ops A e 10 M ops B grátis (FONTE: developers.cloudflare.com/r2/pricing, acesso 08/11/2026). Workers: grátis até 100 mil req/dia, pago US$ 5/mês com 10 M req (FONTE: developers.cloudflare.com/workers/platform/pricing, acesso 08/11/2026). | US$ 25 a 150 (Postgres gerenciado + API + backups) e crescendo com tráfego e réplicas |
| Complexidade (1 pessoa) | Baixa | Média | Alta (migração, segurança, operação 24/7, DDoS, scraping) |
| Latência (primeira resposta) | Boa se fatiar; ruim com índices de 2 MB | Boa: ~20 a 80 KB por consulta, da borda, em cache | Boa mas depende de região; Brasil: latência de nuvem estrangeira 150-250 ms |
| Busca nome/CNPJ em 44k a 100k+ pessoas e milhões de contratos | Prefixo em shards JSON funciona para nome; contratos exigem pré-agregar tudo | CNPJ exato = arquivo por prefixo/hash; nome = índice fatiado (Pagefind ou MiniSearch por shard); contratos = Parquet por empresa lido via range | Melhor flexibilidade (ILIKE, trigramas, `pg_trgm`), mas você paga por isso |
| Privacidade do visitante | Excelente (nada de consulta no servidor) | Excelente: buscas locais; a API só vê o prefixo/hash pedido | Servidor vê cada consulta (LGPD: a busca por pessoa é dado sensível reputacional); logs viram passivo |
| Escalar para outros países | Cada país = novo build gigante | Cada país = pasta/partição própria no R2, um índice por país, mesma API | Esquema único multitenant, mais fácil em tese, mais caro e arriscado |
| Risco de abuso / scraping | Baixo | Médio (limite de taxa no Worker) | Alto |
| Dados desatualizados no ar | Igual ao atual | Atualizações atômicas por versão (`manifest.json`), rollback = trocar ponteiro | Atomicidade fácil, mas migrações complicam |

### 2.2 Recomendação: **(b)**, em duas etapas

**Etapa 1 (fases de 2 semanas e 2 meses), sem API:** tirar o que é pesado de `dist` e do `git push -f`.
- Hospedagem estática no **Cloudflare Pages** (ou manter Pages só para o shell) e **dados no Cloudflare R2** (ou no próprio Pages, mas fora do `gh-pages` forçado). O site passa a ter ~2 MB de shell; os 146 MB de dados vão para R2 com cabeçalhos de cache imutáveis (`/dados/v2026-11-08/...`).
- **Busca:** Pagefind para o texto (páginas de entidade pré-renderizadas) ou índice próprio por prefixo (`b/ab.json` com 2 letras; cada shard 20 a 60 KB). CNPJ: hash do CNPJ-base de 8 dígitos → `empresas/<h2>/<base>.json`. Meta: a primeira resposta chega com ≤ 1 requisição pequena.
- **Sem backend ainda.**

**Etapa 2 (6 meses):** adicionar **uma API mínima em Worker** só onde estático não resolve: (i) busca difusa/fonética de nome com índice em D1/KV; (ii) `og:image` por URL; (iii) registro de inscrições para alertas (push/e-mail); (iv) consultas de contrato por empresa lendo **Parquet por HTTP range** do R2 (DuckDB-WASM no cliente ou lido no Worker). Reavaliar (c) apenas se houver conta de usuário, investigações colaborativas ou SLA contratado.

**Por que não (a) puro:** os índices de 3,2 MB gzip e a ausência de URL por entidade matam desempenho e compartilhamento. **Por que não (c):** custo e operação desproporcionais para 1 pessoa; a busca por nome vira registro de interesse sobre pessoas (risco de privacidade); e DuckDB roda hoje no CI sem servidor.

**Alternativas de busca no cliente, comparadas (INFERÊNCIA; não medi cada uma):**

| Opção | Quando usar | Observação |
|---|---|---|
| Pagefind (índice estático fatiado, carrega só os pedaços) | Páginas de entidade pré-renderizadas, busca por texto | Menor atrito; suporta pt-BR; carrega fragmentos por consulta |
| MiniSearch / FlexSearch em shards por prefixo | Nome de pessoa/empresa com autocomplete | ~100 a 300 KB por shard dá resposta rápida em memória |
| SQLite-WASM com `sqlite-wasm-http` (range) | Consultas estruturadas com índices B-tree | ~1 MB de WASM; bom para "contratos da empresa X" |
| DuckDB-WASM + Parquet por range | Análises, filtros por valor/data/município | ~8 a 10 MB de WASM: **só sob demanda, nunca na primeira tela** |

### 2.3 Formato dos dados

- **Camada bruta/canônica** (pipeline, privada): Parquet particionado `fonte=/ano=/mes=` com `zstd`, como já no HF (`pncp/`, `compras/`, `tse/`, `cnpj/`).
- **Camada pública (R2):** 
  - `dados/<versão>/manifest.json` (lista de arquivos, tamanhos, `sha256`, data de geração, esquema, contagens, frescor por fonte);
  - `entidade/<tipo>/<h2>/<id>.json` (**um arquivo por entidade**, 3 a 40 KB, brotli): empresa, pessoa, órgão, município, alerta;
  - `indice/busca/<prefixo>.json` e `indice/cnpj/<h2>.json`;
  - `agregados/uf/<UF>.json`, `agregados/municipio/<ibge>.json` (o mapa e a página "minha cidade");
  - `contratos/empresa=<base8>/part.parquet` (somente quando a DuckDB-WASM for usada).
- **JSON vs Parquet vs protobuf:** JSON enxuto (chaves curtas, tabelas em arrays, como o `idx.json` atual) para a leitura direta no celular; Parquet para análise e download aberto; **protobuf não compensa** para 1 pessoa (ferramental) frente a brotli em JSON. MessagePack é um meio-termo, só se medir ganho. 
- **Versionamento:** `manifest.json` pequeno e **sem cache longo** apontando para a pasta imutável `v2026-11-08/`; rollback = reverter o ponteiro. O Service Worker usa o manifesto para invalidar.
- **Linhagem de cada número (hoje não existe campo padronizado):** cada fato no JSON ganha um objeto `fonte`:
  ```json
  {"v": 1234.5, "fonte": {"id": "pncp", "arquivo": "pncp/2026-10-16_2026-10-31.parquet",
    "linha": 88213, "url": "https://pncp.gov.br/app/contratos/...",
    "coletado_em": "2026-11-08", "publicado_em": "2026-10-29", "regra": "R03@v4"}}
  ```
  Hoje o alerta tem `visto_em` e URLs nas células de tabela (ex.: `"u":"https://www.camara.leg.br/cota-parlamentar/nota-fiscal-eletronica?ideDocumentoFiscal=8148201"` em `alertas.json`), mas **o hash do arquivo e a versão da regra não vão ao dado**. Recomendado: `regra@versao`, `sha256` do Parquet de origem e `commit` do pipeline em `meta.json`; mostrar "de onde vem este número" em cada valor do front (já tem "o que isto não prova"; falta "de onde vem").
- **Esquema único de alerta (contrato de dados):** JSON Schema versionado (`schemas/alerta.v1.json`) validado no CI. Campos: `id`, `regra`, `regra_versao`, `severidade` (calculada no pipeline), `score` e `score_explicacao[]`, `entidades[]` (`tipo`, `id`), `valor`, `periodo`, `fontes[]`, `nao_prova` (texto), `local` (IBGE), `pais`.

### 2.4 Uma página por entidade, URL estável e compartilhável

| Entidade | URL | Chave estável |
|---|---|---|
| Empresa | `/br/empresa/<cnpj-base8>` (+ `?filial=`) | CNPJ-base (público, estável) |
| Pessoa | `/br/pessoa/<id64>-<slug>` | id de 64 bits, slug só cosmético; redireciona se o slug mudar |
| Órgão | `/br/orgao/<cnpj-ou-UASG>` | UASG/CNPJ do órgão |
| Cidade | `/br/cidade/<ibge7>-<slug>` | código IBGE |
| Alerta | `/br/alerta/<regra>-<id>` | já existe `R01-00870827000318` |
| Caso | `/br/caso/<slug>` | `casos/*.json` |
| País (futuro) | `/<iso2>/...` | ISO 3166-1 alfa-2 |

Regras: **URL por caminho (não hash)**, um ID **nunca reutilizado**, páginas aposentadas respondem `410` com explicação, versão de dado no rodapé ("dados de 02/11/2026"), canonical, data de última atualização visível.

### 2.5 SEO e imagem de compartilhamento

- **Pré-renderização estática** das entidades mais acessadas (top ~5.000 por empresas/pessoas com alerta + 5.570 cidades + alertas "prioridade máxima") a cada rodada; as demais via **Worker com cache** que injeta `<title>`, `<meta description>`, `og:*` e JSON-LD no shell (SSR leve, sem framework). Tamanho: um HTML de ~6 KB por entidade.
- **`og:image` por URL:** Worker com **`workers-og`/Satori + resvg-wasm** (SVG→PNG 1200×630) a partir do JSON da entidade, cacheado no CDN; fallback: PNG pré-gerado no pipeline para as 500 principais (já há `ingestao/cards.py` usando Pillow e fontes TTF em `ingestao/fontes/`). Conteúdo do cartão: nome, número principal, a faixa de coincidência, fonte e data. **Nunca o veredito.** Para pessoa: não mostrar foto automaticamente.
- **Atenção editorial:** a imagem de compartilhamento de uma pessoa é o ponto de maior risco reputacional; precisa do selo "ponto de atenção, não prova" e da fonte no próprio cartão.
- `sitemap.xml` por tipo, `robots.txt`, `lastmod`. **Decisão:** `noindex` em fichas de **pessoas sem função pública atual** (candidatos não eleitos antigos) e em alertas de baixa gravidade, para não criar "ranking de nomes" no Google.

### 2.6 Internacionalização e múltiplos países

- **i18n de interface:** extrair os textos de `main.js`/`v2/textos.js` para catálogos (`i18n/pt-BR.json`, `en.json`, `es.json`) com ICU MessageFormat (plural, moeda, data). Biblioteca: `vue-i18n` (lazy-load por idioma) ou `Intl` puro com catálogo próprio (menor).
- **Textos de regra como dado:** cada regra tem `id`, `titulo`, `explica`, `nao_prova`, `criterio` por idioma em `regras/R03.pt-BR.md` versionado. Isso resolve auditoria editorial e tradução.
- **Modelo de dados multi-país:** `jurisdicao` (`BR`, `BR-SP`, `BR-SP-3550308`), `entidade` com `id_local` + `esquema_id` (CNPJ, CPF-mascarado, EIN, NIT, Companies House number, **Open Contracting `ocid`**, **Popolo/Open Ownership BODS** para beneficiário final). Padrões a adotar: **OCDS** para contratação e **BODS** para propriedade (FONTE: standard.open-contracting.org e standard.openownership.org; **não abri**; conferir antes de adotar). Cada país é um conjunto de adaptadores `ingestao/<pais>/` que emitem o esquema canônico; as **regras** devem ser escritas sobre o esquema canônico, não sobre colunas do PNCP.
- **Moeda:** guardar valor na moeda original + data de câmbio (BCB/FX) para comparação; nunca somar moedas sem conversão marcada.
- **Dados pesados por país:** partição `pais=br/` no R2, uma pasta de manifesto por país; o shell é único.

---

## 3. Front-end

### 3.1 Stack: recomendação

| Opção | Tamanho base (INFERÊNCIA, números típicos publicados, não medidos aqui) | Prós | Contras para este caso |
|---|---|---|---|
| **Vue 3** (já em `web/v2`) | ~35 KB gzip (v2 atual: 35,5 KB gzip total incluindo app) | Já usado; SFC com CSS escopado; ótimo para quem sai de templates em string; `vue-i18n`, `vue-router` e `vite` maduros | Menor ecossistema de dataviz que React |
| Svelte 5 / SvelteKit | ~5 a 10 KB runtime | Menor bundle; prerender e adaptador estático embutidos (ótimo para SEO por entidade) | Troca de stack do único dev; menos libs de mapa |
| React | ~45 KB gzip | Maior ecossistema (deck.gl e libs de dataviz com binding oficial) | Mais peso, mais boilerplate |
| Solid | ~7 KB | Desempenho | Ecossistema pequeno |
| Vanilla + web components | 0 KB | Sem dependência | Custo de manutenção de componentes, sem roteamento/i18n prontos |

**Decisão: Vue 3 + Vite + `vue-router` + `vite-ssg` (pré-renderização) + Pinia só se o estado crescer.** Razões: (1) **a v2 já existe** e foi gasto esforço de direção de arte nela; (2) o dev é um só: trocar de framework custa 2 a 4 pessoas-semana sem ganho para o usuário; (3) o gargalo do app **não é o framework** (35 KB), é MapLibre/deck.gl (≈ 480 KB gzip) e os 1,5 MB de dados na abertura; (4) `vite-ssg` resolve SEO estático. **Se** o time puder pagar a troca e SEO/peso forem prioridade absoluta, SvelteKit é a alternativa mais forte; **não recomendo agora**.

### 3.2 Estrutura de pastas proposta

```
web/
  src/
    app/            # shell, router, i18n, service worker registration
    tokens/         # tokens.css (cor, tipo, espaço, raio, sombra, movimento), gerado de tokens.json
    components/     # Atomic: Valor, Selo, FaixaCoincidencia, Fonte, NaoProva, Cartao, Lista, Tabela
    features/
      alerta/ empresa/ pessoa/ cidade/ orgao/ caso/ busca/ mapa/
    data/           # cliente de dados: manifest, cache, shards, validação de schema
    lib/            # formatadores (brl, data), urlSegura(), escapes, utilitários
    i18n/           # pt-BR.json, en.json
  public/           # manifest.webmanifest, ícones, robots
  tests/            # vitest + playwright + axe
schemas/            # JSON Schemas versionados (alerta, entidade, manifest)
```

### 3.3 Design tokens

Fonte única `tokens.json` → CSS custom properties (e, depois, Swift/Kotlin se for nativo). Grupos: `color.{bg,fg,muted,line,sev.max,sev.rel,sev.ctx,link,focus}`, `type.{family,size,lh,weight}`, `space.{1..9}`, `radius`, `elevation`, `motion.{dur,ease,reduced}`, `z`. **Regras mínimas:** foco visível com contraste ≥ 3:1 sobre qualquer fundo; tamanho mínimo de texto 14 px (corpo 16 px no celular); severidade sempre cor + texto + forma; `prefers-reduced-motion` e `prefers-color-scheme` desde o dia 1. A direção de arte final (briefing: ainda não aprovada) entra **só como valores de tokens e componentes visuais**; a arquitetura não depende dela.

### 3.4 Roteamento e estado

- `vue-router` em modo **history**, rotas do item 2.4, com rotas carregadas sob demanda (`() => import(...)`). Cloudflare Pages: `_redirects` para fallback de SPA com **status 200** nas rotas de entidade e **404 real** para IDs que não existem.
- Estado: dados são **somente leitura**; cache em memória + `Cache Storage` por URL imutável; estado de UI na URL (`?q=`, `?uf=`, `?gravidade=`) para que todo filtro seja compartilhável. Preferências em `localStorage`. Sem global mutável.
- Os gráficos e o mapa recebem **dados já agregados** do pipeline (nunca 4,9 MB de alertas para desenhar 27 estados).

### 3.5 Estratégia de mapas

- **Celular/primeira tela: SVG leve** (`uf.geojson` simplificado a ~20 KB; hoje 98,5 KB bruto/28 KB gzip; municípios por arquivo por UF sob demanda), sem WebGL, tocável com área de toque ≥ 44 px, com lista equivalente (acessível).
- **MapLibre + deck.gl só onde precisa** (painel "explorar", arcos de comércio exterior, heatmap): `import()` dinâmico ao entrar na rota, **nunca no shell**. Meta: bundle de mapa isolado (~480 KB gzip hoje) só para quem abre o mapa.
- Trocar `demotiles.maplibre.org` por glifos próprios ou eliminar rótulos de texto no mapa (`main.js:144`). Mapa-múndi: simplificar `mundo.geojson` (839 KB) para ≤ 120 KB com `mapshaper -simplify` e usar TopoJSON.
- Alternativa para cidade: `<svg>` por município gerado no pipeline (cartograma), 2 a 8 KB.

### 3.6 Tipografia web

- Hoje: 3 famílias no painel (Inter var, Space Grotesk var, JetBrains Mono 400/500) ⇒ ~114 KB; v2: Plex Sans ×3 + Plex Mono ×3 + Londrina ×2 ⇒ ~180 KB no latin. Há 4 famílias instaladas e não usadas.
- Meta: **≤ 2 famílias e ≤ 3 arquivos WOFF2 (≤ 80 KB total)**, só subconjunto `latin` + `latin-ext` sob demanda (`unicode-range`), `font-display: swap` com `size-adjust` na fonte de reserva, `<link rel=preload>` só do arquivo do corpo. Fonte variável (um arquivo) é mais barata que três pesos estáticos. O que a direção de arte escolher (Plex Sans/Mono é compatível com a direção "séria e cortante") precisa caber nesse orçamento.
- Remover do `package.json` as quatro dependências de fonte não usadas e os `.woff` de reserva (os 45 `.woff` somam 527 KB em `dist`, não baixados pelos navegadores modernos).

### 3.7 Offline e cache

- Service Worker (Workbox ou manual ≤ 150 linhas): **pré-cache do shell** (~150 KB), `stale-while-revalidate` para `manifest.json`, `cache-first` para arquivos imutáveis versionados, `network-first` com *timeout* de 3 s para entidade. "Minha cidade" e as últimas 20 entidades vistas ficam disponíveis offline, com selo **"dados de <data>, você está offline"**.
- Orçamento de armazenamento: ≤ 30 MB (iOS limpa o cache de sites sem uso por ~7 dias, FONTE: WebKit, "Full Third-Party Cookie Blocking and More", webkit.org/blog/10218; **não reabri**; conferir).

---

## 4. Aplicativo

### 4.1 PWA (fase 1)

- `manifest.webmanifest` (nome, `short_name`, `start_url: "/?utm=pwa"`, `display: standalone`, ícones 192/512 + **maskable**, `theme_color`, `shortcuts`: "Minha cidade", "Buscar", "Hoje"), `id` estável, capturas de tela.
- Service Worker conforme 3.7. Instalável no Android/Chrome com *prompt* próprio após a 2ª visita (nunca no primeiro acesso). `share_target` para receber links.
- **Push Web:** Android/Chrome funciona; **iOS/iPadOS 16.4+ só funciona se o site foi adicionado à Tela de Início** e com permissão pedida por gesto (FONTE: WebKit, "Web Push for Web Apps on iOS and iPadOS", webkit.org/blog/13878; **não reabri**; conferir). Isso reduz muito o alcance no iOS.

### 4.2 O que o PWA não faz bem no iOS (INFERÊNCIA a partir de conhecimento do ecossistema; conferir antes de decidir)

- Push só após instalar na Tela de Início; sem *badge* confiável em todas as versões; sem *background sync* ou *periodic sync*; cache pode ser removido após semanas sem uso; sem listagem na App Store (descoberta); *deep links* de Universal Link não abrem o PWA instalado como em app nativo; widgets de Tela de Início e Live Activities só nativos; compartilhamento *para dentro* do app é limitado.

### 4.3 PWA vs Capacitor vs Tauri vs Expo vs Flutter

| Caminho | Reuso do código web | Esforço | Quando usar |
|---|---|---|---|
| **PWA** | 100% | Baixo (1 a 2 sem) | **Fase 1**, sempre |
| **Capacitor** (WebView + plugins: push FCM/APNs, share, deep link, widget via plugin/extensão nativa) | ~95% | Médio (4 a 6 sem + conta de loja) | **Fase 3**, se retenção e push exigirem a loja |
| Tauri 2 (mobile) | Alto | Médio-alto, mobile ainda mais novo que o desktop (INFERÊNCIA) | Não: o ganho é desktop |
| Expo/React Native | Baixo (reescrita) | Alto | Só se virar produto nativo de verdade |
| Flutter | Zero | Alto | Não |

### 4.4 Plano de lojas e recursos nativos

- **Google Play:** TWA (Bubblewrap) ou Capacitor; conta de desenvolvedor (taxa única de US$ 25, FONTE: Google Play Console, conhecimento geral; conferir); política de dados/privacidade; declarar ausência de coleta de dados pessoais; contas novas pessoais precisam de período de teste fechado (INFERÊNCIA, regra recente; conferir).
- **App Store:** conta (US$ 99/ano, conferir); a revisão **exige funcionalidade além de "site embrulhado"** (diretriz 4.2): push, compartilhar, widget e leitura offline justificam. Prever 1 a 3 rodadas de revisão. Conteúdo que afirma coisas sobre pessoas exige política clara (diretriz de conteúdo gerado/difamatório): o "o que isto não prova" ajuda.
- **Notificações ("novo sinal na sua cidade")**: assinatura por `ibge` (e por empresa/pessoa seguida) guardada **no aparelho**; o Worker envia pelo tópico FCM/APNs/Web Push `cidade-<ibge7>` quando o `manifest.json` novo tiver alerta novo naquele município. **Privacidade:** o servidor só sabe "um token está no tópico X", sem identidade. Limite de 1 push/dia, janelas de silêncio e só alertas de gravidade alta ou relevante, para respeitar o "se tudo é alerta, nada é alerta".
- **Compartilhamento nativo:** `navigator.share({title, text, url})` com URL de entidade e `og:image` (item 2.5); texto padrão: "Ponto de atenção (não é prova): …".
- **Deep links:** `https://radar.lucasnegrelli.com/br/...` com `assetlinks.json` (Android App Links) e `apple-app-site-association` (iOS Universal Links) servidos em `/.well-known/`. A decisão de URL por caminho (2.4) é pré-requisito.
- **Widgets:** só no nativo (Android Glance/AppWidget, iOS WidgetKit via extensão Swift em projeto Capacitor): "Alertas na sua cidade" com valor e data. **Fase 3 e opcional.**

### 4.5 Caminho por fase

1. **Fase 1 (2 semanas):** manifest, ícones, Service Worker de shell, `share_target`, rotas por caminho.
2. **Fase 2 (2 meses):** offline de "minha cidade", push web (Android + iOS instalado), URLs por entidade com `og:image`.
3. **Fase 3 (6 meses), **condicionada a métrica**:** Capacitor se, após 2 meses, (i) ≥ 10 a 15% das sessões forem PWA instalada e (ii) a assinatura de alertas por cidade tiver retenção D30 relevante. Senão, ficar no PWA.

---

## 5. Analytics e privacidade

- **Ferramenta:** **Plausible** (hospedada, ~US$ 9/mês para 10k visualizações, FONTE: plausible.io/#pricing, conhecimento geral; **não reabri**; conferir) ou **Umami** auto-hospedado (grátis; roda em um Worker/Postgres pequeno ou gratuito no Fly/Neon, a escolher). Sem cookies, sem ID persistente, sem IP armazenado: **dispensa banner de consentimento** na prática (INFERÊNCIA; confirmar com advogado LGPD). Evitar GA4 e SDKs de terceiros no app.
- **Nunca** enviar o **termo buscado** (nome de pessoa/empresa) ao analytics: registrar apenas `busca_enviada`, `resultado_n` (faixa) e `resultado_clicado: sim/não`. O nome buscado é dado sensível.
- **Eventos do produto:**
  | Métrica | Definição |
  |---|---|
  | Tempo até a primeira resposta | `performance.now()` da navegação até o primeiro conteúdo útil (lista ou resultado); alvo p75 < 2,5 s em 4G |
  | Busca bem-sucedida | busca com clique em resultado em ≤ 30 s |
  | Abandono de busca | busca sem clique |
  | Compartilhamentos | `share_click` por tipo de entidade e canal |
  | Retorno | visitantes recorrentes (D7/D30) via Plausible/Umami; no PWA, `launch` instalado |
  | Profundidade | páginas por sessão, "de onde vem este número" clicado, "o que isto não prova" aberto |
  | Qualidade percebida | "isso foi útil?" opcional (sim/não) por alerta, sem texto livre |
  | Web Vitals reais | `web-vitals` enviando LCP/INP/CLS para o mesmo coletor (p75, por tipo de aparelho) |
- **Observabilidade do pipeline:**
  - `status.json` público e página **/status** (a tarefa já está no `ROADMAP.md` como ⬜): para cada fonte, `ultima_coleta`, `ultimo_dado`, `linhas`, `esperado_ate`, `estado` (`ok`/`atrasada`/`falhou`), e o que faltou. Já existe `meta.json` com `fontes[]` (`cobertura`, `linhas`, `atualizado`, `lacuna`) como embrião (VERIFICADO).
  - **Alertas de falha:** passo final de cada workflow (`if: failure()`) abre/atualiza uma *issue* do GitHub ou envia mensagem (Telegram/e-mail/Discord webhook) com a etapa e o link da execução; mais **verificação externa** (UptimeRobot/Healthchecks.io, planos gratuitos) que dispara se `status.json.gerado` tiver > 36 h.
  - **Frescor no próprio produto:** o app mostra "dados de <data>" por fonte e, se atrasada, avisa.
  - **Orçamento de quebra:** porta de qualidade (item 7, problema 3) com limites de variação por métrica.

---

## 6. Roadmap técnico

Esforço em pessoa-semanas (p-s), para **1 pessoa**, incluindo testes. INFERÊNCIA calibrada pelo tamanho do código atual.

### 6.1 Em 2 semanas (≈ 2 p-s): estancar o risco

| # | Entrega | Esforço |
|---|---|---|
| 1 | Corrigir `pncp_pendentes.py` para não gerar janela futura; `risco_financeiro.py` com tratamento de esquema e `|| true` ou falha explícita com aviso | 0,2 |
| 2 | Porta de qualidade no CI antes de publicar (esquema JSON, contagens, `meta.json` com datas) e **passo que alerta** (issue/webhook) em qualquer falha | 0,5 |
| 3 | `urlSegura()` em todos os `href` de terceiros; `esc` onde faltar; limite e validação do `#inv=`; CSP em `<meta>` interina | 0,3 |
| 4 | Remover `nasc` do JSON público; id de pessoa de 64 bits com checagem de colisão | 0,4 |
| 5 | `:focus-visible`, `prefers-reduced-motion`, cartões como `<a>`/`<button>`, tamanhos de alvo ≥ 44 px nos controles principais; `<h1>` | 0,4 |
| 6 | Mover dados para fora do `gh-pages` forçado (R2 ou Pages com deploy via Actions oficial `deploy-pages`) | 0,2 |

**Cortar nesta fase:** novas fontes de dados, nova direção visual, push, loja.

### 6.2 Em 2 meses (≈ 10 a 12 p-s)

| Entrega | p-s |
|---|---|
| Shell Vue 3 + router em modo history + tokens + componentes base (a partir de `web/v2`); painel antigo congelado | 2,5 |
| Dados em R2 versionados + `manifest.json` + um arquivo por entidade + índices de busca fatiados | 2,5 |
| Pré-renderização (vite-ssg) + Worker de `og:image` + sitemap | 1,5 |
| Pipeline em jobs separados (coleta → cálculo → empacotamento → publicação), artefatos intermediários, cache e *retries*; `concurrency` por fonte; cron sem horário redondo | 1,5 |
| Testes: JSON Schema, 12 regras com casos de ouro (`casos/*.json`), Vitest, Playwright + axe (a11y) no CI, Lighthouse CI com orçamento | 1,5 |
| PWA instalável + offline de "minha cidade" | 1 |
| Analytics sem rastreio + `/status` | 0,5 |
| Linhagem (`fonte`, `regra@versao`, `sha256`) em alertas e entidades | 1 |

**Orçamentos de desempenho (CI quebra se ultrapassar):** shell + primeira tela ≤ 150 KB gzip; JS inicial ≤ 100 KB gzip; LCP ≤ 2,5 s p75 em perfil "Moto G, 4G lento"; mapa ≤ 500 KB gzip, carregado sob demanda.

### 6.3 Em 6 meses (≈ 18 a 24 p-s cumulativas)

- API mínima em Worker (busca difusa, assinaturas de alerta, consultas de contrato por range de Parquet) — 3 p-s.
- Push por cidade (Web Push + FCM) — 2 p-s; Capacitor + Play Store (+ App Store se a métrica justificar) — 4 a 6 p-s.
- i18n real (en/es) + esquema canônico multi-país (OCDS/BODS) + **um segundo país piloto** de adaptador — 4 a 6 p-s.
- Brotli/Parquet de download aberto e dicionário de dados — 1 p-s; página de metodologia por regra — 1 p-s.

### 6.4 Riscos

| Risco | Prob./Impacto | Mitigação |
|---|---|---|
| Falha de uma fonte oficial muda de formato (já ocorreu com BCB) | Alta/Média | Contrato de esquema por fonte, teste diário, alerta, "último bom" |
| Difamação/erro de identidade (homônimo, colisão de id) | Média/**Muito alta** | Id longo, marca de identidade provável, `noindex` em pessoas sem função pública, revisão, canal de correção |
| Cloudflare/HF/GitHub mudam termos | Média/Média | Dados canônicos em Parquet abertos; export reproduzível; dois destinos de publicação |
| Conta do HF suspensa ou token expira | Baixa/Alta | Espelho semanal em R2 ou Backblaze B2 (privado) |
| Escopo de app antes do produto estar provado | Alta/Média | Só entrar em loja com métricas (4.5) |
| Dev único (fator ônibus) | Alta/Alta | Documentar `OPERACAO.md` (já existe), CI como fonte de verdade, runbook de falhas |
| iOS limita PWA | Certa/Média | Aceitar; e-mail/RSS/Telegram como canal de alerta alternativo |

### 6.5 O que cortar

- Painel antigo com 14 abas: migrar só Hoje, Cidade, Pessoa, Empresa, Caso e Fontes; **aposentar** Comércio exterior, Agenda, Salários e Viagens do caminho principal (continuam como páginas de "explorar", sem prioridade).
- Quatro dependências de fonte sem uso, `.woff` de reserva, os dois efeitos SVG de "tinta" na v2 (`feTurbulence` é caro no celular de entrada; INFERÊNCIA) até medir.
- Cards para redes sociais por script (`cards.py`) em favor de `og:image` por URL.
- A tela de boas-vindas animada e a `setTimeout(...,1800)` do hash.

---

## 7. Os 10 problemas técnicos mais urgentes (em ordem)

1. **Dado quebrado ou velho vai ao ar sem aviso.** Sem porta de qualidade, sem alerta de falha, `|| true` em dezenas de etapas, e a `leve` republica o que já está no ar. Evidência: falhas de 03 a 04/11 (`risco_financeiro.py`, `CodInst`), deploy com *timeout* em 04/11 e 06/11. (6.1 itens 1 e 2)
2. **Identidade de pessoa com id de 32 bits e chave frágil.** ~21% de chance de colisão com 44.710 pessoas; homônimos sem data fundidos por UF (`pessoas.py:41-42`). Risco reputacional máximo.
3. **Exposição de data de nascimento e de candidatos sem função pública** no JSON público (`s16.json`), contra a regra 3 do projeto e a LGPD (INFERÊNCIA jurídica; conferir).
4. **Peso de abertura: 1,5 MB comprimidos e nada renderiza até 6 `fetch` terminarem** (`main.js:876`); JS de 1,72 MB sem divisão. LCP estimado de 9 a 14 s em 4G lento.
5. **Não existe URL por entidade** (hash `#p-`, `#e-`, `404.html` = `index.html`): impossível compartilhar bem, indexar ou gerar imagem de compartilhamento.
6. **Publicação de 158 MB por `git push -f`**, causa provável dos *timeouts* de deploy do Pages e do crescimento do repositório; dados e shell acoplados.
7. **Gravidade recalculada no navegador** (percentis fixos, `main.js:884-889`), duplicada na v2; a fonte de verdade deveria ser o pipeline, com explicação gravada.
8. **Acessibilidade:** zero foco visível, 10 `outline:none`, cartões clicáveis não focáveis, sem `prefers-reduced-motion`, ~28 regras com fonte de 9 a 10 px, alvos de toque pequenos.
9. **Segurança de front:** `href` de terceiros sem validação de esquema (`javascript:`), importação de investigação por link (`#inv=`), sem CSP, glifos de `demotiles.maplibre.org`. Sem testes dos 12 detectores nem do contrato de JSON.
10. **Agendamento e concorrência não confiáveis:** `cron` com atraso de 4 a 8 h (VERIFICADO), `concurrency` compartilhado que cancela pendências, janelas PNCP futuras que sempre falham, dependência de um dataset privado do HF sem espelho, `actions` em Node 20 obsoleto.

---

## 8. Fontes e limites desta auditoria

- VERIFICADO: leitura do repositório (`web/main.js`, `investigar.js`, `pessoa.js`, `style.css`, `index.html`, `v2/*`, `vite.config.js`, `package.json`, `ingestao/*`, `.github/workflows/*`, `docs/*`, `.gitignore`); `npx vite build` em 08/11/2026; tamanhos de `web/public/data/` e `gzip -9`; `gh run list` e `gh run view --log-failed` (execuções de 03 a 08/11/2026: `41747151293`, `42472181556`, `42250412849`, `42512176388`); cálculo de contraste.
- FONTE (acessadas em 08/11/2026): Cloudflare R2 Pricing, https://developers.cloudflare.com/r2/pricing/ ; Cloudflare Workers Pricing, https://developers.cloudflare.com/workers/platform/pricing/ .
- FONTE não reabertas (conhecimento geral; **conferir antes de decidir**): WebKit, Web Push no iOS (https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/); WebKit, limpeza de armazenamento (https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/); preços de Plausible (https://plausible.io/#pricing); padrões OCDS (https://standard.open-contracting.org) e BODS (https://standard.openownership.org); taxas das lojas.
- NÃO FEITO: Lighthouse/WebPageTest em aparelho real; `npm audit`; teste com leitor de tela (NVDA/TalkBack/VoiceOver); medição de Pagefind/MiniSearch/SQLite-WASM/DuckDB-WASM com os dados reais; análise jurídica LGPD. As estimativas de LCP/TTI e de custo são **INFERÊNCIA** e devem ser confirmadas.
