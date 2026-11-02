"""Validação interna dos detectores contra casos conhecidos (não aparece no painel).
Falha se um detector deixar de acender para um caso do nível do Banco Master.
Uso: python ingestao/testes/test_deteccao_casos.py"""
import pathlib, sys, duckdb
R = pathlib.Path(__file__).resolve().parents[2]
c = duckdb.connect()
sinais = c.execute(f"""
with v as (select AnoMes, CodInst, max(case when Coluna='Ativo Total' then Saldo end) ativo, max(case when Coluna='Captações' then Saldo end) cap, max(case when Coluna='Patrimônio Líquido' then Saldo end) pl
           from read_parquet('{(R/'dados/bcb/ifdata_resumo.parquet').as_posix()}') group by 1,2),
cad as (select CodInst, arg_max(NomeInstituicao, Data) nome from read_parquet('{(R/'dados/bcb/ifdata_cadastro.parquet').as_posix()}') group by 1),
t as (select v.*, cad.nome, lag(cap,4) over (partition by CodInst order by AnoMes) cap_ant from v join cad using (CodInst))
select AnoMes, nome, (cap >= 5e9 and cap/nullif(cap_ant,0) - 1 >= 0.5 and ativo/nullif(pl,0) >= 10 and nome not like '% IP%' and cap_ant > 0) sinal from t order by nome, AnoMes""").fetchall()
def corrida_max(nome):
    run = best = 0
    for am, n, s in sinais:
        if n.startswith(nome): run = run + 1 if s else 0; best = max(best, run)
    return best
casos = [("BANCO MASTER - PRUD", 4, "banco com crescimento acelerado e alavancado, sustentado por 4+ trimestres")]
ok = True
for nome, minimo, desc in casos:
    r = corrida_max(nome); passou = r >= minimo; ok &= passou
    print(("PASSOU" if passou else "FALHOU"), "|", nome, "|", desc, f"| trimestres seguidos: {r} (mínimo {minimo})")
sys.exit(0 if ok else 1)
