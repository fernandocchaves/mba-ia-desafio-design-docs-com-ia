# ADR-006: Reuso dos padrões existentes do projeto no módulo de webhooks

**Status:** Aceito
**Data:** 2026-11-15 (decisão tomada na reunião técnica de quinta-feira, [09:30])
**ADRs relacionadas:** [ADR-002](ADR-002-worker-separado-com-polling.md), [ADR-003](ADR-003-retry-com-backoff-e-dlq.md)

---

## Contexto

O OMS já tem convenções consolidadas: módulos de domínio com camadas fixas, hierarquia de erros com códigos estáveis, validação com Zod, logger estruturado e um middleware de erro central. A feature de webhooks introduz um módulo novo e um processo novo (o worker). Era preciso decidir se ela seguiria essas convenções ou se traria ferramentas próprias.

O que existe hoje:

- **Módulos:** cada domínio em `src/modules/<domínio>/` com `*.controller.ts`, `*.service.ts`, `*.repository.ts`, `*.routes.ts` e `*.schemas.ts` (por exemplo, `src/modules/orders/`). Os routers são montados em `src/routes/index.ts`, e as dependências são instanciadas em `buildControllers` (`src/app.ts`).
- **Erros:** `AppError` (`src/shared/errors/app-error.ts`) carrega `statusCode`, `errorCode` e `details`. As subclasses em `src/shared/errors/http-errors.ts` usam códigos em caixa alta, como `INSUFFICIENT_STOCK` e `INVALID_STATUS_TRANSITION`.
- **Tratamento central:** `errorMiddleware` (`src/middlewares/error.middleware.ts`) converte `AppError`, `ZodError` e erros conhecidos do Prisma (`P2002` e `P2025`) no envelope `{ error: { code, message, details? } }`.
- **Validação:** `validate` (`src/middlewares/validate.middleware.ts`) aplica schemas Zod a body, query e params.
- **Log:** Pino (`src/shared/logger/index.ts`), com `redact` de campos sensíveis.
- **Autorização:** `authenticate` e `requireRole` (`src/middlewares/auth.middleware.ts`).

## Fatores de decisão

- Consistência para quem já trabalha na base ([09:27] Bruno).
- Nenhuma dependência nova sem necessidade: "Não vamos botar nada novo" ([09:29] Bruno).
- Erros do módulo tratados pelo middleware existente, "sem precisar mudar nada" ([09:29] Bruno).
- Prazo de três sprints ([09:46] Larissa).

## Decisão

Reuso máximo do que já existe ([09:30] Larissa):

- **Módulo `src/modules/webhooks/`** com controller, service, repository, routes e schemas, como os demais ([09:27] Bruno). A lógica de entrega fica em `webhook.worker.ts` ou `webhook.processor.ts` dentro do módulo, e o entrypoint do processo fica em `src/worker.ts` ([09:28] Bruno).
- **Erros como subclasses de `AppError`,** com códigos prefixados por `WEBHOOK_`, por exemplo `WEBHOOK_NOT_FOUND` e `WEBHOOK_INVALID_URL` ([09:28] Bruno, [09:29] Larissa).
- **Validação com schemas Zod** no padrão de `*.schemas.ts` e o middleware `validate` ([09:30] Larissa).
- **Log com o Pino existente,** sem biblioteca nova ([09:29] Bruno).
- **`errorMiddleware` sem alteração:** como os novos erros estendem `AppError`, ele já os serializa ([09:29] Bruno).
- **`requireRole('ADMIN')`** no endpoint de replay ([09:36] Larissa).
- **Ids UUID,** como no resto do schema ([09:51] Larissa).

Dois detalhes do código condicionam a aplicação dessa decisão (o FDD os trata em "Integração com o sistema existente"):

1. `NotFoundError` fixa o código `NOT_FOUND`, sem parâmetro de código. Por isso, `WEBHOOK_NOT_FOUND` deve estender `AppError` diretamente. Já `ConflictError` e `UnprocessableEntityError` aceitam um código customizado.
2. `validate` converte qualquer `ZodError` em `ValidationError`, com código fixo `VALIDATION_ERROR`. Uma regra de schema, como a de HTTPS ([09:23] Sofia), não produz `WEBHOOK_INVALID_URL` como `error.code`. O FDD define como o código `WEBHOOK_` é exposto mantendo o middleware compartilhado intacto.

## Alternativas Consideradas

### A. Infraestrutura própria para o módulo (descartada; ver a fala sobre o logger)

Biblioteca de log, formato de erro ou camada de validação próprios para webhooks e para o worker.

- Pró: liberdade para otimizar o worker.
- Contra: duplica padrões, cria um segundo formato de erro para os mesmos clientes da API e aumenta a superfície de revisão. Foi descartada pela diretriz explícita de não acrescentar nada novo ([09:29] Bruno, [09:30] Larissa).

### B. Reaproveitar os códigos genéricos (`NOT_FOUND`, `CONFLICT`) sem prefixo (alternativa plausível, não levantada na reunião)

- Pró: zero classes novas.
- Contra: o cliente da API não distingue um erro de webhook de outros. É o caminho que o próprio código induz para 404, já que `NotFoundError` fixa `NOT_FOUND`, mas o time fixou o prefixo `WEBHOOK_` para tudo do módulo ([09:28] Bruno, [09:29] Larissa).

### C. Reuso dos padrões existentes (escolhida)

- Pró: consistência, nenhuma dependência nova e revisão mais simples.
- Contra: herda as limitações das classes existentes, descritas acima.

## Consequências

**Positivas**

- Curva de aprendizado mínima para o time de Pedidos e para a revisão de segurança.
- Os erros do módulo saem no mesmo envelope JSON e com os mesmos status HTTP que o resto da API.
- O worker reaproveita o logger, a configuração (`src/config/env.ts`) e a criação do Prisma client (`src/config/database.ts`).

**Negativas**

- As limitações do código existente, como `NotFoundError` com código fixo e `validate` com código fixo, exigem pequenas adaptações no módulo, documentadas no FDD.
- O projeto não tem biblioteca de métricas nem de tracing (`package.json`). Reusar só o que existe significa que a observabilidade inicial se apoia em logs estruturados e em consultas às tabelas.

**Trade-off explícito:** prioriza-se a consistência e a velocidade de entrega sobre recursos que exigiriam dependências novas, como métricas nativas e tracing distribuído.

## Referências

- `src/shared/errors/app-error.ts` e `src/shared/errors/http-errors.ts`
- `src/middlewares/error.middleware.ts` e `src/middlewares/validate.middleware.ts`
- `src/routes/index.ts` e `src/app.ts`
- `src/shared/logger/index.ts`
- `TRANSCRICAO.md`: [09:27] a [09:30], [09:36], [09:51]
