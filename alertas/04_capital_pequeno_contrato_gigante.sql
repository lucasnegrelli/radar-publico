-- R04: valor do contrato muito maior que o capital social da empresa (empresa sem porte aparente para executar).
SELECT 'R04' AS regra,
       CASE WHEN p.valor_global >= 50 * greatest(em.capital_social, 1000) AND p.valor_global >= 2000000 THEN 'alta' ELSE 'media' END AS gravidade,
       p.id, p.fornecedor, p.doc14 AS doc, p.orgao, p.esfera, p.uf, p.municipio, p.objeto, p.valor_global AS valor, p.data_assinatura AS data,
       p.tipo_contrato, p.categoria, em.capital_social, em.porte, round(p.valor_global / greatest(em.capital_social, 1000)) AS vezes_o_capital
FROM pncp p
JOIN estab e ON e.cnpj = p.doc14
JOIN emp em ON em.cnpj_basico = e.cnpj_basico
WHERE p.tipo_pessoa = 'PJ' AND p.valor_global >= 500000
  AND p.valor_global >= 30 * greatest(em.capital_social, 1000);
