export interface Interest {
  id: string;
  name: string;
  category: string;
}

export interface Recommendation {
  id: string;
  company: string;
  sector: string;
  role: string;
  description: string;
  matchScore: number;
  skills: string[];
  location: string;
  type: 'internship' | 'full-time' | 'part-time';
  applyUrl?: string;
  requirements: string[];
  benefits: string[];
}

export interface ParsedResume {
  skills: string[];
  interests: string[];
  experience: string[];
  projects: string[];
  education: string[];
  location?: string;
}

export interface Company {
  id: string;
  name: string;
  description: string;
  website: string;
  hiringInterests: string[];
  locations: string[];
  companySize: 'startup' | 'small' | 'medium' | 'large' | 'enterprise';
  industry: string[];
}
