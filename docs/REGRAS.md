# Regras de alerta (metodologia)

Um alerta é um **ponto de atenção**: um cruzamento de dados públicos que saiu do esperado. Não é acusação nem veredito. Cada alerta no site mostra os critérios que acenderam, o que foi descartado e o que **não** prova.
Limiares exatos: ver `alertas/*.sql` e os scripts indicados. Prioridade **alta, média ou baixa** mede quão forte é o sinal e quão pouca dúvida resta, não a gravidade do ato.

| Código | O que procura | Critérios principais | Falsos positivos conhecidos | Onde |
|---|---|---|---|---|
| R01 | Cota parlamentar paga a empresa punida | empresa no CEIS/CNEP **com sanção que impede contratar** (multa e publicação não valem) e que alcança o Congresso | punição restrita a outro órgão; homônimo | `alertas/01` |
| R02 | Contrato com empresa punida | punição vigente na assinatura e com alcance sobre o órgão contratante (esfera e UF) | punição suspensa em juízo; contrato anterior só republicado | `alertas/02` |
| R03 | Empresa nova com contrato grande | menos de 180 dias de vida e contrato ≥ R$ 200 mil, fora consórcio, SPE, fundação, estatal | empresa criada para obra específica | `alertas/03` |
| R04 | Contrato gigante para empresa pequena | contrato de 50 a 1.000 vezes o capital social, entre R$ 500 mil e R$ 300 mi | valor digitado errado; plurianual | `alertas/04` |
| R05 | Doador do prefeito virou fornecedor | sócio doou à campanha de 2024 e a empresa contratou com a prefeitura depois da posse | doação legal de quem já era fornecedor | `alertas/05` |
| R06 | Possível fracionamento | 4 ou mais contratos de R$ 15–70 mil no mesmo trimestre, somando ≥ R$ 200 mil, **só dispensa** | compras de naturezas diferentes | `alertas/06` |
| R07 | Fornecedor concentra a prefeitura | ≥ 50% do valor contratado no ano, fora serviços contínuos típicos e entes especiais | mercado local pequeno | `alertas/07` |
| R08 | Sócio em país de sigilo ou tributação favorecida | sócio sediado em jurisdição das listas de referência (níveis 1 e 2) e contratos ≥ R$ 300 mil | multinacional legítima com holding | `alertas/08` |
| R09 | Emenda para entidade com ponto de atenção | entidade privada com ≥ R$ 100 mil de emendas **e** sanção, ou CEPIM, ou matriz aberta há < 1 ano, ou valor > 50× o capital | sanção posterior ao pagamento; ONG nova legítima | `emendas.py` |
| R10 | Político eleito sócio de fornecedor | nome completo + 6 dígitos do CPF coincidem; contratos ≥ R$ 100 mil desde 2025; alta se depois da posse | sócio já saiu (a base não tem data de saída) | `politicos_socios.py` |
| R11 | Pagamento federal a empresa sancionada | pagamento no mês em que constava punida com alcance sobre a União | pagamento de entrega anterior à sanção | `despesas_federais.py` |
| R12 | Servidor federal sócio de fornecedor | servidor ativo (SIAPE) coincide por nome + CPF parcial; empresa privada com contratos federais; alta se administra | atividade privada autorizada; fundações de apoio (excluídas) | `servidores.py` |
| RF01 | Banco em crescimento acelerado e alavancado | captação ≥ R$ 5 bi, +50% em 12 meses, ativo/PL ≥ 10, sustentado | banco em expansão legítima | `risco_financeiro.py` |

## Nota de relevância (aba Destaques)
`score = prioridade (100/40/0) + 14·log10(valor) + 45 se há sinais combinados + peso do tipo + bônus para político, emenda, sanção/CEPIM e novidade`. Máximo de 8 por tipo e 1 por empresa entre os 40 destaques. Pesos do tipo estão em `web/main.js` (`PESO_R`).

## Pendente (ver ROADMAP)
Recalibrar prioridades depois que as novas fontes estiverem integradas, com taxa de falso positivo medida por amostra conferida.
