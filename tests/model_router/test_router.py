import logging
import unittest

from services.model_router.config import ModelRouterConfig
from services.model_router.providers.devmonster_ollama import ProviderResult
from services.model_router.router import ModelRouter, RouteRequest


class FakeDevMonsterProvider:
    name = "devmonster_ollama"

    def health_check(self):
        return ProviderResult(ok=True, data={"provider": self.name})

    def list_models(self):
        return ProviderResult(ok=True, data={"models": [{"name": "gemma4:26b"}]})

    def generate(self, prompt, model=None):
        self.prompt = prompt
        self.model = model
        return ProviderResult(ok=True, data={"text": "Router operational."})


class ModelRouterTest(unittest.TestCase):
    def test_safe_gemma4_generate_route(self):
        provider = FakeDevMonsterProvider()
        config = ModelRouterConfig(
            devmonster_ollama_url="http://100.93.120.124:11434",
            devmonster_default_model="gemma4:26b",
            openai_api_key="",
            anthropic_api_key="",
            timeout_seconds=1.0,
        )
        router = ModelRouter(config=config, devmonster_provider=provider)

        response = router.generate(
            RouteRequest(
                task_type="summaries",
                model="gemma4:26b",
                prompt="Reply with exactly: Router operational.",
            )
        )

        self.assertEqual(response.provider, "devmonster_ollama")
        self.assertEqual(response.model, "gemma4:26b")
        self.assertEqual(response.text, "Router operational.")
        self.assertEqual(response.task_type, "summaries")
        self.assertGreaterEqual(response.elapsed_seconds, 0)
        self.assertFalse(response.human_approval_required)
        self.assertTrue(response.timestamp)
        self.assertEqual(provider.prompt, "Reply with exactly: Router operational.")
        self.assertEqual(provider.model, "gemma4:26b")

    def test_human_approval_task_routes_to_devmonster_with_flag(self):
        provider = FakeDevMonsterProvider()
        config = ModelRouterConfig(
            devmonster_ollama_url="http://100.93.120.124:11434",
            devmonster_default_model="gemma4:26b",
            openai_api_key="",
            anthropic_api_key="",
            timeout_seconds=1.0,
        )
        router = ModelRouter(config=config, devmonster_provider=provider)

        decision = router.route("Google Workspace actions")

        self.assertEqual(decision.provider, "devmonster_ollama")
        self.assertEqual(decision.model, "gemma4:26b")
        self.assertTrue(decision.human_approval_required)

    def test_cloud_reserved_task_fails_closed(self):
        provider = FakeDevMonsterProvider()
        config = ModelRouterConfig(
            devmonster_ollama_url="http://100.93.120.124:11434",
            devmonster_default_model="gemma4:26b",
            openai_api_key="",
            anthropic_api_key="",
            timeout_seconds=1.0,
        )
        router = ModelRouter(config=config, devmonster_provider=provider)

        logging.disable(logging.CRITICAL)
        try:
            with self.assertRaises(RuntimeError):
                router.generate(
                    RouteRequest(
                        task_type="advanced coding",
                        model="gemma4:26b",
                        prompt="Reply with exactly: Router operational.",
                    )
                )
        finally:
            logging.disable(logging.NOTSET)


if __name__ == "__main__":
    unittest.main()
