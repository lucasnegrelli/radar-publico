"""R12: servidor público federal que consta como sócio ou administrador de empresa que vende ao governo.
Cruza o cadastro de servidores (SIAPE, Portal da Transparência) com os sócios da Receita por NOME COMPLETO + 6 DÍGITOS CENTRAIS DO CPF (ambos publicados mascarados),
e depois olha os contratos federais da empresa no PNCP. Lei 8.112 (art. 117, X) veda ao servidor a gerência ou administração de sociedade privada; ser apenas sócio cotista é permitido.
Só empresas (natureza jurídica 2xxx): fundações de apoio, associações, cooperativas e OS ficam de fora, porque professor na diretoria de fundação de apoio é previsto em lei (Lei 8.958).
Roda DENTRO do exportar_web.py (usa a conexão `con` com a tabela pncp já filtrada) ou sozinho (abre o banco).
Privacidade: o servidor sai com NOME ABREVIADO, cargo e órgão, e o link da página dele no Portal (onde o nome é público). Saída: data-publica/alertas_extra_r12.json"""
import json, os, re, zipfile, datetime, pathlib, unicodedata, urllib.request, urllib.error, duckdb

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
D = RAIZ / "dados" / "siape"; D.mkdir(parents=True, exist_ok=True)
# --- baixa o mês mais recente disponível (direto do repositório de dados abertos da CGU) ---
mes = None
hoje = datetime.date.today().replace(day=1)
for k in range(0, 8):
    m = hoje
    for _ in range(k): m = (m - datetime.timedelta(days=1)).replace(day=1)
    ym = m.strftime("%Y%m")
    if (D / f"{ym}_Cadastro.csv").exists(): mes = ym; break
    try:
        z = D / f"{ym}.zip"
        urllib.request.urlretrieve(f"https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/servidores/{ym}_Servidores_SIAPE.zip", z)
        zipfile.ZipFile(z).extractall(D); z.unlink(); mes = ym; break
    except Exception:
        continue
if not mes:
    print("cadastro de servidores indisponível agora: mantém o R12 da última rodada"); raise SystemExit(0)
print("servidores:", mes, flush=True)

c = globals().get("con") or duckdb.connect("dados/radar.duckdb", read_only=True)
c.execute("drop table if exists serv")
c.execute(f"""create temp table serv as select Id_SERVIDOR_PORTAL id, strip_accents(upper(trim(NOME))) nome, NOME nome_orig, regexp_replace(CPF, '[^0-9]', '', 'g') c6, DESCRICAO_CARGO cargo, ORG_EXERCICIO orgao, ORGSUP_EXERCICIO orgsup, SITUACAO_VINCULO sit, UF_EXERCICIO uf
   from read_csv('{(D / (mes + "_Cadastro.csv")).as_posix()}', delim=';', header=true, all_varchar=true, encoding='latin-1', sample_size=-1, ignore_errors=true)
   where length(regexp_replace(CPF, '[^0-9]', '', 'g')) = 6 and SITUACAO_VINCULO ilike 'ATIVO%'""")
print(c.execute("select count(*) from serv").fetchone()[0], "servidores ativos com CPF parcial", flush=True)
c.execute("drop table if exists soc12")
c.execute("""create temp table soc12 as select s.id sid, s.nome_orig, s.cargo, s.orgao, s.orgsup, s.uf suf, x.cnpj_basico, x.qualificacao, x.data_entrada
   from serv s join read_parquet('dados/cnpj/socios_[0-9]*.parquet') x on strip_accents(upper(trim(x.nome_socio))) = s.nome and substr(x.doc_socio, 4, 6) = s.c6
   where x.tipo_socio = '2' and x.doc_socio like '***%'""")
print(c.execute("select count(*), count(distinct cnpj_basico) from soc12").fetchone(), "servidores-sócios / empresas", flush=True)
rows = c.execute("""select s.*, p.doc14, p.fornecedor, p.orgao orgao_c, p.esfera, p.valor_global v, p.data_assinatura d, p.id cid, p.modalidade
   from soc12 s join pncp p on left(p.doc14, 8) = s.cnpj_basico
   where p.esfera = 'F' and p.valor_global >= 50000 and not p.erro_valor and not p.estatal and not p.tipo_especial and p.natureza like '2%' and p.data_assinatura >= date '2025-01-01'""").fetchall()
desc = [d[0] for d in c.description]; ix = {k: i for i, k in enumerate(desc)}
print(len(rows), "contratos federais de empresas de servidores", flush=True)

ADMIN = {"05", "10", "16", "28", "49"}   # administrador, diretor, presidente, sócio-gerente, sócio-administrador
QUAL = {"05": "Administrador", "10": "Diretor", "16": "Presidente", "22": "Sócio", "28": "Sócio-gerente", "49": "Sócio-administrador", "08": "Conselheiro", "65": "Titular"}
def abrevia(nm):
    pp = [x for x in re.split(r"\s+", (nm or "").strip()) if x]
    return " ".join([pp[0].title()] + [x[0] + "." for x in pp[1:] if len(x) > 2]) if pp else "–"
fmt_cnpj = lambda d: f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"
brl = lambda v: "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
emp = {}
for r in rows: emp.setdefault(r[ix["cnpj_basico"]], []).append(r)
alertas = []
for cb, g in emp.items():
    contratos = {}
    for r in g: contratos[r[ix["cid"]]] = r
    cs = sorted(contratos.values(), key=lambda r: -r[ix["v"]])
    total = sum(r[ix["v"]] for r in cs)
    servs = {}
    for r in g: servs.setdefault(r[ix["sid"]], r)
    admins = [r for r in servs.values() if r[ix["qualificacao"]] in ADMIN]
    if total < 100000: continue
    if not admins and total < 500000: continue
    grav = "alta" if admins else "media"
    r0 = cs[0]
    tab = [[{"t": abrevia(r[ix["nome_orig"]]), "s": QUAL.get(r[ix["qualificacao"]], "Sócio"), "u": f"https://portaldatransparencia.gov.br/servidores/{r[ix['sid']]}", "v": False},
            {"t": (r[ix["cargo"]] or "").title()[:44], "s": (r[ix["orgao"]] or "")[:46], "u": None, "v": False},
            {"t": "Administra" if r[ix["qualificacao"]] in ADMIN else "Cotista", "s": None, "u": None, "v": False},
            {"t": str(r[ix["data_entrada"]] or ""), "s": None, "u": None, "v": False},
            {"t": "ver no Portal", "s": None, "u": f"https://portaldatransparencia.gov.br/servidores/{r[ix['sid']]}", "v": False}] for r in list(servs.values())[:10]]
    alertas.append({"id": f"R12-{cb}", "regra": "R12", "gravidade": grav, "empresa": r0[ix["fornecedor"]] or "", "cnpj": fmt_cnpj(r0[ix["doc14"]]), "total": total, "n": len(cs),
        "inicio": str(min(r[ix["d"]] for r in cs)), "fim": str(max(r[ix["d"]] for r in cs)), "origem": {"lat": -15.7997, "lon": -47.8645, "nome": "Brasília"}, "local": None,
        "orgao": r0[ix["orgao_c"]], "orgao_uf": None, "orgao_municipio": None,
        "manchete": {"tipo": "R12", "n_servidores": len(servs), "administradores": len(admins), "orgaos_servidor": sorted({r[ix["orgsup"]] for r in servs.values() if r[ix["orgsup"]]})[:3],
                     "orgaos_contrato": sorted({r[ix["orgao_c"]] for r in cs})[:3], "mes_cadastro": mes},
        "tabela": {"titulo": "Servidores federais na empresa (nome abreviado)", "cols": ["Servidor", "Cargo e órgão", "Papel", "Desde", ""], "linhas": tab}})
alertas.sort(key=lambda a: ({"alta": 0, "media": 1}[a["gravidade"]], -a["total"]))
alertas = alertas[:150]
(RAIZ / "data-publica" / "alertas_extra_r12.json").write_text(json.dumps(alertas, ensure_ascii=False, default=str), encoding="utf-8")
print(len(alertas), "alertas R12;", sum(1 for a in alertas if a["gravidade"] == "alta"), "altos; total R$", round(sum(a["total"] for a in alertas) / 1e6, 1), "mi")
