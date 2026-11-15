#!/usr/bin/env python3
"""Verificação anti-alucinação do pacote de design docs.

Uso (na raiz do repositório):  python3 docs/tools/verificar_rastreabilidade.py

Confere, sem dependências externas:
  1. toda citação "[hh:mm] Nome" nos documentos corresponde a uma fala real
     desse participante nesse minuto em TRANSCRICAO.md;
  2. todo caminho de código citado entre crases existe no repositório
     (exceto os arquivos novos que a feature vai criar, listados em PLANEJADOS);
  3. toda linha do TRACKER tem Fonte válida, Localização existente e um ID
     que aparece no documento indicado;
  4. todo ID dos documentos (PRD-*, RFC-*, FDD-*, Q-NN, ADR-NNN) tem linha no TRACKER;
  5. links internos entre os .md (inclusive âncoras) não estão quebrados;
  6. a estrutura de entrega e os mínimos do enunciado.
Sai com código 1 se encontrar qualquer inconsistência.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TX = (ROOT / "TRANSCRICAO.md").read_text(encoding="utf-8")
SPOKEN = set(re.findall(r"^\[(\d\d:\d\d)\] (\w+):", TX, re.M))
ADRS = sorted((ROOT / "docs/adrs").glob("ADR-*.md"))
DOCS = [ROOT / "docs" / n for n in ("PRD.md", "RFC.md", "FDD.md", "TRACKER.md")] + ADRS + [ROOT / "README.md"]
PLANEJADOS = {  # arquivos que a feature criará (citados como plano, não como existentes)
    "src/worker.ts", "src/modules/webhooks", "src/modules/webhooks/webhook.worker.ts",
    "src/modules/webhooks/webhook.processor.ts", "src/modules/webhooks/webhook.errors.ts",
    "src/modules/webhooks/webhook.publisher.ts",
}
CODE_RE = re.compile(r"`((?:src|prisma|tests)/[\w./\-]+|package\.json|docker-compose\.yml|tsconfig\.build\.json|vitest\.config\.ts)`")
errors: list[str] = []


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def slug(heading: str) -> str:
    h = re.sub(r"[^\w\- ]", "", heading.strip().lower(), flags=re.U)
    return h.replace(" ", "-")


# 1 e 2: citações e caminhos em todos os documentos
n_cit = n_paths = 0
for d in DOCS:
    text = d.read_text(encoding="utf-8")
    for ts, name in re.findall(r"\[(\d\d:\d\d)\] ([A-Z][a-z]+)", text):
        n_cit += 1
        if (ts, name) not in SPOKEN:
            errors.append(f"{rel(d)}: citação sem fala correspondente: [{ts}] {name}")
    for pth in CODE_RE.findall(text):
        n_paths += 1
        clean = pth.rstrip("/")
        if clean not in PLANEJADOS and not (ROOT / clean).exists():
            errors.append(f"{rel(d)}: caminho de código inexistente: {pth}")

# 3: linhas do tracker
rows = []
for line in (ROOT / "docs/TRACKER.md").read_text(encoding="utf-8").splitlines():
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) == 6 and re.match(r"^(PRD|RFC|FDD|ADR)-", cells[0]):
        rows.append(cells)
for rid, doc, _tipo, _resumo, fonte, loc in rows:
    doc_path = ROOT / doc.strip("`")
    loc = loc.strip("`")
    if fonte == "TRANSCRICAO":
        m = re.fullmatch(r"\[(\d\d:\d\d)\] (\w+)", loc)
        if not m or (m.group(1), m.group(2)) not in SPOKEN:
            errors.append(f"TRACKER {rid}: localização inválida '{loc}'")
    elif fonte == "CODIGO":
        if not (ROOT / loc).exists():
            errors.append(f"TRACKER {rid}: arquivo inexistente '{loc}'")
    else:
        errors.append(f"TRACKER {rid}: Fonte deve ser TRANSCRICAO ou CODIGO, não '{fonte}'")
    if not doc_path.exists():
        errors.append(f"TRACKER {rid}: documento inexistente {doc}")
        continue
    if rid.startswith("ADR-"):
        num = re.match(r"ADR-(\d+)", rid).group(1)
        if not doc_path.name.startswith(f"ADR-{num}-"):
            errors.append(f"TRACKER {rid}: aponta para o ADR errado ({doc})")
        continue
    base = re.match(r"((?:PRD|RFC|FDD)-(?:Q-\d+|[A-Z]+-\d+))", rid)
    if not base:
        errors.append(f"TRACKER {rid}: ID fora do padrão")
        continue
    key = base.group(1).replace("RFC-Q-", "Q-")
    if key not in doc_path.read_text(encoding="utf-8"):
        errors.append(f"TRACKER {rid}: ID {key} não aparece em {doc}")

# 4: cobertura
tracker_ids = {r[0] for r in rows} | {r[0].replace("RFC-Q-", "Q-") for r in rows}
tracker_bases = {re.match(r"((?:PRD|RFC|FDD)-(?:Q-\d+|[A-Z]+-\d+)|ADR-\d+)", i).group(1).replace("RFC-Q-", "Q-")
                 for i in tracker_ids if re.match(r"((?:PRD|RFC|FDD)-(?:Q-\d+|[A-Z]+-\d+)|ADR-\d+)", i)}
doc_ids: set[str] = set()
for n in ("PRD.md", "RFC.md", "FDD.md"):
    doc_ids |= set(re.findall(r"\b(?:PRD|RFC|FDD)-[A-Z]+-\d+\b", (ROOT / "docs" / n).read_text(encoding="utf-8")))
doc_ids |= set(re.findall(r"\*\*(Q-\d+)\*\*", (ROOT / "docs/RFC.md").read_text(encoding="utf-8")))
doc_ids |= {re.match(r"(ADR-\d+)", p.name).group(1) for p in ADRS}
missing = sorted(doc_ids - tracker_bases)
errors += [f"cobertura: {m} não tem linha no TRACKER" for m in missing]
coverage = 100 * (len(doc_ids) - len(missing)) / len(doc_ids)

# 5: links internos
for d in DOCS:
    for target, anchor in re.findall(r"\]\(([^)#\s]*\.md)?(?:#([^)\s]+))?\)", d.read_text(encoding="utf-8")):
        if not target and not anchor:
            continue
        tp = (d.parent / target).resolve() if target else d
        if not tp.exists():
            errors.append(f"{rel(d)}: link quebrado {target}")
        elif anchor and anchor not in {slug(h) for h in re.findall(r"^#+ (.+)$", tp.read_text(encoding="utf-8"), re.M)}:
            errors.append(f"{rel(d)}: âncora inexistente {target}#{anchor}")

# 6: estrutura e mínimos do enunciado
if not 5 <= len(ADRS) <= 8:
    errors.append(f"docs/adrs deve ter de 5 a 8 ADRs (tem {len(ADRS)})")
for a in ADRS:
    if not re.fullmatch(r"ADR-\d{3}-[a-z0-9]+(?:-[a-z0-9]+)*\.md", a.name):
        errors.append(f"nome fora do padrão ADR-NNN-titulo-em-kebab-case.md: {a.name}")
    t = a.read_text(encoding="utf-8")
    for sec in ("**Status:**", "## Contexto", "## Decisão", "## Alternativas Consideradas", "## Consequências"):
        if sec not in t:
            errors.append(f"{a.name}: seção ausente {sec}")
prd = (ROOT / "docs/PRD.md").read_text(encoding="utf-8")
fdd = (ROOT / "docs/FDD.md").read_text(encoding="utf-8")
n_fr = len(set(re.findall(r"PRD-FR-\d+", prd)))
n_endpoints = len(re.findall(r"^### 6\.\d+ \[FDD-CONTRATO-\d+\] `(?:GET|POST|PATCH|DELETE) /api", fdd, re.M))
integ = fdd[fdd.index("## 9. Integração com o sistema existente"):fdd.index("## 10.")]
n_integ_paths = len({p for p in CODE_RE.findall(integ) if (ROOT / p).exists()})
n_codigo = sum(1 for r in rows if r[4] == "CODIGO")
pct_tx = 100 * sum(1 for r in rows if r[4] == "TRANSCRICAO") / len(rows)
for cond, msg in [(n_fr >= 8, f"PRD com {n_fr} RFs (mín. 8)"), (n_endpoints >= 4, f"FDD com {n_endpoints} endpoints (mín. 4)"),
                  (n_integ_paths >= 4, f"Integração com {n_integ_paths} caminhos reais (mín. 4)"),
                  (n_codigo >= 5, f"TRACKER com {n_codigo} linhas CODIGO (mín. 5)"), (pct_tx >= 70, f"TRACKER com {pct_tx:.0f}% TRANSCRICAO (mín. 70%)")]:
    if not cond:
        errors.append("mínimo não atendido: " + msg)

print(f"Citações [hh:mm] Nome conferidas: {n_cit}  |  caminhos de código conferidos: {n_paths}")
print(f"TRACKER: {len(rows)} linhas ({pct_tx:.0f}% TRANSCRICAO, {n_codigo} CODIGO)  |  cobertura dos IDs dos documentos: {coverage:.0f}% de {len(doc_ids)}")
print(f"PRD: {n_fr} RFs  |  FDD: {n_endpoints} endpoints HTTP, {n_integ_paths} caminhos reais na Integração  |  ADRs: {len(ADRS)}")
if errors:
    print(f"\n{len(errors)} inconsistência(s):")
    print("\n".join(f"  - {e}" for e in errors))
    sys.exit(1)
print("OK: nenhuma inconsistência encontrada.")
