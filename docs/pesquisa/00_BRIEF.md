# Radar Público: briefing da missão (leitura obrigatória para toda a equipe)

Data: 08/11/2026. Responsável pela missão: direção de produto e investigação (Claude). Cliente: Lucas Negrelli.

## 1. O que é
**Radar Público** (https://radar.lucasnegrelli.com, repositório `C:\Users\lucas\Desktop\Negrelli\GitHub\radar-publico`) é um monitor do **movimento do dinheiro público no Brasil**. Cruza bases oficiais e abertas (contratos PNCP, emendas, sanções CEIS/CNEP, Receita/CNPJ, TSE, PGFN, Banco Central, Portal da Transparência, Câmara/Senado, salários, viagens, agenda de ministros, comércio exterior) e mostra **sinais de atenção** ("alertas", "coincidências") com a fonte à mostra e o que cada sinal **não** prova.

## 2. Ambição declarada pelo cliente
- Ser **a referência brasileira** em transparência e fiscalização do dinheiro público, feita para o **povo** (não só jornalistas), "um modelo útil para o Brasil" e depois escalar para o mundo.
- Cobrir **todos os poderes e esferas**: Executivo, Legislativo, Judiciário, MP, Tribunais de Contas; federal, estadual, municipal; empresas, pessoas, ligações internacionais (offshore, comércio exterior).
- Ser **tão útil e crível** que quem faz algo errado **tenha medo de aparecer no site**. Mas: "se tudo é alerta, nada é alerta". Credibilidade acima de volume.
- Ser **mobile primeiro**, evoluindo para **aplicativo**.
- Ter **direção de arte própria, de nível de premiação**, "sair do óbvio" e ao mesmo tempo **ser totalmente útil e fácil**. O cliente rejeitou, em ordem: a interface atual (densa, "dói os olhos"), três "peles" (creme/serifa/cartões = "slop de IA"), um protótipo cinza, um protótipo "cordel/xilogravura". Ainda não aprovou nenhuma direção.
- Tom desejado quando abre no celular: **sério e cortante**.

## 3. Estado atual (fatos verificáveis no repositório)
- Front-end atual (painel completo): `web/index.html`, `web/main.js` (~1.600 linhas, JS puro), `web/style.css`; MapLibre + deck.gl. Nova interface em teste: `web/v2/` (Vue 3 + Vite), com a ideia da "faixa da coincidência" (sanção × pagamentos).
- Pipeline: `ingestao/*.py` (Python + DuckDB), orquestrado por GitHub Actions (`.github/workflows/*.yml`), publicado no GitHub Pages com domínio próprio. Dados web em `web/public/data/*.json` (não versionados; gerados no CI).
- Regras de alerta R01–R12 (ver `docs/REGRAS.md`, `docs/TIPOLOGIAS.md`, `docs/FONTES.md`, `docs/ARQUITETURA.md`, `docs/ROADMAP.md`, `docs/PRINCIPIOS.md`): cota × punida, contrato × punida, empresa nova com contrato grande, capital pequeno × contrato gigante, doador do prefeito virou fornecedor, fracionamento, concentração, sócio no exterior, emendas (R09), político sócio, pagamento federal × punida (R11), servidor sócio (R12), risco financeiro de bancos (RF01).
- ~1.581 alertas; priorização por pontuação: cerca de 3% "prioridade máxima", 18% "relevante", resto "contexto".
- Fontes ligadas hoje: PNCP, Portal da Transparência (arquivos e API), emendas, CEIS/CNEP, CEPIM, leniência, CEAF, Câmara, Senado, TSE (2014–2026), Receita/CNPJ, PGFN (dívida ativa), Banco Central (IF.data e regimes especiais), CVM (FIDC), DadosJusBr (remuneração do Judiciário/MP), SIAPE (servidores), e-Agendas (CGU), Comex Stat (MDIC), Offshore Leaks (ICIJ), OFAC/UE, Siconfi, Querido Diário, DataJud, Google Notícias (RSS).
- Lacunas conhecidas: Tribunais de Contas estaduais, portais municipais, folha estadual/municipal, licitação "por dentro" (participantes), quadro de assessores, agenda do presidente, viagens do Senado/Judiciário, valores confirmados de casos como o do Banco Master (só via notícias).

## 4. Regras de ouro do projeto (não negociáveis)
1. **Nunca afirmar culpa.** Alerta = ponto de atenção; sempre com fonte, explicação e "o que isto não prova".
2. **Só dados abertos e públicos.** User-Agent honesto, respeitar limites, nada de burlar bloqueio.
3. **Privacidade:** CPF mascarado; nome de pessoa só quando função pública e dado de transparência ativa.
4. **Honestidade sobre limites:** dizer o que foi verificado e o que é inferência.

## 5. Regras para quem executa esta pesquisa
- Você é um profissional sênior da sua área, trabalhando **para o Radar Público**, e vai entregar **trabalho que o cliente possa usar para decidir**, não um resumo genérico.
- **Não altere o código do produto** (`web/`, `ingestao/`, workflows). Escreva **somente** no arquivo de entrega indicado em `docs/pesquisa/`.
- **Cite fontes com URL** e data de acesso. Marque cada afirmação como **VERIFICADO** (você viu/testou), **FONTE** (afirmado por fonte citada) ou **INFERÊNCIA** (seu raciocínio). Não invente nomes, números, URLs ou prêmios. Se não achou, diga que não achou.
- Não crie contas, não faça login, não baixe arquivos grandes (> 50 MB), não envie dados a terceiros, não imprima chaves de API (se encontrar `.env`, trate como segredo; use só se a sua tarefa mandar, sem exibir).
- Seja específico e acionável: números, exemplos, nomes de campos, trechos de dados, decisões recomendadas e trade-offs.
- Entregue o arquivo em português do Brasil, com acentuação correta. A última mensagem sua deve ter **no máximo 250 palavras**: o que fez, os 5 achados mais importantes e o caminho do arquivo.
