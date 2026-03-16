"""
Tests for the multi-agent audit pipeline.

These tests validate:
1. Agent module imports work correctly
2. The audit_runner can parse agent responses
3. The normalisation logic produces UI-compatible output
"""

import sys
import json
import pytest
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from audit_runner import _parse_agent_response, _normalize_results, _build_fallback_results


# --- Response Parsing Tests ---

class TestResponseParsing:

    def test_parse_clean_json(self):
        """Test parsing a clean JSON response."""
        response = json.dumps({
            "section_validation": {
                "completeness_score": 62.5,
                "sections_present": {"Scope of Work": True, "Deliverables/Outcomes": True},
                "missing_sections": ["Acceptance Criteria"],
                "sections_found": 5,
                "total_required_sections": 8,
            },
            "vagueness_analysis": {
                "vague_items": [{"type": "Vague Quantity", "text": "several", "severity": "Medium"}],
                "vagueness_percentage": 3.5,
                "total_vague_instances": 5,
            },
            "risk_assessment": {
                "risk_score": 45.0,
                "risk_items": [{"risk_level": "High", "text": "as needed"}],
                "total_risks": 3,
            },
            "quality_check": {
                "quality_score": 78.0,
                "issues": [],
                "total_issues": 0,
            },
        })

        result = _parse_agent_response(response, "test.txt")

        assert result["section_validation"]["completeness_score"] == 62.5
        assert result["vagueness_analysis"]["total_vague_instances"] == 5
        assert result["risk_assessment"]["risk_score"] == 45.0
        assert result["quality_check"]["quality_score"] == 78.0
        assert result["document_info"]["filename"] == "test.txt"

    def test_parse_json_in_markdown_block(self):
        """Test parsing JSON embedded in a markdown code block."""
        response = '''Here is the analysis:

```json
{
    "section_validation": {"completeness_score": 75, "sections_present": {}, "missing_sections": []},
    "vagueness_analysis": {"vague_items": [], "vagueness_percentage": 0, "total_vague_instances": 0},
    "risk_assessment": {"risk_score": 20, "risk_items": [], "total_risks": 0},
    "quality_check": {"quality_score": 90, "issues": [], "total_issues": 0}
}
```
'''
        result = _parse_agent_response(response, "doc.docx")
        assert result["section_validation"]["completeness_score"] == 75
        assert result["quality_check"]["quality_score"] == 90

    def test_fallback_on_invalid_response(self):
        """Test that fallback results are generated when parsing fails."""
        response = "This is not JSON at all, just plain text analysis."
        result = _parse_agent_response(response, "bad.txt")

        # Should have the expected structure even on failure
        assert "document_info" in result
        assert "section_validation" in result
        assert "vagueness_analysis" in result
        assert "risk_assessment" in result
        assert "quality_check" in result


class TestNormalization:

    def test_normalize_with_missing_keys(self):
        """Test that normalization handles missing keys gracefully."""
        data = {
            "section_validation": {"completeness_score": 50},
            # vagueness, risk, quality missing entirely
        }
        result = _normalize_results(data, "test.pdf")

        assert result["section_validation"]["completeness_score"] == 50
        assert result["vagueness_analysis"]["vague_items"] == []
        assert result["risk_assessment"]["risk_score"] == 0
        assert result["quality_check"]["quality_score"] == 0

    def test_normalize_preserves_document_info(self):
        """Test that document info is correctly set."""
        data = {}
        result = _normalize_results(data, "contract.docx")

        assert result["document_info"]["filename"] == "contract.docx"
        assert result["document_info"]["file_type"] == "docx"


class TestFallbackResults:

    def test_fallback_structure(self):
        """Test that fallback results have complete structure."""
        result = _build_fallback_results("error text", "file.txt")

        assert result["document_info"]["filename"] == "file.txt"
        assert isinstance(result["section_validation"]["missing_sections"], list)
        assert result["vagueness_analysis"]["ai_enhanced"] is True
        assert result["risk_assessment"]["risk_score"] == 0
        assert result["quality_check"]["quality_score"] == 0


# --- Agent Import Tests ---

class TestAgentImports:

    def test_agents_package_imports(self):
        """Test that the agents package can be imported."""
        from agents.orchestrator import root_agent
        assert root_agent is not None
        assert root_agent.name == "sow_audit_orchestrator"

    def test_sub_agents_exist(self):
        """Test that all sub-agents are accessible."""
        from agents.section_agent import section_agent
        from agents.vagueness_agent import vagueness_agent
        from agents.risk_agent import risk_agent
        from agents.quality_agent import quality_agent

        assert section_agent.name == "section_agent"
        assert vagueness_agent.name == "vagueness_agent"
        assert risk_agent.name == "risk_agent"
        assert quality_agent.name == "quality_agent"
