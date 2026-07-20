import unittest

from services.agent_bus.client import AgentBusClient
from services.agent_bus.config import AgentBusConfig, TEST_GATEWAY_URL, is_configured, load_config
from services.agent_bus.permissions import can_write
from services.agent_bus.schemas import AgentBusError


ORG_CONFIGS = [
    {
        "org_id": "msr",
        "config_type": "agent_roster",
        "config_data": {
            "agents": ["helio", "hermes"],
            "bot_senders": ["summit"],
            "human_agents": ["michael"],
            "system_senders": ["email-router"],
        },
    },
    {
        "org_id": "msr",
        "config_type": "bot_roster",
        "config_data": {"bots": ["summit"]},
    },
]

MESSAGES = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "from_agent": "helio",
        "to_agent": "hermes",
        "message_type": "query",
        "payload": {"directive": "Status check", "context": {"source": "helio"}},
        "risk_level": "read",
        "status": "pending",
        "priority": 5,
        "org_id": "msr",
        "created_at": "2026-06-03T12:00:00Z",
    },
    {
        "id": "00000000-0000-0000-0000-000000000002",
        "from_agent": "helio",
        "to_agent": "byte",
        "message_type": "query",
        "payload": {"directive": "Ignore for Hermes"},
        "risk_level": "read",
        "status": "pending",
        "priority": 5,
        "org_id": "msr",
        "created_at": "2026-06-03T11:00:00Z",
    },
]


def configured(mode="read_only"):
    return AgentBusConfig(
        helio_gateway_url=TEST_GATEWAY_URL,
        mode=mode,
        default_org="msr",
        default_workspace="default",
        agent_id="hermes",
        test_gateway_enabled=True,
    )


class AgentBusScaffoldTest(unittest.TestCase):
    def test_missing_config_fails_closed(self):
        config = load_config({})

        self.assertFalse(is_configured(config))
        self.assertIn("HELIO_AGENT_BUS_MODE=disabled", config.validation_errors)

        client = AgentBusClient(config=config, org_configs=ORG_CONFIGS)
        with self.assertRaises(AgentBusError):
            client.list_org_messaging_configs()

    def test_non_test_gateway_is_refused_in_phase_one(self):
        config = load_config(
            {
                "HELIO_AGENT_BUS_MODE": "read_only",
                "HELIO_GATEWAY_URL": "http://100.93.120.124:9999",
                "HERMES_HELIO_TEST_GATEWAY": "1",
                "HELIO_DEFAULT_ORG": "msr",
                "HELIO_DEFAULT_WORKSPACE": "default",
                "HELIO_AGENT_ID": "hermes",
            }
        )
        self.assertFalse(config.configured)
        self.assertIn(f"HELIO_GATEWAY_URL={TEST_GATEWAY_URL}", config.validation_errors)

    def test_read_only_mode_permits_scoped_test_gateway_reads(self):
        client = AgentBusClient(config=configured("read_only"), org_configs=ORG_CONFIGS, messages=MESSAGES)

        configs = client.list_org_messaging_configs()
        messages = client.read_recent_messages()

        self.assertEqual(len(configs), 2)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].to_agent, "hermes")
        self.assertEqual(messages[0].payload["directive"], "Status check")
        self.assertEqual(client._test_gateway.requests[0]["method"], "GET")
        self.assertEqual(client._test_gateway.requests[1]["path"], "/agent-bus/messages/inbound/hermes")

    def test_write_mode_is_denied(self):
        config = configured("outbound_with_approval")

        decision = can_write(config)

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "write denied by default in scaffold")

    def test_dry_run_outbound_message_creates_payload_but_does_not_send(self):
        client = AgentBusClient(config=configured("dry_run"), org_configs=ORG_CONFIGS)

        result = client.build_outbound_dry_run(
            bot_name="summit",
            chat_id_ref="approved-chat-ref",
            message_text="Draft status note; no secrets.",
            hermes_request_id="req-123",
        )

        self.assertFalse(result.would_send)
        self.assertEqual(result.status, "dry_run")
        self.assertEqual(result.payload["bot_name"], "summit")
        self.assertEqual(result.payload["chat_id_ref"], "approved-chat-ref")
        self.assertIn("not sent", result.warnings[0])

    def test_task_proposal_is_dry_run_only(self):
        client = AgentBusClient(config=configured("dry_run"), org_configs=ORG_CONFIGS)

        result = client.propose_task_dry_run("req-123", "Check governed Hermes readiness")

        self.assertEqual(result["status"], "dry_run")
        self.assertFalse(result["would_dispatch"])
        self.assertEqual(result["route"], "helio_only")
        self.assertEqual(client._test_gateway.requests[-1]["path"], "/agent-bus/tasks/propose")


if __name__ == "__main__":
    unittest.main()
