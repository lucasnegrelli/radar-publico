"""Fichas de EMPRESA para investigar: reúne, por CNPJ, o que os dados abertos dizem em lugares diferentes:
cadastro e sócios (Receita), contratos (PNCP), emendas recebidas (Portal da Transparência), doações a campanhas (TSE), sanções (CEIS/CNEP/CEPIM),
alertas do Radar e sócios que são políticos eleitos. Saída: web/public/data/empresas/idx.json + eXX.json (256 lotes).
Quais empresas entram: as que têm alerta, contrato relevante (>= R$ 1 mi desde 2025), emenda relevante (>= R$ 100 mil), doação relevante a campanha
(>= R$ 50 mil), sanção, ou que são de político. Sócio pessoa física sai com nome abreviado, exceto quando é político eleito (aí vai o nome e o link da ficha)."""
import json, os, re, hashlib, pathlib, datetime, unicodedata, duckdb

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
OUT = RAIZ / "web/public/data/empresas"; OUT.mkdir(parents=True, exist_ok=True)
norm = lambda s: re.sub(r"\s+", " ", "".join(c for c in unicodedata.normalize("NFD", (s or "").upper()) if unicodedata.category(c) != "Mn")).strip()
def TT(s):
    peq = {"da", "de", "do", "das", "dos", "e"}; sig = {"ltda", "sa", "s/a", "me", "epp", "eireli", "cnpj", "ii", "iii", "tv", "ong", "cia"}
    return " ".join((w if (w in peq and i) else (w.upper() if w in sig else w[:1].upper() + w[1:])) for i, w in enumerate((s or "").lower().split()))
def abrevia(nm):
    pp = [x for x in re.split(r"\s+", (nm or "").strip()) if x]
    return " ".join([pp[0].title()] + [x[0] + "." for x in pp[1:] if len(x) > 2]) if pp else "–"

c = duckdb.connect("dados/radar.duckdb", read_only=True)
c.execute("create temp view ceis as select * from read_parquet('dados/tse/ceis.parquet')")
c.execute("create temp view cnep as select * from read_parquet('dados/tse/cnep.parquet')")
alertas = json.loads((RAIZ / "web/public/data/alertas.json").read_text(encoding="utf-8"))["alertas"]
por_cnpj_al = {}
for a in alertas:
    d = re.sub(r"\D", "", a.get("cnpj") or "")
    if len(d) == 14: por_cnpj_al.setdefault(d, []).append({"id": a["id"], "regra": a["regra"], "g": a["gravidade"], "total": a["total"]})

# ---- conjunto de empresas relevantes (por CNPJ completo da matriz) ----
c.execute("""create temp table cand as
  select doc14 doc, sum(valor_global) v, count(*) n from pncp where data_assinatura >= date '2025-01-01' and not erro_valor and doc14 <> '00000000000000' group by 1 having sum(valor_global) >= 1000000""")
alvo = {r[0] for r in c.execute("select doc from cand").fetchall()} | set(por_cnpj_al)
em = c.execute(f"""select lpad(regexp_replace(column06,'\\D','','g'),14,'0') doc, sum(try_cast(replace(replace(column12,'.',''),',','.') as double)) v
   from read_csv('dados/emendas/EmendasParlamentares_PorFavorecido.csv', delim=';', header=false, skip=1, all_varchar=true, encoding='latin-1', columns={{{', '.join(f"'column{i:02d}': 'VARCHAR'" for i in range(13))}}}, sample_size=-1)
   where length(regexp_replace(column06,'\\D','','g')) = 14 group by 1 having sum(try_cast(replace(replace(column12,'.',''),',','.') as double)) >= 100000""").fetchall()
alvo |= {r[0] for r in em}
rec = lambda a: f"select regexp_replace(NR_CPF_CNPJ_DOADOR,'[^0-9]','','g') doc, SQ_CANDIDATO sq, '{a}' ano, try_cast(replace(VR_RECEITA, ',', '.') as double) v from read_parquet('dados/tse/receitas_{a}.parquet')"
c.execute("create temp table doa as " + " union all ".join(rec(a) for a in (2018, 2022, 2026)) + " union all select regexp_replace(NR_CPF_CNPJ_DOADOR,'[^0-9]','','g'), SQ_CANDIDATO, '2024', try_cast(replace(VR_RECEITA, ',', '.') as double) from read_parquet('dados/tse/receitas_2024_todas.parquet')")
alvo |= {r[0] for r in c.execute("select doc from doa where length(doc) = 14 group by 1 having sum(v) >= 50000").fetchall()}
san = c.execute("""select lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\\D','','g'),14,'0') from ceis union select lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\\D','','g'),14,'0') from cnep""").fetchall()
alvo |= {r[0] for r in san if r[0] and r[0] != "0" * 14}
print(len(alvo), "empresas candidatas", flush=True)
c.execute("create temp table alvo(doc varchar)")
c.executemany("insert into alvo values (?)", [(d,) for d in alvo])
c.execute("create temp table alvo8 as select distinct left(doc, 8) b from alvo")

# ---- cadastro e sócios ----
cad = {}
for cn, raz, cap, porte, nat in c.execute("select cnpj_basico, razao_social, capital_social, porte, natureza from read_parquet('dados/cnpj/empresas_*.parquet') where cnpj_basico in (select b from alvo8)").fetchall():
    cad[cn] = {"nome": TT(raz), "capital": cap, "porte": porte, "natureza": nat}
for cnpj, cb, sit, ini, uf, mun in c.execute("select cnpj, cnpj_basico, situacao, data_inicio, uf, municipio from read_parquet('dados/cnpj/estabelecimentos_*.parquet') where matriz = '1' and cnpj_basico in (select b from alvo8)").fetchall():
    if cb in cad: cad[cb].update({"cnpj": cnpj, "situacao": {"01": "nula", "02": "ativa", "03": "suspensa", "04": "inapta", "08": "baixada"}.get(sit, sit), "abertura": ini, "uf": uf})
socios = {}
for cb, nome, doc, qual, ent in c.execute("select cnpj_basico, nome_socio, doc_socio, qualificacao, data_entrada from read_parquet('dados/cnpj/socios_[0-9]*.parquet') where cnpj_basico in (select b from alvo8) and tipo_socio in ('1','2')").fetchall():
    socios.setdefault(cb, []).append({"nome": nome, "c6": (doc or "")[3:9], "qual": qual, "entrada": ent})
# políticos eleitos entre os sócios (nome completo + CPF parcial), vindos de pessoas.py
pol = {}
try:
    import glob
    for f in glob.glob("web/public/data/pessoas/s*.json"):
        for pid, p in json.load(open(f, encoding="utf-8")).items():
            for e in p.get("empresas", []):
                if e.get("cnpj"): pol.setdefault(e["cnpj"][:8], []).append({"id": pid, "nome": p["n"], "partido": p.get("partido"), "uf": p.get("uf")})
except Exception as e:
    print("sem pessoas:", e)

# ---- contratos, emendas, doações, sanções ----
contr = {}
for doc, v, n in c.execute("select doc14, sum(valor_global), count(*) from pncp where data_assinatura >= date '2025-01-01' and not erro_valor and doc14 in (select doc from alvo) group by 1").fetchall():
    contr[doc] = {"total": v, "n": n}
for doc, org, v in c.execute("select doc14, orgao, s from (select doc14, orgao, sum(valor_global) s, row_number() over (partition by doc14 order by sum(valor_global) desc) r from pncp where data_assinatura >= date '2025-01-01' and not erro_valor and doc14 in (select doc from alvo) group by 1,2) where r <= 4").fetchall():
    contr[doc].setdefault("orgaos", []).append([org, v])
emen = {}
for doc, autor, v in c.execute(f"""select lpad(regexp_replace(column06,'\\D','','g'),14,'0') doc, column02 autor, sum(try_cast(replace(replace(column12,'.',''),',','.') as double)) v
   from read_csv('dados/emendas/EmendasParlamentares_PorFavorecido.csv', delim=';', header=false, skip=1, all_varchar=true, encoding='latin-1', columns={{{', '.join(f"'column{i:02d}': 'VARCHAR'" for i in range(13))}}}, sample_size=-1)
   where lpad(regexp_replace(column06,'\\D','','g'),14,'0') in (select doc from alvo) group by 1,2""").fetchall():
    e = emen.setdefault(doc, {"total": 0, "autores": []}); e["total"] += v or 0; e["autores"].append([TT(autor), v])
for e in emen.values(): e["autores"] = sorted(e["autores"], key=lambda x: -(x[1] or 0))[:5]; e["total"] = round(e["total"])
# a quem doou: nomes dos candidatos (campanhas)
nomes_cand = {}
for ano, sq, nm in c.execute("select '2018', SQ_CANDIDATO, NM_URNA_CANDIDATO from read_parquet('dados/tse/consulta_cand_2018.parquet') union all select '2022', SQ_CANDIDATO, NM_URNA_CANDIDATO from read_parquet('dados/tse/consulta_cand_2022.parquet') union all select '2026', SQ_CANDIDATO, NM_URNA_CANDIDATO from read_parquet('dados/tse/consulta_cand_2026.parquet') union all select '2024', SQ_CANDIDATO, NM_URNA_CANDIDATO from read_parquet('dados/tse/cand_2024.parquet')").fetchall():
    nomes_cand[(ano, sq)] = TT(nm)
doaram = {}
for doc, ano, sq, v in c.execute("select doc, ano, sq, sum(v) from doa where doc in (select doc from alvo) group by 1,2,3 having sum(v) > 0").fetchall():
    d = doaram.setdefault(doc, {"total": 0, "para": []}); d["total"] += v; d["para"].append([nomes_cand.get((ano, sq), "?"), ano, v])
for d in doaram.values(): d["para"] = sorted(d["para"], key=lambda x: -x[2])[:6]; d["total"] = round(d["total"])
sanc = {}
for lista, doc, cat, org, ini, fim in c.execute("""select 'CEIS', lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\\D','','g'),14,'0'), "CATEGORIA DA SANÇÃO", "ÓRGÃO SANCIONADOR", "DATA INÍCIO SANÇÃO", "DATA FINAL SANÇÃO" from ceis
   union all select 'CNEP', lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\\D','','g'),14,'0'), "CATEGORIA DA SANÇÃO", "ÓRGÃO SANCIONADOR", "DATA INÍCIO SANÇÃO", "DATA FINAL SANÇÃO" from cnep""").fetchall():
    if doc in alvo: sanc.setdefault(doc, []).append({"lista": lista, "tipo": cat, "orgao": org, "ini": ini, "fim": fim})

# ---- monta fichas ----
fichas = {}
for doc in alvo:
    cb = doc[:8]; d = cad.get(cb)
    if not d: continue
    polit = pol.get(cb, [])
    nomes_pol = {norm(x["nome"]) for x in polit}
    ss = []
    for s in (socios.get(cb) or [])[:14]:
        eh_pol = norm(s["nome"]) in nomes_pol
        ss.append({"nome": TT(s["nome"]) if eh_pol else abrevia(s["nome"]), "qual": s["qual"], "entrada": s["entrada"], "politico": eh_pol})
    f = {"cnpj": doc, "nome": d["nome"], "capital": d.get("capital"), "porte": d.get("porte"), "situacao": d.get("situacao"), "abertura": d.get("abertura"), "uf": d.get("uf"),
         "socios": ss, "politicos": polit[:5], "alertas": por_cnpj_al.get(doc, [])[:8]}
    if doc in contr: f["contratos"] = contr[doc]
    if doc in emen: f["emendas"] = emen[doc]
    if doc in doaram: f["doacoes"] = doaram[doc]
    if doc in sanc: f["sancoes"] = sanc[doc][:5]
    f["score"] = (len(f["alertas"]) * 30) + (40 if polit else 0) + (25 if doc in sanc else 0) + min(30, (contr.get(doc, {}).get("total", 0) / 1e7)) + min(20, emen.get(doc, {}).get("total", 0) / 1e6)
    fichas[doc] = f
idx = sorted(([f["cnpj"], f["nome"], f.get("uf") or "", round(f.get("contratos", {}).get("total", 0)), len(f["alertas"]), 1 if f["politicos"] else 0, round(f["score"])] for f in fichas.values()), key=lambda r: -r[6])
(OUT / "idx.json").write_text(json.dumps({"gerado": str(datetime.date.today()), "e": idx}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
lotes = {}
for f in fichas.values(): lotes.setdefault(f["cnpj"][6:8], {})[f["cnpj"]] = f   # lote = 7º e 8º dígitos do CNPJ (o navegador acha sem calcular hash)
for p in OUT.glob("e*.json"): p.unlink()
for k, v in lotes.items(): (OUT / f"e{k}.json").write_text(json.dumps(v, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(len(fichas), "empresas;", len(lotes), "lotes;", round(sum(f.stat().st_size for f in OUT.glob("*.json")) / 1e6, 1), "MB")
