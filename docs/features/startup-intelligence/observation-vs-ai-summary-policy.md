# Observation vs. AI Summary Separation Policy
## Workstream E Specification

- **Module:** `startup-intelligence`
- **Frontend Route:** `/startups/[opportunityId]`

---

## 1. Principles of Separation

To eliminate AI hallucinations and ensure trust, RIGHT FIT enforces a strict architectural and visual boundary between **Direct Observations** and **Machine-Generated Summaries**:

| Dimension | Observation (Evidence) | AI Summary (Interpretation) |
|---|---|---|
| **Data Source** | Verbatim text directly crawled from public feeds or website headers. | Synthesized by Google Gemini (`gemini-2.0-flash`) or local heuristic templates. |
| **Trust Level** | Primary source fact. | Inferential hypothesis. |
| **Presentation** | Tab 1: "Observation Ledger" with quote styling and provenance links. | Tab 2: "AI Summary & Strategy" with explicit machine-generation badges. |
| **Legal Status** | Public statements or public technical metrics. | Machine opinion; not an official founder statement. |
| **Mandatory Label** | "Unverified public claim" or "Audit metric". | "This summary is machine-generated based on public signals and does not represent an official statement or budget commitment from the target organization." |

---

## 2. Model Metadata Preservation

For every AI summary generated, Core preserves:
1. `ai_model`: The specific model ID (e.g., `gemini-2.0-flash` or `template-heuristic`).
2. `ai_generated_at`: UTC timestamp of generation.
3. `confidence_score`: Heuristic match rating.
4. `human_review_status`: Explicit flag indicating whether a human engineer reviewed the synthesis.

