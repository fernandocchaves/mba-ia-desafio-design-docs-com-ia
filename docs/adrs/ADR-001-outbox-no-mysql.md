# ADR-001: Padrão Outbox no MySQL, gravado na mesma transação da mudança de status

**Status:** Aceito
**Data:** 2026-11-15 (decisão tomada na reunião técnica de quinta-feira, [09:08])
**ADRs relacionadas:** [ADR-002](ADR-002-worker-separado-com-polling.md), [ADR-005](ADR-005-entrega-at-least-once-com-x-event-id.md), [ADR-007](ADR-007-snapshot-do-payload-na-insercao.md)

---

## Contexto

Três clientes B2B (Atlas Comercial, MaxDistribuição e Nova Cargo) pediram para ser notificados quando o status dos seus pedidos muda. Hoje eles fazem polling em `GET /orders`, o que deixa a integração lenta e cara ([09:00] Marcos).

A mudança de status acontece em `OrderService.changeStatus` (`src/modules/orders/order.service.ts`), dentro de um `prisma.$transaction`. Essa transação atualiza `orders`, insere em `order_status_history` e, nas transições previstas em `src/modules/orders/order.status.ts`, debita ou repõe estoque. O time a descreveu como "já pesada" ([09:04] Bruno).

A questão era onde e quando disparar a notificação HTTP ao cliente sem degradar essa transação e sem perder eventos.

## Fatores de decisão

- Um cliente lento ou fora do ar não pode travar a mudança de status de outros pedidos ([09:04] Bruno).
- A falha do cliente não pode desfazer a mudança de status: "dá rollback na mudança de status? Não dá" ([09:04] Bruno).
- Não pode existir status alterado sem evento registrado, nem evento de uma mudança que sofreu rollback ([09:06] Diego, [09:40] Bruno).
- O time é pequeno; subir infraestrutura nova para isso é overengineering ([09:07] Diego).
- O requisito de latência do cliente é "abaixo de 10 segundos" ([09:02] Marcos).

## Decisão

Adotar o **padrão Outbox no MySQL existente**. Dentro da mesma transação SQL que altera `orders` e `order_status_history`, a aplicação insere uma linha na tabela `webhook_outbox` com o evento. Um processo separado (ADR-002) lê essa tabela e faz as chamadas HTTP.

- Se a inserção na outbox falhar, a transação inteira faz rollback, e o status não muda ([09:40] Bruno).
- A inserção é feita por uma função que recebe o client transacional atual, `publishWebhookEvent(tx, order, fromStatus, toStatus)`, chamada por `changeStatus`. Não se injeta um repository inteiro no `OrderService` ([09:41] Bruno, [09:41] Diego).
- O filtro de eventos é aplicado na inserção: se nenhum webhook ativo do cliente assina o novo status, nenhuma linha é criada ([09:34] Bruno).
- A tabela tem estados pendente, processando, falhou e entregue, com índices em status e `created_at`. O worker lê os pendentes mais antigos em lotes pequenos ([09:08] Diego).
- As chaves primárias são UUID, como no resto do schema ([09:51] Larissa; `prisma/schema.prisma` usa `@default(uuid()) @db.Char(36)` em todos os modelos).

## Alternativas Consideradas

### A. Chamada HTTP síncrona dentro de `changeStatus` (descartada)

- Pró: menor latência possível e nenhuma tabela nova.
- Contra: acopla a latência e a disponibilidade de cada cliente à transação de pedidos. Um cliente lento trava mudanças de status de outros pedidos ([09:04] Bruno).
- Contra: não há resposta aceitável para cliente fora do ar, porque desfazer a mudança de status não é opção ([09:04] Bruno).
- Descartada por unanimidade: "Síncrono está fora de questão" ([09:06] Diego).

### B. Redis Streams ou outra fila externa (descartada)

- Pró: consumo reativo, sem polling.
- Contra: exige subir e operar infraestrutura nova, "Redis Cluster pra isso é overengineering" para um time pequeno ([09:07] Larissa, [09:07] Diego).
- Contra: publicar numa fila externa fora da transação do MySQL reabre o problema de consistência entre status e evento. A outbox resolve isso por construção ([09:06] Diego).

### C. Outbox no MySQL (escolhida)

- Pró: atomicidade com a transação de pedidos, sem infraestrutura nova.
- Contra: exige polling (ADR-002) e manutenção do volume da tabela ([09:07] Bruno, [09:08] Diego).

## Consequências

**Positivas**

- Consistência por construção: o evento existe se e somente se a mudança de status foi confirmada ([09:06] Diego).
- Nenhum componente de infraestrutura novo; o mesmo MySQL e o mesmo Prisma ([09:11] Diego).
- A transação de pedidos ganha apenas uma leitura de configuração e uma inserção em lote na outbox, com uma linha por webhook que assina o status. Nenhuma chamada de rede entra nela.

**Negativas**

- A transação de `changeStatus` fica um pouco maior: lê os webhooks ativos do cliente e insere na outbox.
- A tabela cresce continuamente. O arquivamento de linhas entregues ("depois de 30 dias ou assim") ficou fora do escopo desta feature ([09:08] Diego).
- A entrega passa a ser assíncrona, e a latência mínima é a do intervalo de polling (ADR-002).

**Trade-off explícito:** troca-se a simplicidade de uma chamada direta e a reatividade de uma fila dedicada pela garantia transacional sem infraestrutura nova. O custo é latência de polling e crescimento de tabela.

## Referências

- `src/modules/orders/order.service.ts`: `changeStatus`, ponto de inserção do evento, e o tipo `TxClient = Prisma.TransactionClient`
- `src/modules/orders/order.status.ts`: transições válidas e regras de estoque
- `prisma/schema.prisma`: convenção de ids UUID `Char(36)` e enum `OrderStatus`
- `TRANSCRICAO.md`: [09:03] a [09:08], [09:33] a [09:34], [09:40] a [09:41], [09:51]
