# AI-Based Internship Recommendation Engine - Setup Guide

## Overview

This project is a comprehensive AI-based internship recommendation system that helps users find personalized internship opportunities by either uploading their resume or selecting their interests. The system uses machine learning to parse resumes, extract skills and interests, and match them with company requirements.

## Architecture

- **Frontend**: Next.js 15 with TypeScript and modular SCSS
- **Backend**: Node.js with Express
- **ML Service**: Python with FastAPI
- **Database**: In-memory (can be extended to MongoDB/PostgreSQL)

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.9+

### Manual Setup

#### 1. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

#### 2. Backend Setup

```bash
cd backend
npm install
npm run dev
```

#### 3. ML Service Setup

```bash
cd ml-services
pip install -r requirements-simple.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"
uvicorn app.main:app --reload --port 8000
```

## Features

### 1. Resume Upload & Parsing
- Upload PDF, DOC, or DOCX files
- AI-powered extraction of:
  - Skills and technical abilities
  - Interests and hobbies
  - Work experience
  - Projects and achievements
  - Education background
  - Location preferences

### 2. Interest Selection
- Curated list of skills and interests
- Categorized by technology, business, design, etc.
- Search and filter functionality
- Multi-select interface

### 3. Smart Recommendations
- ML-powered matching algorithm
- Top 3 personalized recommendations
- Match score calculation
- Company and position details
- Skills alignment analysis

### 4. Company Database
- Pre-loaded with 5+ companies
- Various industries and company sizes
- Multiple internship positions
- Detailed job descriptions and requirements

## API Endpoints

### Backend API (Port 5000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload and parse resume |
| POST | `/api/recommend` | Get recommendations |
| GET | `/api/companies` | Get company list |
| GET | `/api/health` | Health check |

### ML Service API (Port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/parse_resume` | Parse resume content |
| POST | `/recommend` | Generate recommendations |
| GET | `/companies` | Get company data |
| GET | `/health` | Health check |
| GET | `/docs` | API documentation |

## Usage

### For Users

1. **Upload Resume:**
   - Click "Upload Resume" option
   - Select PDF, DOC, or DOCX file
   - Wait for AI parsing to complete

2. **Select Interests:**
   - Click "Select Interests" option
   - Choose from categorized skills and interests
   - Use search to find specific items

3. **Get Recommendations:**
   - Click "Get My Recommendations"
   - View top 3 personalized matches
   - See match scores and details
   - Apply directly through provided links

### For Developers

#### Adding New Companies

Edit `ml-services/app/services/company_matcher.py`:

```python
companies_data = [
    {
        "id": "new_company_id",
        "name": "Company Name",
        "description": "Company description",
        "website": "https://company.com",
        "hiring_interests": ["skill1", "skill2"],
        "locations": ["City", "Remote"],
        "company_size": "medium",
        "industry": ["Technology"],
        "open_positions": [
            {
                "id": "position_id",
                "title": "Position Title",
                "description": "Job description",
                "type": "internship",
                "location": "City",
                "skills": ["skill1", "skill2"],
                "requirements": ["req1", "req2"],
                "benefits": ["benefit1", "benefit2"],
                "apply_url": "https://company.com/apply"
            }
        ]
    }
]
```

#### Customizing Skills Extraction

Edit `ml-services/app/services/resume_parser.py`:

```python
self.skills_keywords = {
    'new_category': ['skill1', 'skill2', 'skill3'],
    # ... existing categories
}
```

## Configuration

### Environment Variables

#### Backend (.env)
```env
PORT=5000
NODE_ENV=development
ML_SERVICE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

#### ML Service (.env)
```env
PYTHONPATH=/app
```

### Frontend Configuration

The frontend automatically connects to the backend API. Update `app/api/recommend/route.ts` if using different ports.

## Troubleshooting

### Common Issues

1. **ML Service not starting:**
   - Ensure Python 3.9+ is installed
   - Install spaCy model: `python -m spacy download en_core_web_sm`
   - Install NLTK data: `python -c "import nltk; nltk.download('punkt')"`

2. **File upload errors:**
   - Check file size (max 10MB)
   - Ensure file is PDF, DOC, or DOCX
   - Check backend logs for detailed errors

3. **Recommendations not loading:**
   - Verify ML service is running on port 8000
   - Check backend logs for API errors
   - Ensure company data is loaded

4. **Frontend not connecting:**
   - Verify backend is running on port 5000
   - Check CORS configuration
   - Update API URLs in frontend code

### Logs

- **Frontend**: Check browser console
- **Backend**: `npm run dev` shows logs
- **ML Service**: `uvicorn` shows logs

## Development

### Project Structure

```
sih2025/
├── frontend/                 # Next.js frontend
│   ├── app/
│   │   ├── components/       # React components
│   │   ├── api/             # API routes
│   │   └── styles/          # SCSS styles
│   └── package.json
├── backend/                  # Node.js backend
│   ├── src/
│   │   ├── routes/          # API routes
│   │   └── server.js        # Main server file
│   └── package.json
├── ml-services/             # Python ML service
│   ├── app/
│   │   ├── services/        # ML services
│   │   ├── models/          # Data models
│   │   └── main.py          # FastAPI app
│   └── requirements.txt
```

### Adding New Features

1. **New ML Models**: Add to `ml-services/app/services/`
2. **New API Endpoints**: Add to `backend/src/routes/`
3. **New UI Components**: Add to `frontend/app/components/`
4. **New Styles**: Add to `frontend/app/styles/`

## Production Deployment

1. **Build and deploy:**
   ```bash
   # Frontend
   cd frontend && npm run build && npm start
   
   # Backend
   cd backend && npm start
   
   # ML Service
   cd ml-services && uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Environment Variables for Production

- Set `NODE_ENV=production`
- Configure proper database URLs
- Set up proper CORS origins
- Configure file storage (AWS S3, etc.)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Create an issue in the repository
4. Contact the development team
