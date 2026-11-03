# Arquitetura

Tudo roda **online, no GitHub Actions**. Nada precisa estar ligado na máquina de ninguém.

## Visão geral

```
fontes públicas ──► ingestão (Python/DuckDB) ──► alertas/fichas/casos (JSON) ──► site estático ──► GitHub Pages
 (TSE, CGU, PNCP,      ingestao/*.py                  web/public/data/*          web/ (Vite)     radar.lucasnegrelli.com
  Câmara, Senado,      alertas/*.sql
  Receita, BCB…)
```

* **Dados pesados** (CNPJ 3,3 GB, PNCP, licitações, TSE, banco-base) ficam no Hugging Face (`propagang/radar-publico-dados`, privado). O workflow baixa, processa e descarta.
* **Site** é estático: tudo que o navegador lê está em `web/public/data/` (alertas, fichas de pessoa em lotes, fichas de empresa em lotes, casos). Não há servidor nem banco de dados em produção.
* **Histórico** ("NOVOS", linha de base) fica em `data-publica/historico.json` e é commitado pelo próprio workflow.

## Workflows (`.github/workflows/`)

| Arquivo | Quando | O que faz |
|---|---|---|
| `atualizar.yml` | domingo 14:17 UTC + manual | Rodada **completa**: baixa a base, atualiza fontes, calcula todos os alertas, fichas de pessoa e empresa, casos, cards, monta e publica o site (~50 min) |
| `atualizar-leve.yml` | seg–sáb 08:17 UTC + manual | Rodada **leve**: baixa do site já publicado, renova notícias, diários e casos, e republica (~15 min) |
| `pncp.yml` | domingo 03:23 UTC | Janelas quinzenais de contratos do PNCP → Hugging Face (janelas recentes sempre refeitas) |
| `compras.yml` | domingo 03:47 UTC | Licitações (modalidade, valor estimado e homologado) → Hugging Face |
| `cnpj-mensal.yml` | manual | Cadastro de empresas da Receita → Hugging Face |
| `diarios.yml`, `caso.yml` | manual | Buscas no Querido Diário |

Segredos do repositório: `HF_TOKEN` (leitura e escrita no dataset). O token do GitHub (`GITHUB_TOKEN`) é automático.

## Pastas

* `ingestao/` scripts de coleta e cálculo (um por assunto). Ver `docs/FONTES.md`.
* `alertas/*.sql` regras de contrato (R01–R08) e a base `00_base_contratos.sql`.
* `casos/*.json` casos de pessoas e investigações (escritos à mão, com fonte); `ingestao/casos_auto.py` junta com manchetes e fichas.
* `web/` site (`main.js`, `pessoa.js`, `investigar.js`, `glossario.js`, `style.css`).
* `data-publica/` resultados pequenos que viram parte do repositório (alertas extras, histórico, estáticos do mapa).
* `dados/` (ignorado pelo git) cópia local dos dados pesados.
* `docs/` esta documentação.

## Ordem da rodada completa

1. Baixa base e dados do Hugging Face.
2. `atualizar_fontes.py` (CEIS, CNEP, CEPIM, cota da Câmara e do Senado) e recarrega o banco.
3. `bcb_ifdata.py`, `tse_historico.py 2026`.
4. `emendas.py` (R09) e `despesas_federais.py` (R11).
5. `exportar_web.py`: base de contratos, regras R02–R08, e dentro dele `politicos_socios.py` (R10) e `servidores.py` (R12). Gera `alertas.json`.
6. `escala.py`, `fichas.py`, `viagens_cota.py`, `risco_financeiro.py`, `risco_dossie.py`, `fidc.py`, `municipios.py`.
7. Em paralelo: `datajud.py`, `noticias.py`, `noticias_alertas.py`, `diarios.py`, `camara_atividade.py`, `senado_atividade.py`, `ofac.py`.
8. `casos_auto.py` e `cards.py`.
9. `offshore.py`, `pessoas.py`, `empresas.py`, `pessoas_extras.py`.
10. Build do site e publicação no branch `gh-pages`.

## Armadilhas já resolvidas (não repetir)

* O banco-base foi criado no Windows: as views `emp`/`estab` guardam caminho absoluto. `atualizar_fontes.py` as apaga; o exportador as recria.
* O exportador usa muita memória: `DUCK_MEM` (padrão 6 GB; 10 GB no runner de repositório público).
* `pncp` é **tabela**, não view (materializada uma vez por rodada).
* Nunca usar `'\n'` dentro de scripts gerados por heredoc: gravar o script com a ferramenta de arquivo.
