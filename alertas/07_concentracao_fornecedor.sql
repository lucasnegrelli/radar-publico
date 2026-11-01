-- R07: um único fornecedor concentra mais da metade do valor contratado por um órgão municipal num ano (órgãos com R$ 2 mi ou mais no ano).
WITH base AS (
  SELECT *, year(data_assinatura) AS ano FROM pncp
  WHERE esfera = 'M' AND tipo_pessoa = 'PJ' AND NOT erro_valor AND NOT estatal AND NOT credenciamento AND n_mesmo_valor < 3 AND valor_global >= 20000 AND doc14 <> '00000000000000'
), tot AS (SELECT orgao_cnpj, ano, sum(valor_global) total_orgao, count(*) n_orgao_ctr FROM base GROUP BY ALL HAVING sum(valor_global) >= 2000000 AND count(*) >= 5),
f AS (SELECT orgao_cnpj, ano, doc14, sum(valor_global) v, count(*) n FROM base GROUP BY ALL)
SELECT 'R07' AS regra,
       CASE WHEN f.v / t.total_orgao >= 0.7 AND t.total_orgao >= 10000000 THEN 'alta' WHEN f.v / t.total_orgao >= 0.6 THEN 'media' ELSE 'baixa' END AS gravidade,
       md5(b.orgao_cnpj || b.doc14 || b.ano::VARCHAR) AS grupo, b.id, b.fornecedor, b.doc14 AS doc, b.orgao, b.esfera, b.uf, b.municipio, b.objeto,
       b.valor_global AS valor, b.data_assinatura AS data, b.tipo_contrato, b.categoria, b.ano, round(f.v / t.total_orgao, 3) AS share, t.total_orgao
FROM base b JOIN f ON f.orgao_cnpj = b.orgao_cnpj AND f.ano = b.ano AND f.doc14 = b.doc14 JOIN tot t ON t.orgao_cnpj = b.orgao_cnpj AND t.ano = b.ano
WHERE f.v / t.total_orgao >= 0.5;
