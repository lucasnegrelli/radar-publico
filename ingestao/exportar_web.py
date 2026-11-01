"""Gera web/public/data/alertas.json a partir do DuckDB (1 alerta por empresa, com pagamentos e sanção detalhados)."""
import json, pathlib, datetime, duckdb
RAIZ = pathlib.Path(__file__).parent.parent
con = duckdb.connect(str(RAIZ / "dados" / "radar.duckdb"))
sql = (RAIZ / "alertas" / "01_sancionada_recebendo_cota.sql").read_text(encoding="utf-8").rstrip().rstrip(";")
con.execute("create or replace table alerta01 as " + sql)
est = (RAIZ / "dados" / "cnpj" / "estabelecimentos_*.parquet").as_posix()
con.execute(f"""create or replace table loc as
select a.cnpj, any_value(m.lat) lat, any_value(m.lon) lon, any_value(m.nome) cidade, any_value(e.uf) uf
from (select distinct cnpj from alerta01) a
join read_parquet('{est}') e on e.cnpj=a.cnpj
join mun_coord m on m.rfb=e.municipio and m.uf=e.uf group by a.cnpj""")
emp = con.execute("""select cnpj, fornecedor, any_value(lista), any_value(categoria), any_value(orgao), any_value(alcance),
  min(sancao_inicio), max(sancao_fim), sum(valor), count(*), min(emissao), max(emissao) from alerta01 group by cnpj, fornecedor""").fetchall()
pag = con.execute("select cnpj, casa, parlamentar, partido, uf, emissao, valor, tipo, url from alerta01 order by emissao").fetchall()
loc = {r[0]: r[1:] for r in con.execute("select * from loc").fetchall()}
por_cnpj = {}
for c, casa, parl, part, uf, em, val, tipo, url in pag:
    por_cnpj.setdefault(c, []).append({"casa": casa, "parlamentar": parl, "partido": part, "uf": uf, "data": str(em), "valor": val, "tipo": (tipo or "").strip().capitalize(), "url": url})
def fmt_cnpj(d): return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}" if len(d) == 14 and d[:3] != "000" else (f"CPF ***{d[-8:-2]}**" if d.startswith("000") else d)
saida = []
for i, (cnpj, nome, lista, cat, orgao, alc, ini, fim, total, n, d1, d2) in enumerate(sorted(emp, key=lambda r: -r[8])):
    l = loc.get(cnpj)
    gr = "alta" if alc.startswith(("AMPLO", "Todas", "Em todos")) else ("baixa" if alc.startswith("RESTRITO") else "media")
    saida.append({"id": f"R01-{i:03d}", "regra": "R01", "gravidade": gr, "empresa": nome, "cnpj": fmt_cnpj(cnpj), "total": total, "n": n,
      "primeiro": str(d1), "ultimo": str(d2),
      "sancao": {"lista": lista, "tipo": cat, "orgao": orgao, "alcance": alc, "inicio": str(ini), "fim": str(fim) if fim else None},
      "pagamentos": por_cnpj[cnpj],
      "local": {"lat": l[0], "lon": l[1], "cidade": l[2], "uf": l[3]} if l else None})
(RAIZ / "web" / "public" / "data").mkdir(parents=True, exist_ok=True)
(RAIZ / "web" / "public" / "data" / "alertas.json").write_text(json.dumps({"gerado": str(datetime.date.today()), "alertas": saida}, ensure_ascii=False), encoding="utf-8")
print(len(saida), "alertas por empresa;", sum(1 for s in saida if s["local"]), "localizadas")
