-- ALERTA 1: fornecedor pago com cota parlamentar (Câmara) durante período em que
-- constava no CEIS/CNEP (impedida/inidônea). Ponto de atenção, não prova de irregularidade:
-- a sanção pode ter abrangência limitada (ex.: só um órgão ou um estado).
WITH sancoes AS (
  SELECT 'CEIS' AS lista, lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\D','','g'),14,'0') AS doc,
         "NOME DO SANCIONADO" AS nome, "CATEGORIA DA SANÇÃO" AS categoria, "ÓRGÃO SANCIONADOR" AS orgao,
         "ABRAGÊNCIA DA SANÇÃO" AS abrangencia,
         try_strptime("DATA INÍCIO SANÇÃO",'%d/%m/%Y')::date AS ini,
         try_strptime("DATA FINAL SANÇÃO",'%d/%m/%Y')::date AS fim
  FROM ceis
  UNION ALL
  SELECT 'CNEP', lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\D','','g'),14,'0'),
         "NOME DO SANCIONADO","CATEGORIA DA SANÇÃO","ÓRGÃO SANCIONADOR","ABRAGÊNCIA DA SANÇÃO",
         try_strptime("DATA INÍCIO SANÇÃO",'%d/%m/%Y')::date, try_strptime("DATA FINAL SANÇÃO",'%d/%m/%Y')::date
  FROM cnep
), gastos AS (
  SELECT txNomeParlamentar AS parlamentar, sgPartido AS partido, sgUF AS uf,
         txtFornecedor AS fornecedor, lpad(regexp_replace(txtCNPJCPF,'\D','','g'),14,'0') AS doc,
         try_cast(left(datEmissao,10) AS date) AS emissao, try_cast(vlrLiquido AS double) AS valor,
         txtDescricao AS tipo, urlDocumento AS url
  FROM camara_ceap
)
SELECT g.parlamentar, g.partido, g.uf, g.fornecedor, s.lista, s.categoria, s.orgao, s.abrangencia,
       s.ini AS sancao_inicio, s.fim AS sancao_fim, g.emissao, g.valor, g.tipo, g.url
FROM gastos g JOIN sancoes s ON g.doc = s.doc AND g.doc <> '00000000000000'
WHERE g.emissao >= s.ini AND (s.fim IS NULL OR g.emissao <= s.fim)
ORDER BY g.valor DESC;
