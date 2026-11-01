"""Deputados em exercício (API da Câmara) -> dados/camara_deputados.jsonl. Tenta de novo se a API der 5xx."""
import json, pathlib, time, urllib.request
out = pathlib.Path(__file__).parent.parent / "dados" / "camara_deputados.jsonl"
req = lambda u: urllib.request.Request(u, headers={"accept": "application/json"})
n, pag = 0, 1
with out.open("w", encoding="utf-8") as f:
    while True:
        for t in range(5):
            try:
                d = json.load(urllib.request.urlopen(req(f"https://dadosabertos.camara.leg.br/api/v2/deputados?itens=100&pagina={pag}"), timeout=60))["dados"]; break
            except Exception as e:
                print("tentativa", t + 1, e); time.sleep(5)
        else:
            raise SystemExit("API da Câmara indisponível")
        if not d: break
        for x in d: f.write(json.dumps(x, ensure_ascii=False) + "\n"); n += 1
        pag += 1
print(n, "deputados")
