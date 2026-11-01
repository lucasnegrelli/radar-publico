# Tipologias de fraude financeira com dinheiro público

Padrões extraídos de caso público amplamente noticiado (colapso de um banco médio, 2025/2026).
Aqui só entram **padrões**, nunca nomes de pessoas ou empresas: o sistema aponta comportamento,
não acusa ninguém. Cada tipologia vira regras de detecção em `regras/`.

| # | Padrão observado | Sinal público detectável | Fonte |
|---|---|---|---|
| T1 | Produto de captação com rentabilidade muito acima do mercado, lastreado em ativo ilíquido ou inexistente | Emissor cuja remuneração/captação cresce fora da curva do setor | BCB (IF.data, balancetes) |
| T2 | Fundos (FIDC, FIP) usados como canal de circulação e ocultação do dinheiro | Mesma administradora/gestora ligada a muitos veículos que se pagam entre si | CVM (cadastro e informes de fundos) |
| T3 | Banco público compra carteiras de crédito de baixa qualidade de um banco privado pequeno | Compra de carteira concentrada num cedente, valor desproporcional | Balanços do banco público, Portal da Transparência |
| T4 | Fundos de previdência de servidores (RPPS) concentrados num único emissor | % da carteira do RPPS num emissor acima do normal | CADPREV (Previdência) |
| T5 | Vantagem indevida paga via fundo -> sociedade de fachada (SPE/S.A.) em nome de interposta pessoa -> compra de bem | PJ recém-criada, capital alto, sócio sem perfil compatível, compra de imóvel logo após aporte de fundo | CNPJ (Receita), cartórios, CVM |
| T6 | Pagamentos a empresa sem prestação de serviço identificável, ligada a parente de agente público | Fornecedor com sócio parente de agente; CNAE incompatível com o que recebeu | CNPJ, TSE, Portal da Transparência |
| T7 | Atuação legislativa (emenda, relatoria) em favor do mesmo grupo econômico | Emendas/proposições que beneficiam um setor, cruzadas com doadores e fornecedores | APIs Câmara/Senado, TSE |
| T8 | Crédito consignado para servidores como ativo-base de cessões | Cessão/venda de carteira de consignado de ente público | Diários oficiais (Querido Diário), contratos |

## Como isso vira alerta (princípio SIEM)
Evento (dado bruto) -> Regra (padrão acima) -> Alerta (gravidade + explicação em linguagem simples + fonte) -> Caso (alertas ligados à mesma entidade).
