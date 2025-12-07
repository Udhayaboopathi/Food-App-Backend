#!/bin/bash
# Build script to ensure app folder is included in Vercel deployment

echo "📦 Preparing Vercel deployment..."

# Ensure app directory exists in the build
if [ -d "app" ]; then
    echo "✅ app/ directory found"
    ls -la app/ | head -10
else
    echo "❌ app/ directory not found!"
    exit 1
fi

echo "🚀 Build preparation complete"
