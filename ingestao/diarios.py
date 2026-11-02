"""Querido Diário (Open Knowledge Brasil): busca o nome de cada empresa dos alertas nos diários oficiais municipais.
Entrada: data-publica/empresas.json  Saída: data-publica/diarios.json  (id do alerta -> menções)
Roda no GitHub Actions: a conexão TLS do servidor deles falha no Windows local."""
import json, time, pathlib, urllib.parse, urllib.request
RAIZ = pathlib.Path(__file__).parent.parent
entrada = json.loads((RAIZ / "data-publica/empresas.json").read_text(encoding="utf-8"))
API = "https://api.queridodiario.ok.org.br/gazettes"
saida = {}
for i, e in enumerate(entrada):
    q = urllib.parse.urlencode({"querystring": f'"{e["empresa"]}"', "published_since": "2025-01-01", "size": 5, "excerpt_size": 280, "number_of_excerpts": 2, "sort_by": "descending_date"})
    d = None
    for t in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(f"{API}?{q}", headers={"accept": "application/json", "User-Agent": "radar-publico/0.1"}), timeout=60) as r:
                d = json.loads(r.read()); break
        except Exception as ex:
            time.sleep(5 * (t + 1))
    if not d: continue
    ms = []
    for g in d.get("gazettes", []):
        if e.get("uf") and g.get("state_code") != e["uf"]: continue  # só diários do mesmo estado do alerta
        for ex in g.get("excerpts", [])[:1]:
            ms.append({"cidade": g.get("territory_name"), "uf": g.get("state_code"), "data": g.get("date"), "trecho": " ".join(ex.split()), "url": g.get("url") or g.get("txt_url")})
    if ms: saida[e["id"]] = ms[:4]
    if i % 20 == 0: print(i, "/", len(entrada), "| com menção:", len(saida), flush=True)
    time.sleep(0.4)
(RAIZ / "data-publica/diarios.json").write_text(json.dumps(saida, ensure_ascii=False), encoding="utf-8")
print("FIM", len(saida), "alertas com menção em diário oficial")
