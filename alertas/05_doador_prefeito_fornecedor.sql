-- R05: sócio de empresa doou para a campanha do PREFEITO ELEITO (2024) e a empresa passou a ser contratada pela prefeitura dessa cidade (desde jan/2025).
-- Doação de sócio a candidato é legal; o ponto de atenção é a empresa do doador fechar contratos com a prefeitura de quem ele ajudou a eleger.
WITH eleitos AS (
  SELECT SQ_CANDIDATO AS sq, NM_CANDIDATO AS prefeito, SG_PARTIDO AS partido, SG_UF AS uf, strip_accents(upper(NM_UE)) AS cidade
  FROM tse_cand
  WHERE DS_CARGO = 'PREFEITO' AND DS_SIT_TOT_TURNO IN ('ELEITO', 'ELEITO POR QP', 'ELEITO POR MÉDIA')
), doacoes AS (
  SELECT e.uf, e.cidade, e.prefeito, e.partido,
         regexp_replace(r.NR_CPF_CNPJ_DOADOR,'\D','','g') AS cpf,
         strip_accents(upper(coalesce(nullif(r.NM_DOADOR_RFB,''), r.NM_DOADOR))) AS nome,
         sum(try_cast(replace(r.VR_RECEITA,',','.') AS DOUBLE)) AS doado
  FROM tse_receitas r JOIN eleitos e ON e.sq = r.SQ_CANDIDATO
  WHERE r.DS_ORIGEM_RECEITA ILIKE '%pessoas f%' AND length(regexp_replace(r.NR_CPF_CNPJ_DOADOR,'\D','','g')) = 11
  GROUP BY ALL
), vinculo AS (
  SELECT d.uf, d.cidade, d.prefeito, d.partido, d.nome AS doador, d.doado, s.cnpj_basico, s.qualificacao
  FROM doacoes d JOIN socios_pf s ON s.nome = d.nome AND s.mid6 = substr(d.cpf, 4, 6)
), ctr AS (
  SELECT p.*, left(p.doc14, 8) AS basico
  FROM pncp p
  WHERE p.esfera = 'M' AND p.data_assinatura >= DATE '2025-01-01' AND p.tipo_pessoa = 'PJ' AND p.valor_global >= 50000
    AND NOT p.erro_valor AND NOT p.credenciamento AND p.n_mesmo_valor < 3 AND NOT p.estatal
)
SELECT 'R05' AS regra,
       CASE WHEN c.valor_global >= 1000000 AND v.doado >= 5000 THEN 'alta'
            WHEN c.valor_global >= 300000 AND (v.doado >= 2000 OR v.qualificacao = '49') THEN 'media' ELSE 'baixa' END AS gravidade,
       c.id, c.fornecedor, c.doc14 AS doc, c.orgao, c.esfera, c.uf, c.municipio, c.objeto, c.valor_global AS valor, c.data_assinatura AS data,
       c.tipo_contrato, c.categoria, v.doador, v.doado AS doacao, v.prefeito, v.partido, v.qualificacao
FROM ctr c JOIN vinculo v ON v.cnpj_basico = c.basico AND v.uf = c.uf AND v.cidade = strip_accents(upper(c.municipio));
