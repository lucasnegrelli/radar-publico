-- R04: valor do contrato muito maior que o capital social. Exclui credenciamento/valor repetido/consórcio e PJ com capital zerado (sem informação).
SELECT 'R04' AS regra,
       CASE WHEN p.valor_global >= 100 * em.capital_social AND p.valor_global BETWEEN 2000000 AND 100000000 THEN 'alta' ELSE 'media' END AS gravidade,
       p.id, p.fornecedor, p.doc14 AS doc, p.orgao, p.esfera, p.uf, p.municipio, p.objeto, p.valor_global AS valor, p.data_assinatura AS data,
       p.tipo_contrato, p.categoria, em.capital_social, em.porte, round(p.valor_global / em.capital_social) AS vezes_o_capital
FROM pncp p
JOIN estab e ON e.cnpj = p.doc14
JOIN emp em ON em.cnpj_basico = e.cnpj_basico
WHERE p.tipo_pessoa = 'PJ' AND p.valor_global BETWEEN 500000 AND 300000000 AND em.capital_social >= 1000  -- acima de R$ 300 mi: quase sempre erro de digitação na origem
  AND p.valor_global >= 50 * em.capital_social
  AND p.valor_global <= 1000 * em.capital_social  -- acima de 1000x o capital: quase sempre valor digitado errado (escala), não ponto de atenção
  AND NOT p.tipo_especial AND NOT p.credenciamento AND p.n_mesmo_valor < 3 AND NOT p.erro_valor AND NOT p.estatal
  AND NOT (p.valor_global % 1000 = 0 AND p.valor_global / 1000 <= 10 * coalesce(em.capital_social, 0) AND coalesce(em.capital_social, 0) > 0);  -- provável erro de escala por mil
