-- R08: empresa que vende ao governo tem sócio sediado em jurisdição de tributação favorecida (lista de referência, resumida da IN RFB 1.037/2010).
-- Ter sócio no exterior é legal; o ponto de atenção é a opacidade da cadeia societária de quem recebe dinheiro público.
-- Nível 1: jurisdições clássicas de sigilo. Nível 2: centros financeiros com regimes favorecidos.
WITH sx AS (
  SELECT s.cnpj_basico, s.nome_socio, s.tipo_socio, s.qualificacao, p.nome AS pais,
    CASE WHEN regexp_matches(p.nn, 'PANAMA|VIRGENS|CAYMAN|BAHAMAS|BERMUDA|SEYCHELLES|BELIZE|SAMOA|VANUATU|MARSHALL|JERSEY|GUERNSEY|ILHA DE MAN|MAN, ILHA|LIECHTENSTEIN|MONACO|ANDORRA|GIBRALTAR|ANTIGUA|SANTA LUCIA|ANGUILLA|ARUBA|TURKS|NAURU|COOK') THEN 1
         WHEN regexp_matches(p.nn, 'LUXEMBURGO|SUICA|SINGAPURA|HONG KONG|MACAU|EMIRADOS|CHIPRE|MALTA|BARBADOS|MAURICIO|COSTA RICA|URUGUAI|LIBANO|LIBERIA|MALDIVAS') THEN 2 END AS nivel
  FROM read_parquet('dados/cnpj/socios_ext_*.parquet') s JOIN pais_rfb p ON p.cod = s.pais
)
SELECT 'R08' AS regra,
       CASE WHEN x.nivel = 1 AND p.valor_global >= 1000000 THEN 'alta' WHEN x.nivel = 1 OR p.valor_global >= 1000000 THEN 'media' ELSE 'baixa' END AS gravidade,
       md5(p.doc14 || x.pais) AS grupo, p.id, p.fornecedor, p.doc14 AS doc, p.orgao, p.esfera, p.uf, p.municipio, p.objeto, p.valor_global AS valor, p.data_assinatura AS data,
       p.tipo_contrato, p.categoria, x.pais AS pais_socio, x.nivel, x.nome_socio AS socio, x.tipo_socio, x.qualificacao
FROM pncp p JOIN sx x ON x.cnpj_basico = left(p.doc14, 8)
WHERE x.nivel IS NOT NULL AND p.tipo_pessoa = 'PJ' AND p.valor_global >= 300000
  AND NOT p.erro_valor AND NOT p.estatal AND NOT p.credenciamento AND p.n_mesmo_valor < 3;
