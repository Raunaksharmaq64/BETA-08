PREFERRED_MODELS = ["gemini-2.5-flash-lite", "gemini-flash-latest", "gemini-2.5-flash"]

import google.generativeai as genai
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_agent")

def get_gemini_client(api_key: str, model_name: str = "gemini-2.5-flash-lite", system_instruction: str = None):
    """
    Configure Gemini with the user-provided API key, target model, and system instructions.
    """
    genai.configure(api_key=api_key)
    if not model_name:
        model_name = "gemini-2.5-flash-lite"
    return genai.GenerativeModel(model_name, system_instruction=system_instruction)

async def analyze_signal_with_ai(signal_data: dict, api_key: str, custom_services: str = "", model_name: str = "gemini-2.5-flash-lite", custom_system_instructions: str = "", developer_skills: str = ""):
    """
    Uses Gemini API to interpret a scraped signal (e.g. Reddit post, job post) and map it to an opportunity.
    """
    if not api_key:
        raise ValueError("Gemini API key is not configured. Please add your key in Settings.")

    try:
        system_instruction = (
            "You are an expert startup analyst, system architect, and sales outreach strategist.\n"
            "Your goal is to parse raw text signals (like hiring posts, pain point rants, or feedback requests)\n"
            "and map them into a high-value, actionable business lead with structured JSON output.\n\n"
            "CRITICAL CONSTRAINTS:\n"
            "1. Do NOT hallucinate problems or features that are not explicitly stated or strongly implied by the raw signal.\n"
            "2. Ensure the startup name is extracted accurately. If not available, use the author username or a reasonable placeholder.\n"
            "3. Limit the score to 0 to 10. The score represents: Intent (hiring/complaining = high), Recency, and Fit.\n"
            "4. Keep the pitch professional, direct, non-generic, and focused on helping them solve their specific problem.\n"
        )
        if custom_system_instructions:
            system_instruction += f"\n\nADDITIONAL USER OUTREACH AND AUDIT PARAMETERS:\n{custom_system_instructions}"
            
        model = get_gemini_client(api_key, model_name, system_instruction)
        
        prompt = f"""
Analyze this startup signal:
Source: {signal_data.get('source')}
Title: {signal_data.get('title')}
Original Post Content:
{signal_data.get('text')}

Context: The user scans for opportunities to offer these types of services: {custom_services or 'Web development, SEO, Speed Optimization, Custom AI integration, Mobile apps, UI/UX Redesign'}.
User's Tech Stack/Developer Skills: {developer_skills or 'Python, React, Webflow, SEO, Next.js'}.

Return a JSON object that fits the following exact schema:
{
  "startup_name": "Name of the startup (or Author/Username if not found)",
  "category": "One of: UI/UX, Performance, SEO, Development, AI, or Marketing",
  "detected_signal": "Summary of the raw signal detected (e.g., Hiring frontend dev, founder complaining about signups, launching new product)",
  "insight": "A detailed, thorough explanation explaining exactly what the problem or pain point is, the root causes of the issue, and why it presents a bottleneck for their operations/growth. Be very specific.",
  "opportunity": "The exact service or product that can be pitched to them based on this signal.",
  "pitch_idea": "A short, high-conversion email or DM pitch (120-180 words) to send to the founder. It should be highly personalized, show you understand their specific issue, avoid sounding like spam, and propose a clear next step.",
  "score": 8,
  "score_explanation": "Breakdown of why this score was given (e.g., High intent because hiring, fresh post, good service fit).",
  "matched_skills": ["List of skills from the Tech Stack/Developer Skills list that are relevant/needed here. Empty array if none."],
  "match_percentage": 85,
  "problem_explanation": "A detailed, clear, and structured explanation of the startup's problem/pain point, its causes, and operational impact.",
  "how_to_solve_strategy": "A step-by-step guide explaining exactly how the user can resolve the startup's problem using their developer skills. Reference specific libraries, tools, or workflows based on the user's skills."
}

Return ONLY valid JSON. Do not include markdown code block formatting like ```json ... ```. Just return the raw JSON string.
"""

        response = model.generate_content(
            contents=prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_text = "\n".join(lines).strip()
            
        result = json.loads(raw_text)
        return result

    except Exception as e:
        logger.error(f"Error calling Gemini API for signal: {str(e)}")
        raise e

async def analyze_audit_with_ai(audit_data: dict, api_key: str, custom_services: str = "", model_name: str = "gemini-2.5-flash-lite", custom_system_instructions: str = "", developer_skills: str = ""):
    """
    Uses Gemini API to interpret technical website audit results and map them to concrete opportunities.
    """
    if not api_key:
        raise ValueError("Gemini API key is not configured. Please add your key in Settings.")

    try:
        system_instruction = (
            "You are an expert sales engineer and digital agency strategist.\n"
            "Your goal is to parse website technical audits (SEO, performance, and responsiveness)\n"
            "and translate them into actionable business impacts and pitches.\n\n"
            "CRITICAL CONSTRAINTS:\n"
            "1. Highlight exactly 1 or 2 high-impact issues only.\n"
            "2. Translate technical flaws into business cost (e.g., latency reduces conversion rate).\n"
            "3. Offer a clear, actionable solution from the user's services.\n"
        )
        if custom_system_instructions:
            system_instruction += f"\n\nADDITIONAL USER OUTREACH AND AUDIT PARAMETERS:\n{custom_system_instructions}"
            
        model = get_gemini_client(api_key, model_name, system_instruction)
        
        prompt = f"""
Analyze these technical audit results for a startup website:
Domain: {audit_data.get('domain')}
URL: {audit_data.get('url')}
SEO Score: {audit_data.get('seo_score')}/100
Performance Score: {audit_data.get('performance_score')}/100
Mobile Responsiveness Score: {audit_data.get('mobile_score')}/100
Detected Tech Stack: {', '.join(audit_data.get('tech_stack', [])) or 'Not detected'}
Specific Issues Discovered:
{chr(10).join('- ' + issue for issue in audit_data.get('issues', []))}

Context: The user scans for opportunities to offer these types of services: {custom_services or 'Web development, SEO, Speed Optimization, Custom AI integration, Mobile apps, UI/UX Redesign'}.
User's Tech Stack/Developer Skills: {developer_skills or 'Python, React, Webflow, SEO, Next.js'}.

Return a JSON object that maps these technical issues to real business impacts and creates a sellable opportunity. Use the exact schema:
{{
  "startup_name": "Domain name or detected name",
  "category": "One of: UI/UX, Performance, SEO, Development, AI, or Marketing",
  "detected_signal": "Summary of primary site weakness (e.g., Critical page speed issues, missing mobile viewport, SEO gaps)",
  "insight": "A detailed explanation of why these technical audit issues occurred, their root causes, and a thorough translation of these technical flaws into specific business costs. Support with industry metrics and clear consequences (e.g., how a 2.5s load delay causes a 20% drop-off in user signups, how missing viewport tags prevents mobile conversion, and how missing tags hurt search engine crawlability). Make it highly educational and analytical.",
  "opportunity": "What service is recommended (e.g. Page speed optimization package, Landing page redesign, SEO setup, Responsive fixes)",
  "pitch_idea": "A short, professional, friendly outreach email to the startup team (120-180 words). Start by referencing their actual website, politely point out the 1 or 2 highest-impact issues, explain how fixing them will increase conversion/revenue, and propose a quick 10-minute audit review call.",
  "score": 7,
  "score_explanation": "Breakdown of rating based on quantity/severity of issues, domain age/authority indicator, and fit for services.",
  "matched_skills": ["List of skills from the Tech Stack/Developer Skills list that are relevant to these audit issues (e.g., SEO, Webflow, Next.js). Empty array if none."],
  "match_percentage": 85,
  "problem_explanation": "A detailed, clear, and structured explanation of the startup's problem/pain point, its causes, and operational impact.",
  "how_to_solve_strategy": "A step-by-step guide explaining exactly how the user can resolve the startup's problem using their developer skills. Reference specific libraries, tools, or workflows based on the user's skills."
}}

Return ONLY valid JSON. Do not include markdown code block formatting. Just return the raw JSON string.
"""

        response = model.generate_content(
            contents=prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_text = "\n".join(lines).strip()
            
        result = json.loads(raw_text)
        return result

    except Exception as e:
        logger.error(f"Error calling Gemini API for web audit: {str(e)}")
        raise e

async def refine_pitch_with_ai(lead_data: dict, tone: str, api_key: str, custom_services: str = "", model_name: str = "gemini-2.5-flash-lite", custom_system_instructions: str = "") -> str:
    """
    Uses Gemini API to rewrite the existing sales pitch into a specific tone (short, casual, formal).
    """
    if not api_key:
        raise ValueError("Gemini API key is not configured. Please add your key in Settings.")

    try:
        system_instruction = "You are an expert sales outreach copywriter who rewrites pitches to fit specific target styles."
        if custom_system_instructions:
            system_instruction += f"\n\nADDITIONAL USER OUTREACH AND AUDIT PARAMETERS:\n{custom_system_instructions}"
            
        model = get_gemini_client(api_key, model_name, system_instruction)
        
        # Mapping descriptions of tones for Gemini
        tone_instructions = {
            "short": "extremely brief, punchy, and direct (under 60-80 words). Cut any fluff.",
            "casual": "friendly, conversational, informal, and warm. Sounds like a coffee chat request or casual DM.",
            "formal": "highly professional, polite, consulting-focused, structured, and authoritative."
        }
        
        instruction = tone_instructions.get(tone.lower(), "friendly and professional")
        
        prompt = f"""
Here is the startup lead information:
Startup Name: {lead_data.get('startup_name')}
Detected Signal: {lead_data.get('detected_signal')}
Category: {lead_data.get('category')}
Your Services: {custom_services or 'Web development, SEO, Speed Optimization, Custom AI integration, Mobile apps, UI/UX Redesign'}

Here is the current sales pitch:
\"\"\"
{lead_data.get('pitch_idea')}
\"\"\"

Rewrite this sales pitch to be: {instruction}.
CRITICAL CONSTRAINTS:
1. Preserve the core problem mentioned in the signal and the specific solution offered.
2. Keep it engaging and avoid sounding like generic spam.
3. Do NOT include any placeholder text like [Your Name] or [Startup Name] in brackets if they were already filled in. If they are placeholders, keep them as is.
4. Return ONLY the rewritten text of the pitch. Do not wrap it in quotes, markdown, or any introductory text. Just output the clean rewritten message.
"""

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        logger.error(f"Error calling Gemini API for pitch refinement: {str(e)}")
        raise e


async def classify_signal_lead_relevance(title: str, text: str, api_key: str, custom_services: str = "", model_name: str = "gemini-2.5-flash-lite", developer_skills: str = "") -> bool:
    """
    Uses Gemini to classify if the signal represents a potential lead for our services.
    Returns True if relevant, False otherwise.
    """
    if not api_key:
        # If no API key, fall back to True (default to keyword matching success)
        return True
    try:
        model = get_gemini_client(api_key, model_name, "You are a lead qualification classifier.")
        services = custom_services or 'Web development, SEO, Speed Optimization, Custom AI integration, Mobile apps, UI/UX Redesign'
        skills = developer_skills or 'Python, React, Webflow, SEO, Next.js'
        
        prompt = f"""
        Evaluate if the following online post or news title represents an active problem, need, or opportunity related to these services or developer tech skills:
        Services: {services}
        Developer Tech Skills: {skills}

        Post Title: {title}
        Post content or snippet: {text}

        Instructions:
        Determine if this post indicates someone having a problem with their website speed/SEO/UI-UX, looking to hire developers/freelancers with tech stack listed in our core skills, or building a startup where technical services could help.
        If it is relevant, return exactly: YES
        If it is spam, unrelated conversation, generic news with no opportunity, or completely out of scope, return exactly: NO

        Output only YES or NO. Do not add any introductory or explaining text.
        """
        response = model.generate_content(prompt)
        ans = response.text.strip().upper()
        return "YES" in ans
    except Exception as e:
        logger.error(f"Error in classify_signal_lead_relevance: {str(e)}")
        return True # Default to true on error to not miss leads


async def generate_explanation_and_solution(lead_data: dict, api_key: str, developer_skills: str, model_name: str = "gemini-2.5-flash-lite") -> dict:
    """
    Generates detailed problem explanation and skill-based solution strategy on-demand.
    Tries Gemini model cascade with intelligent technical fallback.
    """
    system_instruction = (
        "You are a principal system architect and technical project advisor.\n"
        "Your task is to analyze a startup's opportunity/pain point and generate:\n"
        "1. A detailed explanation of the problem.\n"
        "2. A concrete, step-by-step technical solution guide showing how to solve the problem using the user's specific developer skills."
    )
    prompt = f"""
Analyze this lead:
Startup: {lead_data.get('startup_name')}
Detected Signal: {lead_data.get('detected_signal')}
Insight: {lead_data.get('insight')}
Opportunity: {lead_data.get('opportunity')}
Category: {lead_data.get('category')}
Technical Audit: {json.dumps(lead_data.get('tech_audit', {}))}

User's Developer Skills/Tech Stack: {developer_skills or 'Python, React, Webflow, SEO, Next.js'}

Return a JSON object with the following exact schema:
{{
  "problem_explanation": "A detailed, clear, and structured explanation of the startup's problem/pain point, its causes, and operational impact.",
  "how_to_solve_strategy": "A concrete step-by-step guide explaining exactly how the user can resolve the startup's problem using their developer skills. Reference specific libraries, tools, or workflows based on the user's skills."
}}

Return ONLY valid JSON. Do not include markdown code block formatting. Just return the raw JSON string.
"""
    models_to_try = [model_name] + [m for m in PREFERRED_MODELS if m != model_name]
    for m in models_to_try:
        try:
            model = get_gemini_client(api_key, m, system_instruction)
            response = model.generate_content(
                contents=prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                lines = raw_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_text = "\n".join(lines).strip()
            result = json.loads(raw_text)
            if result.get("problem_explanation") and result.get("how_to_solve_strategy"):
                return result
        except Exception as e:
            logger.warning(f"Model {m} cascade error in generate_explanation_and_solution: {e}")
            continue

    # Fallback to intelligent heuristic blueprint if API quota exhausted
    cat = (lead_data.get('category') or 'Development').title()
    name = lead_data.get('startup_name') or 'Startup'
    sig = lead_data.get('detected_signal') or 'Technical Bottleneck'
    ins = lead_data.get('insight') or sig
    skills = developer_skills or 'Python, React, TypeScript, FastAPI, Next.js, PostgreSQL, Docker'

    return {
        "problem_explanation": f"{name} is encountering architectural friction around: {sig}. {ins} In high-growth production environments, this issue degrades developer velocity, creates operational latency, and risks user churn if not mitigated at the infrastructure level.",
        "how_to_solve_strategy": f"Step-by-Step Developer Implementation Plan using [{skills}]:\n1. Architecture Audit & Root Cause Isolation: Instrument distributed tracing and profiling to measure latency and resource bottlenecks.\n2. Modular Decoupling: Refactor the critical path into isolated, asynchronously processed services using FastAPI/Python and Redis caching.\n3. Production Hardening: Implement automated CI regression testing, containerize via Docker, and deploy with zero-downtime health probes.\n4. Founder Deliverable: Provide a concise impact report demonstrating latency reduction and measurable stability gains."
    }
    """
    Generates detailed problem explanation and skill-based solution strategy on-demand.
    """
    if not api_key:
        raise ValueError("Gemini API key is not configured. Please add your key in Settings.")

    try:
        system_instruction = (
            "You are a principal system architect and technical project advisor.\n"
            "Your task is to analyze a startup's opportunity/pain point and generate:\n"
            "1. A detailed explanation of the problem.\n"
            "2. A concrete, step-by-step technical solution guide showing how to solve the problem using the user's specific developer skills."
        )
        model = get_gemini_client(api_key, model_name, system_instruction)
        
        prompt = f"""
Analyze this lead:
Startup: {lead_data.get('startup_name')}
Detected Signal: {lead_data.get('detected_signal')}
Insight: {lead_data.get('insight')}
Opportunity: {lead_data.get('opportunity')}
Category: {lead_data.get('category')}
Technical Audit: {json.dumps(lead_data.get('tech_audit', {}))}

User's Developer Skills/Tech Stack: {developer_skills or 'Python, React, Webflow, SEO, Next.js'}

Return a JSON object with the following exact schema:
{{
  "problem_explanation": "A detailed, clear, and structured explanation of the startup's problem/pain point, its causes, and operational impact.",
  "how_to_solve_strategy": "A concrete step-by-step guide explaining exactly how the user can resolve the startup's problem using their developer skills. Reference specific libraries, tools, or workflows based on the user's skills."
}}

Return ONLY valid JSON. Do not include markdown code block formatting. Just return the raw JSON string.
"""
        response = model.generate_content(
            contents=prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_text = "\n".join(lines).strip()
            
        result = json.loads(raw_text)
        return result
    except Exception as e:
        logger.error(f"Error generating guide in generate_explanation_and_solution: {str(e)}")
        raise e


