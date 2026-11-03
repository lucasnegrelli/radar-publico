"""Sanções internacionais: lista SDN da OFAC (Tesouro dos EUA), filtrada por ligação com o Brasil (nacionalidade, cidadania, local de nascimento ou endereço).
Saída: dados/ofac_br.json (nome normalizado -> registros). O cruzamento com políticos é feito em pessoas.py por NOME COMPLETO (4+ palavras significativas) e vem marcado
como 'confirmar': listas de sanção podem ter homônimos. Fonte pública: https://www.treasury.gov/ofac/downloads/sdn.csv"""
import csv, io, json, os, re, pathlib, unicodedata, urllib.request

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
raw = urllib.request.urlopen(urllib.request.Request("https://www.treasury.gov/ofac/downloads/sdn.csv", headers={"User-Agent": "radar-publico/0.1 (+https://github.com/lucasnegrelli/radar-publico)"}), timeout=120).read().decode("latin-1")
norm = lambda s: re.sub(r"\s+", " ", "".join(c for c in unicodedata.normalize("NFD", (s or "").upper()) if unicodedata.category(c) != "Mn")).strip()
saida = {}
for r in csv.reader(io.StringIO(raw)):
    if len(r) < 12: continue
    ent, nome, tipo, prog, rem = r[0], r[1].strip(), r[2].strip(), r[3].strip(), r[11]
    if tipo.lower() != "individual" or not re.search(r"Brazil", rem, re.I): continue
    if "," in nome:
        ult, resto = [x.strip() for x in nome.split(",", 1)]; nome_ord = f"{resto} {ult}"
    else:
        nome_ord = nome
    saida.setdefault(norm(nome_ord), []).append({"ent": ent, "nome": nome_ord.title(), "programa": prog, "obs": " ".join(rem.split())[:220]})
(RAIZ / "dados" / "ofac_br.json").write_text(json.dumps(saida, ensure_ascii=False), encoding="utf-8")
print(len(saida), "pessoas na SDN com ligação ao Brasil")
