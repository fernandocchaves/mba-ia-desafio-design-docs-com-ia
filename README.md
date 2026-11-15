# Da Reunião ao Documento: Design Docs do Sistema de Webhooks de Pedidos

Pacote de design docs da feature **Sistema de Webhooks de Notificação de Pedidos** do Order Management System (OMS). Foi produzido com IA a partir da transcrição da reunião técnica ([`TRANSCRICAO.md`](TRANSCRICAO.md)) e do código da aplicação. O enunciado original está no [repositório base](https://github.com/devfullcycle/mba-ia-desafio-design-docs-com-ia).

## Sobre o desafio

Uma empresa que opera um OMS em produção (Node.js, TypeScript, Express, Prisma e MySQL) decidiu, numa call de cerca de 55 minutos entre tech lead, PM, engenheiros e segurança, construir webhooks que avisam clientes B2B quando o status de um pedido muda. Nada foi registrado além da transcrição. A tarefa foi transformar essa conversa, junto com o código existente, em documentação acionável: PRD, RFC, FDD, de 5 a 8 ADRs e um tracker que liga cada item à fala ou ao arquivo de origem.

O desafio não é escrever muito, e sim **não escrever o que ninguém disse**. A reunião mistura decisões fechadas, ideias descartadas, itens adiados e pontos que ficaram ambíguos. O trabalho principal foi separar essas categorias e cruzá-las com o que o código realmente permite. Nenhum arquivo da aplicação (`src/`, `prisma/`, `tests/` ou configurações) foi alterado.

## Ferramentas de IA utilizadas

| Ferramenta | Papel |
|---|---|
| **Claude (Opus 5.5), como agente de código no terminal (OpenCode)** | Leu o código e a transcrição, levantou as decisões, alternativas e ambiguidades e redigiu os documentos. Também escreveu os scripts de geração e verificação do tracker. |
| **Subagente Claude independente (revisor)** | Fez a revisão crítica, em sessão separada e sem acesso ao raciocínio de quem escreveu, de cada linha do tracker contra o texto literal da fala citada. Rodou em duas passadas. |
| **Prompts do curso (Módulo 3, Design Docs com IA)** | Serviram de base de formato: o esqueleto do FDD do "Prompt para geração de um FDD", o PRD do "Exemplo de PRD para Feature (Catálogo de eCommerce)" e as regras MADR do "Prompt para geração de ADR". O curso não traz modelo de RFC, então ele segue as seções do enunciado. |
| **Python (script gerado pela IA)** | [`docs/tools/verificar_rastreabilidade.py`](docs/tools/verificar_rastreabilidade.py) automatiza a checagem anti-alucinação descrita abaixo. |

O repositório de referência de outro aluno, indicado como consulta, **não foi usado**: o pacote foi escrito do zero a partir da transcrição e do código.

## Workflow adotado

1. **Contexto completo antes de escrever.** A transcrição foi lida inteira, assim como todo o código que a feature toca:
   - `order.service.ts` e `order.status.ts`;
   - a hierarquia de erros em `src/shared/errors/`;
   - os middlewares de auth, validação, erro e log;
   - `app.ts`, `routes/index.ts`, `server.ts`, `config/` e o schema Prisma;
   - os testes.

   Os modelos do curso também foram lidos antes de escrever.
2. **Inventário da reunião por categoria.** Cada fala relevante foi classificada como decisão, requisito, restrição, alternativa descartada, item adiado ou ponto ambíguo, sempre com o `[hh:mm] Nome` de origem.
3. **Leitura cruzada com o código.** Antes de escrever, foi conferido onde o que a reunião decidiu esbarra no código real. Esses achados viraram decisões de implementação ou questões em aberto (ver "Iterações e ajustes").
4. **Ordem de produção**, a sugerida pelo enunciado: **ADRs** (o esqueleto de decisões) → **RFC** (proposta, alternativas e questões em aberto, apontando para os ADRs) → **FDD** (implementação) → **PRD** (consolidação de produto) → **TRACKER** → **README**.
5. **IDs em tudo.** Cada item dos documentos recebeu um ID entre colchetes, como `[PRD-FR-07]` ou `[FDD-CONTRATO-03]`. É assim que o tracker e a verificação automática encontram os itens.
6. **Verificação em duas camadas.**
   - **Estrutural (script):** confere que a citação existe, que o arquivo existe, que o ID existe e a cobertura do tracker.
   - **Semântica (subagente revisor):** confere se a fala citada sustenta o que o documento afirma.

   Cada rodada de achados voltou como correção nos documentos.

## Prompts customizados

**1. Revisão semântica do tracker (enviado ao subagente revisor).** O script só prova que a citação existe; este prompt verifica se ela diz o que o documento afirma. A entrada é um arquivo gerado com cada linha do tracker ao lado do texto literal da fala citada.

```text
Você é um revisor crítico e cético de rastreabilidade documental. Não escreva nem altere
arquivos; apenas leia e reporte.

Arquivos:
- /tmp/dd/semantic_pairs.txt — 235 linhas no formato
  `ID | Tipo | AFIRMA: <resumo do item> | FALA [hh:mm] Nome: <texto literal da(s) fala(s)>`
- TRANSCRICAO.md — transcrição completa da reunião (use para contexto quando a fala
  isolada não bastar).

Tarefa: para CADA linha, julgue se a fala citada sustenta a afirmação. Classifique como:
- OK — a fala citada sustenta a afirmação diretamente.
- FRACO — a afirmação é sustentada pela reunião, mas a fala citada não é a melhor fonte.
  Indique o melhor `[hh:mm] Nome` existente na transcrição.
- ERRADO — a fala citada não sustenta, ou a afirmação contradiz a transcrição, ou
  exagera/inventa algo que ninguém disse. Explique em uma frase e sugira a correção.

Seja rigoroso com: números (tempos, tentativas, tamanhos, prazos), quem decidiu o quê,
itens adiados apresentados como decididos (e vice-versa), e afirmações que dependem de
uma interpretação (ex.: linhas marcadas "proposta derivada" podem ser OK se a fala citada
é de fato a decisão da qual a proposta decorre).

Saída: NÃO liste as linhas OK. Liste apenas FRACO e ERRADO, uma por linha:
`ID — CLASSE — motivo — sugestão de [hh:mm] Nome`. No fim, dê a contagem total.
```

**2. Segunda passada, só sobre o que mudou (mesma sessão do revisor).** Ela evita a revisão em loop do pacote inteiro e testa se as correções criaram problemas novos.

```text
Apliquei correções a partir da sua revisão. Ficaram assim:
- alternativas não levantadas agora são rotuladas "Alternativa plausível (não levantada)"
  (o enunciado aceita alternativa "real discutida ou plausível");
- nomes de código não falados aparecem como "nome proposto";
- itens com várias origens foram divididos em linhas complementares (IDs com sufixo);
- a meta "3 de 3" foi removida;
- a listagem e a criação passaram a usar customerId no path.

Revise SÓ o arquivo /tmp/dd/semantic_pairs_v2.txt (61 linhas, mesmo formato de antes),
com o mesmo critério rigoroso e a TRANSCRICAO.md como contexto. Liste apenas FRACO/ERRADO,
no mesmo formato, e dê a contagem final. Não escreva arquivos.
```

**3. Regras de extração e escrita usadas na produção.** São o resumo das instruções que guiaram a geração de cada documento: adaptam o "Prompt para geração de um FDD" do curso, que orienta a não inventar detalhes técnicos sem rotulá-los como hipótese, ao contexto deste desafio.

```text
Para cada documento do pacote:
1. Só registre o que tem origem em TRANSCRICAO.md ([hh:mm] Nome) ou num arquivo real do
   repositório. Cite a origem ao lado do item.
2. Separe: decisão fechada | requisito | restrição | alternativa descartada (com o trade-off
   dito na reunião) | adiado/fora de escopo | ambíguo. Item adiado nunca vira requisito.
3. Quando a reunião não decidiu algo que a implementação precisa, NÃO escolha em silêncio:
   ou registre como questão em aberto no RFC, ou marque no FDD como "(proposta)" e aponte
   a questão (Q-NN) e a decisão da qual a proposta deriva.
4. Antes de afirmar como o código se comporta, leia o arquivo. Se a decisão da reunião
   esbarra no código (ex.: um middleware que fixa o código de erro), documente o conflito
   e a forma de resolvê-lo sem alterar o código compartilhado.
5. Respeite a altura de cada documento: PRD = por que e o quê; RFC = proposta, alternativas
   e questões (sem payloads nem matriz de erros); ADR = uma decisão; FDD = como construir.
6. Dê um ID entre colchetes a cada item, para o TRACKER e a verificação automática.
```

## Iterações e ajustes

Foram **quatro iterações principais** de geração, revisão crítica e correção, além de dezenas de ajustes pontuais. As principais:

**Iteração 1: a leitura cruzada com o código antes da escrita.** Vários pontos que a reunião tratou como simples não fecham quando se olha o código ou a aritmética. Em vez de serem "resolvidos" em silêncio, eles foram registrados:

- **"5 tentativas" contra "quase 15 horas".** Cinco intervalos (1m, 5m, 30m, 2h e 12h) somam 14 h 36 min entre a primeira falha e a última tentativa, o que só bate com 1 envio + 5 retentativas, ou seja, 6 tentativas. Isso virou a questão RFC Q-01, e o FDD deixa o teto como uma constante única.
- **`WEBHOOK_INVALID_URL` contra `validate.middleware.ts`.** O middleware converte todo `ZodError` em `VALIDATION_ERROR`. Uma regra de HTTPS no Zod, como a Sofia pediu, nunca produziria o código `WEBHOOK_INVALID_URL`. Solução documentada: o código do módulo vai em `details[].message`, sem mexer no middleware compartilhado.
- **`NotFoundError` fixa `NOT_FOUND`.** Por isso, `WEBHOOK_NOT_FOUND` precisa estender `AppError` diretamente.
- **`WEBHOOK_SECRET_REQUIRED`**, citado como exemplo por Bruno, não tem gatilho, porque o secret é sempre gerado pelo OMS. Ficou fora da matriz, com a explicação.
- **O schema não liga `User` a `Customer`.** Logo, "qualquer role autenticada" significa que qualquer usuário gerencia webhooks de qualquer cliente. Isso virou um risco no PRD e a questão Q-06.
- **`OrderService.delete` remove pedidos `CANCELLED`.** Uma FK com cascade da outbox para `orders` apagaria o evento de cancelamento ainda não entregue, então a outbox não tem FK para `orders`.
- **Ordem sob retry.** Um único worker não garante a ordem por pedido quando há backoff, porque o evento seguinte ultrapassaria o anterior em espera. O FDD propõe uma regra de ordem por par (webhook, pedido) e registra o custo como risco.

**Iteração 2: a primeira revisão semântica encontrou 6 ERRADO e 34 FRACO em 235 linhas.** A IA tinha:

- **apresentado como "discutidas" duas alternativas que ninguém levantou** ("só TLS, sem assinatura" e "códigos sem prefixo"). Elas foram rotuladas como *alternativa plausível, não levantada na reunião*;
- **inventado uma meta** ("3 de 3 clientes até novembro"; o prazo de novembro é só da Atlas), que foi reescrita;
- **contradito a transcrição** com `GET /webhooks?customerId=`, quando Larissa disse "body ou path". Os contratos passaram para `/customers/:customerId/webhooks`;
- **contradito o próprio FDD** no RFC e no ADR-001 ("no máximo um INSERT", contra uma linha por webhook);
- **tratado nomes de erro como decisões.** Só dois foram falados; os demais agora são "nome proposto";
- **parafraseado errado** "latência mínima de 2 s". No contexto, é o atraso que o polling acrescenta, e não um piso de latência;
- **citado a fala que pergunta, e não a que decide**, em várias alternativas. As localizações foram trocadas, e itens com várias origens ganharam linhas complementares.

**Iteração 3: a segunda revisão (61 linhas alteradas) encontrou 1 ERRADO e 4 FRACO.** Ela revelou mais uma ambiguidade real da reunião: o replay "recoloca na outbox" [09:18], e o UUID é "gerado quando o evento entra na outbox" [09:25]. Lidas ao pé da letra, as duas falas fariam o replay gerar um `event_id` novo, o que quebraria a deduplicação. Isso virou a questão RFC Q-11, e o FDD marca a reutilização do id como proposta. "Uma linha de outbox por webhook" também passou a ser marcada como proposta, porque Diego falou em "uma linha com o evento".

**Iteração 4: verificação estrutural final.** O script pegou um ID fora do padrão (`FDD-ERR-NOSECRET`, que virou `FDD-ERR-11`) e uma âncora para este README antes de ele existir. O resultado final do script:

```text
$ python3 docs/tools/verificar_rastreabilidade.py
Citações [hh:mm] Nome conferidas: 785  |  caminhos de código conferidos: 143
TRACKER: 320 linhas (86% TRANSCRICAO, 46 CODIGO)  |  cobertura dos IDs dos documentos: 100% de 218
PRD: 15 RFs  |  FDD: 7 endpoints HTTP, 20 caminhos reais na Integração  |  ADRs: 7
OK: nenhuma inconsistência encontrada.
```

O que ficou como **questão em aberto** (11 itens no [RFC](docs/RFC.md#5-questões-em-aberto)) é deliberado: são pontos que a reunião não decidiu e que pertencem à sessão de revisão com Bruno e Diego que a Larissa marcou ([09:50] Larissa), e não a uma escolha silenciosa da IA.

## Como navegar a entrega

| Ordem | Documento | O que responde |
|---|---|---|
| 1 | [`docs/PRD.md`](docs/PRD.md) | Por que e o quê: problema, público, métricas, escopo e fora de escopo, 15 requisitos funcionais |
| 2 | [`docs/RFC.md`](docs/RFC.md) | A proposta técnica para revisão: abordagem, 7 alternativas descartadas e 11 questões em aberto |
| 3 | [`docs/adrs/`](docs/adrs/README.md) | Uma decisão por arquivo, ADR-001 a ADR-007: outbox, worker com polling, retry e DLQ, HMAC, at-least-once, reuso de padrões e snapshot |
| 4 | [`docs/FDD.md`](docs/FDD.md) | Como construir: modelo de dados, fluxos, 7 endpoints de API e o contrato de entrega ao cliente, com exemplos, matriz `WEBHOOK_*`, observabilidade e a seção **Integração com o sistema existente** |
| 5 | [`docs/TRACKER.md`](docs/TRACKER.md) | De onde veio cada item: 320 linhas ligadas a `[hh:mm] Nome` ou a um arquivo do código |
| 6 | [`docs/tools/verificar_rastreabilidade.py`](docs/tools/verificar_rastreabilidade.py) | Refaz a verificação: `python3 docs/tools/verificar_rastreabilidade.py` |

**Convenções:**
- `[ID]` liga o item ao tracker.
- `([hh:mm] Nome)` é a fala de origem.
- **(proposta)** no FDD marca uma escolha de implementação que não foi decidida na reunião.
- `Q-NN` é uma questão em aberto do RFC.
