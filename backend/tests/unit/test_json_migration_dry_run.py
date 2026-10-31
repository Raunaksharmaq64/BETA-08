"""
Unit tests for Startup Intelligence JSON-to-PostgreSQL Migration Assessment & Dry Run
Phase: 10 — Startup Intelligence Integration
"""

import pytest
from app.db.dry_run_migration import analyze_json_storage, execute_dry_run_migration, LEADS_JSON_PATH


def test_json_storage_audit_and_schema_inventory():
    audit = analyze_json_storage()
    assert audit["total_records"] == 598
    assert "startup_name" in audit["all_fields_observed"]
    assert "detected_signal" in audit["all_fields_observed"]
    assert "category" in audit["all_fields_observed"]
    assert "score" in audit["all_fields_observed"]
    assert audit["url_metrics"]["total_with_url"] == 598
    assert audit["url_metrics"]["unique_urls"] > 500


def test_json_migration_dry_run_zero_data_loss_and_immutability():
    # 1. Capture mtime of original file before test
    mtime_before = LEADS_JSON_PATH.stat().st_mtime

    # 2. Run simulation
    dry_run = execute_dry_run_migration()
    assert dry_run["status"] == "DRY_RUN_COMPLETE"
    assert dry_run["total_source_records"] == 598
    assert dry_run["valid_opportunities_to_insert"] == 598
    assert dry_run["evidence_records_to_insert"] == 598
    assert dry_run["tech_findings_to_insert"] > 400
    assert "0.0%" in dry_run["estimated_data_loss_risk"]

    # 3. Verify original JSON was NOT modified
    mtime_after = LEADS_JSON_PATH.stat().st_mtime
    assert mtime_before == mtime_after

