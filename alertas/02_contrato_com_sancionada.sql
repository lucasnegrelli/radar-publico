-- R02: contrato público assinado com empresa que constava no CEIS/CNEP na data da assinatura
-- E cuja punição ALCANÇA o órgão contratante (esfera/UF/Poder), não apenas coincide no tempo.
WITH sancoes AS (
  SELECT 'CEIS' AS lista, lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\D','','g'),14,'0') AS doc,
         "CATEGORIA DA SANÇÃO" AS categoria, "ÓRGÃO SANCIONADOR" AS orgao_sancionador, "ABRAGÊNCIA DA SANÇÃO" AS abr,
         "ESFERA ÓRGÃO SANCIONADOR" AS esf, "UF ÓRGÃO SANCIONADOR" AS uf_s,
         try_strptime("DATA INÍCIO SANÇÃO",'%d/%m/%Y')::date AS ini, try_strptime("DATA FINAL SANÇÃO",'%d/%m/%Y')::date AS fim FROM ceis
  UNION ALL
  SELECT 'CNEP', lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\D','','g'),14,'0'), "CATEGORIA DA SANÇÃO","ÓRGÃO SANCIONADOR","ABRAGÊNCIA DA SANÇÃO",
         "ESFERA ÓRGÃO SANCIONADOR","UF ÓRGÃO SANCIONADOR",
         try_strptime("DATA INÍCIO SANÇÃO",'%d/%m/%Y')::date, try_strptime("DATA FINAL SANÇÃO",'%d/%m/%Y')::date FROM cnep
), cruz AS (
  SELECT p.*, s.lista, s.categoria AS sancao_tipo, s.orgao_sancionador, s.abr AS alcance, s.ini AS sancao_ini, s.fim AS sancao_fim,
    CASE
      WHEN s.abr ILIKE 'Todas as Esferas%' THEN 'alta'
      WHEN s.abr ILIKE 'Em todos os Poderes%' THEN
           CASE WHEN s.esf ILIKE 'Federal%' AND p.esfera = 'F' THEN 'alta'
                WHEN s.esf ILIKE 'Estadual%' AND p.esfera = 'E' AND s.uf_s = p.uf THEN 'alta'
                WHEN s.esf ILIKE 'Municipal%' AND p.esfera = 'M' AND s.uf_s = p.uf THEN 'media' END
      WHEN s.abr ILIKE 'Na Esfera e no Poder%' THEN
           CASE WHEN s.esf ILIKE 'Federal%' AND p.esfera = 'F' THEN 'media'
                WHEN s.esf ILIKE 'Estadual%' AND p.esfera = 'E' AND s.uf_s = p.uf THEN 'media'
                WHEN s.esf ILIKE 'Municipal%' AND p.esfera = 'M' AND s.uf_s = p.uf THEN 'baixa' END
      WHEN s.abr ILIKE 'No %rg_o sancionador' THEN
           CASE WHEN (s.esf ILIKE 'Federal%' AND p.esfera = 'F') OR (s.uf_s = p.uf AND (s.esf ILIKE 'Estadual%' AND p.esfera = 'E' OR s.esf ILIKE 'Municipal%' AND p.esfera = 'M')) THEN 'baixa' END
      ELSE CASE WHEN (s.esf ILIKE 'Federal%' AND p.esfera = 'F') OR (s.uf_s = p.uf) THEN 'media' END
    END AS gravidade
  FROM pncp p JOIN sancoes s ON s.doc = p.doc14 AND p.doc14 <> '00000000000000'
  WHERE p.data_assinatura >= s.ini AND (s.fim IS NULL OR p.data_assinatura <= s.fim) AND p.valor_global > 0 AND NOT p.estatal
)
SELECT 'R02' AS regra, gravidade, id, fornecedor, doc14 AS doc, orgao, esfera, uf, municipio, objeto, valor_global AS valor, data_assinatura AS data,
       tipo_contrato, categoria, lista, sancao_tipo, orgao_sancionador, alcance, sancao_ini, sancao_fim
FROM cruz WHERE gravidade IS NOT NULL;
