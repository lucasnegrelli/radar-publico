"""FIDC (CVM, informe mensal): fundos de direitos creditórios que têm previdência de servidores (RPPS) entre os cotistas.
O informe só traz o NÚMERO de cotistas RPPS (não o valor nem qual RPPS): aqui vira uma lista de observação, não um alerta.
Saída: web/public/data/fidc.json"""
import json, io, zipfile, urllib.request, urllib.error, pathlib, datetime, duckdb
RAIZ = pathlib.Path(__file__).parent.parent
D = RAIZ / "dados" / "fidc"; D.mkdir(parents=True, exist_ok=True)
hoje = datetime.date.today(); mes = None
for k in range(0, 5):
    m = (hoje.replace(day=1) - datetime.timedelta(days=30 * k)); ym = m.strftime("%Y%m")
    try:
        urllib.request.urlretrieve(f"https://dados.cvm.gov.br/dados/FIDC/DOC/INF_MENSAL/DADOS/inf_mensal_fidc_{ym}.zip", D / "f.zip"); mes = ym; break
    except urllib.error.HTTPError:
        continue
if not mes: raise SystemExit("informe de FIDC não encontrado")
zipfile.ZipFile(D / "f.zip").extractall(D)
rd = lambda t: f"read_csv('{(D / f'inf_mensal_fidc_tab_{t}_{mes}.csv').as_posix()}', delim=';', header=true, all_varchar=true, encoding='latin-1', sample_size=-1, ignore_errors=true)"
n = lambda c: f"try_cast(replace({c}, ',', '.') as double)"
c = duckdb.connect()
linhas = c.execute(f"""select i.CNPJ_FUNDO_CLASSE cnpj, i.DENOM_SOCIAL nome, i.ADMIN admin, {n('p.TAB_IV_A_VL_PL')} pl, try_cast(x.TAB_X_NR_COTST_SENIOR_RPPS as int) rpps_sr, try_cast(x.TAB_X_NR_COTST_SUBORD_RPPS as int) rpps_sub,
     i.CONDOM, i.FUNDO_EXCLUSIVO
   from {rd('I')} i join {rd('IV')} p using (CNPJ_FUNDO_CLASSE) join {rd('X_1_1')} x using (CNPJ_FUNDO_CLASSE)
   where coalesce(try_cast(x.TAB_X_NR_COTST_SENIOR_RPPS as int),0) + coalesce(try_cast(x.TAB_X_NR_COTST_SUBORD_RPPS as int),0) > 0 and {n('p.TAB_IV_A_VL_PL')} > 0
   order by pl desc""").fetchall()
tot = c.execute(f"select count(*), sum({n('TAB_IV_A_VL_PL')}) from {rd('IV')}").fetchone()
com_sub = [l for l in linhas if (l[5] or 0) > 0]
out = {"competencia": mes, "n_fundos": tot[0], "pl_total": tot[1], "n_com_rpps": len(linhas), "pl_com_rpps": sum(l[3] for l in linhas), "n_rpps_subordinada": len(com_sub), "pl_rpps_subordinada": sum(l[3] for l in com_sub),
       "fundos": [{"cnpj": l[0], "nome": l[1].title(), "admin": (l[2] or "").title(), "pl": l[3], "rpps_senior": l[4] or 0, "rpps_subordinada": l[5] or 0, "condominio": l[6], "exclusivo": l[7]} for l in sorted(linhas, key=lambda l: (-(l[5] or 0) > 0, -l[3]))[:60]]}
(RAIZ / "web/public/data").mkdir(parents=True, exist_ok=True)
(RAIZ / "web/public/data/fidc.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print(mes, out["n_fundos"], "FIDCs;", out["n_com_rpps"], "com RPPS (R$", round(out["pl_com_rpps"] / 1e9, 1), "bi);", out["n_rpps_subordinada"], "com RPPS em cota subordinada")
