"""Votos nominais dos deputados (arquivos abertos da Câmara, 2023 em diante) e alinhamento com a orientação do Governo.
Para cada deputado: votos dados, distribuição (Sim, Não, Abstenção, Obstrução...) e % de votos iguais à orientação do Governo, nas votações em que o Governo orientou Sim ou Não.
Atenção: alinhamento não mede mérito; é um retrato de como votou frente à orientação. Saída: dados/camara_votos.json. Fonte: https://dadosabertos.camara.leg.br/arquivos"""
import json, os, pathlib, datetime, urllib.request, urllib.error, duckdb

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
D = RAIZ / "dados" / "camara_votos"; D.mkdir(parents=True, exist_ok=True)
B = "https://dadosabertos.camara.leg.br/arquivos"
ok = []
for ano in range(2023, datetime.date.today().year + 1):
    for nome, pasta in (("votos", "votacoesVotos"), ("orient", "votacoesOrientacoes")):
        alvo = D / f"{nome}{ano}.csv"
        if not alvo.exists() or ano == datetime.date.today().year:   # o ano corrente muda toda semana
            try: urllib.request.urlretrieve(f"{B}/{pasta}/csv/{pasta}-{ano}.csv", alvo)
            except urllib.error.HTTPError: continue
    if (D / f"votos{ano}.csv").exists() and (D / f"orient{ano}.csv").exists(): ok.append(ano)
print("anos:", ok, flush=True)
c = duckdb.connect()
rd = lambda pad: f"read_csv('{(D / pad).as_posix()}', delim=';', header=true, all_varchar=true, union_by_name=true, sample_size=-1, ignore_errors=true)"
c.execute(f"create table v as select idVotacao, voto, deputado_id id from {rd('votos*.csv')} where deputado_id is not null")
c.execute(f"create table o as select idVotacao, orientacao from {rd('orient*.csv')} where siglaBancada = 'Governo' and orientacao in ('Sim', 'Não')")
print(c.execute("select count(*) from v").fetchone()[0], "votos;", c.execute("select count(*) from o").fetchone()[0], "orientações do Governo", flush=True)
res = {}
for i, voto, n in c.execute("select id, voto, count(*) from v group by 1,2").fetchall():
    res.setdefault(i, {"votos": {}, "n": 0})["votos"][voto] = n; res[i]["n"] += n
for i, n, com in c.execute("select v.id, count(*), sum(case when v.voto = o.orientacao then 1 else 0 end) from v join o using (idVotacao) where v.voto in ('Sim', 'Não') group by 1").fetchall():
    res[i]["gov_n"] = n; res[i]["gov_com"] = com
(RAIZ / "dados" / "camara_votos.json").write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
print(len(res), "deputados com votos;", next(iter(res.items())))
