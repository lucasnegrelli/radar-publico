"""Fichas de PESSOA (políticos): candidaturas 2018/2022/2024, patrimônio declarado, financiamento de campanha, fornecedores de campanha,
cota parlamentar e alertas ligados -> web/public/data/pessoas/idx.json + sXX.json (fichas em lotes)
Só dado aberto (TSE, Câmara, Senado). Tudo "ponto de atenção", nunca veredito. Doador pessoa física sai com nome abreviado."""
import json, os, re, hashlib, pathlib, datetime, unicodedata, duckdb

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
OUT = RAIZ / "web/public/data/pessoas"
OUT.mkdir(parents=True, exist_ok=True)
c = duckdb.connect()  # em memória: só lê os parquets do TSE (roda igual no GitHub Actions)
for _v, _f in (("tse_cand", "cand_2024"), ("tse_receitas", "receitas_2024_todas"), ("ceis", "ceis"), ("cnep", "cnep")):
    c.execute(f"create view {_v} as select * from read_parquet('dados/tse/{_f}.parquet')")
T = lambda n: f"read_parquet('dados/tse/{n}.parquet')"
num = lambda col: f"try_cast(replace({col}, ',', '.') as double)"
norm = lambda s: "".join(ch for ch in unicodedata.normalize("NFD", (s or "").upper()) if unicodedata.category(ch) != "Mn")
def TT(s):
    peq = {"da", "de", "do", "das", "dos", "e", "di", "du"}
    sig = {"ltda", "sa", "s/a", "me", "epp", "eireli", "cnpj", "pt", "psdb", "mdb", "pl", "ii", "iii", "vgbl", "tv", "ong"}
    out = []
    for i, w in enumerate((s or "").lower().split()):
        out.append(w if (w in peq and i) else (w.upper() if w in sig else w[:1].upper() + w[1:]))
    return " ".join(out)
SQ = lambda s: re.sub(r"\s+", " ", norm(s)).strip()

# ---------- candidaturas (uma linha por ano+candidato; fica o último turno) ----------
partes = []
for ano in (2014, 2016, 2018, 2020, 2022, 2026):
    partes.append(f"""select '{ano}' ano, SQ_CANDIDATO sq, NM_CANDIDATO nome, NM_URNA_CANDIDATO urna, DS_CARGO cargo, SG_UF uf, NM_UE ue, SG_PARTIDO partido, NR_CANDIDATO numero,
      DS_SIT_TOT_TURNO sit, try_cast(NR_TURNO as int) turno, DT_NASCIMENTO nasc, DS_OCUPACAO ocup from {T('consulta_cand_' + str(ano))}""")
partes.append("""select ANO_ELEICAO ano, SQ_CANDIDATO sq, NM_CANDIDATO nome, NM_URNA_CANDIDATO urna, DS_CARGO cargo, SG_UF uf, NM_UE ue, SG_PARTIDO partido, NR_CANDIDATO numero,
      DS_SIT_TOT_TURNO sit, try_cast(NR_TURNO as int) turno, DT_NASCIMENTO nasc, DS_OCUPACAO ocup from tse_cand""")
c.execute("create temp table cand0 as " + " union all ".join(partes))
c.execute("create temp table cand as select * exclude(r) from (select *, row_number() over (partition by ano, sq order by turno desc nulls last) r from cand0) where r = 1")
PRESTIGIO = {"PRESIDENTE": 100, "VICE-PRESIDENTE": 60, "GOVERNADOR": 90, "VICE-GOVERNADOR": 40, "SENADOR": 80, "DEPUTADO FEDERAL": 70, "PREFEITO": 65, "DEPUTADO ESTADUAL": 45, "DEPUTADO DISTRITAL": 45}
lista_cargos = ",".join("'" + k + "'" for k in PRESTIGIO)
rows = c.execute(f"select ano, sq, nome, urna, cargo, uf, ue, partido, numero, sit, turno, nasc, ocup from cand where cargo in ({lista_cargos})").fetchall()

pessoas = {}
for ano, sq, nome, urna, cargo, uf, ue, part, numero, sit, turno, nasc, ocup in rows:
    nasc_ok = nasc if nasc and not nasc.startswith("#") else None
    chave = SQ(nome) + "|" + (nasc_ok or f"?{uf}")
    pid = hashlib.sha1(chave.encode()).hexdigest()[:8]
    p = pessoas.setdefault(pid, {"id": pid, "n": TT(nome), "u": TT(urna), "nasc": nasc_ok, "cand": [], "sq": {}, "ocup": None})
    s = (sit or "").upper()
    p["cand"].append({"ano": int(ano), "cargo": cargo.title(), "uf": uf, "ue": TT(ue) if cargo == "PREFEITO" else None, "partido": part, "num": numero,
                      "sit": (sit or "").title(), "eleito": s.startswith("ELEITO"), "segundo": s.startswith("2")})
    p["sq"][int(ano)] = sq
    p["ocup"] = ocup if ocup and not ocup.startswith("#") else p["ocup"]

def mantem(p):
    for k in p["cand"]:
        if k["cargo"] in ("Presidente", "Vice-Presidente", "Governador", "Vice-Governador", "Senador", "Deputado Federal"):
            return True
        if k["eleito"] or k["segundo"]:
            return True
    return False

pessoas = {k: v for k, v in pessoas.items() if mantem(v)}
print(len(pessoas), "pessoas", flush=True)
c.execute("create temp table m_sq(ano varchar, sq varchar, pid varchar)")
c.executemany("insert into m_sq values (?,?,?)", [(str(a), s, pid) for pid, p in pessoas.items() for a, s in p["sq"].items()])

# ---------- patrimônio declarado ----------
c.execute(f"""create temp table bens as select '2018' ano, SQ_CANDIDATO sq, DS_TIPO_BEM_CANDIDATO tipo, DS_BEM_CANDIDATO descr, {num('VR_BEM_CANDIDATO')} v from {T('bens_2018')}
  union all select '2014', SQ_CANDIDATO, DS_TIPO_BEM_CANDIDATO, DS_BEM_CANDIDATO, {num('VR_BEM_CANDIDATO')} from {T('bens_2014')}
  union all select '2016', SQ_CANDIDATO, DS_TIPO_BEM_CANDIDATO, DS_BEM_CANDIDATO, {num('VR_BEM_CANDIDATO')} from {T('bens_2016')}
  union all select '2020', SQ_CANDIDATO, DS_TIPO_BEM_CANDIDATO, DS_BEM_CANDIDATO, {num('VR_BEM_CANDIDATO')} from {T('bens_2020')}
  union all select '2022', SQ_CANDIDATO, DS_TIPO_BEM_CANDIDATO, DS_BEM_CANDIDATO, {num('VR_BEM_CANDIDATO')} from {T('bens_2022')}
  union all select '2024', SQ_CANDIDATO, DS_TIPO_BEM_CANDIDATO, DS_BEM_CANDIDATO, {num('VR_BEM_CANDIDATO')} from {T('bens_2024')}
  union all select '2026', SQ_CANDIDATO, DS_TIPO_BEM_CANDIDATO, DS_BEM_CANDIDATO, {num('VR_BEM_CANDIDATO')} from {T('bens_2026')}""")
for pid, ano, tot, n in c.execute("select m.pid, b.ano, sum(b.v), count(*) from bens b join m_sq m using (ano, sq) group by 1,2").fetchall():
    pessoas[pid].setdefault("bens", {})[ano] = {"total": round(tot or 0), "n": n}
for pid, ano, tipo, descr, v in c.execute("""select pid, ano, tipo, descr, v from (select m.pid, b.ano, b.tipo, b.descr, b.v,
      row_number() over (partition by m.pid, b.ano order by b.v desc) r from bens b join m_sq m using (ano, sq)) where r <= 4""").fetchall():
    pessoas[pid]["bens"][ano].setdefault("top", []).append([TT(tipo or ""), (descr or "")[:90], round(v or 0)])

# ---------- doadores de campanha (receitas) ----------
c.execute(f"""create temp table rec as select '2018' ano, SQ_CANDIDATO sq, DS_ORIGEM_RECEITA origem, NR_CPF_CNPJ_DOADOR doc, NM_DOADOR nm, NM_DOADOR_RFB rfb, {num('VR_RECEITA')} v from {T('receitas_2018')}
  union all select '2022', SQ_CANDIDATO, DS_ORIGEM_RECEITA, NR_CPF_CNPJ_DOADOR, NM_DOADOR, NM_DOADOR_RFB, {num('VR_RECEITA')} from {T('receitas_2022')}
  union all select '2024', SQ_CANDIDATO, DS_ORIGEM_RECEITA, NR_CPF_CNPJ_DOADOR, NM_DOADOR, NM_DOADOR_RFB, {num('VR_RECEITA')} from tse_receitas
  union all select '2026', SQ_CANDIDATO, DS_ORIGEM_RECEITA, NR_CPF_CNPJ_DOADOR, NM_DOADOR, NM_DOADOR_RFB, {num('VR_RECEITA')} from {T('receitas_2026')}""")
for pid, ano, tot, n in c.execute("select m.pid, r.ano, sum(r.v), count(*) from rec r join m_sq m using (ano, sq) group by 1,2").fetchall():
    pessoas[pid].setdefault("camp", {})[ano] = {"receita": round(tot or 0), "n_rec": n}
for pid, ano, orig, v in c.execute("select m.pid, r.ano, r.origem, sum(r.v) from rec r join m_sq m using (ano, sq) group by 1,2,3 having sum(r.v) > 0 order by 4 desc").fetchall():
    pessoas[pid]["camp"][ano].setdefault("origens", []).append([orig, round(v)])

_f = "where \"CATEGORIA DA SANÇÃO\" not ilike 'Multa%' and \"CATEGORIA DA SANÇÃO\" not ilike 'Publica%' and \"CATEGORIA DA SANÇÃO\" not ilike 'Demiss%' and \"CATEGORIA DA SANÇÃO\" not ilike 'Perdimento%' and \"CATEGORIA DA SANÇÃO\" not ilike 'Dissolu%'"
sanc = {re.sub(r"\D", "", r[0]) for r in c.execute(f'select "CPF OU CNPJ DO SANCIONADO" from ceis {_f} union select "CPF OU CNPJ DO SANCIONADO" from cnep {_f}').fetchall() if r[0]}
alertas = json.loads((RAIZ / "web/public/data/alertas.json").read_text(encoding="utf-8"))["alertas"]
por_cnpj = {}
for a in alertas:
    d = re.sub(r"\D", "", a.get("cnpj") or "")
    if len(d) >= 14:
        por_cnpj.setdefault(d[:14], []).append(a["id"])

def abrevia(nm):
    pp = [x for x in re.split(r"\s+", (nm or "").strip()) if x]
    return " ".join([pp[0].title()] + [x[0] + "." for x in pp[1:] if len(x) > 2]) if pp else "–"

def parte(pid, ano, doc, nome, rfb, v, destino):
    pj = len(doc) == 14
    d = {"doc": doc if pj else None, "nome": TT(rfb or nome or "") if pj else abrevia(nome), "pj": pj, "v": round(v or 0)}
    if pj and doc in sanc:
        d["sanc"] = True
    if pj and doc in por_cnpj:
        d["alertas"] = por_cnpj[doc][:3]
    pessoas[pid]["camp"][ano].setdefault(destino, []).append(d)

q = """select pid, ano, doc, nm, rfb, tot from (
  select pid, ano, doc, any_value(nm) nm, any_value(rfb) rfb, sum(v) tot, row_number() over (partition by pid, ano order by sum(v) desc) k
  from (select m.pid, r.ano, regexp_replace(r.doc, '[^0-9]', '', 'g') doc, r.nm, r.rfb, r.v from rec r join m_sq m using (ano, sq)
        where r.doc is not null and r.doc not like '#%' and r.doc <> '' and r.origem not like 'Recursos de partido%' and r.origem not like 'Recursos de outros%' and r.origem not like 'Recursos pr%')
  group by pid, ano, doc) where k <= 8"""
for pid, ano, doc, nm, rfb, tot in c.execute(q).fetchall():
    parte(pid, ano, doc, nm, rfb, tot, "doadores")

# ---------- fornecedores de campanha ----------
c.execute(f"""create temp table forn as select '2018' ano, SQ_CANDIDATO sq, regexp_replace(NR_CPF_CNPJ_FORNECEDOR,'[^0-9]','','g') doc, NM_FORNECEDOR_RFB rfb, NM_FORNECEDOR nm, DS_ORIGEM_DESPESA origem, {num('VR_DESPESA_CONTRATADA')} v from {T('fornec_2018')}
  union all select '2022', SQ_CANDIDATO, regexp_replace(NR_CPF_CNPJ_FORNECEDOR,'[^0-9]','','g'), NM_FORNECEDOR_RFB, NM_FORNECEDOR, DS_ORIGEM_DESPESA, {num('VR_DESPESA_CONTRATADA')} from {T('fornec_2022')}
  union all select '2026', SQ_CANDIDATO, regexp_replace(NR_CPF_CNPJ_FORNECEDOR,'[^0-9]','','g'), NM_FORNECEDOR_RFB, NM_FORNECEDOR, DS_ORIGEM_DESPESA, {num('VR_DESPESA_CONTRATADA')} from {T('fornec_2026')}""")
for pid, ano, tot in c.execute("select m.pid, f.ano, sum(f.v) from forn f join m_sq m using (ano, sq) group by 1,2").fetchall():
    pessoas[pid].setdefault("camp", {}).setdefault(ano, {})["despesa"] = round(tot or 0)
for pid, ano, orig, v in c.execute("select pid, ano, origem, v from (select m.pid, f.ano, f.origem, sum(f.v) v, row_number() over (partition by m.pid, f.ano order by sum(f.v) desc) k from forn f join m_sq m using (ano, sq) group by 1,2,3) where k <= 5").fetchall():
    pessoas[pid]["camp"][ano].setdefault("gastos", []).append([orig, round(v or 0)])
for pid, ano, doc, rfb, nm, v in c.execute("select pid, ano, doc, rfb, nm, v from (select m.pid, f.ano, f.doc, any_value(f.rfb) rfb, any_value(f.nm) nm, sum(f.v) v, row_number() over (partition by m.pid, f.ano order by sum(f.v) desc) k from forn f join m_sq m using (ano, sq) where f.doc is not null and f.doc <> '' group by 1,2,3) where k <= 6").fetchall():
    parte(pid, ano, doc, nm, rfb, v, "fornecedores")

# ---------- mandato: cota parlamentar (fichas) ----------
fichas = json.loads((RAIZ / "web/public/data/fichas.json").read_text(encoding="utf-8"))["fichas"]
por_nome = {}
for pid, p in pessoas.items():
    for k in p["cand"]:
        if k["cargo"] in ("Deputado Federal", "Senador"):
            por_nome.setdefault((SQ(p["u"]), k["uf"]), pid)
            por_nome.setdefault((SQ(p["n"]), k["uf"]), pid)
por_nome_sem_uf = {}
for (n, u), v in por_nome.items():
    por_nome_sem_uf.setdefault(n, v)
for f in fichas:
    if f["t"] == "pref":
        continue
    pid = por_nome.get((SQ(f["n"]), f.get("u"))) if f.get("u") else por_nome_sem_uf.get(SQ(f["n"]))
    reg = {"tipo": "Deputado(a) federal" if f["t"] == "dep" else "Senador(a)", "anos": f["anos"], "forn": f.get("forn", []), "pct25": f.get("pct25"), "alertas": f.get("alertas", [])}
    if pid:
        pessoas[pid]["mandato"] = reg
    else:
        npid = hashlib.sha1(("F|" + SQ(f["n"]) + str(f.get("u"))).encode()).hexdigest()[:8]
        pessoas[npid] = {"id": npid, "n": f["n"], "u": f["n"], "nasc": None, "cand": [], "sq": {}, "ocup": None, "mandato": reg, "uf0": f.get("u"), "p0": f.get("p")}

pref = {(f["u"], SQ(f["n"])): f for f in fichas if f["t"] == "pref"}
for pid, p in pessoas.items():
    for k in p["cand"]:
        if k["cargo"] == "Prefeito" and k["eleito"]:
            f = pref.get((k["uf"], SQ(p["n"])))
            if f and f.get("alertas"):
                p.setdefault("alertas_pref", []).extend(f["alertas"])

# ---------- emendas parlamentares (ingestao/emendas.py) ----------
_ea = RAIZ / "data-publica" / "emendas_autor.json"
emendas = json.loads(_ea.read_text(encoding="utf-8")) if _ea.exists() else {}
for pid, p in pessoas.items():
    for chave in {SQ(p["u"]), SQ(p["n"])}:
        e = emendas.get(chave)
        if e and sum(e["anos"].values()) > 0:
            p["emendas"] = {"anos": e["anos"], "top": e["top"], "alertas": e["alertas"][:8]}
            break

# ---------- voos internacionais pagos com a cota (viagens.json) ----------
_vj = RAIZ / "web/public/data/viagens.json"
if _vj.exists():
    voos = {SQ(d["p"]): d for d in json.loads(_vj.read_text(encoding="utf-8")).get("deputados", [])}
    for pid, p in pessoas.items():
        d = voos.get(SQ(p["u"])) or voos.get(SQ(p["n"]))
        if d and p.get("mandato"):
            p["voos"] = {"n": d["n"], "v": d["v"], "paises": d["paises"]}

# ---------- R10: político sócio de empresa que vende ao governo ----------
r10 = {}
for a in alertas:
    if a["regra"] == "R10": r10.setdefault(SQ(a["manchete"]["politico"]), []).append(a["id"])

# ---------- ICIJ Offshore Leaks: coincidência de nome completo (confirmar) ----------
_of = RAIZ / "dados" / "offshore_br.json"
offshore = json.loads(_of.read_text(encoding="utf-8")) if _of.exists() else {}
for pid, p in pessoas.items():
    m = offshore.get(SQ(p["n"]))
    if m and len(m) <= 3 and len([w for w in SQ(p["n"]).split() if w not in ("DA", "DE", "DO", "DAS", "DOS", "E")]) >= 4:
        p["offshore"] = [{"id": x["id"], "nome": x["nome"], "fonte": x["fonte"], "entidades": x["entidades"][:4]} for x in m]

# ---------- atividade na Câmara (API de dados abertos: ingestao/camara_atividade.py) ----------
_ca = RAIZ / "dados" / "camara_atividade.json"
if _ca.exists():
    for k, d in json.loads(_ca.read_text(encoding="utf-8")).items():
        pid = por_nome.get((SQ(d["nome"]), d["uf"])) or por_nome.get((SQ(d["nome_civil"]), d["uf"]))
        if pid: pessoas[pid]["camara"] = {x: d[x] for x in ("foto", "escolaridade", "nascimento", "natural", "projetos", "frentes", "comissoes")}

# ---------- atividade no Senado (ingestao/senado_atividade.py) ----------
_sa = RAIZ / "dados" / "senado_atividade.json"
if _sa.exists():
    for cod, d in json.loads(_sa.read_text(encoding="utf-8")).items():
        pid = por_nome.get((SQ(d["nome"]), d["uf"])) or por_nome.get((SQ(d["nome_completo"]), d["uf"]))
        if pid: pessoas[pid]["senado"] = {x: d[x] for x in ("foto", "projetos", "comissoes", "votos", "partido")}

# ---------- sanções internacionais (OFAC): coincidência de nome completo, a confirmar ----------
_of2 = RAIZ / "dados" / "ofac_br.json"
ofac = json.loads(_of2.read_text(encoding="utf-8")) if _of2.exists() else {}
for pid, p in pessoas.items():
    m = ofac.get(SQ(p["n"]))
    if m and len([w for w in SQ(p["n"]).split() if w not in ("DA", "DE", "DO", "DAS", "DOS", "E")]) >= 3:
        p["ofac"] = m[:2]

# ---------- empresas em que a pessoa é sócia (Receita: nome completo + 6 dígitos centrais do CPF) ----------
_cp = " union all ".join(f"select '{a}' ano, SQ_CANDIDATO sq, substr(NR_CPF_CANDIDATO, 4, 6) c6 from {T('consulta_cand_' + str(a))}" for a in (2014, 2016, 2018, 2020, 2022, 2026)) + " union all select '2024', SQ_CANDIDATO, substr(NR_CPF_CANDIDATO, 4, 6) from tse_cand"
cpf_por = {(a, s): c6 for a, s, c6 in c.execute(_cp).fetchall() if c6 and c6.isdigit() and len(c6) == 6}
c.execute("create temp table pp(pid varchar, nome varchar, c6 varchar)")
linhas = []
for pid, p in pessoas.items():
    c6 = next((cpf_por[(str(a), s)] for a, s in p["sq"].items() if (str(a), s) in cpf_por), None)
    if c6: linhas.append((pid, SQ(p["n"]), c6))
c.executemany("insert into pp values (?,?,?)", linhas)
c.execute("""create temp table soc as select pp.pid, s.cnpj_basico, s.qualificacao, s.data_entrada
   from read_parquet('dados/cnpj/socios_[0-9]*.parquet') s join pp on strip_accents(upper(trim(s.nome_socio))) = pp.nome and substr(s.doc_socio, 4, 6) = pp.c6
   where s.tipo_socio = '2' and s.doc_socio like '***%'""")
QUALIF = {"05": "Administrador", "10": "Diretor", "16": "Presidente", "22": "Sócio", "49": "Sócio-administrador", "28": "Sócio-gerente", "08": "Conselheiro", "65": "Titular"}
SIT = {"01": "nula", "02": "ativa", "03": "suspensa", "04": "inapta", "08": "baixada"}
emp_rows = c.execute("""select soc.pid, soc.cnpj_basico, e.razao_social, e.capital_social, e.porte, soc.qualificacao, soc.data_entrada, m.cnpj, m.situacao, m.data_inicio, m.uf
   from soc join read_parquet('dados/cnpj/empresas_*.parquet') e using (cnpj_basico)
   left join (select cnpj, cnpj_basico, situacao, data_inicio, uf from read_parquet('dados/cnpj/estabelecimentos_*.parquet') where matriz = '1' and cnpj_basico in (select cnpj_basico from soc)) m using (cnpj_basico)""").fetchall()
for pid, cb, rs, cap, porte, qual, entrada, cnpj14, sit, ini, uf in emp_rows:
    p = pessoas[pid]
    d = {"cnpj": cnpj14 or (cb + "------"), "nome": TT(rs), "capital": cap, "situacao": SIT.get(sit, sit), "abertura": ini, "uf": uf, "qual": QUALIF.get(qual, "Sócio"), "entrada": entrada}
    if cnpj14 and cnpj14 in sanc: d["sanc"] = True
    if cnpj14 and cnpj14 in por_cnpj: d["alertas"] = por_cnpj[cnpj14][:3]
    p.setdefault("empresas", []).append(d)
for p in pessoas.values():
    if p.get("empresas"):
        p["empresas"] = sorted(p["empresas"], key=lambda d: (-(1 if d.get("sanc") or d.get("alertas") else 0), -(float(d["capital"] or 0))))[:12]
print(sum(1 for p in pessoas.values() if p.get("empresas")), "pessoas com empresas em nome próprio (nome + CPF parcial)", flush=True)

# ---------- pontos de atenção (neutros) + ordenação ----------
def brl(v):
    if v < 1e6: return "R$ " + f"{v:,.0f}".replace(",", ".")
    if v < 1e9: return "R$ " + f"{v/1e6:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".") + " mi"
    return "R$ " + f"{v/1e9:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " bi"

for pid, p in pessoas.items():
    pts = []
    b = p.get("bens", {})
    anos_b = sorted(b)
    for a0, a1 in zip(anos_b, anos_b[1:]):
        v0, v1 = b[a0]["total"], b[a1]["total"]
        if v0 >= 100000 and v1 >= 1e6 and v1 >= 2 * v0:
            pts.append({"t": "Patrimônio declarado mais que dobrou", "d": f"{brl(v0)} ({a0}) → {brl(v1)} ({a1}). Valor declarado pelo próprio candidato; herança, venda, atualização de bens e outros fatos legítimos podem explicar."})
    for ano, k in (p.get("camp") or {}).items():
        rec = k.get("receita") or 0
        dn = k.get("doadores", [])
        if rec > 0 and dn and dn[0]["pj"] and dn[0]["v"] / rec >= 0.4:
            pts.append({"t": f"Um único doador pessoa jurídica concentra {round(100 * dn[0]['v'] / rec)}% da campanha de {ano}", "d": f"{dn[0]['nome']} · {brl(dn[0]['v'])}"})
        for d in dn:
            if d.get("sanc"):
                pts.append({"t": f"Doador de {ano} consta no cadastro de empresas sancionadas (CEIS/CNEP)", "d": f"{d['nome']} · {brl(d['v'])}. O cadastro não diz se a sanção já vigorava na data da doação."})
            if d.get("alertas"):
                pts.append({"t": f"Doador de {ano} tem alerta no Radar Público", "d": f"{d['nome']} · {brl(d['v'])}", "alertas": d["alertas"]})
        for d in k.get("fornecedores", []):
            if d.get("sanc"):
                pts.append({"t": f"Fornecedor da campanha de {ano} consta no cadastro de sancionadas (CEIS/CNEP)", "d": f"{d['nome']} · {brl(d['v'])}"})
            if d.get("alertas"):
                pts.append({"t": f"Fornecedor da campanha de {ano} tem alerta no Radar Público", "d": f"{d['nome']} · {brl(d['v'])}", "alertas": d["alertas"]})
    m = p.get("mandato")
    if m and m.get("alertas"):
        pts.append({"t": "Fornecedor da cota parlamentar com alerta no Radar Público", "d": f"{len(m['alertas'])} alerta(s) ligados.", "alertas": m["alertas"][:5]})
    if m and m.get("pct25") and m["pct25"] >= 90:
        pts.append({"t": "Gasto de cota em 2025 entre os 10% maiores", "d": f"Percentil {m['pct25']} entre os deputados. Gastar muito não é irregular; indica onde olhar."})
    if p.get("emendas") and p["emendas"]["alertas"]:
        pts.append({"t": "Emendas pagaram entidades com ponto de atenção no Radar", "d": f"{len(p['emendas']['alertas'])} entidade(s) favorecida(s) com alerta R09 (sancionada, empresa nova ou capital muito pequeno para o valor).", "alertas": p["emendas"]["alertas"]})
    for d in (p.get("empresas") or []):
        if d.get("sanc"): pts.append({"t": "É sócio(a) de empresa que consta como sancionada (CEIS/CNEP)", "d": f"{d['nome']}. A base mostra o quadro societário atual, sem data de saída."})
        if d.get("alertas"): pts.append({"t": "É sócio(a) de empresa com alerta no Radar Público", "d": d["nome"], "alertas": d["alertas"]})
    if p.get("ofac"):
        pts.append({"t": "Nome completo coincide com pessoa na lista de sanções da OFAC (Tesouro dos EUA)", "d": "Coincidência de nome pode ser homônimo: confirme nos detalhes. Estar na lista não é decisão da Justiça brasileira."})
    if p.get("offshore"):
        pts.append({"t": "Nome completo coincide com pessoa ligada a empresa offshore (ICIJ Offshore Leaks)", "d": "Coincidência de nome não prova que seja a mesma pessoa, e constar nos vazamentos não indica ilegalidade: ter empresa no exterior pode ser legal e declarado. Confirme nos detalhes abaixo."})
    if r10.get(SQ(p["n"])):
        pts.append({"t": "Consta como sócio de empresa que vende ao governo", "d": f"{len(r10[SQ(p['n'])])} empresa(s) com contratos desde 2025 (nome completo e 6 dígitos do CPF coincidem com o sócio na Receita). A base mostra o quadro societário atual.", "alertas": r10[SQ(p['n'])][:5]})
    if p.get("alertas_pref"):
        pts.append({"t": "Doador de campanha virou fornecedor do município", "d": f"{len(p['alertas_pref'])} alerta(s) R05 na cidade.", "alertas": p["alertas_pref"][:5]})
    p["pontos"] = pts[:12]
    p["cand"] = sorted(p["cand"], key=lambda k: k["ano"], reverse=True)
    top = max(p["cand"], key=lambda k: (PRESTIGIO.get(k["cargo"].upper(), 0), k["ano"])) if p["cand"] else None
    p["rank"] = (PRESTIGIO.get(top["cargo"].upper(), 0) if top else 55) + (10 if any(k["eleito"] for k in p["cand"]) else 0) + (5 if any(k["ano"] == 2024 for k in p["cand"]) else 0) + 2 * len(p["pontos"])
    p["uf"] = p["cand"][0]["uf"] if p["cand"] else p.get("uf0")
    p["partido"] = p["cand"][0]["partido"] if p["cand"] else p.get("p0")
    p.pop("sq", None)

# ---------- saída: índice leve + fichas em lotes ----------
idx = sorted(([p["id"], p["n"], p["u"], p["partido"] or "", p["uf"] or "", p["cand"][0]["cargo"] if p["cand"] else p["mandato"]["tipo"], p["cand"][0]["ano"] if p["cand"] else 2025, p["rank"]] for p in pessoas.values()), key=lambda r: -r[7])
(OUT / "idx.json").write_text(json.dumps({"gerado": str(datetime.date.today()), "p": idx}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
lotes = {}
for p in pessoas.values():
    lotes.setdefault(p["id"][:2], {})[p["id"]] = p
for f in OUT.glob("s*.json"):
    f.unlink()
for k, v in lotes.items():
    (OUT / f"s{k}.json").write_text(json.dumps(v, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
tam = sum(f.stat().st_size for f in OUT.glob("*.json")) / 1e6
print(len(pessoas), "pessoas,", len(lotes), "lotes,", round(tam, 1), "MB | índice", round((OUT / "idx.json").stat().st_size / 1e6, 2), "MB")
for p in pessoas.values():
    if p["u"].upper() in ("LULA", "JAIR BOLSONARO"):
        print(p["id"], p["n"], p["u"], len(p["pontos"]), list((p.get("camp") or {}).keys()), {a: v["total"] for a, v in (p.get("bens") or {}).items()})
