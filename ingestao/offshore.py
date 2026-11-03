"""ICIJ Offshore Leaks (Panama, Paradise, Pandora Papers etc.): pessoas ligadas ao Brasil e as empresas offshore em que aparecem.
Saída: dados/offshore_br.json  (nome normalizado -> ocorrências). O cruzamento com políticos é feito em pessoas.py, por nome completo,
e SEMPRE marcado como "coincidência de nome, confirmar": constar nos vazamentos não indica ilegalidade (ter empresa offshore pode ser legal e declarado).
Fonte: https://offshoreleaks.icij.org (licença ODbL; cite o ICIJ)."""
import json, os, re, zipfile, pathlib, unicodedata, urllib.request, duckdb

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
D = RAIZ / "dados" / "offshore"; D.mkdir(parents=True, exist_ok=True)
Z = D / "oldb.zip"
if not Z.exists():
    urllib.request.urlretrieve("https://offshoreleaks-data.icij.org/offshoreleaks/csv/full-oldb.LATEST.zip", Z)
    zipfile.ZipFile(Z).extractall(D)
norm = lambda s: re.sub(r"\s+", " ", "".join(c for c in unicodedata.normalize("NFD", (s or "").upper()) if unicodedata.category(c) != "Mn")).strip()
rd = lambda n: f"read_csv('{(D / n).as_posix()}', header=true, all_varchar=true, sample_size=-1, ignore_errors=true)"
c = duckdb.connect()
c.execute(f"create table off as select node_id, name, countries, sourceID fonte from {rd('nodes-officers.csv')} where country_codes like '%BRA%'")
c.execute(f"create table ent as select node_id, name, jurisdiction_description jur, status, incorporation_date inicio, sourceID fonte from {rd('nodes-entities.csv')}")
c.execute(f"create table rel as select node_id_start a, node_id_end b, link from {rd('relationships.csv')} where node_id_start in (select node_id from off)")
print(c.execute("select count(*) from off").fetchone()[0], "pessoas ligadas ao Brasil nos vazamentos", flush=True)
rows = c.execute("""select o.node_id, o.name, o.fonte, e.name, e.jur, e.status, e.inicio, r.link
   from off o left join rel r on r.a = o.node_id left join ent e on e.node_id = r.b""").fetchall()
out = {}
for nid, nome, fonte, en, jur, st, ini, link in rows:
    k = norm(nome)
    if len(k.split()) < 3: continue   # nome curto demais: coincidência demais
    o = out.setdefault(k, {}).setdefault(nid, {"id": nid, "nome": nome.title(), "fonte": fonte, "entidades": []})
    if en and len(o["entidades"]) < 5: o["entidades"].append({"nome": en.title(), "jurisdicao": jur, "status": st, "inicio": ini, "vinculo": link})
out = {k: list(v.values()) for k, v in out.items()}
(RAIZ / "dados" / "offshore_br.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print(len(out), "nomes completos (3+ palavras) ->", round((RAIZ / "dados" / "offshore_br.json").stat().st_size / 1e6, 1), "MB")
