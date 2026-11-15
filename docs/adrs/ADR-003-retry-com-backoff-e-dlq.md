# ADR-003: Retry com backoff exponencial (1m, 5m, 30m, 2h, 12h) e dead letter em tabela separada

**Status:** Aceito
**Data:** 2026-11-15 (decisão tomada na reunião técnica de quinta-feira, [09:17] e [09:18])
**ADRs relacionadas:** [ADR-002](ADR-002-worker-separado-com-polling.md), [ADR-005](ADR-005-entrega-at-least-once-com-x-event-id.md)

---

## Contexto

O endpoint do cliente pode estar lento, fora do ar ou respondendo com erro. A reunião precisava decidir quantas vezes retentar, em que intervalos, o que fazer quando as tentativas acabam e como reprocessar depois.

Há um precedente concreto: um cliente já ficou duas horas indisponível em manutenção planejada ([09:16] Diego).

## Fatores de decisão

- Cobrir indisponibilidades de horas, não apenas de minutos ([09:16] Diego).
- Não deixar evento "pendurado pra sempre" quando o cliente sumiu ([09:15] Diego).
- Manter a outbox principal enxuta para leitura e guardar evidência para debug e reprocessamento ([09:18] Diego).
- Reprocessamento controlado e auditável ([09:36] Sofia).

## Decisão

- **Backoff exponencial com cinco intervalos fixos: 1 min, 5 min, 30 min, 2 h e 12 h** ([09:17] Diego, decidido em [09:17] Larissa).
- **Teto de tentativas.** A reunião registrou "5 tentativas" ([09:17] Larissa, [09:48] Larissa) e, ao mesmo tempo, "quase 15 horas entre primeira falha e última tentativa" ([09:17] Diego). A soma dos cinco intervalos dá 14 h 36 min, então a leitura coerente com as duas falas é: **um envio inicial e cinco retentativas**, cada uma após o intervalo correspondente. Essa interpretação está registrada como questão a confirmar no [RFC](../RFC.md#5-questões-em-aberto) (Q-01).
- **Timeout de 10 segundos por chamada.** Uma resposta que não chega em 10 segundos conta como falha e entra no retry ([09:42] Diego).
- **Dead letter em tabela separada, `webhook_dead_letter`,** com o payload, o motivo da falha e o timestamp ([09:18] Diego). O evento esgotado não fica misturado com os pendentes da outbox.
- **Replay manual por endpoint administrativo,** `POST /admin/webhooks/dead-letter/:id/replay`, que recoloca o evento na outbox como pendente ([09:18] Diego). O endpoint exige role `ADMIN`, reaproveitando o `requireRole` existente ([09:36] Sofia, [09:36] Larissa), e registra em log quem fez o replay ([09:36] Sofia).

## Alternativas Consideradas

### A. Retry indefinido com backoff (descartada)

- Pró: nenhum evento é abandonado automaticamente.
- Contra: eventos ficam pendurados para sempre quando o cliente desaparece ([09:15] Diego).

### B. Três tentativas (descartada)

- Pró: falha mais rápida e menos carga ([09:16] Bruno).
- Contra: três tentativas se esgotam em cerca de 30 minutos e não cobrem uma manutenção de duas horas, que já aconteceu ([09:16] Diego).

### C. Marcar como "falhou" na própria outbox, sem tabela de DLQ (descartada)

- Pró: uma tabela a menos ([09:17] Larissa levantou a opção).
- Contra: mistura eventos mortos com a fila ativa e piora a leitura da outbox. A tabela separada é "mais limpa" e serve como evidência para debug e reprocessamento ([09:18] Diego).

## Consequências

**Positivas**

- Indisponibilidades de até cerca de 14 h 36 min são absorvidas sem intervenção, inclusive a manutenção de duas horas citada como precedente.
- A DLQ preserva payload e motivo, o que permite diagnóstico e replay sem reconstruir o evento.
- O replay é restrito a `ADMIN` e fica auditado.

**Negativas**

- Um cliente fora do ar por mais tempo que a janela perde as notificações automáticas até um replay manual. O PM considerou aceitável: "se um cliente meu cair por 15 horas, ele já tá com problema sério dele" ([09:17] Marcos).
- Não há aviso proativo ao cliente quando as entregas falham. Notificação por e-mail ficou para uma próxima fase ([09:37] Larissa).
- O replay depende de ação humana; não há reprocessamento automático da DLQ.

**Trade-off explícito:** troca-se a garantia de entrega eventual infinita por uma janela finita e conhecida, de cerca de 15 horas, mais o replay manual. O ganho é não acumular eventos órfãos e manter a outbox legível.

## Referências

- `src/middlewares/auth.middleware.ts`: `requireRole`, reaproveitado para exigir `ADMIN` no replay
- `src/shared/logger/index.ts`: logger Pino usado no log de auditoria do replay
- `TRANSCRICAO.md`: [09:14] a [09:18], [09:35] a [09:36], [09:42], [09:48]
