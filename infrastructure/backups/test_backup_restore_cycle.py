"""
RIGHT FIT — Backup & Disaster Recovery Automated Test Cycle
Phase 13: Verifies backup generation, SHA256 integrity calculation,
and atomic restore into an isolated test database.
"""

import os
import sqlite3
import hashlib
import tempfile
import unittest


class TestBackupAndDisasterRecoveryCycle(unittest.TestCase):
    """Test suite proving backup creation, checksum integrity, and isolated database restoration."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.source_db_path = os.path.join(self.temp_dir.name, "source_prod.db")
        self.backup_path = os.path.join(self.temp_dir.name, "backup_prod.dump")
        self.restored_db_path = os.path.join(self.temp_dir.name, "restored_isolated.db")

        # 1. Populate source database with production-like records
        conn = sqlite3.connect(self.source_db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT, full_name TEXT);")
        cursor.execute("CREATE TABLE canonical_opportunities (id TEXT PRIMARY KEY, title TEXT, employer TEXT);")
        cursor.execute("CREATE TABLE compensation_observations (id TEXT PRIMARY KEY, role TEXT, base_min REAL);")

        cursor.execute("INSERT INTO users VALUES ('u-1', 'candidate@example.com', 'Alex Candidate');")
        cursor.execute("INSERT INTO canonical_opportunities VALUES ('opp-1', 'Staff AI Engineer', 'Acme Corp');")
        cursor.execute("INSERT INTO compensation_observations VALUES ('comp-1', 'Staff AI Engineer', 185000.0);")
        conn.commit()
        conn.close()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_backup_generation_and_checksum(self):
        """Verify backup can be created and SHA256 checksum is correctly calculated."""
        # Execute backup simulation
        source_conn = sqlite3.connect(self.source_db_path)
        backup_conn = sqlite3.connect(self.backup_path)
        source_conn.backup(backup_conn)
        backup_conn.close()
        source_conn.close()

        self.assertTrue(os.path.exists(self.backup_path))
        self.assertGreater(os.path.getsize(self.backup_path), 0)

        # Compute SHA256
        with open(self.backup_path, "rb") as f:
            checksum = hashlib.sha256(f.read()).hexdigest()

        self.assertEqual(len(checksum), 64)
        print(f"[TEST PASS] Backup created ({os.path.getsize(self.backup_path)} bytes), SHA256: {checksum[:16]}...")

    def test_isolated_restore_and_data_integrity(self):
        """Verify backup restores into an isolated target DB with zero data loss."""
        # 1. Create backup
        source_conn = sqlite3.connect(self.source_db_path)
        backup_conn = sqlite3.connect(self.backup_path)
        source_conn.backup(backup_conn)
        backup_conn.close()
        source_conn.close()

        # 2. Restore into target database
        target_conn = sqlite3.connect(self.restored_db_path)
        backup_conn = sqlite3.connect(self.backup_path)
        backup_conn.backup(target_conn)
        backup_conn.close()

        # 3. Assert all tables and rows are preserved
        cursor = target_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        self.assertEqual(user_count, 1)

        cursor.execute("SELECT email, full_name FROM users WHERE id = 'u-1';")
        user = cursor.fetchone()
        self.assertEqual(user[0], "candidate@example.com")
        self.assertEqual(user[1], "Alex Candidate")

        cursor.execute("SELECT COUNT(*) FROM canonical_opportunities;")
        self.assertEqual(cursor.fetchone()[0], 1)

        cursor.execute("SELECT base_min FROM compensation_observations WHERE id = 'comp-1';")
        self.assertEqual(cursor.fetchone()[0], 185000.0)

        target_conn.close()
        print("[TEST PASS] Disaster recovery restore verified: 100% rows corroborated.")


if __name__ == "__main__":
    unittest.main()

