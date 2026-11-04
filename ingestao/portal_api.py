"""Cliente da API de dados do Portal da Transparência (CGU). Docs: https://api.portaldatransparencia.gov.br/swagger-ui/index.html
Chave gratuita (cadastro por e-mail), no cabeçalho `chave-api-dados`. PORTAL_TOKEN no ambiente ou no .env.
Limite oficial: 90 requisições por minuto (das 06h às 23h59) e 300 por minuto (de 00h às 05h59). O cliente espera o suficiente para ficar abaixo disso
e, se receber 429, recua e tenta de novo. Páginas vêm com 15 registros (alguns endpoints, 500)."""
import datetime, json, os, pathlib, re, sys, time, urllib.error, urllib.parse, urllib.request

RAIZ = pathlib.Path(__file__).parent.parent
BASE = "https://api.portaldatransparencia.gov.br/api-de-dados"
_tok = os.environ.get("PORTAL_TOKEN", "")
if not _tok and (RAIZ / ".env").exists():
    _m = re.search(r"^PORTAL_TOKEN=(.*)$", (RAIZ / ".env").read_text(encoding="utf-8"), re.M); _tok = _m.group(1).strip() if _m else ""
TEM_CHAVE = bool(_tok)
H = {"chave-api-dados": _tok, "Accept": "application/json", "User-Agent": "RadarPublico/1.0 (projeto civico; github.com/lucasnegrelli/radar-publico)"}
_ultimo = 0.0


def _pausa():
    global _ultimo
    h = (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).hour   # horário de Brasília
    gap = 0.25 if h < 6 else 0.72
    d = time.time() - _ultimo
    if d < gap: time.sleep(gap - d)
    _ultimo = time.time()


def get(ep, **q):
    """Uma página. Devolve lista (ou None se falhar de vez)."""
    u = BASE + ep + "?" + urllib.parse.urlencode({k: v for k, v in q.items() if v is not None})
    for i in range(5):
        _pausa()
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=90).read())
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(20 + 20 * i); continue
            if e.code in (401, 403): print("chave recusada pelo Portal:", e.code); sys.exit(1)
            if e.code == 400: print("pedido inválido em", ep, e.read()[:120]); return None
            time.sleep(3 + 4 * i)
        except Exception: time.sleep(3 + 4 * i)
    return None


def paginas(ep, maximo=200, **q):
    """Percorre as páginas até esvaziar (ou até `maximo`)."""
    for p in range(1, maximo + 1):
        r = get(ep, pagina=p, **q)
        if not r: return
        yield from r
