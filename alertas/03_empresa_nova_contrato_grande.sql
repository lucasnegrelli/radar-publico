-- R03: empresa aberta há pouco tempo assina contrato de valor alto.
SELECT 'R03' AS regra,
       CASE WHEN date_diff('day', e.abertura, p.data_assinatura) < 90 AND p.valor_global >= 1000000 THEN 'alta'
            WHEN date_diff('day', e.abertura, p.data_assinatura) < 90 THEN 'media'
            WHEN p.valor_global >= 1000000 THEN 'media' ELSE 'baixa' END AS gravidade,
       p.id, p.fornecedor, p.doc14 AS doc, p.orgao, p.esfera, p.uf, p.municipio, p.objeto, p.valor_global AS valor, p.data_assinatura AS data,
       p.tipo_contrato, p.categoria, e.abertura, date_diff('day', e.abertura, p.data_assinatura) AS dias_de_vida, em.capital_social, em.porte
FROM pncp p
JOIN estab e ON e.cnpj = p.doc14
LEFT JOIN emp em ON em.cnpj_basico = e.cnpj_basico
WHERE p.tipo_pessoa = 'PJ' AND e.abertura IS NOT NULL
  AND date_diff('day', e.abertura, p.data_assinatura) BETWEEN 0 AND 180
  AND p.valor_global >= 200000;
