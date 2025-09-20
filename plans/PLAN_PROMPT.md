You are a senior automation engineer. Produce ONE deliverable: a phased, step-by-step implementation plan in a single Markdown file named `wreck-beach-wind-alert-cron-plan.md`. Do not include any other outputs or extra commentary.

## Objective
Design a cron-driven pipeline that runs **every 60 minutes** and sends me an **SMS alert** when **north-westerly wind ≥ 25 km/h** is detected **at or nearest to Wreck Beach, Vancouver, BC**.

## Constraints & Definitions
- “North-westerly wind” uses meteorological convention: wind **from** the NW (bearing ~315°). Define a precise range (e.g., 292.5°–337.5°) and justify it.
- Threshold: **25 km/h** sustained wind (not gust). Provide equivalent units: **≈ 6.94 m/s**, **≈ 13.5 kt**. Plan must handle API unit differences and conversions.
- Location: **Wreck Beach, Vancouver, BC, Canada**. Verify exact coordinates via geocoding (e.g., OSM/Nominatim or Google) and explain how you’ll map that point to the wind data source’s nearest grid/station (e.g., model grid cell or marine station).
- Output: Send **one SMS** per qualifying check. Include debouncing guidance to avoid repeated alerts if condition persists (e.g., once per 6–12h unless state changes).

## Process Requirements
Follow these phases and produce a **single .md plan** with clear numbered steps under each phase. Phase A must be “Ultrathink & Research” as below. Use the Internet and any available research tools. Cite sources with links for all claims, docs, pricing, and API capabilities.

### Phase A — Ultrathink & Research
1) **Wind Data APIs**: Identify and compare trustworthy APIs that provide near-real-time or forecast **wind speed (sustained) and direction** at 10m near surface for the Wreck Beach area. Consider at least: Environment and Climate Change Canada (ECCC) / MSC Datamart, Open-Meteo, OpenWeather, Meteostat, NOAA/NWS (note Canadian coverage limits), Meteomatics, Tomorrow.io, Windy API (ECMWF/GFS), Apple WeatherKit.  
   - For each: data latency/refresh, resolution (spatial and temporal), availability at given coordinates, auth model (API key vs none), rate limits, costs, SLA, examples of endpoints/parameters, sample JSON payloads (trimmed), and reliability.  
   - Recommend a **primary** and **fallback** provider with rationale.
2) **SMS Providers**: Identify and compare options to send SMS to a Canadian number: Twilio, AWS SNS, Vonage/Nexmo, MessageBird, Telnyx, etc.  
   - Compare pricing to CA, ease of setup, SDKs/REST, reliability, sender ID constraints in Canada, free tiers, and required compliance (A2P/10DLC impacts if any).  
   - Recommend one **primary** provider and one **fallback** with rationale.
3) **Geocoding**: Specify a method to resolve “Wreck Beach, Vancouver, BC” to coordinates and verify them (two sources). Include chosen coordinates and show a quick sanity check on a map link.

### Phase B — Architecture & Data Flow
4) Draw a concise architecture description (textual) covering: scheduler → fetch wind data → normalize units → evaluate rule (NW & ≥25 km/h) → alert decision & deduping → SMS send → logging/metrics/error handling.  
5) Define the **direction test** precisely (bearing range) and document how to interpret cardinal vs degrees if API returns cardinal strings.  
6) Define unit normalization: m/s ↔ km/h ↔ knots, rounding policy, and sustained vs gust fields.  
7) Define **idempotency/dedup** strategy (e.g., keep last-alert state in a small file/row or key in a managed store with TTL).

### Phase C — Implementation Plan (No code, just a build plan)
8) Choose a language/runtime (**Python preferred**; Node.js acceptable). List required packages/modules (HTTP client, scheduler if needed locally, env loader).  
9) Provide **step-by-step tasks** to implement the script:  
   - Config & secrets management (API keys, phone numbers).  
   - Geocode once and store coordinates (with manual override).  
   - Fetch from primary wind API; on failure, use fallback.  
   - Parse JSON, extract wind speed/direction, convert units.  
   - Evaluate condition; check dedup key; decide to send SMS.  
   - Send SMS via chosen provider; handle errors/retries.  
   - Structured logging; minimal metrics (counts, last status).  
   - Exit codes and retry semantics.  
10) Include **testing guidance**: local dry-run, force-condition flag, unit tests for direction range & unit conversions, and simulated API responses.

### Phase D — Scheduling & Hosting Options
11) Propose at least **four** hosting/scheduling paths with pros/cons, costs, and exact cron settings for **hourly** runs:  
   - **GitHub Actions** (workflow_dispatch + `schedule: cron: "0 * * * *"`; secrets).  
   - **GCP Cloud Run** + **Cloud Scheduler** (preferred if using GCP): deploy container, set hourly trigger, store secrets in **Secret Manager**.  
   - **AWS Lambda** + EventBridge Scheduler (hourly rule; Secrets Manager/SSM).  
   - **A simple VM/VPS** with system cron (`0 * * * *`) and a virtualenv/service user.  
   Include setup steps for secrets, environment variables, and minimal monitoring/log viewing per platform.
12) Pick a **recommended** hosting path based on reliability, simplicity, and your earlier provider choices. Provide exact deployment & cron config instructions.

### Phase E — Observability, Reliability & Ops
13) Define logging format and minimal metrics (alerts sent, last wind reading, errors).  
14) Define alert throttling/dedup policy and state storage (file, SQLite, Redis, or cloud KV).  
15) Define error handling & retries (HTTP backoff, SMS fallback).  
16) Provide a **runbook**: what to check if no alerts arrive or if constant alerts fire.

### Phase F — Security & Cost
17) Secrets handling (never commit keys; platform secrets/SM).  
18) Principle of least privilege.  
19) Provide **rough monthly cost** estimates for the chosen wind API + SMS usage (assume 720 checks/month, low alert frequency) and the hosting option.

## Deliverable Formatting
- File name: `wreck-beach-wind-alert-cron-plan.md`
- Start with an executive summary (1–2 paragraphs).
- Include short comparison tables for Wind APIs and SMS providers.
- Provide **citations with links** for all external facts/pricing/docs.
- No executable code is required; short pseudo-code is allowed only if clarifying.
- End with a concise checklist of tasks to implement.

Now execute the above, perform the research, and output ONLY the single Markdown file.
