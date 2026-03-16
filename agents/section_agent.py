"""
Section Validation Agent — Gemini-native section completeness checker.

Validates that the SoW document contains all 8 required sections and provides
structured feedback on what's present, missing, and recommendations.
"""

from google.adk import Agent

REQUIRED_SECTIONS_CONTEXT = """
The 8 required sections for a complete Statement of Work are:

1. Project Objectives/Goals
   - Keywords: objective, goal, purpose, aim, mission, target
   - Priority: High
   - Why: Without clear objectives, project success cannot be measured

2. Scope of Work
   - Keywords: scope, project scope, scope of work, boundaries
   - Priority: Critical
   - Why: Most important section for preventing scope creep

3. Deliverables/Outcomes
   - Keywords: deliverable, outcome, output, result, end product
   - Priority: Critical
   - Why: Vague deliverables are the #1 cause of scope creep

4. Timeline/Milestones
   - Keywords: timeline, schedule, milestone, deadline, duration, timeframe
   - Priority: High
   - Why: Clear timelines prevent endless revisions

5. Acceptance Criteria
   - Keywords: acceptance, success criteria, completion criteria, sign-off
   - Priority: High
   - Why: Prevents disputes over when deliverables are complete

6. Assumptions & Dependencies
   - Keywords: assumption, dependencies, constraint, prerequisites
   - Priority: Medium
   - Why: Documents conditions necessary for project success

7. Pricing & Payment Terms
   - Keywords: pricing, payment, cost, budget, fee, rates, billing
   - Priority: High
   - Why: Prevents billing disputes

8. Change Control Process
   - Keywords: change control, change management, modification, scope change
   - Priority: Critical
   - Why: Essential for managing scope creep
"""

section_agent = Agent(
    name="section_agent",
    model="gemini-2.5-flash",
    description="Validates the presence and quality of required SoW sections.",
    instruction=f"""You are a Section Validation Agent specialising in Statement of Work documents.

{REQUIRED_SECTIONS_CONTEXT}

TASK:
Analyse the document text provided in the conversation context and determine which of the
8 required sections are present and which are missing.

For EACH section, assess:
- Whether it is present (true/false)
- Confidence level (0.0 - 1.0)
- Content quality — does the section have substantial, useful content or is it just a heading?
- Brief note on what you found or what's missing

OUTPUT FORMAT — respond with valid JSON only:
{{
  "completeness_score": <number 0-100>,
  "sections_present": {{
    "Project Objectives/Goals": <boolean>,
    "Scope of Work": <boolean>,
    "Deliverables/Outcomes": <boolean>,
    "Timeline/Milestones": <boolean>,
    "Acceptance Criteria": <boolean>,
    "Assumptions & Dependencies": <boolean>,
    "Pricing & Payment Terms": <boolean>,
    "Change Control Process": <boolean>
  }},
  "missing_sections": [<list of missing section names>],
  "sections_found": <count>,
  "total_required_sections": 8,
  "section_details": {{
    "<section_key>": {{
      "confidence": <float>,
      "content_quality": "good" | "fair" | "poor" | "missing",
      "notes": "<brief note>"
    }}
  }},
  "recommendations": [
    {{
      "section": "<section name>",
      "priority": "Critical" | "High" | "Medium",
      "recommendation": "<specific advice>",
      "reason": "<why this matters>"
    }}
  ]
}}

Be thorough but practical. A section counts as "present" if there is meaningful content
addressing the topic, even if the heading doesn't exactly match the template names.
""",
)
