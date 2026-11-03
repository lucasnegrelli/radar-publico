"""Resumo por município para a aba "Minha cidade": emendas parlamentares pagas (por ano e por autor), prefeito eleito em 2024 e alertas do Radar na cidade.
Entrada: dados/emendas/EmendasParlamentares.csv (baixado por emendas.py), web/public/data/alertas.json e fichas.json. Saída: web/public/data/municipios.json"""
import json, os, re, pathlib, unicodedata, duckdb

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
norm = lambda s: re.sub(r"\s+", " ", "".join(c for c in unicodedata.normalize("NFD", (s or "").upper()) if unicodedata.category(c) != "Mn")).strip()
c = duckdb.connect()
cols = ["cod", "ano", "tipo", "cod_autor", "autor", "num", "local", "ibge", "mun", "cod_uf", "uf", "regiao", "c1", "funcao", "c2", "sub", "c3", "prog", "c4", "acao", "c5", "plano", "empenhado", "liquidado", "pago", "ri", "rc", "rp"]
spec = ", ".join(f"'column{i:02d}': 'VARCHAR'" for i in range(len(cols)))
c.execute(f"""create table em as select column01 ano, column04 autor, column08 mun, (select any_value(s) from (values ('11','RO'),('12','AC'),('13','AM'),('14','RR'),('15','PA'),('16','AP'),('17','TO'),('21','MA'),('22','PI'),('23','CE'),('24','RN'),('25','PB'),('26','PE'),('27','AL'),('28','SE'),('29','BA'),('31','MG'),('32','ES'),('33','RJ'),('35','SP'),('41','PR'),('42','SC'),('43','RS'),('50','MS'),('51','MT'),('52','GO'),('53','DF')) v(k, s) where k = left(column09, 2)) uf, column13 funcao,
   try_cast(replace(replace(column24,'.',''),',','.') as double) pago
   from read_csv('dados/emendas/EmendasParlamentares.csv', delim=';', header=false, skip=1, all_varchar=true, encoding='latin-1', columns={{{spec}}}, sample_size=-1)""")
rows = c.execute("""select uf, mun, ano, autor, funcao, sum(pago) from em where pago > 0 and length(uf) = 2 and mun is not null and mun not ilike 'M_ltiplo%' and mun not ilike 'Sem informa%'
   and autor not ilike 'Sem informa%' and try_cast(ano as int) >= 2019 group by all""").fetchall()
out = {}
for uf, mun, ano, autor, funcao, v in rows:
    k = f"{uf}|{norm(mun)}"
    d = out.setdefault(k, {"nome": mun.title(), "uf": uf, "anos": {}, "autores": {}, "areas": {}, "total": 0})
    d["anos"][ano] = d["anos"].get(ano, 0) + round(v); d["total"] += round(v)
    d["autores"][autor.title()] = d["autores"].get(autor.title(), 0) + round(v)
    d["areas"][funcao] = d["areas"].get(funcao, 0) + round(v)
for d in out.values():
    d["autores"] = sorted(d["autores"].items(), key=lambda x: -x[1])[:6]
    d["areas"] = sorted(d["areas"].items(), key=lambda x: -x[1])[:4]
alertas = json.loads((RAIZ / "web/public/data/alertas.json").read_text(encoding="utf-8"))["alertas"]
for a in alertas:
    loc = a.get("local")
    if not loc or a["regra"] == "RF01": continue
    k = f"{loc['uf']}|{norm(loc['cidade'])}"
    out.setdefault(k, {"nome": loc["cidade"].title(), "uf": loc["uf"], "anos": {}, "autores": [], "areas": [], "total": 0}).setdefault("alertas", []).append({"id": a["id"], "empresa": a["empresa"], "total": a["total"], "regra": a["regra"], "g": a["gravidade"]})
for d in out.values():
    d["alertas"] = sorted(d.get("alertas", []), key=lambda x: -x["total"])[:6]; d["n_alertas"] = len(d["alertas"])
fichas = json.loads((RAIZ / "web/public/data/fichas.json").read_text(encoding="utf-8"))["fichas"]
for f in fichas:
    if f["t"] == "pref":
        k = f"{f['u']}|{norm(f['c'])}"
        if k in out: out[k]["prefeito"] = {"nome": f["n"], "partido": f.get("p")}
(RAIZ / "web/public/data/municipios.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(len(out), "municípios;", round((RAIZ / "web/public/data/municipios.json").stat().st_size / 1e6, 1), "MB;", sum(1 for d in out.values() if d["total"]), "com emendas")
