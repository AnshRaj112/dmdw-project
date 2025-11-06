'use client';

import { Recommendation } from '../types';
import { ExternalLink, MapPin, Clock, Users, Star } from 'lucide-react';

interface RecommendationsProps {
  recommendations: Recommendation[];
}

const Recommendations: React.FC<RecommendationsProps> = ({ recommendations }) => {
  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'internship':
        return <Users className="w-4 h-4" />;
      case 'full-time':
        return <Clock className="w-4 h-4" />;
      case 'part-time':
        return <Clock className="w-4 h-4" />;
      default:
        return <Users className="w-4 h-4" />;
    }
  };

  return (
    <div className="recommendations">
      <h2 className="recommendations__title">
        Your Personalized Recommendations
      </h2>
      
      <div className="recommendations__grid">
        {recommendations.map((rec) => (
          <div key={rec.id} className="recommendations__card">
            <div className="recommendations__header">
              <h3 className="recommendations__company">{rec.company}</h3>
              <span className={`recommendations__match-score ${getMatchScoreColor(rec.matchScore * 100)}`}>
                {(rec.matchScore * 100).toFixed(0)}% match (Confidence: {rec.matchScore.toFixed(2)})
              </span>
            </div>
            
            <h4 className="recommendations__role">{rec.role}</h4>
            <div className="mb-2">
              <span className="inline-block px-2 py-1 text-xs font-medium rounded bg-blue-50 text-blue-700 border border-blue-100">
                {rec.sector}
              </span>
            </div>
            
            <div className="flex items-center gap-4 mb-3 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <MapPin className="w-4 h-4" />
                {rec.location}
              </div>
              <div className="flex items-center gap-1">
                {getTypeIcon(rec.type)}
                {rec.type.charAt(0).toUpperCase() + rec.type.slice(1).replace('-', ' ')}
              </div>
            </div>
            
            <p className="recommendations__description">{rec.description}</p>
            
            {rec.skills && rec.skills.length > 0 && (
              <div className="recommendations__skills">
                {rec.skills.slice(0, 6).map((skill, index) => (
                  <span key={index} className="recommendations__skill">
                    {skill}
                  </span>
                ))}
                {rec.skills.length > 6 && (
                  <span className="recommendations__skill">
                    +{rec.skills.length - 6} more
                  </span>
                )}
              </div>
            )}
            
            {rec.requirements && rec.requirements.length > 0 && (
              <div className="mb-4">
                <h5 className="text-sm font-medium text-gray-700 mb-2">Key Requirements:</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  {rec.requirements.slice(0, 3).map((req, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      {req}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {rec.benefits && rec.benefits.length > 0 && (
              <div className="mb-4">
                <h5 className="text-sm font-medium text-gray-700 mb-2">Benefits:</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  {rec.benefits.slice(0, 2).map((benefit, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      {benefit}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            <div className="recommendations__actions">
              {rec.applyUrl ? (
                <a
                  href={rec.applyUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="recommendations__apply-btn"
                >
                  Apply Now
                  <ExternalLink className="w-4 h-4 ml-2" />
                </a>
              ) : (
                <button className="recommendations__apply-btn" disabled>
                  Apply Now
                </button>
              )}
              <button className="recommendations__details-btn">
                  View Details
                </button>
            </div>
          </div>
        ))}
      </div>
      
      {recommendations.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Star className="w-16 h-16 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No recommendations found
          </h3>
          <p className="text-gray-600">
            Try adjusting your interests or uploading a different resume.
          </p>
        </div>
      )}
    </div>
  );
};

export default Recommendations;
