from typing import List, Dict, Any
import re
from loguru import logger

from models.schemas import Recommendation, Company, Position
from services.company_matcher import CompanyMatcher

class SimpleRecommendationEngine:
    def __init__(self):
        self.company_matcher = CompanyMatcher()
        
        # Load company data
        self.companies = self.company_matcher.get_all_companies()
        self.positions = self._get_all_positions()

    def _get_all_positions(self) -> List[Position]:
        """Get all available positions from companies"""
        positions = []
        for company in self.companies:
            if hasattr(company, 'open_positions'):
                for position in company.open_positions:
                    position.company_id = company.id
                    position.company_name = company.name
                    positions.append(position)
        return positions

    def generate_recommendations(
        self,
        skills: List[str],
        interests: List[str],
        experience: List[str],
        projects: List[str],
        education: List[str] = None,
        location: str = None,
        profile_type: str = "resume"
    ) -> List[Recommendation]:
        """
        Generate personalized recommendations based on user profile
        """
        try:
            # Create user profile text
            user_profile = self._create_user_profile(
                skills, interests, experience, projects, education
            )
            
            # Calculate similarity scores
            similarities = self._calculate_similarities(user_profile)
            
            # Get top recommendations
            recommendations = self._get_top_recommendations(
                similarities, location, top_k=3
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def _create_user_profile(
        self,
        skills: List[str],
        interests: List[str],
        experience: List[str],
        projects: List[str],
        education: List[str] = None
    ) -> str:
        """Create a text profile from user data"""
        profile_parts = []
        
        # Add skills
        if skills:
            profile_parts.extend(skills)
        
        # Add interests
        if interests:
            profile_parts.extend(interests)
        
        # Add experience (summarized)
        if experience:
            # Take first 3 experiences and extract key terms
            for exp in experience[:3]:
                # Extract key terms from experience
                key_terms = self._extract_key_terms(exp)
                profile_parts.extend(key_terms)
        
        # Add projects (summarized)
        if projects:
            for project in projects[:3]:
                key_terms = self._extract_key_terms(project)
                profile_parts.extend(key_terms)
        
        # Add education
        if education:
            for edu in education[:2]:
                key_terms = self._extract_key_terms(edu)
                profile_parts.extend(key_terms)
        
        return ' '.join(profile_parts)

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text"""
        # Simple keyword extraction
        words = text.lower().split()
        # Filter out common words and keep technical terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        key_terms = [word for word in words if len(word) > 3 and word not in stop_words]
        return key_terms[:5]  # Limit to top 5 terms

    def _calculate_similarities(self, user_profile: str) -> List[float]:
        """Calculate similarity scores between user profile and positions"""
        similarities = []
        user_terms = set(user_profile.lower().split())
        
        for position in self.positions:
            # Combine position information for matching
            position_text = f"{position.title} {position.description} {' '.join(position.skills)}"
            position_terms = set(position_text.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(user_terms & position_terms)
            union = len(user_terms | position_terms)
            
            if union > 0:
                similarity = intersection / union
            else:
                similarity = 0.0
            
            # Boost score for skill matches
            skill_matches = self._calculate_skill_match_score(
                user_profile.lower().split(), position.skills
            )
            similarity += skill_matches * 0.3  # 30% boost for skill matches
            
            similarities.append(min(1.0, similarity))  # Cap at 1.0
        
        return similarities

    def _get_top_recommendations(
        self,
        similarities: List[float],
        location: str = None,
        top_k: int = 3
    ) -> List[Recommendation]:
        """Get top recommendations based on similarity scores"""
        if not similarities or not self.positions:
            return []
        
        # Create list of (index, similarity) tuples
        indexed_similarities = [(i, sim) for i, sim in enumerate(similarities)]
        
        # Sort by similarity score (descending)
        indexed_similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Filter by location if specified
        if location:
            filtered_indices = []
            for idx, sim in indexed_similarities:
                position = self.positions[idx]
                if (location.lower() in position.location.lower() or 
                    'remote' in position.location.lower()):
                    filtered_indices.append((idx, sim))
            indexed_similarities = filtered_indices
        
        # Get top recommendations
        recommendations = []
        for i, (idx, similarity) in enumerate(indexed_similarities[:top_k]):
            position = self.positions[idx]
            
            # Calculate match score (0-100)
            match_score = min(100, max(0, similarity * 100))
            
            # Create recommendation
            recommendation = Recommendation(
                id=f"rec_{i+1}",
                company=position.company_name,
                role=position.title,
                description=position.description,
                match_score=round(match_score, 1),
                skills=position.skills,
                location=position.location,
                type=position.type,
                apply_url=position.apply_url,
                requirements=position.requirements,
                benefits=position.benefits
            )
            
            recommendations.append(recommendation)
        
        return recommendations

    def _calculate_skill_match_score(
        self,
        user_terms: List[str],
        required_skills: List[str]
    ) -> float:
        """Calculate skill match score between user and position"""
        if not user_terms or not required_skills:
            return 0.0
        
        user_skills_lower = [term.lower() for term in user_terms]
        required_skills_lower = [skill.lower() for skill in required_skills]
        
        # Calculate intersection
        matches = set(user_skills_lower) & set(required_skills_lower)
        
        # Calculate match percentage
        match_score = len(matches) / len(required_skills_lower)
        
        return match_score
