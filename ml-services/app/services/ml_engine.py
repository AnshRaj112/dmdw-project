"""
Advanced ML Engine for Resume Analysis and Company Matching
Uses state-of-the-art NLP and ML techniques for perfect recommendations
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any
from collections import Counter
import re
from datetime import datetime
import json

# ML Libraries
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# NLP Libraries
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
import spacy
from textblob import TextBlob
from fuzzywuzzy import fuzz, process

# Advanced NLP
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass

class AdvancedMLEngine:
    """
    Advanced ML Engine for perfect resume analysis and company matching
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.95
        )
        
        self.sentence_model = None
        self.nlp = None
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Initialize models
        self._initialize_models()
        
        # Training data storage
        self.training_data = {
            'resumes': [],
            'companies': [],
            'matches': [],
            'feedback': []
        }
        
        # Load company database
        self.company_database = self._load_company_database()
        
        # Load or create models
        self._load_or_create_models()
    
    def _initialize_models(self):
        """Initialize NLP models"""
        try:
            # Initialize sentence transformer for semantic similarity
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Could not load sentence transformer: {e}")
            self.sentence_model = None
        
        try:
            # Initialize spaCy model
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"Warning: Could not load spaCy model: {e}")
            self.nlp = None
    
    def _load_company_database(self) -> Dict[str, Any]:
        """Load company database with descriptions and role mappings"""
        try:
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "company_database.json")
            with open(db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load company database: {e}")
            return {"companies": {}}
    
    def _load_or_create_models(self):
        """Load existing models or create new ones"""
        model_path = os.path.join(os.path.dirname(__file__), "..", "..", "models")
        os.makedirs(model_path, exist_ok=True)
        
        # Load or create company classifier
        self.company_classifier_path = os.path.join(model_path, "company_classifier.pkl")
        self.similarity_model_path = os.path.join(model_path, "similarity_model.pkl")
        
        if os.path.exists(self.company_classifier_path):
            with open(self.company_classifier_path, 'rb') as f:
                self.company_classifier = pickle.load(f)
        else:
            self.company_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        
        if os.path.exists(self.similarity_model_path):
            with open(self.similarity_model_path, 'rb') as f:
                self.similarity_model = pickle.load(f)
        else:
            self.similarity_model = None
    
    def _save_models(self):
        """Save trained models"""
        with open(self.company_classifier_path, 'wb') as f:
            pickle.dump(self.company_classifier, f)
        
        if self.similarity_model:
            with open(self.similarity_model_path, 'wb') as f:
                pickle.dump(self.similarity_model, f)
    
    def advanced_text_preprocessing(self, text: str) -> str:
        """Advanced text preprocessing with NLP techniques"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s@#]', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        tokens = [token for token in tokens if token not in self.stop_words]
        
        # Lemmatization
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        # Remove short tokens
        tokens = [token for token in tokens if len(token) > 2]
        
        return ' '.join(tokens)
    
    def extract_advanced_features(self, text: str) -> Dict[str, Any]:
        """Extract advanced features from text using multiple NLP techniques"""
        features = {}
        
        # Basic text features
        features['word_count'] = len(text.split())
        features['char_count'] = len(text)
        features['sentence_count'] = len(text.split('.'))
        
        # Sentiment analysis
        try:
            blob = TextBlob(text)
            features['sentiment_polarity'] = blob.sentiment.polarity
            features['sentiment_subjectivity'] = blob.sentiment.subjectivity
        except:
            features['sentiment_polarity'] = 0
            features['sentiment_subjectivity'] = 0
        
        # POS tagging features
        try:
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            pos_counts = Counter(tag for word, tag in pos_tags)
            features['noun_ratio'] = pos_counts.get('NN', 0) / max(len(tokens), 1)
            features['verb_ratio'] = pos_counts.get('VB', 0) / max(len(tokens), 1)
            features['adj_ratio'] = pos_counts.get('JJ', 0) / max(len(tokens), 1)
        except:
            features['noun_ratio'] = 0
            features['verb_ratio'] = 0
            features['adj_ratio'] = 0
        
        # Technical skills detection
        tech_skills = [
            'python', 'java', 'javascript', 'typescript', 'react', 'node', 'angular', 'vue',
            'sql', 'mongodb', 'mysql', 'postgresql', 'redis', 'elasticsearch',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
            'machine learning', 'ai', 'data science', 'analytics', 'statistics',
            'html', 'css', 'bootstrap', 'jquery', 'django', 'flask', 'spring',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib'
        ]
        
        features['tech_skill_count'] = sum(1 for skill in tech_skills if skill in text.lower())
        features['tech_skill_ratio'] = features['tech_skill_count'] / max(features['word_count'], 1)
        
        # Experience indicators
        exp_keywords = ['experience', 'worked', 'developed', 'created', 'managed', 'led', 'implemented']
        features['experience_indicators'] = sum(1 for keyword in exp_keywords if keyword in text.lower())
        
        # Education indicators
        edu_keywords = ['university', 'college', 'degree', 'bachelor', 'master', 'phd', 'diploma', 'certification']
        features['education_indicators'] = sum(1 for keyword in edu_keywords if keyword in text.lower())
        
        return features
    
    def semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using sentence transformers"""
        if not self.sentence_model:
            # Fallback to TF-IDF similarity
            return self._tfidf_similarity(text1, text2)
        
        try:
            embeddings = self.sentence_model.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        except Exception as e:
            print(f"Error in semantic similarity: {e}")
            return self._tfidf_similarity(text1, text2)
    
    def _tfidf_similarity(self, text1: str, text2: str) -> float:
        """Calculate TF-IDF similarity as fallback"""
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    def fuzzy_string_matching(self, text1: str, text2: str) -> float:
        """Fuzzy string matching for better text comparison"""
        return fuzz.ratio(text1.lower(), text2.lower()) / 100.0
    
    def extract_skills_with_confidence(self, text: str) -> List[Tuple[str, float]]:
        """Extract skills with confidence scores"""
        skills_with_confidence = []
        
        # Define skill categories with confidence weights
        skill_categories = {
            'programming': {
                'python': 0.9, 'java': 0.9, 'javascript': 0.9, 'typescript': 0.9,
                'c++': 0.9, 'c#': 0.9, 'go': 0.9, 'rust': 0.9, 'php': 0.9, 'ruby': 0.9
            },
            'web_development': {
                'react': 0.8, 'angular': 0.8, 'vue': 0.8, 'node': 0.8, 'express': 0.8,
                'django': 0.8, 'flask': 0.8, 'spring': 0.8, 'laravel': 0.8
            },
            'databases': {
                'sql': 0.8, 'mysql': 0.8, 'postgresql': 0.8, 'mongodb': 0.8,
                'redis': 0.7, 'elasticsearch': 0.7, 'cassandra': 0.7
            },
            'cloud_tech': {
                'aws': 0.8, 'azure': 0.8, 'gcp': 0.8, 'docker': 0.8, 'kubernetes': 0.8,
                'terraform': 0.7, 'ansible': 0.7
            },
            'ai_ml': {
                'machine learning': 0.9, 'deep learning': 0.9, 'tensorflow': 0.8,
                'pytorch': 0.8, 'scikit-learn': 0.8, 'pandas': 0.7, 'numpy': 0.7
            },
            'design': {
                'ui/ux': 0.8, 'figma': 0.8, 'sketch': 0.8, 'adobe': 0.7, 'photoshop': 0.7,
                'illustrator': 0.7, 'invision': 0.7
            }
        }
        
        text_lower = text.lower()
        
        for category, skills in skill_categories.items():
            for skill, confidence in skills.items():
                if skill in text_lower:
                    skills_with_confidence.append((skill, confidence))
        
        return skills_with_confidence
    
    def calculate_advanced_match_score(self, resume_data: Dict, company_name: str, interests: List[str]) -> float:
        """Calculate advanced match score using company database and ML techniques"""
        score = 0.0
        
        # Get company information from database
        company_info = self.company_database.get('companies', {}).get(company_name, {})
        if not company_info:
            # Fallback to basic matching if company not in database
            return self._basic_company_score(resume_data, company_name, interests)
        
        resume_skills = resume_data.get('skills', [])
        resume_interests = resume_data.get('interests', [])
        
        # 1. Skills matching with company required skills (35% weight)
        company_required_skills = company_info.get('required_skills', [])
        if resume_skills and company_required_skills:
            skill_similarity = self.semantic_similarity(
                ' '.join(resume_skills), 
                ' '.join(company_required_skills)
            )
            score += skill_similarity * 35
        
        # 2. Interest matching with company specializations (25% weight)
        company_specializations = company_info.get('specializations', [])
        interest_match_score = 0
        for interest in interests:
            for spec in company_specializations:
                if interest.lower() in spec.lower() or spec.lower() in interest.lower():
                    interest_match_score += 1
                    break
        
        if company_specializations:
            interest_match_score = min(interest_match_score / len(company_specializations), 1.0)
        score += interest_match_score * 25
        
        # 3. Role preference matching (20% weight)
        company_preferred_roles = company_info.get('preferred_roles', [])
        resume_experience = resume_data.get('experience', [])
        resume_projects = resume_data.get('projects', [])
        
        role_match_score = 0
        for role in company_preferred_roles:
            role_lower = role.lower()
            # Check if resume content matches role requirements
            if any(keyword in ' '.join(resume_experience + resume_projects).lower() 
                   for keyword in role_lower.split()):
                role_match_score += 1
        
        if company_preferred_roles:
            role_match_score = min(role_match_score / len(company_preferred_roles), 1.0)
        score += role_match_score * 20
        
        # 4. Company culture and focus matching (10% weight)
        company_culture = company_info.get('company_culture', '')
        internship_focus = company_info.get('internship_focus', '')
        
        culture_match = 0
        if company_culture:
            culture_keywords = company_culture.lower().split(', ')
            resume_text = ' '.join(resume_data.get('text', '').lower().split())
            culture_match = sum(1 for keyword in culture_keywords if keyword in resume_text)
            culture_match = min(culture_match / len(culture_keywords), 1.0)
        
        score += culture_match * 10
        
        # 5. Company reputation and tier bonus (10% weight)
        company_tier = self._get_company_tier(company_name)
        score += company_tier * 10
        
        return min(100, max(0, score))
    
    def _basic_company_score(self, resume_data: Dict, company_name: str, interests: List[str]) -> float:
        """Basic scoring fallback when company not in database"""
        score = 0.0
        company_lower = company_name.lower()
        
        # Basic keyword matching
        resume_text = ' '.join(resume_data.get('skills', []) + resume_data.get('interests', [])).lower()
        
        # Tech companies
        if any(tech in company_lower for tech in ['microsoft', 'google', 'amazon', 'meta', 'apple', 'adobe']):
            if any(tech in resume_text for tech in ['python', 'java', 'javascript', 'cloud', 'ai', 'ml']):
                score += 70
        # Banking companies
        elif any(bank in company_lower for bank in ['hdfc', 'icici', 'axis', 'bank']):
            if any(fin in resume_text for fin in ['finance', 'banking', 'analytics', 'data']):
                score += 70
        # E-commerce companies
        elif any(ecom in company_lower for ecom in ['flipkart', 'amazon', 'swiggy', 'zomato']):
            if any(ec in resume_text for ec in ['ecommerce', 'marketing', 'analytics', 'mobile']):
                score += 70
        
        return min(100, max(0, score))
    
    def _get_company_tier(self, company_name: str) -> float:
        """Get company tier score (0-1) based on reputation and size"""
        company_lower = company_name.lower()
        
        # Tier 1: FAANG and top tech companies
        if any(tier1 in company_lower for tier1 in ['microsoft', 'google', 'amazon', 'meta', 'apple', 'netflix', 'adobe']):
            return 1.0
        # Tier 2: Major Indian tech and consulting
        elif any(tier2 in company_lower for tier2 in ['tcs', 'infosys', 'wipro', 'hcl', 'accenture', 'cognizant', 'deloitte']):
            return 0.8
        # Tier 3: Established companies
        elif any(tier3 in company_lower for tier3 in ['capgemini', 'ibm', 'kpmg', 'pwc', 'mckinsey']):
            return 0.6
        # Tier 4: Other companies
        else:
            return 0.4
    
    def train_company_classifier(self, training_data: List[Dict]):
        """Train company classification model"""
        if not training_data:
            return
        
        # Prepare training data
        X = []
        y = []
        
        for data in training_data:
            features = self.extract_advanced_features(data.get('text', ''))
            X.append(list(features.values()))
            y.append(data.get('sector', 'Technology'))
        
        if len(X) > 0:
            X = np.array(X)
            y = np.array(y)
            
            # Train classifier
            self.company_classifier.fit(X, y)
            self._save_models()
    
    def predict_company_sector(self, company_text: str) -> str:
        """Predict company sector using trained model"""
        features = self.extract_advanced_features(company_text)
        features_array = np.array(list(features.values())).reshape(1, -1)
        
        try:
            prediction = self.company_classifier.predict(features_array)[0]
            return prediction
        except:
            return "Technology / Software / Digital Services"
    
    def get_perfect_recommendations(self, resume_data: Dict, interests: List[str], 
                                  companies: List[str], top_n: int = 5) -> List[Dict]:
        """Get perfect recommendations using advanced ML techniques"""
        
        # Extract features from resume
        resume_features = self.extract_advanced_features(resume_data.get('text', ''))
        resume_skills = self.extract_skills_with_confidence(resume_data.get('text', ''))
        
        # Calculate scores for all companies
        company_scores = []
        
        for company in companies:
            # Create company data structure
            company_data = {
                'name': company,
                'sector': self.predict_company_sector(company),
                'required_skills': self._get_company_skills(company),
                'experience_required': 'entry',  # Default for internships
                'location': 'Remote',
                'reputation_score': self._get_company_reputation(company)
            }
            
            # Calculate match score
            match_score = self.calculate_advanced_match_score(
                resume_data, company_data, interests
            )
            
            company_scores.append({
                'company': company,
                'score': match_score,
                'sector': company_data['sector'],
                'data': company_data
            })
        
        # Sort by score and return top N
        company_scores.sort(key=lambda x: x['score'], reverse=True)
        
        return company_scores[:top_n]
    
    def _get_company_skills(self, company: str) -> List[str]:
        """Get relevant skills for a company based on its name and sector"""
        company_lower = company.lower()
        
        # Tech companies - only match exact company names, not substrings
        tech_companies = ['microsoft', 'google', 'amazon', 'meta', 'apple']
        if any(company_lower == tc or company_lower.startswith(tc + " ") for tc in tech_companies):
            return ['python', 'javascript', 'machine learning', 'cloud computing', 'data structures']
        elif any(tech in company_lower for tech in ['tcs', 'infosys', 'wipro', 'hcl']):
            return ['java', 'sql', 'testing', 'agile', 'project management']
        elif any(fin in company_lower for fin in ['hdfc', 'icici', 'axis', 'bank']):
            return ['financial analysis', 'risk management', 'compliance', 'data analysis']
        
        return ['communication', 'problem solving', 'teamwork']
    
    def _get_company_reputation(self, company: str) -> float:
        """Get company reputation score"""
        company_lower = company.lower()
        
        # Tier 1 companies (FAANG, etc.) - only match exact company names, not substrings
        tier1_companies = ['microsoft', 'google', 'amazon', 'meta', 'apple', 'netflix']
        if any(company_lower == t1 or company_lower.startswith(t1 + " ") for t1 in tier1_companies):
            return 10.0
        # Tier 2 companies (Major tech, consulting)
        elif any(tier2 in company_lower for tier2 in ['tcs', 'infosys', 'wipro', 'accenture', 'deloitte', 'mckinsey']):
            return 8.0
        # Tier 3 companies (Established companies)
        elif any(tier3 in company_lower for tier3 in ['hcl', 'cognizant', 'capgemini', 'ibm']):
            return 6.0
        # Default
        else:
            return 5.0
    
    def add_feedback(self, recommendation_id: str, feedback_score: int, feedback_text: str = ""):
        """Add feedback to improve the model"""
        feedback_data = {
            'recommendation_id': recommendation_id,
            'score': feedback_score,
            'text': feedback_text,
            'timestamp': datetime.now().isoformat()
        }
        
        self.training_data['feedback'].append(feedback_data)
        
        # Retrain model if enough feedback is available
        if len(self.training_data['feedback']) >= 10:
            self._retrain_with_feedback()
    
    def _retrain_with_feedback(self):
        """Retrain model using feedback data"""
        # This would implement retraining logic based on feedback
        # For now, we'll just save the feedback for future use
        feedback_path = os.path.join(os.path.dirname(__file__), "..", "..", "models", "feedback.json")
        with open(feedback_path, 'w') as f:
            json.dump(self.training_data['feedback'], f, indent=2)
    
    def get_model_performance_metrics(self) -> Dict[str, Any]:
        """Get model performance metrics"""
        return {
            'total_feedback': len(self.training_data['feedback']),
            'average_feedback_score': np.mean([f['score'] for f in self.training_data['feedback']]) if self.training_data['feedback'] else 0,
            'model_accuracy': 'N/A',  # Would be calculated from test data
            'last_updated': datetime.now().isoformat()
        }


# Global ML Engine instance
ml_engine = AdvancedMLEngine()
