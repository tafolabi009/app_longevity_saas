# App Longevity SaaS

This is a SaaS application that uses machine learning models to predict the longevity and success potential of mobile applications. The system analyzes various factors to provide insights about how long an app might remain viable in the marketplace.

## Project Structure

```
app_longevity_saas/
├── backend/           # FastAPI backend
│   ├── api/           # API endpoints
│   ├── core/          # Core configuration
│   ├── models/        # Database models & ML model wrappers
│   ├── services/      # Business logic services
│   └── static/        # Static files including ML models
├── frontend/          # Frontend application
├── model_training/    # Notebooks and scripts for model training
└── deploy/            # Deployment configurations
```

## Features

- Prediction of app longevity based on app name
- Detailed analysis of factors affecting app success
- User management system
- API for integrating predictions into other systems
- Support for different machine learning models

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL (optional, SQLite for development)

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/app_longevity_saas.git
cd app_longevity_saas
```

2. Set up the backend:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

3. Set up the frontend:

```bash
cd ../frontend
npm install
npm run dev
```

## Machine Learning Models

### Model Directory Structure

The project supports multiple machine learning models for predictions. Models are stored in the following locations:

- Primary location: `backend/static/models/`
- Additional locations can be specified via environment variables

### Model Files

Each model consists of the following files:

- **Main model file**: `modelname.joblib`, `modelname.pkl`, `.h5`, or `.keras`
- **Scaler**: `scaler.joblib` or `modelname_scaler.joblib` (optional)
- **Preprocessor**: `preprocessor.pkl` or `modelname_preprocessor.pkl` (optional)
- **Feature importances**: `modelname_feature_importance.json` or `feature_importance.json` (optional)
- **Metadata**: `modelname_metadata.json` or `model_metadata.json` (optional)

### Swapping Models

To use a different machine learning model:

1. **Simple replacement**: Place your new model files in the `backend/static/models/` directory, using the same names as the existing files.

2. **Adding a new model**: Place your new model files with a unique name in the models directory. The system will automatically discover and make it available for selection through the API.

3. **Changing the default model**: Set the `DEFAULT_MODEL` environment variable to the name of your model file.

4. **Using models from different locations**: Set the `ADDITIONAL_MODEL_PATHS` environment variable to a comma-separated list of directories where models can be found.

Example environment configuration:

```bash
DEFAULT_MODEL=advanced_model.joblib
ADDITIONAL_MODEL_PATHS=/path/to/more/models,/another/path/with/models
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/register`: Register a new user
- `POST /api/v1/auth/login`: Login and get access token
- `GET /api/v1/auth/me`: Get current user info

### Predictions

- `POST /api/v1/predictions/predict`: Predict app longevity
  - Parameters:
    - `app_name`: Name of the app to analyze
    - `compare_competitors`: (Optional) Whether to compare with competitors
    - `model_name`: (Optional) Specific model to use for prediction
- `GET /api/v1/predictions/predictions`: Get user's prediction history
- `GET /api/v1/predictions/predictions/{prediction_id}`: Get details of a specific prediction
- `DELETE /api/v1/predictions/predictions/{prediction_id}`: Delete a prediction
- `GET /api/v1/predictions/available-models`: Get list of available prediction models

## Environment Variables

| Variable               | Description                       | Default                                     |
| ---------------------- | --------------------------------- | ------------------------------------------- |
| SECRET_KEY             | Secret key for JWT                | development_secret_key_change_in_production |
| DATABASE_URL           | Database connection URL           | sqlite:///./app_longevity.db                |
| DEFAULT_MODEL          | Default model file name           | rf_model.joblib                             |
| ADDITIONAL_MODEL_PATHS | Additional directories for models | ""                                          |

## Areas for Enhancement

1. **Model Training Pipeline**: Create a CI/CD pipeline for model training and automatic deployment
2. **Performance Optimization**: Improve prediction response time and caching
3. **More Data Sources**: Integrate more app store data sources and metrics
4. **User Interface**: Enhanced visualization of prediction results
5. **Extended Competitor Analysis**: More detailed competitor comparison features
6. **Batch Processing**: Support for analyzing multiple apps simultaneously
7. **Export and Reporting**: Add ability to export prediction results
8. **Premium Features**: Add additional features for premium users
9. **User Feedback Loop**: Collect user feedback on prediction accuracy

## License

[License information]

## Contributors

[Contributors] 
