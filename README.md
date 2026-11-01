# Radar Público

**Ao vivo: https://radar.lucasnegrelli.com**

Monitor de dinheiro público: cruza bases abertas do governo brasileiro e mostra, em linguagem simples,
**pontos de atenção** (contratos, gastos e pagamentos fora do padrão) num mapa interativo.

> Um alerta é um cruzamento automático de dados públicos que encontrou algo fora do esperado.
> **Não é prova de irregularidade nem acusação.** Cada alerta traz o link da fonte oficial para conferência.
> Os dados de origem têm erros (por exemplo, contratos digitados com valor mil vezes maior); o sistema filtra os mais óbvios, mas não todos.

## O que detecta
| Regra | O que procura |
|---|---|
| R01 | Empresa punida (CEIS/CNEP) que recebeu da cota parlamentar (Câmara e Senado) |
| R02 | Contrato público com empresa punida, só quando a punição alcança o órgão contratante |
| R03 | Empresa aberta há menos de 180 dias com contrato de valor alto (exclui concessões e consórcios) |
| R04 | Contrato muito maior que o capital social da empresa (exclui valores com cara de erro de digitação) |
| R05 | Sócio de empresa que doou à campanha do prefeito eleito e a empresa passou a ser contratada pela prefeitura |
| R06 | Possível fracionamento: 4 ou mais contratos pequenos do mesmo órgão com a mesma empresa no trimestre |
| R07 | Um fornecedor concentra mais da metade do valor contratado por uma prefeitura no ano |
| RF01 | Banco em crescimento acelerado e alavancado (Banco Central). Backtest: o critério teria acendido o Banco Master por 9 trimestres, a partir de T1/2023 |

Também tem **fichas de agentes públicos** (deputados, senadores, prefeitos): só dados abertos, sem avaliação de conduta.
Tipologias de fraude financeira em [`docs/TIPOLOGIAS.md`](docs/TIPOLOGIAS.md).

## Limites conhecidos
- Fundos de previdência de servidores (RPPS) que compram papel de banco direto não aparecem em dado aberto em lote (o DAIR só é consultável fundo a fundo). Caminho: Lei de Acesso à Informação.
- Judiciário: só há dados de produtividade e transparência (DataJud, CNJ); não há como medir conduta individual.

## Fontes (todas abertas)
PNCP, Portal da Transparência (CEIS/CNEP), Câmara (CEAP), Senado (CEAPS), TSE, Receita Federal (CNPJ), IBGE, SICONFI, Banco Central (IF.data), CVM.

## Como rodar
```bash
pip install duckdb huggingface_hub
python ingestao/baixar.py 2023 2024 2025 2026   # cota parlamentar e TSE
python ingestao/cnpj.py                         # CNPJ da Receita -> Parquet
python ingestao/pncp_janela.py 2026-10-01_2026-10-15   # (em massa: GitHub Actions)
python ingestao/bcb_ifdata.py                   # Banco Central
python ingestao/carregar.py                     # monta o DuckDB
python ingestao/exportar_web.py                 # alertas das regras R01-R07
python ingestao/risco_financeiro.py             # RF01
python ingestao/fichas.py                       # fichas de agentes públicos
cd web && npm install && npm run dev            # http://127.0.0.1:5173
```
Os downloads pesados rodam no GitHub Actions (`.github/workflows`) e os dados ficam num dataset no Hugging Face.
Chaves ficam em `.env` (ignorado pelo Git): `PORTAL_TRANSPARENCIA_KEY`, `HF_TOKEN`.

## Créditos e inspiração
- [Operação Serenata de Amor](https://github.com/okfn-brasil/serenata-de-amor) (Rosie e Jarbas), MIT
- [Querido Diário](https://github.com/okfn-brasil/querido-diario), Open Knowledge Brasil, MIT
- [God's Eye View](https://github.com/bilawalsidhu/gods-eye-view), MIT, referência de arquitetura em camadas

## Licença
MIT. Os dados pertencem às fontes originais e seguem os termos delas.
