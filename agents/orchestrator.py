"""
Orchestrator — SequentialAgent that runs all sub-agents in order.

Pipeline: parser → section → vagueness → risk → quality
Each agent receives the accumulated context from prior agents,
enabling feedback loops (e.g., risk agent sees vagueness findings).
"""

from google.adk import Agent
from agents.parser_agent import parser_agent
from agents.section_agent import section_agent
from agents.vagueness_agent import vagueness_agent
from agents.risk_agent import risk_agent
from agents.quality_agent import quality_agent


root_agent = Agent(
    name="sow_audit_orchestrator",
    model="gemini-2.5-flash",
    description="Orchestrates the complete SoW audit pipeline across 5 specialised agents.",
    instruction="""You are the SoW Audit Orchestrator. You coordinate a team of specialised agents
to perform a comprehensive Statement of Work audit.

WORKFLOW:
1. First, receive the document text from the user
2. Pass the document text to each sub-agent in sequence
3. Each agent builds on the findings of previous agents:
   - Section Agent: validates document structure
   - Vagueness Agent: detects vague language (uses section findings to focus)
   - Risk Agent: assesses scope creep risks (uses section + vagueness findings)
   - Quality Agent: checks grammar, spelling, formatting

After all agents complete, compile a FINAL AUDIT SUMMARY with:
- Document information
- Overall scores from each agent
- Key findings summary
- Top 5 priority actions

Delegate to your sub-agents by asking them to analyse the document.
Pass the full document text and accumulated findings between agents.

OUTPUT your final summary as JSON with this structure:
{
  "document_info": {"filename": "<name>", "analysis_date": "<date>"},
  "section_validation": <section_agent output>,
  "vagueness_analysis": <vagueness_agent output>,
  "risk_assessment": <risk_agent output>,
  "quality_check": <quality_agent output>,
  "overall_score": <float 0-100>,
  "priority_actions": ["<action1>", "<action2>", ...]
}
""",
    sub_agents=[section_agent, vagueness_agent, risk_agent, quality_agent],
)
