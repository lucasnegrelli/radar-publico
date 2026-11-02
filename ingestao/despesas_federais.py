"""R11: dinheiro federal pago a empresa que, naquele mês, estava sancionada (CEIS/CNEP) com punição que alcança o governo federal,
ou que consta no CEPIM. Fonte: Portal da Transparência, "Recebimentos de recursos por favorecido" (todo pagamento federal, não só contrato do PNCP).
Últimos 12 meses publicados. Saída: data-publica/alertas_extra_r11.json"""
import json, os, glob, re, zipfile, datetime, pathlib, urllib.request, urllib.error, duckdb

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
D = RAIZ / "dados" / "despesas"; D.mkdir(parents=True, exist_ok=True)
hoje = datetime.date.today().replace(day=1)
meses = []
for k in range(1, 15):
    m = hoje
    for _ in range(k): m = (m - datetime.timedelta(days=1)).replace(day=1)
    meses.append(m)
ok = []
for m in meses:
    ym = m.strftime("%Y%m"); alvo = D / f"{ym}_RecebimentosRecursosPorFavorecido.csv"
    if not alvo.exists():
        try:
            z = D / f"{ym}.zip"; urllib.request.urlretrieve(f"https://portaldatransparencia.gov.br/download-de-dados/despesas-favorecidos/{ym}", z)
            zipfile.ZipFile(z).extractall(D); z.unlink()
        except Exception as e:
            print("sem", ym, str(e)[:50]); continue
    ok.append(ym)
    if len(ok) >= 12: break
print("meses:", ok, flush=True)

c = duckdb.connect()
for v, f in (("ceis", "ceis"), ("cnep", "cnep")):
    c.execute(f"create view {v} as select * from read_parquet('dados/tse/{f}.parquet')")
c.execute("create view emp as select cnpj_basico, natureza from read_parquet('dados/cnpj/empresas_*.parquet')")
csv = (D / "*_RecebimentosRecursosPorFavorecido.csv").as_posix()
c.execute(f"""create table pag as select lpad(regexp_replace(column00,'\\D','','g'),14,'0') doc, column01 nome, column02 uf, column03 mun, column05 sup, column07 orgao,
   make_date(try_cast(right(column10,4) as int), try_cast(left(column10,2) as int), 1) mes, try_cast(replace(replace(column11,'.',''),',','.') as double) valor
   from read_csv('{csv}', delim=';', header=false, skip=1, all_varchar=true, encoding='latin-1', columns={{{', '.join(f"'column{i:02d}': 'VARCHAR'" for i in range(12))}}}, sample_size=-1, union_by_name=false)
   where length(regexp_replace(column00,'\\D','','g')) = 14""")
print(c.execute("select count(*), round(sum(valor)/1e9,1) from pag").fetchone(), "pagamentos a PJ nos meses carregados (R$ bi)", flush=True)
c.execute("""create table sanc as
  select 'CEIS' lista, lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\\D','','g'),14,'0') doc, "CATEGORIA DA SANÇÃO" categoria, "ÓRGÃO SANCIONADOR" orgao, "ABRAGÊNCIA DA SANÇÃO" abr, "ESFERA ÓRGÃO SANCIONADOR" esf,
     try_strptime("DATA INÍCIO SANÇÃO",'%d/%m/%Y')::date ini, try_strptime("DATA FINAL SANÇÃO",'%d/%m/%Y')::date fim from ceis
  union all select 'CNEP', lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\\D','','g'),14,'0'), "CATEGORIA DA SANÇÃO", "ÓRGÃO SANCIONADOR", "ABRAGÊNCIA DA SANÇÃO", "ESFERA ÓRGÃO SANCIONADOR",
     try_strptime("DATA INÍCIO SANÇÃO",'%d/%m/%Y')::date, try_strptime("DATA FINAL SANÇÃO",'%d/%m/%Y')::date from cnep""")
c.execute("delete from sanc where categoria ilike 'Multa%' or categoria ilike 'Publica%' or categoria ilike 'Demiss%' or categoria ilike 'Perdimento%' or categoria ilike 'Dissolu%' or categoria ilike 'Proibi__o de receber%'")
c.execute("""create table cruz as
  select p.*, s.lista, s.categoria, s.orgao orgao_sanc, s.abr, s.ini, s.fim,
    case when s.abr ilike 'Todas as Esferas%' then 'alta'
         when s.abr ilike 'Em todos os Poderes%' and s.esf ilike 'Federal%' then 'alta'
         when s.abr ilike 'Na Esfera e no Poder%' and s.esf ilike 'Federal%' then 'media' end grav
  from pag p join sanc s on s.doc = p.doc
  where p.valor > 0 and p.mes >= date_trunc('month', s.ini) and (s.fim is null or p.mes <= s.fim)
    and not exists (select 1 from emp e where e.cnpj_basico = left(p.doc, 8) and (e.natureza like '1%' or e.natureza in ('2011','2038')))""")
rows = c.execute("""select doc, any_value(nome) nome, any_value(uf) uf, any_value(mun) mun, min(mes) ini_p, max(mes) fim_p, sum(valor) total, count(*) n, min(grav) grav_min,
     any_value(lista) lista, any_value(categoria) categoria, any_value(orgao_sanc) orgao_sanc, any_value(abr) abr
   from cruz where grav is not null group by doc having sum(valor) >= 50000 order by sum(valor) desc limit 150""").fetchall()
print(len(rows), "empresas", flush=True)
fmt_cnpj = lambda d: f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"
brl = lambda v: "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
alertas = []
for doc, nome, uf, mun, ip, fp, total, n, gmin, lista, cat, osanc, abr in rows:
    detalhe = c.execute("select mes, orgao, sum(valor) from cruz where doc = ? and grav is not null group by 1,2 order by 1 desc, 3 desc limit 14", [doc]).fetchall()
    orgaos = [r[0] for r in c.execute("select orgao from cruz where doc = ? and grav is not null group by 1 order by sum(valor) desc limit 3", [doc]).fetchall()]
    grav = "alta" if gmin == "alta" or total >= 5e6 else "media"
    alertas.append({"id": f"R11-{doc}", "regra": "R11", "gravidade": grav, "empresa": (nome or "").strip(" '").upper(), "cnpj": fmt_cnpj(doc), "total": total, "n": n, "inicio": str(ip), "fim": str(fp),
        "origem": {"lat": -15.7997, "lon": -47.8645, "nome": "Brasília"}, "local": None, "orgao": orgaos[0] if orgaos else "Governo federal", "orgao_uf": uf, "orgao_municipio": None,
        "manchete": {"tipo": "R11", "orgaos": orgaos, "sancao": cat, "lista": lista, "alcance": abr, "uf": uf, "mun": mun},
        "tabela": {"titulo": "Pagamentos federais no período da sanção", "cols": ["Mês", "Órgão pagador", "", "Valor", ""],
                   "linhas": [[{"t": str(r[0])[:7], "s": None, "u": None, "v": False}, {"t": r[1][:60], "s": None, "u": None, "v": False}, {"t": "", "s": None, "u": None, "v": False}, {"t": brl(r[2]), "s": None, "u": None, "v": True}, {"t": "–", "s": None, "u": None, "v": False}] for r in detalhe]},
        "sancao": {"lista": lista, "tipo": cat, "orgao": osanc, "alcance": abr, "inicio": None, "fim": None}})
out = RAIZ / "data-publica"; out.mkdir(exist_ok=True)
(out / "alertas_extra_r11.json").write_text(json.dumps(alertas, ensure_ascii=False, default=str), encoding="utf-8")
print(len(alertas), "alertas R11;", sum(1 for a in alertas if a["gravidade"] == "alta"), "altos; total R$", round(sum(a["total"] for a in alertas) / 1e6, 1), "mi")
