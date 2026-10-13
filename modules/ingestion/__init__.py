"""Modules Ingestion package for Provenance.

Exports:
- build_corpus() -> None
- find_experts(topic: str, role: Role) -> list[Expert]
- onboarding_path(job_role: str, role: Role) -> OnboardingPath
"""

from __future__ import annotations

from contracts import Expert, OnboardingPath, Role
from modules.ingestion.builder import build, build_corpus
from modules.ingestion.connectors import (
    EmailConnector,
    SharePointConnector,
    SopConnector,
    TeamsConnector,
)
from modules.ingestion.experts import find_experts
from modules.ingestion.onboarding import onboarding_path

__all__ = [
    "build_corpus",
    "find_experts",
    "onboarding_path",
    "build",
    "SharePointConnector",
    "SopConnector",
    "EmailConnector",
    "TeamsConnector",
]
