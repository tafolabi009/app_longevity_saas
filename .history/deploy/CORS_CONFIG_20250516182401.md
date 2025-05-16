# Connecting Netlify Frontend to Render Backend

When deploying your App Longevity SaaS with the frontend on Netlify and backend on Render, you need to properly configure Cross-Origin Resource Sharing (CORS) to ensure they can communicate.

## Updating CORS Configuration

### 1. Add Netlify Domain to Backend CORS Settings

You need to update the Render backend to accept requests from your Netlify domain. Edit the `backend/core/config.py` file:

```python
# CORS
BACKEND_CORS_ORIGINS: list = [
    "http://localhost:3000",  # React dev server
    "http://localhost:8000",  # FastAPI dev server
    "http://localhost",
    "https://localhost",
    "https://app-longevity-predictor.netlify.app",  # Your Netlify domain
    "https://your-custom-domain.com",  # If you have a custom domain
]
```

Replace `app-longevity-predictor.netlify.app` with your actual Netlify domain.

### 2. Set Environment Variables for API URL

In your Netlify dashboard:

1. Go to Site settings > Environment variables
2. Add a variable:
   - Key: `VITE_API_BASE_URL`
   - Value: `https://app-longevity-saas-backend.onrender.com/api/v1`

Replace `app-longevity-saas-backend.onrender.com` with your actual Render domain.

### 3. Configure Frontend API Client

Make sure your frontend code uses the environment variable for API requests. Here's an example:

```javascript
// Example API client configuration
const API_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

async function fetchData(endpoint) {
  const response = await fetch(`${API_URL}/${endpoint}`);
  return response.json();
}
```

## Testing CORS Configuration

After deployment:

1. Open browser developer tools (F12)
2. Go to the Network tab
3. Interact with your app to trigger API requests
4. Check for any CORS errors in the Console tab

## Troubleshooting CORS Issues

If you encounter CORS errors:

### Backend Issues:

1. Verify your CORS configuration is correctly deployed to Render
2. Check Render logs for any errors
3. Ensure your backend is properly accepting OPTIONS preflight requests

### Frontend Issues:

1. Check that your frontend is using the correct API URL
2. Verify environment variables are properly set in Netlify
3. Make sure your authentication headers are properly formatted

### Temporary CORS Testing:

For temporary testing, you can add a more permissive CORS policy (NOT recommended for production):

```python
# CORS - Temporary permissive policy for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
``` 
