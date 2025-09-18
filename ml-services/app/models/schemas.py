from typing import List, Optional, Literal
from pydantic import BaseModel, Field


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


