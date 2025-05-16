# Deploying to Netlify

This directory contains the configuration needed to deploy the App Longevity SaaS frontend to [Netlify](https://netlify.com).

## Deployment Steps

1. **Create a Netlify account** if you don't have one at [netlify.com](https://netlify.com)

2. **Connect your GitHub repository** to Netlify:
   - Go to your Netlify dashboard
   - Click "Add new site" -> "Import an existing project"
   - Connect your GitHub account and select your repository
   - Select the repository with your App Longevity SaaS code

3. **Configure the build settings**:
   - Base directory: `frontend`
   - Build command: `npm ci && npm run build` 
   - Publish directory: `dist`
   - Note: These settings are already in the `netlify.toml` file

4. **Configure environment variables**:
   - Click on "Site settings" -> "Environment variables"
   - Add variable `VITE_API_BASE_URL` with the URL of your backend API deployed on Render
   - Example: `https://app-longevity-saas-backend.onrender.com/api/v1`
   - Note: This is already set in the `netlify.toml` file but you may need to update it

5. **Deploy the site**:
   - Click "Deploy site"
   - Wait for the build and deployment to complete
   - Once finished, Netlify will provide a URL for your frontend

## Configuration

The `netlify.toml` file configures:

1. Build settings for your frontend
2. Environment variables for API communication
3. Redirect rules for SPA routing

## Custom Domain

To set up a custom domain on Netlify:

1. Go to "Site settings" -> "Domain management"
2. Click "Add custom domain"
3. Follow the instructions to set up your domain

## Troubleshooting

- **Build failures**: Check the build logs in Netlify dashboard
- **API connection issues**: Verify that the `VITE_API_BASE_URL` is set correctly
- **CORS errors**: Ensure your backend allows requests from your Netlify domain

## Local Testing

To test your Netlify configuration locally:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Continuous Deployment

Netlify automatically deploys when you push changes to your repository. By default, it:

- Deploys the `main` branch to production
- Creates previews for pull requests
- Can be configured to deploy other branches 
