# 🧠 VALIS Master Plan

This document outlines the high-level architecture, strategic vision, and upcoming sprints for the VALIS universal AI engine.

---

## 🎯 Vision

> VALIS is a universal AI ego engine designed to scale from local apps to global access. It supports complex identity, memory, and personality systems across any model, provider, or interface — with full endpoint delivery, diagnostics, and dashboard control.

---

## 📊 Architecture Overview (See Mermaid Diagrams in `/plan`)

* `valis_overview.mmd` — Global request flow from UI → engine → model
* `valis_memory_stack.mmd` — Five-layer memory abstraction
* `valis_provider_flow.mmd` — Cascade and provider plug-in system
* `valis_future_cloud.mmd` — AWS-style scaling vision

---

## 🪜 Strategic Milestones

| Stage | Focus                    | Outcome                             |
| ----- | ------------------------ | ----------------------------------- |
| ✅ 1   | Memory System            | 5-layer unified memory with tagging |
| 🔄 2  | Provider Interface       | Provider-agnostic memory injection  |
| ⏭️ 3  | Dashboard                | Dev + diagnostic web interface      |
| ⏳ 4   | Persistence Layer        | Redis/Postgres integration          |
| ⏳ 5   | API Gateway              | Secure request routing at scale     |
| ⏳ 6   | Deployment               | Docker, ECS/Kubernetes pipeline     |
| ⏳ 7   | Load Testing             | Simulate thousands of chats         |
| ⏳ 8   | SDKs / Endpoint Delivery | VALIS beams to any app              |

---

## 🧠 Sprint 7: Prompt Bridge for Providers

**Goal**: Ensure all providers (starting with Claude MCP) receive full memory + persona stack as prompt.

### ✅ Tasks

* Build `PromptComposer` that formats memory stack for Claude
* Create Claude-specific template for roleplay prompt
* Integrate `PromptComposer` into MCP persistent bridge
* Add toggle to test prompt via CLI (`test_prompt_render.py`)

### ✅ Acceptance

* MCP returns characterful, memory-aware response
* Prompt debug tool confirms all memory layers visible in prompt

---

## 🖥️ Sprint 8: Dashboard & Diagnostics (v1)

**Goal**: Create a web-based interface for dev inspection, persona selection, and direct chat.

### ✅ Tasks

* Build FastAPI backend (if not already present)
* Create `/dashboard` endpoint w/ auth + static frontend
* UI components:

  * Persona selector
  * Chat window (streaming or reload-based)
  * Memory viewer panel (layers 1–5)
* Hook chat backend to `VALISEngine`

### ✅ Acceptance

* Chat works through dashboard
* Memory layers shown live
* Devs can inspect persona state + log

---

## 💾 Sprint 9: Persistence Layer Abstraction

**Goal**: Wire memory to scalable backends — but keep file fallback.

### ✅ Tasks

* Design `StorageAdapter` interface
* Add Redis adapter (for session + general mem)
* Add Postgres or Mongo adapter (for canon + client mem)
* Fallback to file-based JSON if not connected

### ✅ Acceptance

* Memory routing works w/ Redis/Postgres
* JSON fallback still functional
* Clear config for switching storage type

---

## 📌 Notes for Scaling

* The provider system must stay modular (OpenAI, Claude, Ollama, etc.)
* Memory must be portable, independent, and injectable
* The API layer must be rate-limited, stateless, horizontally scalable
* Redis should hold volatile layers; DB holds persistent identity
* Personas should eventually be user-editable with audit tracking
* Deployment target: Docker, ECS, or Kubernetes with healthcheck probes

---

> This plan is the living blueprint of VALIS. Update it as components evolve.
