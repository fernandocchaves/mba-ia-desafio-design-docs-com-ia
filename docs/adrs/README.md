# Architectural Decision Records

Este diretório armazena os ADRs (Architectural Decision Records) do projeto. Cada decisão arquitetural relevante é registrada num arquivo próprio, nomeado no formato `ADR-NNN-titulo-em-kebab-case.md` e numerado sequencialmente.

Os ADRs seguem uma variante em português do MADR: Status, Data, ADRs relacionadas, Contexto, Fatores de decisão, Decisão, Alternativas Consideradas, Consequências (positivas, negativas e trade-off explícito) e Referências.

## Sistema de Webhooks de Notificação de Pedidos

| ADR | Decisão | Status |
|---|---|---|
| [ADR-001](ADR-001-outbox-no-mysql.md) | Padrão Outbox no MySQL, na mesma transação da mudança de status | Aceito |
| [ADR-002](ADR-002-worker-separado-com-polling.md) | Worker em processo separado, polling de 2 s, instância única | Aceito |
| [ADR-003](ADR-003-retry-com-backoff-e-dlq.md) | Retry 1m/5m/30m/2h/12h e dead letter em tabela separada | Aceito |
| [ADR-004](ADR-004-hmac-sha256-com-secret-por-endpoint.md) | HMAC-SHA256 com secret por endpoint e rotação com carência de 24 h | Aceito |
| [ADR-005](ADR-005-entrega-at-least-once-com-x-event-id.md) | Entrega at-least-once com `X-Event-Id` | Aceito |
| [ADR-006](ADR-006-reuso-dos-padroes-do-projeto.md) | Reuso dos padrões existentes do projeto | Aceito |
| [ADR-007](ADR-007-snapshot-do-payload-na-insercao.md) | Payload renderizado (snapshot) na inserção | Aceito |

Origem de cada decisão na reunião: [TRACKER](../TRACKER.md). Proposta consolidada: [RFC](../RFC.md).
