import re

def detect_intent(normalized_query: str) -> str:
    """
    A more robust, rule-based intent detection system.
    """
    
    # --- MODIFICATION START ---
    # Check for substrings first for key intents like FORECAST
    # This will catch "forecast", "forecasting", "predict", "prediction", etc.
    if "forecast" in normalized_query or "predict" in normalized_query or "future" in normalized_query:
        return "FORECAST"
    # --- MODIFICATION END ---
    
    # Split into tokens for other rule-based checks
    query_tokens = normalized_query.split()
    
    if any(word in query_tokens for word in ["compare", "vs", "versus"]):
        return "COMPARISON"
    elif any(word in query_tokens for word in ["summary", "summarize", "overview", "total", "average"]):
        return "SUMMARIZATION"
    elif any(word in query_tokens for word in ["how many", "what is the", "which", "list", "show"]):
        return "LIST_RETRIEVAL"
    else:
        return "UNKNOWN"

def extract_entities(normalized_query: str) -> dict:
    """
    Extracts key entities like numbers, store IDs, and item IDs from the query.
    """
    entities = {}
    
    # General number extraction
    numbers = re.findall(r'\d+', normalized_query)
    if numbers:
        entities['numbers'] = [int(n) for n in numbers]
        
    # Specific extraction for store and item
    store_match = re.search(r'store (\d+)', normalized_query)
    if store_match:
        entities['store_id'] = int(store_match.group(1))

    item_match = re.search(r'item (\d+)', normalized_query)
    if item_match:
        entities['item_id'] = int(item_match.group(1))
    
    # Keyword extraction
    if "top" in normalized_query:
        entities['ranking'] = 'top'
    if "bottom" in normalized_query or "lowest" in normalized_query:
        entities['ranking'] = 'bottom'
        
    return entities

def suggest_chart_type(intent: str, mentioned_columns: list, df_columns_types: dict) -> str:
    # This is still just a placeholder, we will implement it next
    if intent == "FORECAST":
        return "line_chart"
    return "none"