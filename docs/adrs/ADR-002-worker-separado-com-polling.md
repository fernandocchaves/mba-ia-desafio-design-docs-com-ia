# ADR-002: Worker em processo separado, lendo a outbox por polling de 2 segundos

**Status:** Aceito
**Data:** 2026-11-15 (decisão tomada na reunião técnica de quinta-feira, [09:10] e [09:11])
**ADRs relacionadas:** [ADR-001](ADR-001-outbox-no-mysql.md), [ADR-003](ADR-003-retry-com-backoff-e-dlq.md), [ADR-006](ADR-006-reuso-dos-padroes-do-projeto.md)

---

## Contexto

Com a outbox (ADR-001), alguém precisa ler os eventos pendentes e entregá-los. Duas perguntas ficaram abertas: como esse consumidor descobre que há eventos novos e em que processo ele roda.

A aplicação hoje tem um único entrypoint, `src/server.ts`, que sobe a API Express construída em `src/app.ts`. O cliente aceita como "tempo real" qualquer coisa abaixo de 10 segundos ([09:02] Marcos).

## Fatores de decisão

- Latência de entrega abaixo de 10 segundos ([09:02] Marcos).
- O MySQL não tem um mecanismo de notificação a processos externos equivalente ao `LISTEN/NOTIFY` do Postgres ([09:09] Diego).
- O consumidor não pode morrer junto com a API: "se a API reinicia, perde o worker" ([09:11] Diego).
- O consumidor deve usar o mesmo banco e a mesma stack, sem infraestrutura nova ([09:11] Bruno, [09:11] Diego).

## Decisão

- **Polling em loop a cada 2 segundos.** Cada ciclo busca os eventos pendentes mais antigos, processa e marca o resultado ([09:09] Diego). O polling acrescenta até 2 segundos de espera antes do primeiro envio ("latência mínima vai ser 2 segundos no pior caso"), o que foi aceito pelo PM e pela tech lead ([09:10] Marcos, [09:10] Larissa).
- **Processo separado, mesmo código.** Um entrypoint novo, `src/worker.ts`, ao lado de `src/server.ts`, executado por um script `npm run worker` ([09:11] Larissa). A lógica de processamento fica dentro do módulo, em `src/modules/webhooks/webhook.worker.ts` ou `webhook.processor.ts` ([09:28] Bruno).
- **Mesmo banco, PrismaClient próprio.** O worker usa a mesma `DATABASE_URL`, mas cria a sua própria instância de `PrismaClient`, "porque é outro processo Node" ([09:30] Bruno). O projeto já expõe `createPrismaClient()` em `src/config/database.ts`.
- **Uma única instância.** O worker processa em ordem de `created_at`, o que garante a ordem de entrega por pedido enquanto houver um só worker ([09:12] Diego). Isso é registrado como limitação conhecida, e não como garantia de ordem global ([09:13] Larissa).

## Alternativas Consideradas

### A. Trigger no banco para reagir a inserções (descartada)

- Pró: mais reativo que o polling ([09:09] Bruno).
- Contra: um trigger do MySQL só executa SQL e não notifica processo externo. Avisar o worker exigiria improvisos como escrever em arquivo ou chamar um endpoint ([09:09] Diego).
- Contra: o ganho é irrelevante, porque o polling de 2 segundos já atende o requisito de 10 segundos com folga ([09:09] Diego).

### B. Worker dentro do processo da API (descartada)

- Pró: um deploy e um processo a menos.
- Contra: um restart ou crash da API derruba as entregas ([09:11] Diego). Além disso, o trabalho de entrega disputaria o event loop com as requisições HTTP.

### C. Múltiplos workers em paralelo (adiada)

- Pró: mais vazão.
- Contra: perde a ordem de entrega por pedido. Recuperá-la exigiria particionar por `order_id` ou usar lock pessimista, o que é "problema do futuro, não agora" ([09:13] Diego).

## Consequências

**Positivas**

- Latência previsível: até cerca de 2 segundos até o primeiro envio, mais o tempo de resposta do cliente, dentro da meta de 10 segundos.
- Isolamento de falhas entre API e entregas.
- Nenhuma infraestrutura nova; o deploy ganha apenas um processo a mais com o mesmo artefato.

**Negativas**

- O polling consulta o banco a cada 2 segundos mesmo sem eventos. O custo é mitigado pelo índice em status e `created_at` (ADR-001).
- O worker único é ponto único de falha e teto de vazão. Se ele parar, os eventos se acumulam na outbox, sem perda, até ele voltar.
- A ordem só vale por `order_id` e só com um worker; escalar exigirá uma nova decisão ([09:13] Larissa).

**Trade-off explícito:** aceita-se uma latência mínima de 2 segundos e uma vazão limitada a um worker em troca de simplicidade operacional e da garantia de ordem por pedido.

## Referências

- `src/server.ts`: modelo do entrypoint (bootstrap e encerramento por `SIGINT`/`SIGTERM`)
- `src/config/database.ts`: `createPrismaClient()` para a instância própria do worker
- `package.json`: onde o script `worker` será adicionado
- `TRANSCRICAO.md`: [09:02], [09:09] a [09:14], [09:28], [09:30]
