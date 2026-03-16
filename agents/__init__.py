"""
ContractAudit Multi-Agent System — powered by Google ADK.

This package contains specialized agents that work together to audit
Statement of Work (SoW) documents for scope creep risks, vague language,
missing sections, and quality issues.
"""
from agents.orchestrator import root_agent

__all__ = ["root_agent"]
