'use client';

import { useState, useEffect } from 'react';
import { Interest } from '../types';

interface InterestSelectorProps {
  selectedInterests: Interest[];
  onInterestsChange: (interests: Interest[]) => void;
}

const INTERESTS_DATA: Interest[] = [
  // Technology
  { id: 'web-dev', name: 'Web Development', category: 'Technology' },
  { id: 'mobile-dev', name: 'Mobile Development', category: 'Technology' },
  { id: 'data-science', name: 'Data Science', category: 'Technology' },
  { id: 'ai-ml', name: 'Artificial Intelligence', category: 'Technology' },
  { id: 'cybersecurity', name: 'Cybersecurity', category: 'Technology' },
  { id: 'cloud-computing', name: 'Cloud Computing', category: 'Technology' },
  { id: 'devops', name: 'DevOps', category: 'Technology' },
  { id: 'blockchain', name: 'Blockchain', category: 'Technology' },
  
  // Business
  { id: 'marketing', name: 'Digital Marketing', category: 'Business' },
  { id: 'sales', name: 'Sales', category: 'Business' },
  { id: 'finance', name: 'Finance', category: 'Business' },
  { id: 'hr', name: 'Human Resources', category: 'Business' },
  { id: 'operations', name: 'Operations', category: 'Business' },
  { id: 'strategy', name: 'Business Strategy', category: 'Business' },
  { id: 'consulting', name: 'Consulting', category: 'Business' },
  
  // Design
  { id: 'ui-ux', name: 'UI/UX Design', category: 'Design' },
  { id: 'graphic-design', name: 'Graphic Design', category: 'Design' },
  { id: 'product-design', name: 'Product Design', category: 'Design' },
  { id: 'branding', name: 'Branding', category: 'Design' },
  
  // Content & Media
  { id: 'content-writing', name: 'Content Writing', category: 'Content & Media' },
  { id: 'social-media', name: 'Social Media', category: 'Content & Media' },
  { id: 'video-editing', name: 'Video Editing', category: 'Content & Media' },
  { id: 'photography', name: 'Photography', category: 'Content & Media' },
  
  // Research
  { id: 'research', name: 'Research', category: 'Research' },
  { id: 'analytics', name: 'Analytics', category: 'Research' },
  { id: 'market-research', name: 'Market Research', category: 'Research' },
  
  // Other
  { id: 'project-management', name: 'Project Management', category: 'Other' },
  { id: 'customer-support', name: 'Customer Support', category: 'Other' },
  { id: 'legal', name: 'Legal', category: 'Other' },
  { id: 'education', name: 'Education', category: 'Other' },
];

const InterestSelector: React.FC<InterestSelectorProps> = ({
  selectedInterests,
  onInterestsChange,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  const categories = ['All', ...Array.from(new Set(INTERESTS_DATA.map(interest => interest.category)))];

  const filteredInterests = INTERESTS_DATA.filter(interest => {
    const matchesSearch = interest.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || interest.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const toggleInterest = (interest: Interest) => {
    const isSelected = selectedInterests.some(selected => selected.id === interest.id);
    
    if (isSelected) {
      onInterestsChange(selectedInterests.filter(selected => selected.id !== interest.id));
    } else {
      onInterestsChange([...selectedInterests, interest]);
    }
  };

  return (
    <div className="interests-selection">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Select your interests and skills
        </h3>
        
        {/* Search and Filter */}
        <div className="flex flex-col sm:flex-row gap-4 mb-4">
          <input
            type="text"
            placeholder="Search interests..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>

        {/* Selected Count */}
        <p className="text-sm text-gray-600 mb-4">
          {selectedInterests.length} interest{selectedInterests.length !== 1 ? 's' : ''} selected
        </p>
      </div>

      {/* Interests Grid */}
      <div className="interests-selection__grid">
        {filteredInterests.map(interest => {
          const isSelected = selectedInterests.some(selected => selected.id === interest.id);
          
          return (
            <div
              key={interest.id}
              className={`interests-selection__item ${
                isSelected ? 'interests-selection__item--selected' : ''
              }`}
              onClick={() => toggleInterest(interest)}
            >
              {interest.name}
            </div>
          );
        })}
      </div>

      {filteredInterests.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No interests found matching your search criteria.
        </div>
      )}
    </div>
  );
};

export default InterestSelector;
