-- Visões comuns às regras de contratos (rodar antes das regras 02..05).
CREATE OR REPLACE VIEW pncp AS
SELECT *, lpad(regexp_replace(coalesce(fornecedor_doc,''),'\D','','g'),14,'0') AS doc14
FROM read_parquet('dados/pncp/*.parquet');

CREATE OR REPLACE VIEW estab AS
SELECT cnpj, cnpj_basico, matriz, situacao, try_strptime(data_inicio,'%Y%m%d')::date AS abertura, cnae, uf, municipio
FROM read_parquet('dados/cnpj/estabelecimentos_*.parquet');

CREATE OR REPLACE VIEW emp AS
SELECT cnpj_basico, razao_social, capital_social, porte FROM read_parquet('dados/cnpj/empresas_*.parquet');
