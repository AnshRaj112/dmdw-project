'use client';

import { useState } from 'react';
import { Upload, FileText, CheckCircle, XCircle, Loader2 } from 'lucide-react';
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
      const formData = new FormData();
      
      if (selectedOption === 'resume' && uploadedFile) {
        formData.append('resume', uploadedFile);
      } else if (selectedOption === 'interests') {
        formData.append('interests', JSON.stringify(selectedInterests.map(i => i.name)));
      }

      const response = await fetch('/api/recommend', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to get recommendations');
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
    <div className="min-h-screen bg-gray-50">
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
                style={{
                  padding: '12px 32px',
                  fontSize: '16px',
                  fontWeight: '600',
                  borderRadius: '8px',
                  border: 'none',
                  cursor: canGetRecommendations() && !isLoading ? 'pointer' : 'not-allowed',
                  opacity: canGetRecommendations() && !isLoading ? 1 : 0.6,
                  background: '#0ea5e9',
                  color: 'white',
                  transition: 'all 0.2s ease-in-out'
                }}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="inline-block w-4 h-4 mr-2 animate-spin" />
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