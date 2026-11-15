# ADR-007: Payload do evento renderizado (snapshot) no momento da inserção na outbox

**Status:** Aceito
**Data:** 2026-11-15 (decisão tomada no fim da reunião técnica de quinta-feira, [09:52])
**ADRs relacionadas:** [ADR-001](ADR-001-outbox-no-mysql.md), [ADR-005](ADR-005-entrega-at-least-once-com-x-event-id.md)

---

## Contexto

O evento entra na outbox dentro da transação de `changeStatus` (ADR-001) e é entregue depois, às vezes horas depois, por causa do retry (ADR-003). Nesse intervalo, o pedido pode mudar de novo.

A questão era o que a linha da outbox guarda: o payload já renderizado ou só a referência ao pedido (`order_id`), com o payload montado na hora do envio ([09:51] Bruno).

O payload é JSON enxuto com `event_id`, `event_type` (`order.status_changed`), `timestamp` ISO 8601, `order_id`, `order_number`, `from_status`, `to_status`, `customer_id` e campos básicos do pedido, como `total_cents`. Não inclui itens; quem precisar de detalhes consulta `GET /orders/:id` ([09:43] Diego).

## Fatores de decisão

- O evento deve refletir o estado do pedido no momento da mudança de status ([09:52] Larissa).
- Retentativas e replays do mesmo evento devem enviar exatamente o mesmo conteúdo, coerente com o `X-Event-Id` estável (ADR-005).
- O tamanho de payload tem limite de 64 KB ([09:24] Larissa).

## Decisão

Renderizar o payload completo **na inserção**, dentro da transação, e gravá-lo na outbox. O worker envia o payload gravado, sem consultar o pedido novamente ([09:52] Larissa, [09:52] Diego, [09:52] Bruno).

## Alternativas Consideradas

### A. Guardar apenas `order_id` e renderizar no envio (descartada)

- Pró: linha menor na outbox e dados "mais frescos" no envio.
- Contra: um evento `PAID → PROCESSING` entregue depois que o pedido já está `SHIPPED` sairia com dados inconsistentes com o próprio evento, o "caso esquisito" apontado em [09:52] Larissa.
- Contra: retentativas do mesmo `X-Event-Id` poderiam carregar conteúdos diferentes.

### B. Snapshot na inserção (escolhida)

- Pró: o evento é imutável, fiel ao momento da mudança e idêntico entre tentativas.
- Contra: armazena dados que podem ficar desatualizados, o que é aceitável porque o evento descreve um fato passado.

## Consequências

**Positivas**

- Fidelidade histórica: cada evento descreve a transição que o gerou.
- O worker não lê `orders`, então só depende das tabelas do próprio módulo.
- O replay da DLQ reenvia exatamente o que falhou.

**Negativas**

- A renderização acontece dentro da transação de `changeStatus` e soma algum custo a ela. O custo é baixo porque o payload é enxuto e não inclui itens ([09:43] Diego), e o pedido já está carregado na transação.
- Uma correção no formato do payload não se aplica retroativamente aos eventos já gravados.

**Trade-off explícito:** troca-se um pouco de armazenamento e de trabalho na transação por imutabilidade e consistência entre tentativas.

## Referências

- `src/modules/orders/order.service.ts`: `changeStatus` já carrega o pedido na transação (`tx.order.findUnique`); `orderNumber`, `customerId` e `totalCents` vêm desse registro
- `prisma/schema.prisma`: campos do modelo `Order` usados no snapshot
- `TRANSCRICAO.md`: [09:43] a [09:44], [09:51] a [09:52]
