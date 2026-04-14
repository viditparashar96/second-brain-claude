---
name: product-manager
description: Add, update, and manage products in the organization's product registry (PRODUCTS.md)
argument-hint: "{add|update|list|remove} [product-name]"
triggers:
  - "add product"
  - "new product"
  - "update product"
  - "list products"
  - "product registry"
  - "manage products"
  - "edit product"
  - "remove product"
---

# Product Manager

Manage the organization's product registry (PRODUCTS.md). This is the single source of truth for all products — every department skill pulls from this file for context. Keep it accurate and up to date.

## When to Trigger

- User wants to add a new product to the registry
- User wants to update an existing product's details (features, pricing, status, etc.)
- User asks to see all products or search for a specific one
- A new product is launched or an existing one is sunset
- During onboarding when setting up the organization's product catalog
- User says "add product", "update product", "list products", or "product registry"

## Workflow

### Command: `add` — Add a New Product

1. **Gather product details** — Ask for (or extract from user input):
   - Product name
   - Category (e.g., AI/Voice, Telecom, Gaming, Healthcare, EdTech)
   - Status (active, beta, sunset, planned)
   - Owner (team or person)
   - Target audience
   - Description (2-3 sentences)
   - Key features (top 3-5)
   - Tech stack (if relevant)
   - Pricing model
   - Competitive edge
   - Key clients / deployments
   - Known issues / limitations
   - Roadmap / what's next

2. **Check for duplicates** — Read `~/.second-brain/vault/PRODUCTS.md` and verify no product with the same name exists

3. **Add to PRODUCTS.md** — Append the new product entry under the appropriate section (Active Products, In Development, etc.) following the template format:
   ```markdown
   ### {Product Name}
   - **Category:** {category}
   - **Status:** {status}
   - **Owner:** {owner}
   - **Target Audience:** {audience}
   - **Description:** {description}
   - **Key Features:** {features}
   - **Tech Stack:** {tech stack}
   - **Pricing Model:** {pricing}
   - **Competitive Edge:** {competitive edge}
   - **Key Clients:** {clients}
   - **Known Issues:** {issues}
   - **Roadmap:** {roadmap}
   ```

4. **Update Cross-Department Quick Reference table** at the bottom of PRODUCTS.md

5. **Update Product Relationships** section if this product relates to existing ones

6. **Log to daily** — Append: `- **HH:MM** — [PRODUCT] Added to registry: {product name} ({status})`

### Command: `update` — Update an Existing Product

1. **Read current PRODUCTS.md** from `~/.second-brain/vault/PRODUCTS.md`
2. **Find the product** by name
3. **Ask what changed** — or accept updates from user input
4. **Edit the product entry** in PRODUCTS.md with the new information
5. **Update status** if product is moving between sections (e.g., "In Development" → "Active Products")
6. **Log to daily** — Append: `- **HH:MM** — [PRODUCT] Updated: {product name} — changed: {what changed}`

### Command: `list` — List All Products

1. **Read PRODUCTS.md** from `~/.second-brain/vault/PRODUCTS.md`
2. **Display summary** grouped by status:
   - Active Products (with 1-liner each)
   - In Development
   - Sunset / Deprecated
3. **Show count** — "X active, Y in development, Z sunset"

### Command: `remove` — Sunset a Product

1. **Read current PRODUCTS.md**
2. **Find the product** by name
3. **Move to "Sunset / Deprecated" section** — do NOT delete the entry (historical context matters)
4. **Add sunset date and reason**
5. **Log to daily** — Append: `- **HH:MM** — [PRODUCT] Sunset: {product name} — reason: {reason}`

## Rules

- **PRODUCTS.md is the single source of truth.** All product context flows from this file.
- **Every session loads PRODUCTS.md.** Keep entries concise — this file goes into every conversation's context window.
- **Never delete product entries.** Move sunset products to the Sunset section instead.
- **Update, don't duplicate.** If a product exists, update it. Don't create a second entry.
- **Cross-department relevance matters.** Include fields that serve all departments: sales needs pricing and competitive edge, engineering needs tech stack, HR needs owner/team info, ops needs deployment context.
- **Keep descriptions under 3 sentences.** PRODUCTS.md must stay lean — it loads into every session alongside SOUL.md, USER.md, and MEMORY.md.
- **Use [[wiki-links]]** to connect products to projects, clients, and team files in the vault.

## How Skills Use Product Context

Every department skill automatically has access to PRODUCTS.md because it's injected at session start. Here's how:

- **Sales skills** (deal-prep, proposal-drafter, follow-up) → Pull product features, pricing, competitive edge, key clients for the relevant product
- **HR skills** (onboarding-checklist, performance-review) → Pull which products a team member's department owns
- **Product skills** (prd-drafter, okr-tracker, stakeholder-update) → Pull current product status, roadmap, known issues
- **Ops skills** (sop-creator, compliance-checklist) → Pull tech stack, deployment context, SLAs
- **Engineering skills** (code-review, incident-response) → Pull tech stack, known issues, architecture context
