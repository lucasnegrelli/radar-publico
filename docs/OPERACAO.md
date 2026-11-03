# Operação: como rodar, consertar e não se perder

## Rodar
* **Tudo sozinho:** o GitHub dispara a completa aos domingos e a leve de segunda a sábado.
* **Na hora:** GitHub → Actions → "Atualizar o Radar Público (tudo, online)" → *Run workflow* (marcar `pular_extras = sim` para pular Wikipédia/manchetes das pessoas e ganhar ~15 min).
* **Ver o resultado:** abrir a rodada; cada etapa tem nome. A etapa vermelha é a que falhou.
* **Local (só para desenvolver):** `cd web && npm ci && npx vite` serve o site com os dados de `web/public/data/` (gerados por `ingestao/*.py` a partir de `dados/`).

## Se algo falhar (tabela de sintomas)
| Sintoma | Causa provável | Conserto |
|---|---|---|
| Etapa "Fontes que mudam todo dia" falha com caminho `C:/…` | views `emp`/`estab` do banco-base | já tratado em `atualizar_fontes.py`; se voltar, ressubir `base/radar.duckdb` |
| Exportar alertas: *Out of Memory* | pouca memória | subir `DUCK_MEM` em `atualizar.yml` |
| `No files found … socios_ext_*.parquet` | arquivo não está no Hugging Face | subir `dados/cnpj/socios_ext_*.parquet` em `cnpj/2026-10-13/` |
| R11 não gera | Portal da Transparência não respondeu | o script mantém o resultado anterior; reexecutar depois |
| Montar o site: `cp … estaticos` | arquivos estáticos ausentes | `data-publica/estaticos/` precisa de `uf.geojson` e `mundo.geojson` |
| Diários demoram | API do Querido Diário lenta | teto de 15 min já aplicado em `diarios.py` |
| Página trava no navegador | laço em observador de DOM (glossário) | o glossário só observa `#detalhe`; não observar subárvores que ele próprio altera |

## Dados no Hugging Face (`propagang/radar-publico-dados`)
`base/radar.duckdb` · `cnpj/2026-10-13/*.parquet` · `pncp/*.parquet` · `compras/*.parquet` · `tse/*.parquet`.
Subir um arquivo novo: `python ingestao/sync_hf.py subir <pasta_local> <pasta_remota>` (precisa de `HF_TOKEN` no ambiente ou em `.env`).

## Adicionar uma fonte nova (passo a passo)
1. Escrever `ingestao/<fonte>.py` que lê só dado aberto e grava um JSON pequeno em `data-publica/` ou `dados/`.
2. Registrar a fonte em `docs/FONTES.md` (o que usa, atualização, limites).
3. Se gerar alerta: seguir o formato dos alertas extras (`id`, `regra`, `gravidade`, `empresa`, `cnpj`, `total`, `manchete{tipo}`, `tabela`) e criar o texto em `web/main.js` (manchete, números, critérios, o que não prova).
4. Colocar o passo em `.github/workflows/atualizar.yml` com `|| true` se a fonte for instável.
5. Documentar a regra em `docs/REGRAS.md`.

## Adicionar um caso
Criar `casos/<id>.json` com `titulo`, `resumo`, `situacao[]`, `marcos[]` (cada um com `data`, `tipo` = decisão, investigação, reportagem ou defesa, `texto`, `fonte`, `url`), `pessoas[]`, `consultas[]`, `lacunas[]`, e opcionalmente `valor` e `alertas_regras`. Regra: **todo fato tem fonte e tipo**; o que não foi confirmado vai em `lacunas`.
