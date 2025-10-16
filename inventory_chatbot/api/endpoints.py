from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
import io

from inventory_chatbot.nlp.main_pipeline import process_query
from inventory_chatbot.services.llm_service import LLMService
# Import the new forecasting function
from inventory_chatbot.analytics.forecasting import predict_sales_with_lgbm

# We will create a simple in-memory "database" to hold the uploaded file for this example.
uploaded_data = {}

router = APIRouter()
llm_service = LLMService()

@router.post("/upload")
# ... (this function remains unchanged)
async def upload_inventory_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")
    try:
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        session_id = file.filename 
        uploaded_data[session_id] = df
        return {"session_id": session_id, "columns": list(df.columns), "num_rows": len(df)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")

@router.post("/ask")
async def ask_question(session_id: str = Form(...), query: str = Form(...)):
    """
    Receives a user's query, processes it, calls the appropriate analytics
    function (like forecasting), and streams a response from the LLM.
    """
    if session_id not in uploaded_data:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a file first.")
    
    df = uploaded_data[session_id]
    nlp_result = process_query(query, df.columns.tolist())
    
    # --- Integration Logic for Custom Forecasting ---
    if nlp_result['intent'] == 'FORECAST':
        store_id = nlp_result['entities'].get('store_id')
        item_id = nlp_result['entities'].get('item_id')
        
        if store_id is not None and item_id is not None:
            # Call your new forecasting function
            forecast = predict_sales_with_lgbm(store_id=store_id, item_id=item_id, days_to_forecast=10)
            
            if forecast:
                # Create a detailed prompt for the LLM with the forecast data
                forecast_str = "\n".join([f"- {d}: {s} units" for d, s in zip(forecast['dates'], forecast['predicted_sales'])])
                prompt = f"""
                You are an expert inventory analyst. A machine learning model has generated a sales forecast. 
                Present the following 10-day sales forecast for item {item_id} at store {store_id} to the user in a clear and friendly manner.

                Forecasted Sales:
                {forecast_str}

                Conclude by reminding the user that this is a prediction and should be used as a guideline.
                """
            else:
                prompt = "I couldn't generate a forecast. The forecasting model might not be loaded correctly. Please check the backend server logs."
        else:
            prompt = "To provide a forecast, please tell me the specific store number and item number, for example: 'predict sales for item 50 in store 10'."
    else:
        # --- Default Logic for General Queries ---
        prompt = f"""
        You are an expert inventory analyst. Given the following data summary and user query, provide a helpful and concise response.
        Data Columns Available: {', '.join(df.columns)}
        User's Raw Query: "{query}"
        Analyzed Intent from NLP Pipeline: {nlp_result['intent']}
        Key Entities Found: {nlp_result['entities']}
        Based on this, please answer the user's query.
        """
        
    return StreamingResponse(llm_service.generate_streaming_response(prompt), media_type="text/event-stream")