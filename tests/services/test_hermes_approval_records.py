import json
import tempfile
import unittest
from pathlib import Path

from services.hermes_safety.approval_records import (
    create_approval_request,
    is_approval_valid,
    mark_approval_used,
    read_approval_records,
    validate_approval_record,
    write_approval_record,
)


def sample_request(**overrides):
    record = create_approval_request(
        requested_by="human",
        authority_tier="tier_3_local_approved_execution",
        action_type="service_start",
        target="adapter-service",
        scope="start approved localhost adapter service once",
        exact_command_or_operation="scripts/adapter_service_start.sh",
        allowed_paths=["scripts/adapter_service_start.sh"],
        forbidden_paths=["~/.ssh", "~/.hermes"],
        expiration="2026-06-14T00:00:00Z",
        one_time_use=True,
        risk_level="medium",
        rollback_plan="scripts/adapter_service_stop.sh",
        human_summary="Allow one manual adapter start.",
        timestamp_requested="2026-06-13T00:00:00Z",
        approval_id="approval_test_001",
    )
    record.update(overrides)
    return record


class HermesApprovalRecordsTest(unittest.TestCase):
    def test_write_and_read_approval_records_locally(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            record = sample_request()
            written = write_approval_record(record, log_dir=Path(temp_dir) / "approvals")

            output_path = Path(temp_dir) / "approvals" / "approvals-2026-06-13.jsonl"
            self.assertTrue(output_path.exists())
            rows = output_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(rows), 1)
            self.assertEqual(json.loads(rows[0]), written)

            records = read_approval_records(log_dir=Path(temp_dir) / "approvals")
            self.assertEqual(records, [written])

    def test_expiration_and_one_time_use(self):
        granted = sample_request(
            status="granted",
            approved_by="michael",
            timestamp_granted="2026-06-13T00:01:00Z",
        )

        self.assertTrue(is_approval_valid(granted, now="2026-06-13T12:00:00Z"))
        self.assertFalse(is_approval_valid(granted, now="2026-06-15T00:00:00Z"))

        used = mark_approval_used(granted)
        self.assertEqual(used["status"], "used")
        self.assertFalse(is_approval_valid(used, now="2026-06-13T12:00:00Z"))

    def test_no_model_only_or_blanket_permanent_approval(self):
        model_granted = sample_request(status="granted", approved_by="model")
        with self.assertRaises(ValueError):
            validate_approval_record(model_granted)

        blanket = sample_request(scope="*", expiration="never")
        with self.assertRaises(ValueError):
            validate_approval_record(blanket)

    def test_redacts_secret_values(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            record = sample_request(
                target="sk-test-secret-value",
                exact_command_or_operation="cat ~/.ssh/token",
            )
            written = write_approval_record(record, log_dir=Path(temp_dir) / "approvals")
            serialized = json.dumps(written, sort_keys=True)

            self.assertNotIn("sk-test-secret-value", serialized)
            self.assertIn("[REDACTED]", serialized)

    def test_sensitive_action_types_are_representable_without_execution(self):
        for action_type in ("service_start", "command_execute", "git_push", "resident_start"):
            with self.subTest(action_type=action_type):
                record = sample_request(action_type=action_type, approval_id=f"approval_{action_type}")
                validate_approval_record(record)
                self.assertEqual(record["action_type"], action_type)

    def test_missing_required_fields_are_rejected(self):
        record = sample_request()
        del record["expiration"]

        with self.assertRaises(ValueError):
            validate_approval_record(record)


if __name__ == "__main__":
    unittest.main()
