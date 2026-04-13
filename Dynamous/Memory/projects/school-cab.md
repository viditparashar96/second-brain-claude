# School Cab

Uber-like ride-hailing application built specifically for school students.

**Status:** Planning
**Started:** 2026-04-13
**Owner:** [[team/vidit]]

## Concept

A cab booking platform where:
- **Schools** manage approved routes, drivers, and student rosters
- **Parents** book rides, track their child in real-time, and receive pickup/drop-off confirmations
- **Drivers** receive trip assignments, follow optimized routes, and confirm student handoffs
- **Students** (older ones) can view ride status and ETA
- **Admins** oversee fleet, compliance, safety, and billing

## Key Differentiators from Uber

| Feature | Uber | School Cab |
|---------|------|------------|
| Rider verification | Phone/email | Student ID + parent consent |
| Route model | Point-to-point | Fixed routes + stops (like a school bus, but cabs) |
| Safety | Driver background check | Background check + school-approved driver pool |
| Tracking | Rider sees driver | Parent sees child's cab in real-time |
| Billing | Per-ride / subscription | Monthly subscription per school/parent |
| Scheduling | On-demand | Scheduled (morning pickup, afternoon drop) + on-demand for events |
| Notifications | Rider only | Parent + school admin + student |

---

## Technical Architecture

### System Overview

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Parent App  │  │  Driver App  │  │ School Admin │
│  (Mobile)    │  │  (Mobile)    │  │  (Web)       │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └────────────┬────┴────────────────┘
                    │
              ┌─────▼──────┐
              │ API Gateway │  (rate limiting, auth, routing)
              └─────┬──────┘
                    │
       ┌────────────┼────────────────┐
       │            │                │
┌──────▼───┐ ┌─────▼─────┐  ┌──────▼──────┐
│ Booking  │ │  Tracking  │  │    Admin     │
│ Service  │ │  Service   │  │   Service    │
└──────┬───┘ └─────┬─────┘  └──────┬──────┘
       │           │               │
┌──────▼───┐ ┌─────▼─────┐  ┌─────▼──────┐
│ Matching │ │ Location   │  │ School     │
│ Engine   │ │ Stream     │  │ Management │
└──────┬───┘ └─────┬─────┘  └─────┬──────┘
       │           │               │
       └───────────┼───────────────┘
                   │
          ┌────────▼────────┐
          │   Data Layer    │
          │  (PostgreSQL +  │
          │   Redis + S3)   │
          └─────────────────┘
```

### Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Parent & Driver Apps** | React Native (Expo) | Single codebase for iOS + Android, fast iteration |
| **School Admin Panel** | Next.js | SSR, dashboard-friendly, shared JS ecosystem |
| **API Gateway** | Kong / AWS API Gateway | Auth, rate limiting, request routing |
| **Backend Services** | Node.js (Fastify) | Lightweight, fast, good WebSocket support |
| **Real-time Tracking** | WebSockets + Redis Pub/Sub | Low-latency location streaming |
| **Database** | PostgreSQL | Relational data — users, schools, routes, bookings |
| **Cache / Pub-Sub** | Redis | Session cache, location pub/sub, rate limiting |
| **Maps & Routing** | Google Maps Platform | Directions, geocoding, distance matrix, ETA |
| **Push Notifications** | Firebase Cloud Messaging (FCM) | Cross-platform push to parents, drivers, students |
| **File Storage** | AWS S3 / Cloudflare R2 | Driver documents, student photos, receipts |
| **Auth** | Firebase Auth + custom RBAC | Phone OTP for parents/drivers, email for admins |
| **Payments** | Razorpay | Subscription billing, Indian payment methods |
| **Hosting** | AWS (ECS Fargate) | Containerized, auto-scaling, production-ready |
| **CI/CD** | GitHub Actions | Automated tests, build, deploy |

### Core Services

**1. Booking Service** — Create/cancel/modify rides. Supports scheduled (daily recurring) and on-demand. Validates student-parent relationship. Enforces school-approved time windows.

**2. Matching Engine** — Assigns drivers based on proximity, route overlap, capacity, school preference. Pools multiple students on same route. Handles driver shifts.

**3. Tracking Service** — Real-time GPS streaming via WebSocket. Geofence triggers (arriving, picked up, dropped off). Location history for safety audit.

**4. Admin Service** — School onboarding, driver management, billing dashboard, analytics.

**5. Notification Service** — Event-driven (Redis streams). Templates for ride lifecycle. Push + SMS fallback.

### Data Models (Core)

```
School: id, name, address, coordinates, approved_routes[], settings
User: id, name, phone, email, role, school_id, verified
Student: id, name, grade, section, school_id, parent_id, photo_url
Driver: id, user_id, vehicle_info, documents, status, approved_schools[]
Route: id, school_id, name, stops[], estimated_duration
Booking: id, student_id, parent_id, driver_id, route_id, type, status, times, recurrence
Trip: id, booking_ids[], driver_id, route_id, status, location_history[]
Payment: id, parent_id, plan, amount, status, razorpay_subscription_id
```

### Safety Features

1. Student verification — Driver confirms via photo + OTP
2. Geofenced alerts — Auto-notify parent at school/home zones
3. SOS button — Triggers alert to school admin + emergency contacts
4. Trip recording — GPS trail for audit
5. Driver vetting — Background check + school approval
6. Route deviation alerts — Real-time flagging
7. Ride sharing transparency — Parents see co-riders

### Phase Plan

| Phase | Scope | Estimate |
|-------|-------|----------|
| Phase 1 | Core backend: auth, models, route CRUD | 2 weeks |
| Phase 2 | Booking + matching (scheduled rides) | 2 weeks |
| Phase 3 | Driver app: accept rides, GPS, trip flow | 2 weeks |
| Phase 4 | Parent app: booking, tracking, notifications | 2 weeks |
| Phase 5 | Admin panel: onboarding, dashboard | 2 weeks |
| Phase 6 | Payments (Razorpay subscriptions) | 1 week |
| Phase 7 | Safety: SOS, geofencing, deviation alerts | 1 week |
| Phase 8 | On-demand rides, pooling optimization | 2 weeks |
| Phase 9 | Testing, security audit, deployment | 2 weeks |

**Total: ~16 weeks for MVP**

### Infrastructure

- **Region:** ap-south-1 (Mumbai)
- **Compute:** ECS Fargate (auto-scaling)
- **DB:** RDS PostgreSQL (Multi-AZ)
- **Cache:** ElastiCache Redis
- **Storage:** S3 + CloudFront CDN
- **Monitoring:** CloudWatch + Sentry
