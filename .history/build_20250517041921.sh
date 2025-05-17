#!/usr/bin/env bash
# exit on error
set -o errexit

# Go to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Create needed directories
mkdir -p ./static/models

# Copy any example models if available
if [ -d "../model_training/example_models" ]; then
  cp -r ../model_training/example_models/* ./static/models/
fi

# Install additional dependencies for production
pip install gunicorn 
