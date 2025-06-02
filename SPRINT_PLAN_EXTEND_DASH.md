Perfect. Below is a **focused sprint plan** to build a **VALIS Dashboard** with full chat capabilities, persona switching, diagnostic views, and basic configuration editing — ideal for development, testing, and future extensibility.

---

# 🖥️ VALIS Dashboard Sprint Plan – Chat + Diag + Config

**Sprint Duration:** 2 Weeks
**Team Focus:** Full-stack (Backend + UI/UX)
**Goal:** Build a functional web dashboard to interact with VALIS, inspect sessions/personas, and adjust configuration.

---

## 🧭 Sprint Objectives

1. ✅ Provide a real-time chat interface with persona selection
2. ✅ Show diagnostics (active sessions, last messages, provider stats)
3. ✅ Expose config settings (editable or at least viewable)
4. ✅ Lay groundwork for future use cases (memory UI, logs, history)

---

## 🔧 Backend Tasks (API Layer + Engine Integration)

### **\[API-101] Create a FastAPI or Flask-based VALIS service layer**

* Expose:

  * `POST /chat` — handles chat requests: `{ session_id, persona_id, message }`
  * `GET /personas` — return persona metadata
  * `GET /sessions` — return active sessions with metadata
  * `GET /config` — return current config
  * `GET /health` — proxy to `engine.health_check()`

> *Optional:* `POST /config` for dynamic config editing (file rewrite or in-memory swap)

### **\[API-102] Enable CORS and JSON logging for dev/frontend**

* Use `uvicorn` with debug logging
* Enable cross-origin from `localhost:3000` for local dev

### **\[API-103] Add message history tracking**

* Log per-session messages and persona responses in memory (dict or lightweight SQLite)
* Each message log: `session_id, timestamp, persona_id, message, response, provider_used`

---

## 🎨 Frontend Tasks (React + Tailwind Dashboard)

> *Use shadcn/ui for clean, modular interface components*

### **\[UI-201] Build main layout**

* Header (VALIS logo + status)
* Sidebar:

  * Persona list (selectable)
  * Active sessions list
* Main view:

  * Chat window
  * System diagnostics / config tab

### **\[UI-202] Implement persona selector**

* Load from `/personas`
* Visual card-style selector or dropdown
* Highlight current persona in chat session

### **\[UI-203] Build chat interface**

* Display back-and-forth messages with timestamps
* Input field with `Enter` submit
* Show loading spinner while waiting
* Display provider used per message (small badge)

### **\[UI-204] Session & system diagnostics panel**

* List:

  * Active sessions + last seen
  * Total # of requests
  * Provider usage/failover counts
  * Circuit-breaker status (if active)
* Call `/health` and `/sessions` periodically (e.g. every 15s)

### **\[UI-205] Configuration viewer**

* Read from `/config`
* Display current:

  * provider cascade
  * timeout limits
  * memory toggle
* Highlight if config file differs from running memory

---

## 🧪 Testing & Integration

### **\[QA-301] Smoke test: switch personas + chat**

* Ensure persona context and memory behavior work end-to-end

### **\[QA-302] Load test: 10 concurrent chats**

* Ensure per-session queuing still works
* Check UI doesn’t race or break

### **\[QA-303] Bad config + fallback sanity test**

* Provide intentionally bad config or remove a provider
* Validate fallback kicks in and dashboard shows graceful info

---

## 🚀 Deployment & Ops

### **\[OPS-401] Dev Dockerfile**

* Expose both backend (FastAPI) and frontend (React app)
* Proxy frontend requests to `/api`

### **\[OPS-402] Start with config snapshot system**

* Copy `.valis_config.json` for UI editing
* Optional save button writes to file + reloads engine

---

## 🧾 Definition of Done

* ✅ Users can select a persona and chat via browser
* ✅ See which provider handled each response
* ✅ Live config + session state view
* ✅ Engine runs as async service
* ✅ Logs visible in console or structured log
* ✅ Foundation ready for history/memory features

---

## 📂 Suggested File Layout

```
valis-dashboard/
├── backend/       # FastAPI app
│   ├── main.py
│   ├── routers/
│   ├── valis_service.py
├── frontend/      # React + Tailwind + shadcn/ui
│   ├── src/
│   ├── components/
│   ├── pages/
├── docker/
│   ├── Dockerfile
│   └── nginx.conf (if needed)
```

---

Would you like a code scaffold for this (e.g., working FastAPI + React starter kit)? I can drop that next if helpful.
