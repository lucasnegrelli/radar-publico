# Radar Público

Monitor de dinheiro público: cruza bases abertas do governo brasileiro e mostra, em linguagem simples,
**pontos de atenção** (contratos, gastos e pagamentos fora do padrão), num mapa interativo.

> Um alerta é um cruzamento automático de dados públicos que encontrou algo fora do esperado.
> **Não é prova de irregularidade nem acusação.** Cada alerta traz o link da fonte oficial para conferência.

## O que já detecta
| Regra | O que procura |
|---|---|
| R01 | Empresa punida (CEIS/CNEP) que recebeu dinheiro da cota parlamentar (Câmara e Senado) |
| R02 | Contrato público assinado com empresa punida |
| R03 | Empresa aberta há menos de 180 dias com contrato de valor alto |
| R04 | Contrato muito maior que o capital social da empresa |

Em construção: doador de campanha que virou fornecedor da prefeitura, fracionamento de contratos,
concentração de fornecedores e um módulo de **risco financeiro** (Banco Central, CVM, previdência de servidores).
Tipologias em [`docs/TIPOLOGIAS.md`](docs/TIPOLOGIAS.md).

## Fontes de dados (todas abertas)
PNCP, Portal da Transparência (CEIS/CNEP), Câmara (CEAP), Senado (CEAPS), TSE, Receita Federal (CNPJ), IBGE, SICONFI, Banco Central, CVM.

## Como rodar
```bash
pip install duckdb huggingface_hub
python ingestao/baixar.py 2025 2026        # cota parlamentar e TSE
python ingestao/cnpj.py                    # CNPJ da Receita -> Parquet
python ingestao/pncp_janela.py 2026-10-01_2026-10-15
python ingestao/carregar.py                # monta o DuckDB
python ingestao/exportar_web.py            # gera os alertas
cd web && npm install && npm run dev       # painel em http://127.0.0.1:5173
```
Os downloads pesados rodam no GitHub Actions (`.github/workflows`) e os dados ficam num dataset no Hugging Face.
Chaves ficam em `.env` (ignorado pelo Git): `PORTAL_TRANSPARENCIA_KEY`, `HF_TOKEN`.

## Créditos e inspiração
- [Operação Serenata de Amor](https://github.com/okfn-brasil/serenata-de-amor) (Rosie e Jarbas), MIT
- [Querido Diário](https://github.com/okfn-brasil/querido-diario), Open Knowledge Brasil, MIT
- [God's Eye View](https://github.com/bilawalsidhu/gods-eye-view), MIT, referência de arquitetura em camadas

## Licença
MIT. Os dados pertencem às fontes originais e seguem os termos delas.
