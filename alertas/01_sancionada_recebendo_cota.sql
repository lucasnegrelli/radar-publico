-- ALERTA 1: fornecedor pago com cota parlamentar (Câmara e Senado) durante período em que
-- constava no CEIS/CNEP. Ponto de atenção, não prova de irregularidade.
-- Coluna "alcance" separa o que bloqueia contratação em toda a administração do que é restrito a um órgão.
WITH sancoes AS (
  SELECT 'CEIS' AS lista, lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\D','','g'),14,'0') AS doc,
         "CATEGORIA DA SANÇÃO" AS categoria, "ÓRGÃO SANCIONADOR" AS orgao, "ABRAGÊNCIA DA SANÇÃO" AS abr,
         try_strptime("DATA INÍCIO SANÇÃO",'%d/%m/%Y')::date AS ini, try_strptime("DATA FINAL SANÇÃO",'%d/%m/%Y')::date AS fim
  FROM ceis
  UNION ALL
  SELECT 'CNEP', lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\D','','g'),14,'0'),
         "CATEGORIA DA SANÇÃO","ÓRGÃO SANCIONADOR","ABRAGÊNCIA DA SANÇÃO",
         try_strptime("DATA INÍCIO SANÇÃO",'%d/%m/%Y')::date, try_strptime("DATA FINAL SANÇÃO",'%d/%m/%Y')::date
  FROM cnep
), gastos AS (
  SELECT 'Câmara' AS casa, txNomeParlamentar AS parlamentar, sgPartido AS partido, sgUF AS uf,
         txtFornecedor AS fornecedor, lpad(regexp_replace(txtCNPJCPF,'\D','','g'),14,'0') AS doc,
         try_cast(left(datEmissao,10) AS date) AS emissao, try_cast(vlrLiquido AS double) AS valor,
         txtDescricao AS tipo, urlDocumento AS url
  FROM camara_ceap
  UNION ALL
  SELECT 'Senado', SENADOR, NULL, NULL, FORNECEDOR, lpad(regexp_replace(CNPJ_CPF,'\D','','g'),14,'0'),
         try_strptime(DATA,'%d/%m/%Y')::date, try_cast(replace(VALOR_REEMBOLSADO,',','.') AS double), TIPO_DESPESA, NULL
  FROM senado_ceaps
)
SELECT g.casa, g.parlamentar, g.partido, g.uf, g.fornecedor, g.doc AS cnpj, s.lista, s.categoria, s.orgao,
       CASE WHEN s.abr ILIKE 'Todas as Esferas%' THEN 'AMPLO (todas as esferas)'
            WHEN s.abr ILIKE 'Em todos os Poderes%' THEN 'AMPLO (todos os poderes da esfera)'
            WHEN s.abr ILIKE 'Na Esfera e no Poder%' THEN 'MÉDIO (esfera e poder do órgão)'
            WHEN s.abr ILIKE 'No %rg_o sancionador' THEN 'RESTRITO (só no órgão)'
            ELSE 'NÃO INFORMADO' END AS alcance,
       s.ini AS sancao_inicio, s.fim AS sancao_fim, g.emissao, g.valor, g.tipo, g.url
FROM gastos g JOIN sancoes s ON g.doc = s.doc AND g.doc <> '00000000000000'
WHERE g.emissao >= s.ini AND (s.fim IS NULL OR g.emissao <= s.fim)
ORDER BY (alcance LIKE 'AMPLO%') DESC, g.valor DESC;
