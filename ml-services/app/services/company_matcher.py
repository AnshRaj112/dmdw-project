from typing import List, Dict, Any
from models.schemas import Company, Position
from loguru import logger

class CompanyMatcher:
    def __init__(self):
        self.companies = self._initialize_companies()

    def _initialize_companies(self) -> List[Company]:
        """Initialize company data with positions"""
        companies_data = [
            {
                "id": "1",
                "name": "TechCorp Solutions",
                "description": "Leading technology company specializing in AI and machine learning solutions.",
                "website": "https://techcorp.com",
                "hiring_interests": ["web-development", "data-science", "ai-ml", "cloud-computing", "programming"],
                "locations": ["San Francisco", "New York", "Remote"],
                "company_size": "large",
                "industry": ["Technology", "AI/ML"],
                "open_positions": [
                    {
                        "id": "1",
                        "title": "Software Engineering Intern",
                        "description": "Work on cutting-edge web applications using React and Node.js. You'll collaborate with senior developers to build scalable solutions and learn modern development practices.",
                        "type": "internship",
                        "location": "San Francisco",
                        "skills": ["React", "Node.js", "JavaScript", "TypeScript", "HTML", "CSS"],
                        "requirements": [
                            "Currently enrolled in CS program or related field",
                            "Basic knowledge of web development",
                            "Familiarity with JavaScript",
                            "Strong problem-solving skills"
                        ],
                        "benefits": [
                            "Mentorship program with senior developers",
                            "Flexible working hours",
                            "Competitive stipend",
                            "Free lunch and snacks"
                        ],
                        "apply_url": "https://techcorp.com/careers/internships"
                    },
                    {
                        "id": "2",
                        "title": "Data Science Intern",
                        "description": "Analyze large datasets and build machine learning models. Work with real-world data to solve business problems and gain hands-on experience with ML tools.",
                        "type": "internship",
                        "location": "Remote",
                        "skills": ["Python", "Machine Learning", "Data Analysis", "SQL", "Pandas", "Scikit-learn"],
                        "requirements": [
                            "Statistics or data science background",
                            "Python programming experience",
                            "Understanding of machine learning concepts",
                            "Experience with data analysis tools"
                        ],
                        "benefits": [
                            "Remote work flexibility",
                            "Access to cutting-edge ML tools",
                            "Project ownership opportunities",
                            "Conference attendance budget"
                        ],
                        "apply_url": "https://techcorp.com/careers/data-science"
                    }
                ]
            },
            {
                "id": "2",
                "name": "StartupXYZ",
                "description": "Fast-growing startup focused on mobile app development and user experience.",
                "website": "https://startupxyz.com",
                "hiring_interests": ["mobile-development", "ui-ux", "web-development", "product-design", "programming"],
                "locations": ["Austin", "Remote"],
                "company_size": "startup",
                "industry": ["Mobile", "Design"],
                "open_positions": [
                    {
                        "id": "3",
                        "title": "Mobile App Development Intern",
                        "description": "Build iOS and Android apps using React Native. Work closely with the design team to create beautiful, functional mobile applications.",
                        "type": "internship",
                        "location": "Austin",
                        "skills": ["React Native", "JavaScript", "iOS", "Android", "Mobile Development", "UI/UX"],
                        "requirements": [
                            "Interest in mobile development",
                            "JavaScript knowledge",
                            "Understanding of mobile app concepts",
                            "Portfolio of mobile projects preferred"
                        ],
                        "benefits": [
                            "Equity participation opportunity",
                            "Fast-paced learning environment",
                            "Direct mentorship from founders",
                            "Flexible work arrangements"
                        ],
                        "apply_url": "https://startupxyz.com/jobs"
                    }
                ]
            },
            {
                "id": "3",
                "name": "DataFlow Analytics",
                "description": "Data analytics company helping businesses make data-driven decisions.",
                "website": "https://dataflow.com",
                "hiring_interests": ["data-science", "analytics", "research", "business-strategy", "programming"],
                "locations": ["Chicago", "Boston", "Remote"],
                "company_size": "medium",
                "industry": ["Analytics", "Consulting"],
                "open_positions": [
                    {
                        "id": "4",
                        "title": "Business Analytics Intern",
                        "description": "Analyze business data and create insights for clients. Work with real client data to identify trends and opportunities.",
                        "type": "internship",
                        "location": "Chicago",
                        "skills": ["Excel", "SQL", "Tableau", "Business Analysis", "Statistics", "Data Visualization"],
                        "requirements": [
                            "Business or analytics background",
                            "Excel proficiency",
                            "Strong analytical thinking",
                            "Communication skills"
                        ],
                        "benefits": [
                            "Direct client exposure",
                            "Real-world project experience",
                            "Career development opportunities",
                            "Networking events"
                        ],
                        "apply_url": "https://dataflow.com/careers"
                    }
                ]
            },
            {
                "id": "4",
                "name": "DesignStudio Pro",
                "description": "Creative design agency specializing in UI/UX and brand design.",
                "website": "https://designstudiopro.com",
                "hiring_interests": ["ui-ux", "graphic-design", "product-design", "branding", "web-development"],
                "locations": ["Los Angeles", "Remote"],
                "company_size": "small",
                "industry": ["Design", "Creative"],
                "open_positions": [
                    {
                        "id": "5",
                        "title": "UI/UX Design Intern",
                        "description": "Create user interfaces and experiences for web and mobile applications. Work with design tools and collaborate with developers.",
                        "type": "internship",
                        "location": "Los Angeles",
                        "skills": ["Figma", "Adobe Creative Suite", "UI Design", "UX Research", "Prototyping", "User Testing"],
                        "requirements": [
                            "Design portfolio required",
                            "Familiarity with design tools",
                            "Understanding of UX principles",
                            "Creative problem-solving skills"
                        ],
                        "benefits": [
                            "Creative freedom",
                            "Portfolio building opportunities",
                            "Design tool licenses",
                            "Mentorship from senior designers"
                        ],
                        "apply_url": "https://designstudiopro.com/internships"
                    }
                ]
            },
            {
                "id": "5",
                "name": "CloudTech Solutions",
                "description": "Cloud infrastructure and DevOps company helping businesses scale their operations.",
                "website": "https://cloudtech.com",
                "hiring_interests": ["cloud-computing", "devops", "programming", "cybersecurity", "data-science"],
                "locations": ["Seattle", "Remote"],
                "company_size": "medium",
                "industry": ["Cloud", "Infrastructure"],
                "open_positions": [
                    {
                        "id": "6",
                        "title": "Cloud Engineering Intern",
                        "description": "Work with AWS, Azure, and GCP to build scalable cloud solutions. Learn infrastructure as code and automation.",
                        "type": "internship",
                        "location": "Remote",
                        "skills": ["AWS", "Azure", "Docker", "Kubernetes", "Terraform", "Python"],
                        "requirements": [
                            "Computer science background",
                            "Basic cloud knowledge",
                            "Python or similar programming language",
                            "Interest in infrastructure"
                        ],
                        "benefits": [
                            "Cloud certification support",
                            "Hands-on infrastructure projects",
                            "Remote work flexibility",
                            "Competitive compensation"
                        ],
                        "apply_url": "https://cloudtech.com/careers"
                    }
                ]
            }
        ]
        
        # Convert to Company objects
        companies = []
        for company_data in companies_data:
            positions = []
            for pos_data in company_data["open_positions"]:
                position = Position(
                    id=pos_data["id"],
                    title=pos_data["title"],
                    description=pos_data["description"],
                    type=pos_data["type"],
                    location=pos_data["location"],
                    skills=pos_data["skills"],
                    requirements=pos_data["requirements"],
                    benefits=pos_data["benefits"],
                    apply_url=pos_data.get("apply_url")
                )
                positions.append(position)
            
            company = Company(
                id=company_data["id"],
                name=company_data["name"],
                description=company_data["description"],
                website=company_data["website"],
                hiring_interests=company_data["hiring_interests"],
                locations=company_data["locations"],
                company_size=company_data["company_size"],
                industry=company_data["industry"]
            )
            # Add positions as attribute
            company.open_positions = positions
            companies.append(company)
        
        return companies

    def get_all_companies(self) -> List[Company]:
        """Get all companies"""
        return self.companies

    def get_company_by_id(self, company_id: str) -> Company:
        """Get company by ID"""
        for company in self.companies:
            if company.id == company_id:
                return company
        return None

    def search_companies(
        self,
        interests: List[str] = None,
        location: str = None,
        company_size: str = None,
        industry: str = None
    ) -> List[Company]:
        """Search companies based on criteria"""
        filtered_companies = self.companies.copy()
        
        # Filter by interests
        if interests:
            filtered_companies = [
                company for company in filtered_companies
                if any(
                    any(interest.lower() in hiring_interest.lower() 
                        for hiring_interest in company.hiring_interests)
                    for interest in interests
                )
            ]
        
        # Filter by location
        if location:
            filtered_companies = [
                company for company in filtered_companies
                if any(
                    location.lower() in company_location.lower() or
                    'remote' in company_location.lower()
                    for company_location in company.locations
                )
            ]
        
        # Filter by company size
        if company_size:
            filtered_companies = [
                company for company in filtered_companies
                if company.company_size == company_size
            ]
        
        # Filter by industry
        if industry:
            filtered_companies = [
                company for company in filtered_companies
                if industry.lower() in [ind.lower() for ind in company.industry]
            ]
        
        return filtered_companies

    def get_positions_by_company(self, company_id: str) -> List[Position]:
        """Get all positions for a specific company"""
        company = self.get_company_by_id(company_id)
        if company:
            return company.open_positions
        return []

    def get_all_positions(self) -> List[Position]:
        """Get all available positions across all companies"""
        all_positions = []
        for company in self.companies:
            all_positions.extend(company.open_positions)
        return all_positions
