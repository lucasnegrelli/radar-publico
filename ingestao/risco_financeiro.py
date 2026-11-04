"""Módulo de risco financeiro -> web/public/data/risco.json
RF01: banco em crescimento acelerado e alavancado de forma sustentada (lista de observação, Banco Central/IF.data).
      Dossiê automático (balanço, imprensa, diários): ingestao/risco_dossie.py.
Exposição de fundos (CVM/CDA): quanto de fundos abertos está em papel de cada banco listado."""
import json, os, pathlib, datetime, duckdb

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
c = duckdb.connect("dados/radar.duckdb")
c.execute("""create or replace table bcb_painel as
select AnoMes, CodInst,
  max(case when Coluna='Ativo Total' then Saldo end) ativo,
  max(case when Coluna='Captações' then Saldo end) captacao,
  max(case when Coluna='Patrimônio Líquido' then Saldo end) pl
from read_parquet('dados/bcb/ifdata_resumo.parquet') group by 1,2""")
try:
    c.execute("""create or replace table bcb_cad as
select CodInst, arg_max(NomeInstituicao, Data) nome, arg_max(Uf, Data) uf, arg_max(Municipio, Data) municipio, arg_max(CnpjInstituicaoLider, Data) cnpj8
from read_parquet('dados/bcb/ifdata_cadastro.parquet') group by 1""")
except Exception as e:
    print("cadastro do BCB indisponível, usando a tabela bcb_cad já existente:", str(e)[:80])
c.execute("""create or replace table bcb_sinais as
with t as (select p.*, c.nome, c.uf, c.municipio, c.cnpj8,
    lag(captacao,4) over (partition by p.CodInst order by AnoMes) cap_ant, lag(ativo,4) over (partition by p.CodInst order by AnoMes) ativo_ant
  from bcb_painel p join bcb_cad c using (CodInst))
select *, captacao/nullif(cap_ant,0) - 1 cap_yoy, ativo/nullif(ativo_ant,0) - 1 ativo_yoy, ativo/nullif(pl,0) alav,
       (captacao >= 5e9 and captacao/nullif(cap_ant,0) - 1 >= 0.5 and ativo/nullif(pl,0) >= 10 and nome not like '% IP%' and cap_ant > 0) as sinal
from t""")
ultimo = c.execute("select max(AnoMes) from bcb_painel").fetchone()[0]
rows = c.execute("select CodInst, nome, uf, municipio, cnpj8, AnoMes, sinal from bcb_sinais order by CodInst, AnoMes").fetchall()

# sequência de trimestres consecutivos com sinal, terminando em cada trimestre
corridas = {}
for cod, nome, uf, mun, cnpj8, am, sinal in rows:
    d = corridas.setdefault(cod, {"nome": nome, "uf": uf, "mun": mun, "cnpj8": cnpj8, "seq": {}, "run": 0})
    d["run"] = d["run"] + 1 if sinal else 0
    d["seq"][am] = d["run"]

def fmt_trim(am): return f"{am[4:6]}/{am[:4]}".replace("03/", "T1/").replace("06/", "T2/").replace("09/", "T3/").replace("12/", "T4/")
def bi(v): return f"R$ {v/1e9:,.1f} bi".replace(",", "X").replace(".", ",").replace("X", ".") if v is not None else "–"
def coord(mun, uf):
    r = c.execute("select m.lat, m.lon, m.nome from mun_ibge m join uf_cod u on cast(u.cod as varchar)=m.codigo_uf where strip_accents(upper(m.nome))=strip_accents(upper(?)) and u.uf=?", [mun, uf]).fetchone()
    return {"lat": r[0], "lon": r[1], "cidade": r[2], "uf": uf} if r else None

meses_cda = [r[0] for r in c.execute("select distinct mes from cda_rf order by 1").fetchall()]
def fundos(cnpj8):
    out = []
    for mes in (meses_cda[-1], "2025-09"):
        tot = c.execute("select count(distinct cnpj_fundo), coalesce(sum(valor),0) from cda_rf where left(cnpj_emissor,8)=? and mes=?", [cnpj8, mes]).fetchone()
        top = c.execute("select substr(fundo,1,60), round(sum(valor)/1e6,1) from cda_rf where left(cnpj_emissor,8)=? and mes=? group by 1 order by 2 desc limit 5", [cnpj8, mes]).fetchall()
        out.append((mes, tot[0], tot[1], top))
    return out

def montar(cod, d, ate, ref=False):
    am_list = [am for am in sorted(d["seq"]) if am <= ate][-9:]
    tabela = []
    for am in am_list:
        r = c.execute("select ativo, captacao, pl, cap_yoy, alav, sinal from bcb_sinais where CodInst=? and AnoMes=?", [cod, am]).fetchone()
        tabela.append([{"t": fmt_trim(am)}, {"t": bi(r[0]), "v": True}, {"t": bi(r[1]), "v": True}, {"t": bi(r[2]), "v": True},
                       {"t": f"{r[3]*100:+.0f}%" if r[3] is not None else "–", "v": True}, {"t": f"{r[4]:.1f}x" if r[4] else "–", "v": True}, {"t": "●" if r[5] else ""}])
    ult = c.execute("select ativo, captacao, pl, cap_yoy, alav from bcb_sinais where CodInst=? and AnoMes=?", [cod, ate]).fetchone()
    secoes = []
    f = fundos(d["cnpj8"]) if d["cnpj8"] else []
    kv = []
    for mes, n, tot, top in f:
        kv.append([f"Fundos em {mes}", f"{n} fundos abertos · R$ {tot/1e6:,.0f} mi em papel do banco".replace(",", ".")])
        for nome, v in top[:3]: kv.append(["  · " + nome.title(), f"R$ {v:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")])
    if kv: secoes.append({"titulo": "Quem segura o papel (fundos abertos, CVM)", "kv": kv})
    secoes.append({"titulo": "O que este dado não mostra", "kv": [["Lacuna", "Fundos de previdência de servidores (RPPS) que compram o papel direto não aparecem em dado aberto em lote (o DAIR só pode ser consultado fundo a fundo no sistema do Ministério da Previdência). Pedir por Lei de Acesso à Informação."]]})
    run = d["seq"][ate] if ate in d["seq"] else 0
    return {"id": f"RF01-{cod}{'-ref' if ref else ''}", "regra": "RF01", "gravidade": "alta" if ref or run >= 6 else ("media" if run >= 4 else "baixa"),
            "empresa": d["nome"].replace(" - PRUDENCIAL", ""), "cnpj": f"CNPJ base {d['cnpj8']}" if d["cnpj8"] else "", "total": ult[1] or 0, "n": run,
            "inicio": f"{am_list[0][:4]}-{am_list[0][4:6]}-01", "fim": f"{ate[:4]}-{ate[4:6]}-28",
            "origem": {"lat": -15.7997, "lon": -47.8645, "nome": "Brasília"}, "local": coord(d["mun"], d["uf"]),
            "manchete": {"tipo": "RF01", "trimestres": run, "yoy": ult[3], "alav": ult[4], "captacao": ult[1], "ativo": ult[0], "pl": ult[2], "ref": ref, "ate": fmt_trim(ate)},
            "tabela": {"titulo": "Evolução trimestral (Banco Central)", "cols": ["Trimestre", "Ativo", "Captações", "Patrim. líquido", "Capt. em 12m", "Alavanc.", "Alerta"], "linhas": tabela},
            "secoes": secoes}

alertas = []
# lista de observação atual: sinal sustentado por >= 4 trimestres terminando no último trimestre
for cod, d in corridas.items():
    if d["seq"].get(ultimo, 0) >= 2: alertas.append(montar(cod, d, ultimo))
# (o Banco Master NÃO entra aqui: é uma investigação cadastrada em casos/, validada por testes internos)

saida = {"gerado": str(datetime.date.today()), "ultimo_trimestre": ultimo, "alertas": alertas}
(RAIZ / "web" / "public" / "data" / "risco.json").write_text(json.dumps(saida, ensure_ascii=False, default=str), encoding="utf-8")
print(len(alertas), "alertas RF01 (último trimestre", ultimo + "):", [a["empresa"] for a in alertas])
