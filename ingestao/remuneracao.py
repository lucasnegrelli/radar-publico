"""Remuneração de servidores federais acima do teto (SIAPE, Portal da Transparência).
O teto do mês é INFERIDO dos próprios dados: é o valor em que a remuneração fica cortada ("abate-teto") para quem estourou. Depois olhamos quem continua acima desse valor
mesmo com o abate (corte incompleto), quem tem valor acima do teto sem abate algum, e onde isso se concentra (por órgão).
Isto NÃO é alerta de irregularidade: há exceções legais (acumulação permitida de cargos, parcelas eventuais fora do teto, vínculos distintos). Serve de lista de conferência.
Privacidade: nome abreviado, cargo, órgão e link do Portal. Precisa de dados/siape/<mes>_Remuneracao.csv e _Cadastro.csv (baixados por servidores.py). Saída: web/public/data/remuneracao.json"""
import json, os, re, glob, pathlib, duckdb

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
D = RAIZ / "dados" / "siape"
cad = sorted(glob.glob(str(D / "*_Cadastro.csv")))
if not cad:
    print("sem cadastro do SIAPE (rode servidores.py antes)"); raise SystemExit(0)
mes = pathlib.Path(cad[-1]).name[:6]
rem = D / f"{mes}_Remuneracao.csv"
if not rem.exists():
    print("sem arquivo de remuneração para", mes); raise SystemExit(0)
c = duckdb.connect()
cols = ", ".join(f"'column{i:02d}': 'VARCHAR'" for i in range(39))
n = lambda i: f"try_cast(replace(column{i:02d}, ',', '.') as double)"
c.execute(f"""create table r as select column02 id, column04 nome, {n(5)} bruta, {n(7)} abate, {n(15)} eventual, {n(29)} liquida
   from read_csv('{rem.as_posix()}', delim=';', header=false, all_varchar=true, encoding='utf-8', columns={{{cols}}}, ignore_errors=true) where column00 = '{mes[:4]}'""")
c.execute(f"""create table k as select Id_SERVIDOR_PORTAL id, any_value(DESCRICAO_CARGO) cargo, any_value(ORG_EXERCICIO) orgao, any_value(ORGSUP_EXERCICIO) orgsup, any_value(SITUACAO_VINCULO) sit, count(*) vinculos
   from read_csv('{cad[-1]}', delim=';', header=true, all_varchar=true, encoding='latin-1', sample_size=-1, ignore_errors=true) group by 1""")
# teto do mês: valor mais comum de (bruta + abate) entre quem teve corte
print(c.execute("select round(bruta + abate, 2) v, count(*) q from r where abate < -0.01 and bruta + abate > 20000 group by 1 having count(*) >= 20 order by 2 desc limit 6").fetchall(), flush=True)
# teto = o MAIOR valor-de-corte repetido por muita gente (subtetos estaduais/municipais cortam em valores menores; o federal é o mais alto)
teto = c.execute("select round(mode(round(bruta + abate, 2)), 2) from r where abate < -0.01 and bruta + abate > 40000").fetchone()[0]
print("mês", mes, "| teto inferido:", teto, flush=True)
c.execute("create table r1 as select distinct on (id) * from r order by id, bruta desc"); c.execute("drop table r"); c.execute("alter table r1 rename to r")
tot = c.execute("select count(*) from r").fetchone()[0]
c.execute(f"create table x as select r.*, k.cargo, k.orgao, k.orgsup, k.sit, k.vinculos, (r.bruta + coalesce(r.abate, 0)) - {teto} excedente from r left join k using (id) where (r.bruta + coalesce(r.abate, 0)) > {teto} + 1")
n_acima = c.execute("select count(*) from x").fetchone()[0]
n_sem_abate = c.execute("select count(*) from x where coalesce(abate, 0) > -0.01").fetchone()[0]
org = c.execute("select coalesce(orgao, 'Sem informação'), count(*), round(sum(excedente)) from x group by 1 order by 3 desc limit 15").fetchall()
abrevia = lambda nm: " ".join([nm.split()[0].title()] + [p[0] + "." for p in nm.split()[1:] if len(p) > 2]) if nm else "–"
casos = [{"id": i, "nome": abrevia(nome), "cargo": (cg or "").title()[:50], "orgao": og, "bruta": b, "abate": a or 0, "excedente": round(e, 2), "sem_abate": (a or 0) > -0.01, "vinculos": vq}
         for i, nome, b, a, cg, og, e, vq in c.execute("select id, nome, bruta, abate, cargo, orgao, excedente, vinculos from x order by excedente desc limit 60").fetchall()]
out = {"mes": mes, "teto": teto, "n_servidores": tot, "n_acima": n_acima, "n_sem_abate": n_sem_abate, "excedente_mensal": round(c.execute("select coalesce(sum(excedente), 0) from x").fetchone()[0]),
       "orgaos": [{"orgao": o, "n": q, "excedente": v} for o, q, v in org], "casos": casos}
(RAIZ / "web/public/data").mkdir(parents=True, exist_ok=True)
(RAIZ / "web/public/data/remuneracao.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print(tot, "remunerações;", n_acima, "acima do teto;", n_sem_abate, "sem nenhum abate; excedente mensal R$", out["excedente_mensal"])
