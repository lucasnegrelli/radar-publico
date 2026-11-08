# Direção de arte do Radar Público (documento de trabalho)

Estado: **pesquisa e conceito, sem pele final**. As três telas de teste (Cédula, Boletim, Carta) foram descartadas: eram "papel creme + serifa + cartões", o mesmo vocabulário genérico que qualquer gerador produz. Este documento define o que falta antes de desenhar de novo.

## 1. Por que as primeiras tentativas deram errado (diagnóstico)
- Partiram de um **estilo** ("papel de dinheiro", "jornal", "atlas") e não do **material** do produto.
- Usaram os mesmos ingredientes de sempre: fundo creme, serifa de moda, cartões arredondados, pílulas de filtro, ícones de traço. É o "visual de IA" de 2025–26.
- Misturaram identidade com decoração (guilhoche, linhas de nível): enfeite que não significa nada.
- Pensaram a tela como página de site, não como **ferramenta de bolso** (celular, polegar, WhatsApp, rede ruim).

## 2. O que a pesquisa de referências mostrou (e o que não mostrou)
Olhado de verdade (capturas): The Pudding, Politicômetro, Flightradar24, Windy, OpenSanctions, ICIJ Offshore Leaks, Downdetector, Liveuamap, World Monitor.

| Referência | O que faz bem | O que levar |
|---|---|---|
| **The Pudding** | Personalidade inconfundível; cada história tem seu mundo de cor; a miniatura É o dado | Identidade nasce de uma voz, não de uma paleta |
| **Windy / Flightradar24** | O mapa é a tela; controles mínimos; sempre há algo "ao vivo" para tocar | Poucos controles, resposta imediata |
| **Downdetector** | Uma frase, dois números, um gráfico vivo; entende-se em 3 segundos | Hierarquia brutal |
| **ICIJ Offshore Leaks** | Aviso legal antes da busca; busca em primeiro lugar | Credibilidade: o que o dado NÃO prova vem antes |
| **OpenSanctions** | Título curto, busca grande, números de cobertura | Confiança por transparência de fonte |
| **Politicômetro** | Pergunta como navegação (Quem governa, Contas, Obras, Dinheiro que chegou); diretório de todos; mobile | Navegar por perguntas do cidadão |

Limite honesto: as buscas por vencedores de prêmios (Information is Beautiful, SND, Awwwards) não trouxeram listas utilizáveis de 2025–26, e eu não consegui abrir cases premiados suficientes para chamar isto de pesquisa de nível de premiação. O que está acima é leitura de produtos reais, não uma meta-análise de prêmios.

## 3. Princípios (o que um bom designer exigiria)
1. **Conceito vem do material.** O que o Radar tem de próprio: dinheiro público que corre até alguém, e uma **coincidência** que não deveria existir (pagamento dentro de uma punição, doador que vira fornecedor, contrato de 100x o capital).
2. **Um gesto de assinatura.** Uma imagem que só o Radar tem e que se repete em tudo.
3. **Uma pergunta por tela.** O que está acontecendo? E na minha cidade? Quem é essa pessoa ou empresa? Quanto custa?
4. **Credibilidade desenhada.** Prioridade só para o que pesa; "o que isto não prova" sempre visível; fonte a um toque.
5. **Bolso primeiro.** Polegar, uma mão, 360 px, rede lenta, compartilhável no WhatsApp com imagem própria. Desktop é ampliação, não o contrário.
6. **Sem decoração que não significa.** Cada elemento visual carrega informação.
7. **Tipografia com caráter e legibilidade em português** (acentos, números tabulares).

## 4. Anti-slop (lista de recusas)
Fundo creme/papel · serifa de moda no título · cartões arredondados com sombra · pílulas de filtro por toda parte · emojis como ícones · gradientes roxo/azul · "glassmorphism" · ícones de traço genéricos · números gigantes condensados (já é do Politicômetro) · texturas de nota/atlas.

## 5. Hipótese de conceito: "A coincidência"
O gesto de assinatura: **dois eixos de tempo que se sobrepõem**.
- Em cada alerta, uma faixa mostra o período da restrição (sanção, mandato, abertura da empresa) e marcas mostram os pagamentos. O sinal é **onde as duas coisas se tocam**.
- A sobreposição é a única coisa que ganha a cor de alerta. Todo o resto é neutro.
- O mesmo vocabulário serve a todos os alertas: punição × pagamento, mandato × contrato, empresa nova × contrato, doação × fornecimento.
- Vira também o selo de compartilhamento (imagem gerada) e a marca.

Isto é uma hipótese a testar em cinza, não uma pele pronta.

## 6. Processo daqui para frente
1. Você reage ao conceito e ao tom (ver perguntas na conversa) e manda 3 a 5 referências que dão a sensação certa (qualquer coisa: site, app, cartaz, embalagem, filme).
2. Eu desenho **em escala de cinza** a tela inicial e a ficha de um alerta, com o gesto da coincidência, só com tipografia e espaço.
3. Só depois entram cor, tipo final e movimento.
4. Teste em celular real, com pessoas não técnicas, antes de refazer as demais telas.
5. PWA instalável e imagem de compartilhamento por alerta.


## 7. Rodada 2: pesquisa de referências e nova hipótese (cordel / xilogravura)
O que vi de fato: vencedores recentes do Awwwards (Site of the Year: mundos ilustrados e em 3D, como Messenger/abeto, um site de cachorro ilustrado à mão, Igloo), o showcase do Information is Beautiful 2024 (formas feitas sob medida para o dado, não gráficos de biblioteca) e The Pudding (personalidade e cor por história). Leitura de apoio: Data Humanism (Giorgia Lupi: abraçar a complexidade, sair dos padrões, trazer contexto, lembrar que o dado é imperfeito) e as tendências de 2025–26 (volta do feito à mão, tipografia como herói, reação ao visual "polido e genérico").

Conclusão: o que escapa do genérico é (a) **um mundo assumido até o fim**, (b) **marca de mão** (não CSS limpo) e (c) **forma própria do dado**. O "estilo" nunca basta.

Hipótese: **Cordel e xilogravura** como linguagem do Radar. O cordel é a literatura popular que denuncia e informa; a xilogravura é preto sobre papel, entalhe, hachura. Casa com o tom (sério e cortante), com o gesto da coincidência (a faixa entalhada com goiva) e com o Brasil como ponto de partida. Referências brasileiras a estudar: J. Borges e Gilvan Samico (xilogravura de cordel), Lygia Pape (Tecelares), Athos Bulcão (azulejos de Brasília), Waldemar Cordeiro (arte concreta). Fonte de cartaz: Londrina Solid (desenhada no Brasil a partir de letras populares).

Alternativa a testar se esta não convencer: **Concreto** (geometria e planos sobrepostos da arte concreta brasileira), em que a coincidência vira composição de planos.

Riscos: virar folclore/kitsch (evitar ornamento; manter preto, branco, um vermelho de carimbo e muita disciplina), e acessibilidade (textura nunca em texto corrido).
