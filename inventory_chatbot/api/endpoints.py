# inventory_chatbot/api/endpoints.py

from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
import base64
import re

from inventory_chatbot.analytics.core_analytics import (
    load_dataset_for_session,
    get_session_dataframe,
)

from inventory_chatbot.services.llm_service import LLMService
from inventory_chatbot.analytics.forecasting import ForecastingTool
from inventory_chatbot.analytics.visualization import VisualizationTool

router = APIRouter()
llm = LLMService()
forecast_tool = ForecastingTool()
viz = VisualizationTool()


# ----------------------------------------------------------
# UPLOAD CSV
# ----------------------------------------------------------
@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), session_id: str = Form(...)):
    df = load_dataset_for_session(file, session_id)

    return {
        "message": "File uploaded successfully",
        "session_id": session_id,
        "columns": list(df.columns)
    }


# ----------------------------------------------------------
# ASK ENDPOINT (FINAL + CLEAN)
# ----------------------------------------------------------
@router.post("/ask")
async def ask_question(request: Request):

    data = await request.form()
    query = data.get("query")
    session_id = data.get("session_id")

    if not query:
        return JSONResponse({"error": "Missing query"}, status_code=400)

    if not session_id:
        return JSONResponse({"error": "Missing session_id"}, status_code=400)

    df = get_session_dataframe(session_id)
    if df is None:
        return JSONResponse({"error": "No dataset found"}, status_code=400)

    query_lower = query.lower()

    # ======================================================
    # 1️⃣ EXTRACT ITEM & STORE FROM QUERY
    # ======================================================
    # Finds all numbers in the query
    matches = re.findall(r"\b\d+\b", query_lower)

    item = store = None
    if len(matches) >= 2:
        item = int(matches[0])
        store = int(matches[1])

    # ======================================================
    # 2️⃣ FORECASTING INTENT
    # ======================================================
    if "forecast" in query_lower or "predict" in query_lower:

        png_bytes, forecast_values = forecast_tool.generate_forecast(
            df,
            item=item,
            store=store,
            periods=10
        )

        chart_b64 = base64.b64encode(png_bytes).decode("utf-8")

        return {
            "response": forecast_values,
            "chart_b64": chart_b64
        }

    # ======================================================
    # 3️⃣ VISUALIZATION INTENTS
    # ======================================================
    if any(w in query_lower for w in ["trend", "visual", "plot", "chart", "pattern"]):

        png_bytes = viz.generate_sales_trend_plot(df)

        chart_b64 = base64.b64encode(png_bytes).decode("utf-8")

        return {
            "response": "Here is the trend visualization based on your dataset.",
            "chart_b64": chart_b64
        }

    # ======================================================
    # 4️⃣ DEFAULT — Send data summary + query to LLM
    # ======================================================
    sample_text = df.head(5).to_string()
    columns_text = ", ".join(df.columns)

    context_prompt = f"""
You are an Inventory Management AI Assistant.

The user uploaded an inventory dataset with these columns:
{columns_text}

First 5 rows:
{sample_text}

Answer the user's question **using only the dataset**.

User question:
{query}
"""

    response_text = llm.chat(context_prompt)

    return {"response": response_text}
