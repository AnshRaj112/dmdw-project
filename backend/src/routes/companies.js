const express = require('express');
const axios = require('axios');

const router = express.Router();

// Mock company data - in production, this would come from a database
const mockCompanies = [
  {
    id: '1',
    name: 'TechCorp Solutions',
    description: 'Leading technology company specializing in AI and machine learning solutions.',
    website: 'https://techcorp.com',
    hiringInterests: ['web-development', 'data-science', 'ai-ml', 'cloud-computing'],
    locations: ['San Francisco', 'New York', 'Remote'],
    companySize: 'large',
    industry: ['Technology', 'AI/ML'],
    openPositions: [
      {
        id: '1',
        title: 'Software Engineering Intern',
        description: 'Work on cutting-edge web applications using React and Node.js',
        type: 'internship',
        location: 'San Francisco',
        skills: ['React', 'Node.js', 'JavaScript', 'TypeScript'],
        requirements: ['Currently enrolled in CS program', 'Basic knowledge of web development'],
        benefits: ['Mentorship program', 'Flexible hours', 'Competitive stipend']
      },
      {
        id: '2',
        title: 'Data Science Intern',
        description: 'Analyze large datasets and build machine learning models',
        type: 'internship',
        location: 'Remote',
        skills: ['Python', 'Machine Learning', 'Data Analysis', 'SQL'],
        requirements: ['Statistics background', 'Python experience'],
        benefits: ['Remote work', 'Learning opportunities', 'Project ownership']
      }
    ]
  },
  {
    id: '2',
    name: 'StartupXYZ',
    description: 'Fast-growing startup focused on mobile app development and user experience.',
    website: 'https://startupxyz.com',
    hiringInterests: ['mobile-development', 'ui-ux', 'web-development', 'product-design'],
    locations: ['Austin', 'Remote'],
    companySize: 'startup',
    industry: ['Mobile', 'Design'],
    openPositions: [
      {
        id: '3',
        title: 'Mobile App Development Intern',
        description: 'Build iOS and Android apps using React Native',
        type: 'internship',
        location: 'Austin',
        skills: ['React Native', 'JavaScript', 'iOS', 'Android'],
        requirements: ['Mobile development interest', 'JavaScript knowledge'],
        benefits: ['Equity participation', 'Fast-paced environment', 'Direct mentorship']
      }
    ]
  },
  {
    id: '3',
    name: 'DataFlow Analytics',
    description: 'Data analytics company helping businesses make data-driven decisions.',
    website: 'https://dataflow.com',
    hiringInterests: ['data-science', 'analytics', 'research', 'business-strategy'],
    locations: ['Chicago', 'Boston', 'Remote'],
    companySize: 'medium',
    industry: ['Analytics', 'Consulting'],
    openPositions: [
      {
        id: '4',
        title: 'Business Analytics Intern',
        description: 'Analyze business data and create insights for clients',
        type: 'internship',
        location: 'Chicago',
        skills: ['Excel', 'SQL', 'Tableau', 'Business Analysis'],
        requirements: ['Business or analytics background', 'Excel proficiency'],
        benefits: ['Client exposure', 'Real-world projects', 'Career development']
      }
    ]
  }
];

// Get all companies
router.get('/', async (req, res) => {
  try {
    res.json({
      success: true,
      companies: mockCompanies
    });
  } catch (error) {
    console.error('Companies Error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch companies',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

// Get company by ID
router.get('/:id', async (req, res) => {
  try {
    const companyId = req.params.id;
    const company = mockCompanies.find(c => c.id === companyId);
    
    if (!company) {
      return res.status(404).json({
        success: false,
        message: 'Company not found'
      });
    }

    res.json({
      success: true,
      company: company
    });
  } catch (error) {
    console.error('Company Error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch company',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

// Get companies by interests
router.post('/search', async (req, res) => {
  try {
    const { interests, location, companySize } = req.body;
    
    let filteredCompanies = mockCompanies;
    
    // Filter by interests
    if (interests && interests.length > 0) {
      filteredCompanies = filteredCompanies.filter(company =>
        company.hiringInterests.some(interest =>
          interests.some(userInterest =>
            userInterest.toLowerCase().includes(interest.toLowerCase()) ||
            interest.toLowerCase().includes(userInterest.toLowerCase())
          )
        )
      );
    }
    
    // Filter by location
    if (location) {
      filteredCompanies = filteredCompanies.filter(company =>
        company.locations.some(companyLocation =>
          companyLocation.toLowerCase().includes(location.toLowerCase()) ||
          companyLocation.toLowerCase() === 'remote'
        )
      );
    }
    
    // Filter by company size
    if (companySize) {
      filteredCompanies = filteredCompanies.filter(company =>
        company.companySize === companySize
      );
    }

    res.json({
      success: true,
      companies: filteredCompanies,
      total: filteredCompanies.length
    });
  } catch (error) {
    console.error('Company Search Error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to search companies',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

module.exports = router;
