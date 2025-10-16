import re

def detect_intent(normalized_query: str) -> str:
    """
    A simple rule-based intent detection system.
    This can be expanded with more sophisticated logic or a trained model.
    """
    query_tokens = normalized_query.split()
    
    # Rule-based intent classification
    if any(word in query_tokens for word in ["forecast", "predict", "future"]):
        return "FORECAST"
    elif any(word in query_tokens for word in ["compare", "vs", "versus"]):
        return "COMPARISON"
    elif any(word in query_tokens for word in ["summary", "summarize", "overview", "total", "average"]):
        return "SUMMARIZATION"
    elif any(word in query_tokens for word in ["how many", "what is the", "which", "list", "show"]):
        return "LIST_RETRIEVAL"
    else:
        return "UNKNOWN"

import re

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
    """
    Suggests a visualization type based on the query intent and data types.
    `df_columns_types` would be a dict like {'col_name': 'numeric', 'col_name2': 'categorical'}
    For this example, we'll keep it simple.
    """
    if intent in ["LIST_RETRIEVAL", "SUMMARIZATION"] and len(mentioned_columns) >= 2:
        return "bar_chart"
    if intent == "FORECAST":
        return "line_chart"
    return "none"