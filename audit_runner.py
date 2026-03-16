"""
Audit Runner — Bridge between Google ADK agents and Streamlit.

Provides a synchronous `run_audit()` function that:
1. Creates an ADK Runner + InMemorySessionService
2. Sends the document text to the orchestrator agent
3. Collects all agent responses
4. Parses the structured JSON output
5. Returns results in the format expected by the Streamlit UI
"""

import asyncio
import json
import re
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from agents.orchestrator import root_agent

logger = logging.getLogger(__name__)


async def _run_audit_async(document_text: str, filename: str) -> Dict[str, Any]:
    """
    Run the full audit pipeline asynchronously via ADK.

    Args:
        document_text: The extracted text content of the document.
        filename: Original filename for the report.

    Returns:
        Audit results dictionary compatible with the Streamlit UI.
    """
    # Create session service and runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="contract_audit",
        session_service=session_service,
    )

    # Create a session
    user_id = "streamlit_user"
    session_id = str(uuid.uuid4())
    session = await session_service.create_session(
        app_name="contract_audit",
        user_id=user_id,
        session_id=session_id,
    )

    # Build the user message with the document
    user_message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=f"""Please perform a complete SoW audit on the following document.

DOCUMENT FILENAME: {filename}
ANALYSIS DATE: {datetime.now().isoformat()}

DOCUMENT TEXT:
---
{document_text[:50000]}
---

Analyse this Statement of Work document using all your sub-agents:
1. Section Validation — check for all 8 required sections
2. Vagueness Detection — find vague language and scope risks
3. Risk Assessment — assess scope creep risks with business impact
4. Quality Check — grammar, spelling, formatting, professionalism

After all analyses, provide the compiled results as a single JSON object.
""")]
    )

    # Run the agent and collect responses
    final_response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
    ):
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    final_response_text += part.text

    # Parse the response
    return _parse_agent_response(final_response_text, filename)


def _parse_agent_response(response_text: str, filename: str) -> Dict[str, Any]:
    """
    Parse the agent's response into the structured format expected by the UI.
    Handles both clean JSON and JSON embedded in markdown code blocks.
    """
    # Try to extract JSON from the response
    json_data = None

    # First try: direct JSON parse
    try:
        json_data = json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Second try: extract from markdown code blocks
    if json_data is None:
        json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', response_text, re.DOTALL)
        if json_match:
            try:
                json_data = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

    # Third try: find the largest JSON object in the text
    if json_data is None:
        json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
        for match in sorted(json_matches, key=len, reverse=True):
            try:
                json_data = json.loads(match)
                break
            except json.JSONDecodeError:
                continue

    # Build the result in the expected UI format
    if json_data:
        return _normalize_results(json_data, filename)
    else:
        logger.warning("Could not parse JSON from agent response, using fallback")
        return _build_fallback_results(response_text, filename)


def _normalize_results(data: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """
    Normalize agent output to match the exact format expected by the Streamlit UI.
    """
    # Build section validation results
    section_data = data.get("section_validation", {})
    section_results = {
        "completeness_score": section_data.get("completeness_score", 0),
        "sections_present": section_data.get("sections_present", {}),
        "missing_sections": section_data.get("missing_sections", []),
        "sections_found": section_data.get("sections_found", 0),
        "total_required_sections": section_data.get("total_required_sections", 8),
        "section_details": section_data.get("section_details", {}),
        "recommendations": section_data.get("recommendations", []),
    }

    # Build vagueness results
    vagueness_data = data.get("vagueness_analysis", {})
    vagueness_results = {
        "vague_items": vagueness_data.get("vague_items", []),
        "vagueness_percentage": vagueness_data.get("vagueness_percentage", 0),
        "total_vague_instances": vagueness_data.get("total_vague_instances", 0),
        "suggestions": vagueness_data.get("suggestions", []),
        "severity_breakdown": vagueness_data.get("severity_breakdown", {"High": 0, "Medium": 0, "Low": 0}),
        "ai_enhanced": True,
    }

    # Build risk results
    risk_data = data.get("risk_assessment", {})
    risk_results = {
        "risk_score": risk_data.get("risk_score", 0),
        "risk_items": risk_data.get("risk_items", []),
        "total_risks": risk_data.get("total_risks", 0),
        "risk_breakdown": risk_data.get("risk_breakdown", {"High": 0, "Medium": 0, "Low": 0}),
        "priority_risks": risk_data.get("priority_risks", risk_data.get("risk_items", [])[:10]),
        "mitigation_strategies": risk_data.get("mitigation_strategies", []),
        "ai_enhanced": True,
        "risk_categories": risk_data.get("risk_categories", {}),
    }

    # Build quality results
    quality_data = data.get("quality_check", {})
    quality_results = {
        "quality_score": quality_data.get("quality_score", 0),
        "issues": quality_data.get("issues", []),
        "total_issues": quality_data.get("total_issues", 0),
        "issue_breakdown": quality_data.get("issue_breakdown", {}),
        "suggestions": quality_data.get("suggestions", []),
        "ai_enhanced": True,
        "readability_metrics": quality_data.get("readability_metrics", {}),
    }

    return {
        "document_info": {
            "filename": filename,
            "file_type": filename.split(".")[-1] if "." in filename else "unknown",
            "analysis_date": datetime.now().isoformat(),
        },
        "section_validation": section_results,
        "vagueness_analysis": vagueness_results,
        "risk_assessment": risk_results,
        "quality_check": quality_results,
    }


def _build_fallback_results(response_text: str, filename: str) -> Dict[str, Any]:
    """
    Build minimal results when JSON parsing fails.
    The response text is preserved so the user can still see the analysis.
    """
    return {
        "document_info": {
            "filename": filename,
            "file_type": filename.split(".")[-1] if "." in filename else "unknown",
            "analysis_date": datetime.now().isoformat(),
        },
        "section_validation": {
            "completeness_score": 0,
            "sections_present": {},
            "missing_sections": ["Could not parse agent response"],
            "sections_found": 0,
            "total_required_sections": 8,
            "recommendations": [{"section": "Parse Error", "priority": "High",
                                "recommendation": "Agent response could not be parsed. Raw response available.",
                                "reason": response_text[:500]}],
        },
        "vagueness_analysis": {
            "vague_items": [],
            "vagueness_percentage": 0,
            "total_vague_instances": 0,
            "suggestions": [],
            "severity_breakdown": {"High": 0, "Medium": 0, "Low": 0},
            "ai_enhanced": True,
        },
        "risk_assessment": {
            "risk_score": 0,
            "risk_items": [],
            "total_risks": 0,
            "risk_breakdown": {"High": 0, "Medium": 0, "Low": 0},
            "priority_risks": [],
            "mitigation_strategies": [],
            "ai_enhanced": True,
            "risk_categories": {},
        },
        "quality_check": {
            "quality_score": 0,
            "issues": [],
            "total_issues": 0,
            "issue_breakdown": {},
            "suggestions": [],
            "ai_enhanced": True,
            "readability_metrics": {},
        },
    }


def run_audit(document_text: str, filename: str) -> Dict[str, Any]:
    """
    Synchronous entry point for running the audit pipeline.
    Called from Streamlit's main thread.

    Args:
        document_text: The extracted text content of the document.
        filename: Original filename for metadata.

    Returns:
        Audit results dictionary in the format expected by app.py UI.
    """
    try:
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're inside an already-running loop (e.g. Streamlit)
                # Use nest_asyncio or create a new thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, _run_audit_async(document_text, filename))
                    return future.result(timeout=300)  # 5 min timeout
            else:
                return loop.run_until_complete(_run_audit_async(document_text, filename))
        except RuntimeError:
            return asyncio.run(_run_audit_async(document_text, filename))

    except Exception as e:
        logger.error(f"Audit pipeline failed: {str(e)}", exc_info=True)
        raise RuntimeError(f"Multi-agent audit failed: {str(e)}") from e
