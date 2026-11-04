"""Dívida ativa da União (PGFN, dados abertos, sem chave) -> web/public/data/pgfn.json
Baixa os arquivos do trimestre mais recente em https://dadosabertos.pgfn.gov.br/ (Previdenciário, FGTS e, com --tudo, o Sistema SIDA/não previdenciário, 1,4 GB)
e soma por RAIZ de CNPJ (8 dígitos: matriz e filiais juntas) o valor consolidado, só de pessoa jurídica. Leitura em fluxo, sem descompactar tudo em disco.
Dívida ativa não é crime nem prova de irregularidade: muita empresa discute a dívida na Justiça ou parcela. O cruzamento serve para perguntar
"por que o governo segue pagando quem deve tanto à União?". Uso: python ingestao/pgfn.py [--tudo]"""
import csv, io, json, os, pathlib, sys, zipfile, datetime, urllib.request

RAIZ = pathlib.Path(__file__).parent.parent; os.chdir(RAIZ)
D = RAIZ / "dados/pgfn"; D.mkdir(parents=True, exist_ok=True)
(RAIZ / "web/public/data").mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "RadarPublico/1.0 (projeto civico; github.com/lucasnegrelli/radar-publico)"}
BASE = "https://dadosabertos.pgfn.gov.br/"
TUDO = "--tudo" in sys.argv
hoje = datetime.date.today()
pastas = []
a, t = hoje.year, (hoje.month - 1) // 3 + 1
for _ in range(6):
    pastas.append(f"{a}_trimestre_{t:02d}/"); t -= 1
    if t == 0: a, t = a - 1, 4


def existe(u):
    try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA, method="HEAD"), timeout=30).status == 200
    except Exception: return False


def baixar(nome, pasta):
    dest = D / f"{pasta.strip('/')}_{nome}"
    if dest.exists() and dest.stat().st_size > 1000: return dest
    with urllib.request.urlopen(urllib.request.Request(BASE + pasta + nome, headers=UA), timeout=600) as r, open(dest, "wb") as f:
        while (b := r.read(1 << 22)): f.write(b)
    return dest


arqs = []
for nome in ("Dados_abertos_Previdenciario.zip", "Dados_abertos_FGTS.zip") + (("Dados_abertos_Sistema_SIDA.zip",) if TUDO else ()):
    for p in pastas:
        if existe(BASE + p + nome): arqs.append((nome, p)); break
    else: print("não achei", nome)
tot = {}      # raiz -> [valor, n, ajuizado, nome, uf, {tipo_credito: valor}]
ref = None
for nome, p in arqs:
    z = zipfile.ZipFile(baixar(nome, p)); ref = ref or p.strip("/")
    for info in z.infolist():
        if not info.filename.lower().endswith(".csv") or info.file_size < 1000: continue
        with z.open(info) as raw:
            rd = csv.DictReader(io.TextIOWrapper(raw, encoding="latin-1", newline=""), delimiter=";")
            for r in rd:
                if r.get("TIPO_PESSOA") != "Pessoa jurídica": continue
                if (r.get("TIPO_DEVEDOR") or "").startswith("Corresp"): pass            # corresponsável também deve; conta
                doc = "".join(ch for ch in (r.get("CPF_CNPJ") or "") if ch.isdigit())
                if len(doc) < 8: continue
                try: v = float((r.get("VALOR_CONSOLIDADO") or "0").replace(",", "."))
                except ValueError: continue
                k = doc[:8]; x = tot.get(k)
                if x is None: x = tot[k] = [0.0, 0, 0, r.get("NOME_DEVEDOR"), r.get("UF_DEVEDOR"), {}]
                x[0] += v; x[1] += 1; x[2] += 1 if r.get("INDICADOR_AJUIZADO") == "SIM" else 0
                tc = (r.get("TIPO_CREDITO") or "Outros").title()[:40]; x[5][tc] = x[5].get(tc, 0) + v
    print(nome, "lido; raízes até agora:", len(tot), flush=True)

lista = sorted(tot.items(), key=lambda kv: -kv[1][0])
grandes = [(k, v) for k, v in lista if v[0] >= 1_000_000][:30000]
saida = {"gerado": hoje.isoformat(), "ref": ref, "fonte": "PGFN, dívida ativa da União (dados abertos)", "completo": TUDO, "n_empresas": len(tot), "total": round(sum(v[0] for v in tot.values())),
         "nota": "Previdenciário e FGTS" + (" e não previdenciário (SIDA)" if TUDO else " (o não previdenciário, maior, entra na rodada mensal)"),
         "top": [{"raiz": k, "nome": (v[3] or "").title()[:80], "uf": v[4], "v": round(v[0]), "n": v[1], "aj": v[2], "tipos": dict(sorted(v[5].items(), key=lambda kv: -kv[1])[:3])} for k, v in lista[:40]],
         "por_raiz": {k: [round(v[0]), v[1]] for k, v in grandes}}
(RAIZ / "web/public/data/pgfn.json").write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
if TUDO:   # resultado completo fica guardado (cache do Actions) e os zips gigantes são apagados
    (D / "pgfn_full.json").write_text((RAIZ / "web/public/data/pgfn.json").read_text(encoding="utf-8"), encoding="utf-8")
    for z in D.glob("*.zip"): z.unlink()
print(len(tot), "empresas com dívida |", len(grandes), "acima de R$ 1 mi | total R$", round(saida["total"] / 1e9, 1), "bi")
