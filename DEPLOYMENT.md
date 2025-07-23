# 🚀 Vercel Deployment Guide

This guide will help you deploy your Travel Booking AI backend to Vercel.

## Prerequisites

- GitHub account
- Vercel account (free tier works)
- OpenAI API key
- Optional: SMTP credentials for email sending

## Step 1: Prepare Your Repository

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Ensure these files are in your repo:**
   - `api/index.py` - WSGI entry point
   - `main.py` - FastAPI application
   - `vercel.json` - Vercel configuration
   - `requirements.txt` - Python dependencies
   - `runtime.txt` - Python version
   - All other backend files

## Step 2: Deploy to Vercel

1. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**

2. **Click "New Project"**

3. **Import your GitHub repository**
   - Select your travel chatbot repository
   - Vercel will auto-detect it's a Python project

4. **Configure Environment Variables**
   - Click "Environment Variables"
   - Add these variables:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     SMTP_EMAIL=your_email@example.com (optional)
     SMTP_PASSWORD=your_email_password (optional)
     AMADEUS_API_KEY=your_amadeus_key (optional)
     AMADEUS_API_SECRET=your_amadeus_secret (optional)
     ```

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete (2-3 minutes)

## Step 3: Get Your Backend URL

After deployment, Vercel will give you a URL like:
```
https://your-project-name.vercel.app
```

Your API endpoints will be available at:
- `https://your-project-name.vercel.app/api/chat`
- `https://your-project-name.vercel.app/api/health`
- `https://your-project-name.vercel.app/docs`

## Step 4: Update Frontend

Update your frontend to use the new backend URL:

**Option A: URL Parameter**
```
frontend.html?api=https://your-project-name.vercel.app
```

**Option B: Edit HTML directly**
```javascript
const API_BASE_URL = 'https://your-project-name.vercel.app';
```

## Step 5: Test Your Deployment

1. **Test the health endpoint:**
   ```bash
   curl https://your-project-name.vercel.app/api/health
   ```

2. **Test the chat endpoint:**
   ```bash
   curl -X POST https://your-project-name.vercel.app/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}'
   ```

3. **Open your frontend** and test the full flow

## Troubleshooting

### Common Issues:

1. **Build Fails**
   - Check that all files are committed to GitHub
   - Verify `requirements.txt` is correct
   - Check environment variables are set

2. **CORS Errors**
   - The backend is configured to accept requests from common frontend domains
   - If using a custom domain, add it to the CORS origins in `main.py`

3. **API Key Issues**
   - Ensure environment variables are set correctly in Vercel
   - Check the API key is valid

4. **Import Errors**
   - Make sure all Python files are in the repository
   - Check that `api/index.py` imports from `main.py` correctly

### Environment Variables Reference:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `SMTP_EMAIL` | No | Email for sending travel packages |
| `SMTP_PASSWORD` | No | Email password |
| `AMADEUS_API_KEY` | No | Amadeus API key for flight search |
| `AMADEUS_API_SECRET` | No | Amadeus API secret |

## Production Considerations

1. **Custom Domain**
   - Add a custom domain in Vercel settings
   - Update CORS origins in `main.py`

2. **Environment Variables**
   - Use Vercel's environment variable management
   - Different values for production/staging

3. **Monitoring**
   - Vercel provides basic analytics
   - Consider adding logging for debugging

4. **Scaling**
   - Vercel auto-scales based on traffic
   - Free tier has generous limits

## Next Steps

After successful deployment:

1. **Test thoroughly** with your frontend
2. **Monitor logs** in Vercel dashboard
3. **Set up custom domain** if needed
4. **Configure monitoring** for production use

Your backend is now live and ready to serve your frontend! 🎉 