"""Emendas parlamentares (Portal da Transparência) -> cruza autor da emenda x empresa favorecida.
R09: empresa/entidade privada que recebeu dinheiro de emenda e tem ponto de atenção (sancionada na data, aberta há menos de 1 ano, capital pequeno demais para o valor).
Saídas: data-publica/alertas_extra.json (alertas R09 no mesmo formato do painel) e data-publica/emendas_autor.json (resumo por parlamentar, usado nas fichas de pessoa).
Fonte: https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares (dados abertos, sem chave)."""
import json, os, re, glob, pathlib, datetime, unicodedata, urllib.request, zipfile, duckdb

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
D = RAIZ / "dados" / "emendas"
D.mkdir(parents=True, exist_ok=True)
ZIP = D / "emendas.zip"
if not ZIP.exists() or (datetime.datetime.now().timestamp() - ZIP.stat().st_mtime) > 5 * 86400:
    print("baixando emendas...", flush=True)
    urllib.request.urlretrieve("https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/emendas-parlamentares/EmendasParlamentares.zip", ZIP)
    zipfile.ZipFile(ZIP).extractall(D)

c = duckdb.connect()
norm = lambda s: "".join(ch for ch in unicodedata.normalize("NFD", (s or "").upper()) if unicodedata.category(ch) != "Mn")
num = lambda col: f"try_cast(replace(replace({col}, '.', ''), ',', '.') as double)"
def csv(nome):
    return f"read_csv('{(D / nome).as_posix()}', delim=';', header=true, all_varchar=true, encoding='latin-1', sample_size=-1)"
# colunas por posição: o nome vem com acento e o duckdb lê como latin-1, então renomeia pela ordem
fav_cols = ["emenda", "cod_autor", "autor", "num", "tipo_emenda", "ano_mes", "doc", "favorecido", "natureza", "tipo_fav", "uf", "municipio", "valor"]
c.execute(f"create table fav as select * from (select {', '.join(f'column{i:02d} as {n}' for i, n in enumerate(fav_cols))} from read_csv('{(D / 'EmendasParlamentares_PorFavorecido.csv').as_posix()}', delim=';', header=false, skip=1, all_varchar=true, encoding='latin-1', columns={{{', '.join(f'column{i:02d}: VARCHAR' for i in range(13))}}}))")
c.execute(f"update fav set valor = {num('valor')}::varchar")
c.execute("alter table fav alter valor type double using try_cast(valor as double)")
print(c.execute("select count(*), sum(valor)/1e9 from fav").fetchall(), flush=True)

# --- apoio: sancionadas, empresas e estabelecimentos
c.execute("create view ceis as select * from read_parquet('dados/tse/ceis.parquet')")
c.execute("create view cnep as select * from read_parquet('dados/tse/cnep.parquet')")
c.execute("create view emp as select cnpj_basico, razao_social, capital_social, porte from read_parquet('dados/cnpj/empresas_*.parquet')")
c.execute("create view estab as select cnpj, cnpj_basico, try_strptime(data_inicio,'%Y%m%d')::date abertura, uf, municipio from read_parquet('dados/cnpj/estabelecimentos_*.parquet')")
c.execute("""create table sanc as
  select 'CEIS' lista, lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\\D','','g'),14,'0') doc, "CATEGORIA DA SANÇÃO" categoria, "ÓRGÃO SANCIONADOR" orgao, "ABRAGÊNCIA DA SANÇÃO" abr, "ESFERA ÓRGÃO SANCIONADOR" esf,
     try_strptime("DATA INÍCIO SANÇÃO",'%d/%m/%Y')::date ini, try_strptime("DATA FINAL SANÇÃO",'%d/%m/%Y')::date fim from ceis
  union all select 'CNEP', lpad(regexp_replace("CPF OU CNPJ DO SANCIONADO",'\\D','','g'),14,'0'), "CATEGORIA DA SANÇÃO", "ÓRGÃO SANCIONADOR", "ABRAGÊNCIA DA SANÇÃO", "ESFERA ÓRGÃO SANCIONADOR",
     try_strptime("DATA INÍCIO SANÇÃO",'%d/%m/%Y')::date, try_strptime("DATA FINAL SANÇÃO",'%d/%m/%Y')::date from cnep""")

# --- pagamentos a entidades privadas (pessoa jurídica que não é órgão público)
c.execute("""create table pag as
  select emenda, autor, tipo_emenda, ano_mes, make_date(try_cast(left(ano_mes,4) as int), greatest(1, least(12, try_cast(right(ano_mes,2) as int))), 1) data,
         lpad(regexp_replace(doc,'\\D','','g'),14,'0') doc, favorecido, natureza, uf, municipio, valor
  from fav where tipo_fav ILIKE 'Pessoa Jur%' and length(regexp_replace(doc,'\\D','','g')) = 14 and valor > 0
   and natureza not ILIKE '%Município%' and natureza not ILIKE '%Estado%' and natureza not ILIKE '%Órgão%' and natureza not ILIKE '%Orgao%' and natureza not ILIKE '%Autarquia%'
   and natureza not ILIKE '%Distrito Federal%' and natureza not ILIKE '%União%' and natureza not ILIKE '%Fundo Público%' and natureza not ILIKE '%Consórcio Público%' and natureza not ILIKE '%Empresa Pública%' and natureza not ILIKE '%Economia Mista%'""")
c.execute("""create table agg as
  select p.doc, any_value(p.favorecido) nome, any_value(p.natureza) natureza, sum(p.valor) total, count(*) n, min(p.data) ini, max(p.data) fim, count(distinct p.autor) n_autores,
         e.abertura, em.capital_social, em.porte
  from pag p left join (select cnpj_basico, min(abertura) abertura from estab where cnpj_basico in (select distinct left(doc, 8) from pag) group by 1) e on e.cnpj_basico = left(p.doc, 8)
  left join emp em on em.cnpj_basico = left(p.doc, 8) where p.favorecido not ILIKE '%CONSORCIO%' and p.favorecido not ILIKE '%CONSÓRCIO%'
  group by p.doc, e.abertura, em.capital_social, em.porte having sum(p.valor) >= 100000""")
c.execute("""create table flags as
  select a.*, (select list(s.lista || '|' || coalesce(s.categoria,'') || '|' || coalesce(s.abr,'') || '|' || coalesce(s.orgao,'') || '|' || coalesce(s.esf,'')) from sanc s
                where s.doc = a.doc and s.ini <= a.fim and (s.fim is null or s.fim >= a.ini)) sancoes,
         (a.abertura is not null and a.abertura > a.ini - interval 365 day and a.total >= 200000) nova,
         (a.capital_social is not null and a.total >= 500000 and a.capital_social > 0 and a.total > 50 * a.capital_social) capital_pequeno
  from agg a""")
rows = c.execute("""select doc, nome, natureza, total, n, ini, fim, n_autores, abertura, capital_social, porte, sancoes, nova, capital_pequeno from flags
   where sancoes is not null or nova or capital_pequeno order by total desc""").fetchall()
print(len(rows), "empresas com emenda e ponto de atenção", flush=True)

# --- monta alertas
def fmt_cnpj(d): return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"
brl = lambda v: "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
uf_cod = None
try:
    db = duckdb.connect("dados/radar.duckdb", read_only=True)
    uf_cod = dict(db.execute("select uf, cast(cod as varchar) from uf_cod").fetchall())
except Exception:
    db = None
def local(doc):
    if not db: return None
    r = db.execute(f"select m.lat, m.lon, m.nome, e.uf from read_parquet('{(RAIZ/'dados/cnpj/estabelecimentos_*.parquet').as_posix()}') e join mun_coord m on m.rfb=e.municipio and m.uf=e.uf where e.cnpj=? limit 1", [doc]).fetchone()
    return {"lat": r[0], "lon": r[1], "cidade": r[2], "uf": r[3]} if r else None
BRASILIA = {"lat": -15.7997, "lon": -47.8645, "nome": "Brasília"}
alertas = []
for doc, nome, nat, total, n, ini, fim, n_aut, ab, cap, porte, sancoes, nova, cap_peq in rows[:200]:
    sc = [s.split("|") for s in (sancoes or [])]
    forte = any(s[2].startswith(("Todas as Esferas", "Em todos os Poderes")) and "Federal" in s[4] or s[2].startswith("Todas as Esferas") for s in sc)
    flags = int(bool(sc)) + int(bool(nova)) + int(bool(cap_peq))
    grav = "alta" if forte or (nova and total >= 1e6) or flags >= 2 else ("media" if total >= 500000 else "baixa")
    linhas = [[{"t": str(r[0])[:7], "s": None, "u": None, "v": False}, {"t": r[1].title()[:48], "s": r[2], "u": None, "v": False}, {"t": r[3].title()[:44], "s": f"{(r[4] or '').title()}/{r[5]}", "u": None, "v": False},
               {"t": brl(r[6]), "s": None, "u": None, "v": True}, {"t": "–", "s": None, "u": None, "v": False}]
              for r in c.execute("select data, autor, favorecido, municipio, uf, valor, valor from pag where doc = ? order by data", [doc]).fetchall()]
    linhas = [[x[0], {"t": a_["autor"].title()[:56], "s": a_["tipo"], "u": None, "v": False}, x[2], x[3], x[4]] for x, a_ in zip(linhas, [{"autor": r[0], "tipo": r[1]} for r in c.execute("select autor, tipo_emenda from pag where doc = ? order by data", [doc]).fetchall()])][:14]
    top = c.execute("select autor, sum(valor) v from pag where doc = ? group by 1 order by 2 desc limit 3", [doc]).fetchall()
    a = {"id": f"R09-{doc}", "regra": "R09", "gravidade": grav, "empresa": (nome or "").upper(), "cnpj": fmt_cnpj(doc), "total": total, "n": n, "inicio": str(ini), "fim": str(fim),
         "origem": BRASILIA, "local": local(doc), "orgao": "Emenda parlamentar (União)", "orgao_uf": None, "orgao_municipio": None,
         "manchete": {"tipo": "R09", "autores": [{"nome": t[0].title(), "valor": t[1]} for t in top], "n_autores": n_aut, "natureza": nat, "nova": bool(nova), "abertura": str(ab) if ab else None,
                      "capital": cap, "capital_peq": bool(cap_peq), "sancao": bool(sc), "porte": porte},
         "tabela": {"titulo": "Emendas pagas à entidade", "cols": ["Mês", "Autor da emenda", "Local", "Valor", ""], "linhas": linhas}}
    if sc:
        s0 = sc[0]
        a["sancao"] = {"lista": s0[0], "tipo": s0[1], "orgao": s0[3], "alcance": s0[2], "inicio": None, "fim": None}
    alertas.append(a)
out = RAIZ / "data-publica"; out.mkdir(exist_ok=True)
(out / "alertas_extra.json").write_text(json.dumps(alertas, ensure_ascii=False, default=str), encoding="utf-8")

# --- resumo por autor (parlamentar) para as fichas de pessoa
por_autor = {}
for autor, ano, tot in c.execute("select autor, left(ano_mes,4), sum(valor) from fav group by 1,2").fetchall():
    por_autor.setdefault(norm(autor), {"nome": autor, "anos": {}, "top": [], "alertas": []})["anos"][ano] = round(tot or 0)
for autor, nome, doc, tot in c.execute("select autor, favorecido, lpad(regexp_replace(doc,'\\D','','g'),14,'0'), sum(valor) from fav where valor > 0 group by 1,2,3 qualify row_number() over (partition by autor order by sum(valor) desc) <= 6").fetchall():
    por_autor[norm(autor)]["top"].append([nome.title(), doc if len(doc) == 14 else None, round(tot or 0)])
ids_al = {a["id"][4:]: a["id"] for a in alertas}
for autor, doc in c.execute("select distinct autor, doc from pag").fetchall():
    if doc in ids_al: por_autor[norm(autor)]["alertas"].append(ids_al[doc])
(out / "emendas_autor.json").write_text(json.dumps(por_autor, ensure_ascii=False), encoding="utf-8")
print(len(alertas), "alertas R09;", len(por_autor), "autores de emenda")
