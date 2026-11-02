"""DataJud (CNJ): ações de improbidade administrativa (classe 64) por tribunal e ano -> web/public/data/judiciario.json
A chave da API é pública (divulgada pelo CNJ na wiki do DataJud)."""
import json, time, pathlib, datetime, urllib.request
KEY = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
RAIZ = pathlib.Path(__file__).parent.parent
TJ = {"ac":"AC","al":"AL","am":"AM","ap":"AP","ba":"BA","ce":"CE","dft":"DF","es":"ES","go":"GO","ma":"MA","mg":"MG","ms":"MS","mt":"MT","pa":"PA","pb":"PB","pe":"PE","pi":"PI","pr":"PR","rj":"RJ","rn":"RN","ro":"RO","rr":"RR","rs":"RS","sc":"SC","se":"SE","sp":"SP","to":"TO"}
TRF = {"trf1": "Região 1 (DF e 12 estados)", "trf2": "Região 2 (RJ e ES)", "trf3": "Região 3 (SP e MS)", "trf4": "Região 4 (Sul)", "trf5": "Região 5 (Nordeste)", "trf6": "Região 6 (MG)"}
CONSULTA = {"size": 0, "query": {"term": {"classe.codigo": 64}}, "aggs": {"por_ano": {"date_histogram": {"field": "dataAjuizamento", "calendar_interval": "year", "min_doc_count": 0}}}}

def consultar(alias):
    req = urllib.request.Request(f"https://api-publica.datajud.cnj.jus.br/api_publica_{alias}/_search", data=json.dumps(CONSULTA).encode(),
                                 headers={"Authorization": "APIKey " + KEY, "Content-Type": "application/json"})
    for t in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r: return json.loads(r.read())
        except Exception as e:
            print("  tentativa", t + 1, alias, str(e)[:80], flush=True); time.sleep(8 * (t + 1))
    return None

saida = []
for sufixo, uf in TJ.items():
    d = consultar("tj" + sufixo)
    if not d: continue
    anos = {b["key_as_string"][:4]: b["doc_count"] for b in d["aggregations"]["por_ano"]["buckets"] if b["key_as_string"][:4] >= "2015"}
    saida.append({"sigla": "TJ" + uf, "nome": f"Tribunal de Justiça ({uf})", "uf": uf, "esfera": "Estadual", "total": d["hits"]["total"]["value"], "anos": anos}); print("TJ" + uf, saida[-1]["total"], flush=True)
for alias, nome in TRF.items():
    d = consultar(alias)
    if not d: continue
    anos = {b["key_as_string"][:4]: b["doc_count"] for b in d["aggregations"]["por_ano"]["buckets"] if b["key_as_string"][:4] >= "2015"}
    saida.append({"sigla": alias.upper(), "nome": f"Tribunal Regional Federal, {nome}", "uf": None, "esfera": "Federal", "total": d["hits"]["total"]["value"], "anos": anos}); print(alias, saida[-1]["total"], flush=True)
(RAIZ / "web/public/data/judiciario.json").write_text(json.dumps({"gerado": str(datetime.date.today()), "classe": "Ação de improbidade administrativa (classe CNJ 64)", "tribunais": saida}, ensure_ascii=False), encoding="utf-8")
print("FIM", len(saida), "tribunais", flush=True)
