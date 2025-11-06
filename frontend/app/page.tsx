'use client';

import { useState } from 'react';
import { Upload, FileText, Loader2 } from 'lucide-react';
import FileUpload from './components/FileUpload';
import InterestSelector from './components/InterestSelector';
import Recommendations from './components/Recommendations';
import { Interest, Recommendation } from './types';

export default function Home() {
  const [selectedOption, setSelectedOption] = useState<'resume' | 'interests' | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [selectedInterests, setSelectedInterests] = useState<Interest[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGetRecommendations = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://sih2025-1-om5y.onrender.com';
      let response: Response;

      if (selectedOption === 'interests') {
        const payload = { interests: selectedInterests.map(i => i.name) };
        response = await fetch(`${backendUrl}/api/recommend`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } else if (selectedOption === 'resume' && uploadedFile) {
        // Step 1: Upload resume to backend to parse
        const formData = new FormData();
        formData.append('resume', uploadedFile);
        const uploadRes = await fetch(`${backendUrl}/api/upload`, {
          method: 'POST',
          body: formData,
        });
        if (!uploadRes.ok) {
          const errJson = await uploadRes.json().catch(() => null);
          throw new Error(errJson?.message || 'Failed to parse resume');
        }
        const uploadJson = await uploadRes.json();
        const parsed = uploadJson?.data;

        // Step 2: Call recommend with parsed resume JSON
        const resumePayload = {
          skills: parsed?.skills || [],
          interests: parsed?.interests || [],
          experience: parsed?.experience || [],
          projects: parsed?.projects || [],
          education: parsed?.education || [],
          location: parsed?.location || null,
        };

        if (!resumePayload.interests || resumePayload.interests.length === 0) {
          throw new Error('Could not infer interests from resume. Please select interests instead.');
        }

        response = await fetch(`${backendUrl}/api/recommend`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(resumePayload),
        });
      } else {
        throw new Error('Please provide required input');
      }

      if (!response.ok) {
        const errJson = await response.json().catch(() => null);
        throw new Error(errJson?.message || 'Failed to get recommendations');
      }

      const data = await response.json();
      setRecommendations(data.recommendations);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const canGetRecommendations = () => {
    if (selectedOption === 'resume') {
      return uploadedFile !== null;
    } else if (selectedOption === 'interests') {
      return selectedInterests.length > 0;
    }
    return false;
  };

  return (
    <div className="page-wrapper">
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <h1 className="hero__title">
            Find Your Perfect Internship Match
          </h1>
          <p className="hero__subtitle">
            Upload your resume or select your interests to get personalized internship recommendations from top companies.
          </p>
        </div>
      </section>

      {/* Main Content */}
      <div className="container">
        <section className="upload-section">
          <h2 className="upload-section__title">
            How would you like to get started?
          </h2>
          
          <div className="upload-section__options">
            <div 
              className={`upload-option ${selectedOption === 'resume' ? 'upload-option--active' : ''}`}
              onClick={() => setSelectedOption('resume')}
            >
              <Upload className="upload-option__icon" />
              <h3 className="upload-option__title">Upload Resume</h3>
              <p className="upload-option__description">
                Upload your CV or resume and let our AI extract your skills and interests automatically.
              </p>
            </div>

            <div 
              className={`upload-option ${selectedOption === 'interests' ? 'upload-option--active' : ''}`}
              onClick={() => setSelectedOption('interests')}
            >
              <FileText className="upload-option__icon" />
              <h3 className="upload-option__title">Select Interests</h3>
              <p className="upload-option__description">
                Choose from our curated list of skills and interests to find matching opportunities.
              </p>
            </div>
          </div>

          {/* Resume Upload */}
          {selectedOption === 'resume' && (
            <FileUpload
              onFileSelect={setUploadedFile}
              selectedFile={uploadedFile}
            />
          )}

          {/* Interest Selection */}
          {selectedOption === 'interests' && (
            <InterestSelector
              selectedInterests={selectedInterests}
              onInterestsChange={setSelectedInterests}
            />
          )}

          {/* Action Button */}
          {selectedOption && (
            <div className="text-center mt-8">
              <button
                className="button-primary"
                onClick={handleGetRecommendations}
                disabled={!canGetRecommendations() || isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="animate-spin" />
                    Getting Recommendations...
                  </>
                ) : (
                  'Get My Recommendations'
                )}
              </button>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="error">
              <h3 className="error__title">Error</h3>
              <p className="error__message">{error}</p>
            </div>
          )}
        </section>

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <Recommendations recommendations={recommendations} />
        )}
      </div>
    </div>
  );
}