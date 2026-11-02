-- Visões comuns às regras de contratos. Higiene dos dados:
--  * descarta datas/valores impossíveis (erros de digitação na origem do PNCP);
--  * erro_valor: sinais objetivos de valor digitado errado (ver abaixo) -> as regras R03/R04 ignoram;
--  * credenciamento/valor repetido na mesma compra: o valor é do edital, não do contrato;
--  * consórcio/concessão/SPE/PPP: nascem recentes por desenho.
CREATE OR REPLACE VIEW emp AS
SELECT cnpj_basico, razao_social, natureza, capital_social, porte FROM read_parquet('dados/cnpj/empresas_*.parquet');

DROP TABLE IF EXISTS pncp;
CREATE TABLE pncp AS
WITH base AS (
  SELECT *, lpad(regexp_replace(coalesce(fornecedor_doc,''),'\D','','g'),14,'0') AS doc14,
         count(*) OVER (PARTITION BY compra, valor_global) AS n_mesmo_valor,
         count(*) OVER (PARTITION BY compra) AS n_na_compra,
         median(valor_global) OVER (PARTITION BY compra) AS med_compra,
         count(*) OVER (PARTITION BY orgao_cnpj) AS n_orgao,
         median(valor_global) OVER (PARTITION BY orgao_cnpj) AS med_orgao,
         (coalesce(objeto,'') ILIKE '%credenciamento%' OR coalesce(objeto,'') ILIKE '%chamamento p_blico%') AS credenciamento,
         (coalesce(objeto,'') ILIKE '%concess%' OR coalesce(objeto,'') ILIKE '%parceria p_blico%' OR trim(coalesce(fornecedor,'')) = '' OR
          regexp_matches(upper(coalesce(fornecedor,'')), 'CONCESSION|CONSORCIO|CONSÓRCIO|\bSPE\b|S\.?P\.?E\.?\s|PARCERIA|PPP|PROPOSITO ESPECIFICO|PROPÓSITO ESPECÍFICO|FUNDO |COOPERATIVA|ASSOCIACAO|ASSOCIAÇÃO|FUNDACAO|FUNDAÇÃO|INSTITUTO|ORGANIZA[CÇ][AÃ]O SOCIAL|IRMANDADE|SANTA CASA|HOSPITAL|BENEFICENTE|SOCIEDADE BENEFICENTE')) AS tipo_especial
  FROM read_parquet('dados/pncp/*.parquet')
  WHERE data_assinatura BETWEEN DATE '2020-01-01' AND current_date AND valor_global BETWEEN 0 AND 3000000000
), pop AS (SELECT cod_ibge::VARCHAR AS ibge, max(populacao) AS populacao FROM siconfi_entes GROUP BY 1),
-- licitação de origem (PNCP/compras): modalidade e valores homologado/estimado; vazia se ainda não baixada
cmp AS (SELECT id, modalidade, amparo, valor_estimado, valor_homologado, greatest(coalesce(valor_homologado,0), coalesce(valor_estimado,0)) AS valor_licitado
        FROM read_parquet('dados/compras/*.parquet', union_by_name=true) WHERE id IS NOT NULL
        QUALIFY row_number() OVER (PARTITION BY id ORDER BY publicado DESC NULLS LAST) = 1)
SELECT b.*, p.populacao, ee.natureza, cm.modalidade, cm.amparo, cm.valor_licitado,
  (cm.modalidade ILIKE '%dispensa%' OR cm.modalidade ILIKE '%inexigibilidade%') AS contratacao_direta,
  (cm.valor_licitado > 0 AND b.valor_global > 3 * cm.valor_licitado) AS f_acima_da_licitacao,   -- contrato muito maior que a licitação que o originou
  (ee.natureza LIKE '1%' OR ee.natureza IN ('2011','2038')) AS estatal,   -- administração pública, empresa pública, economia mista: contratar é esperado
  (b.valor_inicial > 0 AND b.valor_global > 20 * b.valor_inicial)                                   AS f_global_vs_inicial,
  (b.esfera = 'M' AND p.populacao > 0 AND b.valor_global > p.populacao * 10000)                      AS f_maior_que_orcamento,
  (b.n_na_compra >= 3 AND b.med_compra > 0 AND b.valor_global > 100 * b.med_compra)                  AS f_outlier_na_compra,
  (b.n_orgao >= 20 AND b.med_orgao > 0 AND b.valor_global > 1000 * b.med_orgao AND b.valor_global >= 50000000) AS f_outlier_no_orgao,
  (b.valor_global >= 10000000 AND b.valor_global % 1000 = 0 AND b.n_orgao >= 10 AND b.med_orgao > 0
     AND b.valor_global > 100 * b.med_orgao AND b.valor_global / 1000 <= 20 * b.med_orgao)                    AS f_escala_mil,
  (b.valor_inicial > 0 AND b.valor_global > 20 * b.valor_inicial)
   OR (cm.valor_licitado > 0 AND b.valor_global > 3 * cm.valor_licitado)
   OR (b.valor_inicial = 0 AND b.valor_global >= 5000000)   -- sem valor inicial e valor global alto: quase sempre digitação ou estimativa de ata
   OR (b.valor_global >= 10000000 AND b.valor_global % 1000 = 0 AND b.n_orgao >= 10 AND b.med_orgao > 0
       AND b.valor_global > 100 * b.med_orgao AND b.valor_global / 1000 <= 20 * b.med_orgao)
   OR (b.esfera = 'M' AND p.populacao > 0 AND b.valor_global > p.populacao * 10000)
   OR (b.n_na_compra >= 3 AND b.med_compra > 0 AND b.valor_global > 100 * b.med_compra)
   OR (b.n_orgao >= 20 AND b.med_orgao > 0 AND b.valor_global > 1000 * b.med_orgao AND b.valor_global >= 50000000) AS erro_valor
FROM base b LEFT JOIN pop p ON p.ibge = b.ibge
LEFT JOIN emp ee ON ee.cnpj_basico = left(b.doc14, 8)
LEFT JOIN cmp cm ON cm.id = b.compra
-- dedupe: o mesmo contrato aparece mais de uma vez (retificações/republicações)
QUALIFY row_number() OVER (PARTITION BY b.orgao_cnpj, b.doc14, b.data_assinatura, b.valor_global, left(b.objeto, 80) ORDER BY b.id) = 1;

CREATE OR REPLACE VIEW estab AS
SELECT cnpj, cnpj_basico, matriz, situacao, try_strptime(data_inicio,'%Y%m%d')::date AS abertura, cnae, uf, municipio
FROM read_parquet('dados/cnpj/estabelecimentos_*.parquet');

