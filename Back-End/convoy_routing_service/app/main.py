from fastapi import FastAPI
from .db.database import engine, Base
from .api import endpoints

# Create all database tables based on the models
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Defense Convoy Routing System",
    description="A comprehensive backend for dynamic, secure, and intelligent convoy mission planning and monitoring.",
    version="1.0.0"
)

# Include all API routes
app.include_router(endpoints.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Convoy Routing System API is online."}