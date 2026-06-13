import json
import tempfile
import unittest
from pathlib import Path

from services.hermes_safety.audit_log import (
    REQUIRED_FIELDS,
    build_audit_event,
    redact_event,
    write_audit_event,
)


class HermesAuditLogTest(unittest.TestCase):
    def test_write_audit_event_creates_local_jsonl_file(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            event = build_audit_event(
                phase="6M",
                actor="codex",
                authority_tier="tier_0_observe",
                action_type="observe",
                target_type="policy",
                target_identifier="local-audit-test",
                status="succeeded",
                risk_level="low",
                rollback_available=False,
                human_summary="Audit primitive wrote one local test event.",
                machine_summary="audit_write_test",
                timestamp="2026-06-13T00:00:00Z",
                event_id="audit_test_001",
            )

            written = write_audit_event(event, log_dir=Path(temp_dir) / "audit")

            output_path = Path(temp_dir) / "audit" / "events-2026-06-13.jsonl"
            self.assertTrue(output_path.exists())
            rows = output_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(rows), 1)
            parsed = json.loads(rows[0])
            self.assertEqual(parsed, written)
            self.assertEqual(parsed["event_id"], "audit_test_001")

    def test_audit_event_includes_required_fields(self):
        event = build_audit_event(
            phase="6M",
            actor="codex",
            authority_tier="tier_0_observe",
            action_type="observe",
            target_type="policy",
            target_identifier="required-fields",
            status="succeeded",
            risk_level="low",
            rollback_available=False,
            human_summary="Required fields test.",
            machine_summary="required_fields_test",
        )

        for field in REQUIRED_FIELDS:
            with self.subTest(field=field):
                self.assertIn(field, event)

        self.assertTrue(event["event_id"].startswith("audit_"))

    def test_redacts_secret_values_and_secret_like_keys(self):
        raw_secret = "sk-test-secret-value"
        event = build_audit_event(
            phase="6M",
            actor="codex",
            authority_tier="tier_0_observe",
            action_type="policy_violation",
            target_type="policy",
            target_identifier=raw_secret,
            status="blocked",
            risk_level="high",
            rollback_available=False,
            human_summary="Secret redaction test.",
            machine_summary="secret_redaction_test",
            metadata={
                "api_key": "value-that-must-not-survive",
                "nested": {"token": "nested-token-value"},
                "safe": "kept",
            },
        )

        redacted, changed = redact_event(event)
        serialized = json.dumps(redacted, sort_keys=True)

        self.assertTrue(changed)
        self.assertTrue(redacted["redaction_applied"])
        self.assertNotIn(raw_secret, serialized)
        self.assertNotIn("value-that-must-not-survive", serialized)
        self.assertNotIn("nested-token-value", serialized)
        self.assertIn("[REDACTED]", serialized)
        self.assertIn("kept", serialized)

    def test_write_rejects_missing_required_fields(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            with self.assertRaises(ValueError):
                write_audit_event({"phase": "6M"}, log_dir=Path(temp_dir) / "audit")


if __name__ == "__main__":
    unittest.main()
