### PRD: Sistema de Webhooks de Notificação de Pedidos

Versão: v1

Data: 2026-11-15

Responsável: Fernando Cezar Chaves, a partir da reunião com Marcos (Product Manager) e Larissa (Tech Lead)

Documentos relacionados: [RFC](RFC.md) · [FDD](FDD.md) · [ADRs](adrs/) · [Tracker](TRACKER.md)

Os identificadores entre colchetes, como **[PRD-FR-01]**, são as chaves do [Tracker](TRACKER.md), que liga cada item à fala da reunião ou ao arquivo de código de origem.

---

### Resumo e contexto

**[PRD-SUM-01]** Esta feature permite que clientes B2B do Order Management System (OMS) sejam **avisados automaticamente, por webhook, quando o status de um pedido muda**. O cliente cadastra uma URL HTTPS e escolhe os status que quer receber. A partir daí, o OMS envia a ele um aviso assinado a cada mudança de status relevante, em menos de 10 segundos, com retentativas automáticas se o sistema do cliente estiver fora do ar.

**[PRD-SUM-02]** O OMS já controla o ciclo de vida do pedido com uma máquina de estados: `PENDING`, `PAID`, `PROCESSING`, `SHIPPED`, `DELIVERED` e `CANCELLED` (`src/modules/orders/order.status.ts`). Cada mudança de status é auditada em histórico (`order_status_history`). O sistema, porém, não tem nenhum mecanismo de notificação externa: quem quer saber de uma mudança precisa perguntar.

---

### Problema e motivação

**[PRD-PROB-01]** Três clientes B2B (Atlas Comercial, MaxDistribuição e Nova Cargo) fizeram um pedido formal para serem notificados quando o status dos seus pedidos muda ([09:00] Marcos).

**[PRD-PROB-02]** Hoje esses clientes consultam `GET /orders` periodicamente para descobrir se algo mudou. Isso deixa a integração **lenta e cara** para eles ([09:00] Marcos).

**[PRD-PROB-03]** Há risco comercial: a Atlas sinalizou que pode migrar para um concorrente se a solução não for entregue até o fim do trimestre ([09:00] Marcos), e pediu entrega para o fim de novembro ([09:45] Marcos).

---

### Público-alvo e cenários de uso

**Público-alvo**

- **Clientes B2B integrados por API**, inicialmente Atlas Comercial, MaxDistribuição e Nova Cargo, que querem **receber** avisos e não enviá-los ([09:02] Marcos).
- **Usuários do OMS que representam esses clientes**, que cadastram e mantêm os webhooks pela API do OMS, autenticados com o JWT do sistema ([09:32] Marcos).
- **Administradores do OMS**, que reprocessam entregas que falharam definitivamente ([09:36] Sofia).

**Cenários de uso**

- **[PRD-CEN-01]** Um pedido da Nova Cargo passa a `SHIPPED`. Em poucos segundos, o sistema da Nova Cargo recebe o aviso, sem precisar consultar o OMS.
- **[PRD-CEN-02]** A Atlas só quer saber quando o pedido vira `SHIPPED` ou `DELIVERED` e cadastra um webhook com esses dois status ([09:33] Marcos).
- **[PRD-CEN-03]** O sistema da MaxDistribuição fica duas horas fora do ar em manutenção planejada. Os avisos do período são reenviados automaticamente quando ele volta ([09:16] Diego).
- **[PRD-CEN-04]** Um cliente suspeita que o secret vazou e pede um novo pela API. O antigo continua aceito por 24 horas enquanto ele atualiza os sistemas ([09:21] Sofia).
- **[PRD-CEN-05]** Um cliente quer entender por que não recebeu um aviso e consulta o histórico das últimas entregas, com resultado, resposta e tempo ([09:34] Marcos).
- **[PRD-CEN-06]** Um cliente ficou fora do ar por mais tempo que a janela de retentativas. Um administrador reenvia manualmente os avisos que falharam ([09:18] Diego).

---

### Objetivos e métricas de sucesso

| ID | Objetivo | Métrica | Meta | Origem |
|---|---|---|---|---|
| PRD-OBJ-01 | Notificar em "tempo real" na percepção do cliente | Tempo entre a mudança de status e a entrega bem-sucedida, quando o endpoint do cliente está disponível | **Abaixo de 10 segundos** | [09:02] Marcos |
| PRD-OBJ-02 | Atender no prazo o cliente sob risco de churn | Data em que a funcionalidade entra em produção | Até o **fim de novembro**, prazo pedido pela Atlas | [09:45] Marcos, [09:00] Marcos |
| PRD-OBJ-03 | Não perder avisos por indisponibilidade curta do cliente | Avisos não entregues durante indisponibilidades de até cerca de 14 h 36 min (janela de retentativas) | **0** perdidos sem intervenção | [09:17] Diego, [09:17] Marcos |
| PRD-OBJ-04 | Entregar no prazo planejado | Sprints até o deploy, incluindo a revisão de segurança | **3 sprints** | [09:46] Larissa, [09:47] Larissa |

Indicador de acompanhamento, sem meta definida na reunião: volume de consultas a `GET /orders` dos três clientes antes e depois do lançamento, que mede o problema de polling descrito em [09:00] Marcos. A linha de base deve ser medida antes do lançamento.

---

### Escopo

**Incluso**

- Cadastro, listagem, edição e remoção de webhooks por cliente ([09:31] Marcos, [09:33] Bruno)
- Escolha dos status de pedido que cada webhook recebe ([09:33] Marcos)
- Aviso automático a cada mudança de status de pedido ([09:00] Marcos)
- Assinatura de cada aviso e secret exclusivo por webhook, com rotação ([09:22] Sofia)
- Retentativas automáticas e fila de falhas definitivas com reenvio manual ([09:17] Larissa, [09:18] Diego)
- Histórico das últimas 100 entregas por webhook ([09:34] Marcos)

**Fora de escopo** (descartado ou adiado na reunião)

| ID | Item | Situação | Origem |
|---|---|---|---|
| PRD-OUT-01 | **Aviso por e-mail** ao cliente quando o webhook dele falha repetidamente | Adiado para a próxima fase, depois de medir o impacto | [09:37] Marcos, [09:37] Larissa |
| PRD-OUT-02 | **Painel visual** (dashboard) para o cliente ver os webhooks | Descartado nesta fase; é projeto separado do time de frontend | [09:39] Marcos, [09:40] Larissa |
| PRD-OUT-03 | **Rate limiting** do envio para o cliente | Adiado: "observar e decidir depois" | [09:38] Diego, [09:39] Larissa |
| PRD-OUT-04 | **Webhooks de entrada** (cliente enviando ao OMS) | Fora do escopo: só saída | [09:02] Marcos, [09:03] Sofia |
| PRD-OUT-05 | **Garantia de ordem global** e múltiplos workers em paralelo | Adiado; a ordem vale por pedido, com um único worker | [09:13] Diego, [09:14] Marcos |
| PRD-OUT-06 | **Arquivamento** das notificações entregues após cerca de 30 dias | Fora do escopo desta feature | [09:08] Diego |
| PRD-OUT-07 | **Itens do pedido no aviso** | Descartado para manter o payload enxuto; o cliente consulta `GET /orders/:id` | [09:43] Diego |
| PRD-OUT-08 | **Entrega exactly-once** | Descartada; a garantia é at-least-once | [09:25] Diego |

---

### Requisitos funcionais

| ID | Requisito | Origem |
|---|---|---|
| PRD-FR-01 | O usuário autenticado **cadastra um webhook** para um cliente informando a URL e a lista de status que quer receber. O OMS **gera o secret** e o devolve na resposta de criação | [09:31] Marcos |
| PRD-FR-02 | O cliente associado ao webhook é **informado na requisição** (body ou path; o FDD propõe path) e **não é inferido do JWT**, que identifica o usuário operador | [09:32] Larissa |
| PRD-FR-03 | O usuário **lista os webhooks de um cliente** | [09:33] Bruno |
| PRD-FR-04 | O usuário **edita** um webhook (URL, status assinados e estado ativo) | [09:33] Bruno, [09:21] Bruno |
| PRD-FR-05 | O usuário **remove** um webhook | [09:33] Bruno |
| PRD-FR-06 | Cada webhook recebe **apenas os status que escolheu**. Se nenhum webhook do cliente quer aquele status, nenhum aviso é gerado | [09:33] Marcos, [09:34] Bruno |
| PRD-FR-07 | A cada mudança de status de pedido, o OMS **envia um aviso** ao webhook com o identificador do evento, o tipo `order.status_changed`, o momento da mudança, o pedido (id e número), o status anterior e o novo, o cliente e o valor total. O aviso **não inclui os itens** | [09:43] Diego |
| PRD-FR-08 | Cada aviso traz **identificação no cabeçalho**: id do evento, id do webhook, momento do envio e assinatura | [09:44] Diego, [09:44] Sofia |
| PRD-FR-09 | Cada aviso é **assinado com HMAC-SHA256** usando um secret exclusivo do webhook, para o cliente validar a origem e a integridade | [09:20] Sofia, [09:21] Sofia |
| PRD-FR-10 | O usuário **solicita um novo secret** pela API, e o anterior continua válido por **24 horas** | [09:21] Sofia |
| PRD-FR-11 | O OMS **recusa URLs que não sejam HTTPS** com erro de validação | [09:23] Sofia |
| PRD-FR-12 | Se a entrega falhar, o OMS **retenta automaticamente** após 1 min, 5 min, 30 min, 2 h e 12 h | [09:17] Diego, [09:17] Larissa |
| PRD-FR-13 | Esgotadas as tentativas, o aviso vai para uma **fila de falhas** que guarda o conteúdo, o motivo e o momento da falha | [09:18] Diego |
| PRD-FR-14 | Um **administrador reenvia** manualmente um aviso da fila de falhas, e o OMS **registra quem fez o reenvio** | [09:18] Diego, [09:36] Sofia |
| PRD-FR-15 | O usuário consulta o **histórico das últimas 100 entregas** de um webhook, com sucesso ou falha, conteúdo enviado, resposta do cliente e tempo de resposta | [09:34] Marcos |

---

### Requisitos não funcionais

| ID | Categoria | Requisito | Origem |
|---|---|---|---|
| PRD-NFR-01 | Latência | Entrega em menos de 10 s; o ciclo de leitura de 2 s pode somar até 2 s de espera, o que foi aceito | [09:02] Marcos, [09:10] Larissa |
| PRD-NFR-02 | Isolamento | A lentidão ou indisponibilidade de um cliente **não pode atrasar nem impedir** a mudança de status de pedidos | [09:04] Bruno |
| PRD-NFR-03 | Consistência | Toda mudança de status confirmada que deve gerar aviso gera o aviso; se a mudança for desfeita, o aviso também é | [09:06] Diego, [09:40] Bruno |
| PRD-NFR-04 | Garantia de entrega | **At-least-once**: o cliente pode receber o mesmo aviso mais de uma vez e deduplica pelo id do evento | [09:24] Diego, [09:26] Larissa |
| PRD-NFR-05 | Ordem | Os avisos de um mesmo pedido chegam na ordem das mudanças; não há ordem global entre pedidos | [09:12] Diego, [09:13] Larissa |
| PRD-NFR-06 | Tempo de resposta do cliente | O cliente tem **10 s** para responder; acima disso, a tentativa conta como falha | [09:42] Diego |
| PRD-NFR-07 | Tamanho | Aviso limitado a **64 KB**; acima disso, ele não é enviado e gera erro, sem truncar | [09:23] Sofia, [09:24] Larissa |
| PRD-NFR-08 | Segurança | Secret **exclusivo por webhook**, nunca global; transporte apenas por **TLS** | [09:21] Sofia, [09:23] Sofia |
| PRD-NFR-09 | Autorização | Gestão de webhooks para **qualquer usuário autenticado**; reenvio da fila de falhas **somente `ADMIN`** | [09:37] Sofia, [09:36] Sofia |
| PRD-NFR-10 | Disponibilidade | O envio roda em **processo separado** da API: reiniciar a API não interrompe as entregas | [09:11] Diego |
| PRD-NFR-11 | Infraestrutura | **Nenhuma infraestrutura nova**: mesmo banco MySQL e mesma stack | [09:07] Diego, [09:11] Diego |
| PRD-NFR-12 | Padrões | Seguir os padrões do projeto: módulos, erros com código (prefixo `WEBHOOK_`), logger e validação existentes | [09:30] Larissa |

---

### Decisões e trade-offs principais

Cada decisão tem um ADR com contexto, alternativas e consequências.

### Decisão: registrar o aviso no próprio banco, junto com a mudança de status ([ADR-001](adrs/ADR-001-outbox-no-mysql.md))

- **Justificativa:** garante que status e aviso nunca divirjam e não exige infraestrutura nova ([09:06] Diego, [09:07] Diego)
- **Trade-off:** o aviso deixa de ser instantâneo e passa a depender de um processo que lê a fila a cada 2 s ([09:10] Larissa)

### Decisão: retentar por cerca de 15 horas e depois exigir reenvio manual ([ADR-003](adrs/ADR-003-retry-com-backoff-e-dlq.md))

- **Justificativa:** cobre indisponibilidades de horas, como a manutenção de 2 h que já aconteceu, sem deixar avisos pendurados para sempre ([09:16] Diego, [09:15] Diego)
- **Trade-off:** um cliente fora do ar por mais de cerca de 15 h perde os avisos automáticos, o que o PM considerou aceitável ([09:17] Marcos)

### Decisão: o cliente pode receber avisos repetidos ([ADR-005](adrs/ADR-005-entrega-at-least-once-com-x-event-id.md))

- **Justificativa:** é o padrão de mercado (Stripe, GitHub) e muito mais simples que garantir entrega única ([09:25] Diego)
- **Trade-off:** a responsabilidade de deduplicar fica com o cliente ([09:25] Sofia), mitigada por documentação no portal ([09:26] Marcos)

### Decisão: secret exclusivo por webhook, com rotação ([ADR-004](adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md))

- **Justificativa:** um vazamento afeta um único cliente ([09:21] Sofia)
- **Trade-off:** mais gestão de segredos e um período de 24 h com dois secrets válidos

As demais decisões estão em [ADR-002](adrs/ADR-002-worker-separado-com-polling.md) (processo separado e polling), [ADR-006](adrs/ADR-006-reuso-dos-padroes-do-projeto.md) (reuso dos padrões) e [ADR-007](adrs/ADR-007-snapshot-do-payload-na-insercao.md) (conteúdo fixado no momento da mudança).

---

### Dependências

### [PRD-DEP-01] Dependência organizacional: revisão de segurança

A Sofia precisa de **pelo menos dois dias úteis** para revisar o código de assinatura e de geração de secret antes do deploy ([09:46] Sofia, [09:49] Sofia). A revisão está incluída nas três sprints ([09:47] Larissa).

### [PRD-DEP-02] Dependência de produto: documentação no portal do desenvolvedor

O Marcos documenta no portal como integrar via API, com destaque para a deduplicação pelo id do evento ([09:26] Marcos, [09:40] Marcos). Sem isso, o cliente não sabe validar a assinatura nem tratar avisos repetidos.

### [PRD-DEP-03] Dependência comercial: confirmação de prazo com os clientes

O Marcos confirma o prazo com a Atlas e atualiza os três clientes ([09:47] Marcos, [09:49] Marcos).

### [PRD-DEP-04] Dependência técnica: novo processo no deploy

O envio roda num processo próprio, que precisa ser executado e mantido no ambiente junto com a API ([09:11] Diego, [09:11] Larissa).

---

### Riscos e mitigação

### [PRD-RISK-01] Não entregar até o fim de novembro e perder a Atlas

- **Probabilidade:** média (três sprints estimadas, com revisão de segurança no fim)
- **Impacto:** alto (risco de migração da Atlas para um concorrente, [09:00] Marcos)
- **Mitigação:**
    - Escopo fechado na reunião, com e-mail, painel e rate limiting fora ([09:48] Larissa)
    - Revisão de segurança reservada no plano ([09:46] Sofia)
- **Plano de contingência:** comunicação antecipada do prazo aos clientes pelo PM ([09:47] Marcos)

### [PRD-RISK-02] Cliente processar o mesmo aviso duas vezes

- **Probabilidade:** média
- **Impacto:** médio (ação repetida no sistema do cliente)
- **Mitigação:**
    - Id único do evento em todo aviso ([09:25] Diego)
    - Documentação destacada no portal ([09:26] Marcos)
- **Plano de contingência:** o histórico de entregas mostra cada tentativa de um mesmo evento

### [PRD-RISK-03] Cliente fora do ar por mais de cerca de 15 horas

- **Probabilidade:** baixa
- **Impacto:** médio (avisos do período param na fila de falhas)
- **Mitigação:**
    - Janela de retentativas de cerca de 15 h ([09:17] Diego)
- **Plano de contingência:** reenvio manual por administrador ([09:18] Diego); aviso por e-mail numa próxima fase ([09:37] Larissa)

### [PRD-RISK-04] Vazamento do secret pelo cliente

- **Probabilidade:** média (já aconteceu com um cliente, [09:22] Diego)
- **Impacto:** médio (avisos falsos para aquele cliente)
- **Mitigação:**
    - Secret exclusivo por webhook ([09:21] Sofia)
    - Rotação pelo próprio cliente, com 24 h de transição ([09:21] Sofia)
- **Plano de contingência:** rotação imediata

### [PRD-RISK-05] Qualquer usuário autenticado gerencia webhooks de qualquer cliente

- **Probabilidade:** média
- **Impacto:** médio (um usuário pode alterar a URL de outro cliente)
- **Mitigação:**
    - Decisão consciente para esta fase ([09:37] Sofia); o OMS hoje não associa usuário a cliente (`prisma/schema.prisma`)
- **Plano de contingência:** endurecer as permissões numa fase seguinte ([09:37] Sofia)

---

### Critérios de aceitação

- **[PRD-AC-01]** Um usuário autenticado cadastra um webhook HTTPS para um cliente e recebe o secret na resposta.
- **[PRD-AC-02]** O cadastro com URL `http://` é recusado com erro de validação.
- **[PRD-AC-03]** Quando um pedido muda para um status assinado, o webhook recebe o aviso em menos de 10 s, com id do evento, id do webhook, momento do envio e assinatura válida.
- **[PRD-AC-04]** Quando o pedido muda para um status não assinado, nenhum aviso é enviado.
- **[PRD-AC-05]** Se a mudança de status falhar e for desfeita, nenhum aviso é enviado.
- **[PRD-AC-06]** Com o endpoint do cliente fora do ar, o aviso é retentado em 1 min, 5 min, 30 min, 2 h e 12 h e depois aparece na fila de falhas com o motivo.
- **[PRD-AC-07]** Somente um `ADMIN` consegue reenviar um aviso da fila de falhas, e o reenvio fica registrado com o autor.
- **[PRD-AC-08]** Depois de rotacionar o secret, o cliente consegue validar os avisos com o secret antigo por 24 h.
- **[PRD-AC-09]** O histórico mostra as últimas 100 entregas com resultado, resposta e tempo.
- **[PRD-AC-10]** A mudança de status de pedidos continua funcionando normalmente quando o endpoint do cliente está lento ou fora do ar.

---

### Estratégia de testes e validação

**Tipos de teste obrigatórios**

- **Unitários:**
  - montagem do aviso;
  - assinatura HMAC;
  - cálculo dos intervalos de retentativa;
  - filtro de status.
- **[PRD-TEST-01] Integração** (Vitest + Supertest contra MySQL real, como os testes atuais em `tests/orders.test.ts`):
  - CRUD de webhooks;
  - geração do aviso junto com a mudança de status;
  - rollback conjunto;
  - reenvio restrito a `ADMIN`.
- **Ponta a ponta do envio:** o processo de entrega contra um servidor HTTP de teste que simula o cliente:
  - sucesso;
  - erro;
  - lentidão acima de 10 s;
  - fila de falhas;
  - rotação de secret.
- **Segurança:** revisão manual da Sofia sobre assinatura e geração de secret antes do deploy ([09:46] Sofia).

**Estratégia de validação**

- **[PRD-TEST-02]** Revisão do desenho com Bruno e Diego antes do início da implementação ([09:50] Larissa).
- Validação dos critérios de aceitação acima em homologação, antes de liberar para os três clientes ([09:47] Marcos).
- Acompanhamento das métricas de latência e da fila de falhas descritas no [FDD](FDD.md#8-observabilidade) depois do lançamento.
