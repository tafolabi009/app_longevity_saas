#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create needed directories
mkdir -p ./static/models

# Copy any example models if available
if [ -d "../model_training/example_models" ]; then
  cp -r ../model_training/example_models/* ./static/models/
fi 
