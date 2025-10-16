import re

def normalize_text(query: str) -> str:
    """
    Cleans the user query by converting to lowercase, removing punctuation,
    and collapsing whitespace.
    """
    query = query.lower()
    query = re.sub(r'[^\w\s]', '', query) # Remove punctuation
    query = re.sub(r'\s+', ' ', query).strip() # Collapse whitespace
    return query

def find_column_keywords(normalized_query: str, columns: list[str]) -> list[str]:
    """
    Identifies which of the DataFrame's columns are mentioned in the query.
    This helps in making the system "schema-aware".
    """
    mentioned_columns = []
    for col in columns:
        # Normalize column name for matching (e.g., "Stock Level" -> "stock level")
        normalized_col = col.lower().replace('_', ' ')
        if normalized_col in normalized_query:
            mentioned_columns.append(col)
    return mentioned_columns