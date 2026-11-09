# Radar Público: pesquisa de design e quatro territórios de direção de arte

Data: 08/11/2026. Autoria: diretor(a) de arte/pesquisador(a) (Claude), para Lucas Negrelli. Base: `docs/pesquisa/00_BRIEF.md` e `docs/DIRECAO_DE_ARTE.md` (lidos na íntegra).

Convenção do briefing: **VERIFICADO** = eu abri/testei nesta sessão (08/11/2026); **FONTE** = afirmado por fonte citada ou por conhecimento geral que não reverifiquei (indico); **INFERÊNCIA** = meu raciocínio.

---

## 0. Resumo executivo (leia isto se tiver 2 minutos)

1. Abri de fato **24 sites** no Chrome (lista na seção 1). Em cada um, extraí por script as fontes, tamanhos, pesos e cores computados de h1/h2/p/body e tirei screenshot. Seis alvos falharam ou foram barrados (Reuters pede verificação de dispositivo, TheyWorkForYou devolveu 429, Washington Post 404, Berliner Morgenpost e Politicômetro deram erro, Awwwards só mostrou uma lista sem valor). Não contornei bloqueio nenhum.
2. **Limite honesto:** a janela do navegador ficou majoritariamente em ~559 px (celular largo) e, nas últimas visitas, em 1920 px (marcado onde ocorreu). FT, NYT e Estadão só mostraram um muro de cookies ou 404: dessas três só tenho fontes e cores, não layout. Não afirmo nada sobre o "gesto" dessas.
3. **Achado mais forte:** quase todo site jornalístico abre, no celular, com um **muro de consentimento** (vi em Guardian, FT, NYT, OCCRP, Flightradar24, Correctiv, FTM, OWID, Núcleo, Aos Fatos, Lupa). O Radar não rastreia ninguém; a **primeira tela sem nenhuma barreira** já é uma diferença de produto que se vê.
3b. O trabalho premiado que li de perto (Sigma 2026, texto oficial dos vencedores) vence por **método à mostra, um caso humano concreto e forma própria do dado**, não por estilo. Um vencedor é praticamente o irmão do Radar: *Fantasmas del Erario* (Quinto Elemento Lab, México), 834 empresas de fachada e 486 instituições públicas.
4. Os quatro territórios propostos (mais um "reserva"): **Extrato** (radicalmente tipográfico), **Sobreposição** (arte concreta em vetor, sem textura), **Placa** (sinalização), **Lambe** (cartaz de rua em duas tintas) e **Cordel disciplinado** (reserva, já testado e não aprovado).
5. **Recomendação:** construir a base em **Extrato** (por ser a mais fácil de usar, mais barata e mais difícil de virar "slop") e **roubar da Sobreposição o gesto da coincidência**, com a tinta de alerta única da **Placa**. Teste primeiro, com 6 a 8 pessoas não técnicas em Android de entrada, as três telas (início, ficha, cidade) em Extrato contra Lambe. Detalhes na seção 7.

---

## 1. Os projetos analisados (família a família)

Cada ficha traz: URL, ano/prêmio (só se verificado), o que é distintivo, **specs observadas**, o que **não** serve ao Radar. Fontes/cores são os `computed styles` lidos por script em 08/11/2026; "w=559" indica a largura da janela.

### Família (a) Jornalismo de dados e investigação

**1. ProPublica** (https://www.propublica.org) — VERIFICADO.
- Distintivo: logotipo-palavra enorme e condensado no topo; tema escuro no celular; foto-manchete de página inteira.
- Specs: manchete em "Feature Headline" (serifa própria) 32 px/700, quando em h1; UI e links em "Brut Grotesque" 16 px; fundo preto, texto cinza-quente `rgb(221,219,212)`; um único vermelho (botão "Donate"); barra fixa inferior de newsletter com campo + botão branco.
- Dado/credibilidade: o slogan "no bullsh*t" aparece na barra de assinatura; "Investigative Journalism in the Public Interest" no topo.
- Não serve: serifa de manchete e foto de página inteira dependem de apuração humana por matéria; o Radar tem milhares de alertas gerados por regra.

**2. The Pudding** (https://pudding.cool) — VERIFICADO.
- Distintivo: logotipo desenhado à mão, cada história com seu "mundo" de cor; miniatura é o próprio gráfico; número da edição (#228) e data em etiqueta de contorno.
- Specs: fundo `#191919`, texto `#efefef`; "Gooper SemiCondensed" 16 px (corpo, serifa semicondensada) + "Atlas Grotesk" 14 px (rótulos); busca "Find a story…" e seletor; capa em coluna única, imagem em largura total (vermelho vivo em #228).
- Não serve: identidade por história (cada uma com paleta) não cabe num produto que precisa ser constante.

**3. Our World in Data** (https://ourworldindata.org) — VERIFICADO.
- Distintivo: a **busca é a capa** ("Research and data to make progress against the world's largest problems"), com contador de cobertura ("14,087 charts across 126 topics").
- Specs: h2 em Playfair Display 24/600; Lato 16 no corpo; azul-marinho `rgb(29,61,99)` + amarelo `rgb(247,192,32)` + branco; atalhos "Popular pages" como chips horizontais; muro de cookies em amarelo sobre o rodapé.
- Não serve: o tom é didático e otimista, contrário ao "sério e cortante".

**4. Reuters Graphics** (https://www.reuters.com/graphics/) — barrado por "Verificando o dispositivo". Só li fontes da página de verificação (knowledge-medium/regular). Não analisado; Sigma 2026 premia "How Iran Moves Sanctioned Oil Around the World" (Reuters, Cingapura), FONTE: https://www.sigmaawards.org (ver item 23).

**5. The Guardian** (https://www.theguardian.com/international) — VERIFICADO (muro de cookies cobrindo metade da tela).
- Specs: "GH Guardian Headline" 24/700 (serifa egípcia) + GuardianTextSans 17; masthead azul-marinho com o título sobre fundo escuro; abas de seção em linha.
- Distintivo: manchetes em serifa egípcia pesada com cor de seção. Não serve: tudo é voltado a texto longo.

**6. ICIJ** (https://www.icij.org) — VERIFICADO.
- Specs: Poppins 27/700 em h1 e 18 px no corpo; fundo branco; logo com globo vermelho; **rótulo de seção em vermelho pequeno em caixa-alta** ("EUROPE", "CORRUPTION"); linha de autoria em caixa-alta com data.
- Distintivo: um único vermelho para categoria + autoria sempre visível. Não serve: Poppins (geométrica arredondada) suaviza demais.

**7. OCCRP** (https://www.occrp.org/en) — VERIFICADO.
- Specs: Inter 600 32 px (títulos), Lora 28 (resumo), "Inter Tight" 14 (UI); fundo `rgb(30,31,33)`; fotos em **duotom azul-e-amarelo** de rostos; muro de cookies.
- Distintivo: a foto vira marca, duotom controla a "cara" do site. Não serve: rostos de pessoas físicas, contra a regra de privacidade do Radar.

**8. Follow the Money (FTM)** (https://www.ftm.eu) — VERIFICADO.
- Specs: títulos em "Pilat Condensed" 24/700, corpo em "GT America" 16; fundo creme `rgb(245,241,237)`; capa de aniversário em colagem azul-claro com estrela amarela.
- Nota: é creme, o que o cliente rejeita. Distintivo é a colagem de recortes "bagunçada de propósito". Não serve ao Radar.

**9. Correctiv** (https://correctiv.org) — VERIFICADO.
- Specs: "Source Sans 3" 17 px; títulos 23/700; fundo `#f8f8f8`; botão de apoio amarelo; muro de privacidade em português (curioso: banner em pt-PT).
- Distintivo: sobriedade; o "Recherche" (apuração) como seção. Não serve: não há gesto próprio.

**10. SCMP Infographics** (https://www.scmp.com/infographic) — VERIFICADO.
- Specs: fundo `rgb(39,41,45)`; títulos Merriweather 300 (serifa leve); Roboto 300/400 em corpo; "LATEST PROJECT" com capa ilustrada grande ("Lessons from a tragedy": ilustração em amarelo/preto de prédios); carrossel horizontal "FEATURED PROJECTS".
- Distintivo: cada projeto tem **ilustração-capa própria**; o índice é um catálogo de capas.
- Não serve: a ilustração por projeto é trabalho manual que o Radar não pode repetir por alerta.

**11. Núcleo Jornalismo** (https://www.nucleo.jor.br) — VERIFICADO.
- Specs: títulos em **Young Serif** 24–26 px; corpo Barlow 15–16; fundo `#eee`; botão roxo; abas "Conversas / Destaques / Radar rápido"; banner de instalar app na primeira tela.
- Nota: Young Serif é exatamente a "serifa da moda" que o cliente rejeitou. Bom contraexemplo.

**12. Aos Fatos** (https://www.aosfatos.org) — VERIFICADO.
- Specs: títulos em Libre Baskerville 22/700; fundo preto com texto claro; foto de página inteira; **ilustrações tipo adesivo** em amarelo/ciano/preto (urna eletrônica, moeda) dentro do modal de apoio; logotipo "aos fatos:" com dois-pontos.
- Distintivo: o dois-pontos no nome como gesto verbal. Não serve: muro de doação na primeira tela.

**13. Lupa** (https://lupa.news) — VERIFICADO (janela em 1920 px).
- Specs: Barlow Semi Condensed 700 (h1 32) em toda a página; **verde-limão** forte no topo (não medi o hex) + faixa preta "ÚLTIMAS" com texto correndo; fundo branco.
- Distintivo: cor ácida inconfundível numa categoria sisuda (checagem). Não serve: o limão sinaliza "marca de jornal", não alerta.

**14. Quinto Elemento Lab** (https://quintoelab.org) — VERIFICADO (1920 px).
- Specs: IBM Plex Sans 18 px, branco; logotipo de **pontos coloridos** formando um círculo; nome em caixa-alta; navegação em caixa-alta com régua fina; ilustrações em **duotom amarelo/preto** com etiquetas rosa "INVESTIGACIONES".
- Distintivo: ilustração editorial coerente num sistema simples. Vencedor Sigma 2026 (ver 23).

### Família (b) Prêmios e showcases

**23. Sigma Awards 2026** (https://www.sigmaawards.org/from-toxic-supply-chains-in-africa-to-baltic-sabotage-to-stolen-children-in-syria-10-data-projects-win-2026-sigma-awards/) — VERIFICADO, texto lido na íntegra. Anunciado em 12/05/2026 pela GIJN: 543 inscrições de 84 países, 31 finalistas, 17 jurados, sem categorias por assunto nem formato. Dez vencedores:
- *Green to Grey* (Arena for Journalism in Europe/NRK + 11 veículos, UE): perda de natureza equivalente a 600 campos de futebol por dia; jurados elogiam apresentação "intuitiva, com forte narrativa".
- *Inside Russia's Shadow War in the Baltics* (Financial Times): 11 incidentes e 3 navios, "beautifully rendered" (juízes).
- *Invisibles* (Salud con lupa, Peru): algoritmo exclui idosos da pensão; inclui guias de serviço público; "ajudou a levar a reforma do governo".
- *The Human Trap* (ARIJ/Al-Muhajir), *Fantasmas del Erario* (Quinto Elemento Lab, México; **486 instituições, 834 empresas de fachada, US$ 570 milhões em duas décadas**), *Syria's Stolen Children* (Lighthouse Reports e outros), **Cerrado, o elo sagrado das águas do Brasil** (Ambiental Media, Brasil), *The Silent Victims of War* (NZZ + Texty), *The Poisonous Lead Trade* (The Examination + NYT), *How Iran Moves Sanctioned Oil* (Reuters).
- O que os jurados valorizaram, nas palavras deles: "torna fácil ver"; "conecta um sistema complexo a consequências reais"; "metodologia replicável"; "equipa outros jornalistas para continuar" (no caso do México); consentimento e anonimato como padrão de excelência; "sofisticação estética + reportagem profunda" (Cerrado). INFERÊNCIA: o júri não premia "visual bonito", premia **clareza + prova + cuidado**.
- Aplicação ao Radar: o projeto mexicano usa quase a mesma matéria do Radar (lista oficial de empresas inidôneas cruzada com contratos federais). Nunca vi a interface dele (só a página do Quinto Elemento); só confirmo os números e o texto dos jurados.

**24. Information is Beautiful Awards, showcase** (https://www.informationisbeautifulawards.com/showcase) — VERIFICADO (lista e filtros; não abri projetos individuais).
- Specs da página: "proxima-nova-soft" 14 px, fundo `rgb(246,246,246)`; filtros por ano (2012–2024), tipo de prêmio (Gold, Silver, Bronze, Shortlist, Longlist, Rising Star, Best Non-English-Language, Outstanding Studio, Student, Community, Most Beautiful) e por tema (inclui "Current Affairs & Politics", "Politics & Global"); primeiro cartão visível: "Things I love about my cat" (forma própria de dado, pares de peças claro/escuro).
- Limite: não consegui ler a lista de vencedores por ano. Não citarei nenhum vencedor específico que não vi.

**25. Awwwards, categoria "Government"** (https://www.awwwards.com/websites/government/) — VERIFICADO, **inútil**: a listagem trouxe sites genéricos de pequenos estúdios, sem nenhum caso cívico premiado. Não extrapolo nada. (O documento anterior já registrava Site of the Year como "mundos ilustrados e em 3D": FONTE, `docs/DIRECAO_DE_ARTE.md` §7.)

### Família (c) Produtos de dados densos

**15. Windy** (https://www.windy.com) — VERIFICADO.
- Specs: mapa em tela cheia; fonte do sistema 14 px (`-apple-system`, Segoe UI); **menu de camadas à direita como lista vertical de discos coloridos** (Vento, Chuva, Temperatura, Nuvens…); botão vermelho "Menu"; **linha do tempo inferior com botão de play**; busca no topo com cartão de temperatura ao lado.
- Gesto: arrastar o tempo. Cor = valor do dado. Não serve: o Radar não é um campo contínuo.

**16. Flightradar24** (https://www.flightradar24.com) — VERIFICADO.
- Specs: Open Sans 16; mapa; **barra inferior com 3 abas** (Configurações, Clima, Filtros) com ícone; busca no topo; avião como objeto tocável; modal de consentimento ocupando 60% da tela.
- Gesto: tocar o objeto. Lição: controles embaixo, ao alcance do polegar.

**17. OpenSanctions** (https://www.opensanctions.org) — VERIFICADO.
- Specs: Mona Sans 500/700 (h1 32); cabeçalho azul com título branco, busca larga com botão verde "Search"; **faixa escura monoespaçada "1,904,846 entities · 487 data sources"** logo abaixo; links azuis `rgb(0,78,235)`.
- Lição: a busca grande + o número de cobertura em mono = confiança instantânea.

**18. USAspending.gov** (https://www.usaspending.gov) — VERIFICADO.
- Specs: Source Sans Pro; faixa-governo no topo; título "The official source of government spending data"; botão azul-escuro de largura total "Start Searching Awards", segundo botão em contorno; ilustração-paisagem com cidade e turbinas; seção verde-água "What people are searching" (categorias populares como "National Security").
- Lição: **perguntas populares como atalho**; ilustração decorativa é o que o Radar não deve fazer.

**19. GovTrack** (https://www.govtrack.us) — VERIFICADO (passou por uma verificação Cloudflare antes; carregou).
- Specs: Public Sans (18/23/15,2 px); fundo da página bordô `rgb(157,33,70)`; cartões brancos com **filete azul-marinho no topo**; primeiro texto: "We're tracking the activities of the United States Congress and the White House to make a more open and accountable government."
- Lição: a primeira frase explica a função sem jargão. Não serve: bordô + cartões é visual institucional americano.

**20. TheyWorkForYou** — 429 Too Many Requests; **não analisei**.

**21. Base dos Dados** (https://basedosdados.org) — VERIFICADO.
- Specs: Roboto; logomarca "BD" em dois quadrados verdes; H1 "Dados organizados. Análises confiáveis."; botão verde de largura total "Acesse a plataforma de dados" + botão em contorno "Conheça os serviços de consultoria"; imagem do produto logo abaixo; logos de parceiros.
- Lição: duas promessas de três palavras e CTA único. Não serve: visual de SaaS.

**22. Atlas Brasil** (https://www.atlasbrasil.org.br) — VERIFICADO.
- Specs: Catamaran 800 (21,6 px), Open Sans 14,4; abertura escura com fotografia noturna e frase "Retratamos o desenvolvimento humano sustentável e as desigualdades no Brasil, combinando dados de qualidade com formas amigáveis de visualização."; seta de rolagem.
- Lição: o PNUD/Ipea/FJP usam **tom emocional na abertura** antes da ferramenta; a ferramenta fica atrás de uma rolagem. Pouco funcional no celular.

### Outros já vistos na rodada anterior (FONTE: `docs/DIRECAO_DE_ARTE.md` §2; não reverificados hoje)
Politicômetro, Downdetector, Liveuamap, World Monitor, ICIJ Offshore Leaks.

### Visitas que só renderam fontes (sem layout)
- **FT** (https://www.ft.com/visual-and-data-journalism): muro de cookies; títulos "FinancierDisplayWeb" 32; corpo "metric 2 VF" 16 px; texto `rgb(51,48,46)`. Sigma 2026 premia o FT ("Inside Russia's Shadow War in the Baltics").
- **NYT Graphics** (https://www.nytimes.com/spotlight/graphics): muro de privacidade em português; títulos "nyt-karnak" 24/900, UI "nyt-franklin" 14–18.
- **Estadão** (a URL de dados deu 404): só tipografia "EstadaoHeadline-SemiBold" 42 em azul `rgb(0,47,216)` + Lato.

### Não consegui (e não finjo ter feito)
Reuters Graphics, TheyWorkForYou, Washington Post, Berliner Morgenpost, Süddeutsche, NZZ (visuals), Bloomberg, Folha, Webby, FWA, CSSDA, Data Journalism Awards (global), SND. Busca por lista de vencedores DJA 2025 não retornou nomes (só confirmou, FONTE: https://www.journalism.co.uk, que há premiação; sem nomes). O "Sigma 2026" substitui parcialmente essa lacuna.

---

## 2. Padrões: o que separa trabalho premiado de genérico

**Leitura combinada** (INFERÊNCIA a partir das 24 visitas e do texto dos jurados do Sigma): o genérico copia um **estilo**; o premiado resolve um **problema do material** e deixa a prova à mostra. Cada princípio tem dois exemplos reais.

| # | Princípio transferível | Exemplo 1 | Exemplo 2 |
|---|---|---|---|
| 1 | **Uma frase diz a função.** Sem jargão, na primeira dobra. | GovTrack: "We're tracking the activities of the United States Congress…" (VERIFICADO) | Base dos Dados: "Dados organizados. Análises confiáveis." (VERIFICADO) |
| 2 | **A busca ou a pergunta é o herói** da primeira tela. | OWID: busca em destaque + "Popular pages" (VERIFICADO) | OpenSanctions: busca larga + botão verde (VERIFICADO) |
| 3 | **Número de cobertura como prova de vida**, em mono, pequeno. | OpenSanctions: "1,904,846 entities · 487 data sources" (VERIFICADO) | OWID: "14,087 charts across 126 topics" (VERIFICADO) |
| 4 | **O objeto é a tela**; controles ao alcance do polegar. | Windy: mapa total, linha do tempo embaixo (VERIFICADO) | Flightradar24: barra inferior de 3 abas (VERIFICADO) |
| 5 | **Forma sob medida para o dado**, não gráfico de biblioteca. | FT Baltic: 11 incidentes e 3 navios em mapa de AIS (FONTE: texto Sigma 2026) | NZZ/Texty: a trajetória de **uma criança** como espinha (FONTE: Sigma 2026) |
| 6 | **Um caso humano ou concreto como porta**, depois o sistema. | Salud con lupa, "Invisibles": do idoso sem pensão ao algoritmo (FONTE: Sigma 2026) | Quinto Elemento: de uma empresa de fachada às 834 (FONTE: Sigma 2026) |
| 7 | **Cor com significado único e escasso.** | ICIJ: o vermelho só para categoria (VERIFICADO) | ProPublica: preto + um vermelho só para doar (VERIFICADO) |
| 8 | **Duas vozes tipográficas**: uma de manchete com caráter, uma neutra para interface. | NYT: Karnak 900 + Franklin (VERIFICADO) | ProPublica: Feature Headline + Brut Grotesque (VERIFICADO) |
| 9 | **Método, limite e consentimento à vista** (credibilidade desenhada). | NZZ/Texty: "explicação completa da metodologia" ao leitor e proteção da criança (FONTE: Sigma 2026) | ICIJ Offshore Leaks: aviso legal antes da busca (FONTE: `docs/DIRECAO_DE_ARTE.md`) |
| 10 | **Marca de mão ou de sistema, nunca de modelo.** | The Pudding: logotipo à mão e capa por história (VERIFICADO) | Quinto Elemento: logo de pontos + duotom amarelo/preto consistente (VERIFICADO) |

Três padrões negativos (o que o genérico faz), todos observados:
- **Muro de consentimento antes de qualquer conteúdo** (11 sites). Para o Radar: não ter.
- **Serifa de manchete "da moda" + creme** (Núcleo/Young Serif, FTM/creme). É o que o cliente rejeitou.
- **Ilustração-capa por matéria** (SCMP, Aos Fatos, Quinto Elemento): funciona para quem tem ilustrador por pauta; o Radar gera milhares de alertas por regra. **O visual de cada alerta precisa nascer dos dados**, não de um ilustrador.

---

## 3. Cultura visual brasileira como matéria-prima

Nada daqui foi reverificado hoje; é **FONTE (conhecimento geral)** com minha avaliação (INFERÊNCIA). Antes de qualquer uso de obra ou marca específica, checar direitos.

| Vertente | O que é potente | Clichê/risco |
|---|---|---|
| **Arte concreta (Ruptura, SP, 1952; Waldemar Cordeiro) e neoconcretismo (1959; Lygia Clark, Lygia Pape, Hélio Oiticica)** | Geometria como pensamento: planos que se sobrepõem, cor como estrutura, o espaço como participante. Casa com "a coincidência" (dois eixos que se tocam). | Virar "quadrado colorido de museu". Evitar citar obras; usar a lógica (plano, módulo, sobreposição). |
| **Design gráfico moderno brasileiro (Escola de Ulm/ESDI, Alexandre Wollner, Cauduro/Martino, Aloísio Magalhães)** | Sistemas de identidade rigorosos, símbolos de uma só ideia, sinalização do Metrô de SP. Mostra que "sério" não precisa ser frio. | Nostalgia de manual de marca. |
| **Tropicalismo gráfico (Rogério Duarte, capas e cartazes dos anos 1960–70)** | Mistura de cultura popular e vanguarda, tipografia irreverente. | Muito ornamental e musical; contradiz o "cortante". |
| **Cartaz político/sindical e Diretas Já** | Tipografia gigante, uma ou duas tintas, mensagem direta; economia de meio. | Ser lido como "panfleto partidário", o que prejudica a neutralidade do Radar. O cuidado é crítico (ver Lambe). |
| **Lambe-lambe** | Impresso barato colado na rua; reproduzível, reconhecível por todo brasileiro; a "dobra" do papel, a sobreposição de cartazes. | Textura simulada sem função vira decoração. |
| **Cordel e xilogravura (J. Borges, Samico)** | Literatura popular que informa e denuncia; preto sobre papel; hachura. | **Já testado e não aprovado.** Risco de folclore/kitsch e de leitura "regional" em produto nacional. |
| **Sinalização urbana e rodoviária; placas de obra; faixas de pedestre; "Cuidado"** | Linguagem universal que o povo lê em 1 segundo; amarelo + preto é sinal de cautela. | Cuidado com o uso de elementos oficiais de trânsito (símbolos CONTRAN) como se fossem sinal de verdade. |
| **Cédulas e selos** | Confiança, serial, microtexto. | Guilhoche já rejeitado ("enfeite que não significa"). |
| **Azulejaria (Athos Bulcão, Brasília)** | Módulo repetido com variação, ritmo. | Vira padrão decorativo de fundo. |
| **Tipografia brasileira** | Letras de cartaz popular (ex.: Londrina Solid, mencionada no documento anterior); letras de caminhão, faixa pintada à mão. | Letreiro pintado à mão em tudo vira "festa junina". |

**Síntese:** o que é potente é **a lógica** (concreto: sobreposição; sinalização: urgência legível; lambe: tipografia/tinta simples), não a **imagem** (xilogravura, azulejo, tropicália). Quem usa a imagem corre risco de folclore; quem usa a lógica cria algo brasileiro sem rótulo.

---

## 4. Restrições de projeto (derivadas do briefing e do material)

1. Mobile primeiro: 360×640 px (Android de entrada) como base; 390×844 como alvo comum; rede lenta. INFERÊNCIA.
2. Peso: sem fonte pesada: no máximo 2 famílias, 4 arquivos; WebGL só se o ganho for decisivo.
3. Sem muro de consentimento (não rastrear).
4. Todo alerta traz **fonte** e **"o que isto não prova"**; nunca afirmar culpa.
5. "Se tudo é alerta, nada é alerta": só ~3% "prioridade máxima" e ~18% "relevante" (briefing §3). A cor de alerta tem de aparecer **pouco**.
6. Teste de acentos em toda fonte: `Ação, coincidência, órgão público, Conceição, São João d'Oeste, ônibus, Nº 12/2024, R$ 1.234.567,89`. Todas as famílias abaixo existem no Google Fonts (VERIFICADO: a API de CSS respondeu 200 para cada uma) e o subconjunto "latin" cobre português (FONTE: conhecimento geral); **o teste visual de acentos em tela ainda precisa ser feito** (marcado em cada território).
7. Acessibilidade: contraste ≥ 4,5:1 no texto; nenhuma informação só por cor (usar forma/posição); alvos de toque ≥ 44 px; textura nunca atrás de texto corrido.

---

## 5. Cinco territórios de direção de arte

Convenção de cada brief: **Conceito** → **Tipografia** → **Cor** → **Grade mobile** → **Linguagem do gráfico** → **Gesto de assinatura** → **Movimento** → **Tom de voz** → **3 telas** → **Referências** → **Riscos** → **Custo** → **Acessibilidade** → **Identidade e compartilhamento**.

Vocabulário comum a todos: *valor* = quanto dinheiro; *período* = quando; *ligação* = empresa ↔ órgão; *coincidência* = a sobreposição dos dois eixos de tempo (restrição × pagamento) do documento anterior.

---

### Território 1 — EXTRATO (radicalmente tipográfico e funcional; sem textura, sem ilustração)

**Conceito.** O Radar é um **extrato de conta do dinheiro público**: linhas, valores, datas, fontes. A beleza vem de uma tipografia severa e de uma **diagramação de documento oficial bem feito**, em que cada linha é auditável. O alerta é um **lançamento que não fecha**. (Derivado do material: pagamentos, períodos, fontes.)

**Tipografia.**
- Títulos/UI: **Schibsted Grotesk** (grotesca de origem jornalística, 400–900; existe no Google Fonts, VERIFICADO 200).
- Valores, datas, CNPJ, códigos: **Martian Mono** (VERIFICADO 200; mono larga e tabular, legível em 12–14 px) ou, se pesar, **JetBrains Mono**.
- Escala (mobile): 12/14/16/20/28/40 px (razão ~1,3); manchete 28/32 px peso 800, `letter-spacing` −1%; valor principal 40 px em mono 500, **sem condensar** (evita "número gigante condensado" do Politicômetro).
- Teste de acentos: a fazer em tela; a Schibsted tem os diacríticos latinos completos (INFERÊNCIA; confirmar "ç ã õ ê Ç Ã" em peso 800).

**Cor.** **2 cores + papel**: tinta preta `#111`, papel branco-frio `#FAFAFA` (não creme), e **uma só cor de alerta** (vermelho-carimbo `#D7261E`, contraste ≈ 5:1 sobre branco, cálculo meu) reservada **exclusivamente** para "coincidência". Modo escuro: papel `#0E0E0E`, tinta `#F2F2F2`, vermelho `#FF5A4F`. Nada mais ganha cor.

**Grade mobile.** Coluna única de 16 px de margem; linhas de 56–64 px de altura (alvo de toque) separadas por filete de 1 px; **rótulo à esquerda em 12 px caixa-alta mono, valor à direita alinhado por vírgula** (colunas tabulares). Navegação: barra inferior com 4 rótulos em texto (sem ícones): Hoje · Minha cidade · Buscar · Fontes.

**Linguagem do gráfico.**
- *Valor*: **o próprio número em mono** + uma barra de 4 px com comprimento proporcional (escala logarítmica explícita quando varia 100×; rótulo "escala log").
- *Período*: **régua de linha única** (um filete com ticks anuais) e uma faixa grossa (8 px) para a restrição.
- *Ligação*: **duas linhas de texto unidas por um colchete** ("Empresa X ⟷ Órgão Y · 14 pagamentos · R$ …"), não grafo.
- *Coincidência*: a faixa da restrição e os pontos de pagamento caem na régua; **só os pagamentos dentro da faixa viram vermelho**.

**Gesto de assinatura.** **"O lançamento que não fecha"**: toda ficha termina com um **fechamento de conta** em duas linhas: `Pagamentos durante a restrição ........ R$ X` e `O que isto não prova ........ texto`. O "não prova" tem o mesmo peso do número.

**Movimento.** Quase nenhum: números "contam" de 0 ao valor em 400 ms ao entrar (uma vez); a régua desenha-se da esquerda à direita em 600 ms; `prefers-reduced-motion` desliga.

**Tom de voz.** Seco, em frase afirmativa e curta: "Pagou R$ 2,1 mi a empresa impedida de contratar. Isto não prova irregularidade. Fonte: CEIS, PNCP."

**Três telas em palavras.**
1. *Início*: topo com uma frase ("1.581 sinais. 48 pedem atenção hoje."), a **busca** logo abaixo, e uma lista de **5 lançamentos** ordenados por prioridade; cada linha: tipo mono pequeno ("R11 · PAGAMENTO × PUNIDA"), nome, valor, e a régua de 12 px de altura com a faixa. Sem foto, sem ícone.
2. *Ficha de alerta*: cabeçalho com tipo e data da fonte; **uma frase**; régua grande (a coincidência) ocupando a largura; tabela "pagamentos" em mono; bloco **"O que isto não prova"** em caixa de contorno 2 px; botão "Fonte" e "Compartilhar" no rodapé fixo.
3. *Cidade*: busca por município; resultado em **lista ordenada** (não mapa): "Município · nº de sinais · valor sob atenção"; linha selecionada expande a lista de alertas da cidade; mapa pequeno opcional abaixo.

**Referências reais.** OpenSanctions (faixa mono de cobertura, VERIFICADO), GovTrack (frase de função, VERIFICADO), extratos bancários e notas fiscais (INFERÊNCIA), ProPublica (autoria e rigor, VERIFICADO), Quinto Elemento (régua fina, VERIFICADO).

**Riscos.** Frio e "planilha"; precisa de qualidade tipográfica excelente para não parecer protótipo cinza (o protótipo anterior já era cinza e foi rejeitado, ver `DIRECAO_DE_ARTE.md` §Rodada 2). Mitigação: **vermelho com disciplina**, microtipografia, um logotipo forte.

**Custo.** CSS + SVG simples; sem bibliotecas novas. Baixo (1x).

**Acessibilidade.** Contraste alto; informação em texto, não só cor (o "não prova" é texto); mono tabular ajuda leitura de números; alvo de toque 56 px; leitor de tela lê a linha como frase.

**Identidade/compartilhamento.** Ícone do app: o **fechamento da conta** reduzido: um quadrado preto com **uma faixa vermelha** atravessando. Imagem WhatsApp (1080×1350 e 1200×630): a ficha em formato de **comprovante**: tipo, nome, valor, régua com a coincidência em vermelho, linha "O que isto não prova", URL.

---

### Território 2 — SOBREPOSIÇÃO (arte concreta em vetor; sem textura, sem ilustração)

**Conceito.** A coincidência é **geometria**: dois planos (restrição e pagamentos) que se cruzam; a interseção é a única cor viva. O Radar é uma **composição de planos sobre uma grade**, no espírito concreto/neoconcreto (lógica, não obra).

**Tipografia.**
- **Archivo** (variável, eixos de largura e peso; VERIFICADO 200): extra-largo em 800 para rótulos de plano, normal para texto.
- Corpo: **Atkinson Hyperlegible** (desenhada para legibilidade; VERIFICADO 200). Dois tamanhos de números: 32 px extra-largo para valores, 14 px tabular.
- Teste de acentos: a fazer; Atkinson Hyperlegible tem boa cobertura latina (INFERÊNCIA).

**Cor.** Quatro cores com **função fixa**: (1) tinta `#14181F`; (2) papel `#F3F3F1` (cinza-claro neutro, sem calor); (3) **azul-plano** `#1F3FFF` = o período da restrição (sanção, mandato, abertura); (4) **amarelo-plano** `#FFD400` = o dinheiro pago. **A interseção, calculada em CSS com `mix-blend-mode: multiply`, resulta num marrom-verde-escuro; sobre ela pousa o vermelho `#E0301E`**, único alerta. Aviso: azul + amarelo evoca bandeira e partido; testar neutralidade (INFERÊNCIA/risco).

**Grade mobile.** Módulo de 8 px, **colunas de 4**; cada cartão é um retângulo sem cantos arredondados; planos sangram até a borda da tela. Rolagem vertical; navegação por **tabs de texto grandes** no topo (Hoje, Cidade, Buscar).

**Linguagem do gráfico.**
- *Valor*: **área de um retângulo** (a largura = período, a altura = valor); em lista, só a altura.
- *Período*: **largura do plano azul**.
- *Ligação*: dois retângulos de cores diferentes **encostados** (empresa em um, órgão em outro) com a área comum rotulada.
- *Coincidência*: a interseção azul × amarelo, com a quantia dentro, em vermelho.

**Gesto de assinatura.** **A cruz de planos**: azul (horizontal, largo) cortando amarelo (vertical, em barras). O produto inteiro é essa leitura. Uma ficha = uma composição.

**Movimento.** Os planos **deslizam até se sobrepor** (500 ms, ease-out) ao abrir a ficha; ao tocar um pagamento, o amarelo daquele pagamento acende e o valor sobe. Sem parallax.

**Tom de voz.** Geométrico e explicativo: "Aqui as duas coisas coincidem."

**Três telas.**
1. *Início*: **um plano-manchete**: "48 coincidências hoje" sobre faixa azul, abaixo uma pilha de 5 retângulos (alertas), cada um com seus dois planos miniatura.
2. *Ficha*: composição em tela cheia: eixo do tempo horizontal, plano azul (restrição), barras amarelas (pagamentos), interseção em vermelho; texto embaixo; o "não prova" em retângulo preto com texto branco.
3. *Cidade*: **treemap** (retângulos proporcionais ao valor sob atenção) dos municípios do estado; toque expande para lista.

**Referências reais.** FONTE (conhecimento geral, não reverificado): Ruptura/Waldemar Cordeiro, Lygia Pape. VERIFICADO: Windy (cor = valor), The Pudding (a miniatura é o dado). INFERÊNCIA: treemaps de dinheiro.

**Riscos.** Azul + amarelo = bandeira/partido; a leitura "bonita demais" pode esconder a regra de ouro "nunca afirmar culpa"; treemaps têm leitura ruim de rótulos em 360 px.

**Custo.** SVG/CSS + `mix-blend-mode`; treemap com D3 (~20 kB). Médio (1,5x).

**Acessibilidade.** Daltonismo: azul/amarelo é seguro (eixo azul-amarelo preservado em deuteranopia); **a interseção precisa de padrão/rótulo**, não só cor; alt text gerado da regra.

**Identidade/compartilhamento.** Ícone: **dois retângulos cruzados** (azul/amarelo) com o quadrado de interseção em vermelho. WhatsApp: a composição em quadrado, número em extra-largo, URL.

---

### Território 3 — PLACA (sinalização e atenção; textura mínima)

**Conceito.** O Radar é **sinalização do dinheiro público**: a linguagem de "atenção, obra, desvio" que todo brasileiro lê sem aprender. Um alerta é uma **placa de advertência**: forma + palavra, nunca pergunta. Dá o tom "sério e cortante" por uma via que o povo já conhece. (INFERÊNCIA: não verifiquei o manual de sinalização.)

**Tipografia.**
- Placas e rótulos: **Overpass** (derivada da Highway Gothic; FONTE: conhecimento geral; o Overpass Mono respondeu 200 em teste, **a família Overpass comum não foi testada**). Alternativa verificada: **Archivo** 700–900.
- Texto corrido: **Public Sans** (VERIFICADO 200; usada pelo GovTrack, VERIFICADO).
- Escala: placas em 20/28 px caixa-alta 800; corpo 16 px; números em 32 px tabular.
- Teste de acentos: caixa-alta com acento ("AÇÃO", "ÓRGÃO") precisa ser conferida (altura do til).

**Cor.** Três: **preto `#111`, amarelo-advertência `#FFC400`, branco**. Amarelo = "atenção" apenas em placa de alerta; o resto é preto e branco. Prioridade máxima: placa cheia amarela; relevante: borda amarela; contexto: sem amarelo. Isto resolve o "tudo é alerta": o amarelo é escasso por regra.

**Grade mobile.** Coluna única; **placas retangulares com cantos de 4 px** e borda preta de 3 px, sem rebites nem outra decoração. Navegação: barra inferior de 4 abas com texto.

**Linguagem do gráfico.**
- *Valor*: número grande dentro da placa ("R$ 2,1 mi").
- *Período*: **fita zebrada** (listras diagonais amarelo/preto) para o intervalo da restrição, como fita de isolamento; pagamentos como **pinos** pretos.
- *Ligação*: placa "EMPRESA → ÓRGÃO" com seta.
- *Coincidência*: pinos que caem dentro da fita zebrada viram **blocos cheios** (o resto fica vazio).

**Gesto de assinatura.** **A fita zebrada** como faixa da restrição. Reconhecimento instantâneo.

**Movimento.** A placa "cai" 8 px com leve ressalto (200 ms) ao aparecer na lista; a fita zebrada anda em diagonal de forma lenta no alerta de prioridade máxima (desligável).

**Tom de voz.** Imperativo curto: "ATENÇÃO. Empresa impedida recebeu R$ 2,1 mi. Isto não prova irregularidade."

**Três telas.**
1. *Início*: grande placa amarela "HOJE: 48 PEDEM ATENÇÃO"; embaixo placas menores; busca como placa branca.
2. *Ficha*: placa-título; fita zebrada com pinos; "O QUE ISTO NÃO PROVA" como placa branca de contorno preto; fonte.
3. *Cidade*: lista de municípios com **número de placas** (contagem) e a mais grave primeiro; mapa abaixo com **pinos** amarelos.

**Referências reais.** INFERÊNCIA/FONTE geral: sinalização de trânsito, placas de obra, fita de isolamento; VERIFICADO: GovTrack/USAspending (clareza institucional), Lupa (cor ácida marcando categoria, VERIFICADO).

**Riscos.** Faixa zebrada + amarelo pode parecer "alarmista" e violar o princípio "nunca afirmar culpa"; é preciso moderar o tom (placa de **atenção**, nunca de **perigo/proibido**). Pode lembrar autoridade de trânsito; evitar símbolos oficiais. Amarelo sobre branco falha no contraste: sempre sobre preto ou com texto preto.

**Custo.** CSS (`repeating-linear-gradient`) + SVG. Baixo (1x).

**Acessibilidade.** Preto sobre amarelo ≈ 13:1 (cálculo meu); fita zebrada não carrega informação sozinha (o rótulo diz o período); movimento opcional.

**Identidade/compartilhamento.** Ícone: **placa amarela com ponto de exclamação não** (clichê); usar a **fita zebrada cortada em diagonal** e um ponto. WhatsApp: placa amarela com a frase, valor e fonte; fundo preto.

---

### Território 4 — LAMBE (cartaz de rua em duas tintas; depende de textura/impressão)

**Conceito.** O Radar é **o cartaz colado no poste**: público, barato, impossível de ignorar, feito por quem quer que se saiba. Dois tintas (preto + uma cor) sobre papel, tipografia gigante, **sobreposição de cartazes** como estrutura.

**Tipografia.**
- Cartaz: **Anton** ou **Big Shoulders Display** (VERIFICADO 200 ambas), 48–72 px caixa-alta, tracking −1%; alternativa brasileira: **Londrina Solid** (VERIFICADO 200; já citada no documento anterior).
- Corpo: **Archivo** 16 px (VERIFICADO).
- Teste de acentos: Anton em caixa-alta com "Ã" e "Ç" precisa checagem (corta o acento em linhas apertadas).

**Cor.** Papel **branco-azulado `#F4F6F7`** (evitar creme, rejeitado pelo cliente) + tinta preta + **uma tinta fluorescente** (rosa-choque `#FF2E6E` ou laranja-urgente `#FF5B14`) em **sobreposição por multiplicação** (`mix-blend-mode: multiply`), sugerindo a impressão em risografia/serigrafia. A cor fluorescente = coincidência.

**Grade mobile.** **Cartazes empilhados**: cada alerta é um cartaz retangular em largura total, **ligeiramente rotacionado (±0,6°)** só nas bordas, sobrepostos 12 px uns aos outros; texto não rotacionado.

**Linguagem do gráfico.** Barras em **tinta cheia** (sem arredondamento), valores em tipografia de cartaz; período = largura de uma faixa fluorescente atrás das datas; ligação = **seta grossa desenhada** (traço pincel em SVG); coincidência = fluorescente que sobrepõe o preto, resultando em cor escura.

**Gesto de assinatura.** **O cartaz que cobre o anterior**: ao rolar, o novo cartaz **cobre** o anterior (efeito de colar).

**Movimento.** "Colar": cartaz entra com 4 px de deslocamento e uma leve sombra de cola (200 ms). Ruído de granulação estático (não animado).

**Tom de voz.** Gritado, mas factual: "R$ 2,1 MILHÕES. PARA QUEM NÃO PODIA RECEBER."

**Três telas.**
1. *Início*: título de cartaz "O DINHEIRO PÚBLICO NÃO SOME. ÀS VEZES, COINCIDE."; pilha de cartazes.
2. *Ficha*: cartaz grande; a faixa fluorescente; o "não prova" em **etiqueta branca colada** no rodapé.
3. *Cidade*: **mural**: cartazes pequenos de cada alerta da cidade, em grade 2×N.

**Referências reais.** FONTE (conhecimento geral): lambe-lambe, cartaz sindical, risografia; VERIFICADO: Aos Fatos (adesivos amarelo/ciano), Quinto Elemento (duotom amarelo/preto), SCMP (capas ilustradas), The Pudding (mão).

**Riscos.** O maior de todos: **cartaz político/sindical → leitura partidária**; o alarmismo ameaça a credibilidade; texturas pesam; texto sobre papel granulado piora a leitura. Alto risco de "kitsch de rua". Mitigação: granulação só nas bordas, nunca atrás do texto.

**Custo.** CSS + SVG filtros (`feTurbulence`) ou imagens leves; 2x. Pode esquentar celular com blend + filtro em listas longas.

**Acessibilidade.** Rosa fluorescente sobre branco falha no contraste: **texto sempre preto**; rotação pequena evita fadiga; animações desligáveis.

**Identidade/compartilhamento.** Ícone: **um cartaz** (retângulo com canto dobrado) em rosa sobre preto. WhatsApp: ótimo: a imagem é o cartaz, naturalmente compartilhável.

---

### Território 5 (reserva) — CORDEL DISCIPLINADO (já testado; só se o cliente quiser reabrir)

**Conceito.** Preto, branco e um vermelho de carimbo, goiva e hachura apenas na **faixa da coincidência**; tipografia de cartaz.
**Tipografia.** Londrina Solid (títulos) + Newsreader ou Public Sans (corpo) (ambas VERIFICADO 200).
**Posição:** **não recomendado**: o cliente rejeitou o protótipo (briefing §2); o risco de folclore/kitsch é alto (ver seção 3). Se reaberto, manter a goiva restrita ao gesto e nada de ornamento.
**Custo:** 2x (SVG com rugosidade). **Acessibilidade:** textura nunca em texto corrido.

---

## 6. Quadro comparativo

| Critério | 1 Extrato | 2 Sobreposição | 3 Placa | 4 Lambe | 5 Cordel |
|---|---|---|---|---|---|
| Depende de textura/ilustração | Não | Não | Quase nada | Sim | Sim |
| Tom "sério e cortante" | Muito | Médio | Alto (risco alarmista) | Alto (risco partidário) | Médio |
| Facilidade de uso (um polegar) | Máxima | Boa | Muito boa | Média | Média |
| Risco de "slop de IA" | Baixo | Baixo-médio | Baixo | Médio | Médio (já rejeitado) |
| Gesto da coincidência | Régua + vermelho | Interseção de planos | Fita zebrada | Cartaz sobreposto | Faixa entalhada |
| Custo de implementação | 1x | 1,5x | 1x | 2x | 2x |
| Brasilidade | Documento/extrato | Concreto | Sinalização | Lambe | Cordel |
| Risco de credibilidade | Baixo | Médio (bonito demais) | Médio | Alto | Médio |

---

## 7. Recomendação

**Escolha: construir sobre o Território 1 (EXTRATO), incorporando a fita de tinta única do Território 3 e a lógica de interseção do Território 2.** Em outras palavras: *a diagramação do extrato, o vermelho como único sinal de coincidência, e a interseção de planos como gesto*. Justificativa:

1. **Credibilidade primeiro.** O briefing pede que "quem faz algo errado tenha medo de aparecer". O que assusta e convence é **precisão**, não estilo: o jurado do Sigma elogia métodos replicáveis e provas à vista (FONTE). O Extrato é o território em que cada linha é auditável, e "o que isto não prova" tem o mesmo peso do valor.
2. **Facilidade.** Lista + busca + barra inferior em texto: nada a aprender. É também o território que menos depende de ilustração e que mais perdoa um dado imperfeito.
3. **Anti-slop real, não aparente.** Evita as marcas que o cliente rejeitou (creme, serifa da moda, cartões arredondados, pílulas, ícones, número condensado). **Aviso honesto:** o protótipo cinza já se aproximava disto e foi rejeitado. A diferença proposta é *(a)* uma tipografia com mais personalidade (Schibsted + mono larga), *(b)* um vermelho com função única e *(c)* o fechamento de conta como gesto. Se o cliente rejeitar "cinza + mono" pela segunda vez, o caminho de reserva é o Território 4 (Lambe) em versão contida.
4. **Custo e escala.** CSS/SVG; cada alerta gera sua própria imagem (comprovante) sem ilustrador.

**O que testar primeiro (com usuários), em ordem:**
1. **Teste de 5 segundos** na tela inicial, 3 variantes (Extrato, Placa, Lambe): "o que este site faz?" e "qual a sensação (escolha 3 palavras)?". Meta: ≥ 80% descrevem corretamente a função; palavras "sério/confiável" em ≥ 60%.
2. **Tarefas de uso em celular real** (Android de entrada, rede 3G simulada): (a) achar o alerta mais grave de hoje; (b) achar os alertas da sua cidade; (c) explicar com as próprias palavras o que um alerta **não** prova; (d) compartilhar no WhatsApp.
3. **Compreensão da coincidência**: mostrar a régua sem legenda e perguntar "onde está o problema?".

**Como medir "agradável e fácil":**
- **Tempo até a primeira tarefa concluída** (alvo: ≤ 30 s para achar a cidade).
- **Taxa de sucesso sem ajuda** (alvo: ≥ 85%) e erros por tarefa.
- **SUS** (System Usability Scale, 10 perguntas; alvo ≥ 80, FONTE: escala padrão da área).
- **Compreensão do "não prova"**: ≥ 90% acertam que o alerta não é acusação (a métrica mais importante para a regra de ouro nº 1).
- **Teste de preferência** entre variantes + comentário livre; **taxa de compartilhamento** (ação 4).
- Amostra: **6 a 8 pessoas por rodada** (a literatura de usabilidade indica que poucos usuários revelam a maioria dos problemas, FONTE geral), incluindo pessoas de baixa escolaridade, 50+ e usuários de Android de entrada. Repetir a rodada após os ajustes.

**Próximo passo (sem alterar produto ainda):** desenhar as 3 telas do Extrato em protótipo HTML estático (início, ficha com régua da coincidência, cidade) em 360 px com acentos reais, e uma imagem de compartilhamento, para a rodada 1.

---

## 8. Lacunas e como seriam fechadas

- Reuters, Süddeutsche, Berliner Morgenpost, Bloomberg, Folha, Washington Post, TheyWorkForYou: não analisados (bloqueio/erro). Tentar em outra sessão, em janela de 390 px, ou com capturas manuais do cliente.
- Information is Beautiful 2025–26 e DJA: sem lista de vencedores por ano; abrir página a página.
- Brasileiros premiados em visualização: apenas *Cerrado* (Ambiental Media, Sigma 2026) citado em texto; **não abri o projeto**. Fazer em seguida.
- A cultura visual brasileira (seção 3) é conhecimento geral; antes de citar obra/autor em material público, checar a ficha de cada um.
- Todas as famílias tipográficas: confirmadas no Google Fonts (disponibilidade); falta o teste visual de acentos em tela e o teste de peso (kB) por arquivo.

## 9. Fontes consultadas (acesso em 08/11/2026)
https://www.propublica.org · https://pudding.cool · https://ourworldindata.org · https://www.opensanctions.org · https://www.usaspending.gov · https://www.theguardian.com/international · https://www.windy.com · https://www.govtrack.us · https://www.icij.org · https://www.occrp.org/en · https://www.flightradar24.com · https://www.scmp.com/infographic · https://www.nucleo.jor.br · https://www.aosfatos.org · https://basedosdados.org · https://www.atlasbrasil.org.br · https://www.ft.com/visual-and-data-journalism · https://correctiv.org · https://www.ftm.eu · https://www.nytimes.com/spotlight/graphics · https://quintoelab.org · https://lupa.news · https://www.informationisbeautifulawards.com/showcase · https://www.sigmaawards.org (2026 winners) · https://www.awwwards.com/websites/government/ · https://fonts.googleapis.com (checagem de disponibilidade de famílias).
