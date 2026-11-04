"""Instituições financeiras em regime especial (liquidação extrajudicial, RAET, intervenção) -> web/public/data/bcb_regimes.json
Fonte: Banco Central, dados abertos (Olinda, serviço regimes_especiais, sem chave). Dá o CNPJ, o tipo de regime e a data de início; os valores (captação, garantia do FGC) vêm
dos balancetes (IF.data) e dos comunicados do BC e do FGC, que não têm API aberta estável."""
import datetime, json, os, pathlib, urllib.request

RAIZ = pathlib.Path(__file__).parent.parent; os.chdir(RAIZ)
U = "https://olinda.bcb.gov.br/olinda/servico/regimes_especiais/versao/v1/odata/Regimes?$format=json&$orderby=Inicio%20desc"
d = json.loads(urllib.request.urlopen(urllib.request.Request(U, headers={"User-Agent": "RadarPublico/1.0 (projeto civico; github.com/lucasnegrelli/radar-publico)"}), timeout=60).read())
itens = [{"raiz": x.get("CnpjRaiz"), "cnpj": x.get("CnpjInstituicao"), "nome": x.get("NomeInstituicao"), "inicio": x.get("Inicio"), "tipo": x.get("Tipo"), "uf": x.get("UF"), "municipio": x.get("Municipio")} for x in d.get("value", [])]
ordem = lambda i: "".join(reversed((i["inicio"] or "00/00/0000").split("/")))
itens.sort(key=ordem, reverse=True)
(RAIZ / "web/public/data/bcb_regimes.json").write_text(json.dumps({"gerado": datetime.date.today().isoformat(), "fonte": "Banco Central do Brasil, dados abertos (regimes especiais)", "n": len(itens), "itens": itens}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(len(itens), "instituições em regime especial | mais recente:", itens[0]["nome"] if itens else "-", itens[0]["inicio"] if itens else "")
