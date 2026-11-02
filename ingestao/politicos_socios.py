"""R10: político eleito que é sócio de empresa que vende ao governo.
Cruza sócios da Receita (nome + 6 dígitos centrais do CPF, que a Receita publica mascarado) com candidatos eleitos do TSE (2018, 2022, 2024, 2026, com CPF),
e depois com os contratos do PNCP da empresa. Casamento por nome completo + CPF parcial, o que torna homônimo praticamente impossível.
Roda DEPOIS de exportar_web.py (usa a tabela pncp já filtrada, sem valores com erro). Saída: data-publica/alertas_extra_r10.json"""
import json, os, pathlib, datetime, re, duckdb

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
c = globals().get("con") or duckdb.connect("dados/radar.duckdb", read_only=True)   # dentro do exportador reaproveita a conexão (e a tabela pncp já filtrada)
T = lambda n: f"read_parquet('dados/tse/{n}.parquet')"
cols = "NM_CANDIDATO, NR_CPF_CANDIDATO, DS_CARGO, SG_UF, NM_UE, SG_PARTIDO, DS_SIT_TOT_TURNO, {ano} ano"
partes = [f"select {cols.format(ano=a)} from {T('consulta_cand_' + str(a))}" for a in (2018, 2022, 2026)] + [f"select {cols.format(ano=2024)} from {T('cand_2024')}"]
c.execute("create temp table eleitos as select strip_accents(upper(trim(NM_CANDIDATO))) nome, substr(NR_CPF_CANDIDATO, 4, 6) cpf6, DS_CARGO cargo, SG_UF uf, NM_UE ue, SG_PARTIDO partido, ano "
          "from (" + " union all ".join(partes) + ") where DS_SIT_TOT_TURNO like 'ELEITO%' and length(NR_CPF_CANDIDATO) = 11 and DS_CARGO not in ('VICE-PREFEITO', 'VICE-GOVERNADOR', 'VICE-PRESIDENTE', '1º SUPLENTE', '2º SUPLENTE')")
print(c.execute("select count(*) from eleitos").fetchone()[0], "eleitos com CPF", flush=True)
c.execute("""create temp table soc as select cnpj_basico, strip_accents(upper(trim(nome_socio))) nome, substr(doc_socio, 4, 6) cpf6, qualificacao, data_entrada
   from read_parquet('dados/cnpj/socios_[0-9]*.parquet') where tipo_socio = '2' and doc_socio like '***%'""")
c.execute("""create temp table achados as select e.nome, e.cargo, e.uf, e.ue, e.partido, e.ano, s.cnpj_basico, s.qualificacao, s.data_entrada
   from eleitos e join soc s on s.nome = e.nome and s.cpf6 = e.cpf6""")
print(c.execute("select count(*), count(distinct cnpj_basico) from achados").fetchone(), "políticos-sócios / empresas", flush=True)
c.execute("""create temp table cont as select a.nome, a.cargo, a.uf polit_uf, a.ue, a.partido, a.ano, a.qualificacao, a.data_entrada, p.id, p.fornecedor, p.doc14, p.orgao, p.esfera, p.uf, p.municipio, p.objeto,
      p.valor_global valor, p.data_assinatura data, p.modalidade
   from achados a join pncp p on left(p.doc14, 8) = a.cnpj_basico
   where p.valor_global >= 50000 and not p.erro_valor and not p.estatal and p.data_assinatura >= date '2025-01-01'""")
rows = c.execute("select * from cont order by valor desc").fetchall()
desc = [d[0] for d in c.description]
ix = {k: i for i, k in enumerate(desc)}
print(len(rows), "contratos de empresas de políticos", flush=True)
norm = lambda s: re.sub(r"\s+", " ", "".join(ch for ch in __import__("unicodedata").normalize("NFD", (s or "").upper()) if __import__("unicodedata").category(ch) != "Mn")).strip()
fmt_cnpj = lambda d: f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"
brl = lambda v: "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
CARGOS_FED = ("DEPUTADO FEDERAL", "SENADOR", "PRESIDENTE", "GOVERNADOR", "DEPUTADO ESTADUAL", "DEPUTADO DISTRITAL")
grupos = {}
POSSE = {2018: "2019-02-01", 2022: "2023-02-01", 2024: "2025-01-01", 2026: "2027-02-01"}
vistos = set()
for r in rows:
    k = (r[ix["nome"]], r[ix["doc14"]][:8])
    if (k, r[ix["id"]]) in vistos: continue   # a mesma pessoa eleita em mais de uma eleição repetiria o contrato
    vistos.add((k, r[ix["id"]])); grupos.setdefault(k, []).append(r)
ano_min = {}
for r in rows:
    k = (r[ix["nome"]], r[ix["doc14"]][:8]); ano_min[k] = min(ano_min.get(k, 9999), r[ix["ano"]])
alertas = []
for (nome, basico), g in grupos.items():
    r0 = g[0]
    cargo = r0[ix["cargo"]]
    mesmo_mun = any(x[ix["esfera"]] == "M" and norm(x[ix["municipio"]]) == norm(r0[ix["ue"]]) for x in g) if cargo in ("PREFEITO", "VEREADOR") else False
    posse = POSSE[ano_min[(nome, basico)]]
    apos = [x for x in g if str(x[ix["data"]]) >= posse]
    grav = "alta" if apos and (cargo in CARGOS_FED or mesmo_mun) else "media"
    total = sum(x[ix["valor"]] for x in g)
    if total < 100000: continue
    antes = r0[ix["data_entrada"]] and str(r0[ix["data_entrada"]]) <= min(str(x[ix["data"]]).replace("-", "") for x in g)
    tab = [[{"t": str(x[ix["data"]]), "s": None, "u": None, "v": False}, {"t": (x[ix["orgao"]] or "")[:46], "s": f"{x[ix['municipio']]}/{x[ix['uf']]}", "u": None, "v": False},
            {"t": (x[ix["objeto"]] or "")[:90], "s": ("como contratou: " + x[ix["modalidade"]]) if x[ix["modalidade"]] else None, "u": None, "v": False}, {"t": brl(x[ix["valor"]]), "s": None, "u": None, "v": True},
            {"t": "ver contrato", "s": None, "u": (lambda m: f"https://pncp.gov.br/app/contratos/{m.group(1)}/{m.group(3)}/{int(m.group(2))}" if m else None)(re.match(r"^(\d{14})-\d+-(\d+)/(\d{4})", x[ix["id"]] or "")), "v": False}]
           for x in sorted(g, key=lambda y: y[ix["data"]])[:12]]
    alertas.append({"id": f"R10-{basico}-{norm(nome)[:12].replace(' ', '')}", "regra": "R10", "gravidade": grav, "empresa": r0[ix["fornecedor"]] or "", "cnpj": fmt_cnpj(r0[ix["doc14"]]), "total": total, "n": len(g),
        "inicio": str(min(x[ix["data"]] for x in g)), "fim": str(max(x[ix["data"]] for x in g)), "origem": {"lat": -15.7997, "lon": -47.8645, "nome": "Brasília"}, "local": None,
        "orgao": r0[ix["orgao"]], "orgao_uf": r0[ix["uf"]], "orgao_municipio": r0[ix["municipio"]],
        "manchete": {"tipo": "R10", "politico": nome.title(), "cargo": cargo.title(), "ano": r0[ix["ano"]], "partido": r0[ix["partido"]], "uf": r0[ix["polit_uf"]], "ue": (r0[ix["ue"]] or "").title(),
                     "qualificacao": r0[ix["qualificacao"]], "mesmo_municipio": bool(mesmo_mun), "posse": posse, "apos_posse": len(apos), "ano_min": ano_min[(nome, basico)], "entrou_antes": bool(antes), "orgaos": sorted({x[ix["orgao"]] for x in g})[:3]},
        "tabela": {"titulo": "Contratos da empresa", "cols": ["Data", "Órgão contratante", "Objeto", "Valor", ""], "linhas": tab}})
alertas.sort(key=lambda a: ({"alta": 0, "media": 1}[a["gravidade"]], -a["total"]))
alertas = alertas[:150]
(RAIZ / "data-publica" / "alertas_extra_r10.json").write_text(json.dumps(alertas, ensure_ascii=False, default=str), encoding="utf-8")
print(len(alertas), "alertas R10;", sum(1 for a in alertas if a["gravidade"] == "alta"), "altos")
