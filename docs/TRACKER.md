# Tracker de rastreabilidade

Este tracker liga cada item registrado no pacote de design docs à sua origem: uma fala da reunião (`TRANSCRICAO.md`) ou um arquivo do código base. Ele é a defesa contra conteúdo inventado: um item sem linha aqui, ou cuja localização não exista, não deveria estar nos documentos.

**Como ler**

- **ID:** o mesmo identificador usado entre colchetes nos documentos, por exemplo **[PRD-FR-01]**. As questões em aberto `Q-NN` do RFC aparecem como `RFC-Q-NN`. Para os ADRs, `ADR-NNN` é a decisão, e os sufixos marcam as partes do ADR: `-CTX` (contexto), `-ALT-A/B/C` (alternativas), `-CONS` (consequências) e `-REF`/`-COD` (referência ao código).
- **Linhas complementares:** um ID com sufixo `-COD`, `-ORD` ou similar (por exemplo, `FDD-DADOS-02-COD`) registra uma segunda origem do mesmo item, em geral a restrição de código que motivou um detalhe.
- **Localização:** cada linha aponta a origem **principal**. Quando um item foi construído por várias falas, as demais aparecem no próprio documento, ao lado do item.
- **"(proposta derivada)":** escolha de implementação do FDD que não foi decidida literalmente na reunião. A linha aponta a decisão da qual ela decorre, e o FDD a marca como proposta, a validar na revisão com Bruno e Diego ([09:50] Larissa).

**Resumo:** 320 linhas. 274 com Fonte = TRANSCRICAO (86%) e 46 com Fonte = CODIGO (14%). Por documento: PRD 78, RFC 55, FDD 123, ADRs 64.

O script [`docs/tools/verificar_rastreabilidade.py`](tools/verificar_rastreabilidade.py) refaz a verificação a qualquer momento: `python3 docs/tools/verificar_rastreabilidade.py`. Ele confere que cada `[hh:mm] Nome` existe na transcrição (o falante tem fala naquele minuto), que cada caminho de código existe, que cada ID existe no documento indicado e que todo ID dos documentos tem linha aqui. A revisão **semântica**, que confere se a fala citada de fato sustenta o item, foi feita por um revisor independente e está descrita no [README](../README.md#iterações-e-ajustes).

| ID | Documento | Tipo | Conteúdo (resumo) | Fonte | Localização |
|---|---|---|---|---|---|
| ADR-001 | `docs/adrs/ADR-001-outbox-no-mysql.md` | Decisão | Outbox no MySQL gravada na mesma transação da mudança de status | TRANSCRICAO | [09:08] Larissa |
| ADR-001-CTX | `docs/adrs/ADR-001-outbox-no-mysql.md` | Contexto | Transação de changeStatus já é pesada (orders, history, estoque) | TRANSCRICAO | [09:04] Bruno |
| ADR-001-CTX-COD | `docs/adrs/ADR-001-outbox-no-mysql.md` | Contexto | changeStatus roda em prisma.$transaction e usa TxClient | CODIGO | `src/modules/orders/order.service.ts` |
| ADR-001-ALT-A | `docs/adrs/ADR-001-outbox-no-mysql.md` | Alternativa descartada | HTTP síncrono em changeStatus: cliente lento trava outros pedidos | TRANSCRICAO | [09:04] Bruno |
| ADR-001-ALT-B | `docs/adrs/ADR-001-outbox-no-mysql.md` | Alternativa descartada | Redis Streams: infra nova, overengineering para time pequeno | TRANSCRICAO | [09:07] Diego |
| ADR-001-IDX | `docs/adrs/ADR-001-outbox-no-mysql.md` | Decisão | Estados pendente/processando/falhou/entregue e índices em status e created_at | TRANSCRICAO | [09:08] Diego |
| ADR-001-UUID | `docs/adrs/ADR-001-outbox-no-mysql.md` | Restrição | Ids UUID como no resto do schema | CODIGO | `prisma/schema.prisma` |
| ADR-001-CONS | `docs/adrs/ADR-001-outbox-no-mysql.md` | Trade-off | Consistência sem infra nova em troca de polling e crescimento da tabela | TRANSCRICAO | [09:08] Diego |
| ADR-002 | `docs/adrs/ADR-002-worker-separado-com-polling.md` | Decisão | Worker em polling de 2 s; latência mínima de 2 s aceita | TRANSCRICAO | [09:10] Larissa |
| ADR-002-PROC | `docs/adrs/ADR-002-worker-separado-com-polling.md` | Decisão | Worker em processo separado da API | TRANSCRICAO | [09:11] Diego |
| ADR-002-ENTRY | `docs/adrs/ADR-002-worker-separado-com-polling.md` | Decisão | Entrypoint src/worker.ts e script npm run worker | TRANSCRICAO | [09:11] Larissa |
| ADR-002-ENTRY-COD | `docs/adrs/ADR-002-worker-separado-com-polling.md` | Restrição | Modelo do entrypoint existente (bootstrap e shutdown) | CODIGO | `src/server.ts` |
| ADR-002-PRISMA | `docs/adrs/ADR-002-worker-separado-com-polling.md` | Decisão | Mesmo banco, PrismaClient próprio por processo | TRANSCRICAO | [09:30] Bruno |
| ADR-002-ALT-A | `docs/adrs/ADR-002-worker-separado-com-polling.md` | Alternativa descartada | Trigger no banco: MySQL não notifica processo externo | TRANSCRICAO | [09:09] Diego |
| ADR-002-ALT-B | `docs/adrs/ADR-002-worker-separado-com-polling.md` | Alternativa descartada | Worker dentro da API: restart da API derruba entregas | TRANSCRICAO | [09:11] Diego |
| ADR-002-ALT-C | `docs/adrs/ADR-002-worker-separado-com-polling.md` | Alternativa adiada | Múltiplos workers: perde ordem; particionar ou lock no futuro | TRANSCRICAO | [09:13] Diego |
| ADR-002-CONS | `docs/adrs/ADR-002-worker-separado-com-polling.md` | Trade-off | Ordem só por order_id e com worker único (limitação conhecida) | TRANSCRICAO | [09:13] Larissa |
| ADR-003 | `docs/adrs/ADR-003-retry-com-backoff-e-dlq.md` | Decisão | Backoff 1m/5m/30m/2h/12h, 5 tentativas | TRANSCRICAO | [09:17] Larissa |
| ADR-003-WINDOW | `docs/adrs/ADR-003-retry-com-backoff-e-dlq.md` | Restrição | Quase 15 h entre a primeira falha e a última tentativa | TRANSCRICAO | [09:17] Diego |
| ADR-003-DLQ | `docs/adrs/ADR-003-retry-com-backoff-e-dlq.md` | Decisão | DLQ em tabela webhook_dead_letter com payload, motivo e timestamp | TRANSCRICAO | [09:18] Diego |
| ADR-003-REPLAY | `docs/adrs/ADR-003-retry-com-backoff-e-dlq.md` | Decisão | Replay manual POST /admin/webhooks/dead-letter/:id/replay | TRANSCRICAO | [09:18] Diego |
| ADR-003-ADMIN | `docs/adrs/ADR-003-retry-com-backoff-e-dlq.md` | Restrição | Replay exige ADMIN e registra quem fez | TRANSCRICAO | [09:36] Sofia |
| ADR-003-ALT-A | `docs/adrs/ADR-003-retry-com-backoff-e-dlq.md` | Alternativa descartada | Retry indefinido deixa evento pendurado para sempre | TRANSCRICAO | [09:15] Diego |
| ADR-003-ALT-B | `docs/adrs/ADR-003-retry-com-backoff-e-dlq.md` | Alternativa descartada | Três tentativas não cobrem manutenção de 2 h | TRANSCRICAO | [09:16] Diego |
| ADR-003-ALT-C | `docs/adrs/ADR-003-retry-com-backoff-e-dlq.md` | Alternativa descartada | Marcar falha na própria outbox; descartada por Diego (tabela separada mais limpa) | TRANSCRICAO | [09:18] Diego |
| ADR-003-CONS | `docs/adrs/ADR-003-retry-com-backoff-e-dlq.md` | Trade-off | Cliente fora por >15 h depende de replay manual; aceito pelo PM | TRANSCRICAO | [09:17] Marcos |
| ADR-003-REF | `docs/adrs/ADR-003-retry-com-backoff-e-dlq.md` | Restrição | requireRole existente reaproveitado no replay | CODIGO | `src/middlewares/auth.middleware.ts` |
| ADR-004 | `docs/adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md` | Decisão | HMAC-SHA256 sobre o corpo, secret por endpoint, rotação com carência de 24 h | TRANSCRICAO | [09:22] Sofia |
| ADR-004-CTX | `docs/adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md` | Contexto | Cliente precisa validar origem e integridade do payload | TRANSCRICAO | [09:19] Sofia |
| ADR-004-HDR | `docs/adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md` | Decisão | Assinatura enviada no header X-Signature | TRANSCRICAO | [09:20] Sofia |
| ADR-004-GEN | `docs/adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md` | Decisão | Secret gerado pelo OMS e devolvido na criação | TRANSCRICAO | [09:31] Marcos |
| ADR-004-TLS | `docs/adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md` | Restrição | Somente https; http recusado no schema Zod | TRANSCRICAO | [09:23] Sofia |
| ADR-004-ALT-A | `docs/adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md` | Alternativa descartada | Secret global: um vazamento compromete todos | TRANSCRICAO | [09:21] Sofia |
| ADR-004-ALT-B | `docs/adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md` | Alternativa plausível (não levantada) | Só TLS sem assinatura; TLS foi exigido em adição ao HMAC | TRANSCRICAO | [09:23] Sofia |
| ADR-004-INC | `docs/adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md` | Contexto | Cliente já vazou secret em log | TRANSCRICAO | [09:22] Diego |
| ADR-004-REV | `docs/adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md` | Restrição | Revisão de segurança de 2 dias úteis antes do deploy | TRANSCRICAO | [09:46] Sofia |
| ADR-004-REF | `docs/adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md` | Restrição | Lista redact do Pino para não logar o secret | CODIGO | `src/shared/logger/index.ts` |
| ADR-005 | `docs/adrs/ADR-005-entrega-at-least-once-com-x-event-id.md` | Decisão | At-least-once com X-Event-Id para dedup no cliente | TRANSCRICAO | [09:26] Larissa |
| ADR-005-ID | `docs/adrs/ADR-005-entrega-at-least-once-com-x-event-id.md` | Decisão | UUID gerado na entrada da outbox, enviado em X-Event-Id | TRANSCRICAO | [09:25] Diego |
| ADR-005-ALT-A | `docs/adrs/ADR-005-entrega-at-least-once-com-x-event-id.md` | Alternativa descartada | Exactly-once exige coordenação dos dois lados | TRANSCRICAO | [09:25] Diego |
| ADR-005-CONS | `docs/adrs/ADR-005-entrega-at-least-once-com-x-event-id.md` | Trade-off | Responsabilidade de deduplicar vai para o cliente | TRANSCRICAO | [09:25] Sofia |
| ADR-005-DOC | `docs/adrs/ADR-005-entrega-at-least-once-com-x-event-id.md` | Dependência | PM documenta a deduplicação no portal do desenvolvedor | TRANSCRICAO | [09:26] Marcos |
| ADR-005-REF | `docs/adrs/ADR-005-entrega-at-least-once-com-x-event-id.md` | Restrição | Padrão de id de correlação (X-Request-Id com uuid) | CODIGO | `src/middlewares/request-logger.middleware.ts` |
| ADR-006 | `docs/adrs/ADR-006-reuso-dos-padroes-do-projeto.md` | Decisão | Reuso máximo: AppError, Pino, error middleware, módulos e Zod | TRANSCRICAO | [09:30] Larissa |
| ADR-006-MOD | `docs/adrs/ADR-006-reuso-dos-padroes-do-projeto.md` | Decisão | Módulo src/modules/webhooks com controller/service/repository/routes/schemas | TRANSCRICAO | [09:27] Bruno |
| ADR-006-PROC | `docs/adrs/ADR-006-reuso-dos-padroes-do-projeto.md` | Decisão | Lógica do worker em webhook.worker.ts ou webhook.processor.ts | TRANSCRICAO | [09:28] Bruno |
| ADR-006-ERR | `docs/adrs/ADR-006-reuso-dos-padroes-do-projeto.md` | Decisão | Erros com códigos prefixados WEBHOOK_ | TRANSCRICAO | [09:29] Larissa |
| ADR-006-ERR-COD | `docs/adrs/ADR-006-reuso-dos-padroes-do-projeto.md` | Restrição | AppError com statusCode, errorCode e details | CODIGO | `src/shared/errors/app-error.ts` |
| ADR-006-NF | `docs/adrs/ADR-006-reuso-dos-padroes-do-projeto.md` | Restrição | NotFoundError fixa o código NOT_FOUND | CODIGO | `src/shared/errors/http-errors.ts` |
| ADR-006-VAL | `docs/adrs/ADR-006-reuso-dos-padroes-do-projeto.md` | Restrição | validate converte ZodError em VALIDATION_ERROR fixo | CODIGO | `src/middlewares/validate.middleware.ts` |
| ADR-006-MW | `docs/adrs/ADR-006-reuso-dos-padroes-do-projeto.md` | Decisão | errorMiddleware trata AppError, Zod e Prisma sem mudança | TRANSCRICAO | [09:29] Bruno |
| ADR-006-MW-COD | `docs/adrs/ADR-006-reuso-dos-padroes-do-projeto.md` | Restrição | errorMiddleware serializa AppError e trata P2002/P2025 | CODIGO | `src/middlewares/error.middleware.ts` |
| ADR-006-ALT-A | `docs/adrs/ADR-006-reuso-dos-padroes-do-projeto.md` | Alternativa descartada | Infra própria do módulo: 'Não vamos botar nada novo' | TRANSCRICAO | [09:29] Bruno |
| ADR-006-ALT-B | `docs/adrs/ADR-006-reuso-dos-padroes-do-projeto.md` | Alternativa plausível (não levantada) | Códigos genéricos sem prefixo; prefixo WEBHOOK_ fixado | TRANSCRICAO | [09:29] Larissa |
| ADR-006-CONS | `docs/adrs/ADR-006-reuso-dos-padroes-do-projeto.md` | Trade-off | Sem biblioteca de métricas/tracing no projeto | CODIGO | `package.json` |
| ADR-007 | `docs/adrs/ADR-007-snapshot-do-payload-na-insercao.md` | Decisão | Payload renderizado (snapshot) na inserção da outbox | TRANSCRICAO | [09:52] Larissa |
| ADR-007-CTX | `docs/adrs/ADR-007-snapshot-do-payload-na-insercao.md` | Contexto | Pergunta: guardar payload renderizado ou só order_id | TRANSCRICAO | [09:51] Bruno |
| ADR-007-FMT | `docs/adrs/ADR-007-snapshot-do-payload-na-insercao.md` | Decisão | Payload JSON enxuto sem itens | TRANSCRICAO | [09:43] Diego |
| ADR-007-ALT-A | `docs/adrs/ADR-007-snapshot-do-payload-na-insercao.md` | Alternativa descartada | Renderizar no envio gera evento com dados posteriores | TRANSCRICAO | [09:52] Larissa |
| ADR-007-AGREE | `docs/adrs/ADR-007-snapshot-do-payload-na-insercao.md` | Decisão | Snapshot confirmado por Diego e Bruno | TRANSCRICAO | [09:52] Bruno |
| ADR-007-REF | `docs/adrs/ADR-007-snapshot-do-payload-na-insercao.md` | Restrição | changeStatus já carrega o pedido na transação | CODIGO | `src/modules/orders/order.service.ts` |
| RFC-CTX-01 | `docs/RFC.md` | Contexto | 3 clientes B2B pedem notificação; polling lento e caro | TRANSCRICAO | [09:00] Marcos |
| RFC-CTX-02 | `docs/RFC.md` | Contexto | changeStatus atualiza orders, history e estoque numa transação | CODIGO | `src/modules/orders/order.service.ts` |
| RFC-CTX-03 | `docs/RFC.md` | Restrição | Escopo só de saída (outbound) | TRANSCRICAO | [09:02] Marcos |
| RFC-PROP-01 | `docs/RFC.md` | Decisão | publishWebhookEvent(tx, ...) dentro da transação; rollback conjunto | TRANSCRICAO | [09:41] Bruno |
| RFC-PROP-02 | `docs/RFC.md` | Decisão | Worker em processo separado da API | TRANSCRICAO | [09:11] Diego |
| RFC-PROP-03 | `docs/RFC.md` | Decisão | Backoff 1m/5m/30m/2h/12h | TRANSCRICAO | [09:17] Larissa |
| RFC-PROP-04 | `docs/RFC.md` | Decisão | HMAC-SHA256 sobre o corpo, secret por endpoint, rotação 24 h | TRANSCRICAO | [09:22] Sofia |
| RFC-PROP-05 | `docs/RFC.md` | Decisão | Headers X-Event-Id, X-Signature, X-Timestamp e Content-Type | TRANSCRICAO | [09:44] Diego |
| RFC-PROP-06 | `docs/RFC.md` | Requisito Funcional | API de gestão: CRUD e filtro de eventos | TRANSCRICAO | [09:33] Bruno |
| RFC-PROP-07 | `docs/RFC.md` | Decisão | Módulo segue padrões do projeto | TRANSCRICAO | [09:30] Larissa |
| RFC-ALT-01 | `docs/RFC.md` | Alternativa descartada | HTTP síncrono em changeStatus | TRANSCRICAO | [09:04] Bruno |
| RFC-ALT-02 | `docs/RFC.md` | Alternativa descartada | Redis Streams / fila dedicada | TRANSCRICAO | [09:07] Larissa |
| RFC-ALT-03 | `docs/RFC.md` | Alternativa descartada | Trigger no banco: MySQL sem LISTEN/NOTIFY | TRANSCRICAO | [09:09] Diego |
| RFC-ALT-04 | `docs/RFC.md` | Alternativa descartada | Retry indefinido ou só 3 tentativas (descartes de Diego) | TRANSCRICAO | [09:16] Diego |
| RFC-ALT-05 | `docs/RFC.md` | Alternativa descartada | Secret global da plataforma | TRANSCRICAO | [09:21] Sofia |
| RFC-ALT-06 | `docs/RFC.md` | Alternativa descartada | Exactly-once | TRANSCRICAO | [09:25] Diego |
| RFC-ALT-07 | `docs/RFC.md` | Alternativa descartada | Renderizar payload no envio | TRANSCRICAO | [09:52] Larissa |
| RFC-Q-01 | `docs/RFC.md` | Questão em aberto | '5 tentativas' inclui o envio inicial? (5 intervalos e ~15 h) | TRANSCRICAO | [09:48] Larissa |
| RFC-Q-02 | `docs/RFC.md` | Questão em aberto | customer_id no body ou no path (não vem do JWT) | TRANSCRICAO | [09:32] Larissa |
| RFC-Q-03 | `docs/RFC.md` | Questão em aberto | Como assinar durante a carência de 24 h da rotação | TRANSCRICAO | [09:21] Sofia |
| RFC-Q-04 | `docs/RFC.md` | Questão em aberto | Rate limiting de saída: observar e decidir depois | TRANSCRICAO | [09:39] Larissa |
| RFC-Q-05 | `docs/RFC.md` | Questão em aberto | Escalar para múltiplos workers (partição ou lock) | TRANSCRICAO | [09:13] Diego |
| RFC-Q-06 | `docs/RFC.md` | Questão em aberto | Endurecer permissões do CRUD de webhooks | TRANSCRICAO | [09:37] Sofia |
| RFC-Q-06-COD | `docs/RFC.md` | Restrição | Schema não relaciona User a Customer | CODIGO | `prisma/schema.prisma` |
| RFC-Q-07 | `docs/RFC.md` | Questão em aberto | Onde aplicar o limite de 64 KB (inserção ou envio) | TRANSCRICAO | [09:24] Larissa |
| RFC-Q-08 | `docs/RFC.md` | Questão em aberto | Aviso por e-mail de falhas: próxima fase | TRANSCRICAO | [09:37] Larissa |
| RFC-Q-09 | `docs/RFC.md` | Questão em aberto | Arquivamento da outbox após ~30 dias | TRANSCRICAO | [09:08] Diego |
| RFC-Q-10 | `docs/RFC.md` | Questão em aberto | Criação do pedido (PENDING) deve gerar evento? | CODIGO | `src/modules/orders/order.service.ts` |
| RFC-IMP-01 | `docs/RFC.md` | Impacto | changeStatus ganha leitura de webhooks e inserção na outbox; nada se nenhum webhook quer o status | TRANSCRICAO | [09:34] Bruno |
| RFC-IMP-02 | `docs/RFC.md` | Impacto | Tabela webhook_outbox | TRANSCRICAO | [09:06] Diego |
| RFC-IMP-03 | `docs/RFC.md` | Impacto | Novo processo no deploy, mesmo artefato | TRANSCRICAO | [09:11] Larissa |
| RFC-IMP-04 | `docs/RFC.md` | Impacto | Sem dependência nova; fetch nativo do Node >= 20 | CODIGO | `package.json` |
| RFC-RISK-01 | `docs/RFC.md` | Risco | Cliente que não deduplica processa repetidos | TRANSCRICAO | [09:25] Sofia |
| RFC-RISK-02 | `docs/RFC.md` | Risco | Worker único é ponto único de falha | TRANSCRICAO | [09:12] Diego |
| RFC-RISK-03 | `docs/RFC.md` | Risco | Vazamento de secret pelo cliente | TRANSCRICAO | [09:22] Diego |
| RFC-RISK-04 | `docs/RFC.md` | Risco | Prazo de 3 sprints contra fim de novembro | TRANSCRICAO | [09:46] Larissa |
| PRD-SUM-01 | `docs/PRD.md` | Contexto | Notificar clientes B2B por webhook a cada mudança de status | TRANSCRICAO | [09:00] Marcos |
| PRD-SUM-02 | `docs/PRD.md` | Contexto | Máquina de estados do pedido existente | CODIGO | `src/modules/orders/order.status.ts` |
| PRD-PROB-01 | `docs/PRD.md` | Contexto | Pedido formal de Atlas, MaxDistribuição e Nova Cargo | TRANSCRICAO | [09:00] Marcos |
| PRD-PROB-02 | `docs/PRD.md` | Contexto | Polling em GET /orders é lento e caro | TRANSCRICAO | [09:00] Marcos |
| PRD-PROB-03 | `docs/PRD.md` | Restrição | Prazo: Atlas quer para fim de novembro | TRANSCRICAO | [09:45] Marcos |
| PRD-CEN-01 | `docs/PRD.md` | Cenário | Cliente recebe aviso de SHIPPED sem consultar | TRANSCRICAO | [09:02] Marcos |
| PRD-CEN-02 | `docs/PRD.md` | Cenário | Webhook só para SHIPPED e DELIVERED | TRANSCRICAO | [09:33] Marcos |
| PRD-CEN-03 | `docs/PRD.md` | Cenário | Manutenção de 2 h coberta pelo retry | TRANSCRICAO | [09:16] Diego |
| PRD-CEN-04 | `docs/PRD.md` | Cenário | Rotação de secret com 24 h | TRANSCRICAO | [09:21] Sofia |
| PRD-CEN-05 | `docs/PRD.md` | Cenário | Consulta ao histórico de entregas | TRANSCRICAO | [09:34] Marcos |
| PRD-CEN-06 | `docs/PRD.md` | Cenário | Admin reenvia avisos da fila de falhas | TRANSCRICAO | [09:18] Diego |
| PRD-OBJ-01 | `docs/PRD.md` | Métrica | Entrega abaixo de 10 s | TRANSCRICAO | [09:02] Marcos |
| PRD-OBJ-02 | `docs/PRD.md` | Métrica | Funcionalidade em produção até fim de novembro (prazo da Atlas) | TRANSCRICAO | [09:45] Marcos |
| PRD-OBJ-03 | `docs/PRD.md` | Métrica | 0 avisos perdidos em indisponibilidades dentro da janela de retry | TRANSCRICAO | [09:17] Diego |
| PRD-OBJ-04 | `docs/PRD.md` | Métrica | Entrega em 3 sprints com revisão de segurança | TRANSCRICAO | [09:47] Larissa |
| PRD-OUT-01 | `docs/PRD.md` | Fora de escopo | E-mail de falhas: próxima fase | TRANSCRICAO | [09:37] Larissa |
| PRD-OUT-02 | `docs/PRD.md` | Fora de escopo | Dashboard visual: projeto do frontend | TRANSCRICAO | [09:40] Larissa |
| PRD-OUT-03 | `docs/PRD.md` | Fora de escopo | Rate limiting de saída: observar | TRANSCRICAO | [09:39] Larissa |
| PRD-OUT-04 | `docs/PRD.md` | Fora de escopo | Webhooks de entrada | TRANSCRICAO | [09:02] Marcos |
| PRD-OUT-05 | `docs/PRD.md` | Fora de escopo | Ordem global e múltiplos workers | TRANSCRICAO | [09:14] Marcos |
| PRD-OUT-06 | `docs/PRD.md` | Fora de escopo | Arquivamento após ~30 dias | TRANSCRICAO | [09:08] Diego |
| PRD-OUT-07 | `docs/PRD.md` | Fora de escopo | Itens do pedido no payload | TRANSCRICAO | [09:43] Diego |
| PRD-OUT-08 | `docs/PRD.md` | Fora de escopo | Exactly-once | TRANSCRICAO | [09:25] Diego |
| PRD-FR-01 | `docs/PRD.md` | Requisito Funcional | Cadastrar webhook com url e status; secret gerado e devolvido | TRANSCRICAO | [09:31] Marcos |
| PRD-FR-02 | `docs/PRD.md` | Requisito Funcional | customer_id informado na requisição, não do JWT | TRANSCRICAO | [09:32] Larissa |
| PRD-FR-03 | `docs/PRD.md` | Requisito Funcional | Listar webhooks de um cliente | TRANSCRICAO | [09:33] Bruno |
| PRD-FR-04 | `docs/PRD.md` | Requisito Funcional | Editar webhook | TRANSCRICAO | [09:33] Bruno |
| PRD-FR-05 | `docs/PRD.md` | Requisito Funcional | Remover webhook | TRANSCRICAO | [09:33] Bruno |
| PRD-FR-06 | `docs/PRD.md` | Requisito Funcional | Filtro por status aplicado na inserção | TRANSCRICAO | [09:34] Bruno |
| PRD-FR-07 | `docs/PRD.md` | Requisito Funcional | Aviso com campos do evento, sem itens | TRANSCRICAO | [09:43] Diego |
| PRD-FR-08 | `docs/PRD.md` | Requisito Funcional | Headers de identificação (incl. X-Webhook-Id) | TRANSCRICAO | [09:44] Sofia |
| PRD-FR-09 | `docs/PRD.md` | Requisito Funcional | Assinatura HMAC-SHA256 por webhook | TRANSCRICAO | [09:20] Sofia |
| PRD-FR-10 | `docs/PRD.md` | Requisito Funcional | Rotação de secret com 24 h de carência | TRANSCRICAO | [09:21] Sofia |
| PRD-FR-11 | `docs/PRD.md` | Requisito Funcional | Recusar URL não https | TRANSCRICAO | [09:23] Sofia |
| PRD-FR-12 | `docs/PRD.md` | Requisito Funcional | Retry automático 1m/5m/30m/2h/12h | TRANSCRICAO | [09:17] Diego |
| PRD-FR-13 | `docs/PRD.md` | Requisito Funcional | Fila de falhas com conteúdo, motivo e momento | TRANSCRICAO | [09:18] Diego |
| PRD-FR-14 | `docs/PRD.md` | Requisito Funcional | Reenvio manual por admin com registro do autor | TRANSCRICAO | [09:36] Sofia |
| PRD-FR-15 | `docs/PRD.md` | Requisito Funcional | Histórico das últimas 100 entregas | TRANSCRICAO | [09:34] Marcos |
| PRD-NFR-01 | `docs/PRD.md` | Requisito Não Funcional | Latência < 10 s; mínima de 2 s aceita | TRANSCRICAO | [09:10] Larissa |
| PRD-NFR-02 | `docs/PRD.md` | Requisito Não Funcional | Cliente lento não afeta mudança de status | TRANSCRICAO | [09:04] Bruno |
| PRD-NFR-03 | `docs/PRD.md` | Requisito Não Funcional | Status e aviso consistentes (rollback conjunto) | TRANSCRICAO | [09:40] Bruno |
| PRD-NFR-04 | `docs/PRD.md` | Requisito Não Funcional | At-least-once | TRANSCRICAO | [09:24] Diego |
| PRD-NFR-05 | `docs/PRD.md` | Requisito Não Funcional | Ordem por pedido, não global | TRANSCRICAO | [09:13] Larissa |
| PRD-NFR-06 | `docs/PRD.md` | Requisito Não Funcional | Timeout de 10 s do cliente | TRANSCRICAO | [09:42] Diego |
| PRD-NFR-07 | `docs/PRD.md` | Requisito Não Funcional | Limite de 64 KB, erro em vez de truncar | TRANSCRICAO | [09:24] Larissa |
| PRD-NFR-08 | `docs/PRD.md` | Requisito Não Funcional | Secret por webhook e TLS obrigatório | TRANSCRICAO | [09:23] Sofia |
| PRD-NFR-09 | `docs/PRD.md` | Requisito Não Funcional | CRUD para qualquer autenticado; replay só ADMIN | TRANSCRICAO | [09:37] Sofia |
| PRD-NFR-10 | `docs/PRD.md` | Requisito Não Funcional | Envio em processo separado da API | TRANSCRICAO | [09:11] Diego |
| PRD-NFR-11 | `docs/PRD.md` | Requisito Não Funcional | Nenhuma infraestrutura nova | TRANSCRICAO | [09:07] Diego |
| PRD-NFR-12 | `docs/PRD.md` | Requisito Não Funcional | Seguir padrões do projeto (WEBHOOK_, logger, validação) | TRANSCRICAO | [09:30] Larissa |
| PRD-DEP-01 | `docs/PRD.md` | Dependência | Revisão de segurança de 2 dias úteis | TRANSCRICAO | [09:46] Sofia |
| PRD-DEP-02 | `docs/PRD.md` | Dependência | Documentação no portal do desenvolvedor | TRANSCRICAO | [09:40] Marcos |
| PRD-DEP-03 | `docs/PRD.md` | Dependência | Confirmação de prazo com clientes | TRANSCRICAO | [09:47] Marcos |
| PRD-DEP-04 | `docs/PRD.md` | Dependência | Novo processo de worker no ambiente | TRANSCRICAO | [09:11] Larissa |
| PRD-RISK-01 | `docs/PRD.md` | Risco | Atraso e churn da Atlas | TRANSCRICAO | [09:00] Marcos |
| PRD-RISK-02 | `docs/PRD.md` | Risco | Cliente processa aviso duplicado | TRANSCRICAO | [09:25] Sofia |
| PRD-RISK-03 | `docs/PRD.md` | Risco | Cliente fora por mais de ~15 h | TRANSCRICAO | [09:17] Marcos |
| PRD-RISK-04 | `docs/PRD.md` | Risco | Vazamento de secret | TRANSCRICAO | [09:22] Diego |
| PRD-RISK-05 | `docs/PRD.md` | Risco | Qualquer usuário gerencia webhooks de qualquer cliente | TRANSCRICAO | [09:37] Sofia |
| PRD-AC-01 | `docs/PRD.md` | Critério de aceitação | Cadastro https devolve secret | TRANSCRICAO | [09:31] Marcos |
| PRD-AC-02 | `docs/PRD.md` | Critério de aceitação | URL http recusada | TRANSCRICAO | [09:23] Sofia |
| PRD-AC-03 | `docs/PRD.md` | Critério de aceitação | Aviso em < 10 s com headers e assinatura válida | TRANSCRICAO | [09:02] Marcos |
| PRD-AC-04 | `docs/PRD.md` | Critério de aceitação | Status não assinado não gera aviso | TRANSCRICAO | [09:34] Bruno |
| PRD-AC-05 | `docs/PRD.md` | Critério de aceitação | Rollback da mudança não gera aviso | TRANSCRICAO | [09:06] Diego |
| PRD-AC-06 | `docs/PRD.md` | Critério de aceitação | Retry nos intervalos e fila de falhas | TRANSCRICAO | [09:17] Larissa |
| PRD-AC-07 | `docs/PRD.md` | Critério de aceitação | Reenvio só ADMIN e registrado | TRANSCRICAO | [09:36] Larissa |
| PRD-AC-08 | `docs/PRD.md` | Critério de aceitação | Secret antigo válido por 24 h após rotação | TRANSCRICAO | [09:21] Sofia |
| PRD-AC-09 | `docs/PRD.md` | Critério de aceitação | Histórico das últimas 100 entregas | TRANSCRICAO | [09:34] Marcos |
| PRD-AC-10 | `docs/PRD.md` | Critério de aceitação | Mudança de status funciona com cliente fora do ar | TRANSCRICAO | [09:04] Bruno |
| PRD-TEST-01 | `docs/PRD.md` | Estratégia de teste | Integração com Vitest + Supertest contra MySQL | CODIGO | `tests/orders.test.ts` |
| PRD-TEST-02 | `docs/PRD.md` | Estratégia de teste | Revisão do desenho com Bruno e Diego antes de codar | TRANSCRICAO | [09:50] Larissa |
| FDD-CTX-01 | `docs/FDD.md` | Contexto | Clientes fazem polling em GET /orders | TRANSCRICAO | [09:00] Marcos |
| FDD-CTX-02 | `docs/FDD.md` | Contexto | Regras de transição e estoque de changeStatus | CODIGO | `src/modules/orders/order.status.ts` |
| FDD-CTX-03 | `docs/FDD.md` | Contexto | Webhooks de saída a partir de outbox transacional | TRANSCRICAO | [09:06] Diego |
| FDD-OBJ-01 | `docs/FDD.md` | Objetivo técnico | Atomicidade status/evento | TRANSCRICAO | [09:06] Diego |
| FDD-OBJ-02 | `docs/FDD.md` | Objetivo técnico | Latência: polling 2 s, meta < 10 s | TRANSCRICAO | [09:10] Larissa |
| FDD-OBJ-03 | `docs/FDD.md` | Objetivo técnico | Nenhum HTTP na API nem na transação | TRANSCRICAO | [09:04] Bruno |
| FDD-OBJ-04 | `docs/FDD.md` | Objetivo técnico | Retry determinístico 1m/5m/30m/2h/12h | TRANSCRICAO | [09:17] Larissa |
| FDD-OBJ-05 | `docs/FDD.md` | Objetivo técnico | 100% das entregas assinadas | TRANSCRICAO | [09:22] Sofia |
| FDD-OBJ-06 | `docs/FDD.md` | Objetivo técnico | X-Event-Id estável | TRANSCRICAO | [09:25] Diego |
| FDD-EXC-01 | `docs/FDD.md` | Fora de escopo | Webhooks de entrada | TRANSCRICAO | [09:02] Marcos |
| FDD-EXC-02 | `docs/FDD.md` | Fora de escopo | E-mail de falhas | TRANSCRICAO | [09:37] Larissa |
| FDD-EXC-03 | `docs/FDD.md` | Fora de escopo | Rate limiting de saída | TRANSCRICAO | [09:39] Larissa |
| FDD-EXC-04 | `docs/FDD.md` | Fora de escopo | Painel visual | TRANSCRICAO | [09:40] Larissa |
| FDD-EXC-05 | `docs/FDD.md` | Fora de escopo | Arquivamento após ~30 dias | TRANSCRICAO | [09:08] Diego |
| FDD-EXC-06 | `docs/FDD.md` | Fora de escopo | Múltiplos workers e ordem global | TRANSCRICAO | [09:13] Larissa |
| FDD-EXC-07 | `docs/FDD.md` | Fora de escopo | Itens no payload | TRANSCRICAO | [09:43] Diego |
| FDD-EXC-08 | `docs/FDD.md` | Fora de escopo | Exactly-once | TRANSCRICAO | [09:25] Diego |
| FDD-EXC-09 | `docs/FDD.md` | Fora de escopo | Evento na criação do pedido (não discutido) | CODIGO | `src/modules/orders/order.service.ts` |
| FDD-EXC-10 | `docs/FDD.md` | Fora de escopo | Listagem da DLQ (só replay por id foi discutido) | TRANSCRICAO | [09:18] Diego |
| FDD-DADOS-01 | `docs/FDD.md` | Modelo de dados | Tabela webhooks: url, secret, customer_id, ativo | TRANSCRICAO | [09:21] Bruno |
| FDD-DADOS-01-COD | `docs/FDD.md` | Restrição | Json já usado em Customer.address; ids Char(36) | CODIGO | `prisma/schema.prisma` |
| FDD-DADOS-02 | `docs/FDD.md` | Modelo de dados | Tabela webhook_outbox com estados e índices | TRANSCRICAO | [09:08] Diego |
| FDD-DADOS-02-COD | `docs/FDD.md` | Restrição | Sem FK para orders: delete remove pedidos CANCELLED | CODIGO | `src/modules/orders/order.service.ts` |
| FDD-DADOS-03 | `docs/FDD.md` | Modelo de dados | Tabela webhook_dead_letter (payload, motivo, timestamp, replay) | TRANSCRICAO | [09:18] Diego |
| FDD-DADOS-04 | `docs/FDD.md` | Modelo de dados | Tabela webhook_deliveries para o histórico | TRANSCRICAO | [09:34] Marcos |
| FDD-FLX-01 | `docs/FDD.md` | Fluxo | Evento criado na outbox dentro de changeStatus, filtro na inserção | TRANSCRICAO | [09:41] Bruno |
| FDD-FLX-02 | `docs/FDD.md` | Fluxo | Worker: polling 2 s, lote pequeno, ordem por created_at | TRANSCRICAO | [09:09] Diego |
| FDD-FLX-02-ORD | `docs/FDD.md` | Decisão (proposta derivada) | Regra de ordem por (webhook, pedido) para manter ordem sob retry | TRANSCRICAO | [09:12] Diego |
| FDD-FLX-03 | `docs/FDD.md` | Fluxo | Retry com tabela de backoff e MAX_ATTEMPTS | TRANSCRICAO | [09:17] Diego |
| FDD-FLX-04 | `docs/FDD.md` | Fluxo | Envio para DLQ | TRANSCRICAO | [09:18] Diego |
| FDD-FLX-05 | `docs/FDD.md` | Fluxo | Replay ADMIN com auditoria e mesmo event_id | TRANSCRICAO | [09:36] Sofia |
| FDD-FLX-06 | `docs/FDD.md` | Fluxo (proposta derivada) | Recuperação de PROCESSING órfão no startup (at-least-once) | TRANSCRICAO | [09:24] Diego |
| FDD-FLX-07 | `docs/FDD.md` | Fluxo | Rotação de secret com previous_secret e 24 h | TRANSCRICAO | [09:21] Sofia |
| FDD-CONTRATO-01 | `docs/FDD.md` | Contrato | POST ao cliente com payload e 5 headers | TRANSCRICAO | [09:44] Diego |
| FDD-CONTRATO-02 | `docs/FDD.md` | Contrato | POST /api/v1/customers/:customerId/webhooks (secret só na criação) | TRANSCRICAO | [09:31] Marcos |
| FDD-CONTRATO-02-COD | `docs/FDD.md` | Restrição | Rotas montadas sob /api/v1 | CODIGO | `src/app.ts` |
| FDD-CONTRATO-03 | `docs/FDD.md` | Contrato | GET /api/v1/customers/:customerId/webhooks (lista por cliente) | TRANSCRICAO | [09:33] Bruno |
| FDD-CONTRATO-04 | `docs/FDD.md` | Contrato | PATCH /api/v1/webhooks/:id | TRANSCRICAO | [09:33] Bruno |
| FDD-CONTRATO-05 | `docs/FDD.md` | Contrato | DELETE /api/v1/webhooks/:id | TRANSCRICAO | [09:33] Bruno |
| FDD-CONTRATO-06 | `docs/FDD.md` | Contrato | POST /api/v1/webhooks/:id/rotate-secret | TRANSCRICAO | [09:21] Sofia |
| FDD-CONTRATO-07 | `docs/FDD.md` | Contrato | GET /api/v1/webhooks/:id/deliveries (últimas 100) | TRANSCRICAO | [09:34] Marcos |
| FDD-CONTRATO-08 | `docs/FDD.md` | Contrato | POST /api/v1/admin/webhooks/dead-letter/:id/replay | TRANSCRICAO | [09:35] Diego |
| FDD-CONTRATO-09 | `docs/FDD.md` | Contrato | Assinatura de publishWebhookEvent(tx, order, from, to) | TRANSCRICAO | [09:41] Bruno |
| FDD-ERR-01 | `docs/FDD.md` | Erro | WEBHOOK_NOT_FOUND (404) | TRANSCRICAO | [09:28] Bruno |
| FDD-ERR-02 | `docs/FDD.md` | Erro | WEBHOOK_INVALID_URL via mensagem do Zod | TRANSCRICAO | [09:23] Sofia |
| FDD-ERR-03 | `docs/FDD.md` | Erro | WEBHOOK_CUSTOMER_NOT_FOUND (404; nome proposto sob o prefixo decidido) | TRANSCRICAO | [09:29] Larissa |
| FDD-ERR-04 | `docs/FDD.md` | Erro | WEBHOOK_DEAD_LETTER_NOT_FOUND (404; nome proposto, condição do replay) | TRANSCRICAO | [09:18] Diego |
| FDD-ERR-05 | `docs/FDD.md` | Erro | WEBHOOK_REPLAY_ALREADY_PENDING (409, proposta) | TRANSCRICAO | [09:18] Diego |
| FDD-ERR-06 | `docs/FDD.md` | Erro | WEBHOOK_DELIVERY_TIMEOUT (nome proposto; condição: 10 s) | TRANSCRICAO | [09:42] Diego |
| FDD-ERR-07 | `docs/FDD.md` | Erro | WEBHOOK_DELIVERY_FAILED (nome proposto; condição: falha de entrega) | TRANSCRICAO | [09:15] Diego |
| FDD-ERR-08 | `docs/FDD.md` | Erro | WEBHOOK_MAX_ATTEMPTS_EXCEEDED (nome proposto; condição: teto de tentativas) | TRANSCRICAO | [09:17] Larissa |
| FDD-ERR-09 | `docs/FDD.md` | Erro | WEBHOOK_PAYLOAD_TOO_LARGE (nome proposto; condição: > 64 KB) | TRANSCRICAO | [09:24] Larissa |
| FDD-ERR-10 | `docs/FDD.md` | Erro | WEBHOOK_INACTIVE (proposta) | TRANSCRICAO | [09:21] Bruno |
| FDD-ERR-11 | `docs/FDD.md` | Restrição | WEBHOOK_SECRET_REQUIRED sem gatilho: secret é gerado pelo OMS | TRANSCRICAO | [09:31] Marcos |
| FDD-RES-01 | `docs/FDD.md` | Resiliência | Timeout 10 s | TRANSCRICAO | [09:42] Diego |
| FDD-RES-02 | `docs/FDD.md` | Resiliência | 5 tentativas lidas como envio inicial + 5 retentativas (interpretação pendente de Q-01) | TRANSCRICAO | [09:17] Diego |
| FDD-RES-03 | `docs/FDD.md` | Resiliência | Backoff 1m/5m/30m/2h/12h | TRANSCRICAO | [09:17] Diego |
| FDD-RES-04 | `docs/FDD.md` | Resiliência | DLQ e replay ADMIN | TRANSCRICAO | [09:18] Diego |
| FDD-RES-05 | `docs/FDD.md` | Resiliência | Rate limiting em aberto; circuit breaker não adotado (proposta) | TRANSCRICAO | [09:39] Larissa |
| FDD-INV-01 | `docs/FDD.md` | Invariante | Sem status confirmado sem evento | TRANSCRICAO | [09:40] Bruno |
| FDD-INV-02 | `docs/FDD.md` | Invariante | event_id nunca muda | TRANSCRICAO | [09:25] Diego |
| FDD-INV-03 | `docs/FDD.md` | Invariante | Bytes assinados = bytes enviados | TRANSCRICAO | [09:22] Sofia |
| FDD-INV-04 | `docs/FDD.md` | Invariante | Nenhuma rede dentro da transação | TRANSCRICAO | [09:04] Bruno |
| FDD-INV-05 | `docs/FDD.md` | Invariante (derivada) | Secret só devolvido na criação/rotação; nunca em log | TRANSCRICAO | [09:31] Marcos |
| FDD-OBS-01 | `docs/FDD.md` | Observabilidade | Logs estruturados com Pino, auditoria do replay | TRANSCRICAO | [09:29] Bruno |
| FDD-OBS-01-COD | `docs/FDD.md` | Restrição | requestLogger só registra metadados (secret não vaza) | CODIGO | `src/middlewares/request-logger.middleware.ts` |
| FDD-OBS-02 | `docs/FDD.md` | Observabilidade | Métricas derivadas das tabelas; meta de 10 s | TRANSCRICAO | [09:02] Marcos |
| FDD-OBS-03 | `docs/FDD.md` | Observabilidade | Tracing por ids de correlação (sem lib de tracing) | CODIGO | `package.json` |
| FDD-OBS-04 | `docs/FDD.md` | Observabilidade | Alertas de atraso, heartbeat e DLQ (proposta) | TRANSCRICAO | [09:02] Marcos |
| FDD-INT-01 | `docs/FDD.md` | Integração | changeStatus chama publishWebhookEvent após history | CODIGO | `src/modules/orders/order.service.ts` |
| FDD-INT-02 | `docs/FDD.md` | Integração | events usa o enum OrderStatus das transições | CODIGO | `src/modules/orders/order.status.ts` |
| FDD-INT-03 | `docs/FDD.md` | Integração | Erros WEBHOOK_ estendem AppError/ConflictError | CODIGO | `src/shared/errors/http-errors.ts` |
| FDD-INT-04 | `docs/FDD.md` | Integração | errorMiddleware sem alteração | CODIGO | `src/middlewares/error.middleware.ts` |
| FDD-INT-05 | `docs/FDD.md` | Integração | Schemas via validate; código WEBHOOK_ em details | CODIGO | `src/middlewares/validate.middleware.ts` |
| FDD-INT-06 | `docs/FDD.md` | Integração | authenticate e requireRole('ADMIN') | CODIGO | `src/middlewares/auth.middleware.ts` |
| FDD-INT-07 | `docs/FDD.md` | Integração | Routers /webhooks e /admin/webhooks | CODIGO | `src/routes/index.ts` |
| FDD-INT-08 | `docs/FDD.md` | Integração | worker.ts modelado em server.ts | CODIGO | `src/server.ts` |
| FDD-INT-09 | `docs/FDD.md` | Integração | createPrismaClient no worker | CODIGO | `src/config/database.ts` |
| FDD-INT-10 | `docs/FDD.md` | Integração | Variáveis WEBHOOK_* no envSchema | CODIGO | `src/config/env.ts` |
| FDD-INT-11 | `docs/FDD.md` | Integração | redactPaths com secret | CODIGO | `src/shared/logger/index.ts` |
| FDD-INT-12 | `docs/FDD.md` | Integração | Novos modelos Prisma e migration | CODIGO | `prisma/schema.prisma` |
| FDD-INT-13 | `docs/FDD.md` | Integração | Script worker e nenhuma dependência nova | CODIGO | `package.json` |
| FDD-INT-14 | `docs/FDD.md` | Integração | paginated na listagem | CODIGO | `src/shared/http/response.ts` |
| FDD-INT-15 | `docs/FDD.md` | Integração | Limpeza das tabelas novas nos testes | CODIGO | `tests/setup.ts` |
| FDD-INT-16 | `docs/FDD.md` | Restrição | JWT só traz id/email/role; sem vínculo usuário-cliente | CODIGO | `src/middlewares/auth.middleware.ts` |
| FDD-COMP-01 | `docs/FDD.md` | Compatibilidade | Contrato de PATCH /orders/:id/status inalterado | CODIGO | `src/modules/orders/order.routes.ts` |
| FDD-COMP-02 | `docs/FDD.md` | Compatibilidade | Versionamento por event_type (proposta) | TRANSCRICAO | [09:43] Diego |
| FDD-COMP-03 | `docs/FDD.md` | Compatibilidade | Cliente sem webhook não gera linha | TRANSCRICAO | [09:34] Bruno |
| FDD-RISK-01 | `docs/FDD.md` | Risco | Processamento duplicado no cliente | TRANSCRICAO | [09:25] Sofia |
| FDD-RISK-02 | `docs/FDD.md` | Risco | Worker único parado ou lento | TRANSCRICAO | [09:11] Diego |
| FDD-RISK-03 | `docs/FDD.md` | Risco | Vazamento de secret | TRANSCRICAO | [09:22] Diego |
| FDD-RISK-04 | `docs/FDD.md` | Risco | Replay de requisições; X-Timestamp não assinado | TRANSCRICAO | [09:44] Diego |
| FDD-RISK-05 | `docs/FDD.md` | Risco | Rajada de eventos sem rate limiting | TRANSCRICAO | [09:38] Diego |
| FDD-RISK-06 | `docs/FDD.md` | Risco | Bloqueio por regra de ordem | TRANSCRICAO | [09:12] Diego |
| FDD-RISK-07 | `docs/FDD.md` | Risco | Crescimento das tabelas | TRANSCRICAO | [09:07] Bruno |
| FDD-AC-01 | `docs/FDD.md` | Critério de aceite técnico | Outbox criada por webhook ativo | TRANSCRICAO | [09:40] Bruno |
| FDD-AC-02 | `docs/FDD.md` | Critério de aceite técnico | Status não assinado não cria linha | TRANSCRICAO | [09:34] Bruno |
| FDD-AC-03 | `docs/FDD.md` | Critério de aceite técnico | Erro na publicação faz rollback total | TRANSCRICAO | [09:40] Bruno |
| FDD-AC-04 | `docs/FDD.md` | Critério de aceite técnico | Headers e HMAC conferem | TRANSCRICAO | [09:44] Diego |
| FDD-AC-05 | `docs/FDD.md` | Critério de aceite técnico | Intervalos de retry e DLQ | TRANSCRICAO | [09:17] Larissa |
| FDD-AC-06 | `docs/FDD.md` | Critério de aceite técnico | Timeout de 10 s gera retry | TRANSCRICAO | [09:42] Diego |
| FDD-AC-07 | `docs/FDD.md` | Critério de aceite técnico | Replay 403 para OPERATOR e 202 para ADMIN | TRANSCRICAO | [09:36] Larissa |
| FDD-AC-08 | `docs/FDD.md` | Critério de aceite técnico | URL http responde 400 | TRANSCRICAO | [09:23] Sofia |
| FDD-AC-09 | `docs/FDD.md` | Critério de aceite técnico | Corpo > 64 KB gera erro sem envio (destino DLQ é proposta, Q-07) | TRANSCRICAO | [09:24] Larissa |
| FDD-AC-10 | `docs/FDD.md` | Critério de aceite técnico | Assinatura durante a carência (depende de Q-03) | TRANSCRICAO | [09:21] Sofia |
| FDD-AC-11 | `docs/FDD.md` | Critério de aceite técnico | Deliveries com até 100 itens | TRANSCRICAO | [09:34] Marcos |
| FDD-AC-12 | `docs/FDD.md` | Critério de aceite técnico | Worker parado não afeta status; backlog em ordem | TRANSCRICAO | [09:11] Diego |
| FDD-AC-13 | `docs/FDD.md` | Critério de aceite técnico (derivado) | Secret nunca em log | TRANSCRICAO | [09:22] Diego |
| FDD-AC-14 | `docs/FDD.md` | Critério de aceite técnico | Revisão de segurança antes do deploy | TRANSCRICAO | [09:46] Sofia |
| RFC-PROP-02-PRISMA | `docs/RFC.md` | Decisão | PrismaClient próprio no worker, mesma DATABASE_URL | TRANSCRICAO | [09:30] Bruno |
| RFC-PROP-02-SINGLE | `docs/RFC.md` | Restrição | Instância única; ordem só por order_id | TRANSCRICAO | [09:13] Larissa |
| RFC-PROP-03-TIMEOUT | `docs/RFC.md` | Decisão | Timeout de 10 s por chamada | TRANSCRICAO | [09:42] Diego |
| RFC-PROP-03-DLQ | `docs/RFC.md` | Decisão | DLQ em tabela própria | TRANSCRICAO | [09:18] Diego |
| RFC-PROP-03-ADMIN | `docs/RFC.md` | Restrição | Replay restrito a ADMIN | TRANSCRICAO | [09:36] Larissa |
| RFC-PROP-04-TLS | `docs/RFC.md` | Restrição | URLs apenas https | TRANSCRICAO | [09:23] Sofia |
| RFC-PROP-04-SIZE | `docs/RFC.md` | Requisito Não Funcional | Limite de 64 KB | TRANSCRICAO | [09:24] Larissa |
| RFC-PROP-05-WHID | `docs/RFC.md` | Decisão | Header X-Webhook-Id | TRANSCRICAO | [09:44] Sofia |
| RFC-PROP-05-BODY | `docs/RFC.md` | Decisão | Payload enxuto sem itens | TRANSCRICAO | [09:43] Diego |
| RFC-PROP-06-DEL | `docs/RFC.md` | Requisito Funcional | Histórico das últimas 100 entregas | TRANSCRICAO | [09:34] Marcos |
| RFC-PROP-06-ROT | `docs/RFC.md` | Requisito Funcional | Rotação de secret | TRANSCRICAO | [09:21] Sofia |
| RFC-PROP-06-REPLAY | `docs/RFC.md` | Requisito Funcional | Replay de DLQ com ADMIN | TRANSCRICAO | [09:36] Larissa |
| RFC-IMP-02-CFG | `docs/RFC.md` | Impacto | Tabela de configuração de webhooks | TRANSCRICAO | [09:21] Bruno |
| RFC-IMP-02-DLQ | `docs/RFC.md` | Impacto | Tabela webhook_dead_letter | TRANSCRICAO | [09:18] Diego |
| RFC-IMP-02-DEL | `docs/RFC.md` | Impacto (derivado) | Tabela de histórico de entregas, derivada do requisito | TRANSCRICAO | [09:34] Marcos |
| PRD-NFR-08-SECRET | `docs/PRD.md` | Requisito Não Funcional | Secret exclusivo por webhook | TRANSCRICAO | [09:21] Sofia |
| PRD-NFR-09-ADMIN | `docs/PRD.md` | Requisito Não Funcional | Replay somente ADMIN | TRANSCRICAO | [09:36] Larissa |
| PRD-RISK-05-JWT | `docs/PRD.md` | Restrição | customer_id não vem do JWT | TRANSCRICAO | [09:32] Larissa |
| PRD-RISK-05-COD | `docs/PRD.md` | Restrição | Schema sem vínculo User-Customer | CODIGO | `prisma/schema.prisma` |
| PRD-AC-03-HDR | `docs/PRD.md` | Critério de aceitação | Headers X-Event-Id, X-Signature e X-Timestamp | TRANSCRICAO | [09:44] Diego |
| PRD-AC-03-SIG | `docs/PRD.md` | Critério de aceitação | Assinatura válida | TRANSCRICAO | [09:22] Sofia |
| FDD-FLX-01-FILTER | `docs/FDD.md` | Fluxo | Filtro de status aplicado na inserção | TRANSCRICAO | [09:34] Bruno |
| FDD-FLX-01-COD | `docs/FDD.md` | Restrição | Ponto de inserção após orderStatusHistory.create | CODIGO | `src/modules/orders/order.service.ts` |
| FDD-FLX-02-BATCH | `docs/FDD.md` | Fluxo | Lote pequeno dos pendentes | TRANSCRICAO | [09:08] Diego |
| FDD-FLX-02-ORDER | `docs/FDD.md` | Fluxo | Processamento por ordem de created_at | TRANSCRICAO | [09:12] Diego |
| FDD-FLX-05-EVID | `docs/FDD.md` | Fluxo (proposta derivada) | Replay mantém o mesmo event_id (id único por evento; ver Q-11) | TRANSCRICAO | [09:25] Diego |
| FDD-CONTRATO-01-WHID | `docs/FDD.md` | Contrato | Header X-Webhook-Id | TRANSCRICAO | [09:44] Sofia |
| FDD-CONTRATO-01-BODY | `docs/FDD.md` | Contrato | Campos do payload | TRANSCRICAO | [09:43] Diego |
| FDD-CONTRATO-02-PATH | `docs/FDD.md` | Decisão (proposta) | customerId no path (body ou path admitidos) | TRANSCRICAO | [09:32] Larissa |
| FDD-ERR-02-COD | `docs/FDD.md` | Restrição | validate só emite VALIDATION_ERROR; código em details | CODIGO | `src/middlewares/validate.middleware.ts` |
| FDD-OBS-01-AUDIT | `docs/FDD.md` | Observabilidade | Log de auditoria de quem fez o replay | TRANSCRICAO | [09:36] Sofia |
| FDD-AC-14-COD | `docs/FDD.md` | Critério de aceite técnico | Scripts test, lint e build existentes | CODIGO | `package.json` |
| FDD-AC-14-SPRINT | `docs/FDD.md` | Restrição | Testes ponta a ponta na estimativa | TRANSCRICAO | [09:46] Larissa |
| RFC-IMP-01-ROWS | `docs/RFC.md` | Impacto (proposta derivada) | Uma linha por webhook de destino; Diego falou em uma linha com o evento | TRANSCRICAO | [09:06] Diego |
| RFC-Q-11 | `docs/RFC.md` | Questão em aberto | Replay reutiliza o event_id? 'recoloca na outbox' vs id gerado na entrada | TRANSCRICAO | [09:18] Diego |
| RFC-Q-11-ID | `docs/RFC.md` | Questão em aberto | UUID gerado quando o evento entra na outbox, único por evento | TRANSCRICAO | [09:25] Diego |
| ADR-001-CONS-CONSIST | `docs/adrs/ADR-001-outbox-no-mysql.md` | Trade-off | Consistência: commit registra o evento, rollback o remove | TRANSCRICAO | [09:06] Diego |
| ADR-001-CONS-INFRA | `docs/adrs/ADR-001-outbox-no-mysql.md` | Trade-off | Sem infra nova: outbox no MySQL existente | TRANSCRICAO | [09:07] Diego |
| ADR-001-CONS-POLL | `docs/adrs/ADR-001-outbox-no-mysql.md` | Trade-off | Custo: leitura por polling | TRANSCRICAO | [09:09] Diego |
| RFC-ALT-04-INF | `docs/RFC.md` | Alternativa descartada | Retry indefinido: evento pendurado para sempre | TRANSCRICAO | [09:15] Diego |
| PRD-AC-03-WHID | `docs/PRD.md` | Critério de aceitação | Header X-Webhook-Id | TRANSCRICAO | [09:44] Sofia |
| FDD-FLX-05-REPLAY | `docs/FDD.md` | Fluxo | Replay recoloca o evento na outbox como pendente | TRANSCRICAO | [09:18] Diego |
| FDD-DADOS-02-ROWS | `docs/FDD.md` | Modelo de dados (proposta derivada) | Uma linha por webhook de destino, mesmo event_id | TRANSCRICAO | [09:06] Diego |
