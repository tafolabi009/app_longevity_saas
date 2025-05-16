# Deploying to Render

This directory contains the configuration needed to deploy the App Longevity SaaS backend to [Render](https://render.com).

## Deployment Steps

1. **Create a Render account** if you don't have one at [render.com](https://render.com)

2. **Connect your GitHub repository** to Render:
   - Go to your Render dashboard
   - Click "New" and select "Blueprint"
   - Connect your GitHub account and select your repository
   - Select the repository with your App Longevity SaaS code

3. **Provide the YAML path**:
   - When prompted, specify the location of your render.yaml file
   - Enter: `deploy/render/render.yaml`

4. **Configure your services**:
   - Render will automatically detect the services defined in the YAML
   - Review the settings and make any necessary adjustments
   - Click "Apply" to start the deployment

5. **Check deployment status**:
   - Render will build and deploy your application
   - This may take a few minutes
   - Once complete, you'll get a URL for your backend API

## Configuration

The `render.yaml` file configures:

1. A web service for the backend API using Python
2. A PostgreSQL database (free tier)

## Environment Variables

The deployment automatically sets up:

- `SECRET_KEY`: A securely generated random key for JWT signing
- `DATABASE_URL`: The connection string to your Render PostgreSQL database
- `DEFAULT_MODEL`: The default ML model to use

## Custom Domain

After deployment, you can set up a custom domain:

1. Go to your service in the Render dashboard
2. Click on "Settings" then "Custom Domains"
3. Follow the instructions to add your domain

## Troubleshooting

- **Build failures**: Check the build logs in Render dashboard
- **Runtime errors**: Check the service logs in Render dashboard
- **Database issues**: Ensure the database service is running correctly

## Local Testing

To test your Render deployment configuration locally:

```bash
# Navigate to the backend directory
cd backend

# Install gunicorn
pip install gunicorn

# Start the server using the same command as in render.yaml
gunicorn main:app -k uvicorn.workers.UvicornWorker
``` 
