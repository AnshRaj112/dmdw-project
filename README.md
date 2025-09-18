# AI-Based Internship Recommendation Engine for PM Internship Scheme

## Overview

This project develops a lightweight AI-based recommendation engine to assist candidates applying for the PM Internship Scheme. Many applicants are first-generation learners from rural and underserved backgrounds, with limited exposure to digital tools and internships. With hundreds of opportunities listed, identifying the right internship is often challenging.

The system provides candidates with 3–5 personalized internship recommendations based on their resumes, skills, interests, academic background, and location preferences. The solution is designed to be mobile-friendly, user-friendly, and compatible with low-resource environments.

## Objectives

- Capture candidate inputs (education, skills, sector interests, location)
- Support both manual interest selection and automatic CV/resume parsing
- Match candidate profiles with a curated or scraped dataset of company roles
- Suggest 3–5 most relevant internships instead of overwhelming lists
- Provide an intuitive and simple user interface accessible on mobile devices
- Ensure easy integration with the PM Internship Scheme portal

## System Architecture

### Workflow Diagram

```mermaid
flowchart LR
    A[Candidate] -->|Upload Resume / Select Interests| B[Frontend: Next.js]
    B -->|Send Request| C[Backend: Node.js/Express]
    C -->|Forward Resume/Inputs| D[ML Service: Python FastAPI]
    D -->|Parse Resume & Extract Skills| E[Resume Parser/NLP Model]
    D -->|Match Interests with Roles| F[Recommendation Engine]
    F -->|Fetch Company Dataset| G[Database / Scraped Data]
    F -->|Return Top 3-5 Matches| C
    C -->|Send Recommendations| B
    B -->|Display Results| A
```

### System Components

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Next.js App]
        B[React Components]
        C[TailwindCSS + shadcn/ui]
    end
    
    subgraph "Backend Layer"
        D[Node.js/Express API]
        E[Authentication Service]
        F[File Upload Handler]
    end
    
    subgraph "ML Service Layer"
        G[Python FastAPI]
        H[Resume Parser]
        I[Recommendation Engine]
        J[NLP Models]
    end
    
    subgraph "Data Layer"
        K[MongoDB/PostgreSQL]
        L[Company Dataset]
        M[Processed Data]
    end
    
    A --> D
    D --> G
    G --> K
    H --> J
    I --> L
```

## Folder Structure

```
pm-internship-recommender/
├── README.md
├── package.json
├── docker-compose.yml
├── /docs/                     
├── /scripts/                  
│
├── frontend/                  
│   └── src/
│       ├── app/               
│       ├── components/        
│       ├── hooks/             
│       ├── lib/               
│       ├── styles/            
│       └── utils/             
│
├── backend/                   
│   └── src/
│       ├── routes/            
│       ├── controllers/       
│       ├── services/          
│       ├── models/            
│       └── utils/             
│
├── ml-service/                
│   └── app/
│       ├── models/            
│       ├── services/          
│       ├── routes/            
│       ├── utils/             
│       └── config/            
│
├── data/                      
│   ├── candidates/            
│   ├── companies/             
│   ├── processed/             
│   └── raw/                   
│
├── database/                  
│   ├── migrations/
│   └── schema.sql
│
└── tests/                     
    ├── frontend/
    ├── backend/
    └── ml-service/
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14+
- **Styling**: TailwindCSS
- **UI Components**: shadcn/ui
- **State Management**: React Context/Zustand
- **File Upload**: React Dropzone

### Backend
- **Runtime**: Node.js 18+
- **Framework**: Express.js
- **Database**: MongoDB/PostgreSQL
- **Authentication**: JWT
- **File Processing**: Multer

### ML Service
- **Framework**: Python 3.9+
- **API**: FastAPI
- **NLP**: spaCy, Sentence-BERT
- **PDF Processing**: PDFMiner
- **ML Libraries**: scikit-learn, pandas

### Deployment
- **Containerization**: Docker, Docker Compose
- **Orchestration**: Docker Swarm/Kubernetes (optional)

## API Endpoints

### Backend (Node.js/Express)

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `POST` | `/api/upload` | Upload resume and forward to ML service | `FormData` with resume file |
| `POST` | `/api/recommend` | Get top internship recommendations | `{ profile, preferences }` |
| `GET` | `/api/companies` | Retrieve available company and role dataset | - |
| `GET` | `/api/health` | Health check endpoint | - |

### ML Service (Python FastAPI)

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `POST` | `/parse_resume` | Extract candidate interests and skills from CV | `{ file_path, file_type }` |
| `POST` | `/recommend` | Match candidate profile with company roles | `{ skills, interests, location }` |
| `GET` | `/health` | Health check endpoint | - |
| `GET` | `/docs` | API documentation | - |

## Installation and Setup

### Prerequisites

- Node.js 18+ 
- Python 3.9+
- Docker & Docker Compose
- Git

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/username/sih2025.git
   cd pm-internship-recommender
   ```

2. **Start services with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - ML Service: http://localhost:8000
   - ML Service Docs: http://localhost:8000/docs

### Manual Setup

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

#### Backend Setup
```bash
cd backend
npm install
npm run dev
```

#### ML Service Setup
```bash
cd ml-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Usage

### For Candidates

1. **Upload Resume**: Upload your CV/resume in PDF or DOC format
2. **Manual Input**: Alternatively, manually select your skills and interests
3. **Location Preference**: Specify your preferred work location
4. **Get Recommendations**: Receive 3-5 personalized internship suggestions
5. **Apply**: Click through to apply for recommended positions

### For Administrators

1. **Manage Dataset**: Update company and role information
2. **Monitor Usage**: Track recommendation accuracy and user feedback
3. **System Health**: Monitor service status and performance

## Data Flow

```mermaid
sequenceDiagram
    participant C as Candidate
    participant F as Frontend
    participant B as Backend
    participant M as ML Service
    participant D as Database
    
    C->>F: Upload Resume/Select Interests
    F->>B: POST /api/upload
    B->>M: POST /parse_resume
    M->>M: Extract Skills & Interests
    M->>B: Return Parsed Data
    B->>M: POST /recommend
    M->>D: Query Company Dataset
    D->>M: Return Matching Roles
    M->>B: Top 3-5 Recommendations
    B->>F: Send Recommendations
    F->>C: Display Results
```

## Configuration

### Environment Variables

#### Backend (.env)
```env
PORT=5000
MONGODB_URI=mongodb://localhost:27017/pm-internship
JWT_SECRET=your_jwt_secret
ML_SERVICE_URL=http://localhost:8000
```

#### ML Service (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/pm_internship
MODEL_PATH=./models/
UPLOAD_PATH=./uploads/
```

## Testing

### Run Tests
```bash
# Frontend tests
cd frontend && npm test

# Backend tests
cd backend && npm test

# ML Service tests
cd ml-service && pytest

# All tests
npm run test:all
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Enhancements

- [ ] **Regional Language Support**: Add support for regional languages for users with low digital literacy
- [ ] **Improved NLP Models**: Implement more accurate skill extraction using advanced NLP models
- [ ] **Recommendation Explanation**: Add explanations for why specific internships are recommended to improve candidate trust
- [ ] **Portal Integration**: Direct integration with PM Internship Scheme portal APIs
- [ ] **Mobile App**: Native mobile application for better accessibility
- [ ] **Analytics Dashboard**: Admin dashboard for monitoring and analytics
- [ ] **Feedback System**: User feedback collection to improve recommendation accuracy
- [ ] **Multi-language Support**: Support for multiple Indian languages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email support@pm-internship-recommender.com or create an issue in the repository.

## Acknowledgments

- PM Internship Scheme for providing the opportunity
- Open source community for the amazing tools and libraries
- Contributors and testers who helped improve the system
