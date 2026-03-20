"""
FastAPI Backend Server — AI Adaptive Onboarding Engine
Endpoints:
  POST /analyze        — upload Resume + JD, get full pathway
  GET  /skills         — list all skills in the graph
  GET  /health         — health check
"""

import io
import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import PyPDF2
import docx

from skill_graph import SkillGraphEngine
from ai_parser import AIParsingEngine

app = FastAPI(
    title="AI Adaptive Onboarding Engine",
    description="Personalized learning pathway generator using skill graph traversal",
    version="1.0.0"
)

# ── CORS (allows React frontend to talk to this server) ───────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Initialize engines once at startup ───────────────────────────
skill_graph = SkillGraphEngine()
ai_parser = AIParsingEngine(skill_graph)


# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────

def extract_text_from_file(file: UploadFile) -> str:
    """Extracts raw text from PDF or DOCX upload."""
    contents = file.file.read()
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(io.BytesIO(contents))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()

    elif filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(contents))
        return "\n".join([para.text for para in doc.paragraphs]).strip()

    elif filename.endswith(".txt"):
        return contents.decode("utf-8", errors="ignore").strip()

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.filename}. Use PDF, DOCX, or TXT."
        )


# ─────────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {
        "status": "online",
        "skill_graph_nodes": skill_graph.graph.number_of_nodes(),
        "skill_graph_edges": skill_graph.graph.number_of_edges()
    }


@app.get("/skills")
def get_all_skills():
    """Returns the full skill catalog — used by frontend."""
    return {
        "skills": skill_graph.get_all_skills(),
        "domains": skill_graph.get_skill_domains(),
        "total": skill_graph.graph.number_of_nodes()
    }


@app.post("/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: UploadFile = File(...)
):
    """
    Main endpoint — full pipeline:
    1. Extract text from uploaded files
    2. AI parses resume → known skills
    3. AI parses JD → target skills
    4. Skill graph computes adaptive pathway
    5. AI generates reasoning summary
    6. Returns complete result to frontend
    """

    # ── Step 1: Extract text ──────────────────────────────────────
    try:
        resume_text = extract_text_from_file(resume)
        jd_text = extract_text_from_file(job_description)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File reading error: {str(e)}")

    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from resume.")
    if not jd_text:
        raise HTTPException(status_code=400, detail="Could not extract text from job description.")

    # ── Step 2: AI skill extraction ───────────────────────────────
    try:
        resume_result = ai_parser.extract_skills_from_resume(resume_text)
        jd_result = ai_parser.extract_skills_from_jd(jd_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI parsing error: {str(e)}")

    known_skill_ids = resume_result.get("known_skill_ids", [])
    target_skill_ids = jd_result.get("target_skill_ids", [])

    # ── Step 3: Adaptive pathway computation ─────────────────────
    try:
        pathway_result = skill_graph.compute_learning_pathway(
            known_skill_ids=known_skill_ids,
            target_skill_ids=target_skill_ids
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pathway computation error: {str(e)}")

    # ── Step 4: AI reasoning summary ─────────────────────────────
    try:
        reasoning_summary = ai_parser.generate_reasoning_summary(
            resume_result, jd_result, pathway_result
        )
    except Exception as e:
        reasoning_summary = "Reasoning summary unavailable."

    # ── Step 5: Build final response ─────────────────────────────
    return JSONResponse(content={
        "success": True,

        "candidate": {
            "summary": resume_result.get("candidate_summary", ""),
            "experience_level": resume_result.get("experience_level", ""),
            "primary_domain": resume_result.get("primary_domain", ""),
            "known_skills": resume_result.get("matched_skills", []),
            "known_skill_count": len(known_skill_ids)
        },

        "role": {
            "summary": jd_result.get("role_summary", ""),
            "seniority_level": jd_result.get("seniority_level", ""),
            "primary_domain": jd_result.get("primary_domain", ""),
            "required_skills": jd_result.get("required_skills", []),
            "must_have_ids": jd_result.get("must_have_ids", []),
            "nice_to_have_ids": jd_result.get("nice_to_have_ids", [])
        },

        "pathway": {
            "modules": pathway_result.get("pathway", []),
            "total_hours": pathway_result.get("total_hours", 0),
            "gap_count": pathway_result.get("gap_count", 0),
            "known_skills_count": pathway_result.get("known_skills_count", 0),
            "target_skills_count": pathway_result.get("target_skills_count", 0)
        },

        "reasoning": {
            "summary": reasoning_summary,
            "algorithm_trace": pathway_result.get("reasoning_trace", []),
            "gap_analysis": pathway_result.get("gap_analysis", {}),
            "hallucination_guard": {
                "resume": resume_result.get("hallucination_guard", {}),
                "jd": jd_result.get("hallucination_guard", {})
            }
        }
    })


@app.post("/analyze-text")
async def analyze_text(
    resume_text: str = Form(...),
    jd_text: str = Form(...)
):
    """
    Text-only version of /analyze — useful for testing
    without needing actual files.
    """
    try:
        resume_result = ai_parser.extract_skills_from_resume(resume_text)
        jd_result = ai_parser.extract_skills_from_jd(jd_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI parsing error: {str(e)}")

    known_skill_ids = resume_result.get("known_skill_ids", [])
    target_skill_ids = jd_result.get("target_skill_ids", [])

    pathway_result = skill_graph.compute_learning_pathway(
        known_skill_ids=known_skill_ids,
        target_skill_ids=target_skill_ids
    )

    reasoning_summary = ai_parser.generate_reasoning_summary(
        resume_result, jd_result, pathway_result
    )

    return JSONResponse(content={
        "success": True,
        "candidate": resume_result,
        "role": jd_result,
        "pathway": pathway_result,
        "reasoning": {
            "summary": reasoning_summary,
            "algorithm_trace": pathway_result.get("reasoning_trace", [])
        }
    })