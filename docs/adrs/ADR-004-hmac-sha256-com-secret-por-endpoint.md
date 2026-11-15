# ADR-004: Autenticação das entregas com HMAC-SHA256 e secret por endpoint, rotacionável com carência de 24h

**Status:** Aceito
**Data:** 2026-11-15 (decisão tomada na reunião técnica de quinta-feira, [09:22])
**ADRs relacionadas:** [ADR-005](ADR-005-entrega-at-least-once-com-x-event-id.md)

---

## Contexto

Os webhooks são apenas de saída: o OMS envia, e o cliente recebe ([09:02] Marcos, [09:03] Sofia). As entregas levam dados de pedido para um endpoint fora da nossa infraestrutura. O cliente precisa conseguir verificar que a requisição veio do OMS e que o corpo não foi adulterado no caminho ([09:19] Sofia).

Há histórico de incidente: um cliente já vazou um secret em log da própria aplicação ([09:22] Diego).

## Fatores de decisão

- Autenticidade e integridade verificáveis pelo cliente ([09:19] Sofia).
- Padrão de mercado, com biblioteca disponível para qualquer cliente ([09:20] Sofia).
- Limitar o raio de impacto de um vazamento: "se vaza uma, vaza tudo" ([09:21] Sofia).
- Permitir rotação sem interromper o cliente ([09:21] Sofia).

## Decisão

- **Assinatura HMAC-SHA256 sobre o corpo da requisição,** enviada no header `X-Signature` ([09:20] Sofia, [09:22] Sofia).
- **Um secret por endpoint de webhook,** nunca um secret global da plataforma ([09:21] Sofia). O secret fica junto da configuração do webhook (URL, secret, `customer_id` e estado ativo) ([09:21] Bruno, [09:21] Sofia).
- **O secret é gerado pelo OMS** e devolvido ao cliente na criação do webhook ([09:31] Marcos).
- **Rotação pela API:** o cliente pede um novo secret, e o anterior continua válido por 24 horas em paralelo, para dar tempo de migrar os sistemas do cliente. Depois disso, o anterior deixa de valer ([09:21] Sofia).
- **Apenas HTTPS:** URL com `http` é recusada por validação no schema Zod ([09:23] Sofia). Sofia classificou essa regra como validação, não como decisão arquitetural; ela entra aqui porque completa o modelo de segurança do canal.
- **Revisão de segurança:** pelo menos dois dias úteis de revisão da Sofia sobre HMAC e geração de secret antes do deploy ([09:46] Sofia).

## Alternativas Consideradas

### A. Secret global da plataforma (descartada)

- Pró: gestão trivial, com um único segredo.
- Contra: um vazamento compromete todos os clientes ([09:21] Sofia), risco concreto pelo histórico citado em [09:22] Diego.

### B. Enviar sem assinatura, confiando só no TLS (alternativa plausível, não levantada na reunião)

- Pró: nada a implementar no cliente.
- Contra: o TLS protege o transporte, mas não prova ao cliente que o remetente é o OMS. Qualquer um que descubra a URL poderia forjar eventos. A necessidade de o cliente validar a origem é o requisito de partida ([09:19] Sofia), e o TLS foi exigido em adição à assinatura, não em seu lugar ([09:23] Sofia).

### C. HMAC-SHA256 com secret por endpoint (escolhida)

- Pró: padrão de mercado ([09:20] Sofia), isolamento por endpoint e rotação possível.
- Contra: o OMS precisa guardar o secret de forma recuperável para assinar, porque não pode guardar só um hash dele.

## Consequências

**Positivas**

- Um vazamento afeta um único endpoint, e o cliente o resolve sozinho com a rotação.
- Os clientes verificam a assinatura com bibliotecas padrão.
- A carência de 24h evita indisponibilidade da integração na troca do secret.

**Negativas**

- Durante a carência existem dois secrets válidos. A reunião não definiu como o OMS assina nesse período (com o novo, com ambos ou outro mecanismo); isso ficou como questão em aberto no [RFC](../RFC.md#5-questões-em-aberto) (Q-03).
- A assinatura cobre apenas o corpo ([09:22] Sofia). O `X-Timestamp` serve para o cliente detectar replay "se quiser" ([09:44] Diego), mas não é assinado, então essa detecção é fraca. Isso fica registrado como risco no FDD.
- O secret precisa ser armazenado de forma recuperável. A forma de proteção em repouso não foi discutida e depende da revisão da Sofia ([09:46] Sofia).

**Trade-off explícito:** aceita-se a complexidade de gerir um secret por endpoint, com rotação e carência, em troca de isolar vazamentos e dar ao cliente uma verificação padrão de mercado.

## Referências

- `src/shared/logger/index.ts`: a lista `redact` do Pino, onde o secret deve ser acrescentado para nunca aparecer em log
- `src/modules/customers/customer.schemas.ts`: padrão dos schemas Zod que recebem a validação de HTTPS
- `TRANSCRICAO.md`: [09:02] a [09:03], [09:19] a [09:23], [09:31], [09:46]
