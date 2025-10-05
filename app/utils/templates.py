# app/utils/templates.py
SUMMARY_PROMPT = """
You are generating a structured summary for NASA bioscience publication.
Title: {title}
Abstract: {abstract}

Focus section: {focus_section}
Persona: {persona}

Return JSON with keys:
- bullet_summary (array of <=5 bullet points)
- key_findings (array of insightful findings)
- risk_assessment (array describing risks to human/tissue health in space)
- recommended_actions (array of actionable next steps)
Use concise professional language.
"""