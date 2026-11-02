"""Gera web/public/data/alertas.json (todas as regras) a partir do DuckDB + Parquets.
Cada alerta: id, regra, gravidade, empresa, cnpj, origem, local, total, n, manchete, numeros, tabela, secoes, checagem, fontes."""
import json, os, pathlib, datetime, glob, re, duckdb

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)  # as regras usam caminhos relativos (dados/...)
LIMITE = 150     # alertas por regra no painel (os de maior valor/gravidade)
con = duckdb.connect(str(RAIZ / "dados" / "radar.duckdb"))
BRASILIA = {"lat": -15.7997, "lon": -47.8645, "nome": "Brasília"}
ORDEM = {"alta": 0, "media": 1, "baixa": 2}
NOME_REGRA = {"R01": "Empresa punida recebeu cota parlamentar", "R02": "Contrato com empresa punida",
              "R03": "Empresa nova com contrato grande", "R04": "Contrato gigante para empresa pequena", "R05": "Doador do prefeito virou fornecedor", "R06": "Possível fracionamento de compras", "R07": "Fornecedor concentra os contratos da prefeitura", "R08": "Sócio em paraíso fiscal"}

def sql(nome): return (RAIZ / "alertas" / nome).read_text(encoding="utf-8").strip().rstrip(";")
def fmt_cnpj(d): return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}" if len(d) == 14 and not d.startswith("000") else f"CPF ***{d[-8:-2]}**"
def brl(v): return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
def url_pncp(i):
    m = re.match(r"(\d{14})-\d-(\d+)/(\d{4})", i or "")
    return f"https://pncp.gov.br/app/contratos/{m.group(1)}/{m.group(3)}/{int(m.group(2))}" if m else None
def cel(t, s=None, u=None, v=False): return {"t": t, "s": s, "u": u, "v": v}

# ---------- apoio: coordenadas ----------
con.execute("create or replace table _ibge as select cast(codigo_ibge as varchar) ibge, lat, lon, nome from mun_ibge")
est_glob = (RAIZ / "dados" / "cnpj" / "estabelecimentos_*.parquet").as_posix()
def local_de(docs):
    if not docs: return {}
    con.execute("create or replace temp table _docs(doc varchar)"); con.executemany("insert into _docs values (?)", [(d,) for d in docs])
    r = con.execute(f"""select d.doc, any_value(m.lat), any_value(m.lon), any_value(m.nome), any_value(e.uf)
       from _docs d join read_parquet('{est_glob}') e on e.cnpj=d.doc join mun_coord m on m.rfb=e.municipio and m.uf=e.uf group by d.doc""").fetchall()
    return {d: {"lat": a, "lon": b, "cidade": c, "uf": u} for d, a, b, c, u in r}
def origem_de(ibges):
    if not ibges: return {}
    con.execute("create or replace temp table _ib(ibge varchar)"); con.executemany("insert into _ib values (?)", [(i,) for i in ibges if i])
    return {i: {"lat": a, "lon": b, "nome": n} for i, a, b, n in con.execute("select i.ibge, m.lat, m.lon, m.nome from _ib i join _ibge m on m.ibge=i.ibge").fetchall()}

alertas = []

# ================= R01 (cota parlamentar) =================
con.execute("create or replace table alerta01 as " + sql("01_sancionada_recebendo_cota.sql"))
emp = con.execute("""select cnpj, fornecedor, any_value(lista), any_value(categoria), any_value(orgao), any_value(alcance), min(sancao_inicio), max(sancao_fim),
  sum(valor), count(*), min(emissao), max(emissao) from alerta01 group by cnpj, fornecedor""").fetchall()
pag = con.execute("select cnpj, casa, parlamentar, partido, uf, emissao, valor, tipo, url from alerta01 order by emissao").fetchall()
loc01 = local_de([e[0] for e in emp]); por = {}
for c, casa, parl, part, uf, em, val, tipo, url in pag:
    por.setdefault(c, []).append([cel(str(em)), cel(parl, f"{casa}{' · ' + part if part else ''}{'/' + uf if uf else ''}"), cel((tipo or "").strip().capitalize()[:60]), cel(brl(val), v=True), cel("ver nota", u=url) if url else cel("–")])
for cnpj, nome, lista, cat, orgao, alc, ini, fim, total, n, d1, d2 in emp:
    RAW = {"AMPLO (todas": "Todas as Esferas em todos os Poderes", "AMPLO (todos": "Em todos os Poderes da Esfera do órgão sancionador",
           "MÉDIO": "Na Esfera e no Poder do órgão sancionador", "RESTRITO": "No órgão sancionador"}
    alc = next((v for k, v in RAW.items() if alc.startswith(k)), "Sem Informação")
    gr = "alta" if alc.startswith(("Todas", "Em todos")) else ("baixa" if alc.startswith("No ") else "media")
    alertas.append({"id": f"R01-{cnpj}", "regra": "R01", "gravidade": gr, "empresa": nome, "cnpj": fmt_cnpj(cnpj), "total": total, "n": n, "inicio": str(d1), "fim": str(d2),
      "origem": BRASILIA, "local": loc01.get(cnpj),
      "manchete": {"tipo": "R01", "sancao": cat, "lista": lista}, "tabela": {"titulo": "Rastro do dinheiro", "cols": ["Data", "Parlamentar", "Gasto", "Valor", ""], "linhas": por[cnpj]},
      "sancao": {"lista": lista, "tipo": cat, "orgao": orgao, "alcance": alc, "inicio": str(ini), "fim": str(fim) if fim else None}})

# ================= regras de contratos (precisam do PNCP em massa) =================
if glob.glob(str(RAIZ / "dados" / "pncp" / "*.parquet")):
    con.execute(sql("00_base_contratos.sql").replace("dados/pncp/", (RAIZ / "dados" / "pncp").as_posix() + "/").replace("dados/cnpj/", (RAIZ / "dados" / "cnpj").as_posix() + "/"))
    cols = "id, fornecedor, doc, orgao, esfera, uf, municipio, objeto, valor, data, tipo_contrato, categoria"
    def montar(regra, tabela, extra):
        rows = con.execute(f"select * from {tabela} order by case gravidade when 'alta' then 0 when 'media' then 1 else 2 end, valor desc").fetchall()
        desc = [d[0] for d in con.description]
        total_regra = len(rows)
        rows = rows[:LIMITE * 6] if regra == "R02" else rows[:LIMITE]
        docs = [r[desc.index("doc")] for r in rows]; loc = local_de(set(docs))
        ib = origem_de({str(r[desc.index("id")]) and None for r in rows})
        return rows, desc, loc, total_regra
    # R02 agrupado por empresa
    for regra, arq in (("R02", "02_contrato_com_sancionada.sql"), ("R03", "03_empresa_nova_contrato_grande.sql"), ("R04", "04_capital_pequeno_contrato_gigante.sql"), ("R05", "05_doador_prefeito_fornecedor.sql"), ("R06", "06_fracionamento.sql"), ("R07", "07_concentracao_fornecedor.sql"), ("R08", "08_socio_em_paraiso_fiscal.sql")):
        con.execute(f"create or replace table t_{regra} as " + sql(arq))
    ibge_por_id = {}
    # código IBGE do órgão (para origem no mapa)
    ib_rows = con.execute("select id, ibge from pncp").fetchall() if False else []
    for regra in ("R02", "R03", "R04", "R05", "R06", "R07", "R08"):
        rows = con.execute(f"select * from t_{regra} order by case gravidade when 'alta' then 0 when 'media' then 1 else 2 end, valor desc").fetchall()
        desc = [d[0] for d in con.description]; ix = {k: i for i, k in enumerate(desc)}
        if regra in ("R02", "R05", "R06", "R07", "R08"):
            grupos = {}
            for r in rows: grupos.setdefault(r[ix["doc"]] if regra == "R02" else (r[ix["grupo"]] if regra in ("R06", "R07", "R08") else (r[ix["doc"]], r[ix["municipio"]], r[ix["uf"]])), []).append(r)
            itens = sorted(grupos.values(), key=lambda g: (ORDEM[g[0][ix["gravidade"]]], -sum(x[ix["valor"]] for x in g)))[:LIMITE]
        else:
            itens = [[r] for r in rows[:LIMITE]]
        loc = local_de({g[0][ix["doc"]] for g in itens})
        for g in itens:
            r0 = g[0]; doc = r0[ix["doc"]]; tot = sum(x[ix["valor"]] for x in g)
            tab = [[cel(str(x[ix["data"]])), cel(x[ix["orgao"]][:46], f"{x[ix['municipio']]}/{x[ix['uf']]}"), cel((x[ix["objeto"]] or "")[:90]), cel(brl(x[ix["valor"]]), v=True), cel("ver contrato", u=url_pncp(x[ix["id"]])) if url_pncp(x[ix["id"]]) else cel("–")] for x in sorted(g, key=lambda y: y[ix["data"]])[:12]]
            a = {"id": f"{regra}-{r0[ix['grupo']]}" if regra in ("R06", "R07", "R08") else f"{regra}-{doc}" if regra == "R02" else (f"{regra}-{doc}-{r0[ix['municipio']]}-{r0[ix['uf']]}" if regra == "R05" else f"{regra}-{doc}-{r0[ix['id']]}"), "regra": regra, "gravidade": r0[ix["gravidade"]], "empresa": r0[ix["fornecedor"]], "cnpj": fmt_cnpj(doc),
                 "total": tot, "n": len(g), "inicio": str(min(x[ix["data"]] for x in g)), "fim": str(max(x[ix["data"]] for x in g)),
                 "origem": None, "local": loc.get(doc), "orgao": r0[ix["orgao"]], "orgao_uf": r0[ix["uf"]], "orgao_municipio": r0[ix["municipio"]],
                 "tabela": {"titulo": "Contratos", "cols": ["Data", "Órgão contratante", "Objeto", "Valor", ""], "linhas": tab}}
            if regra == "R02":
                a["manchete"] = {"tipo": "R02", "sancao": r0[ix["sancao_tipo"]], "lista": r0[ix["lista"]]}
                a["sancao"] = {"lista": r0[ix["lista"]], "tipo": r0[ix["sancao_tipo"]], "orgao": r0[ix["orgao_sancionador"]], "alcance": r0[ix["alcance"]], "inicio": str(r0[ix["sancao_ini"]]), "fim": str(r0[ix["sancao_fim"]]) if r0[ix["sancao_fim"]] else None}
            elif regra == "R06":
                vals = [x[ix["valor"]] for x in g]
                a["manchete"] = {"tipo": "R06", "minimo": min(vals), "maximo": max(vals), "tri": r0[ix["tri"]]}
            elif regra == "R08":
                nome_s = r0[ix["socio"]] or ""
                parece_pj = bool(re.search(r"\b(LTD|LIMITED|INC|S\.?A|SA|CORP|HOLDING|LLC|GMBH|FUND|TRUST|PARTICIPA|INVEST|CAPITAL|GROUP|SARL|B\.?V|AG|PARTNERS|VENTURES|SICAV)\b", nome_s.upper()))
                a["manchete"] = {"tipo": "R08", "pais": (r0[ix["pais_socio"]] or "").title(), "nivel": r0[ix["nivel"]], "socio": nome_s.title() if parece_pj else "pessoa física no exterior", "qualificacao": r0[ix["qualificacao"]]}
            elif regra == "R07":
                a["manchete"] = {"tipo": "R07", "share": r0[ix["share"]], "total_orgao": r0[ix["total_orgao"]], "ano": r0[ix["ano"]]}
            elif regra == "R05":
                rb = max(g, key=lambda x: x[ix["doacao"]]); nome = [w for w in rb[ix["doador"]].split() if w]
                mascarado = nome[0].title() + " " + " ".join(w[0] + "." for w in nome[1:]) if nome else "sócio"
                a["manchete"] = {"tipo": "R05", "doador": mascarado, "doacao": rb[ix["doacao"]], "prefeito": rb[ix["prefeito"]].title(), "partido": rb[ix["partido"]],
                                 "cidade": (r0[ix["municipio"]] or "").title(), "uf": r0[ix["uf"]], "qualificacao": rb[ix["qualificacao"]]}
            elif regra == "R03":
                a["manchete"] = {"tipo": "R03", "abertura": str(r0[ix["abertura"]]), "dias": r0[ix["dias_de_vida"]], "capital": r0[ix["capital_social"]], "porte": r0[ix["porte"]]}
            else:
                a["manchete"] = {"tipo": "R04", "capital": r0[ix["capital_social"]], "vezes": r0[ix["vezes_o_capital"]], "porte": r0[ix["porte"]]}
            alertas.append(a)
    # origem = município do órgão contratante (pelo nome/UF -> coordenadas)
    con.execute("create or replace temp table _org(chave varchar)")
    chaves = {(a.get("orgao_municipio"), a.get("orgao_uf")) for a in alertas if a.get("orgao_municipio")}
    uf_cod = dict(con.execute("select uf, cast(cod as varchar) from uf_cod").fetchall())
    mapa = {}
    for mun, uf in chaves:
        r = con.execute("select lat, lon from mun_ibge where strip_accents(upper(nome))=strip_accents(upper(?)) and codigo_uf=?", [mun, uf_cod.get(uf)]).fetchone()
        if r: mapa[(mun, uf)] = {"lat": r[0], "lon": r[1], "nome": mun}
    for a in alertas:
        if a["regra"] != "R01": a["origem"] = mapa.get((a.get("orgao_municipio"), a.get("orgao_uf")), BRASILIA)

contagem = {}
for a in alertas: contagem.setdefault(a["regra"], {"alta": 0, "media": 0, "baixa": 0})[a["gravidade"]] += 1
saida = {"gerado": str(datetime.date.today()), "regras": NOME_REGRA, "contagem": contagem, "alertas": alertas}
out = RAIZ / "web" / "public" / "data"; out.mkdir(parents=True, exist_ok=True)
(out / "alertas.json").write_text(json.dumps(saida, ensure_ascii=False, default=str), encoding="utf-8")
print(len(alertas), "alertas |", {k: sum(v.values()) for k, v in contagem.items()}, "|", sum(1 for a in alertas if a["local"]), "localizados")
