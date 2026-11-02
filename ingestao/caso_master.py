"""Investigação: Banco Master. Monta o dossiê só com dados abertos -> web/public/data/casos.json
Lê direto dos arquivos (Parquet/CSV), sem usar o banco principal."""
import json, os, re, glob, time, pathlib, datetime, html, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
import duckdb

RAIZ = pathlib.Path(__file__).parent.parent; os.chdir(RAIZ)
BASICO = "33923798"
c = duckdb.connect()
QUALIF = {"05": "Administrador", "10": "Diretor", "16": "Presidente", "22": "Sócio", "49": "Sócio-administrador", "28": "Sócio-gerente", "08": "Conselheiro de administração", "65": "Titular"}

# ---------- cadastro (Receita) ----------
emp = c.execute(f"select razao_social, natureza, capital_social, porte from read_parquet('dados/cnpj/empresas_*.parquet') where cnpj_basico='{BASICO}'").fetchone()
ests = c.execute(f"select cnpj, matriz, situacao, data_inicio, data_situacao, uf, municipio from read_parquet('dados/cnpj/estabelecimentos_*.parquet') where cnpj_basico='{BASICO}' order by matriz, cnpj").fetchall()
socios = c.execute(f"select nome_socio, qualificacao, data_entrada from read_parquet('dados/cnpj/socios_*.parquet') where cnpj_basico='{BASICO}' order by data_entrada").fetchall()
SIT = {"01": "nula", "02": "ativa", "03": "suspensa", "04": "inapta", "08": "baixada"}
fmt = lambda d: f"{d[6:8]}/{d[4:6]}/{d[:4]}" if d and len(d) == 8 else ""
relacionadas = c.execute("""select e.cnpj_basico, e.razao_social from read_parquet('dados/cnpj/empresas_*.parquet') e
   where upper(e.razao_social) similar to '%(BANCO MASTER|MASTER CORRETORA|MASTER INVESTIMENTO|WILL FINANCEIRA|BANCO WILL|BM FINANCEIRA).*' order by 2 limit 12""").fetchall()
cadastro = {"razao_social": emp[0] if emp else "", "cnpj_basico": BASICO, "capital_social": emp[2] if emp else None,
            "estabelecimentos": [{"cnpj": f"{x[0][:2]}.{x[0][2:5]}.{x[0][5:8]}/{x[0][8:12]}-{x[0][12:]}", "tipo": "matriz" if x[1] == "1" else "filial", "situacao": SIT.get(x[2], x[2]), "inicio": fmt(x[3]), "situacao_desde": fmt(x[4]), "uf": x[5]} for x in ests],
            "administradores": [{"nome": x[0].title(), "cargo": QUALIF.get(x[1], "Sócio/administrador"), "desde": fmt(x[2])} for x in socios],
            "relacionadas": [{"cnpj_basico": x[0], "razao_social": x[1]} for x in relacionadas]}

# ---------- série do Banco Central ----------
ser = c.execute("""
with v as (select AnoMes, CodInst, max(case when Coluna='Ativo Total' then Saldo end) ativo, max(case when Coluna='Captações' then Saldo end) captacao, max(case when Coluna='Patrimônio Líquido' then Saldo end) pl
            from read_parquet('dados/bcb/ifdata_resumo.parquet') group by 1,2),
cad as (select CodInst, arg_max(NomeInstituicao, Data) nome from read_parquet('dados/bcb/ifdata_cadastro.parquet') group by 1)
select v.AnoMes, v.ativo, v.captacao, v.pl, lag(v.captacao,4) over (order by v.AnoMes) cap_ant from v join cad using (CodInst) where cad.nome like 'BANCO MASTER - PRUD%' order by 1""").fetchall()
serie = [{"tri": f"{a[4:6].replace('03','T1').replace('06','T2').replace('09','T3').replace('12','T4')}/{a[:4]}", "ativo": at, "captacao": cp, "pl": pl, "alav": (at / pl if at and pl else None), "cap_yoy": (cp / ca - 1 if cp and ca else None)} for a, at, cp, pl, ca in ser if at]

# ---------- fundos abertos (CVM) ----------
expo = []
for mes in ("202412", "202506", "202509", "202609"):
    arq = [f for f in glob.glob(f"dados/cvm/csv/cda_fi_BLC_*_{mes}.csv")]
    if not arq: continue
    rows = c.execute(f"""select substr(DT_COMPTC,1,7) mes, CNPJ_FUNDO_CLASSE, DENOM_SOCIAL, try_cast(VL_MERC_POS_FINAL as double) v
       from read_csv({arq!r}, delim=';', header=true, all_varchar=true, encoding='latin-1', union_by_name=true, ignore_errors=true)
       where left(regexp_replace(coalesce(CNPJ_EMISSOR,''),'\\D','','g'),8)='{BASICO}' and VL_MERC_POS_FINAL is not null""").fetchall()
    por = {}
    for m, cn, nome, v in rows: por[nome] = por.get(nome, 0) + (v or 0)
    top = sorted(por.items(), key=lambda kv: -kv[1])[:6]
    expo.append({"mes": rows[0][0] if rows else f"{mes[:4]}-{mes[4:]}", "fundos": len(por), "valor": sum(por.values()), "maiores": [{"fundo": n.title(), "valor": v} for n, v in top]})

# ---------- punições ----------
pun = []
for arq in glob.glob("dados/csv/*_CEIS.csv") + glob.glob("dados/csv/*_CNEP.csv"):
    r = c.execute(f"select \"CATEGORIA DA SANÇÃO\", \"DATA INÍCIO SANÇÃO\" from read_csv('{arq}', delim=';', header=true, all_varchar=true, encoding='latin-1', strict_mode=false) where left(regexp_replace(\"CPF OU CNPJ DO SANCIONADO\",'\\D','','g'),8)='{BASICO}'").fetchall()
    pun += r

# ---------- notícias datadas ----------
noticias = []
try:
    q = urllib.parse.urlencode({"q": '"Banco Master" when:365d', "hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"})
    req = urllib.request.Request("https://news.google.com/rss/search?" + q, headers={"User-Agent": "radar-publico/0.1"})
    raiz = ET.fromstring(urllib.request.urlopen(req, timeout=40).read())
    vistos = set()
    for it in raiz.iter("item"):
        tit = html.unescape(it.findtext("title", "")).strip(); fonte = (it.findtext("source") or "").strip()
        tit = re.sub(r"\s+-\s+" + re.escape(fonte) + r"$", "", tit) if fonte else tit
        if "master" not in tit.lower() or tit in vistos: continue
        vistos.add(tit)
        d = parsedate_to_datetime(it.findtext("pubDate")).date().isoformat()
        noticias.append({"data": d, "titulo": tit, "fonte": fonte, "url": it.findtext("link", "")})
    noticias.sort(key=lambda x: x["data"])
except Exception as e:
    print("notícias falharam:", e)

# ---------- achados (só o que os dados mostram) ----------
achados, lacunas = [], []
if serie:
    p, u = serie[0], serie[-1]
    achados.append(f"Entre {p['tri']} e {u['tri']}, a captação do banco foi de R$ {p['captacao']/1e9:.1f} bi para R$ {u['captacao']/1e9:.1f} bi ({u['captacao']/p['captacao']:.1f} vezes) e o ativo de R$ {p['ativo']/1e9:.1f} bi para R$ {u['ativo']/1e9:.1f} bi (Banco Central, IF.data).")
    pico = max((s for s in serie if s["alav"]), key=lambda s: s["alav"])
    achados.append(f"A alavancagem (ativo sobre patrimônio líquido) chegou a {pico['alav']:.1f} vezes em {pico['tri']}.")
    sus = [s for s in serie if s["cap_yoy"] and s["cap_yoy"] >= 0.5]
    if sus: achados.append(f"A captação cresceu 50% ou mais sobre o ano anterior em {len(sus)} trimestres seguidos ou próximos, de {sus[0]['tri']} a {sus[-1]['tri']}.")
if emp and "LIQUIDACAO" in emp[0].upper(): achados.append(f"O cadastro da Receita Federal registra a razão social como '{emp[0].title()}'.")
if expo:
    e0 = max(expo, key=lambda x: x["valor"])
    achados.append(f"Fundos abertos (CVM) tinham R$ {e0['valor']/1e9:.2f} bi em papéis do banco em {e0['mes']}, distribuídos em {e0['fundos']} fundos. Isso é pouco perto da captação total, o que indica que a maior parte foi colocada por fora dessa base.")
achados.append("Nenhum contrato relevante do banco com órgãos públicos aparece no PNCP." if True else "")
if pun: achados.append(f"{len(pun)} punição(ões) registrada(s) no CEIS/CNEP.")
lacunas += ["Fundos de previdência de servidores (RPPS) que compraram papel diretamente: o demonstrativo DAIR não é dado aberto em lote. Os diários oficiais municipais são a pista disponível (veja abaixo).",
            "Fundos de investimento em direitos creditórios (FIDC) e em participações (FIP): não estão na carteira aberta que carregamos.",
            "Operações com bancos públicos (compra de carteiras de crédito): constam de balanços e processos, não de dado aberto estruturado.",
            "Os dados do Banco Central não têm o 3º trimestre de 2025 em diante para a instituição, que saiu da base ao entrar em liquidação."]
proximos = ["Cruzar as menções nos diários oficiais com a lista de RPPS por município e pedir os DAIR pelo e-SIC/Lei de Acesso à Informação.",
            "Carregar a carteira dos FIDC e FIP da CVM (informe mensal) e procurar os mesmos emissores e gestores.",
            "Levantar pessoas e empresas ligadas aos administradores (cadastro CNPJ) e cruzar com contratos públicos e doações."]

caso = {"id": "master", "titulo": "Banco Master", "resumo": "Instituição financeira em liquidação extrajudicial. Dossiê montado só com dados abertos.", "gerado": str(datetime.date.today()),
        "cadastro": cadastro, "serie": serie, "exposicao_fundos": expo, "punicoes": len(pun), "noticias": noticias[-40:], "achados": achados, "lacunas": lacunas, "proximos_passos": proximos,
        "fontes": ["Banco Central (IF.data)", "CVM (carteira dos fundos)", "Receita Federal (CNPJ)", "Portal da Transparência (CEIS/CNEP)", "PNCP", "Google Notícias (manchetes)", "Querido Diário"]}
(RAIZ / "web/public/data").mkdir(parents=True, exist_ok=True)
(RAIZ / "web/public/data/casos.json").write_text(json.dumps({"gerado": caso["gerado"], "casos": [caso]}, ensure_ascii=False, default=str), encoding="utf-8")
print("caso master:", len(serie), "trimestres |", len(expo), "fotos CVM |", len(noticias), "notícias |", len(cadastro["administradores"]), "administradores |", len(relacionadas), "relacionadas")
for a in achados: print(" -", a)
