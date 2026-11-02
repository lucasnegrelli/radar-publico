"""Atualiza o Radar Público de ponta a ponta (a parte que roda na máquina) e publica no GitHub Pages.
Uso:  python ingestao/atualizar.py            -> tudo
      python ingestao/atualizar.py pessoas    -> só os passos cujo nome contém "pessoas"
Cada passo roda isolado: se um falhar, o resto segue e o resumo final diz quem falhou.
A ingestão pesada (PNCP, CNPJ, licitações) roda no GitHub Actions (workflows pncp, cnpj-mensal, compras)."""
import subprocess, sys, time, pathlib, datetime

RAIZ = pathlib.Path(__file__).parent.parent
PY = sys.executable
LOG = RAIZ / "dados" / "atualizar_log.txt"
filtro = sys.argv[1] if len(sys.argv) > 1 else ""

PASSOS = [
    ("tse 2026 (candidaturas, bens, campanha)", [PY, "ingestao/tse_historico.py", "2026"], 1800),
    ("banco central (IF.data)", [PY, "ingestao/bcb_ifdata.py"], 3600),
    ("risco financeiro (RF01)", [PY, "ingestao/risco_financeiro.py"], 900),
    ("risco dossie (balanço, imprensa)", [PY, "ingestao/risco_dossie.py"], 900),
    ("noticias gerais", [PY, "ingestao/noticias.py"], 900),
    ("noticias por alerta", [PY, "ingestao/noticias_alertas.py"], 3600),
    ("fichas de agentes", [PY, "ingestao/fichas.py"], 1800),
    ("pessoas (fichas)", [PY, "ingestao/pessoas.py"], 3600),
    ("pessoas extras (wikipedia, imprensa)", [PY, "ingestao/pessoas_extras.py", "2500"], 7200),
    ("site (build)", ["npx.cmd", "vite", "build"], 900, "web"),
    ("site (publicar no GitHub Pages)", ["bash", "publicar-pages.sh"], 900, "web"),
]

def log(msg):
    linha = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(linha, flush=True)
    with LOG.open("a", encoding="utf-8") as f: f.write(linha + "\n")

resumo = []
for passo in PASSOS:
    nome, cmd, limite = passo[:3]
    pasta = RAIZ / passo[3] if len(passo) > 3 else RAIZ
    if filtro and filtro not in nome: continue
    t0 = time.time(); log(f"INÍCIO {nome}")
    try:
        r = subprocess.run(cmd, cwd=pasta, timeout=limite, capture_output=True, text=True, encoding="utf-8", errors="replace")
        ok = r.returncode == 0
        if not ok: log("   erro: " + (r.stderr or r.stdout)[-400:].replace("\n", " | "))
    except subprocess.TimeoutExpired:
        ok = False; log("   estourou o tempo")
    resumo.append((nome, ok, round(time.time() - t0)))
    log(f"{'OK  ' if ok else 'FALHOU'} {nome} ({round(time.time() - t0)}s)")
print("\nRESUMO"); [print(("  ok     " if ok else "  FALHOU ") + n, f"({s}s)") for n, ok, s in resumo]
sys.exit(0 if all(ok for _, ok, _ in resumo) else 1)
