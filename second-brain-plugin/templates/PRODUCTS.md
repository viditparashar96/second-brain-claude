# PRODUCTS — blackNgreen Product Registry

## Active Products

### Nexiva
- **Category:** AI Customer Experience Platform
- **Status:** active
- **Owner:** Rahul Gupta & Karthik Shankar (BNG Founders)
- **Target Audience:** Enterprises (insurance, e-commerce, logistics, NBFC), telecom operators
- **Description:** Next-gen AI venture for customer care. Advanced conversational platforms, real-time multilingual voice assistants, and agentic AI for autonomous decision-making.
- **Key Features:** Predictive analytics, adaptive learning, 20+ languages, agentic AI, 30% faster resolution times
- **Tech Stack:** Conversational AI, multilingual NLP, real-time voice processing
- **Pricing Model:** Enterprise SaaS (per-deployment / per-interaction)
- **Competitive Edge:** AI-first architecture, multilingual-first, measurable ROI (30% faster resolution), deep enterprise customization
- **Key Clients:** 20+ live POCs — Orange, BTC, Africell; sectors: insurance, e-commerce, logistics, NBFC across India, Middle East, Latin America
- **Investment:** ₹130 Crore planned by 2028
- **Website:** https://www.nexiva.ai/

### EVA (Enterprise Voice AI)
- **Category:** Voice-First AI Customer Experience
- **Status:** active
- **Owner:** BNG Core Team
- **Target Audience:** Telecom operators, BFSI, FMCG, healthcare enterprises
- **Description:** Voice-first AI platform with 5 specialized avatars for different enterprise CX needs. Deployed at scale across Africa and GCC.
- **Key Features:** 5 avatars (Customer Care, Ask Me Anything, Personal Assistant, Virtual Receptionist, Sales Agent), 95+ languages, 70+ CRM integrations, omnichannel (voice + chat)
- **Tech Stack:** Voice AI, NLP, CRM integration layer, omnichannel orchestration
- **Pricing Model:** Per-operator licensing / per-interaction
- **Competitive Edge:** 95+ languages (industry-leading), proven metrics (40% cost reduction, 83% first-call resolution, 94% CSAT), 5 specialized avatars
- **Key Clients:** Orange, Africell, Umniah, Moov (Africa & GCC); 20+ enterprise pilots
- **Investment:** ₹40 Crore cumulative
- **Known Issues:** Enterprise onboarding can be complex; customization per-operator takes time

### Voxa Voice AI
- **Category:** Voice AI SaaS Platform
- **Status:** active (early-stage sales)
- **Owner:** Engineering Team
- **Target Audience:** Telecom operators (white-label), hospitals, large enterprises needing high-volume voice AI
- **Description:** Radical low-cost voice AI platform. Multi-tenant SaaS, white-label ready. 10-17x cheaper than competitors.
- **Key Features:** $0.019/min all-in cost, multilingual-first (Hindi, English, Arabic, African languages), white-label/multi-tenant, carrier-grade FreeSWITCH telephony
- **Tech Stack:** Pipecat + LiveKit (WebRTC), FreeSWITCH, Deepgram (STT), Gemini Flash (LLM), Cartesia (TTS)
- **Pricing Model:** Per-minute SaaS ($0.019/min all-in)
- **Competitive Edge:** 10-17x cheaper than Vapi ($0.18-$0.33/min), Retell ($0.07-$0.20/min), Bland ($0.09-$0.14/min). Owns telephony layer (no Twilio dependency). White-label ready.
- **Key Clients:** Apollo Hospital (target), telecom operators
- **Known Issues:** No no-code builder yet, compliance certs (HIPAA/SOC2) not public, latency benchmarks not documented
- **Roadmap:** Publish latency benchmarks, pursue HIPAA certification, build basic no-code agent builder

### MobiBattle
- **Category:** Mobile Gaming / Engagement Platform
- **Status:** active
- **Owner:** Digital Services Team
- **Target Audience:** Telecom operators looking to increase subscriber engagement and ARPU
- **Description:** Hypercasual multiplayer gaming platform for telecom operators. Drives engagement and micro-transaction revenue.
- **Key Features:** Real-time multiplayer, available via app/web/IVR, operator-branded (white-label), micro-transaction model
- **Tech Stack:** Mobile gaming engine, WebSocket multiplayer, IVR integration
- **Pricing Model:** Revenue share with operators
- **Competitive Edge:** Multi-platform (app + web + IVR), proven engagement metrics, low integration effort

### VAS Platform (Core)
- **Category:** Mobile Value-Added Services
- **Status:** active (mature)
- **Owner:** Telecom Solutions Team
- **Target Audience:** Telecom operators (all sizes, all markets)
- **Description:** Full suite of mobile VAS services powering 160+ operators globally. The original BNG business and revenue backbone.
- **Key Features:** IVR services, WAP services, SMS services, network solutions, mobile applications, OTT platform, AI-powered MVAS
- **Tech Stack:** Telecom infrastructure, IVR, SMS gateways, WAP, OTT
- **Pricing Model:** Per-operator licensing + revenue share
- **Competitive Edge:** Global scale (160+ operators), proven reliability, local market expertise across 100+ countries
- **Key Clients:** 160+ telecom operators across APAC, Africa, Middle East, LatAm

### Digital Services Suite
- **Category:** Consumer Entertainment / Gaming
- **Status:** active
- **Owner:** Digital Services Team
- **Target Audience:** Consumers via telecom operators
- **Description:** Consumer-facing entertainment services deployed through telecom operators.
- **Key Features:** Real money mobile gaming, contesting services, Magic Voice (voice changing), rich media services
- **Tech Stack:** Mobile gaming, voice processing, content delivery
- **Pricing Model:** Revenue share with operators + micro-transactions

---

## In Development

### Medical Scribe / Veterinary Medical Scribe
- **Category:** Healthcare AI
- **Status:** planned
- **Owner:** Engineering Team
- **Target Audience:** Veterinary clinics, hospitals, medical practices
- **Description:** AI tool that listens to medical/veterinary consultations and auto-generates clinical notes, treatment plans, prescriptions.
- **Key Features (Planned):** Speech-to-text transcription, LLM-powered note structuring, medical/vet knowledge base, real-time drug/treatment lookup, multi-location support
- **Tech Stack:** Voxa voice infra + healthcare domain LLM + medical knowledge base
- **Key Clients:** Happy Paws Veterinary Clinic (Bangalore, 3 branches, CEO: Gaurav) — meeting pending
- **Roadmap:** Complete meeting with Gaurav, define MVP scope, build PoC leveraging Voxa infrastructure

### School Cab
- **Category:** EdTech / Transportation
- **Status:** planned
- **Owner:** New Ventures Team
- **Target Audience:** Schools (B2B), parents (B2C)
- **Description:** B2B2C platform for school transportation management. Sold to schools, parents are end users.
- **Key Features (Planned):** Verified driver profiles, live GPS tracking, route optimization, parent notifications
- **Pricing Model:** Subscription per student per month (B2B2C)
- **Roadmap:** Define MVP features, build prototype, pilot with 2-3 schools

---

## Product Relationships

```
BNG (Parent Organization)
├── AI & Voice (Growth Engines)
│   ├── Nexiva (next-gen AI venture, ₹130Cr) ──→ Evolution of EVA vision
│   ├── EVA (5 avatars, 95+ languages, ₹40Cr) ──→ Foundation for Nexiva
|
├── Telecom Core (Revenue Backbone)
│   ├── VAS Platform (160+ operators) ──→ Entry point, upsell to EVA/Nexiva
│   └── Digital Services (gaming, Magic Voice) ──→ Complements MobiBattle
├── Gaming
│   └── MobiBattle (multiplayer engagement) ──→ Part of Digital Services ecosystem

```

**Upsell Paths:**
- VAS Platform → EVA → Nexiva (telecom operators upgrade path)
- Voxa → Medical Scribe (shared voice infrastructure)
- MobiBattle → Digital Services (gaming ecosystem expansion)

## Cross-Department Quick Reference

| Product | Sales Pitch (1-liner) | Engineering Context | HR Onboarding Note |
|---------|----------------------|--------------------|--------------------|
| Nexiva | AI that handles customer care in 20+ languages with 30% faster resolution | Conversational AI, multilingual NLP, real-time voice | Flagship AI venture — key strategic priority |
| EVA | 5 AI avatars for CX, 95+ languages, proven 40% cost savings | Voice AI, CRM integrations, omnichannel | Mature product with global deployments |
| Voxa | Voice AI at $0.019/min — 10x cheaper than any competitor | Pipecat, LiveKit, FreeSWITCH, Deepgram, Gemini Flash, Cartesia | Disruptive pricing play, early-stage |
| MobiBattle | Multiplayer gaming that boosts operator engagement and ARPU | Mobile gaming engine, WebSocket, IVR | Digital services team product |
| VAS Platform | Powering 160+ telecom operators in 100+ countries | Telecom infra, IVR, SMS, WAP, OTT | Core business, revenue backbone |
| Digital Services | Consumer entertainment via telecom — gaming, contests, Magic Voice | Mobile gaming, voice processing, content delivery | Consumer-facing entertainment |
| Medical Scribe | AI that auto-generates clinical notes from doctor consultations | Voxa infra + healthcare LLM | In planning — new vertical |
| School Cab | Safe school transport with live tracking — sold to schools, used by parents | Mobile app, GPS, routing | In planning — new venture |
