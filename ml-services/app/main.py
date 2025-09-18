from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

try:
    from services.resume_parser import ResumeParser
except ImportError:
    try:
        from services.simple_resume_parser import SimpleResumeParser as ResumeParser
    except ImportError:
        from services.minimal_resume_parser import MinimalResumeParser as ResumeParser
try:
    from services.recommendation_engine import RecommendationEngine
except ImportError:
    from services.simple_recommendation_engine import SimpleRecommendationEngine as RecommendationEngine
from services.company_matcher import CompanyMatcher
from models.schemas import ParsedResume, RecommendationRequest, RecommendationResponse

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Internship Recommendation Engine",
    description="ML service for parsing resumes and generating internship recommendations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
resume_parser = ResumeParser()
recommendation_engine = RecommendationEngine()
company_matcher = CompanyMatcher()

@app.get("/")
async def root():
    return {"message": "AI Internship Recommendation Engine ML Service"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ml-service",
        "version": "1.0.0"
    }

@app.post("/parse_resume")
async def parse_resume(file: UploadFile = File(...), file_type: str = Form(...)):
    """
    Parse uploaded resume and extract skills, interests, experience, and projects
    """
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        if file_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF, DOC, and DOCX files are supported."
            )
        
        # Read file content
        content = await file.read()
        
        # Parse resume
        parsed_data = resume_parser.parse_resume(content, file_type)
        
        return {
            "success": True,
            "message": "Resume parsed successfully",
            "data": parsed_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse resume: {str(e)}"
        )

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Generate internship recommendations based on user profile
    """
    try:
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(
            skills=request.skills,
            interests=request.interests,
            experience=request.experience,
            projects=request.projects,
            education=request.education,
            location=request.location,
            profile_type=request.type
        )
        
        return RecommendationResponse(
            success=True,
            message="Recommendations generated successfully",
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

@app.get("/companies")
async def get_companies():
    """
    Get list of companies and their hiring interests
    """
    try:
        companies = company_matcher.get_all_companies()
        return {
            "success": True,
            "companies": companies
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch companies: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
