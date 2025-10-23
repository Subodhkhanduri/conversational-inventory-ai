from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pandas as pd
import io
import json

from inventory_chatbot.nlp.main_pipeline import process_query
from inventory_chatbot.services.llm_service import LLMService
from inventory_chatbot.analytics.forecasting import predict_sales_with_lgbm
# Import our new plotting function
from inventory_chatbot.analytics.visualization import plot_forecast_chart

# --- In-memory "Database" ---
uploaded_data = {}

# --- Pydantic Models for Request Body ---
class ChatMessage(BaseModel):
    role: str
    content: str

class AskRequest(BaseModel):
    session_id: str
    messages: list[ChatMessage]

# --- Router Setup ---
router = APIRouter()
llm_service = LLMService()

@router.post("/upload")
async def upload_inventory_file(file: UploadFile = File(...)):
    # ... (This function remains unchanged)
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
async def ask_question(request_body: AskRequest):
    """
    Receives the chat history, processes the query, and streams a response.
    If a forecast is requested, it also generates and streams a chart.
    """
    session_id = request_body.session_id
    messages = [msg.model_dump() for msg in request_body.messages]

    if session_id not in uploaded_data:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a file first.")
    if not messages:
        raise HTTPException(status_code=400, detail="No messages provided.")

    df = uploaded_data[session_id]
    latest_query = messages[-1]['content']
    
    nlp_result = process_query(latest_query, df.columns.tolist())
    
    system_prompt = f"""
    You are an expert inventory analyst. You are helpful, friendly, and concise.
    You are analyzing an inventory file with the following columns: {', '.join(df.columns)}.
    """
    
    llm_messages = []

    if nlp_result['intent'] == 'FORECAST':
        store_id = nlp_result['entities'].get('store_id')
        item_id = nlp_result['entities'].get('item_id')
        
        if store_id is not None and item_id is not None:
            forecast = predict_sales_with_lgbm(store_id=store_id, item_id=item_id, days_to_forecast=10)
            
            if forecast:
                forecast_str = "\n".join([f"- {d}: {s} units" for d, s in zip(forecast['dates'], forecast['predicted_sales'])])
                prompt = f"""
                A machine learning model has generated a 10-day sales forecast for item {item_id} at store {store_id}. 
                Present this forecast to the user. Be friendly and clear.

                Forecasted Sales:
                {forecast_str}

                Conclude by reminding the user this is a prediction.
                """
                llm_messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
                
                # 1. Generate the plot
                chart_b64 = plot_forecast_chart(
                    dates=forecast['dates'],
                    sales_data=forecast['predicted_sales'],
                    title=f"10-Day Sales Forecast for Item {item_id} at Store {store_id}"
                )
                
                # 2. Get the LLM stream
                llm_stream = llm_service.generate_streaming_response(llm_messages)
                
                # 3. Create a new generator to chain the LLM stream and the chart data
                async def response_generator(stream, chart_json):
                    for chunk in stream:
                        yield chunk
                    # At the very end, yield the JSON for the chart
                    yield chart_json
                
                chart_json_string = json.dumps({"chart_b64": chart_b64})
                
                return StreamingResponse(response_generator(llm_stream, chart_json_string), media_type="text/event-stream")
            
            else:
                llm_messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "Tell the user the forecasting model couldn't be loaded. Check server logs."}]
        else:
            llm_messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "Tell the user they must provide both a store ID and an item ID for forecasting, like 'forecast sales for item 50 in store 10'."}]
    
    else:
        # General conversation (no chart)
        llm_messages = [{"role": "system", "content": system_prompt}] + messages
    
    # Return a streaming response for general chat
    return StreamingResponse(llm_service.generate_streaming_response(llm_messages), media_type="text/event-stream")
