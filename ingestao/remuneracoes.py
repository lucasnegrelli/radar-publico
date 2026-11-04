"""Ranking de remunerações do setor público -> web/public/data/remuneracoes.json
 - Justiça e MP (juízes, desembargadores, ministros de tribunais superiores, procuradores): DadosJusBr (Transparência Brasil, CC-BY-4.0), com o detalhe de cada
   rubrica (remuneracao.csv). "Penduricalho" aqui = tudo que não é subsídio/vencimento-base, listado item a item. Muitas dessas verbas são legais e indenizatórias
   (ficam fora do teto por lei); o ranking mostra quanto cada pessoa recebeu no total e de quê, não diz que algo é irregular.
 - Executivo federal: SIAPE (Portal da Transparência), mês mais recente em dados/siape (baixado por servidores.py).
 - Fotos: miniatura da Wikipédia (pt), só para ministros de tribunais superiores e de Estado, quando existe página com a foto.
Nomes completos: remuneração de agente público é dado de transparência ativa (nominal) no CNJ e no Portal da Transparência."""
import datetime, glob, io, json, os, pathlib, re, time, urllib.parse, urllib.request, zipfile
from concurrent.futures import ThreadPoolExecutor
import duckdb

RAIZ = pathlib.Path(__file__).parent.parent; os.chdir(RAIZ)
UA = {"User-Agent": "RadarPublico/1.0 (projeto civico; github.com/lucasnegrelli/radar-publico)"}
API = "https://api.dadosjusbr.org/v2"
TETO = 46366.19
TMP = RAIZ / "dados" / "justica"; TMP.mkdir(parents=True, exist_ok=True)


def get(u, t=60):
    for i in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t).read()
        except Exception: time.sleep(2 + 3 * i)
    return None


_part = {"De", "Da", "Do", "Dos", "Das", "E"}
nm = lambda n: " ".join(w.lower() if w in _part and i else w for i, w in enumerate((n or "").title().split()))
def rub(k):
    k = (k or "").strip()
    if k in ("", "0"): return None
    return (k[:1].upper() + k[1:].lower())[:90]
num = lambda s: float(str(s).replace(".", "").replace(",", ".")) if s not in (None, "") else 0.0
TOP = 600


# ---------- Justiça e MP ----------
hoje = datetime.date.today(); meses = []; a, m = hoje.year, hoje.month
for _ in range(5):
    m -= 1
    if m == 0: a, m = a - 1, 12
    meses.append((a, m))


def orgao(o):
    oid = o["id_orgao"]
    for ano, mes in meses:
        raw = get(f"{API}/dados/{oid}/{ano}/{mes}", 30)
        if not raw: continue
        try: url = (json.loads(raw).get("pacote_de_dados") or {}).get("url")
        except Exception: continue
        z = get(url, 120) if url else None
        if not z: continue
        try:
            zf = zipfile.ZipFile(io.BytesIO(z)); pasta = TMP / f"rem-{oid}-{ano}-{mes}"
            zf.extract("contracheque.csv", pasta); zf.extract("remuneracao.csv", pasta)
        except Exception: continue
        c = duckdb.connect()
        cc = (pasta / "contracheque.csv").as_posix(); rr = (pasta / "remuneracao.csv").as_posix()
        c.execute(f"""create table t as select id_contracheque id, nome, funcao,
            try_cast(replace(salario, ',', '.') as double) sal, try_cast(replace(beneficios, ',', '.') as double) ben, try_cast(replace(remuneracao, ',', '.') as double) liq
            from read_csv('{cc}', delim=';', header=true, all_varchar=true, ignore_errors=true) where try_cast(replace(salario, ',', '.') as double) is not null""")
        c.execute(f"""create table r as select id_contracheque id, tipo, item, try_cast(replace(valor, ',', '.') as double) v
            from read_csv('{rr}', delim=';', header=true, all_varchar=true, ignore_errors=true)""")
        rows = c.execute("select id, nome, funcao, sal, coalesce(ben, 0), liq from t where sal + coalesce(ben, 0) > 0 order by sal + coalesce(ben, 0) desc limit 40").fetchall()
        out = []
        for i, nome, fn, sal, ben, liq in rows:
            its = c.execute("select item, sum(v) v from r where id = ? and tipo = 'R/O' and v > 0 group by 1 order by 2 desc", [i]).fetchall()
            out.append({"nome": nm(nome), "cargo": (fn or "").title()[:70], "orgao": o["nome"], "oid": oid, "poder": "MP" if o["entidade"] in ("Ministério", "Ministério Público") or oid.startswith("mp") else "J",
                        "ref": f"{mes:02d}/{ano}", "bruta": round(sal + ben), "sub": round(sal), "pend": round(sum(v for _, v in its)), "liq": round(liq or 0),
                        "it": [[rub(k), round(v)] for k, v in its if rub(k)][:8]})
        return out
    return None


orgaos = json.loads(get(API + "/orgaos"))
with ThreadPoolExecutor(8) as ex: res = [x for x in ex.map(orgao, orgaos) if x]
pessoas = [p for r in res for p in r]
print("justiça/MP:", len(pessoas), "pessoas de", len(res), "órgãos", flush=True)

# ---------- Executivo (SIAPE) ----------
D = RAIZ / "dados" / "siape"; cad = sorted(glob.glob(str(D / "*_Cadastro.csv")))
if cad:
    mes = pathlib.Path(cad[-1]).name[:6]; rem = D / f"{mes}_Remuneracao.csv"
    if rem.exists():
        c = duckdb.connect(); cols = ", ".join(f"'column{i:02d}': 'VARCHAR'" for i in range(39))
        n = lambda i: f"coalesce(try_cast(replace(column{i:02d}, ',', '.') as double), 0)"
        c.execute(f"""create table r as select column02 id, column04 nome, {n(5)} bruta, {n(7)} abate, {n(9)} natalina, {n(13)} ferias, {n(15)} eventual, {n(29)} liquida, {n(37)} indeniz
           from read_csv('{rem.as_posix()}', delim=';', header=false, all_varchar=true, encoding='utf-8', columns={{{cols}}}, ignore_errors=true) where column00 = '{mes[:4]}'""")
        c.execute(f"""create table k as select Id_SERVIDOR_PORTAL id, any_value(DESCRICAO_CARGO) cargo, any_value(ORG_EXERCICIO) orgao, any_value(ORGSUP_EXERCICIO) orgsup
           from read_csv('{cad[-1]}', delim=';', header=true, all_varchar=true, encoding='latin-1', sample_size=-1, ignore_errors=true) group by 1""")
        rows = c.execute("""select r.id, r.nome, k.cargo, coalesce(k.orgsup, k.orgao), bruta + abate + eventual + ferias + natalina, bruta, abate, eventual + ferias + natalina, indeniz, liquida
           from (select id, any_value(nome) nome, sum(bruta) bruta, sum(abate) abate, sum(natalina) natalina, sum(ferias) ferias, sum(eventual) eventual, sum(liquida) liquida, sum(indeniz) indeniz from r group by 1) r
           left join k using (id) order by bruta + abate + eventual + ferias + natalina + indeniz desc limit 300""").fetchall()
        for i, nome, cargo, org, tot, bruta, abate, ev, ind, liq in rows:
            its = [[k, round(v)] for k, v in (("Remuneração básica bruta", bruta), ("Abate-teto", abate), ("Eventuais (férias, 13º, outras)", ev), ("Verbas indenizatórias", ind)) if abs(v) > 0.5]
            pessoas.append({"nome": nm(nome), "cargo": (cargo or "").title()[:70], "orgao": (org or "").title()[:80], "oid": "siape", "poder": "E", "ref": f"{mes[4:]}/{mes[:4]}",
                            "bruta": round(bruta + abate + ev + ind), "sub": round(bruta), "pend": round(ev + ind), "liq": round(liq), "it": its, "u": f"https://portaldatransparencia.gov.br/servidores/{i}"})
        print("executivo:", len(rows), "servidores", mes, flush=True)

pessoas.sort(key=lambda p: -p["bruta"])
alto = ("ministro", "presidente")
fixos = [p for p in pessoas if p["oid"] in ("stf", "stj", "tst", "stm", "tse") and any(w in p["cargo"].lower() for w in alto)]
topo = [p for p in pessoas if p["poder"] != "E"][:TOP] + [p for p in pessoas if p["poder"] == "E"][:250]; topo.sort(key=lambda p: -p["bruta"]); ids = {(p["nome"], p["orgao"]) for p in topo}
topo += [p for p in fixos if (p["nome"], p["orgao"]) not in ids]

# ---------- fotos (Wikipédia pt) ----------
part = {"De", "Da", "Do", "Dos", "Das", "E"}
tit = lambda n: " ".join(w.lower() if w in part else w for w in n.split())
def fotos(nomes):
    out = {}
    for i in range(0, len(nomes), 40):
        lote = nomes[i:i + 40]
        q = urllib.parse.urlencode({"action": "query", "format": "json", "prop": "pageimages", "piprop": "thumbnail", "pithumbsize": 160, "redirects": 1, "titles": "|".join(tit(n) for n in lote)})
        raw = get("https://pt.wikipedia.org/w/api.php?" + q, 30)
        if not raw: continue
        d = json.loads(raw).get("query", {}); mapa = {x["to"]: x["from"] for x in d.get("redirects", [])}
        pg = {p["title"]: p.get("thumbnail", {}).get("source") for p in d.get("pages", {}).values()}
        for n in lote:
            t = tit(n); t = next((to for to, fr in mapa.items() if fr == t), t)
            if pg.get(t): out[n] = pg[t]
    return out
quer = sorted({p["nome"] for p in topo[:150]} | {p["nome"] for p in fixos})
F = fotos(quer)
for p in topo:
    if p["nome"] in F: p["foto"] = F[p["nome"]]
print("fotos:", len(F), "de", len(quer), flush=True)

verbas = {}
for p in topo:
    if p["poder"] in ("J", "MP"):
        for k, v in p["it"]:
            if k.lower().startswith(("vencimentos", "subsídio", "subsidio")): continue
            s = verbas.setdefault(k, {"item": k, "total": 0, "n": 0}); s["total"] += v; s["n"] += 1
saida = {"gerado": hoje.isoformat(), "teto": TETO, "fonte": "DadosJusBr (CC-BY-4.0), SIAPE/Portal da Transparência, fotos da Wikipédia", "n": len(topo),
         "ranking": topo, "verbas": sorted(verbas.values(), key=lambda s: -s["total"])[:40]}
(RAIZ / "web/public/data/remuneracoes.json").write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(len(topo), "no ranking | maior:", topo[0]["nome"], topo[0]["bruta"], "|", len(verbas), "tipos de verba")
