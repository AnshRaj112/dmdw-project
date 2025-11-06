from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union, Dict
import os
import io
import re
from collections import Counter

# Import advanced ML engine
from app.services.ml_engine import ml_engine

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
    sector: str
    role: str
    description: str
    type: Literal["internship", "full-time", "part-time"]
    location: str
    skills: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    matchScore: float  # Confidence score (0.0 to 1.0, e.g., 0.88, 0.82, 0.78)
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
    """
    Load company names ONLY from company_database.json.
    Returns empty list if database cannot be loaded (no hardcoded fallbacks).
    """
    import json
    db_path = os.path.join(os.path.dirname(__file__), "..", "data", "company_database.json")
    try:
        with open(os.path.abspath(db_path), "r", encoding="utf-8") as db_file:
            db_data = json.load(db_file)
            companies = list(db_data.get("companies", {}).keys())
            if not companies:
                print("Warning: company_database.json contains no companies")
            return companies
    except FileNotFoundError:
        print(f"Error: company_database.json not found at {db_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in company_database.json: {e}")
        return []
    except Exception as e:
        print(f"Error: Could not load company database: {e}")
        return []


COMPANY_NAMES = load_company_names()

# Enhanced sector taxonomy with detailed roles, skills, and benefits
SECTOR_TO_DETAILS = {
    "Technology / Software / Digital Services": {
        "roles": [
            "Software Development Intern", "Data Science Intern", "DevOps Intern", 
            "UI/UX Design Intern", "Product Management Intern", "QA Testing Intern",
            "Cloud Engineering Intern", "AI/ML Intern", "Cybersecurity Intern",
            "Video Editing Intern", "Graphic Design Intern", "Content Creation Intern",
            "Photography Intern", "Music Production Intern", "Game Development Intern",
            "Motion Graphics Intern", "Creative Director Intern", "Digital Marketing Intern"
        ],
        "skills": [
            "Programming Languages", "Problem Solving", "Analytical Thinking", 
            "Team Collaboration", "Version Control", "Agile Methodologies",
            "Database Management", "API Development", "System Design"
        ],
        "requirements": [
            "Currently pursuing Computer Science/IT degree", "Basic programming knowledge",
            "Strong problem-solving skills", "Good communication skills", "Eager to learn"
        ],
        "benefits": [
            "Mentorship from senior developers", "Real-world project experience",
            "Flexible working hours", "Learning resources", "Networking opportunities",
            "Certificate of completion", "Potential full-time offer"
        ]
    },
    "Fintech / Banking / Finance": {
        "roles": [
            "Fintech Development Intern", "Risk Analysis Intern", "Data Analytics Intern",
            "Product Management Intern", "UX Research Intern", "Compliance Intern"
        ],
        "skills": [
            "Financial Analysis", "Data Interpretation", "Risk Assessment", 
            "Regulatory Knowledge", "Customer Service", "Problem Solving"
        ],
        "requirements": [
            "Finance/Economics/Commerce background preferred", "Analytical mindset",
            "Attention to detail", "Basic understanding of financial products"
        ],
        "benefits": [
            "Industry exposure", "Financial modeling training", "Regulatory insights",
            "Professional networking", "Performance bonus potential"
        ]
    },
    "E-commerce / Retail / Consumer": {
        "roles": [
            "E-commerce Operations Intern", "Digital Marketing Intern", "Supply Chain Intern",
            "Customer Experience Intern", "Data Analytics Intern", "Product Management Intern"
        ],
        "skills": [
            "Digital Marketing", "Customer Analysis", "Supply Chain Management",
            "Data Analytics", "User Experience", "Project Management"
        ],
        "requirements": [
            "Business/Marketing background preferred", "Digital literacy",
            "Customer service orientation", "Analytical thinking"
        ],
        "benefits": [
            "E-commerce platform experience", "Digital marketing tools training",
            "Customer insights", "Supply chain optimization knowledge"
        ]
    },
    "Automotive / Manufacturing / Industrial": {
        "roles": [
            "Manufacturing Engineering Intern", "Quality Control Intern", "Process Optimization Intern",
            "Supply Chain Intern", "Safety Engineering Intern", "R&D Intern"
        ],
        "skills": [
            "Process Analysis", "Quality Management", "Safety Protocols", 
            "Manufacturing Systems", "Problem Solving", "Technical Documentation"
        ],
        "requirements": [
            "Engineering background preferred", "Safety consciousness",
            "Technical aptitude", "Process improvement mindset"
        ],
        "benefits": [
            "Manufacturing process exposure", "Safety training certification",
            "Quality management insights", "Industrial automation knowledge"
        ]
    },
    "Energy / Oil & Gas / Utilities": {
        "roles": [
            "Energy Analytics Intern", "Sustainability Intern", "Operations Intern",
            "Environmental Compliance Intern", "Project Management Intern"
        ],
        "skills": [
            "Energy Analysis", "Environmental Awareness", "Regulatory Compliance",
            "Project Management", "Data Analysis", "Sustainability Planning"
        ],
        "requirements": [
            "Engineering/Environmental Science background", "Sustainability interest",
            "Regulatory awareness", "Analytical capabilities"
        ],
        "benefits": [
            "Energy sector insights", "Sustainability practices", "Regulatory knowledge",
            "Environmental impact assessment"
        ]
    },
    "Healthcare / Pharmaceuticals / Biotech": {
        "roles": [
            "Research Intern", "Clinical Data Intern", "Regulatory Affairs Intern",
            "Quality Assurance Intern", "Medical Writing Intern", "Lab Assistant"
        ],
        "skills": [
            "Research Methodology", "Data Analysis", "Regulatory Knowledge",
            "Laboratory Techniques", "Medical Writing", "Quality Standards"
        ],
        "requirements": [
            "Life Sciences/Medical background", "Research aptitude",
            "Attention to detail", "Regulatory awareness"
        ],
        "benefits": [
            "Research experience", "Regulatory insights", "Laboratory techniques",
            "Medical writing skills", "Clinical trial exposure"
        ]
    },
    "Consulting / Professional Services": {
        "roles": [
            "Business Analysis Intern", "Strategy Intern", "Research Intern",
            "Client Services Intern", "Data Analytics Intern", "Project Management Intern"
        ],
        "skills": [
            "Business Analysis", "Strategic Thinking", "Client Communication",
            "Research Skills", "Presentation Skills", "Problem Solving"
        ],
        "requirements": [
            "Strong analytical skills", "Communication abilities", "Business acumen",
            "Research capabilities", "Presentation skills"
        ],
        "benefits": [
            "Business strategy exposure", "Client interaction experience",
            "Industry insights", "Professional networking", "Case study experience"
        ]
    }
}

# Enhanced company-to-sector mapping with modern tech companies
SECTOR_KEYWORDS = {
    "Technology / Software / Digital Services": [
        "microsoft", "google", "amazon", "meta", "adobe", "oracle", "salesforce", "netflix", 
        "uber", "flipkart", "paytm", "zomato", "swiggy", "oyo", "byju", "unacademy", "vedantu", 
        "upgrad", "cred", "razorpay", "phonepe", "bharatpe", "juspay", "payu", "cashfree", 
        "freshworks", "zoho", "postman", "hashicorp", "docker", "atlassian", "slack", "twilio", 
        "stripe", "shopify", "woocommerce", "magento", "wix", "squarespace", "webflow", "figma", 
        "canva", "notion", "asana", "trello", "miro", "invision", "sketch", "principle", "framer",
        "spotify", "soundcloud", "bandcamp", "apple", "samsung", "oneplus", "xiaomi", "oppo", 
        "vivo", "realme", "intel", "amd", "nvidia", "qualcomm", "broadcom", "mediatek", "arm",
        "tcs", "infosys", "wipro", "hcl", "tech mahindra", "accenture", "cognizant", "capgemini", 
        "ibm", "deloitte", "kpmg", "pwc", "ernst", "mckinsey", "bain", "boston consulting", 
        "oliver wyman", "at kearney", "strategy", "booz allen", "youtube", "instagram", "tiktok",
        "twitter", "linkedin", "snapchat", "pinterest", "reddit", "discord", "twitch", "vimeo",
        "dailymotion", "unity", "epic games", "unreal engine", "steam", "sony", "nintendo", "valve",
        "blizzard", "electronic arts", "ubisoft", "rockstar", "activision", "bungie", "riot games",
        "supercell", "mojang", "roblox", "fortnite", "minecraft", "league of legends", "world of warcraft",
        "call of duty", "grand theft auto", "fifa", "assassin's creed", "far cry", "watch dogs", "just dance",
        "technology", "software", "digital", "it"
    ],
    "Fintech / Banking / Finance": [
        "hdfc bank", "icici bank", "axis bank", "kotak mahindra bank", "indusind bank", 
        "bajaj finance", "lic housing finance", "power finance corporation", 
        "rural electrification", "shriram finance", "muthoot finance", "pfc", "rec",
        "bank", "finance", "fintech", "payment", "credit", "lending", "investment", 
        "wealth", "insurance", "mutual fund", "trading", "housing finance"
    ],
    "E-commerce / Retail / Consumer": [
        "reliance retail", "hindustan unilever", "itc", "flipkart", "amazon", "swiggy", "zomato", 
        "oyo", "retail", "ecommerce", "e-commerce", "consumer", "fmcg", "fashion", "lifestyle", 
        "grocery", "marketplace", "logistics", "supply chain", "merchandising"
    ],
    "Automotive / Manufacturing / Industrial": [
        "auto", "maruti", "mahindra", "bajaj auto", "hero", "tvs", "eicher", "ashok leyland", 
        "hyundai", "kia", "volkswagen", "skoda", "audi", "bmw", "mercedes", "jaguar", "volvo", 
        "ford", "general motors", "chrysler", "jeep", "ram", "dodge", "fiat", "alfa romeo", 
        "maserati", "ferrari", "lamborghini", "bentley", "rolls-royce", "aston martin", 
        "mclaren", "porsche", "lotus", "morgan", "caterham", "tvr", "noble", "koenigsegg", 
        "bugatti", "pagani", "rimac", "l&t", "larsen", "ultratech", "suzuki", "manufactur", "industrial"
    ],
    "Energy / Oil & Gas / Utilities": [
        "oil", "ongc", "gail", "bharat petroleum", "hpcl", "bpcl", "indian oil", "oil india", 
        "adani", "reliance", "ntpc", "nhpc", "power grid", "nuclear", "energy", "gas", "power", 
        "utilities", "renewable", "solar", "wind", "hydro", "thermal", "coal", "petroleum"
    ],
    "Healthcare / Pharmaceuticals / Biotech": [
        "serum", "pharma", "pharmaceutical", "health", "hospital", "medical", "biotech", 
        "biotechnology", "clinical", "research", "drug", "medicine", "therapeutic", "diagnostic", 
        "vaccine", "biomedical", "life sciences", "healthcare", "wellness"
    ],
    "Consulting / Professional Services": [
        "deloitte", "kpmg", "pwc", "ernst", "mckinsey", "bain", "boston consulting", 
        "oliver wyman", "at kearney", "strategy", "booz allen", "consulting", "advisory", 
        "professional services", "management consulting", "strategy consulting"
    ]
}

# Enhanced interest keywords to sectors mapping
INTEREST_TO_SECTORS = {
    # Technology interests
    "software": ["Technology / Software / Digital Services"],
    "coding": ["Technology / Software / Digital Services"],
    "programming": ["Technology / Software / Digital Services"],
    "it": ["Technology / Software / Digital Services"],
    "digital": ["Technology / Software / Digital Services"],
    "web development": ["Technology / Software / Digital Services"],
    "ai-ml": ["Technology / Software / Digital Services"],
    "machine learning": ["Technology / Software / Digital Services"],
    "artificial intelligence": ["Technology / Software / Digital Services"],
    "data science": ["Technology / Software / Digital Services"],
    "cloud": ["Technology / Software / Digital Services"],
    "devops": ["Technology / Software / Digital Services"],
    "cybersecurity": ["Technology / Software / Digital Services"],
    "mobile": ["Technology / Software / Digital Services"],
    "ui/ux": ["Technology / Software / Digital Services"],
    "product design": ["Technology / Software / Digital Services"],
    "ux": ["Technology / Software / Digital Services"],
    "ui": ["Technology / Software / Digital Services"],
    "design": ["Technology / Software / Digital Services"],
    "video editing": ["Technology / Software / Digital Services"],
    "graphic design": ["Technology / Software / Digital Services"],
    "content creation": ["Technology / Software / Digital Services"],
    "photography": ["Technology / Software / Digital Services"],
    "music production": ["Technology / Software / Digital Services"],
    "gaming": ["Technology / Software / Digital Services"],
    "product management": ["Technology / Software / Digital Services"],
    "blockchain": ["Technology / Software / Digital Services"],
    "iot": ["Technology / Software / Digital Services"],
    "ar/vr": ["Technology / Software / Digital Services"],
    "gaming": ["Technology / Software / Digital Services"],
    
    # Finance interests
    "banking": ["Fintech / Banking / Finance"],
    "finance": ["Fintech / Banking / Finance"],
    "fintech": ["Fintech / Banking / Finance"],
    "insurance": ["Fintech / Banking / Finance"],
    "investment": ["Fintech / Banking / Finance"],
    "trading": ["Fintech / Banking / Finance"],
    "cryptocurrency": ["Fintech / Banking / Finance"],
    "blockchain": ["Fintech / Banking / Finance"],
    "payments": ["Fintech / Banking / Finance"],
    "lending": ["Fintech / Banking / Finance"],
    
    # E-commerce interests
    "retail": ["E-commerce / Retail / Consumer"],
    "ecommerce": ["E-commerce / Retail / Consumer"],
    "e-commerce": ["E-commerce / Retail / Consumer"],
    "fmcg": ["E-commerce / Retail / Consumer"],
    "consumer": ["E-commerce / Retail / Consumer"],
    "sales": ["E-commerce / Retail / Consumer"],
    "marketing": ["E-commerce / Retail / Consumer"],
    "digital marketing": ["E-commerce / Retail / Consumer"],
    "supply chain": ["E-commerce / Retail / Consumer"],
    "logistics": ["E-commerce / Retail / Consumer"],
    
    # Automotive/Manufacturing interests
    "automotive": ["Automotive / Manufacturing / Industrial"],
    "manufacturing": ["Automotive / Manufacturing / Industrial"],
    "industrial": ["Automotive / Manufacturing / Industrial"],
    "mechanical": ["Automotive / Manufacturing / Industrial"],
    "automotive engineering": ["Automotive / Manufacturing / Industrial"],
    "production": ["Automotive / Manufacturing / Industrial"],
    "quality control": ["Automotive / Manufacturing / Industrial"],
    
    # Energy interests
    "energy": ["Energy / Oil & Gas / Utilities"],
    "oil": ["Energy / Oil & Gas / Utilities"],
    "gas": ["Energy / Oil & Gas / Utilities"],
    "power": ["Energy / Oil & Gas / Utilities"],
    "renewable energy": ["Energy / Oil & Gas / Utilities"],
    "solar": ["Energy / Oil & Gas / Utilities"],
    "wind": ["Energy / Oil & Gas / Utilities"],
    "sustainability": ["Energy / Oil & Gas / Utilities"],
    "environmental": ["Energy / Oil & Gas / Utilities"],
    "utilities": ["Energy / Oil & Gas / Utilities"],
    
    # Healthcare interests
    "pharma": ["Healthcare / Pharmaceuticals / Biotech"],
    "pharmaceutical": ["Healthcare / Pharmaceuticals / Biotech"],
    "healthcare": ["Healthcare / Pharmaceuticals / Biotech"],
    "medical": ["Healthcare / Pharmaceuticals / Biotech"],
    "biotech": ["Healthcare / Pharmaceuticals / Biotech"],
    "biotechnology": ["Healthcare / Pharmaceuticals / Biotech"],
    "clinical": ["Healthcare / Pharmaceuticals / Biotech"],
    "research": ["Healthcare / Pharmaceuticals / Biotech"],
    "life sciences": ["Healthcare / Pharmaceuticals / Biotech"],
    "medicine": ["Healthcare / Pharmaceuticals / Biotech"],
    
    # Consulting interests
    "consulting": ["Consulting / Professional Services"],
    "strategy": ["Consulting / Professional Services"],
    "management": ["Consulting / Professional Services"],
    "business analysis": ["Consulting / Professional Services"],
    "advisory": ["Consulting / Professional Services"],
    "professional services": ["Consulting / Professional Services"],
}


def _company_sector(company: str) -> str:
    name = company.lower()
    
    # Remove common suffixes for better matching
    name_clean = name.replace(" limited", "").replace(" private limited", "").replace(" corporation", "")
    
    # Check for finance companies first (most specific)
    if any(k in name_clean for k in ["hdfc bank", "icici bank", "axis bank", "kotak mahindra bank", "indusind bank", 
                                    "bajaj finance", "lic housing finance", "power finance corporation", 
                                    "rural electrification", "shriram finance", "muthoot finance"]):
        return "Fintech / Banking / Finance"
    
    # Check for banking/finance keywords
    if any(k in name_clean for k in ["bank", "finance", "fintech", "payment", "credit", "lending", "investment", "wealth", "insurance", "mutual fund", "trading", "housing finance"]):
        return "Fintech / Banking / Finance"
    
    # Check for technology companies (including social media and gaming)
    if any(k in name_clean for k in ["microsoft", "google", "amazon", "meta", "adobe", "oracle", "salesforce", "netflix", "uber", "flipkart", "paytm", "zomato", "swiggy", "oyo", "byju", "unacademy", "vedantu", "upgrad", "cred", "razorpay", "phonepe", "bharatpe", "juspay", "payu", "cashfree", "freshworks", "zoho", "postman", "hashicorp", "docker", "atlassian", "slack", "twilio", "stripe", "shopify", "woocommerce", "magento", "wix", "squarespace", "webflow", "figma", "canva", "notion", "asana", "trello", "miro", "invision", "sketch", "principle", "framer", "spotify", "soundcloud", "bandcamp", "apple", "samsung", "oneplus", "xiaomi", "oppo", "vivo", "realme", "intel", "amd", "nvidia", "qualcomm", "broadcom", "mediatek", "arm", "tcs", "infosys", "wipro", "hcl", "tech mahindra", "accenture", "cognizant", "capgemini", "ibm", "deloitte", "kpmg", "pwc", "ernst", "mckinsey", "bain", "boston consulting", "oliver wyman", "at kearney", "strategy", "booz allen", "youtube", "instagram", "tiktok", "twitter", "linkedin", "snapchat", "pinterest", "reddit", "discord", "twitch", "vimeo", "dailymotion", "unity", "epic games", "unreal engine", "steam", "sony", "nintendo", "valve", "blizzard", "electronic arts", "ubisoft", "rockstar", "activision", "bungie", "riot games", "supercell", "mojang", "roblox", "fortnite", "minecraft", "league of legends", "world of warcraft", "call of duty", "grand theft auto", "fifa", "assassin's creed", "far cry", "watch dogs", "just dance"]):
        return "Technology / Software / Digital Services"
    
    # Check for e-commerce/retail
    if any(k in name_clean for k in ["retail", "ecommerce", "e-commerce", "consumer", "fmcg", "fashion", "lifestyle", "grocery", "marketplace", "logistics", "supply chain", "merchandising"]):
        return "E-commerce / Retail / Consumer"
    
    # Check for automotive/manufacturing
    if any(k in name_clean for k in ["auto", "maruti", "mahindra", "bajaj auto", "hero", "tvs", "eicher", "ashok leyland", "hyundai", "kia", "volkswagen", "skoda", "audi", "bmw", "mercedes", "jaguar", "volvo", "ford", "general motors", "chrysler", "jeep", "ram", "dodge", "fiat", "alfa romeo", "maserati", "ferrari", "lamborghini", "bentley", "rolls-royce", "aston martin", "mclaren", "porsche", "lotus", "morgan", "caterham", "tvr", "noble", "koenigsegg", "bugatti", "pagani", "rimac", "l&t", "larsen", "ultratech", "suzuki", "manufactur", "industrial"]):
        return "Automotive / Manufacturing / Industrial"
    
    # Check for energy/oil & gas
    if any(k in name_clean for k in ["oil", "ongc", "gail", "bharat petroleum", "hpcl", "bpcl", "indian oil", "oil india", "adani", "reliance", "ntpc", "nhpc", "power grid", "nuclear", "energy", "gas", "power", "utilities", "renewable", "solar", "wind", "hydro", "thermal", "coal", "petroleum"]):
        return "Energy / Oil & Gas / Utilities"
    
    # Check for healthcare/pharma
    if any(k in name_clean for k in ["serum", "pharma", "pharmaceutical", "health", "hospital", "medical", "biotech", "biotechnology", "clinical", "research", "drug", "medicine", "therapeutic", "diagnostic", "vaccine", "biomedical", "life sciences", "healthcare", "wellness"]):
        return "Healthcare / Pharmaceuticals / Biotech"
    
    # Check for consulting
    if any(k in name_clean for k in ["deloitte", "kpmg", "pwc", "ernst", "mckinsey", "bain", "boston consulting", "oliver wyman", "at kearney", "strategy", "booz allen", "consulting", "advisory", "professional services", "management consulting", "strategy consulting"]):
        return "Consulting / Professional Services"
    
    # Default to technology sector
    return "Technology / Software / Digital Services"


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
    """Enhanced resume parsing using advanced ML engine"""
    try:
        # Use advanced ML engine for better parsing
        features = ml_engine.extract_advanced_features(text)
        skills_with_confidence = ml_engine.extract_skills_with_confidence(text)
        
        # Extract skills from confidence-based extraction
        found_skills = [skill for skill, confidence in skills_with_confidence if confidence > 0.5]
        
        # Enhanced interest detection using ML
        lowered = text.lower()
        interest_keywords_map = {
            "data science": ["data", "pandas", "numpy", "ml", "machine", "analytics", "statistics", "analysis"],
            "ai-ml": ["ml", "machine", "deep", "neural", "ai", "pytorch", "tensorflow", "artificial intelligence"],
            "web development": ["react", "node", "javascript", "typescript", "css", "html", "frontend", "backend"],
            "cloud": ["aws", "azure", "gcp", "kubernetes", "docker", "cloud", "devops"],
            "devops": ["docker", "kubernetes", "ci", "cd", "jenkins", "pipeline", "automation"],
            "cybersecurity": ["security", "owasp", "vulnerability", "penetration", "threat", "cyber"],
            "mobile": ["android", "ios", "flutter", "react native", "mobile development"],
            "product design": ["product design", "ui/ux", "ux", "ui", "design", "wireframe", "prototype", "figma", "sketch", "invision", "framer", "adobe xd", "adobe"],
            "video editing": ["video editing", "video", "editing", "premiere", "after effects", "final cut", "davinci", "resolve", "film", "cinematography", "motion graphics", "animation", "post production"],
            "graphic design": ["graphic design", "photoshop", "illustrator", "indesign", "canva", "visual design", "branding", "logo", "typography", "layout"],
            "content creation": ["content creation", "content", "social media", "youtube", "instagram", "tiktok", "blogging", "writing", "copywriting", "marketing"],
            "photography": ["photography", "photo", "camera", "lightroom", "photoshop", "portrait", "landscape", "wedding", "fashion", "commercial"],
            "music production": ["music production", "music", "audio", "sound", "mixing", "mastering", "recording", "studio", "pro tools", "ableton", "logic"],
            "gaming": ["gaming", "game development", "unity", "unreal", "game design", "level design", "game art", "3d modeling", "animation", "game programming"]
        }

        inferred_interests = []
        for label, kws in interest_keywords_map.items():
            if any((kw in lowered) for kw in kws):
                inferred_interests.append(label)

        # Enhanced experience and project extraction
        experience = []
        projects = []
        education = []

        for line in lowered.splitlines():
            line_stripped = line.strip()
            if not line_stripped:
                continue
            if any(h in line_stripped for h in ["experience", "intern", "worked", "company", "employment", "position", "role"]):
                experience.append(line.strip())
            if any(h in line_stripped for h in ["project", "built", "developed", "created", "implemented", "designed"]):
                projects.append(line.strip())
            if any(h in line_stripped for h in ["b.tech", "btech", "bachelor", "master", "university", "college", "degree", "education", "graduated"]):
                education.append(line.strip())

        # Location is not parsed from resume - always set to None
        location = None

        # Ensure at least one interest to avoid downstream errors
        if not inferred_interests and found_skills:
            # Map some common skills to interests using ML confidence
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
            "ml_features": features,  # Include ML-extracted features
            "skills_confidence": skills_with_confidence
        }
    except Exception as e:
        print(f"Error in advanced parsing: {e}")
        # Fallback to basic parsing
        return _basic_infer_from_text(text)

def _basic_infer_from_text(text: str) -> dict:
    """Basic fallback parsing method"""
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

    found_skills = []
    for skill in known_skills:
        if " " in skill:
            if skill in lowered:
                found_skills.append(skill)
        else:
            if counts.get(skill, 0) > 0:
                found_skills.append(skill)

    # Basic interest mapping
    inferred_interests = []
    if any(s in found_skills for s in ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch"]):
        inferred_interests.append("ai-ml")
    if any(s in found_skills for s in ["react", "javascript", "typescript", "html", "css", "node"]):
        inferred_interests.append("web development")
    if any(s in found_skills for s in ["aws", "azure", "gcp", "docker", "kubernetes"]):
        inferred_interests.append("cloud")

    return {
        "skills": sorted(set(found_skills)),
        "interests": sorted(set(inferred_interests)),
        "experience": [],
        "projects": [],
        "education": [],
        "location": None,
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


def _infer_target_sectors(interests: List[str]) -> List[str]:
    targets: List[str] = []
    for term in interests:
        t = term.lower()
        # direct map
        for key, sectors in INTEREST_TO_SECTORS.items():
            if key in t:
                targets.extend(sectors)
        # heuristic groupings
        if any(k in t for k in ["python", "react", "developer", "engineering", "software", "coding"]):
            targets.append("IT / Software / Digital Services")
        if any(k in t for k in ["bank", "finance", "fintech", "credit"]):
            targets.append("Banking, Finance, Insurance")
        if any(k in t for k in ["energy", "oil", "gas", "power"]):
            targets.append("Oil, Gas & Energy")
        if any(k in t for k in ["hotel", "tour", "travel", "hospitality"]):
            targets.append("Travel & Hospitality")
        if any(k in t for k in ["retail", "fmcg", "consumer", "sales"]):
            targets.append("Retail / FMCG / Consumer Goods")
        if any(k in t for k in ["construction", "infrastructure", "civil"]):
            targets.append("Infrastructure & Construction")
        if any(k in t for k in ["mining", "steel", "metal"]):
            targets.append("Metals & Mining")
        if any(k in t for k in ["pharma", "health", "hospital"]):
            targets.append("Pharmaceuticals & Healthcare")
    # unique preserve order
    seen = set()
    ordered = []
    for s in targets:
        if s not in seen:
            seen.add(s)
            ordered.append(s)
    return ordered


def _calculate_confidence_score(company: str, interests: List[str], resume_data: Dict = None) -> float:
    """
    Calculate confidence score (0.0 to 1.0) based on:
    1. Interest → Sector matching
    2. Skills → Company required skills matching
    3. Overall match quality
    
    Returns confidence as decimal (e.g., 0.88, 0.82, 0.78)
    """
    # Get company info from database
    company_info = ml_engine.company_database.get('companies', {}).get(company, {})
    if not company_info:
        return 0.0  # No confidence if company not in database
    
    confidence_components = []
    
    # 1. Interest → Sector matching (40% weight)
    company_sector = company_info.get('sector', '')
    target_sectors = _infer_target_sectors(interests)
    
    interest_sector_confidence = 0.0
    if target_sectors:
        # Check if company sector matches any target sector
        company_sector_lower = company_sector.lower()
        
        # Check specializations first (most specific match)
        company_specializations = company_info.get('specializations', [])
        specialization_matches = 0
        for interest in interests:
            interest_lower = interest.lower()
            for spec in company_specializations:
                spec_lower = spec.lower()
                # Exact match in specialization
                if interest_lower == spec_lower or (interest_lower in spec_lower and len(interest_lower) > 2):
                    specialization_matches += 1
                    break
        
        if company_specializations and interests:
            specialization_ratio = specialization_matches / len(interests)
            interest_sector_confidence = min(0.85 + (specialization_ratio * 0.15), 1.0)  # 0.85-1.0 range
        
        # Check sector match
        for target_sector in target_sectors:
            target_sector_lower = target_sector.lower()
            
            # Exact or very close match
            if target_sector_lower in company_sector_lower or company_sector_lower in target_sector_lower:
                interest_sector_confidence = max(interest_sector_confidence, 0.88)  # High confidence for exact match
                break
            # Partial match (check for key words)
            elif any(word in company_sector_lower for word in target_sector_lower.split() if len(word) > 3):
                interest_sector_confidence = max(interest_sector_confidence, 0.75)
        
        # If no sector match but specialization match exists, use that
        if interest_sector_confidence == 0.0 and specialization_matches > 0:
            interest_sector_confidence = 0.80
    
    confidence_components.append(('interest_sector', interest_sector_confidence, 0.40))
    
    # 2. Skills → Company required skills matching (50% weight)
    resume_skills = resume_data.get('skills', []) if resume_data else []
    company_required_skills = company_info.get('required_skills', [])
    
    skills_confidence = 0.0
    if resume_skills and company_required_skills:
        matched_skills = 0
        exact_matches = 0
        resume_skills_lower = [s.lower().strip() for s in resume_skills]
        company_skills_lower = [s.lower().strip() for s in company_required_skills]
        
        # Exact matches (higher weight)
        for skill in resume_skills_lower:
            if skill in company_skills_lower:
                matched_skills += 1.0
                exact_matches += 1
            else:
                # Partial matches (check if skill contains or is contained in company skill)
                for company_skill in company_skills_lower:
                    if skill in company_skill or company_skill in skill:
                        matched_skills += 0.6  # Partial match gets lower weight
                        break
        
        # Calculate confidence based on match ratio
        # Higher confidence for more matches
        if company_required_skills:
            match_ratio = matched_skills / len(company_required_skills)
            # Scale to 0.75-0.95 range for good matches, 0.95+ for excellent
            if match_ratio >= 0.8:
                skills_confidence = 0.78 + (match_ratio - 0.8) * 0.85  # 0.78-0.95 range
            elif match_ratio >= 0.5:
                skills_confidence = 0.65 + (match_ratio - 0.5) * 0.43  # 0.65-0.78 range
            else:
                skills_confidence = match_ratio * 1.3  # 0.0-0.65 range
            skills_confidence = min(skills_confidence, 1.0)
        else:
            skills_confidence = 0.0
    elif not resume_skills and company_required_skills:
        # No skills provided, lower confidence
        skills_confidence = 0.25
    elif resume_skills and not company_required_skills:
        # Company doesn't specify skills, moderate confidence based on interest match
        skills_confidence = 0.50
    
    confidence_components.append(('skills_match', skills_confidence, 0.50))
    
    # 3. Interest → Company specializations matching (10% weight)
    company_specializations = company_info.get('specializations', [])
    specialization_confidence = 0.0
    if company_specializations:
        matched_specializations = 0
        for interest in interests:
            interest_lower = interest.lower()
            for spec in company_specializations:
                spec_lower = spec.lower()
                if interest_lower in spec_lower or spec_lower in interest_lower:
                    matched_specializations += 1
                    break
        
        specialization_confidence = min(matched_specializations / len(interests) if interests else 0, 1.0)
    
    confidence_components.append(('specialization_match', specialization_confidence, 0.10))
    
    # Calculate weighted average confidence
    total_confidence = sum(conf * weight for _, conf, weight in confidence_components)
    total_weight = sum(weight for _, _, weight in confidence_components)
    
    final_confidence = total_confidence / total_weight if total_weight > 0 else 0.0
    
    # Round to 2 decimal places (e.g., 0.88, 0.82)
    return round(final_confidence, 2)


def _score_company(company: str, interests: List[str], resume_data: Dict = None) -> int:
    """Enhanced company scoring using ML engine and company database"""
    try:
        # Use advanced ML engine for scoring
        if resume_data:
            score = ml_engine.calculate_advanced_match_score(resume_data, company, interests)
        else:
            # Fallback to basic scoring for interests-only matching
            score = _basic_company_score(company, interests)
        
        return int(score)
    except Exception as e:
        print(f"Error in advanced scoring: {e}")
        # Fallback to basic scoring
        return _basic_company_score(company, interests)

def _basic_company_score(company: str, interests: List[str]) -> int:
    """Basic company scoring fallback"""
    text = company.lower()
    sector = _company_sector(company)
    target_sectors = _infer_target_sectors(interests)
    score = 0
    
    # Enhanced scoring algorithm
    # 1. Sector match (highest priority)
    if sector in target_sectors:
        score += 70  # Increased from 60
    
    # 2. Company name keyword matching with weighted scoring
    for term in interests:
        t = term.lower()
        if t in text:
            # Exact match gets higher score
            score += 25
        elif any(word in text for word in t.split()):
            # Partial match gets moderate score
            score += 12
        # Additional scoring for tech companies with tech interests
        # Note: Only check for exact company name matches, not substrings
        # This prevents false matches (e.g., "Google Ads" matching "Google")
        tech_companies_exact = ["microsoft", "google", "amazon", "meta", "adobe", "oracle", "salesforce"]
        if any(tech_interest in t for tech_interest in ["ai-ml", "data science", "web development", "cloud", "devops"]):
            # Only match if the company name exactly equals or starts with the tech company name
            if any(text == tc or text.startswith(tc + " ") for tc in tech_companies_exact):
                score += 15
    
    # 3. Company size and reputation bonus
    # Note: Only check for exact company name matches, not substrings
    premium_companies_exact = ["microsoft", "google", "amazon", "meta", "apple", "netflix", "uber", "spotify"]
    if any(text == pc or text.startswith(pc + " ") for pc in premium_companies_exact):
        score += 10
    elif any(established_company in text for established_company in ["tcs", "infosys", "wipro", "hcl", "accenture", "cognizant"]):
        score += 8
    
    # 4. Startup/Innovation bonus for certain interests
    if any(startup_interest in interests for startup_interest in ["ai-ml", "data science", "blockchain", "fintech"]) and any(startup_company in text for startup_company in ["freshworks", "zoho", "postman", "razorpay", "phonepe", "cred"]):
        score += 12
    
    # 5. Creative interest boosts creative companies
    if any(d in " ".join(interests) for d in ["product design", "ui/ux", "ux", "ui", "design"]):
        if any(brand in text for brand in ["figma", "canva", "adobe", "sketch", "invision", "framer", "notion", "miro"]):
            score += 18
    
    # 6. Video editing interest boosts video/creative companies
    if any(d in " ".join(interests) for d in ["video editing", "video", "editing", "premiere", "after effects", "film", "cinematography", "animation"]):
        if any(brand in text for brand in ["adobe", "apple", "netflix", "youtube", "spotify", "canva", "figma", "notion", "miro"]):
            score += 20
    
    # 7. Content creation interest boosts content companies
    if any(d in " ".join(interests) for d in ["content creation", "content", "social media", "youtube", "instagram", "tiktok", "blogging", "marketing"]):
        if any(brand in text for brand in ["netflix", "youtube", "spotify", "instagram", "tiktok", "facebook", "meta", "twitter", "linkedin", "snapchat"]):
            score += 20
    
    # 8. Gaming interest boosts gaming companies
    if any(d in " ".join(interests) for d in ["gaming", "game development", "unity", "unreal", "game design", "game art", "3d modeling", "animation"]):
        # Only match exact company names, not substrings
        gaming_brands = ["unity", "unreal", "epic", "nvidia", "amd", "intel", "microsoft", "sony", "nintendo", "steam"]
        if any(text == gb or text.startswith(gb + " ") for gb in gaming_brands):
            score += 20

    return max(0, min(100, score))


def _select_role_for_company(company: str, sector: str, interests: List[str]) -> str:
    """Select role based on company-specific information and interests"""
    try:
        # Get company information from ML engine database
        company_info = ml_engine.company_database.get('companies', {}).get(company, {})
        
        if company_info and company_info.get('preferred_roles'):
            # Use company-specific preferred roles
            preferred_roles = company_info['preferred_roles']
            
            # Match interests with preferred roles
            desired = " ".join(interests).lower()
            
            for role in preferred_roles:
                role_lower = role.lower()
                # Check if any interest keywords match the role
                if any(interest in role_lower for interest in desired.split()):
                    return role
                # Check for specific role-interest mappings
                if any(k in desired for k in ["ai", "ml", "machine learning", "data science"]) and "ai" in role_lower:
                    return role
                if any(k in desired for k in ["design", "ui", "ux"]) and any(d in role_lower for d in ["design", "ui", "ux"]):
                    return role
                if any(k in desired for k in ["development", "programming", "coding"]) and "development" in role_lower:
                    return role
                if any(k in desired for k in ["data", "analytics"]) and "analytics" in role_lower:
                    return role
            
            # Return first preferred role if no specific match
            return preferred_roles[0]
        
        # Fallback to sector-based role selection
        return _select_role_for_sector(sector, interests)
        
    except Exception as e:
        print(f"Error in company-specific role selection: {e}")
        return _select_role_for_sector(sector, interests)

def _select_role_for_sector(sector: str, interests: List[str]) -> str:
    """Fallback role selection based on sector and interests"""
    desired = " ".join(interests).lower()
    
    # Creative and design roles
    if any(k in desired for k in ["video editing", "video", "editing", "premiere", "after effects", "final cut", "davinci", "resolve", "film", "cinematography", "motion graphics", "animation", "post production"]):
        return "Video Editing Intern"
    if any(k in desired for k in ["graphic design", "photoshop", "illustrator", "indesign", "canva", "visual design", "branding", "logo", "typography", "layout"]):
        return "Graphic Design Intern"
    if any(k in desired for k in ["content creation", "content", "social media", "youtube", "instagram", "tiktok", "blogging", "writing", "copywriting", "marketing"]):
        return "Content Creation Intern"
    if any(k in desired for k in ["photography", "photo", "camera", "lightroom", "portrait", "landscape", "wedding", "fashion", "commercial"]):
        return "Photography Intern"
    if any(k in desired for k in ["music production", "music", "audio", "sound", "mixing", "mastering", "recording", "studio", "pro tools", "ableton", "logic"]):
        return "Music Production Intern"
    if any(k in desired for k in ["gaming", "game development", "unity", "unreal", "game design", "level design", "game art", "3d modeling", "animation", "game programming"]):
        return "Game Development Intern"
    if any(k in desired for k in ["product design", "ui/ux", "ux", "ui", "design", "wireframe", "prototype", "figma", "sketch", "invision", "framer", "adobe xd", "adobe"]):
        if "Technology" in sector:
            return "UI/UX Design Intern"
        if "E-commerce" in sector:
            return "Product Design Intern"
        if "Fintech" in sector:
            return "UX Research Intern"
    
    # Technical roles
    if "product management" in desired:
        return "Product Management Intern"
    if any(k in desired for k in ["ai-ml", "machine learning", "artificial intelligence", "data science", "ml", "neural", "deep learning"]):
        return "AI/ML Intern"
    if any(k in desired for k in ["cybersecurity", "security", "penetration", "vulnerability", "threat"]):
        return "Cybersecurity Intern"
    if any(k in desired for k in ["devops", "cloud", "aws", "azure", "gcp", "kubernetes", "docker"]):
        return "DevOps Intern"
    if any(k in desired for k in ["web development", "react", "javascript", "typescript", "node", "frontend", "backend", "full stack"]):
        return "Software Development Intern"
    
    # Sector-based fallbacks
    if "Technology" in sector:
        return "Software Development Intern"
    if "Fintech" in sector:
        return "Data Analytics Intern"
    if "E-commerce" in sector:
        return "Digital Marketing Intern"
    if "Automotive" in sector:
        return "Quality Control Intern"
    if "Energy" in sector:
        return "Sustainability Intern"
    if "Healthcare" in sector:
        return "Research Intern"
    if "Consulting" in sector:
        return "Business Analysis Intern"
    return "Intern"


def _make_recommendation(company: str, confidence_score: float, location_hint: Optional[str], interests: List[str], resume_data: Dict = None) -> Recommendation:
    import random
    
    # Get company info from database
    company_info = ml_engine.company_database.get('companies', {}).get(company, {})
    sector = company_info.get('sector', _company_sector(company))
    
    # Select role based on company-specific information and interests
    role = _select_role_for_company(company, sector, interests)
    job_type: Literal["internship", "full-time", "part-time"] = "internship"
    location = "Remote"  # Always set to Remote, not parsed from resume or location_hint
    
    # Use company-specific data from database, fallback to sector defaults
    if company_info:
        skills = company_info.get('required_skills', [])[:6]
        # Use preferred roles as requirements context
        preferred_roles = company_info.get('preferred_roles', [])
        requirements = [
            f"Interest in {role.lower()}" for role in preferred_roles[:3]
        ] if preferred_roles else ["Currently enrolled in a degree program", "Eager to learn"]
        
        # Generate benefits based on company culture and focus
        culture = company_info.get('company_culture', '')
        focus = company_info.get('internship_focus', '')
        benefits = []
        if culture:
            benefits.append(f"Experience {culture.lower()}")
        if focus:
            benefits.append(f"Work on {focus.lower()}")
        benefits.extend(["Mentorship", "Flexible hours", "Learning opportunities"])
        benefits = benefits[:6]
    else:
        # Fallback to sector defaults
        sector_details = SECTOR_TO_DETAILS.get(sector, {
            "roles": ["Intern"],
            "skills": ["Communication", "Problem Solving", "Teamwork"],
            "requirements": ["Currently enrolled in a degree program", "Eager to learn"],
            "benefits": ["Mentorship", "Flexible hours"]
        })
        skills = sector_details["skills"][:6]
        requirements = sector_details["requirements"][:5]
        benefits = sector_details["benefits"][:6]
    
    apply_url = None
    rec_id = f"{abs(hash(company)) % 10_000_000}"
    
    # Enhanced description based on company database info
    if company_info:
        company_desc = company_info.get('description', '')
        if company_desc:
            description = f"{company_desc} Join as a {role} and gain hands-on experience while contributing to real-world projects."
        else:
            # Fallback to sector-based description
            if "Technology" in sector:
                description = f"Join {company} as a {role} and work on cutting-edge technology projects. Gain hands-on experience with modern development tools and methodologies while contributing to real-world solutions."
            elif "Finance" in sector:
                description = f"Explore the world of finance and technology at {company} as a {role}. Work on innovative financial products and gain insights into digital banking and fintech solutions."
            else:
                description = f"Opportunity at {company} as a {role}. Contribute to projects and learn from industry professionals."
    else:
        # Fallback to sector-based description
        if "Technology" in sector:
            description = f"Join {company} as a {role} and work on cutting-edge technology projects. Gain hands-on experience with modern development tools and methodologies while contributing to real-world solutions."
        elif "Finance" in sector:
            description = f"Explore the world of finance and technology at {company} as a {role}. Work on innovative financial products and gain insights into digital banking and fintech solutions."
        else:
            description = f"Opportunity at {company} as a {role}. Contribute to projects and learn from industry professionals."

    return Recommendation(
        id=rec_id,
        company=company,
        sector=sector,
        role=role,
        description=description,
        type=job_type,
        location=location,
        skills=skills,
        requirements=requirements,
        benefits=benefits,
        matchScore=confidence_score,
        applyUrl=apply_url,
    )


@app.post("/recommend")
def recommend(payload: Union[InterestsPayload, ResumePayload]):
    try:
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

        # Create resume data structure for confidence calculation
        resume_data = {
            'skills': payload.skills if hasattr(payload, 'skills') else [],
            'interests': interests,
            'experience': payload.experience if hasattr(payload, 'experience') else [],
            'projects': payload.projects if hasattr(payload, 'projects') else [],
            'text': ' '.join(interests + (payload.skills if hasattr(payload, 'skills') else [])),
            'location': payload.location if hasattr(payload, 'location') else None
        }

        # Get all companies from company_database.json only
        try:
            companies_in_db = list(ml_engine.company_database.get('companies', {}).keys())
        except Exception as e:
            print(f"Error accessing company database: {e}")
            raise HTTPException(status_code=500, detail=f"Error loading company database: {str(e)}")
        
        if not companies_in_db:
            raise HTTPException(status_code=500, detail="No companies found in database")

        # Calculate confidence scores for all companies
        scored = []
        for company_name in companies_in_db:
            try:
                confidence = _calculate_confidence_score(company_name, interests, resume_data)
                if confidence > 0:  # Only include companies with some confidence
                    scored.append((company_name, confidence))
            except Exception as e:
                print(f"Error calculating confidence for {company_name}: {e}")
                continue  # Skip this company and continue with others

        # Sort by confidence desc, then name
        scored.sort(key=lambda x: (-x[1], x[0]))

        # Select top recommendations based on confidence thresholds
        high_confidence = [s for s in scored if s[1] >= 0.75]  # High confidence (0.75+)
        medium_confidence = [s for s in scored if 0.50 <= s[1] < 0.75]  # Medium confidence (0.50-0.74)
        low_confidence = [s for s in scored if 0.25 <= s[1] < 0.50]  # Low confidence (0.25-0.49)
        
        selected = []
        
        # Prioritize high-confidence matches
        if high_confidence:
            selected.extend(high_confidence[:2])  # Take up to 2 high-confidence matches
        
        # Add medium-confidence matches if we need more
        if len(selected) < 3 and medium_confidence:
            remaining_slots = 3 - len(selected)
            selected.extend(medium_confidence[:remaining_slots])
        
        # Add low-confidence matches if we still need more
        if len(selected) < 3 and low_confidence:
            remaining_slots = 3 - len(selected)
            selected.extend(low_confidence[:remaining_slots])
        
        # Fallback to top companies by confidence if nothing scored well
        if not selected and scored:
            selected = scored[:3]
        
        # Ensure we have exactly 3 recommendations (or fewer if not enough companies)
        if len(selected) < 3 and len(scored) > len(selected):
            remaining_slots = 3 - len(selected)
            fallback_companies = [s for s in scored if s[0] not in [sel[0] for sel in selected]]
            selected.extend(fallback_companies[:remaining_slots])

        # Create recommendations with confidence scores
        recommendations = []
        for company_name, confidence in selected:
            try:
                rec = _make_recommendation(company_name, confidence, location, interests, resume_data)
                recommendations.append(rec)
            except Exception as e:
                print(f"Error creating recommendation for {company_name}: {e}")
                continue  # Skip this recommendation and continue with others

        if not recommendations:
            raise HTTPException(status_code=500, detail="Failed to generate any recommendations. Please try again.")

        return {"recommendations": [r.dict() for r in recommendations]}
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Unexpected error in /recommend endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


