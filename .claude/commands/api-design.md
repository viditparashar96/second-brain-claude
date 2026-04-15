---
description: "API design review — contract-first, quality checks, OpenAPI spec, breaking change detection"
allowed-tools: ["Read", "Glob", "Grep", "Bash", "Agent", "Write"]
---

# API Design Review

Contract-first API design with systematic review.

## Request

$ARGUMENTS

## Step 1: Context

```bash
cat ~/.second-brain/vault/PRODUCTS.md 2>/dev/null
ls docs/api-specs/ 2>/dev/null
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "API design" --top-k 5 2>/dev/null
```

Determine: product, consumers, style (REST/GraphQL/gRPC), constraints.

**Present context. Wait for confirmation.**

## Step 2: Design

**Ultrathink** — Based on product's domain model:

1. Resource model
2. Endpoints with request/response schemas
3. Error contract (consistent format)
4. Pagination (cursor-based for collections)
5. Auth model

## Step 3: Review (4 checks)

- **Naming:** consistent casing, correct HTTP methods/status codes
- **Security:** auth everywhere, input validation, rate limiting
- **Performance:** pagination, caching, no unbounded queries
- **Evolution:** versioned, additive-compatible

Present findings. **Wait for approval.**

## Step 4: Document (LOCAL FIRST)

```bash
mkdir -p docs/api-specs docs/api-docs
```

- `docs/api-specs/{product}-{version}.yaml` — OpenAPI spec
- `docs/api-docs/{product}-api-guide.md` — developer guide

If updating existing API: detect breaking changes, generate migration guide.

Log to memory:
```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from memory_search import log_memory
log_memory('API DESIGN: {product} — {N} endpoints. Breaking: {yes/no}.')
"
```

## Rules

- Design BEFORE implementing
- Every endpoint: auth, validation, errors, latency target
- Breaking changes require versioning + migration
- Save locally, memory second
