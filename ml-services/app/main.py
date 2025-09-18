from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union
import os
import io
import re
from collections import Counter

try:
    # Optional dependencies; declared in requirements.txt
    import PyPDF2  # type: ignore
except Exception:  # pragma: no cover - optional import
    PyPDF2 = None  # type: ignore

try:
    import docx  # python-docx  # type: ignore
except Exception:  # pragma: no cover - optional import
    docx = None  # type: ignore


class Recommendation(BaseModel):
    id: str
    company: str
    role: str
    description: str
    type: Literal["internship", "full-time", "part-time"]
    location: str
    skills: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    matchScore: int
    applyUrl: Optional[str] = None


class ResumePayload(BaseModel):
    skills: List[str]
    interests: List[str]
    experience: List[str]
    projects: List[str]
    education: Optional[List[str]] = None
    location: Optional[str] = None
    type: Literal["resume"] = "resume"


class InterestsPayload(BaseModel):
    interests: List[str]
    type: Literal["interests"] = "interests"


app = FastAPI(title="ML Services", version="1.0.0")

# CORS (align with backend/frontend local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_company_names() -> List[str]:
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "companies.txt")
    try:
        with open(os.path.abspath(data_path), "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
            return [line.split("\t", 1)[-1] if "\t" in line else line for line in lines if line]
    except FileNotFoundError:
        # Fallback minimal list
        return [
            "RELIANCE INDUSTRIES LIMITED",
            "TATA CONSULTANCY SERVICES LIMITED",
            "HDFC BANK LIMITED",
            "INFOSYS LIMITED",
        ]


COMPANY_NAMES = load_company_names()


@app.get("/health")
def health():
    return {"status": "healthy"}


def _extract_text_from_pdf(content_stream: io.BytesIO) -> str:
    if PyPDF2 is None:
        return ""
    try:
        reader = PyPDF2.PdfReader(content_stream)
        texts = []
        for page in getattr(reader, "pages", []):
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                continue
        return "\n".join(texts)
    except Exception:
        return ""


def _extract_text_from_docx(content_stream: io.BytesIO) -> str:
    if docx is None:
        return ""
    try:
        document = docx.Document(content_stream)
        return "\n".join(p.text for p in document.paragraphs if p.text)
    except Exception:
        return ""


def _extract_text_generic(filename: str, data: bytes, mime: Optional[str]) -> str:
    ext = (os.path.splitext(filename or "")[1] or "").lower()
    mime = (mime or "").lower()
    stream = io.BytesIO(data)

    if ext == ".pdf" or "pdf" in mime:
        return _extract_text_from_pdf(stream)
    if ext == ".docx" or "officedocument.wordprocessingml.document" in mime:
        return _extract_text_from_docx(stream)
    # Fallback: try decode as text
    try:
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def _infer_from_text(text: str) -> dict:
    lowered = text.lower()
    tokens = re.findall(r"[a-zA-Z][a-zA-Z+.#-]+", lowered)
    counts = Counter(tokens)

    known_skills = [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "sql", "mongodb", "mysql", "postgres", "aws", "azure", "gcp",
        "docker", "kubernetes", "linux", "react", "node", "django", "flask",
        "tensorflow", "pytorch", "scikit-learn", "nlp", "ml", "machine learning",
        "data science", "pandas", "numpy", "git", "html", "css"
    ]
    interest_keywords_map = {
        "data science": ["data", "pandas", "numpy", "ml", "machine", "analytics"],
        "ai-ml": ["ml", "machine", "deep", "neural", "ai", "pytorch", "tensorflow"],
        "web development": ["react", "node", "javascript", "typescript", "css", "html"],
        "cloud": ["aws", "azure", "gcp", "kubernetes", "docker", "cloud"],
        "devops": ["docker", "kubernetes", "ci", "cd", "jenkins", "pipeline"],
        "cybersecurity": ["security", "owasp", "vulnerability", "penetration", "threat"],
        "mobile": ["android", "ios", "flutter", "react native"]
    }

    found_skills = []
    for skill in known_skills:
        if " " in skill:
            if skill in lowered:
                found_skills.append(skill)
        else:
            if counts.get(skill, 0) > 0:
                found_skills.append(skill)

    inferred_interests = []
    for label, kws in interest_keywords_map.items():
        if any((kw in lowered) for kw in kws):
            inferred_interests.append(label)

    # Simple heuristics for other sections
    experience = []
    projects = []
    education = []

    for line in lowered.splitlines():
        line_stripped = line.strip()
        if not line_stripped:
            continue
        if any(h in line_stripped for h in ["experience", "intern", "worked", "company"]):
            experience.append(line.strip())
        if any(h in line_stripped for h in ["project", "built", "developed"]):
            projects.append(line.strip())
        if any(h in line_stripped for h in ["b.tech", "btech", "bachelor", "master", "university", "college"]):
            education.append(line.strip())

    location = None
    loc_match = re.search(r"\b(location|based in|residing in)[:\s]+([a-zA-Z ,.-]+)\b", lowered)
    if loc_match:
        location = loc_match.group(2).title()

    # Ensure at least one interest to avoid downstream errors
    if not inferred_interests and found_skills:
        # Map some common skills to interests
        if any(s in found_skills for s in ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch"]):
            inferred_interests.append("ai-ml")
        if any(s in found_skills for s in ["react", "javascript", "typescript", "html", "css", "node"]):
            inferred_interests.append("web development")
        if any(s in found_skills for s in ["aws", "azure", "gcp", "docker", "kubernetes"]):
            inferred_interests.append("cloud")

    return {
        "skills": sorted(set(found_skills)),
        "interests": sorted(set(inferred_interests)),
        "experience": experience[:20],
        "projects": projects[:20],
        "education": education[:20],
        "location": location,
    }


@app.post("/parse_resume")
async def parse_resume(file: UploadFile = File(...), file_type: Optional[str] = Form(None)):
    filename = file.filename or "resume"
    content_bytes = await file.read()
    await file.close()

    text = _extract_text_generic(filename, content_bytes, file_type or file.content_type)
    inferred = _infer_from_text(text)

    size_kb = max(1, int(len(content_bytes) / 1024))
    return {
        "filename": filename,
        "sizeKB": size_kb,
        **inferred,
    }


def _normalize_terms(values: List[str]) -> List[str]:
    normed = []
    for v in values or []:
        if not v:
            continue
        s = str(v).strip().lower()
        if s:
            normed.append(s)
    return normed


def _score_company(company: str, interests: List[str]) -> int:
    # Naive scoring: keyword overlap between company/industry hints and interests
    text = company.lower()
    score = 0
    for term in interests:
        if term in text:
            score += 30
        elif any(word in text for word in term.split()):
            score += 10
    # Clamp 0..100
    return max(0, min(100, score))


def _make_recommendation(company: str, match_score: int, location_hint: Optional[str]) -> Recommendation:
    role = "Intern"
    job_type: Literal["internship", "full-time", "part-time"] = "internship"
    location = location_hint or "Remote"
    skills = ["Communication", "Problem Solving", "Teamwork"]
    requirements = ["Currently enrolled in a degree program", "Eager to learn"]
    benefits = ["Mentorship", "Flexible hours"]
    apply_url = None
    rec_id = f"{abs(hash(company)) % 10_000_000}"
    description = f"Opportunity at {company}. Contribute to projects and learn from industry professionals."

    return Recommendation(
        id=rec_id,
        company=company,
        role=role,
        description=description,
        type=job_type,
        location=location,
        skills=skills,
        requirements=requirements,
        benefits=benefits,
        matchScore=match_score,
        applyUrl=apply_url,
    )


@app.post("/recommend")
def recommend(payload: Union[InterestsPayload, ResumePayload]):
    # Determine interests list and optional location from payload
    if payload.type == "interests":
        interests = _normalize_terms(payload.interests)
        location = None
    elif payload.type == "resume":
        interests = _normalize_terms(payload.interests)
        location = payload.location
    else:
        raise HTTPException(status_code=400, detail="Invalid payload type")

    if not interests:
        raise HTTPException(status_code=400, detail="No interests provided")

    # Score all companies and pick top N
    scored = []
    for name in COMPANY_NAMES:
        score = _score_company(name, interests)
        scored.append((name, score))

    # Sort by score desc, then name
    scored.sort(key=lambda x: (-x[1], x[0]))

    top = [s for s in scored if s[1] > 0][:20]  # top 20 with positive score
    if not top:
        # If nothing scored, fallback to first few companies with low score
        top = [(name, 50) for name in COMPANY_NAMES[:10]]

    recommendations = [_make_recommendation(name, score, location) for name, score in top]

    return {"recommendations": [r.dict() for r in recommendations]}


