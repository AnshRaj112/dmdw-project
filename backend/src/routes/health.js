const express = require('express');
const axios = require('axios');

const router = express.Router();

// Health check endpoint
router.get('/', async (req, res) => {
  try {
    const healthStatus = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      version: process.env.npm_package_version || '1.0.0',
      services: {
        database: 'connected', // In production, check actual DB connection
        mlService: 'unknown'
      }
    };

    // Check ML service health
    try {
      const mlServiceUrl = process.env.ML_SERVICE_URL || 'http://localhost:8000';
      const mlResponse = await axios.get(`${mlServiceUrl}/health`, {
        timeout: 5000
      });
      healthStatus.services.mlService = mlResponse.data.status || 'healthy';
    } catch (mlError) {
      healthStatus.services.mlService = 'unhealthy';
      healthStatus.mlServiceError = mlError.message;
    }

    const statusCode = healthStatus.services.mlService === 'unhealthy' ? 503 : 200;
    
    res.status(statusCode).json(healthStatus);
  } catch (error) {
    console.error('Health Check Error:', error);
    res.status(500).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
});

// Detailed health check
router.get('/detailed', async (req, res) => {
  try {
    const detailedHealth = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      environment: process.env.NODE_ENV || 'development',
      version: process.env.npm_package_version || '1.0.0',
      services: {
        database: {
          status: 'connected',
          responseTime: '< 1ms' // Mock response time
        },
        mlService: {
          status: 'unknown',
          responseTime: null,
          error: null
        }
      }
    };

    // Check ML service with detailed info
    try {
      const mlServiceUrl = process.env.ML_SERVICE_URL || 'http://localhost:8000';
      const startTime = Date.now();
      const mlResponse = await axios.get(`${mlServiceUrl}/health`, {
        timeout: 10000
      });
      const responseTime = Date.now() - startTime;
      
      detailedHealth.services.mlService = {
        status: mlResponse.data.status || 'healthy',
        responseTime: `${responseTime}ms`,
        error: null
      };
    } catch (mlError) {
      detailedHealth.services.mlService = {
        status: 'unhealthy',
        responseTime: null,
        error: mlError.message
      };
    }

    const hasUnhealthyService = Object.values(detailedHealth.services).some(
      service => service.status === 'unhealthy'
    );
    
    const statusCode = hasUnhealthyService ? 503 : 200;
    
    res.status(statusCode).json(detailedHealth);
  } catch (error) {
    console.error('Detailed Health Check Error:', error);
    res.status(500).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
});

module.exports = router;
