"""Gera carrosséis (1080x1350, formato feed do Instagram) de cada caso de web/public/data/casos.json.
Cada carrossel: capa, situação, linha do tempo com fonte e tipo (decisão, investigação, reportagem, defesa), o que o Radar cruzou, o que falta verificar e aviso.
Saída: web/public/cards/<caso>/01.png... + legenda.txt, e web/public/cards/index.json. Nada é postado: o usuário baixa e publica.
Regra editorial embutida nos cards: investigação, denúncia ou citação NÃO são condenação; cada fato mostra o tipo e a fonte.
Variáveis: RADAR_HANDLE (padrão @radarpublico.seg), RADAR_SITE (padrão radar.lucasnegrelli.com)."""
import json, os, re, pathlib, datetime, textwrap
from PIL import Image, ImageDraw, ImageFont

RAIZ = pathlib.Path(__file__).parent.parent
HANDLE = os.environ.get("RADAR_HANDLE", "@radarpublico.seg")
SITE = os.environ.get("RADAR_SITE", "radar.lucasnegrelli.com")
W, H, M = 1080, 1350, 76
BG, PAINEL, TXT, MUT, ACC = (7, 9, 13), (17, 23, 33), (233, 238, 246), (133, 145, 165), (61, 255, 154)
TIPO = {"decisão": ((61, 255, 154), "DECISÃO"), "investigação": ((255, 179, 0), "INVESTIGAÇÃO"), "reportagem": ((0, 184, 255), "REPORTAGEM"), "defesa": ((179, 136, 255), "DEFESA")}
_cache = {}
def fonte(nome, tam, peso):
    k = (nome, tam, peso)
    if k not in _cache:
        f = ImageFont.truetype(str(RAIZ / "ingestao" / "fontes" / f"{nome}.ttf"), tam)
        try:
            f.set_variation_by_axes([peso] if nome == "SpaceGrotesk" else [min(32, max(14, tam // 3)), peso])
        except Exception: pass
        _cache[k] = f
    return _cache[k]
D = lambda t, p=700: fonte("SpaceGrotesk", t, p)
T = lambda t, p=400: fonte("Inter", t, p)

def quebra(d, texto, f, larg):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if d.textlength(teste, font=f) <= larg: atual = teste
        else:
            if atual: linhas.append(atual)
            atual = palavra
    if atual: linhas.append(atual)
    return linhas

def bloco(d, x, y, texto, f, cor, larg, entre=1.32, max_linhas=None):
    linhas = quebra(d, texto, f, larg)
    if max_linhas and len(linhas) > max_linhas:
        linhas = linhas[:max_linhas]; linhas[-1] = linhas[-1].rstrip(" ,.;") + "…"
    for l in linhas:
        d.text((x, y), l, font=f, fill=cor); y += int(f.size * entre)
    return y

def altura(d, texto, f, larg, entre=1.32, max_linhas=None):
    n = len(quebra(d, texto, f, larg)); n = min(n, max_linhas) if max_linhas else n
    return int(n * f.size * entre)

def chip(d, x, y, texto, cor):
    f = T(24, 700); w = int(d.textlength(texto, font=f)) + 30
    d.rounded_rectangle([x, y, x + w, y + 42], 21, outline=cor, width=2, fill=tuple(int(c * .14) + 4 for c in cor))
    d.text((x + 15, y + 8), texto, font=f, fill=cor)
    return x + w + 12

def base(n, total, titulo_topo="RADAR PÚBLICO"):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    for i in range(0, 520, 2):   # brilho verde discreto no topo
        a = int(26 * (1 - i / 520)); d.line([(0, i), (W, i)], fill=(BG[0], min(255, BG[1] + a // 2), min(255, BG[2] + a // 4)))
    d.ellipse([M, 70, M + 22, 92], outline=ACC, width=3); d.ellipse([M + 8, 78, M + 14, 84], fill=ACC)
    d.text((M + 38, 62), titulo_topo, font=D(34, 700), fill=TXT)
    d.text((W - M - d.textlength(f"{n}/{total}", font=T(26, 500)), 68), f"{n}/{total}", font=T(26, 500), fill=MUT)
    d.line([(M, H - 120), (W - M, H - 120)], fill=(30, 38, 51), width=2)
    d.text((M, H - 94), HANDLE, font=T(28, 600), fill=ACC)
    d.text((W - M - d.textlength(SITE, font=T(26, 500)), H - 92), SITE, font=T(26, 500), fill=MUT)
    return im, d

def mdata(s):
    p = str(s).split("-")
    return f"{p[2]}/{p[1]}/{p[0]}" if len(p) == 3 else f"{p[1]}/{p[0]}" if len(p) == 2 else str(s)

def slides_do_caso(c):
    S = []   # cada item: função(n, total) -> Image
    def capa(n, t):
        im, d = base(n, t)
        y = 240
        chip(d, M, y, "CASO", ACC); y += 90
        y = bloco(d, M, y, c["titulo"], D(80, 700), TXT, W - 2 * M, 1.08, 6) + 24
        y = bloco(d, M, y, re.split(r"(?<=[.!?])\s", c["resumo"])[0], T(36, 400), (190, 201, 218), W - 2 * M, 1.4, 6) + 30
        if c.get("valor"):
            d.rounded_rectangle([M, y, W - M, y + 130], 20, fill=PAINEL, outline=(255, 45, 85), width=2)
            d.text((M + 28, y + 18), f"R$ {c['valor']['bi']:,.1f} bi".replace(",", "X").replace(".", ",").replace("X", ".") + " citados", font=D(48, 700), fill=(255, 107, 136))
            d.text((M + 28, y + 80), "em investigação ou acordo. Não é prejuízo confirmado.", font=T(26, 400), fill=MUT)
        d.text((M, H - 190), f"{len(c.get('marcos', []))} fatos com fonte  ·  atualizado em {datetime.date.today():%d/%m/%Y}  ·  arraste →", font=T(28, 500), fill=MUT)
        return im
    S.append(capa)
    if c.get("situacao"):
        def situ(n, t):
            im, d = base(n, t); y = 200
            d.text((M, y), "SITUAÇÃO HOJE", font=T(28, 700), fill=ACC); y += 70
            for s in c["situacao"][:4]:
                y0 = y
                h = 56 + altura(d, s["valor"], T(32, 400), W - 2 * M - 56, 1.38, 8) + 30
                if y + h > H - 150: break
                d.rounded_rectangle([M, y, W - M, y + h], 18, fill=PAINEL)
                d.text((M + 28, y + 20), s["rotulo"].upper(), font=T(24, 700), fill=(255, 179, 0))
                bloco(d, M + 28, y + 60, s["valor"], T(32, 400), TXT, W - 2 * M - 56, 1.38, 8)
                y += h + 18
            return im
        S.append(situ)
    # linha do tempo: agrupa marcos por slide conforme a altura
    marcos = c.get("marcos", []); i = 0
    medidor = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    while i < len(marcos):
        grupo, y = [], 210
        while i < len(marcos):
            m = marcos[i]
            h = 50 + altura(medidor, m["texto"], T(33, 400), W - 2 * M - 40, 1.38, 9) + 66
            if grupo and y + h > H - 150: break
            grupo.append(m); y += h + 14; i += 1
        def tl(n, t, grupo=grupo):
            im, d = base(n, t); y = 190
            d.text((M, y), "LINHA DO TEMPO", font=T(28, 700), fill=ACC); y += 60
            for m in grupo:
                cor, rot = TIPO.get(m["tipo"], ((138, 160, 181), m["tipo"].upper()))
                h = 50 + altura(d, m["texto"], T(33, 400), W - 2 * M - 40, 1.38, 9) + 66
                d.line([(M + 10, y + 8), (M + 10, y + h + 6)], fill=(30, 38, 51), width=3); d.ellipse([M + 2, y + 6, M + 18, y + 22], fill=cor)
                d.text((M + 40, y), mdata(m["data"]), font=T(28, 600), fill=MUT)
                chip(d, M + 40 + int(d.textlength(mdata(m["data"]), font=T(28, 600))) + 20, y - 8, rot, cor)
                yy = bloco(d, M + 40, y + 52, m["texto"], T(33, 400), TXT, W - 2 * M - 40, 1.38, 9)
                d.text((M + 40, yy + 6), "Fonte: " + (m.get("fonte") or "ver legenda"), font=T(25, 500), fill=(0, 184, 255))
                y += h + 14
            return im
        S.append(tl)
    # o que o Radar cruzou
    extra = []
    pe = [p["nome"] for p in c.get("pessoas", []) if p.get("id")]
    if pe: extra.append(("Pessoas com ficha no Radar (candidaturas, patrimônio, campanha, emendas)", ", ".join(pe)))
    if c.get("alertas"): extra.append(("Alertas do Radar ligados ao tema", f"{len(c['alertas'])} empresas/entidades, por exemplo " + ", ".join(a["empresa"].title() for a in c["alertas"][:2])))
    if c.get("valor"): extra.append(("Valor citado", c["valor"]["rotulo"]))
    if extra:
        def cruz(n, t):
            im, d = base(n, t); y = 200
            d.text((M, y), "O QUE O RADAR CRUZOU", font=T(28, 700), fill=ACC); y += 70
            for rot, val in extra:
                h = 60 + altura(d, val, T(34, 400), W - 2 * M - 56, 1.38, 8) + 30
                d.rounded_rectangle([M, y, W - M, y + h], 18, fill=PAINEL)
                d.text((M + 28, y + 20), rot.upper(), font=T(23, 700), fill=ACC)
                bloco(d, M + 28, y + 64, val, T(34, 400), TXT, W - 2 * M - 56, 1.38, 8); y += h + 18
            return im
        S.append(cruz)
    if c.get("lacunas"):
        def lac(n, t):
            im, d = base(n, t); y = 200
            d.text((M, y), "O QUE AINDA FALTA VERIFICAR", font=T(28, 700), fill=(255, 179, 0)); y += 70
            for l in c["lacunas"][:5]:
                h = altura(d, l, T(33, 400), W - 2 * M - 60, 1.38, 7) + 24
                if y + h > H - 150: break
                d.ellipse([M, y + 14, M + 14, y + 28], fill=(255, 179, 0))
                bloco(d, M + 36, y, l, T(33, 400), TXT, W - 2 * M - 60, 1.38, 7); y += h + 14
            return im
        S.append(lac)
    def fim(n, t):
        im, d = base(n, t); y = 260
        y = bloco(d, M, y, "Como ler este material", D(64, 700), TXT, W - 2 * M, 1.1) + 20
        for txt in ["Decisão, investigação, reportagem e defesa são coisas diferentes: cada fato vem com o tipo e a fonte.",
                    "Investigação, denúncia, indiciamento ou citação NÃO são condenação. Ninguém é culpado antes de decisão judicial definitiva.",
                    "Os links de todas as fontes estão na legenda e no site. Confira antes de compartilhar.",
                    "Achou erro? Responda este post ou use 'Sinalizar erro' no site: corrigimos."]:
            d.ellipse([M, y + 16, M + 12, y + 28], fill=ACC); y = bloco(d, M + 34, y, txt, T(33, 400), (200, 210, 224), W - 2 * M - 40, 1.4) + 18
        d.rounded_rectangle([M, H - 330, W - M, H - 170], 22, fill=PAINEL, outline=ACC, width=2)
        d.text((M + 30, H - 308), "Investigue você mesmo", font=D(44, 700), fill=ACC)
        d.text((M + 30, H - 244), f"Empresas, políticos, emendas e contratos: {SITE}", font=T(30, 500), fill=TXT)
        return im
    S.append(fim)
    return S

def legenda(c):
    L = [c["titulo"].upper(), "", re.split(r"(?<=[.!?])\s", c["resumo"])[0], ""]
    for m in c.get("marcos", [])[:6]:
        L.append(f"• {mdata(m['data'])} [{m['tipo']}] {m['texto'][:170]}" + ("…" if len(m["texto"]) > 170 else ""))
    L += ["", "Fontes:"] + [f"- {m.get('fonte')}: {m['url']}" for m in c.get("marcos", []) if m.get("url")][:8]
    L += ["", "Investigação, denúncia ou citação não são condenação. Ninguém é culpado antes de decisão judicial definitiva.", f"Dados abertos cruzados em {SITE}", "",
          "#radarpublico #transparencia #dinheiropublico #corrupcao #politica #investigacao #dadosabertos #jornalismodedados"]
    return "\n".join(L)

casos = json.loads((RAIZ / "web/public/data/casos.json").read_text(encoding="utf-8"))["casos"]
saida = RAIZ / "web/public/cards"; saida.mkdir(parents=True, exist_ok=True)
indice = []
for c in casos:
    if c.get("tipo") != "politico" or not c.get("marcos"): continue
    S = slides_do_caso(c); pasta = saida / c["id"]; pasta.mkdir(exist_ok=True)
    for f in pasta.glob("*.png"): f.unlink()
    for k, fn in enumerate(S, 1):
        fn(k, len(S)).convert("P", palette=Image.ADAPTIVE, colors=96).save(pasta / f"{k:02d}.png", optimize=True)
    (pasta / "legenda.txt").write_text(legenda(c), encoding="utf-8")
    indice.append({"id": c["id"], "titulo": c["titulo"], "slides": len(S), "ultimo": c.get("ultimo", "")})
    print(c["id"], len(S), "slides", flush=True)
(saida / "index.json").write_text(json.dumps(indice, ensure_ascii=False), encoding="utf-8")
print(len(indice), "carrosséis;", round(sum(f.stat().st_size for f in saida.rglob("*.png")) / 1e6, 1), "MB")
