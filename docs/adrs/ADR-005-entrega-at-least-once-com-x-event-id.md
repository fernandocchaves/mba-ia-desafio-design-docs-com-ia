# ADR-005: Garantia de entrega at-least-once, com deduplicação pelo cliente via X-Event-Id

**Status:** Aceito
**Data:** 2026-11-15 (decisão tomada na reunião técnica de quinta-feira, [09:26])
**ADRs relacionadas:** [ADR-001](ADR-001-outbox-no-mysql.md), [ADR-003](ADR-003-retry-com-backoff-e-dlq.md)

---

## Contexto

Com outbox, worker e retry (ADR-001 a ADR-003), há janelas em que o OMS não sabe se o cliente processou um evento. Exemplos: o cliente processou, mas a resposta excedeu o timeout de 10 segundos ([09:42] Diego); o worker caiu entre o envio e o registro do resultado; um administrador fez replay de um evento da DLQ ([09:18] Diego).

Era preciso decidir qual garantia de entrega o OMS oferece e como o cliente lida com repetições.

## Fatores de decisão

- Nenhum evento confirmado pode ser perdido (ADR-001).
- Simplicidade de implementação e operação para um time pequeno ([09:07] Diego).
- Alinhamento com o padrão de mercado, "Stripe faz assim, GitHub faz assim" ([09:25] Diego).
- Dar ao cliente um meio determinístico de reconhecer duplicatas ([09:25] Bruno).

## Decisão

- O OMS garante **at-least-once**: um evento pode chegar mais de uma vez, e o cliente deve estar preparado ([09:24] Diego).
- Cada evento recebe um **UUID gerado quando entra na outbox**, enviado no header **`X-Event-Id`**. Ele é único por evento e se mantém igual em todas as tentativas e replays ([09:25] Diego). O cliente deduplica por esse valor ([09:25] Diego).
- O PM documenta esse comportamento, com destaque, no portal do desenvolvedor ([09:26] Marcos).
- Decisão registrada pela tech lead: "At-least-once com X-Event-Id pra dedup do lado do cliente" ([09:26] Larissa).

## Alternativas Consideradas

### A. Exactly-once (descartada)

- Pró: o cliente não precisa deduplicar.
- Contra: exige coordenação dos dois lados e fica "muito mais complexo" ([09:25] Diego).

### B. At-most-once, sem retry (alternativa plausível, não levantada na reunião)

- Pró: sem duplicatas.
- Contra: perde eventos sempre que o cliente estiver indisponível, o que contradiz a política de retry de até cerca de 15 horas do ADR-003.

### C. At-least-once com X-Event-Id (escolhida)

- Pró: simples, padrão de mercado e compatível com retry e replay.
- Contra: transfere ao cliente a responsabilidade de deduplicar ([09:25] Sofia).

## Consequências

**Positivas**

- Retry, timeout e replay podem reenviar sem risco de perda; o reenvio é sempre seguro do ponto de vista do OMS.
- O `X-Event-Id` também serve de chave de correlação nos logs e no histórico de entregas.

**Negativas**

- O cliente precisa implementar deduplicação. Um cliente que não o faça pode processar o mesmo evento duas vezes. A mitigação é documentação destacada no portal ([09:26] Marcos).
- O id precisa ser estável entre tentativas e replays, então o replay deve reutilizar o evento original em vez de criar um novo. A reunião não tratou disso explicitamente; está registrado como questão em aberto no [RFC](../RFC.md#5-questões-em-aberto) (Q-11).

**Trade-off explícito:** o OMS aceita reenviar e transfere a deduplicação ao cliente em troca de uma implementação simples e padrão de mercado. A alternativa, exactly-once, exigiria coordenação entre os dois lados.

## Referências

- `src/middlewares/request-logger.middleware.ts`: padrão existente de id de correlação (`X-Request-Id` gerado com `uuid`), que o `X-Event-Id` segue para eventos
- `package.json`: dependência `uuid`, já presente
- `TRANSCRICAO.md`: [09:24] a [09:26]
