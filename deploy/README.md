# App Longevity SaaS Deployment Guide

This guide provides step-by-step instructions for deploying the App Longevity SaaS platform using Render for the backend and Netlify for the frontend.

## Deployment Architecture

The deployment setup uses:

- **Backend**: Deployed on [Render](https://render.com) - Python FastAPI application with ML models
- **Frontend**: Deployed on [Netlify](https://netlify.com) - React/Vue frontend application
- **Database**: PostgreSQL database provided by Render

## Deployment Steps Overview

### 1. Backend Deployment to Render

1. Create a Render account
2. Connect your GitHub repository
3. Configure the Render Blueprint using `deploy/render/render.yaml`
4. Deploy the backend service and database

Detailed instructions: [Render Deployment Guide](./render/README.md)

### 2. Frontend Deployment to Netlify

1. Create a Netlify account
2. Connect your GitHub repository
3. Configure the build settings using `deploy/netlify/netlify.toml`
4. Set environment variables to point to your Render backend
5. Deploy the frontend application

Detailed instructions: [Netlify Deployment Guide](./netlify/README.md)

### 3. Connect Frontend and Backend

1. Update CORS settings in the backend to allow requests from the Netlify domain
2. Configure the frontend to use the Render backend URL
3. Test the connection between the two services

Detailed instructions: [CORS Configuration Guide](./CORS_CONFIG.md)

## Deployment Checklist

- [ ] Backend code is ready for production
- [ ] Required ML models are included in the repository or accessible to Render
- [ ] Frontend code is configured to use environment variables for API URLs
- [ ] Database schema is properly set up
- [ ] CORS settings are properly configured

## Testing After Deployment

1. Visit your Netlify URL and ensure the frontend loads
2. Try to register and log in
3. Test the prediction functionality
4. Check that ML models are properly loaded and working

## Monitoring and Maintenance

### Render Backend

- Monitor service logs in the Render dashboard
- Set up alerts for errors or performance issues
- Scale resources as needed based on usage

### Netlify Frontend

- Monitor deploy logs in the Netlify dashboard
- Review analytics to identify any client-side issues
- Set up form handling if you have contact forms

## Troubleshooting Common Issues

- **Backend not accessible**: Check Render logs and ensure service is running
- **Frontend not loading**: Check Netlify build logs for errors
- **API connection issues**: Verify CORS settings and environment variables
- **Database errors**: Check Render database status and connection strings

## Custom Domain Setup

### Option 1: Single Domain for Both Services

1. Purchase a domain (e.g., `app-longevity.com`)
2. Set up the frontend on the root domain (`app-longevity.com`)
3. Set up the backend on a subdomain (`api.app-longevity.com`)
4. Configure DNS records for both services

### Option 2: Separate Domains

1. Set up separate domains for frontend and backend
2. Ensure CORS is properly configured to allow cross-domain requests

## Security Considerations

- Ensure `SECRET_KEY` is securely generated and not committed to the repository
- Enable HTTPS for all communications
- Set up proper authentication and authorization
- Regularly update dependencies to patch security vulnerabilities 
