"""Querido Diário: busca de termos de uma investigação nos diários oficiais municipais.
Entrada: casos/<caso>_consultas.json   Saída: data-publica/caso_<caso>_diarios.json
Roda no GitHub Actions (a conexão TLS do servidor falha no Windows local)."""
import json, sys, time, pathlib, urllib.parse, urllib.request
RAIZ = pathlib.Path(__file__).parent.parent
caso = sys.argv[1] if len(sys.argv) > 1 else "master"
cfg = json.loads((RAIZ / f"casos/{caso}_consultas.json").read_text(encoding="utf-8"))
API = "https://api.queridodiario.ok.org.br/gazettes"
vistos, saida = set(), []
for q in cfg["consultas"]:
    for off in range(0, 300, 50):
        params = urllib.parse.urlencode({"querystring": q, "published_since": cfg["desde"], "size": 50, "offset": off, "excerpt_size": 420, "number_of_excerpts": 2, "sort_by": "descending_date"})
        d = None
        for t in range(3):
            try:
                with urllib.request.urlopen(urllib.request.Request(f"{API}?{params}", headers={"accept": "application/json", "User-Agent": "radar-publico/0.1"}), timeout=90) as r:
                    d = json.loads(r.read()); break
            except Exception:
                time.sleep(6 * (t + 1))
        if not d or not d.get("gazettes"): break
        for g in d["gazettes"]:
            k = (g.get("url") or g.get("txt_url"))
            if k in vistos: continue
            vistos.add(k)
            saida.append({"cidade": g.get("territory_name"), "uf": g.get("state_code"), "ibge": g.get("territory_id"), "data": g.get("date"), "consulta": q,
                          "trechos": [" ".join(x.split()) for x in g.get("excerpts", [])[:2]], "url": k})
        print(q[:40], "offset", off, "| acumulado", len(saida), flush=True)
        time.sleep(0.5)
        if len(d["gazettes"]) < 50: break
(RAIZ / f"data-publica/caso_{caso}_diarios.json").write_text(json.dumps({"total": len(saida), "diarios": saida}, ensure_ascii=False), encoding="utf-8")
print("FIM", len(saida), "diários com menção")
