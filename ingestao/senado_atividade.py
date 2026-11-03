"""Atividade dos senadores (API de dados abertos do Senado): foto, projetos de autoria, comissões atuais e votos nominais de 2025 e 2026.
Saída: dados/senado_atividade.json (lido por pessoas.py). Fonte: https://legis.senado.leg.br/dadosabertos"""
import json, os, time, pathlib, datetime, urllib.request
from concurrent.futures import ThreadPoolExecutor

RAIZ = pathlib.Path(__file__).parent.parent
os.chdir(RAIZ)
B = "https://legis.senado.leg.br/dadosabertos"
UA = "radar-publico/0.1 (+https://github.com/lucasnegrelli/radar-publico)"

def get(ep, tent=3):
    for t in range(tent):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(f"{B}/{ep}", headers={"accept": "application/json", "User-Agent": UA}), timeout=60).read())
        except Exception:
            time.sleep(2 * (t + 1))
    return None

def lista(x, *caminho):
    for k in caminho:
        x = (x or {}).get(k) if isinstance(x, dict) else None
    return x if isinstance(x, list) else ([x] if x else [])

L = lista(get("senador/lista/atual"), "ListaParlamentarEmExercicio", "Parlamentares", "Parlamentar")
print(len(L), "senadores em exercício", flush=True)

def um(p):
    ident = p["IdentificacaoParlamentar"]; cod = ident["CodigoParlamentar"]
    aut = lista(get(f"senador/{cod}/autorias"), "MateriasAutoriaParlamentar", "Parlamentar", "Autorias", "Autoria")
    proj = {(a.get("Materia") or {}).get("Codigo") for a in aut if (a.get("Materia") or {}).get("Sigla") in ("PL", "PLS", "PEC", "PLP", "PLN", "PDL", "PRS")}
    com = lista(get(f"senador/{cod}/comissoes"), "MembroComissaoParlamentar", "Parlamentar", "MembroComissoes", "Comissao")
    atuais = []
    for c in com:
        if c.get("DataFim"): continue
        i = c.get("IdentificacaoComissao") or {}
        atuais.append({"sigla": i.get("SiglaComissao"), "nome": i.get("NomeComissao"), "titulo": c.get("DescricaoParticipacao")})
    votos = {}
    for ano in (2025, datetime.date.today().year):
        for v in lista(get(f"senador/{cod}/votacoes?ano={ano}"), "VotacaoParlamentar", "Parlamentar", "Votacoes", "Votacao"):
            k = v.get("SiglaVotoParlamentar") or "?"
            votos[k] = votos.get(k, 0) + 1
    return cod, {"nome": ident.get("NomeParlamentar"), "nome_completo": ident.get("NomeCompletoParlamentar"), "partido": ident.get("SiglaPartidoParlamentar"), "uf": ident.get("UfParlamentar"),
                 "foto": (ident.get("UrlFotoParlamentar") or "").replace("http://", "https://"), "projetos": len([x for x in proj if x]), "comissoes": atuais[:6], "votos": votos}

saida = {}
with ThreadPoolExecutor(6) as ex:
    for cod, d in ex.map(um, L):
        saida[cod] = d
(RAIZ / "dados" / "senado_atividade.json").write_text(json.dumps(saida, ensure_ascii=False), encoding="utf-8")
print(len(saida), "senadores; exemplo:", next(iter(saida.values())))
