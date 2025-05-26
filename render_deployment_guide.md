# Render.com Deployment Guide

## Overview

This document provides instructions for deploying the E-ID File Signing application to Render.com.

## Prerequisites

- A Render.com account
- The GitHub repository: https://github.com/vikram-io/e-id-threema-fileshare

## Deployment Steps

### Option 1: Deploy from the Render Dashboard

1. Log in to your Render.com account
2. Click "New +" and select "Web Service"
3. Connect your GitHub account and select the repository
4. Configure the service:
   - Name: e-id-file-signing
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn src.main:app`
5. Add the following environment variables:
   - THREEMA_IDENTITY: *3MAGW01
   - THREEMA_SECRET: &YwrCeMju6ApTHNRpa6p
6. Click "Create Web Service"

### Option 2: Deploy using render.yaml (Blueprint)

1. Log in to your Render.com account
2. Go to the "Blueprints" section
3. Click "New Blueprint Instance"
4. Connect your GitHub account and select the repository
5. Render will automatically detect the render.yaml file and configure the service
6. Review the configuration and click "Apply"

## Environment Variables

The application requires the following environment variables:

- `THREEMA_IDENTITY`: The Threema Gateway ID (*3MAGW01)
- `THREEMA_SECRET`: The Threema Gateway secret (&YwrCeMju6ApTHNRpa6p)

## Persistent Storage

The application uses a disk for persistent storage of uploaded files:
- Mount path: /src/static/uploads
- Size: 1GB

## Accessing the Application

Once deployed, your application will be available at:
`https://e-id-file-signing.onrender.com`

## Monitoring and Logs

You can monitor the application and view logs from the Render dashboard:
1. Go to your Render dashboard
2. Select the e-id-file-signing service
3. Click on the "Logs" tab to view application logs

## Troubleshooting

If you encounter issues with the deployment:
1. Check the build logs for any errors
2. Verify that all environment variables are correctly set
3. Ensure the disk is properly mounted
4. Check the application logs for runtime errors
