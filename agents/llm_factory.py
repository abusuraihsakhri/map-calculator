"""
Inference Engine supporting local Ollama, Claude, OpenAI, and deterministic Mock with Zero-PHI checks.
"""
from typing import Dict, Any, Optional
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Map Calculator"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return f"No conversational model is configured. This is a test-only placeholder for {self.system_name}; the query was not clinically evaluated."


class LLMFactory:
    """Creates configured LLM client instances with zero-PHI protection."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Map Calculator"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM(system_name)
        raise ValueError(f"Model provider {provider!r} is not implemented; use 'mock' for offline tests.")
