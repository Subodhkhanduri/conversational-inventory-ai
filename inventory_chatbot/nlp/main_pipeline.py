from .basic_analyzer import normalize_text, find_column_keywords
from .advanced_analyzer import detect_intent, extract_entities, suggest_chart_type

def process_query(query: str, columns: list[str]) -> dict:
    """
    Orchestrates the full NLP pipeline from raw query to structured output.
    
    Args:
        query (str): The raw user query.
        columns (list[str]): The list of column names from the inventory DataFrame.

    Returns:
        dict: A structured dictionary containing the analysis results.
    """
    # 1. Basic Analysis
    normalized_query = normalize_text(query)
    mentioned_columns = find_column_keywords(normalized_query, columns)
    
    # 2. Advanced Analysis
    intent = detect_intent(normalized_query)
    entities = extract_entities(normalized_query)
    
    # In a real app, you would determine column types from the DataFrame itself.
    # For now, we'll pass an empty dict for demonstration.
    chart_suggestion = suggest_chart_type(intent, mentioned_columns, {})
    
    # 3. Assemble the structured result
    nlp_result = {
        "raw_query": query,
        "normalized_query": normalized_query,
        "intent": intent,
        "mentioned_columns": mentioned_columns,
        "entities": entities,
        "chart_suggestion": chart_suggestion
    }
    
    return nlp_result