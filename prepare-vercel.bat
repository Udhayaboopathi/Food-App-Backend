@echo off
REM Pre-deployment script to copy app folder into api for Vercel

echo 📦 Preparing Vercel deployment...
echo Copying app folder into api folder...

REM Remove old copy if exists
if exist "api\app" (
    rmdir /s /q "api\app"
)

REM Copy app folder into api
xcopy /E /I /Y "app" "api\app"

echo ✅ App folder copied successfully!
echo 📁 api\app is ready for Vercel deployment
