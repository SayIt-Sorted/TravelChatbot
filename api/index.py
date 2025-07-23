"""
WSGI entry point for Vercel deployment
"""
from main import app

# Export the FastAPI app for Vercel
handler = app 