"""Cartões de pagamento do governo federal (CPGF, "cartão corporativo") via API do Portal da Transparência.
Coleta em lotes que RETOMAM de onde pararam (estado em dados/portal/estado.json, transações em dados/portal/cpgf/AAAA-MM.jsonl), para caber nos limites da API
e rodar à noite no GitHub Actions. Uso: python ingestao/portal_cartoes.py [meses_para_tras=12] [minutos_de_orcamento=150]
Saída: web/public/data/cartoes.json (totais, maiores estabelecimentos, saques, unidades gestoras, cruzamento com CEIS/CNEP na data da compra).
Cruzar com sanção não prova irregularidade: pode haver decisão judicial, erro de cadastro ou compra de antes da sanção ser registrada."""
import datetime, json, os, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import portal_api as api

RAIZ = pathlib.Path(__file__).parent.parent; os.chdir(RAIZ)
if not api.TEM_CHAVE: print("sem PORTAL_TOKEN: pulando"); sys.exit(0)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
ORC = float(sys.argv[2]) * 60 if len(sys.argv) > 2 else 150 * 60
T0 = time.time()
D = RAIZ / "dados/portal"; (D / "cpgf").mkdir(parents=True, exist_ok=True)
(RAIZ / "web/public/data").mkdir(parents=True, exist_ok=True)
EST = D / "estado.json"; estado = json.loads(EST.read_text(encoding="utf-8")) if EST.exists() else {}
hoje = datetime.date.today().replace(day=1)
meses = []; m = hoje
for _ in range(N):
    m = (m - datetime.timedelta(days=1)).replace(day=1); meses.append(m)     # mês fechado mais recente primeiro (o corrente raramente tem extrato)
salva = lambda: EST.write_text(json.dumps(estado, ensure_ascii=False), encoding="utf-8")

for m in (meses if ORC > 0 else []):
    k = m.strftime("%Y-%m"); st = estado.setdefault("cpgf", {}).setdefault(k, {"pagina": 1, "feito": False})
    recente = m >= (hoje - datetime.timedelta(days=75))
    if st["feito"] and not recente: continue
    if st["feito"] and recente: st["pagina"] = 1; st["feito"] = False; (D / "cpgf" / f"{k}.jsonl").unlink(missing_ok=True)   # meses recentes podem ser corrigidos: recoleta
    arq = D / "cpgf" / f"{k}.jsonl"; mm = m.strftime("%m/%Y")
    with open(arq, "a", encoding="utf-8") as f:
        while time.time() - T0 < ORC:
            r = api.get("/cartoes", pagina=st["pagina"], mesExtratoInicio=mm, mesExtratoFim=mm)
            if r is None: print("falha em", k, "pág", st["pagina"]); break
            if not r: st["feito"] = True; break
            for x in r:
                e = x.get("estabelecimento") or {}; u = x.get("unidadeGestora") or {}; o = u.get("orgaoVinculado") or {}
                f.write(json.dumps({"d": x.get("dataTransacao"), "v": x.get("valorTransacao"), "t": (x.get("tipoCartao") or {}).get("codigo"), "cnpj": e.get("cnpjFormatado"), "cpf": bool(e.get("cpfFormatado")),
                                    "nome": e.get("razaoSocialReceita") or e.get("nome"), "tipo": e.get("tipo"), "ug": u.get("nome"), "org": (o.get("nome") if isinstance(o, dict) else None)}, ensure_ascii=False) + "\n")
            st["pagina"] += 1
            if st["pagina"] % 25 == 0: salva(); f.flush(); print(k, "pág", st["pagina"], f"{int(time.time() - T0)}s", flush=True)
    salva(); print(k, "feito" if st["feito"] else f"parou na pág {st['pagina']}", flush=True)
    if time.time() - T0 >= ORC: print("orçamento de tempo esgotado; continua na próxima rodada"); break

# ---------- agregação ----------
import duckdb
arqs = sorted((D / "cpgf").glob("*.jsonl"))
if not arqs: sys.exit(0)
c = duckdb.connect()
c.execute(f"""create table tx as select try_strptime(d, '%d/%m/%Y')::date dia, try_cast(replace(replace(v, '.', ''), ',', '.') as double) valor, t, regexp_replace(coalesce(cnpj, ''), '\\D', '', 'g') cnpj, cpf, nome, tipo, ug, org
  from read_json_auto([{", ".join("'" + a.as_posix() + "'" for a in arqs)}], format='newline_delimited', ignore_errors=true) where d is not null""")
c.execute("create view ceis as select * from read_parquet('dados/tse/ceis.parquet')"); c.execute("create view cnep as select * from read_parquet('dados/tse/cnep.parquet')") if (RAIZ / "dados/tse/cnep.parquet").exists() else None
try:
    c.execute("""create table sanc as select lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\\D','','g'),14,'0') doc, "CATEGORIA DA SANÇÃO" cat, "ÓRGÃO SANCIONADOR" orgao, "ABRAGÊNCIA DA SANÇÃO" abr,
        try_strptime("DATA INÍCIO SANÇÃO",'%d/%m/%Y')::date ini, try_strptime("DATA FINAL SANÇÃO",'%d/%m/%Y')::date fim from ceis
        union all select lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\\D','','g'),14,'0'), "CATEGORIA DA SANÇÃO", "ÓRGÃO SANCIONADOR", "ABRAGÊNCIA DA SANÇÃO",
        try_strptime("DATA INÍCIO SANÇÃO",'%d/%m/%Y')::date, try_strptime("DATA FINAL SANÇÃO",'%d/%m/%Y')::date from cnep""")
    c.execute("delete from sanc where cat ilike 'Multa%' or cat ilike 'Publica%' or cat ilike 'Demiss%' or cat ilike 'Perdimento%' or cat ilike 'Dissolu%'")
except Exception as e:
    print("sem listas de sanções:", str(e)[:60]); c.execute("create table sanc(doc varchar, cat varchar, orgao varchar, abr varchar, ini date, fim date)")
tot = c.execute("select count(*), round(sum(valor)), min(dia), max(dia) from tx where valor > 0").fetchone()
por_mes = c.execute("select strftime(dia, '%Y-%m') m, count(*), round(sum(valor)) from tx where valor > 0 group by 1 order by 1").fetchall()
top_est = c.execute("""select nome, any_value(cnpj) cnpj, any_value(tipo) tipo, count(*) n, round(sum(valor)) v, count(distinct ug) ugs from tx where valor > 0 and not cpf and cnpj <> '' and nome not ilike '%saque%'
   group by nome, cnpj order by v desc limit 25""").fetchall()
saques = c.execute("""select ug, any_value(org) org, count(*) n, round(sum(valor)) v from tx where valor > 0 and (nome ilike '%saque%' or tipo ilike '%saque%') group by ug order by v desc limit 15""").fetchall()
por_ug = c.execute("select ug, any_value(org) org, count(*) n, round(sum(valor)) v from tx where valor > 0 group by ug order by v desc limit 15").fetchall()
cruz = c.execute("""select t.nome, t.cnpj, count(*) n, round(sum(t.valor)) v, any_value(s.cat) cat, any_value(s.orgao) orgao, any_value(s.abr) abr, min(t.dia) de, max(t.dia) ate, count(distinct t.ug) ugs
   from tx t join sanc s on s.doc = lpad(t.cnpj, 14, '0') where t.valor > 0 and t.cnpj <> '' and not t.cpf and t.dia >= s.ini and (s.fim is null or t.dia <= s.fim) group by t.nome, t.cnpj order by v desc limit 30""").fetchall()
j = lambda rows, cols: [dict(zip(cols, r)) for r in rows]
out = {"gerado": datetime.date.today().isoformat(), "fonte": "Portal da Transparência (CGU), Cartões de Pagamento (CPGF)", "n": tot[0], "valor": tot[1], "de": str(tot[2]), "ate": str(tot[3]),
       "meses": j(por_mes, ["m", "n", "v"]), "estabelecimentos": j(top_est, ["nome", "cnpj", "tipo", "n", "v", "ugs"]), "saques": j(saques, ["ug", "org", "n", "v"]), "unidades": j(por_ug, ["ug", "org", "n", "v"]),
       "sancionadas": j(cruz, ["nome", "cnpj", "n", "v", "cat", "orgao", "abr", "de", "ate", "ugs"]),
       "completo": all(v.get("feito") for k, v in estado.get("cpgf", {}).items())}
(RAIZ / "web/public/data/cartoes.json").write_text(json.dumps(out, ensure_ascii=False, default=str, separators=(",", ":")), encoding="utf-8")
print("cartões:", tot[0], "transações | R$", tot[1], "|", len(cruz), "estabelecimentos com sanção na data da compra")
