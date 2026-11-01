import os
import uuid
import json
import warnings
import logging
# pyrefly: ignore [missing-import]
import httpx

# Suppress noisy library and framework warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

# Silence verbose third-party HTTP request logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Optional
import uvicorn
import threading
import asyncio
from dotenv import load_dotenv

import scraper
import ai_agent

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI App
app = FastAPI(title="Startup Intelligence & Opportunity Agent API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LEADS_FILE = os.path.join(DATA_DIR, "leads.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

# Create data and public directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

# Helper Functions for File DB
_db_lock = threading.Lock()

def load_leads() -> List[dict]:
    with _db_lock:
        if not os.path.exists(LEADS_FILE):
            return []
        try:
            with open(LEADS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

def save_leads(leads: List[dict]):
    with _db_lock:
        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)

def load_settings() -> dict:
    default_settings = {
        "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
        "custom_services": "Web design, SEO Audit, Frontend performance, Custom AI solutions, Lead capture engines, Speed optimization",
        "developer_skills": "Python, React, Webflow, SEO, Next.js",
        "target_subreddits": ["saas", "startups", "SideProject"],
        "enabled_sources": ["reddit", "rss", "duckduckgo", "github", "indiehackers", "devto", "google_news", "hackernews"],
        "gemini_model": "gemini-2.0-flash",
        "scheduler_enabled": False,
        "scheduler_interval_hours": 6,
        "webhook_url": "",
        "webhook_type": "Discord",
        "custom_system_instructions": ""
    }
    if not os.path.exists(SETTINGS_FILE):
        return default_settings
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
            # Ensure keys exist
            for k, v in default_settings.items():
                if k not in saved:
                    saved[k] = v
            return saved
    except Exception:
        return default_settings

def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

# Helper function to get mock matching skills based on keywords
def get_mock_skills_matching(text: str, developer_skills: str) -> tuple[list[str], int]:
    if not developer_skills:
        return [], 0
    skills = [s.strip() for s in developer_skills.split(",") if s.strip()]
    matched = []
    text_lower = text.lower()
    for s in skills:
        if s.lower() in text_lower:
            matched.append(s)
    # If no explicit keyword matches, provide a fallback match for tech requests
    if not matched and any(w in text_lower for w in ["dev", "hiring", "react", "python", "code", "site", "web"]):
        if skills:
            matched.append(skills[0])
            return matched, 75
    return matched, 90 if matched else 50

# Mock generation for UX demo when API Key is missing
def get_mock_pitch_and_analysis(title: str, text: str, source: str) -> dict:
    text_lower = (title + " " + text).lower()
    settings = load_settings()
    dev_skills = settings.get("developer_skills", "Python, React, Webflow, SEO, Next.js")
    matched_skills, match_pct = get_mock_skills_matching(title + " " + text, dev_skills)
    
    if "hire" in text_lower or "hiring" in text_lower or "looking for" in text_lower:
        return {
            "startup_name": "Hiring Startup (" + source + ")",
            "category": "Development",
            "detected_signal": "Founder searching for talent in: " + title,
            "insight": (
                "The startup is currently scaling and faces critical resource constraints. "
                "Hiring a full-time in-house developer is slow (average 45-60 days to hire and onboard) "
                "and expensive (involving recruiting costs, equity, and benefits). "
                "The root cause of their bottleneck is that key product features are delayed, "
                "which stalls user acquisition and delays revenue milestones. "
                "They require immediate engineering capacity without the long-term overhead of a permanent hire."
            ),
            "opportunity": (
                "Fractional engineering support or a project-based development package. "
                "This addresses their immediate timeline constraints by onboarding an expert developer "
                "within 48 hours to ship high-priority roadmap features while they continue their permanent hire search."
            ),
            "pitch_idea": "Hi there,\n\nSaw your post looking to hire developers. Recruits can take 30-60 days to onboard. I specialize in bootstrapping development tasks immediately. I can help build your features starting this week while you search for the perfect long-term hire. Let's do a quick 10-minute call to check alignment?\n\nBest,\n[Your Name]",
            "score": 9,
            "score_explanation": "Very high intent signal (active hiring) with immediate budget.",
            "matched_skills": matched_skills,
            "match_percentage": match_pct,
            "problem_explanation": "The startup is unable to proceed with key software delivery because of a shortage of technical developers, resulting in delayed product releases and slower growth.",
            "how_to_solve_strategy": "Step 1: Offer contracting/freelancing services to pick up their backlog immediately.\nStep 2: Act as a core developer with your skills in " + dev_skills + " to implement their top priority features.\nStep 3: Setup clear documentation and code tests to ease hand-off when they hire full-time."
        }
    elif "slow" in text_lower or "page load" in text_lower or "speed" in text_lower or "performance" in text_lower:
        return {
            "startup_name": "Speed Optimization Prospect",
            "category": "Performance",
            "detected_signal": "Complaints or performance concern mentioned",
            "insight": (
                "The platform exhibits severe load latency under peak usage or on mobile networks. "
                "According to industry benchmarks, a 1-second delay in page load time decreases customer satisfaction "
                "by 16% and drops conversions by 7%. "
                "The root cause of performance bottleneck usually stems from unoptimized media assets, "
                "excessive third-party script bloat, and lack of browser caching. "
                "This friction frustrates users and directly harms their paid acquisition ROI."
            ),
            "opportunity": (
                "Core Web Vitals and Page Speed Optimization Package. "
                "We will compress static assets, defer non-critical Javascript, optimize database queries, "
                "and set up a globally distributed CDN to bring load times under the 1.5-second threshold."
            ),
            "pitch_idea": "Hey,\n\nI noticed you mentioned web speeds. Fast sites retain 40% more visitors. I checked your tech footprint and would love to perform a free speed audit to identify what's slowing your platform down. Would you be open to an audit report next Tuesday?\n\nCheers,\n[Your Name]",
            "score": 8,
            "score_explanation": "Technical pain point directly impacts their bottom-line metrics.",
            "matched_skills": matched_skills,
            "match_percentage": match_pct,
            "problem_explanation": "The landing page is slow, causing friction, bounce-offs, and lower ranking in search engines.",
            "how_to_solve_strategy": "Step 1: Conduct a speed audit to find slow files or heavy scripts.\nStep 2: Optimize the site using your skills in " + dev_skills + " (compress images, implement caching, defer JS).\nStep 3: Set up CDNs and verify mobile loading performance."
        }
    else:
        return {
            "startup_name": "Growth Stage Startup",
            "category": "UI/UX",
            "detected_signal": "General startup feedback or launch: " + title,
            "insight": (
                "New product launches require frictionless onboarding flows to convert early traffic into registered users. "
                "Currently, complex sign-up steps, poor form layouts, and lack of visual hierarchy cause "
                "up to 40% of newly acquired visitors to drop off before completing the registration. "
                "The bottleneck lies in the user experience design—users are overwhelmed by options and "
                "do not see the immediate value proposition above the fold."
            ),
            "opportunity": (
                "UX/UI Landing Page Audit & User Onboarding Redesign. "
                "We will perform a step-by-step conversion funnel audit, simplify the user registration steps, "
                "rework the header copy to be benefits-driven, and run A/B testing on the primary Call-To-Action (CTA)."
            ),
            "pitch_idea": "Hi,\n\nCongrats on the launch! I took a look at your onboarding flow and saw a couple of areas where new signups might get confused. I drafted a quick UX mockup that could simplify this step. Let me know if you want me to send it over?\n\nRegards,\n[Your Name]",
            "score": 7,
            "score_explanation": "Recently launched product looking for early user feedback and optimization.",
            "matched_skills": matched_skills,
            "match_percentage": match_pct,
            "problem_explanation": "Friction in signup/onboarding flow reduces early user adoption and wastes traffic acquisition budgets.",
            "how_to_solve_strategy": "Step 1: Simplify onboarding input forms and layout structure.\nStep 2: Utilize " + dev_skills + " to code a seamless, fast multi-step registration flow.\nStep 3: Run quick A/B test variations to identify top-performing CTA configurations."
        }

def get_mock_audit_analysis(audit: dict) -> dict:
    domain = audit.get("domain", "Your Startup")
    issues = audit.get("issues", [])
    
    primary_issue = issues[0] if issues else "General optimization gaps"
    seo = audit.get("seo_score", 100)
    perf = audit.get("performance_score", 100)
    mobile = audit.get("mobile_score", 100)
    
    score = int((seo + perf + mobile) / 30)
    # Lower technical scores = higher sales opportunity
    opportunity_score = 10 - score
    opportunity_score = max(3, min(opportunity_score, 10))
    
    # Formulate detailed insight based on actual scores
    detailed_insight = (
        f"The technical website audit of {domain} revealed significant performance and structural vulnerabilities. "
        f"The primary flagged bottleneck is: '{primary_issue}'. "
    )
    if perf < 70:
        detailed_insight += (
            f"The landing page took {audit.get('load_time_ms', 'over 1200')}ms to respond, resulting in a low Performance score ({perf}/100). "
            "This delay acts as a direct barrier to user retention, as slow speeds increase bounce rates by up to 90%. "
        )
    if seo < 80:
        detailed_insight += (
            f"Additionally, missing meta tags and structural SEO flaws resulting in an SEO score of {seo}/100 "
            "negatively affect indexation, causing search engines to rank this platform below competitors. "
        )
    if mobile < 80:
        detailed_insight += (
            f"A low mobile score of {mobile}/100 indicates that elements are overlapping or too small, "
            "which prevents mobile conversions and penalizes the site on Google's mobile-first indexing."
        )
        
    detailed_opportunity = (
        f"A targeted remediation package addressing the {len(issues)} flagged issues. "
        "We will run speed optimizations (defer JS, optimize assets) and fix meta structures to recover lost traffic."
    )
    
    settings = load_settings()
    dev_skills = settings.get("developer_skills", "Python, React, Webflow, SEO, Next.js")
    matched_skills = []
    skills = [s.strip() for s in dev_skills.split(",") if s.strip()]
    for s in skills:
        s_lower = s.lower()
        if "seo" in s_lower and seo < 90:
            matched_skills.append(s)
        elif ("perf" in s_lower or "speed" in s_lower or "next" in s_lower) and perf < 90:
            matched_skills.append(s)
        elif ("ui" in s_lower or "ux" in s_lower or "design" in s_lower or "webflow" in s_lower) and mobile < 90:
            matched_skills.append(s)
            
    if not matched_skills and skills:
        matched_skills.append(skills[0])
    match_pct = 85 if matched_skills else 50
    
    return {
        "startup_name": domain.replace("www.", "").capitalize(),
        "category": "SEO" if seo < 80 else "Performance" if perf < 80 else "UI/UX",
        "detected_signal": f"Technical audit detected low scores: SEO ({seo}), Perf ({perf}), Mobile ({mobile})",
        "insight": detailed_insight,
        "opportunity": detailed_opportunity,
        "pitch_idea": f"Hi Team,\n\nI ran a quick audit on {domain} and noticed that page speeds scored {perf}/100, primarily due to large assets. A speed fix would help increase retention by up to 15%. I've mapped out a simple plan to fix this in 3 days. Let's connect for 10 minutes to discuss?\n\nBest,\n[Your Name]",
        "score": opportunity_score,
        "score_explanation": f"Lead rating set to {opportunity_score}/10 based on site issues and service match.",
        "matched_skills": matched_skills,
        "match_percentage": match_pct,
        "problem_explanation": f"The technical audit for {domain} indicates serious vulnerabilities. SEO score ({seo}/100), Performance score ({perf}/100), and Mobile score ({mobile}/100) are below benchmarks, caused by '{primary_issue}'. This harms user conversion and search engine ranking.",
        "how_to_solve_strategy": "Step 1: Minify JS and CSS files and optimize static assets.\nStep 2: Correct mobile responsiveness bugs (viewport scale, tap target spacing).\nStep 3: Setup meta tags, structured data, and audit robot.txt to optimize SEO visibility."
    }

# --- ENDPOINTS ---

@app.get("/health")
def health_check():
    leads = load_leads()
    return {
        "status": "healthy",
        "service": "startup-intelligence",
        "version": "1.0.0",
        "storage": "json",
        "records_count": len(leads),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/leads/{lead_id}")
def get_lead_by_id(lead_id: str):
    leads = load_leads()
    for l in leads:
        if l.get("id") == lead_id:
            return l
    raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")

@app.get("/api/leads")
def get_leads(
    category: Optional[str] = None,
    min_score: Optional[int] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
):
    leads = load_leads()
    if category and category != "All":
        leads = [l for l in leads if l.get("category") == category]
    if min_score is not None:
        leads = [l for l in leads if l.get("score", 0) >= min_score]
        
    # Sort leads: higher scores first, then recent first
    leads.sort(key=lambda x: (x.get("score", 0), x.get("created_at", "")), reverse=True)
    if offset:
        leads = leads[offset:]
    if limit is not None and limit > 0:
        leads = leads[:limit]
    return leads

@app.post("/api/leads/status")
def update_lead_status(payload: dict = Body(...)):
    lead_id = payload.get("id")
    status = payload.get("status")
    if not lead_id or not status:
        raise HTTPException(status_code=400, detail="Missing id or status")
        
    leads = load_leads()
    found = False
    for lead in leads:
        if lead.get("id") == lead_id:
            lead["status"] = status
            found = True
            break
            
    if not found:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    save_leads(leads)
    return {"success": True, "message": f"Lead status updated to {status}"}

@app.post("/api/leads/delete")
def delete_lead(payload: dict = Body(...)):
    lead_id = payload.get("id")
    if not lead_id:
        raise HTTPException(status_code=400, detail="Missing id")
        
    leads = load_leads()
    updated_leads = [l for l in leads if l.get("id") != lead_id]
    
    if len(updated_leads) == len(leads):
        raise HTTPException(status_code=404, detail="Lead not found")
        
    save_leads(updated_leads)
    return {"success": True, "message": "Lead deleted successfully"}

@app.post("/api/leads/edit")
def edit_lead(payload: dict = Body(...)):
    lead_id = payload.get("id")
    if not lead_id:
        raise HTTPException(status_code=400, detail="Missing id")
        
    leads = load_leads()
    lead = None
    for l in leads:
        if l.get("id") == lead_id:
            lead = l
            break
            
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    if "startup_name" in payload and payload["startup_name"]:
        lead["startup_name"] = payload["startup_name"]
        
    if "category" in payload:
        lead["category"] = payload["category"]
        
    if "score" in payload:
        try:
            lead["score"] = int(payload["score"])
        except (ValueError, TypeError):
            pass
            
    if "pitch_idea" in payload:
        lead["pitch_idea"] = payload["pitch_idea"]
        
    if "contact_info" in payload:
        if not lead.get("contact_info"):
            lead["contact_info"] = {}
        lead["contact_info"].update(payload["contact_info"])
        
    if "tech_audit" in payload:
        lead["tech_audit"] = payload["tech_audit"]
        
    if "url" in payload:
        url = payload["url"]
        if lead.get("url") != url:
            lead["url"] = url
            lead["analyzed"] = False
            # Keep author but clear other contact info since we have a new domain
            author = lead.get("contact_info", {}).get("author", "Unknown")
            lead["contact_info"] = {
                "email": "",
                "twitter": "",
                "linkedin": "",
                "contact_page": "",
                "author": author
            }
        
    save_leads(leads)
    return {"success": True, "lead": lead}

@app.get("/api/settings")
def get_settings_endpoint():
    return load_settings()

@app.post("/api/settings")
def update_settings_endpoint(settings: dict = Body(...)):
    existing = load_settings()
    existing.update(settings)
    save_settings(existing)
    return {"success": True, "message": "Settings updated successfully"}

@app.post("/api/settings/test-webhook")
async def test_webhook_endpoint(payload: dict = Body(...)):
    webhook_url = payload.get("webhook_url")
    webhook_type = payload.get("webhook_type", "Discord")
    
    if not webhook_url:
        raise HTTPException(status_code=400, detail="Missing webhook URL")
        
    mock_lead = {
        "startup_name": "Test Startup",
        "category": "Performance",
        "detected_signal": "System integration test signal",
        "url": "https://example.com",
        "pitch_idea": "This is a mock pitch generated to test your webhook integration. Everything works perfectly!",
        "score": 9,
        "source": "Webhook Tester",
        "status": "New"
    }
    
    try:
        await send_webhook_alert(mock_lead, webhook_url, webhook_type)
        return {"success": True, "message": "Test webhook alert sent successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send webhook: {str(e)}")

@app.post("/api/scrape/feeds")
async def run_feed_scraper():
    settings = load_settings()
    subreddits = settings.get("target_subreddits", ["saas", "startups", "SideProject"])
    enabled_sources = settings.get("enabled_sources", ["reddit", "rss", "duckduckgo", "github", "indiehackers", "devto", "google_news", "hackernews"])
    developer_skills = settings.get("developer_skills", "Python, React, Webflow, SEO, Next.js")
    skills = [s.strip() for s in developer_skills.split(",") if s.strip()]
    
    # 1. Fetch raw signals from enabled sources in parallel
    tasks = []
    if "reddit" in enabled_sources:
        tasks.append(scraper.fetch_reddit_signals(subreddits))
    if "rss" in enabled_sources:
        tasks.append(scraper.fetch_rss_signals())
    if "duckduckgo" in enabled_sources:
        tasks.append(scraper.fetch_duckduckgo_signals(skills))
    if "github" in enabled_sources:
        tasks.append(scraper.fetch_github_signals())
    if "indiehackers" in enabled_sources:
        tasks.append(scraper.fetch_indiehackers_signals(skills))
    if "devto" in enabled_sources:
        tasks.append(scraper.fetch_devto_signals())
    if "google_news" in enabled_sources:
        tasks.append(scraper.fetch_google_news_signals())
    if "hackernews" in enabled_sources:
        tasks.append(scraper.fetch_hackernews_signals())
        
    all_signals = []
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, list):
                all_signals.extend(res)
            elif isinstance(res, Exception):
                print(f"Scraper task encountered an exception: {str(res)}")
    
    # Load existing leads to avoid duplicates
    existing_leads = load_leads()
    existing_urls = {l.get("url") for l in existing_leads if l.get("url")}
    
    new_leads_added = 0
    skipped_duplicates = 0
    logs = []
    
    logs.append(f"Discovered {len(all_signals)} total raw signals in target feeds.")
    
    # Filter out duplicates first
    unique_signals = []
    for sig in all_signals:
        url = sig.get("url")
        if url in existing_urls:
            skipped_duplicates += 1
            continue
        unique_signals.append(sig)

    # Run AI Semantic Classification in parallel if API key is set
    api_key = settings.get("gemini_api_key", "")
    custom_services = settings.get("custom_services", "")
    model_name = settings.get("gemini_model", "gemini-2.0-flash")
    
    filtered_signals = []
    if api_key and api_key.strip() and unique_signals:
        logs.append("Running AI Semantic Classifier on new signals...")
        try:
            classification_tasks = [
                ai_agent.classify_signal_lead_relevance(
                    sig["title"], sig.get("text", ""), api_key, custom_services, model_name, developer_skills=developer_skills
                ) for sig in unique_signals
            ]
            classification_results = await asyncio.gather(*classification_tasks, return_exceptions=True)
            
            for sig, is_relevant in zip(unique_signals, classification_results):
                if isinstance(is_relevant, Exception) or is_relevant:
                    filtered_signals.append(sig)
                else:
                    logs.append(f"AI filter skipped irrelevant signal: '{sig['title'][:40]}...'")
        except Exception as e:
            logs.append(f"AI Classifier encountered an error: {str(e)}. Proceeding with all unique signals.")
            filtered_signals = unique_signals
    else:
        filtered_signals = unique_signals

    for signal in filtered_signals:
        url = signal.get("url")
        logs.append(f"Adding signal: '{signal['title'][:40]}...' from {signal['source']}")
        
        # Fast local categorization based on title/text keywords
        text_lower = (signal["title"] + " " + signal.get("text", "")).lower()
        category = "UI/UX"
        score = 6
        
        if "hire" in text_lower or "hiring" in text_lower or "looking for" in text_lower or "freelancer" in text_lower or "developer" in text_lower:
            category = "Development"
            score = 8
        elif "slow" in text_lower or "page load" in text_lower or "performance" in text_lower or "speed" in text_lower or "latency" in text_lower:
            category = "Performance"
            score = 7
        elif "seo" in text_lower or "google rank" in text_lower or "meta" in text_lower or "organic" in text_lower:
            category = "SEO"
            score = 7
        elif "ai" in text_lower or "gpt" in text_lower or "llm" in text_lower or "chatbot" in text_lower or "agent" in text_lower:
            category = "AI"
            score = 8
        elif "marketing" in text_lower or "growth" in text_lower or "acquisition" in text_lower or "traffic" in text_lower:
            category = "Marketing"
            score = 6
            
        # Clean startup name extraction from author or titles
        startup_name = "Unknown Startup"
        if "reddit" in signal["source"].lower():
            startup_name = f"u/{signal.get('author', 'reddit_user')}"
        elif "hacker news" in signal["source"].lower():
            cleaned = signal["title"].replace("Show HN:", "").replace("Ask HN:", "").strip()
            cleaned = cleaned.split(" - ")[0].split(" | ")[0].split(":")[0].strip()
            startup_name = cleaned[:30]
        else:
            # Clean PH / HN / BetaList title to get name
            cleaned = signal["title"].split(" - ")[0].split(" | ")[0].split(":")[0].strip()
            startup_name = cleaned[:30]
            
        local_matched, local_pct = get_mock_skills_matching(signal["title"] + " " + signal.get("text", ""), developer_skills)
        lead = {
            "id": str(uuid.uuid4()),
            "startup_name": startup_name,
            "category": category,
            "detected_signal": signal["title"],
            "insight": "AI research pending. Select this lead and click 'Research & Generate Pitch' to trigger analysis.",
            "opportunity": "Opportunity mapping pending.",
            "pitch_idea": "",
            "score": score,
            "score_explanation": "Preliminary rating based on feed signal keywords.",
            "source": signal["source"],
            "url": url,
            "contact_info": {
                "author": signal.get("author", "System Feed"),
                "email": "",
                "twitter": "",
                "linkedin": ""
            },
            "status": "New",
            "created_at": datetime.now().isoformat(),
            "analyzed": False,
            "raw_text": signal.get("text", ""),
            "matched_skills": local_matched,
            "match_percentage": local_pct
        }
        existing_leads.append(lead)
        existing_urls.add(url)
        new_leads_added += 1
            
    if new_leads_added > 0:
        save_leads(existing_leads)
        
    logs.append(f"Scraping completed. Added {new_leads_added} new leads, skipped {skipped_duplicates} duplicates.")
    
    return {
        "success": True,
        "new_leads_count": new_leads_added,
        "skipped_count": skipped_duplicates,
        "logs": logs
    }

@app.post("/api/leads/analyze")
async def analyze_lead_endpoint(payload: dict = Body(...)):
    lead_id = payload.get("id")
    if not lead_id:
        raise HTTPException(status_code=400, detail="Missing lead id")
        
    leads = load_leads()
    lead = None
    for l in leads:
        if l.get("id") == lead_id:
            lead = l
            break
            
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    settings = load_settings()
    api_key = settings.get("gemini_api_key", "")
    custom_services = settings.get("custom_services", "")
    developer_skills = settings.get("developer_skills", "")
    
    # 1. Resolve actual website URL using DuckDuckGo search if needed
    url = lead.get("url", "")
    website_url = ""
    
    # If the URL points to a listing aggregator (Reddit, PH, HN), search for the real website domain!
    is_aggregator = any(domain in url.lower() for domain in ["reddit.com", "ycombinator.com", "producthunt.com", "betalist.com"])
    
    if is_aggregator or not url:
        # First try to extract a URL directly from the post text to avoid web search lookup
        raw_text_to_scan = lead.get("raw_text", "") or lead.get("detected_signal", "")
        extracted_url = scraper.extract_url_from_text(raw_text_to_scan)
        if extracted_url:
            website_url = extracted_url
            lead["url"] = extracted_url
            print(f"Extracted URL directly from post text: {extracted_url}")
        else:
            # Lookup using startup name
            search_name = lead["startup_name"]
            if search_name.startswith("u/"):
                # If it's a reddit user, search for the text mentioned in the post instead
                search_name = lead["detected_signal"]
            
            discovered_url = await scraper.lookup_startup_website(search_name)
            if discovered_url:
                website_url = discovered_url
                lead["url"] = discovered_url # Update to real website!
    else:
        website_url = url
        
    # 2. Run website audit on official startup site
    audit_data = None
    if website_url:
        try:
            print(f"Auditing website: {website_url}...")
            audit_data = await scraper.audit_website(website_url, api_key)
            # Merge contact info if crawled
            if audit_data.get("success"):
                audit_contacts = audit_data.get("contact_info", {}) or {}
                if not lead.get("contact_info"):
                    lead["contact_info"] = {"author": "Unknown", "email": "", "twitter": "", "linkedin": "", "contact_page": ""}
                lead["contact_info"]["email"] = audit_contacts.get("email", "") or lead["contact_info"].get("email", "")
                lead["contact_info"]["twitter"] = audit_contacts.get("twitter", "") or lead["contact_info"].get("twitter", "")
                lead["contact_info"]["linkedin"] = audit_contacts.get("linkedin", "") or lead["contact_info"].get("linkedin", "")
                lead["contact_info"]["contact_page"] = audit_contacts.get("contact_page", "") or lead["contact_info"].get("contact_page", "")
                
            # Run contact enrichment if any key details are still empty
            if not lead["contact_info"].get("email") or not lead["contact_info"].get("twitter") or not lead["contact_info"].get("linkedin") or not lead["contact_info"].get("contact_page"):
                try:
                    print("Enriching contact info using search engines...")
                    enrich_data = await scraper.enrich_contact_info(lead["startup_name"], website_url)
                    for key in ["email", "twitter", "linkedin", "contact_page"]:
                        if not lead["contact_info"].get(key) and enrich_data.get(key):
                            lead["contact_info"][key] = enrich_data[key]
                except Exception as ex:
                    print(f"Contact enrichment failed: {str(ex)}")
        except Exception as e:
            print(f"Website audit failed: {str(e)}")
            
    # 3. Call Gemini AI to map opportunity
    try:
        if api_key and api_key.strip():
            model_name = settings.get("gemini_model", "gemini-2.0-flash")
            custom_system_instructions = settings.get("custom_system_instructions", "")
            if audit_data and audit_data.get("success"):
                # Call website audit analyzer
                ai_report = await ai_agent.analyze_audit_with_ai(audit_data, api_key, custom_services, model_name, custom_system_instructions, developer_skills=developer_skills)
            else:
                # Call text signal analyzer
                signal_data = {
                    "source": lead["source"],
                    "title": lead["detected_signal"],
                    "text": lead.get("raw_text", lead["detected_signal"]),
                    "author": lead["contact_info"].get("author", "Unknown")
                }
                ai_report = await ai_agent.analyze_signal_with_ai(signal_data, api_key, custom_services, model_name, custom_system_instructions, developer_skills=developer_skills)
        else:
            # Local Mock fallbacks if no API key
            if audit_data and audit_data.get("success"):
                ai_report = get_mock_audit_analysis(audit_data)
            else:
                ai_report = get_mock_pitch_and_analysis(lead["detected_signal"], lead.get("raw_text", ""), lead["source"])
                
        # 4. Save and return updated lead
        lead["startup_name"] = ai_report.get("startup_name", lead["startup_name"])
        lead["category"] = ai_report.get("category", lead["category"])
        lead["insight"] = ai_report.get("insight", lead["insight"])
        lead["opportunity"] = ai_report.get("opportunity", lead["opportunity"])
        lead["pitch_idea"] = ai_report.get("pitch_idea", lead["pitch_idea"])
        try:
            lead["score"] = int(ai_report.get("score", lead["score"]))
        except (ValueError, TypeError):
            pass
        lead["score_explanation"] = ai_report.get("score_explanation", lead["score_explanation"])
        lead["matched_skills"] = ai_report.get("matched_skills", [])
        try:
            lead["match_percentage"] = int(ai_report.get("match_percentage", 0))
        except (ValueError, TypeError):
            lead["match_percentage"] = 0
        lead["problem_explanation"] = ai_report.get("problem_explanation", "")
        lead["how_to_solve_strategy"] = ai_report.get("how_to_solve_strategy", "")
        lead["analyzed"] = True
        
        # Save tech audit metrics if available
        if audit_data and audit_data.get("success"):
            lead["tech_audit"] = {
                "seo_score": audit_data.get("seo_score", 100),
                "performance_score": audit_data.get("performance_score", 100),
                "mobile_score": audit_data.get("mobile_score", 100),
                "tech_stack": audit_data.get("tech_stack", []),
                "issues": audit_data.get("issues", [])
            }
        
        save_leads(leads)
        return {
            "success": True,
            "lead": lead
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Research mapping failed: {str(e)}")


def get_mock_explanation_and_solution(lead_name: str, category: str, skills: str) -> dict:
    skills_list = [s.strip() for s in skills.split(",") if s.strip()]
    matched_skills = skills_list[:2] if skills_list else ["React", "Python"]
    skills_str = " and ".join(matched_skills)
    
    return {
        "problem_explanation": f"The startup '{lead_name}' is experiencing bottlenecks in their {category} workflow. This is typically caused by poorly optimized code structures, lack of responsiveness, or lack of proper automation pipelines. This bottleneck impacts user engagement and search engine visibility negatively.",
        "how_to_solve_strategy": f"Step 1: Conduct a code audit on the core workflows.\nStep 2: Utilize your expertise in {skills_str} to optimize performance hotspots and resolve UI glitches.\nStep 3: Setup continuous monitoring and validation scripts to prevent regression."
    }


@app.post("/api/leads/explain-solve")
async def explain_solve_endpoint(payload: dict = Body(...)):
    lead_id = payload.get("id")
    if not lead_id:
        raise HTTPException(status_code=400, detail="Missing lead id")
        
    leads = load_leads()
    lead = None
    for l in leads:
        if l.get("id") == lead_id:
            lead = l
            break
            
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    settings = load_settings()
    api_key = settings.get("gemini_api_key", "")
    developer_skills = settings.get("developer_skills", "")
    
    try:
        if api_key and api_key.strip():
            model_name = settings.get("gemini_model", "gemini-2.0-flash")
            res = await ai_agent.generate_explanation_and_solution(lead, api_key, developer_skills, model_name)
        else:
            res = get_mock_explanation_and_solution(lead["startup_name"], lead["category"], developer_skills)
            
        lead["problem_explanation"] = res.get("problem_explanation", "")
        lead["how_to_solve_strategy"] = res.get("how_to_solve_strategy", "")
        save_leads(leads)
        
        return {
            "success": True,
            "lead": lead
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation & solution: {str(e)}")


@app.post("/api/leads/pitch/send-email")
async def send_pitch_email_endpoint(payload: dict = Body(...)):
    lead_id = payload.get("id")
    if not lead_id:
        raise HTTPException(status_code=400, detail="Missing lead id")
        
    leads = load_leads()
    lead = None
    for l in leads:
        if l.get("id") == lead_id:
            lead = l
            break
            
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    resend_key = os.getenv("RESEND_API_KEY", "")
    if not resend_key:
        raise HTTPException(status_code=400, detail="Resend API key is not configured in .env file. Please add it first.")
        
    email_to = lead.get("contact_info", {}).get("email")
    if not email_to:
        raise HTTPException(status_code=400, detail="Recipient email is missing for this lead. Please enrich contact details first.")
        
    pitch_text = lead.get("pitch_idea", "")
    if not pitch_text:
        raise HTTPException(status_code=400, detail="Outreach pitch content is empty. Please generate a pitch first.")
        
    subject = f"Quick question about {lead.get('startup_name')}"
    sender = os.getenv("RESEND_SENDER_EMAIL", "onboarding@resend.dev")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {resend_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": sender,
                    "to": email_to,
                    "subject": subject,
                    "text": pitch_text
                }
            )
            
            if resp.status_code in [200, 201, 202]:
                data = resp.json()
                return {
                    "success": True,
                    "message": f"Pitch email successfully sent to {email_to} via Resend API!"
                }
            else:
                err_msg = resp.text
                try:
                    err_data = resp.json()
                    err_msg = err_data.get("message", err_msg)
                except Exception:
                    pass
                raise Exception(err_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email via Resend: {str(e)}")


@app.post("/api/leads/pitch/refine")
async def refine_lead_pitch_endpoint(payload: dict = Body(...)):
    lead_id = payload.get("id")
    tone = payload.get("tone")
    if not lead_id or not tone:
        raise HTTPException(status_code=400, detail="Missing lead id or tone")
        
    leads = load_leads()
    lead = None
    for l in leads:
        if l.get("id") == lead_id:
            lead = l
            break
            
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    settings = load_settings()
    api_key = settings.get("gemini_api_key", "")
    custom_services = settings.get("custom_services", "")
    
    # If no api key is found, fall back to mock pitches for demo purposes
    if not api_key or not api_key.strip():
        startup_name = lead.get("startup_name", "Startup")
        category = lead.get("category", "Development")
        problem = lead.get("detected_signal", "Website issues")
        
        mock_pitches = {
            "short": f"Hey,\n\nI saw you are looking into {category} issues on {startup_name}. I specialize in this and have helped companies boost speeds and UI conversions in 3 days. Would you be open to a quick 10-minute chat this week?\n\nBest,\n[Your Name]",
            "casual": f"Hi there! 👋\n\nCongrats on the launch/updates for {startup_name}. I was checking it out and noticed a couple of minor things under the hood related to {category} that could be optimized to improve user signup flow. I build custom solutions for startups. Let me know if you'd like a quick free speed/SEO audit report?\n\nCheers,\n[Your Name]",
            "formal": f"Dear Team,\n\nI hope this message finds you well. I recently analyzed your platform, {startup_name}, and identified key optimization opportunities within your {category} stack, specifically relating to {problem}.\n\nOur agency provides high-performance consulting services. I would be pleased to schedule a brief introductory call next Tuesday to present our recommendations.\n\nRespectfully yours,\n[Your Name]"
        }
        refined_pitch = mock_pitches.get(tone.lower(), lead.get("pitch_idea", ""))
    else:
        try:
            model_name = settings.get("gemini_model", "gemini-2.0-flash")
            custom_system_instructions = settings.get("custom_system_instructions", "")
            refined_pitch = await ai_agent.refine_pitch_with_ai(lead, tone, api_key, custom_services, model_name, custom_system_instructions)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI Pitch refinement failed: {str(e)}")
            
    # Update lead details
    lead["pitch_idea"] = refined_pitch
    save_leads(leads)
    
    return {
        "success": True,
        "pitch_idea": refined_pitch
    }

@app.post("/api/scrape/audit")
async def run_website_audit(payload: dict = Body(...)):
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Missing website URL")
        
    settings = load_settings()
    api_key = settings.get("gemini_api_key", "")
    custom_services = settings.get("custom_services", "")
    model_name = settings.get("gemini_model", "gemini-2.0-flash")
    custom_system_instructions = settings.get("custom_system_instructions", "")
    developer_skills = settings.get("developer_skills", "")
    
    # 1. Fetch and audit HTML
    audit_data = await scraper.audit_website(url, api_key)
    
    # 2. Process with AI
    try:
        if api_key and api_key.strip():
            ai_report = await ai_agent.analyze_audit_with_ai(audit_data, api_key, custom_services, model_name, custom_system_instructions, developer_skills=developer_skills)
        else:
            ai_report = get_mock_audit_analysis(audit_data)
            
        # Combine scraped contact info with AI report
        raw_contact = audit_data.get("contact_info", {}) if audit_data.get("success") else {}
        contact_info = {
            "email": raw_contact.get("email", ""),
            "twitter": raw_contact.get("twitter", ""),
            "linkedin": raw_contact.get("linkedin", ""),
            "contact_page": raw_contact.get("contact_page", "")
        }
        
        try:
            match_pct = int(ai_report.get("match_percentage", 0))
        except (ValueError, TypeError):
            match_pct = 0
            
        lead = {
            "id": str(uuid.uuid4()),
            "startup_name": ai_report.get("startup_name", audit_data["domain"]),
            "category": ai_report.get("category", "Performance"),
            "detected_signal": ai_report.get("detected_signal", "Website Technical Weakness Audit"),
            "insight": ai_report.get("insight", "Site audits reveal code issues."),
            "opportunity": ai_report.get("opportunity", "Tech optimizations"),
            "pitch_idea": ai_report.get("pitch_idea", ""),
            "score": ai_report.get("score", 6),
            "score_explanation": ai_report.get("score_explanation", "Derived from site audits."),
            "source": "Website Audit",
            "url": audit_data["url"],
            "contact_info": contact_info,
            "status": "New",
            "created_at": datetime.now().isoformat(),
            "analyzed": True,
            "matched_skills": ai_report.get("matched_skills", []),
            "match_percentage": match_pct,
            "tech_audit": {
                "seo_score": audit_data.get("seo_score", 100),
                "performance_score": audit_data.get("performance_score", 100),
                "mobile_score": audit_data.get("mobile_score", 100),
                "tech_stack": audit_data.get("tech_stack", []),
                "issues": audit_data.get("issues", [])
            }
        }
        
        # Save lead to database
        leads = load_leads()
        leads = [l for l in leads if l.get("url") != lead["url"]]
        leads.append(lead)
        save_leads(leads)
        
        return {
            "success": True,
            "lead": lead,
            "audit_raw": audit_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Audit generation failed: {str(e)}")

async def send_webhook_alert(lead: dict, webhook_url: str, webhook_type: str):
    """
    Sends a webhook notification to Discord, Slack, or a Custom JSON endpoint.
    """
    if not webhook_url:
        return
        
    try:
        # Standard HTTP client
        async with httpx.AsyncClient(timeout=10.0) as client:
            score = lead.get("score", 0)
            category = lead.get("category", "General")
            title = lead.get("detected_signal", "New Lead")
            url = lead.get("url", "")
            pitch = lead.get("pitch_idea", "No pitch generated.")
            source = lead.get("source", "Scraper")
            startup = lead.get("startup_name", "Startup")
            
            if webhook_type.lower() == "discord":
                payload = {
                    "embeds": [
                        {
                            "title": f"🔥 New Hot Lead Discovered: {startup} ({score}/10)",
                            "description": f"**Signal:** {title}\n\n**Category:** {category}\n**Source:** {source}\n**URL:** {url or 'None'}",
                            "color": 3447003, # Discord Blue
                            "fields": [
                                {
                                    "name": "AI Generated Pitch Draft",
                                    "value": pitch[:1000] + ("..." if len(pitch) > 1000 else "")
                                }
                            ],
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }
                    ]
                }
            elif webhook_type.lower() == "slack":
                payload = {
                    "text": f"🔥 *New Hot Lead Discovered: {startup} ({score}/10)*",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"🔥 *New Hot Lead Discovered: {startup} ({score}/10)*\n*Signal:* {title}\n*Category:* {category}\n*Source:* {source}\n*URL:* {url}"
                            }
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*AI Pitch Draft:*\n```{pitch}```"
                            }
                        }
                    ]
                }
            else:
                payload = {
                    "event": "new_lead",
                    "lead": lead
                }
                
            res = await client.post(webhook_url, json=payload)
            print(f"Webhook alert sent to {webhook_type}. Response code: {res.status_code}")
    except Exception as e:
        print(f"Failed to send webhook alert: {str(e)}")


# pyrefly: ignore [missing-import]
import httpx
async def run_periodic_scraper():
    """
    Runs in the background, periodically scans active sources, maps new leads,
    and dispatches webhook notifications for leads scoring >= 8.
    """
    print("Background periodic scraper task started.")
    await asyncio.sleep(10) # wait 10s on boot
    
    while True:
        try:
            settings = load_settings()
            enabled = settings.get("scheduler_enabled", False)
            interval_hours = settings.get("scheduler_interval_hours", 6)
            
            if enabled:
                print("Background Scheduler: Starting automatic signal scan...")
                subreddits = settings.get("target_subreddits", ["saas", "startups", "SideProject"])
                enabled_sources = settings.get("enabled_sources", ["reddit", "rss", "duckduckgo", "github", "indiehackers", "devto", "google_news", "hackernews"])
                developer_skills = settings.get("developer_skills", "Python, React, Webflow, SEO, Next.js")
                skills = [s.strip() for s in developer_skills.split(",") if s.strip()]
                
                raw_signals = []
                tasks = []
                
                if "reddit" in enabled_sources:
                    tasks.append(scraper.fetch_reddit_signals(subreddits))
                if "rss" in enabled_sources:
                    tasks.append(scraper.fetch_rss_signals())
                if "duckduckgo" in enabled_sources:
                    tasks.append(scraper.fetch_duckduckgo_signals(skills))
                if "github" in enabled_sources:
                    tasks.append(scraper.fetch_github_signals())
                if "indiehackers" in enabled_sources:
                    tasks.append(scraper.fetch_indiehackers_signals(skills))
                if "devto" in enabled_sources:
                    tasks.append(scraper.fetch_devto_signals())
                if "google_news" in enabled_sources:
                    tasks.append(scraper.fetch_google_news_signals())
                if "hackernews" in enabled_sources:
                    tasks.append(scraper.fetch_hackernews_signals())
                    
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for res in results:
                    if isinstance(res, list):
                        raw_signals.extend(res)
                        
                leads = load_leads()
                existing_sigs = {l["detected_signal"] for l in leads}
                new_leads_added = 0
                
                api_key = settings.get("gemini_api_key", "")
                custom_services = settings.get("custom_services", "")
                model_name = settings.get("gemini_model", "gemini-2.0-flash")
                custom_system_instructions = settings.get("custom_system_instructions", "")
                webhook_url = settings.get("webhook_url", "")
                webhook_type = settings.get("webhook_type", "Discord")
                
                # Filter duplicates
                unique_signals = []
                for sig in raw_signals:
                    if sig["title"] not in existing_sigs and sig["text"] not in existing_sigs:
                        unique_signals.append(sig)
                        
                # AI classification filter
                filtered_signals = []
                if api_key and api_key.strip() and unique_signals:
                    print("Background Scheduler: Running AI Semantic Classifier on new signals...")
                    try:
                        classification_tasks = [
                            ai_agent.classify_signal_lead_relevance(
                                sig["title"], sig.get("text", ""), api_key, custom_services, model_name, developer_skills=developer_skills
                            ) for sig in unique_signals
                        ]
                        classification_results = await asyncio.gather(*classification_tasks, return_exceptions=True)
                        for sig, is_relevant in zip(unique_signals, classification_results):
                            if isinstance(is_relevant, Exception) or is_relevant:
                                filtered_signals.append(sig)
                            else:
                                print(f"Background Scheduler: AI filtered irrelevant signal: {sig['title'][:40]}")
                    except Exception as e:
                        print(f"Background Scheduler AI Classifier error: {str(e)}")
                        filtered_signals = unique_signals
                else:
                    filtered_signals = unique_signals

                for sig in filtered_signals:
                    lead_id = str(uuid.uuid4())
                    
                    local_matched, local_pct = get_mock_skills_matching(sig["title"] + " " + sig.get("text", ""), developer_skills)
                    new_lead = {
                        "id": lead_id,
                        "startup_name": "Detecting...",
                        "category": "Development",
                        "detected_signal": sig["title"],
                        "insight": "Scan lead to extract insight...",
                        "opportunity": "Scan lead to map opportunity...",
                        "pitch_idea": "Drafting pitch...",
                        "score": 5,
                        "score_explanation": "Not analyzed yet",
                        "url": sig["url"],
                        "source": sig["source"],
                        "status": "New",
                        "analyzed": False,
                        "contact_info": {
                            "email": "",
                            "twitter": "",
                            "linkedin": "",
                            "contact_page": "",
                            "author": sig["author"]
                        },
                        "raw_text": sig["text"],
                        "created_at": datetime.now().isoformat(),
                        "matched_skills": local_matched,
                        "match_percentage": local_pct
                    }
                    
                    try:
                        # 1. Resolve URL
                        website_url = ""
                        is_aggregator = any(domain in sig["url"].lower() for domain in ["reddit.com", "ycombinator.com", "producthunt.com", "betalist.com"])
                        if is_aggregator or not sig["url"]:
                            extracted_url = scraper.extract_url_from_text(sig["text"])
                            if extracted_url:
                                website_url = extracted_url
                                new_lead["url"] = extracted_url
                        else:
                            website_url = sig["url"]
                            
                        # 2. Audit website and enrich contact info
                        audit_data = None
                        if website_url:
                            audit_data = await scraper.audit_website(website_url, api_key)
                            if audit_data.get("success"):
                                    new_lead["contact_info"]["email"] = audit_data["contact_info"].get("email", "")
                                    new_lead["contact_info"]["twitter"] = audit_data["contact_info"].get("twitter", "")
                                    new_lead["contact_info"]["linkedin"] = audit_data["contact_info"].get("linkedin", "")
                                    new_lead["contact_info"]["contact_page"] = audit_data["contact_info"].get("contact_page", "")
                                    new_lead["tech_audit"] = {
                                        "seo_score": audit_data.get("seo_score", 100),
                                        "performance_score": audit_data.get("performance_score", 100),
                                        "mobile_score": audit_data.get("mobile_score", 100),
                                        "tech_stack": audit_data.get("tech_stack", []),
                                        "issues": audit_data.get("issues", [])
                                    }
                                    
                            if not new_lead["contact_info"].get("email") and website_url:
                                enrich_data = await scraper.enrich_contact_info(new_lead["startup_name"], website_url)
                                for key in ["email", "twitter", "linkedin", "contact_page"]:
                                    if not new_lead["contact_info"].get(key) and enrich_data.get(key):
                                        new_lead["contact_info"][key] = enrich_data[key]
                                        
                            # 3. Call AI
                            if api_key and api_key.strip():
                                if audit_data and audit_data.get("success"):
                                    ai_report = await ai_agent.analyze_audit_with_ai(
                                        audit_data, api_key, custom_services, model_name, custom_system_instructions, developer_skills=developer_skills
                                    )
                                else:
                                    signal_data = {
                                        "source": new_lead["source"],
                                        "title": new_lead["detected_signal"],
                                        "text": sig["text"],
                                        "author": new_lead["contact_info"].get("author", "Unknown")
                                    }
                                    ai_report = await ai_agent.analyze_signal_with_ai(
                                        signal_data, api_key, custom_services, model_name, custom_system_instructions, developer_skills=developer_skills
                                    )
                            else:
                                if audit_data and audit_data.get("success"):
                                    ai_report = get_mock_audit_analysis(audit_data)
                                else:
                                    ai_report = get_mock_pitch_and_analysis(new_lead["detected_signal"], new_lead.get("raw_text", ""), new_lead["source"])
                                    
                            new_lead["startup_name"] = ai_report.get("startup_name", new_lead["startup_name"])
                            new_lead["category"] = ai_report.get("category", new_lead["category"])
                            new_lead["insight"] = ai_report.get("insight", new_lead["insight"])
                            new_lead["opportunity"] = ai_report.get("opportunity", new_lead["opportunity"])
                            new_lead["pitch_idea"] = ai_report.get("pitch_idea", new_lead["pitch_idea"])
                            try:
                                new_lead["score"] = int(ai_report.get("score", new_lead["score"]))
                            except:
                                pass
                            new_lead["score_explanation"] = ai_report.get("score_explanation", new_lead["score_explanation"])
                            new_lead["matched_skills"] = ai_report.get("matched_skills", [])
                            try:
                                new_lead["match_percentage"] = int(ai_report.get("match_percentage", 0))
                            except:
                                pass
                            new_lead["analyzed"] = True
                    except Exception as ai_ex:
                        print(f"Scheduler AI Lead mapping failed: {str(ai_ex)}")
                        
                    leads.append(new_lead)
                    new_leads_added += 1
                    
                    # Webhook alert trigger for Score >= 8
                    if new_lead.get("score", 0) >= 8 and webhook_url:
                        await send_webhook_alert(new_lead, webhook_url, webhook_type)
                            
                if new_leads_added > 0:
                    save_leads(leads)
                    print(f"Background Scheduler: Added {new_leads_added} new leads dynamically.")
            else:
                print("Background Scheduler: Scraper periodic check skipped (Disabled).")
        except Exception as loop_ex:
            print(f"Background Scheduler Loop Error: {str(loop_ex)}")
            
        await asyncio.sleep(max(1, interval_hours) * 3600)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_periodic_scraper())


# Mount static frontend files
app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="public")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on http://localhost:{port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
