# Merge & Unmerge Audit Trail

## 1. Overview

Merging duplicate opportunities is a common data cleaning task, but erroneous merges without unmerge capabilities degrade database integrity over time. RIGHT FIT guarantees that every merge decision is **fully auditable and 100% reversible**.

---

## 2. Merge Operation Lifecycle

When `POST /api/v1/duplicates/merge` is invoked:

1. **State Snapshot**: Captures a snapshot of all duplicate opportunities (`was_suppressed`, `verification_status`, and list of `source_mapping_ids`).
2. **Suppression**: Marks each duplicate opportunity as `is_suppressed = True` so it disappears from candidate discovery.
3. **Mapping Reassignment**: Repoints all `OpportunitySourceMappingRecord`s from duplicates to the primary record with `match_method = "MERGE_DECISION"`.
4. **Immutable Decision Record**: Creates a `MergeDecisionRecord` in `merge_decisions` storing:
   - `canonical_opportunity_id`
   - `original_opportunity_ids_json`
   - `actor_id` (admin email)
   - `reason` (auditable justification)
   - `evidence_json` (containing the snapshot for reversal)
   - `status = "CONFIRMED"`

---

## 3. Reversible Unmerge Operation

When `POST /api/v1/duplicates/{decision_id}/unmerge` is invoked:

1. **Snapshot Restoration**: Retrieves `evidence_json["previous_state"]` from the decision record.
2. **Un-suppression**: Restores `is_suppressed = False` on every unmerged duplicate opportunity.
3. **Mapping Restoration**: Reassigns original source mappings back to their respective opportunities.
4. **Audit Transition**: Updates `MergeDecisionRecord`:
   - `status = "UNMERGED"`
   - `unmerged_at = utc_now()`
   - `unmerged_by = actor_id`
   - `unmerge_reason = payload.reason`

Both the merge and unmerge actions leave permanent records for auditability.

