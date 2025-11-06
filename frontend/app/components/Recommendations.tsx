'use client';

import { useState } from 'react';
import { Recommendation } from '../types';
import { ExternalLink, MapPin, Clock, Users, Star, ChevronDown, ChevronUp } from 'lucide-react';

interface RecommendationsProps {
  recommendations: Recommendation[];
}

const Recommendations: React.FC<RecommendationsProps> = ({ recommendations }) => {
  const [expandedDescriptions, setExpandedDescriptions] = useState<Set<string>>(new Set());

  const toggleDescription = (recId: string) => {
    setExpandedDescriptions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(recId)) {
        newSet.delete(recId);
      } else {
        newSet.add(recId);
      }
      return newSet;
    });
  };

  const isDescriptionLong = (description: string) => {
    // Consider description long if it has more than 150 characters
    return description.length > 150;
  };

  const getMatchScoreClass = (score: number) => {
    if (score >= 90) return 'recommendations__match-score--excellent';
    if (score >= 70) return 'recommendations__match-score--good';
    return 'recommendations__match-score--fair';
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
              <span className={`recommendations__match-score ${getMatchScoreClass(rec.matchScore * 100)}`}>
                {(rec.matchScore * 100).toFixed(0)}% Match
              </span>
            </div>
            
            <h4 className="recommendations__role">{rec.role}</h4>
            <div className="recommendations__sector-wrapper">
              <span className="recommendations__sector">
                {rec.sector}
              </span>
            </div>
            
            <div className="recommendations__meta">
              <div className="recommendations__meta-item">
                <MapPin />
                <span>{rec.location}</span>
              </div>
              <div className="recommendations__meta-item">
                {getTypeIcon(rec.type)}
                <span>{rec.type.charAt(0).toUpperCase() + rec.type.slice(1).replace('-', ' ')}</span>
              </div>
            </div>
            
            <div className="recommendations__description-wrapper">
              <p 
                className={`recommendations__description ${
                  expandedDescriptions.has(rec.id) ? 'recommendations__description--expanded' : ''
                }`}
              >
                {rec.description}
              </p>
              {isDescriptionLong(rec.description) && (
                <button
                  className="recommendations__read-more"
                  onClick={() => toggleDescription(rec.id)}
                  aria-expanded={expandedDescriptions.has(rec.id)}
                >
                  {expandedDescriptions.has(rec.id) ? (
                    <>
                      Read Less
                      <ChevronUp className="recommendations__read-more-icon" />
                    </>
                  ) : (
                    <>
                      Read More
                      <ChevronDown className="recommendations__read-more-icon" />
                    </>
                  )}
                </button>
              )}
            </div>
            
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
              <div className="recommendations__section recommendations__section--requirements">
                <h5>Key Requirements</h5>
                <ul>
                  {rec.requirements.slice(0, 3).map((req, index) => (
                    <li key={index}>{req}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {rec.benefits && rec.benefits.length > 0 && (
              <div className="recommendations__section recommendations__section--benefits">
                <h5>Benefits</h5>
                <ul>
                  {rec.benefits.slice(0, 2).map((benefit, index) => (
                    <li key={index}>{benefit}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* <div className="recommendations__actions">
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
            </div> */}
          </div>
        ))}
      </div>
      
      {recommendations.length === 0 && (
        <div className="recommendations__empty-state">
          <Star />
          <h3>No recommendations found</h3>
          <p>Try adjusting your interests or uploading a different resume.</p>
        </div>
      )}
    </div>
  );
};

export default Recommendations;
