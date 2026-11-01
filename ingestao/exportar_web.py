"""Gera web/public/data/alertas.json a partir do DuckDB.
Uso: python exportar_web.py            (local, com nomes)
     python exportar_web.py --publico  (anonimiza pessoas e empresas: versão que vai ao ar)"""
import sys, json, hashlib, pathlib, duckdb
PUBLICO = "--publico" in sys.argv
RAIZ = pathlib.Path(__file__).parent.parent
con = duckdb.connect(str(RAIZ / "dados" / "radar.duckdb"), read_only=False)

con.execute(f"""create or replace table estab_loc as
select cnpj, uf, municipio from read_parquet('{(RAIZ/'dados'/'cnpj'/'estabelecimentos_*.parquet').as_posix()}')
where cnpj in (select lpad(regexp_replace(CASE WHEN fornecedor IS NULL THEN '' ELSE '' END,'x','','g'),14,'0') where false)""") if False else None

# CNPJs dos fornecedores do alerta 01 (precisa recriar a tabela com doc)
sql = (RAIZ / "alertas" / "01_sancionada_recebendo_cota.sql").read_text(encoding="utf-8").rstrip().rstrip(";")
con.execute("create or replace table alerta01 as " + sql)
docs = con.execute("""select distinct fornecedor from alerta01""").fetchall()

# doc do fornecedor: reconstrói a partir de CEAP/Senado (nome -> cnpj)
con.execute("""create or replace table forn_doc as
select txtFornecedor nome, lpad(regexp_replace(txtCNPJCPF,'\D','','g'),14,'0') doc from camara_ceap
union select FORNECEDOR, lpad(regexp_replace(CNPJ_CPF,'\D','','g'),14,'0') from senado_ceaps""")
con.execute(f"""create or replace table loc as
select f.nome, any_value(m.lat) lat, any_value(m.lon) lon, any_value(m.nome) cidade, any_value(e.uf) uf
from forn_doc f
join read_parquet('{(RAIZ/'dados'/'cnpj'/'estabelecimentos_*.parquet').as_posix()}') e on e.cnpj=f.doc
join mun_coord m on m.rfb=e.municipio and m.uf=e.uf
where f.nome in (select fornecedor from alerta01)
group by f.nome""")

linhas = con.execute("""
select a.casa, a.parlamentar, a.partido, a.uf, a.fornecedor, a.lista, a.categoria, a.alcance,
       min(a.emissao) ini, max(a.emissao) fim, count(*) n, round(sum(a.valor),2) total,
       l.lat, l.lon, l.cidade, l.uf as uf_forn
from alerta01 a left join loc l on l.nome=a.fornecedor
group by all order by total desc""").fetchall()

def anon(txt, pref): return pref + hashlib.sha1(txt.encode()).hexdigest()[:4].upper()
grav = lambda alc: "alta" if alc.startswith("AMPLO") else ("baixa" if alc.startswith("RESTRITO") else "media")
saida = []
for i, r in enumerate(linhas):
    casa, parl, part, uf, forn, lista, cat, alc, ini, fim, n, tot, lat, lon, cid, uff = r
    g = grav(alc)
    if g != "alta" and not lat: continue
    quem = anon(parl, "Parlamentar #") if PUBLICO else f"{parl} ({part or ''}{'/' if part and uf else ''}{uf or ''})".replace("()", "")
    emp = anon(forn, "Empresa #") if PUBLICO else forn
    saida.append({
      "id": f"R01-{i:03d}", "regra": "R01", "gravidade": g, "titulo": "Empresa punida recebeu dinheiro de cota parlamentar",
      "explicacao": f"{emp} recebeu R$ {tot:,.0f} da cota de {quem} ({n} pagamento(s) entre {ini} e {fim}) quando constava na lista de empresas punidas ({lista}: {cat}). Alcance da punição: {alc}. Pode haver explicação legal; vale conferir na fonte.".replace(",", "."),
      "casa": casa, "valor": tot, "inicio": str(ini), "fim": str(fim), "fonte": "Portal da Transparência (CEIS/CNEP) + dados abertos da " + casa,
      "origem": {"lat": -15.7997, "lon": -47.8645, "nome": "Brasília"},
      "destino": {"lat": lat, "lon": lon, "nome": cid, "uf": uff} if lat else None,
    })
out = RAIZ / "web" / "public" / "data"; out.mkdir(parents=True, exist_ok=True)
(out / "alertas.json").write_text(json.dumps({"gerado": str(__import__("datetime").date.today()), "publico": PUBLICO, "alertas": saida}, ensure_ascii=False), encoding="utf-8")
print(len(saida), "alertas;", sum(1 for s in saida if s["destino"]), "com localização;", "modo", "PUBLICO" if PUBLICO else "LOCAL")
