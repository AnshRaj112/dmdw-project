const express = require('express');
const axios = require('axios');
const Joi = require('joi');

const router = express.Router();

// Validation schemas
const interestsSchema = Joi.object({
  interests: Joi.array().items(Joi.string()).min(1).required()
});

const resumeSchema = Joi.object({
  skills: Joi.array().items(Joi.string()).required(),
  interests: Joi.array().items(Joi.string()).required(),
  experience: Joi.array().items(Joi.string()).required(),
  projects: Joi.array().items(Joi.string()).required(),
  education: Joi.array().items(Joi.string()).optional(),
  location: Joi.string().allow(null).optional(),
  type: Joi.string().valid('resume').optional()
});

// Get recommendations endpoint
router.post('/', async (req, res) => {
  try {
    const mlServiceUrl = process.env.ML_SERVICE_URL || 'https://sih2025-fcbf.onrender.com';
    
    // Check if request contains resume data (skills + interests) or just interests
    if (req.body.skills && req.body.interests) {
      // Validate resume data
      const { error, value } = resumeSchema.validate(req.body);
      if (error) {
        return res.status(400).json({
          success: false,
          message: 'Invalid resume data',
          error: error.details[0].message
        });
      }

      // Forward to ML service for recommendations based on parsed resume
      try {
        const response = await axios.post(`${mlServiceUrl}/recommend`, {
          ...value,
          type: 'resume'
        }, {
          timeout: 30000
        });

        res.json({
          success: true,
          message: 'Recommendations generated successfully',
          recommendations: response.data.recommendations
        });

      } catch (mlError) {
        console.error('ML Service Error:', mlError.message);
        res.status(500).json({
          success: false,
          message: 'Failed to generate recommendations. Please try again.',
          error: process.env.NODE_ENV === 'development' ? mlError.message : undefined
        });
      }

    } else if (req.body.interests) {
      // Validate interests input
      const { error, value } = interestsSchema.validate(req.body);
      if (error) {
        return res.status(400).json({
          success: false,
          message: 'Invalid input data',
          error: error.details[0].message
        });
      }

      // Forward to ML service for recommendations based on interests
      try {
        const response = await axios.post(`${mlServiceUrl}/recommend`, {
          interests: value.interests,
          type: 'interests'
        }, {
          timeout: 30000
        });

        res.json({
          success: true,
          message: 'Recommendations generated successfully',
          recommendations: response.data.recommendations
        });

      } catch (mlError) {
        console.error('ML Service Error:', mlError.message);
        res.status(500).json({
          success: false,
          message: 'Failed to generate recommendations. Please try again.',
          error: process.env.NODE_ENV === 'development' ? mlError.message : undefined
        });
      }

    } else {
      res.status(400).json({
        success: false,
        message: 'Invalid request. Please provide either interests or resume data.'
      });
    }

  } catch (error) {
    console.error('Recommendation Error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

module.exports = router;
