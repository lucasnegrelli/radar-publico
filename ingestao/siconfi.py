"""Lista de entes (estados e municípios) do Tesouro/SICONFI -> dados/siconfi_entes.jsonl"""
import json, pathlib, urllib.request
out = pathlib.Path(__file__).parent.parent / "dados" / "siconfi_entes.jsonl"
off, n = 0, 0
with out.open("w", encoding="utf-8") as f:
    while True:
        url = f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/entes?limit=5000&offset={off}"
        r = json.load(urllib.request.urlopen(url, timeout=60))
        for i in r["items"]:
            f.write(json.dumps(i, ensure_ascii=False) + "\n"); n += 1
        if not r.get("hasMore"): break
        off += 5000
print(n, "entes")
