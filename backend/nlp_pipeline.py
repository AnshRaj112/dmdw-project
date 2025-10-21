import os
# NLP-based Resume to Internship Matching Pipeline
# -----------------------------------------------


# Try to use sentence-transformers for embeddings; if not available, fall back to a simple keyword-overlap matcher.
try:
    
    _HAS_SENTENCE_TRANSFORMERS = True
    _SBERT_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
except Exception:
    _HAS_SENTENCE_TRANSFORMERS = False
    _SBERT_MODEL = None

import re
def _simple_overlap_score(a, b):
    # simple token overlap score (no external libs) — returns cosine-like score
    ta = re.findall(r"\w+", a.lower())
    tb = re.findall(r"\w+", b.lower())
    sa = {}
    sb = {}
    for w in ta:
        sa[w] = sa.get(w,0)+1
    for w in tb:
        sb[w] = sb.get(w,0)+1
    # intersection size (min counts)
    inter = sum(min(sa.get(w,0), sb.get(w,0)) for w in sa.keys() & sb.keys())
    # normalize by sqrt(len_a*len_b))
    denom = (sum(sa.values())**0.5) * (sum(sb.values())**0.5)
    return inter/denom if denom>0 else 0.0

def semantic_similarity(a, b):
    """Compute similarity between two strings. Use SBERT if available, otherwise simple overlap."""
    if _HAS_SENTENCE_TRANSFORMERS and _SBERT_MODEL is not None:
        emb_a = _SBERT_MODEL.encode(a, convert_to_tensor=True)
        emb_b = _SBERT_MODEL.encode(b, convert_to_tensor=True)
        return float(util.cos_sim(emb_a, emb_b).item())
    else:
        return _simple_overlap_score(a, b)

import docx
import PyPDF2

# -------------------------
# 📂 Step 1: Resume Reader
# -------------------------
def read_resume(file_path):
    text = ""
    if file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs])
    elif file_path.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file_path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    else:
        raise ValueError("Unsupported file type. Please upload PDF or DOCX.")
    return text

# -------------------------
# 📊 Step 2: NLP Model
# -------------------------
model = _SBERT_MODEL

def match_internships(resume_text, internships):
    """Match a resume to a list of internship descriptions and print ranked results."""
    scores = []
    for idx, intern in enumerate(internships):
        # compute semantic similarity using SBERT if available, otherwise simple overlap
        score = semantic_similarity(resume_text, intern)
        scores.append((idx, score))
    results = sorted(scores, key=lambda x: x[1], reverse=True)
    print("Top Internship Recommendations:\n")
    for rank, (idx, score) in enumerate(results, start=1):
        print(f"{rank}. Internship #{idx+1} — score: {score:.4f}")
        print(f"   Description: {internships[idx][:200]}")
    return results

# -------------------------
# 🚀 Step 3: Run Example
# -------------------------

if __name__ == "__main__":
    # Use a fallback sample resume text if the sample file is missing
    resume_path = "sample_resume.pdf"   # Replace with actual file path
    if os.path.exists(resume_path):
        resume_text = read_resume(resume_path)
    else:
        resume_text = """John Doe
        Experienced in Python, machine learning, deep learning, NLP, TensorFlow, and cloud deployment.
        Worked on Kaggle projects, built REST APIs, and deployed models to AWS."""
        print("Using embedded sample resume text (no file found).\n")
    
    internships = [
        "We need a data analyst with strong Python, SQL, and Tableau skills for business insights.",
        "Looking for an ML intern with experience in NLP, Transformers, and model deployment.",
        "Internship for a web developer skilled in React, Node.js, and MongoDB."
    ]
    
    match_internships(resume_text, internships)
