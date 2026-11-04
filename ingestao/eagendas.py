"""Agenda oficial de ministros e secretários-executivos (e-Agendas, CGU) -> web/public/data/agenda.json
API pública da CGU, exige token (EAGENDAS_TOKEN no ambiente ou no arquivo .env). Docs: https://eagendas.cgu.gov.br/docs?api-docs.json
Pega, dos órgãos da administração direta, os ministros de Estado e secretários-executivos, e deles: compromissos (-30 a +14 dias), viagens e presentes/hospitalidades (12 meses).
Dos participantes privados guardamos só a entidade representada, nunca o nome de pessoa física. O que cada agente registra e publica é responsabilidade do órgão."""
import datetime, json, os, pathlib, re, sys, time, urllib.error, urllib.parse, urllib.request

RAIZ = pathlib.Path(__file__).parent.parent; os.chdir(RAIZ)
tok = os.environ.get("EAGENDAS_TOKEN", "")
if not tok and (RAIZ / ".env").exists():
    m = re.search(r"^EAGENDAS_TOKEN=(.*)$", (RAIZ / ".env").read_text(encoding="utf-8"), re.M); tok = m.group(1).strip() if m else ""
if not tok:
    print("sem EAGENDAS_TOKEN: pulando a agenda"); sys.exit(0)
H = {"Accept": "application/json", "Authorization": "Bearer " + tok, "User-Agent": "RadarPublico/1.0 (projeto civico; github.com/lucasnegrelli/radar-publico)"}
BASE = "https://eagendas.cgu.gov.br/api/v2"


def g(ep, **q):
    u = BASE + ep + ("?" + urllib.parse.urlencode(q) if q else "")
    for i in range(3):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=90).read())
        except urllib.error.HTTPError as e:
            if e.code in (401, 403): print("token recusado pela API:", e.code); sys.exit(1)
            time.sleep(2 + 3 * i)
        except Exception: time.sleep(2 + 3 * i)
    return {}


def lista(r, chave):
    x = (r.get("resposta") or {}) if isinstance(r, dict) else {}
    return x.get(chave) or next((v for v in x.values() if isinstance(v, list)), []) if isinstance(x, dict) else []


hoje = datetime.date.today(); fmt = lambda d: d.strftime("%d-%m-%Y"); iso = lambda s: "-".join(reversed(s.split("-"))) if s else None
orgs = [x for x in lista(g("/orgaos", situacao="Ativo"), "orgaos") if "Direta" in (x.get("classificacao_administrativa") or "")]
alto = []
for o in orgs:
    for x in lista(g("/agentes-publicos-obrigados", orgao_id=o["id"], situacao="Ativo"), "agentes_publicos_obrigados"):
        c = x.get("cargo_comissao") or ""
        if re.match(r"^(MINISTRO|SECRET[ÁA]RIO.EXECUTIV)", c) and "SUBSTITUT" not in c and "ADJUNTO" not in c:
            alto.append({"apo": x["apo_id"], "nome": x["apo_nome"].title(), "cargo": c.title()[:90], "orgao": (x.get("orgao") or "").split(" - ", 1)[-1], "sigla": (x.get("orgao") or "").split(" - ")[0],
                         "ministro": c.startswith("MINISTRO")})
print(len(alto), "autoridades em", len(orgs), "órgãos", flush=True)

de, ate = hoje - datetime.timedelta(days=30), hoje + datetime.timedelta(days=14)
nome_pub = lambda p: (p.get("apo_nome") or "").title()
n_comp = 0
for a in alto:
    comp = lista(g("/compromissos", data_inicio=fmt(de), data_termino=fmt(ate), apo_id=a["apo"]), "compromissos")
    a["compromissos"] = [{"id": c["id"], "tipo": c.get("tipo_compromisso"), "assunto": re.sub(r"\s+", " ", c.get("assunto") or "")[:260], "det": re.sub(r"\s+", " ", c.get("detalhamento") or "")[:500], "obj": [o.get("descricao") or o.get("objetivo") or "" for o in c.get("objetivos_compromisso", []) if isinstance(o, dict)][:3], "local": (c.get("local") or "").strip(" ."), "d": iso(c.get("data_inicio")), "df": iso(c.get("data_termino")),
                          "h": c.get("hora_inicio"), "hf": c.get("hora_termino"), "viagem": bool(c.get("viagem_id")),
                          "com": sorted({nome_pub(p) for p in c.get("participantes_publicos", []) if p.get("apo_id") != a["apo"] and p.get("apo_nome")})[:4],
                          "privados": sorted({(p.get("nome_instituicao") or "").strip() + "|" + re.sub(r"\D", "", p.get("cnpj_instituicao") or "") + "|" + (p.get("cargo_instituicao") or "").strip() for p in c.get("participantes_privados", []) if p.get("nome_instituicao")})[:8],
                          "n_privados": len(c.get("participantes_privados", [])), "exterior": [x for x in (((r.get("representante_cargo") or "") + " · " + (r.get("representante_orgao") or r.get("representante_nome_organismo_internacional") or "")).strip(" ·") for r in c.get("representantes", [])) if x][:4], "n_pub": len(c.get("participantes_publicos", []))} for c in comp]
    a["compromissos"].sort(key=lambda c: (c["d"] or "", c["h"] or ""), reverse=True); n_comp += len(a["compromissos"])
    v = lista(g("/viagens", data_inicio=fmt(hoje - datetime.timedelta(days=90)), data_termino=fmt(ate), apo_id=a["apo"]), "viagens")
    a["viagens"] = [{k: x.get(k) for k in ("id", "data_inicio", "data_termino", "cidade_destino", "uf_destino", "pais_destino", "motivo", "assunto", "descricao") if x.get(k) is not None} for x in v][:20]
    p = lista(g("/presentes-hospitalidades", data_inicio=fmt(hoje - datetime.timedelta(days=365)), data_termino=fmt(hoje), apo_id=a["apo"]), "presentes_hospitalidades")
    a["presentes"] = [{k: x.get(k) for k in ("id", "tipo", "descricao", "valor", "ofertante", "data", "data_recebimento", "tipo_item_recebido") if x.get(k) is not None} for x in p][:20]
    time.sleep(0.15)

alto = [a for a in alto if a["compromissos"] or a["viagens"] or a["presentes"]]
alto.sort(key=lambda a: (not a["ministro"], -len(a["compromissos"])))
saida = {"gerado": hoje.isoformat(), "janela": [de.isoformat(), ate.isoformat()], "fonte": "e-Agendas (CGU)", "n_autoridades": len(alto), "n_compromissos": n_comp, "autoridades": alto}
(RAIZ / "web/public/data/agenda.json").write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(len(alto), "autoridades com registro |", n_comp, "compromissos |", sum(len(a["viagens"]) for a in alto), "viagens |", sum(len(a["presentes"]) for a in alto), "presentes")
