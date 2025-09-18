import re
import io
from typing import List, Dict, Any
import PyPDF2
import pdfplumber
from docx import Document
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from loguru import logger

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    logger.warning("Failed to download NLTK data")

class ResumeParser:
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize stopwords
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set()
        
        # Skills and interests keywords
        self.skills_keywords = {
            'programming': ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
            'web_dev': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring'],
            'mobile_dev': ['ios', 'android', 'react native', 'flutter', 'xamarin', 'ionic'],
            'data_science': ['python', 'r', 'sql', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'matplotlib'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra'],
            'tools': ['git', 'github', 'gitlab', 'jira', 'confluence', 'slack', 'figma', 'sketch']
        }
        
        self.interests_keywords = {
            'technology': ['technology', 'tech', 'innovation', 'digital', 'software', 'hardware'],
            'ai_ml': ['artificial intelligence', 'machine learning', 'ai', 'ml', 'deep learning', 'neural networks'],
            'data': ['data science', 'data analysis', 'big data', 'analytics', 'statistics'],
            'web': ['web development', 'frontend', 'backend', 'full stack', 'web design'],
            'mobile': ['mobile development', 'ios', 'android', 'mobile apps'],
            'design': ['ui', 'ux', 'user interface', 'user experience', 'design', 'graphic design'],
            'business': ['business', 'marketing', 'sales', 'finance', 'management', 'strategy'],
            'research': ['research', 'analysis', 'investigation', 'study', 'academic']
        }

    def parse_resume(self, content: bytes, file_type: str) -> Dict[str, Any]:
        """
        Parse resume content and extract structured information
        """
        try:
            # Extract text based on file type
            text = self._extract_text(content, file_type)
            
            if not text:
                raise ValueError("Could not extract text from file")
            
            # Clean and preprocess text
            cleaned_text = self._clean_text(text)
            
            # Extract different sections
            skills = self._extract_skills(cleaned_text)
            interests = self._extract_interests(cleaned_text)
            experience = self._extract_experience(cleaned_text)
            projects = self._extract_projects(cleaned_text)
            education = self._extract_education(cleaned_text)
            location = self._extract_location(cleaned_text)
            
            return {
                'skills': skills,
                'interests': interests,
                'experience': experience,
                'projects': projects,
                'education': education,
                'location': location
            }
            
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            raise

    def _extract_text(self, content: bytes, file_type: str) -> str:
        """Extract text from different file formats"""
        try:
            if file_type == "application/pdf":
                return self._extract_from_pdf(content)
            elif file_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                return self._extract_from_docx(content)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            raise

    def _extract_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except:
            # Fallback to PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text

    def _extract_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX"""
        doc = Document(io.BytesIO(content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep alphanumeric and basic punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', ' ', text)
        return text.strip()

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        skills = set()
        text_lower = text.lower()
        
        # Extract skills based on keywords
        for category, skill_list in self.skills_keywords.items():
            for skill in skill_list:
                if skill.lower() in text_lower:
                    skills.add(skill.title())
        
        # Use NLP to extract additional skills
        if self.nlp:
            doc = self.nlp(text)
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN'] and 
                    len(token.text) > 2 and 
                    token.text.lower() not in self.stop_words and
                    not token.is_punct):
                    # Check if it's likely a technical skill
                    if any(keyword in token.text.lower() for keyword in 
                          ['programming', 'development', 'design', 'analysis', 'management']):
                        skills.add(token.text.title())
        
        return list(skills)

    def _extract_interests(self, text: str) -> List[str]:
        """Extract interests from resume text"""
        interests = set()
        text_lower = text.lower()
        
        # Extract interests based on keywords
        for category, interest_list in self.interests_keywords.items():
            for interest in interest_list:
                if interest.lower() in text_lower:
                    interests.add(interest.title())
        
        # Look for interest sections
        interest_patterns = [
            r'interests?[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)',
            r'hobbies?[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)',
            r'passion[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in interest_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Split by common separators
                items = re.split(r'[,;•\n]', match)
                for item in items:
                    item = item.strip()
                    if len(item) > 2:
                        interests.add(item.title())
        
        return list(interests)

    def _extract_experience(self, text: str) -> List[str]:
        """Extract work experience from resume text"""
        experience = []
        
        # Look for experience sections
        exp_patterns = [
            r'experience[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)',
            r'work\s+history[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)',
            r'employment[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)',
            r'professional\s+experience[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Split by job entries (look for dates or company names)
                entries = re.split(r'(?=\d{4}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))', match)
                for entry in entries:
                    entry = entry.strip()
                    if len(entry) > 10:  # Filter out very short entries
                        experience.append(entry)
        
        return experience[:5]  # Limit to top 5 experiences

    def _extract_projects(self, text: str) -> List[str]:
        """Extract projects from resume text"""
        projects = []
        
        # Look for project sections
        project_patterns = [
            r'projects?[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)',
            r'portfolio[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)',
            r'key\s+projects?[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Split by project entries
                entries = re.split(r'(?=\n\w|\n\d)', match)
                for entry in entries:
                    entry = entry.strip()
                    if len(entry) > 10:  # Filter out very short entries
                        projects.append(entry)
        
        return projects[:5]  # Limit to top 5 projects

    def _extract_education(self, text: str) -> List[str]:
        """Extract education from resume text"""
        education = []
        
        # Look for education sections
        edu_patterns = [
            r'education[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)',
            r'academic[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)',
            r'qualifications?[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in edu_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Split by education entries
                entries = re.split(r'(?=\n\w|\n\d)', match)
                for entry in entries:
                    entry = entry.strip()
                    if len(entry) > 5:  # Filter out very short entries
                        education.append(entry)
        
        return education[:3]  # Limit to top 3 education entries

    def _extract_location(self, text: str) -> str:
        """Extract location from resume text"""
        # Look for location patterns
        location_patterns = [
            r'location[:\s]+([^\n]+)',
            r'address[:\s]+([^\n]+)',
            r'based\s+in[:\s]+([^\n]+)',
            r'residing\s+in[:\s]+([^\n]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
