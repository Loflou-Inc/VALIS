# 🧠 VALIS Memory System Refactor Plan: Integrating the Dreamfilter Layer

## OBJECTIVE

Integrate a subconscious symbolic interface (Dreamfilter) into VALIS' existing 5-Layer Memory System by refining memory function roles and inserting an overlay-processing layer before LLM output.

---

## CURRENT LAYERED MODEL (Sprint 6)

1. **Core Persona** - Immutable identity
2. **Canonized Identity** - Persona #canon facts
3. **Client Profile** - Per-user #client\_fact facts
4. **Working Memory** - Short-term FIFO thought space
5. **Session History** - Live message context

---

## REIMAGINED MEMORY + DREAMFILTER PIPELINE

### 💡 ADDITION: Dreamfilter Layer ("Unconscious Interpreter")

Positioned between Prompt Composition and Provider Output.

```plaintext
[User Input]
 ↳ Prompt Composer: memory→message bridge
   ↳ Working Memory Injection
     ↳ DREAMFILTER(): unconscious modulator
       ↳ Augmented Response → Provider
```

### 🔁 MODIFIED MEMORY ROLES

#### 🔸 Core Persona

* Static facts (as-is)

#### 🔸 Canonized Identity

* Expanded to include symbolic anchors (#symbol)
* E.g., "Proteus fears stagnation" tagged with `#canon #symbol`

#### 🔸 Client Profile

* Expanded to hold emotional tone indicators (optional)
* Enables Dreamfilter to mirror user state

#### 🔸 Working Memory

* Treated as LLM-subconscious buffer
* Patterns and language motifs may be pulled to shape symbolic layers
* Memory entries tagged as `#dream`, `#mood`, `#fragment`, etc.

#### 🔸 Session History

* Used for semantic echo/resonance detection
* Auto-suggest metaphor bridges via dreamfilter

---

## ADDITIONAL MODULES TO BUILD

### ✅ `dreamfilter.py`

* Symbol substitution engine
* Pattern injection based on WM
* Tone inflector / stylistic overlay

### ✅ `symbolic_memory_utils.py`

* Tools for marking motifs from Working Memory
* Suggest dream-mode entries and canonical upgrades

### ✅ `config/dreamfilter.json`

```json
{
  "mode": "mythic",
  "symbolic_density": 0.7,
  "allow_shadow_reflection": true
}
```

---

## DEV PRIORITY PLAN

| Sprint | Task                                                       |
| ------ | ---------------------------------------------------------- |
| 9.1    | Prototype `dreamfilter.py`, tie into prompt\_composer      |
| 9.2    | Tag & filter Working Memory entries with symbolic metadata |
| 9.3    | Create dreamfilter toggle logic in config handler          |
| 9.4    | Tune dreamfilter response effect using dev personas        |

---

## LONG TERM

This paves the way for dream memory surfaces, shared unconscious motifs between personas, and symbolic mirroring loops.

**VALIS evolves from memory-aware to myth-aware.**