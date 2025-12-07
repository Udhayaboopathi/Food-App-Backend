#!/bin/bash
# Pre-deployment script to copy app folder into api for Vercel

echo "📦 Preparing Vercel deployment..."
echo "Copying app folder into api folder..."

# Remove old copy if exists
if [ -d "api/app" ]; then
    rm -rf api/app
fi

# Copy app folder into api
cp -r app api/app

echo "✅ App folder copied successfully!"
echo "📁 api/app is ready for Vercel deployment"
