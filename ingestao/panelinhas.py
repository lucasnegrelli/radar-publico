"""Panelinhas: empresas em que 2+ políticos/candidatos de PARTIDOS DIFERENTES aparecem como sócios (quadro societário da Receita, cruzado com as fichas).
"Adversários na urna, sócios no CNPJ". Cruzamento por nome completo + 6 dígitos centrais do CPF (o mesmo das fichas). Entidades institucionais (associações, consórcios, conselhos)
ficam num grupo à parte: sócios em associação de municípios é normal. Isto NÃO indica irregularidade: sociedade é legal; mostra quem se liga a quem.
Entrada: web/public/data/pessoas/s*.json. Saída: web/public/data/panelinhas.json"""
import glob, json, os, pathlib, collections, re

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
emp, P = collections.defaultdict(dict), {}
for f in glob.glob("web/public/data/pessoas/s*.json"):
    for pid, v in json.load(open(f, encoding="utf-8")).items():
        P[pid] = v
        for e in v.get("empresas") or []:
            emp[e["cnpj"]].setdefault(pid, e)
INST = re.compile(r"\b(associa[cç][aã]o|cons[oó]rcio|conselho|sindicato|federa[cç][aã]o|confedera[cç][aã]o|fundo|cooperativa|c[aâ]mara de|instituto)\b", re.I)
def pol(pid):
    v = P[pid]; c = (v.get("cand") or [{}])[0]
    return {"id": pid, "nome": v["n"], "partido": v.get("partido") or c.get("partido") or "", "uf": v.get("uf") or "", "cargo": c.get("cargo") or "", "ano": c.get("ano"), "qual": emp_q.get(pid, "")}
out_pan, out_inst = [], []
for cnpj, d in emp.items():
    if len(d) < 2: continue
    emp_q = {pid: e.get("qual", "") for pid, e in d.items()}
    ps = [pol(pid) for pid in d]
    partidos = {p["partido"] for p in ps if p["partido"]}
    nome = next(iter(d.values()))["nome"]
    item = {"cnpj": cnpj, "empresa": nome, "capital": next(iter(d.values())).get("capital"), "situacao": next(iter(d.values())).get("situacao"), "uf": next(iter(d.values())).get("uf"),
            "partidos": sorted(partidos), "n": len(ps), "pessoas": sorted(ps, key=lambda p: p["nome"])[:12], "cruzado": len(partidos) >= 2}
    (out_inst if INST.search(nome) else out_pan).append(item)
# família (mesmo sobrenome final comum, mesmo partido) vira ruído: destaca só os de partidos diferentes
ruzado = sorted([x for x in out_pan if x["cruzado"]], key=lambda x: (-len(x["partidos"]), -x["n"]))
out = {"n_empresas_com_2mais": len(out_pan) + len(out_inst), "n_partidos_diferentes": len(ruzado), "n_institucionais": len(out_inst),
       "panelinhas": ruzado[:150], "institucionais": sorted([x for x in out_inst if x["cruzado"]], key=lambda x: -x["n"])[:30]}
(RAIZ / "web/public/data/panelinhas.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print(out["n_empresas_com_2mais"], "empresas com 2+ políticos;", len(ruzado), "com partidos diferentes (não institucionais)")
