// API configuration
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Feature flags
export const FEATURES = {
  COMPETITOR_ANALYSIS: true, // Whether to show competitor analysis feature
  VISUALIZATION: true,      // Whether to show visualization features
};

// App constants
export const APP_NAME = 'App Longevity Predictor';
export const APP_DESCRIPTION = 'Predict the success and lifespan of mobile apps using advanced AI models';
export const MAX_FREE_PREDICTIONS = 10; // Maximum predictions per day on free tier
