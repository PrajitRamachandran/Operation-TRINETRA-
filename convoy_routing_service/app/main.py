from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # 1. Import the middleware
from .db.database import engine, Base
from .api import endpoints

# Create all database tables based on the models
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Defense Convoy Routing System",
    description="A comprehensive backend for dynamic, secure, and intelligent convoy mission planning and monitoring.",
    version="1.0.0"
)

# 2. Add the CORS middleware to the app
# This must be added before you include the routers
# In your main.py file

origins = [
    "http://localhost:5500",  # For when you type 'localhost'
    "http://127.0.0.1:5500", # For when you type '127.0.0.1'
    # Keep other origins you might need, like for React development
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(endpoints.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Convoy Routing System API is online."}