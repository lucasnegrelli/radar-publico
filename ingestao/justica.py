"""Remuneração do Sistema de Justiça (juízes, desembargadores, ministros, procuradores) via DadosJusBr (Transparência Brasil), licença CC-BY-4.0.
O CNJ só publica painel, não dados abertos; o DadosJusBr coleta e padroniza os contracheques de ~124 órgãos (tribunais, MPs, conselhos). API: https://api.dadosjusbr.org/v2
Para cada órgão pega o mês mais recente disponível e resume: quantos membros, média e máximo da remuneração BRUTA (salário + benefícios/indenizações), % acima do teto constitucional.
ATENÇÃO: verbas indenizatórias ficam fora do teto por lei; "acima do teto" aqui NÃO é irregularidade, é retrato de quanto o total pago passa do subsídio. Nomes abreviados.
Saída: web/public/data/justica.json"""
import datetime, io, json, os, pathlib, time, urllib.request, zipfile, duckdb

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
UA = {"User-Agent": "radar-publico/0.1 (+https://github.com/lucasnegrelli/radar-publico)"}
API = "https://api.dadosjusbr.org/v2"
TETO = 46366.19   # subsídio de ministro do STF (vigente desde 02/2025); atualizar se mudar
TMP = RAIZ / "dados" / "justica"; TMP.mkdir(parents=True, exist_ok=True)

def get(u, t=60):
    for i in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t).read()
        except Exception: time.sleep(2 + 3 * i)
    return None

orgaos = json.loads(get(API + "/orgaos"))
hoje = datetime.date.today()
meses = []
a, m = hoje.year, hoje.month
for _ in range(5):
    m -= 1
    if m == 0: a, m = a - 1, 12
    meses.append((a, m))
abrevia = lambda nm: " ".join([nm.split()[0].title()] + [p[0] + "." for p in nm.split()[1:] if len(p) > 3]) if nm else "–"
def um(o):
    c = duckdb.connect()
    oid = o["id_orgao"]
    for ano, mes in meses:
        raw = get(f"{API}/dados/{oid}/{ano}/{mes}", 30)
        if not raw: continue
        try: d = json.loads(raw)
        except Exception: continue
        url = (d.get("pacote_de_dados") or {}).get("url")
        if not url: continue
        z = get(url, 120)
        if not z: continue
        try:
            zf = zipfile.ZipFile(io.BytesIO(z)); pasta = TMP / f"{oid}-{ano}-{mes}"; zf.extract("contracheque.csv", pasta)
        except Exception: continue
        f = (pasta / "contracheque.csv").as_posix()
        c.execute(f"""create or replace table t as select nome, funcao, local_trabalho,
            try_cast(replace(salario, ',', '.') as double) salario, try_cast(replace(beneficios, ',', '.') as double) benef,
            try_cast(replace(remuneracao, ',', '.') as double) liquida from read_csv('{f}', delim=';', header=true, all_varchar=true, ignore_errors=true)
            where try_cast(replace(salario, ',', '.') as double) is not null""")
        c.execute("alter table t add column bruta double"); c.execute("update t set bruta = salario + coalesce(benef, 0)")
        n, med, mx, acima, soma_ex = c.execute(f"select count(*), avg(bruta), max(bruta), count(*) filter (where bruta > {TETO} + 1), coalesce(sum(bruta - {TETO}) filter (where bruta > {TETO} + 1), 0) from t").fetchone()
        if not n: continue
        r = {"id": oid, "nome": o["nome"], "jurisdicao": o["jurisdicao"], "entidade": o["entidade"], "uf": o.get("uf"), "ref": f"{mes:02d}/{ano}", "n": n,
             "media": round(med), "max": round(mx), "acima_teto": acima, "pct_acima": round(100 * acima / n, 1), "excedente": round(soma_ex)}
        tp = [{"nome": abrevia(nm), "funcao": (fn or "").title()[:60], "orgao": o["nome"], "ref": f"{mes:02d}/{ano}", "bruta": round(b), "subsidio": round(s or 0), "liquida": round(lq or 0)}
              for nm, fn, lt, b, s, lq in c.execute("select nome, funcao, local_trabalho, bruta, salario, liquida from t order by bruta desc limit 3").fetchall()]
        print(oid, f"{mes:02d}/{ano}", n, "membros;", acima, "acima do teto", flush=True)
        return r, tp
    return None
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(8) as ex: rs = [x for x in ex.map(um, orgaos) if x]
res = [x[0] for x in rs]; top = [y for x in rs for y in x[1]]
top.sort(key=lambda x: -x["bruta"])
res.sort(key=lambda x: -x["excedente"])
out = {"teto": TETO, "fonte": "DadosJusBr (Transparência Brasil), CC-BY-4.0", "n_orgaos": len(res), "n_membros": sum(r["n"] for r in res), "n_acima": sum(r["acima_teto"] for r in res),
       "excedente_mensal": sum(r["excedente"] for r in res), "orgaos": res, "top": top[:40]}
(RAIZ / "web/public/data").mkdir(parents=True, exist_ok=True)
(RAIZ / "web/public/data/justica.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print(out["n_orgaos"], "órgãos;", out["n_membros"], "membros;", out["n_acima"], "acima do teto")
