from fastapi import FastAPI
from .api import endpoints
from .config import settings

app = FastAPI(
    title="Conversational AI for Inventory Management API",
    description="Backend for the Streamlit Inventory Chatbot.",
    version="1.0.0"
)

# Include the API router
app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Inventory Chatbot Backend!"}
