# RFC: Sistema de Webhooks de Notificação de Pedidos

| Campo | Valor |
|---|---|
| **Autor** | Fernando Cezar Chaves, a partir da reunião técnica conduzida por Larissa |
| **Status** | Em revisão |
| **Data** | 2026-11-15 |
| **Revisores** | Larissa (Tech Lead), Marcos (Product Manager), Bruno (Engenheiro Pleno, Pedidos), Diego (Engenheiro Sênior, Plataforma), Sofia (Engenharia de Segurança) |
| **Documentos** | [PRD](PRD.md) · [FDD](FDD.md) · [ADRs](adrs/) · [Tracker](TRACKER.md) |

Os identificadores entre colchetes, como **[RFC-ALT-01]**, são as chaves do [Tracker](TRACKER.md), que liga cada item à fala da reunião ou ao arquivo de código de origem.

---

## 1. Resumo (TL;DR)

Propomos notificar clientes B2B por **webhooks de saída** sempre que o status de um pedido mudar.

- **Registro do evento:** o evento é gravado numa **outbox no MySQL**, na mesma transação da mudança de status.
- **Entrega:** um **worker em processo separado** lê a outbox a cada **2 segundos** e entrega por HTTPS.
- **Segurança:** cada entrega é assinada com **HMAC-SHA256** usando um secret próprio de cada endpoint.
- **Garantia:** a entrega é **at-least-once**; o cliente deduplica pelo `X-Event-Id`.
- **Falhas:** são retentadas com **backoff de 1m, 5m, 30m, 2h e 12h**; depois vão para uma **tabela de dead letter**, com replay manual por administradores.

Tudo é construído com o MySQL, o Prisma e os padrões já existentes no OMS, sem infraestrutura nova.

## 2. Contexto e problema

**[RFC-CTX-01]** Três clientes B2B (Atlas Comercial, MaxDistribuição e Nova Cargo) pediram formalmente para ser avisados quando seus pedidos mudam de status. Hoje eles fazem polling em `GET /orders`, o que torna a integração "lenta e cara". A Atlas sinalizou que pode migrar para um concorrente se a entrega não sair até o fim do trimestre ([09:00] Marcos). Para eles, "tempo real" é **abaixo de 10 segundos** ([09:02] Marcos).

**[RFC-CTX-02]** O OMS não tem nenhum mecanismo de notificação externa, evento ou fila. A mudança de status vive em `OrderService.changeStatus` (`src/modules/orders/order.service.ts`), numa transação que já atualiza `orders`, insere em `order_status_history` e mexe em estoque ([09:04] Bruno). Qualquer solução precisa conviver com essa transação sem torná-la dependente da rede.

**[RFC-CTX-03]** O escopo é só de saída: o OMS envia, e o cliente recebe ([09:02] Marcos).

## 3. Proposta técnica

```
 API (processo atual)                          Worker (processo novo)
 ┌────────────────────────────────┐            ┌────────────────────────────────┐
 │ PATCH /orders/:id/status       │            │ a cada 2 s: pendentes mais     │
 │  └ changeStatus (transação)    │            │ antigos, em lote pequeno       │
 │     ├ orders / history / stock │   MySQL    │  ├ assina (HMAC-SHA256)        │──HTTPS──▶ endpoint
 │     └ publishWebhookEvent(tx) ─┼──────────▶ │  ├ POST com timeout de 10 s    │          do cliente
 │                                │ webhook_   │  ├ sucesso → entregue          │
 │ CRUD /webhooks, deliveries,    │ outbox     │  ├ falha → reagenda (backoff)  │
 │ replay de DLQ (ADMIN)          │            │  └ esgotou → webhook_dead_letter│
 └────────────────────────────────┘            └────────────────────────────────┘
```

1. **[RFC-PROP-01] Outbox transacional.** `changeStatus` chama `publishWebhookEvent(tx, order, fromStatus, toStatus)` dentro da transação existente ([09:41] Bruno). Se algum webhook ativo do cliente assina o novo status, a função grava o evento na `webhook_outbox`; se nenhum assina, nada é gravado ([09:34] Bruno). Se a gravação falhar, a mudança de status inteira faz rollback ([09:40] Bruno). O payload é gravado já renderizado, como snapshot ([09:52] Larissa). Ver [ADR-001](adrs/ADR-001-outbox-no-mysql.md) e [ADR-007](adrs/ADR-007-snapshot-do-payload-na-insercao.md).
2. **[RFC-PROP-02] Worker separado em polling.** `src/worker.ts`, executado por `npm run worker`, roda fora da API, com o mesmo banco e um `PrismaClient` próprio ([09:11] Larissa, [09:30] Bruno). Há uma única instância, então a ordem de entrega vale por pedido, e não globalmente ([09:13] Larissa). Ver [ADR-002](adrs/ADR-002-worker-separado-com-polling.md).
3. **[RFC-PROP-03] Resiliência.**
   - Timeout de 10 s por chamada ([09:42] Diego).
   - Backoff de 1m, 5m, 30m, 2h e 12h ([09:17] Larissa).
   - Dead letter em tabela própria ([09:18] Diego), com replay restrito a `ADMIN` e auditado ([09:36] Sofia).
   - Ver [ADR-003](adrs/ADR-003-retry-com-backoff-e-dlq.md).
4. **[RFC-PROP-04] Segurança.**
   - HMAC-SHA256 sobre o corpo, no header `X-Signature`.
   - Um secret por endpoint, gerado pelo OMS e rotacionável com 24 h de carência ([09:22] Sofia, [09:31] Marcos).
   - URLs apenas `https` ([09:23] Sofia).
   - Payload limitado a 64 KB ([09:24] Larissa).
   - Ver [ADR-004](adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md).
5. **[RFC-PROP-05] Contrato de entrega.**
   - Corpo: JSON enxuto do evento `order.status_changed`, sem itens ([09:43] Diego).
   - Headers: `X-Event-Id`, `X-Signature`, `X-Timestamp`, `X-Webhook-Id` e `Content-Type: application/json` ([09:44] Diego, [09:44] Sofia).
   - Garantia at-least-once ([09:26] Larissa); ver [ADR-005](adrs/ADR-005-entrega-at-least-once-com-x-event-id.md).
6. **[RFC-PROP-06] API de gestão.**
   - Criar, listar, editar e remover webhooks, com filtro por status de pedido ([09:33] Bruno).
   - Histórico das últimas 100 entregas ([09:34] Marcos).
   - Rotação de secret ([09:21] Sofia).
   - Replay da DLQ ([09:18] Diego).
   - O CRUD aceita qualquer usuário autenticado; o replay exige `ADMIN` ([09:37] Sofia, [09:36] Larissa).
7. **[RFC-PROP-07] Padrões do projeto.** O módulo fica em `src/modules/webhooks/`, com erros `AppError` de prefixo `WEBHOOK_`, Zod, Pino e o `errorMiddleware` existente ([09:30] Larissa). Ver [ADR-006](adrs/ADR-006-reuso-dos-padroes-do-projeto.md).

Os contratos HTTP, o modelo de dados, a matriz de erros e o algoritmo do worker estão no [FDD](FDD.md).

## 4. Alternativas consideradas

| ID | Alternativa | Por que foi descartada (trade-off) | Origem |
|---|---|---|---|
| **RFC-ALT-01** | Disparar o HTTP **sincronamente** dentro de `changeStatus` | Ganharia latência mínima, mas acopla a transação de pedidos à disponibilidade de cada cliente: um cliente lento trava mudanças de outros pedidos, e um cliente fora do ar não tem tratamento possível, porque desfazer a mudança de status não é opção. | [09:04] Bruno, [09:06] Diego |
| **RFC-ALT-02** | **Redis Streams** ou fila dedicada | Ganharia consumo reativo, mas exige subir e operar infraestrutura nova ("Redis Cluster pra isso é overengineering") e não garante atomicidade com a transação do MySQL. | [09:07] Larissa, [09:07] Diego |
| **RFC-ALT-03** | **Trigger no banco** para acordar o worker | Seria mais reativa, mas o MySQL não notifica processos externos (não há `LISTEN/NOTIFY` como no Postgres) e exigiria improvisos. O polling de 2 s já atende a meta de 10 s. | [09:09] Bruno, [09:09] Diego |
| **RFC-ALT-04** | **Retry indefinido**, ou apenas **3 tentativas** | O indefinido deixa eventos pendurados para sempre quando o cliente some. Três tentativas se esgotam em cerca de 30 minutos e não cobrem uma manutenção de 2 h que já aconteceu. | [09:15] Diego, [09:16] Bruno, [09:16] Diego |
| **RFC-ALT-05** | **Secret global** da plataforma | É mais simples de gerir, mas um vazamento compromete todos os clientes. | [09:21] Sofia |
| **RFC-ALT-06** | **Exactly-once** | Dispensaria a deduplicação no cliente, mas exige coordenação dos dois lados e é muito mais complexo. O mercado (Stripe, GitHub) usa at-least-once. | [09:25] Diego |
| **RFC-ALT-07** | **Renderizar o payload no envio**, guardando só `order_id` | Ocuparia menos espaço, mas o evento poderia sair com dados posteriores à transição que descreve. | [09:51] Bruno, [09:52] Larissa |

## 5. Questões em aberto

| ID | Questão | Situação na reunião | Origem |
|---|---|---|---|
| **Q-01** | O "total de **5 tentativas**" conta o envio inicial? Os 5 intervalos (1m, 5m, 30m, 2h e 12h) e as "quase 15 horas entre primeira falha e última tentativa" só fecham com **1 envio + 5 retentativas**. O FDD adota essa leitura até a confirmação. | Ambíguo | [09:17] Diego, [09:17] Larissa, [09:48] Larissa |
| **Q-02** | O `customer_id` vai no **body ou no path**? Ficou definido só que não vem do JWT. O FDD propõe **path** (`/customers/:customerId/webhooks`) para criar e listar, e mantém as operações por id em `/webhooks/:id`, como no `/webhooks/:id/deliveries` citado. | Não decidido | [09:32] Larissa, [09:34] Marcos |
| **Q-03** | **Como assinar durante a carência de 24 h** da rotação: só com o novo secret, com os dois ou de outra forma. | Não decidido; depende da revisão de segurança | [09:21] Sofia, [09:46] Sofia |
| **Q-04** | **Rate limiting de saída** por cliente, por exemplo 50 mudanças de status em um minuto. | Adiado: "observar e decidir depois" | [09:38] Diego, [09:39] Larissa |
| **Q-05** | **Escalar para mais de um worker**: particionar por `order_id` ou usar lock pessimista. | Adiado ("problema do futuro") | [09:13] Diego, [09:13] Larissa |
| **Q-06** | **Endurecer as permissões** do CRUD de webhooks. Hoje qualquer usuário autenticado gerencia webhooks de qualquer cliente, porque o schema não liga `User` a `Customer` (`prisma/schema.prisma`). | Adiado ("mais pra frente") | [09:37] Sofia |
| **Q-07** | **Onde aplicar o limite de 64 KB**: na inserção (o erro abortaria a mudança de status) ou no envio. O FDD propõe no envio, com o evento indo direto para a DLQ. | Não decidido | [09:23] Sofia, [09:24] Larissa |
| **Q-08** | **Avisar o cliente por e-mail** quando o webhook dele falha repetidamente. | Adiado para a próxima fase | [09:37] Marcos, [09:37] Larissa |
| **Q-09** | **Arquivamento** das linhas entregues da outbox, "depois de 30 dias ou assim". | Fora do escopo desta feature | [09:08] Diego |
| **Q-10** | A **criação do pedido** (`create`, que nasce em `PENDING`) deve gerar evento? A reunião tratou apenas de mudança de status, e o FDD não emite evento na criação. | Não discutido; levantado na leitura do código | `src/modules/orders/order.service.ts` |
| **Q-11** | O **replay reutiliza o `event_id` original**? Pela leitura literal, o replay "recoloca na outbox", e o UUID é "gerado quando o evento entra na outbox", o que daria um id novo. Mas o id é "único por evento" e serve para o cliente deduplicar. O FDD propõe **reutilizar** o id. | Não discutido explicitamente | [09:18] Diego, [09:25] Diego |

## 6. Impacto e riscos

**Impacto no sistema existente**

- **[RFC-IMP-01]** Uma linha nova em `changeStatus`, dentro da transação: uma leitura dos webhooks ativos do cliente e uma inserção em lote, com uma linha de outbox por webhook que assina o status ([09:34] Bruno, [09:40] Bruno). Diego descreveu "uma linha ... com o evento" ([09:06] Diego); materializar uma linha por webhook de destino é **proposta do FDD**, porque cada destino tem tentativas, status e histórico próprios. Nenhuma chamada de rede entra na transação.
- **[RFC-IMP-02]** Quatro tabelas novas no MySQL:
  - configuração de webhooks ([09:21] Bruno);
  - `webhook_outbox` ([09:06] Diego);
  - `webhook_dead_letter` ([09:18] Diego);
  - histórico de entregas. Esta não foi nomeada na reunião; é derivada do requisito de histórico ([09:34] Marcos).
- **[RFC-IMP-03]** Um processo novo no deploy, com o mesmo artefato e outro entrypoint ([09:11] Larissa).
- **[RFC-IMP-04]** Nenhuma dependência nova de runtime ([09:29] Bruno). Assinatura e geração de secret usam `node:crypto`; o envio HTTP usa o `fetch` nativo do Node ≥ 20 (`package.json`, `engines`).

**Riscos principais** (o detalhamento e as mitigações estão no [PRD](PRD.md#riscos-e-mitigação) e no [FDD](FDD.md#11-riscos-e-mitigação))

- **[RFC-RISK-01]** Cliente que não deduplica processa eventos repetidos ([09:25] Sofia).
- **[RFC-RISK-02]** O worker único é ponto único de falha e de vazão ([09:11] Diego, [09:12] Diego).
- **[RFC-RISK-03]** Vazamento de secret pelo cliente ([09:22] Diego).
- **[RFC-RISK-04]** Prazo: três sprints, incluindo dois dias úteis de revisão de segurança, contra o fim de novembro pedido pela Atlas ([09:45] Marcos, [09:46] Larissa, [09:46] Sofia).

## 7. Decisões relacionadas

| ADR | Decisão |
|---|---|
| [ADR-001](adrs/ADR-001-outbox-no-mysql.md) | Padrão Outbox no MySQL, na mesma transação da mudança de status |
| [ADR-002](adrs/ADR-002-worker-separado-com-polling.md) | Worker em processo separado, polling de 2 s, instância única |
| [ADR-003](adrs/ADR-003-retry-com-backoff-e-dlq.md) | Retry 1m/5m/30m/2h/12h, timeout de 10 s e DLQ em tabela separada com replay `ADMIN` |
| [ADR-004](adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md) | HMAC-SHA256 com secret por endpoint e rotação com carência de 24 h |
| [ADR-005](adrs/ADR-005-entrega-at-least-once-com-x-event-id.md) | At-least-once com `X-Event-Id` |
| [ADR-006](adrs/ADR-006-reuso-dos-padroes-do-projeto.md) | Reuso dos padrões do projeto (módulos, `AppError`, Zod, Pino, `errorMiddleware`) |
| [ADR-007](adrs/ADR-007-snapshot-do-payload-na-insercao.md) | Payload renderizado (snapshot) na inserção |
