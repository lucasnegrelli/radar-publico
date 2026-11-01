-- R02: contrato público assinado com empresa que constava no CEIS/CNEP na data da assinatura.
WITH sancoes AS (
  SELECT 'CEIS' AS lista, lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\D','','g'),14,'0') AS doc,
         "CATEGORIA DA SANÇÃO" AS categoria, "ÓRGÃO SANCIONADOR" AS orgao_sancionador, "ABRAGÊNCIA DA SANÇÃO" AS abr,
         try_strptime("DATA INÍCIO SANÇÃO",'%d/%m/%Y')::date AS ini, try_strptime("DATA FINAL SANÇÃO",'%d/%m/%Y')::date AS fim FROM ceis
  UNION ALL
  SELECT 'CNEP', lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\D','','g'),14,'0'), "CATEGORIA DA SANÇÃO","ÓRGÃO SANCIONADOR","ABRAGÊNCIA DA SANÇÃO",
         try_strptime("DATA INÍCIO SANÇÃO",'%d/%m/%Y')::date, try_strptime("DATA FINAL SANÇÃO",'%d/%m/%Y')::date FROM cnep
)
SELECT 'R02' AS regra,
       CASE WHEN s.abr ILIKE 'Todas as Esferas%' OR s.abr ILIKE 'Em todos os Poderes%' THEN 'alta'
            WHEN s.abr ILIKE 'No %rg_o sancionador' THEN 'baixa' ELSE 'media' END AS gravidade,
       p.id, p.fornecedor, p.doc14 AS doc, p.orgao, p.esfera, p.uf, p.municipio, p.objeto, p.valor_global AS valor, p.data_assinatura AS data,
       p.tipo_contrato, p.categoria, s.lista, s.categoria AS sancao_tipo, s.orgao_sancionador, s.abr AS alcance, s.ini AS sancao_ini, s.fim AS sancao_fim
FROM pncp p JOIN sancoes s ON s.doc = p.doc14 AND p.doc14 <> '00000000000000'
WHERE p.data_assinatura >= s.ini AND (s.fim IS NULL OR p.data_assinatura <= s.fim) AND p.valor_global > 0;
