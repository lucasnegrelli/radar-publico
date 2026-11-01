-- Visões comuns às regras de contratos. Higiene dos dados:
--  * descarta datas/valores impossíveis (erros de digitação na origem do PNCP);
--  * marca contratos cujo valor global se repete em vários fornecedores da mesma compra (credenciamento/ata: o valor é do edital, não do contrato);
--  * marca objetos de credenciamento e fornecedores que são consórcio/concessão/SPE (nascem recentes por desenho).
CREATE OR REPLACE VIEW pncp AS
SELECT *, lpad(regexp_replace(coalesce(fornecedor_doc,''),'\D','','g'),14,'0') AS doc14,
       count(*) OVER (PARTITION BY compra, valor_global) AS n_mesmo_valor,
       (coalesce(objeto,'') ILIKE '%credenciamento%' OR coalesce(objeto,'') ILIKE '%chamamento p_blico%') AS credenciamento,
       (coalesce(objeto,'') ILIKE '%concess%' OR coalesce(objeto,'') ILIKE '%parceria p_blico%' OR trim(coalesce(fornecedor,'')) = '' OR
        regexp_matches(upper(coalesce(fornecedor,'')), 'CONCESSION|CONSORCIO|CONSÓRCIO|\bSPE\b|S\.?P\.?E\.?\s|PARCERIA|PPP|PROPOSITO ESPECIFICO|PROPÓSITO ESPECÍFICO|FUNDO |COOPERATIVA|ASSOCIACAO|ASSOCIAÇÃO')) AS tipo_especial
FROM read_parquet('dados/pncp/*.parquet')
WHERE data_assinatura BETWEEN DATE '2020-01-01' AND current_date
  AND valor_global BETWEEN 0 AND 3000000000;

CREATE OR REPLACE VIEW estab AS
SELECT cnpj, cnpj_basico, matriz, situacao, try_strptime(data_inicio,'%Y%m%d')::date AS abertura, cnae, uf, municipio
FROM read_parquet('dados/cnpj/estabelecimentos_*.parquet');

CREATE OR REPLACE VIEW emp AS
SELECT cnpj_basico, razao_social, capital_social, porte FROM read_parquet('dados/cnpj/empresas_*.parquet');
