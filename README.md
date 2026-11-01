# Radar Público

Painel que cruza bases públicas do governo e mostra, em linguagem simples,
pontos de atenção: contratos e gastos fora do padrão.

**Anomalia estatística não é prova de corrupção.** Todo alerta é "ponto de atenção",
sempre com link para a fonte oficial.

## Fontes
- PNCP (contratos e licitações): https://pncp.gov.br/api/consulta/swagger-ui/index.html
- Receita Federal, CNPJ (sócios, data de abertura)
- CEIS/CNEP, Portal da Transparência (chave gratuita)
- TSE Dados Abertos (doações de campanha)
- API da Câmara e do Senado

## Créditos e inspiração
- Operação Serenata de Amor (Rosie e Jarbas), MIT: https://github.com/okfn-brasil/serenata-de-amor
- Querido Diário, Open Knowledge Brasil, MIT: https://github.com/okfn-brasil/querido-diario
- Open Knowledge Brasil: https://ok.org.br

## Status
- [x] PNCP responde sem chave (testado 31/10/2026)
- [ ] Querido Diário API: handshake SSL falhando em 31/10, retestar
- [x] Ingestão -> DuckDB (PNCP, CEAP Câmara, CEAPS Senado, TSE 2024, SICONFI, deputados)
- [ ] CNPJ da Receita (servidor não conecta daqui, achar espelho)
- [x] Alerta 1: fornecedor de cota parlamentar com sanção vigente (CEIS/CNEP), ver alertas/01
- [ ] Alerta 2: doador de campanha que virou fornecedor
- [ ] Alerta 3: empresa nova com contrato grande (precisa do CNPJ da Receita)
