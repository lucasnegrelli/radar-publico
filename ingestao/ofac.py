"""Sanções internacionais ligadas ao Brasil: lista SDN da OFAC (EUA) e lista consolidada da União Europeia.
Saída: dados/ofac_br.json (nome normalizado -> registros, cada um com a lista de origem). O cruzamento com políticos é feito em pessoas.py por NOME COMPLETO e
vem marcado como 'confirmar': listas de sanção podem ter homônimos. Fontes públicas:
  OFAC: https://www.treasury.gov/ofac/downloads/sdn.csv
  UE:   https://webgate.ec.europa.eu/fsd/fsf/public/files/csvFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNw (token público do próprio portal)"""
import csv, io, json, os, re, pathlib, unicodedata, urllib.request, duckdb

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
UA = {"User-Agent": "radar-publico/0.1 (+https://github.com/lucasnegrelli/radar-publico)"}
norm = lambda s: re.sub(r"\s+", " ", "".join(c for c in unicodedata.normalize("NFD", (s or "").upper()) if unicodedata.category(c) != "Mn")).strip()
saida = {}

# ---- OFAC ----
raw = urllib.request.urlopen(urllib.request.Request("https://www.treasury.gov/ofac/downloads/sdn.csv", headers=UA), timeout=120).read().decode("latin-1")
n_of = 0
for r in csv.reader(io.StringIO(raw)):
    if len(r) < 12: continue
    ent, nome, tipo, prog, rem = r[0], r[1].strip(), r[2].strip(), r[3].strip(), r[11]
    if tipo.lower() != "individual" or not re.search(r"Brazil", rem, re.I): continue
    if "," in nome:
        ult, resto = [x.strip() for x in nome.split(",", 1)]; nome_ord = f"{resto} {ult}"
    else: nome_ord = nome
    saida.setdefault(norm(nome_ord), []).append({"lista": "OFAC (EUA)", "ent": ent, "nome": nome_ord.title(), "programa": prog, "obs": " ".join(rem.split())[:220]}); n_of += 1
print(n_of, "registros OFAC ligados ao Brasil", flush=True)

# ---- União Europeia ----
try:
    alvo = RAIZ / "dados" / "extra" / "eu.csv"; alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_bytes(urllib.request.urlopen(urllib.request.Request("https://webgate.ec.europa.eu/fsd/fsf/public/files/csvFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNw", headers=UA), timeout=180).read())
    rows = duckdb.sql(f"""select NameAlias_WholeName, Entity_Regulation_Programme, Entity_Remark, Entity_LogicalId from read_csv('{alvo.as_posix()}', delim=';', header=true, all_varchar=true, sample_size=-1, ignore_errors=true, quote='"')
        where Entity_SubjectType ilike 'person%' and upper(coalesce(Citizenship_CountryDescription,'') || coalesce(BirthDate_CountryDescription,'') || coalesce(Address_CountryDescription,'')) like '%BRAZIL%'
          and NameAlias_WholeName is not null""").fetchall()
    n_eu = 0
    for nome, prog, rem, lid in rows:
        saida.setdefault(norm(nome), []).append({"lista": "União Europeia", "ent": lid, "nome": nome.title(), "programa": prog or "", "obs": " ".join((rem or "").split())[:220]}); n_eu += 1
    print(n_eu, "registros da UE ligados ao Brasil", flush=True)
except Exception as e:
    print("UE indisponível agora:", str(e)[:120])
(RAIZ / "dados" / "ofac_br.json").write_text(json.dumps(saida, ensure_ascii=False), encoding="utf-8")
print(len(saida), "nomes na saída")
