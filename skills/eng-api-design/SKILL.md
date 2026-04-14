---
name: eng-api-design
description: "API design review and documentation — contract-first development, systematic quality checks, OpenAPI spec generation, breaking change detection."
argument-hint: "[design|review|document] [api-description|spec-path] [--product name] [--style rest|graphql|grpc]"
triggers:
  - "API design"
  - "API review"
  - "design API"
  - "API contract"
  - "OpenAPI"
  - "swagger"
  - "API spec"
  - "endpoint design"
  - "API documentation"
  - "REST API"
  - "GraphQL schema"
  - "gRPC service"
  - "breaking change API"
---

# API Design Review & Documentation

Contract-first: context → design → review → document.

## Workflow

### Phase 1: CONTEXT
1. Read PRODUCTS.md — identify product, consumers, existing API patterns dynamically
2. Check `docs/api-specs/` for existing specs
3. Search memory for prior API decisions
4. Determine: product, consumers (internal/partner/public), style (REST/GraphQL/gRPC), constraints
5. **🚫 GATE — Requirements confirmed**

### Phase 2: DESIGN
**Ultrathink** — Based on product's domain model from PRODUCTS.md:
1. Resource model (map domain to resources)
2. Endpoints with request/response schemas
3. Error contract (consistent format, error codes)
4. Pagination (cursor-based for collections)
5. Auth model

### Phase 3: REVIEW (4 checks)
- **Naming:** consistent casing, correct HTTP methods/status codes
- **Security:** auth everywhere, input validation, rate limiting, no secrets in URLs
- **Performance:** pagination, caching headers, no unbounded queries, latency targets
- **Evolution:** versioned, additive-compatible, deprecation strategy

If updating existing API: detect breaking changes, generate migration guide.

Present findings. **🚫 GATE — Design approved**

### Phase 4: DOCUMENT (LOCAL FIRST)
1. Save `docs/api-specs/{product}-{version}.yaml` — OpenAPI spec
2. Save `docs/api-docs/{product}-api-guide.md` — developer guide with quick start
3. Log to memory via `log_note`

## Rules
- Design BEFORE implementing (contract-first)
- Every endpoint: auth, validation, errors, latency target
- Breaking changes require versioning + migration plan
- Product context from PRODUCTS.md — never hardcode
- Save locally first, memory second
