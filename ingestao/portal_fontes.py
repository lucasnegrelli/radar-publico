"""Fontes oficiais via API do Portal da Transparência -> web/public/data/
 - leniencia.json: acordos de leniência (empresas, órgão, situação, vigência)
 - ceaf.json: servidores expulsos (CEAF), últimos 12 meses: contagem por órgão e tipo; a pessoa só aparece com nome (publicado no DOU) e CPF mascarado
Outras fontes da API entram aqui conforme forem sendo validadas (cartões, convênios, licitações por dentro, renúncias fiscais, PEPs)."""
import datetime, json, os, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import portal_api as api

RAIZ = pathlib.Path(__file__).parent.parent; os.chdir(RAIZ)
if not api.TEM_CHAVE:
    print("sem PORTAL_TOKEN: pulando"); sys.exit(0)
hoje = datetime.date.today(); SAIDA = RAIZ / "web/public/data"; SAIDA.mkdir(parents=True, exist_ok=True)
fmt = lambda d: d.strftime("%d/%m/%Y")

# ---- acordos de leniência ----
ac = []
for r in api.paginas("/acordos-leniencia", maximo=60):
    ac.append({"id": r.get("id"), "inicio": r.get("dataInicioAcordo"), "fim": r.get("dataFimAcordo"), "orgao": r.get("orgaoResponsavel"), "situacao": r.get("situacaoAcordo"),
               "empresas": [{"nome": s.get("razaoSocial") or s.get("nomeInformadoOrgaoResponsavel"), "cnpj": s.get("cnpj")} for s in r.get("sancoes", [])],
               "efeitos": [e.get("descricaoResumida") or e.get("descricaoDetalhada") for e in r.get("efeitosAcordo", []) if isinstance(e, dict)][:4], "termos": r.get("quantidade") })
(SAIDA / "leniencia.json").write_text(json.dumps({"gerado": hoje.isoformat(), "fonte": "Portal da Transparência (CGU), acordos de leniência", "n": len(ac), "acordos": ac}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("leniência:", len(ac), "acordos", sum(len(a["empresas"]) for a in ac), "empresas", flush=True)

# ---- CEAF (expulsões de servidores), 12 meses, por janelas de 30 dias para não estourar a paginação ----
reg = []
fim = hoje
for _ in range(12):
    ini = fim - datetime.timedelta(days=30)
    for r in api.paginas("/ceaf", maximo=40, dataPublicacaoInicio=fmt(ini), dataPublicacaoFim=fmt(fim)):
        reg.append(r)
    fim = ini - datetime.timedelta(days=1)
por_org, por_tipo, recentes = {}, {}, []
vistos = set()
for r in reg:
    if r.get("id") in vistos: continue
    vistos.add(r.get("id"))
    org = (r.get("orgaoLotacao") or {}).get("nome") or (r.get("orgaoLotacao") or {}).get("sigla") or "Sem informação" if isinstance(r.get("orgaoLotacao"), dict) else (r.get("orgaoLotacao") or "Sem informação")
    tipo = (r.get("tipoPunicao") or {}).get("descricao") or "Outra"
    por_org[org] = por_org.get(org, 0) + 1; por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
    pu = r.get("punicao") or {}
    recentes.append({"d": r.get("dataPublicacao"), "nome": (pu.get("nomePunido") or "").title(), "cpf": pu.get("cpfPunidoFormatado"), "tipo": tipo, "org": org, "portaria": pu.get("portaria"), "dou": f"seção {pu.get('secaoDOU')}, pág. {pu.get('paginaDOU')}"})
recentes.sort(key=lambda x: (x["d"] or "")[6:] + (x["d"] or "")[3:5] + (x["d"] or "")[:2], reverse=True)
(SAIDA / "ceaf.json").write_text(json.dumps({"gerado": hoje.isoformat(), "fonte": "Portal da Transparência (CGU), CEAF", "n": len(vistos), "por_orgao": sorted(({"org": k, "n": v} for k, v in por_org.items()), key=lambda x: -x["n"])[:40],
    "por_tipo": sorted(({"tipo": k, "n": v} for k, v in por_tipo.items()), key=lambda x: -x["n"]), "recentes": recentes[:60]}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("CEAF:", len(vistos), "expulsões em 12 meses |", len(por_org), "órgãos")
