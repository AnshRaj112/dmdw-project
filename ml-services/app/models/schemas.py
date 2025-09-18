from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ProfileType(str, Enum):
    RESUME = "resume"
    INTERESTS = "interests"

class RecommendationRequest(BaseModel):
    skills: List[str] = Field(..., description="List of skills")
    interests: List[str] = Field(..., description="List of interests")
    experience: List[str] = Field(..., description="List of experience items")
    projects: List[str] = Field(..., description="List of projects")
    education: Optional[List[str]] = Field(None, description="List of education items")
    location: Optional[str] = Field(None, description="Preferred location")
    type: ProfileType = Field(..., description="Type of profile (resume or interests)")

class ParsedResume(BaseModel):
    skills: List[str] = Field(..., description="Extracted skills")
    interests: List[str] = Field(..., description="Extracted interests")
    experience: List[str] = Field(..., description="Extracted experience")
    projects: List[str] = Field(..., description="Extracted projects")
    education: List[str] = Field(..., description="Extracted education")
    location: Optional[str] = Field(None, description="Extracted location")

class Company(BaseModel):
    id: str = Field(..., description="Company ID")
    name: str = Field(..., description="Company name")
    description: str = Field(..., description="Company description")
    website: str = Field(..., description="Company website")
    hiring_interests: List[str] = Field(..., description="Company hiring interests")
    locations: List[str] = Field(..., description="Company locations")
    company_size: str = Field(..., description="Company size")
    industry: List[str] = Field(..., description="Company industry")

class Position(BaseModel):
    id: str = Field(..., description="Position ID")
    title: str = Field(..., description="Position title")
    description: str = Field(..., description="Position description")
    type: str = Field(..., description="Position type (internship, full-time, part-time)")
    location: str = Field(..., description="Position location")
    skills: List[str] = Field(..., description="Required skills")
    requirements: List[str] = Field(..., description="Position requirements")
    benefits: List[str] = Field(..., description="Position benefits")
    apply_url: Optional[str] = Field(None, description="Application URL")

class Recommendation(BaseModel):
    id: str = Field(..., description="Recommendation ID")
    company: str = Field(..., description="Company name")
    role: str = Field(..., description="Role title")
    description: str = Field(..., description="Role description")
    match_score: float = Field(..., description="Match score (0-100)")
    skills: List[str] = Field(..., description="Required skills")
    location: str = Field(..., description="Location")
    type: str = Field(..., description="Position type")
    apply_url: Optional[str] = Field(None, description="Application URL")
    requirements: List[str] = Field(..., description="Requirements")
    benefits: List[str] = Field(..., description="Benefits")

class RecommendationResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message")
    recommendations: List[Recommendation] = Field(..., description="List of recommendations")
