-- R06: possível fracionamento. O mesmo órgão contrata a mesma empresa 4 ou mais vezes no mesmo trimestre, cada contrato abaixo de R$ 70 mil
-- (faixa da dispensa de licitação por valor), somando R$ 200 mil ou mais. Pode indicar uma compra maior dividida para fugir da licitação.
WITH base AS (
  SELECT *, date_trunc('quarter', data_assinatura) AS tri_ini FROM pncp
  WHERE tipo_pessoa = 'PJ' AND valor_global BETWEEN 15000 AND 70000 AND NOT erro_valor AND NOT estatal AND NOT credenciamento AND n_mesmo_valor < 3
), g AS (
  SELECT orgao_cnpj, doc14, tri_ini, count(*) n, sum(valor_global) soma FROM base GROUP BY ALL HAVING count(*) >= 4 AND sum(valor_global) >= 200000
)
SELECT 'R06' AS regra,
       CASE WHEN g.n >= 8 AND g.soma >= 500000 THEN 'alta' WHEN g.n >= 5 THEN 'media' ELSE 'baixa' END AS gravidade,
       md5(b.orgao_cnpj || b.doc14 || b.tri_ini::VARCHAR) AS grupo, b.id, b.fornecedor, b.doc14 AS doc, b.orgao, b.esfera, b.uf, b.municipio, b.objeto,
       b.valor_global AS valor, b.data_assinatura AS data, b.tipo_contrato, b.categoria, strftime(b.tri_ini, '%Y-%m') AS tri
FROM base b JOIN g USING (orgao_cnpj, doc14, tri_ini);
