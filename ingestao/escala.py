"""Escala: quanto o painel cobre perto do tamanho do país. Saída: web/public/data/escala.json"""
import json, pathlib, duckdb
RAIZ = pathlib.Path(__file__).parent.parent
c = duckdb.connect()
P = (RAIZ / "dados/pncp/*.parquet").as_posix()
ano = c.execute(f"""select year(data_assinatura) a, count(*), round(sum(valor_global)/1e9, 1) from read_parquet('{P}')
  where data_assinatura between date '2025-01-01' and current_date and valor_global between 0 and 3e9 and not (valor_inicial = 0 and valor_global >= 5e6) group by 1 order by 1""").fetchall()
A = json.loads((RAIZ / "web/public/data/alertas.json").read_text(encoding="utf-8"))["alertas"]
em_atencao = sum(a["total"] for a in A if a["gravidade"] != "baixa") / 1e9
alta = sum(a["total"] for a in A if a["gravidade"] == "alta") / 1e9
pncp = sum(x[2] for x in ano)
out = {"pib_tri": 12.0, "pncp_anos": [{"ano": a, "contratos": n, "bi": b} for a, n, b in ano], "pncp_bi": pncp, "alertas_bi": round(em_atencao, 1), "alta_bi": round(alta, 1), "pct_pncp": round(100 * em_atencao / pncp, 2) if pncp else None, "pct_pib": round(100 * em_atencao / 12000, 3)}
(RAIZ / "web/public/data/escala.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print(out)
