import pandas as pd

def summarize_data(df: pd.DataFrame, column: str):
    """
    Generates descriptive statistics for a specific numerical column in the DataFrame.
    """
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return None
    
    summary = {
        "mean": df[column].mean(),
        "median": df[column].median(),
        "std_dev": df[column].std(),
        "min": df[column].min(),
        "max": df[column].max(),
        "total": df[column].sum()
    }
    return summary

def filter_below_threshold(df: pd.DataFrame, level_col: str, threshold_col: str):
    """
    Filters the DataFrame to find rows where the level is below the threshold.
    [cite_start]This directly corresponds to queries like "Which products are below reorder threshold?"[cite: 461].
    """
    if level_col not in df.columns or threshold_col not in df.columns:
        return pd.DataFrame() # Return empty DataFrame if columns are missing
    
    low_stock_items = df[df[level_col] < df[threshold_col]]
    return low_stock_items

def get_top_n_items(df: pd.DataFrame, column: str, n: int = 5, ascending: bool = False):
    """
    Gets the top N items from the DataFrame based on a specific column.
    """
    if column not in df.columns:
        return pd.DataFrame()
        
    return df.sort_values(by=column, ascending=ascending).head(n)

def aggregate_by_category(df: pd.DataFrame, category_col: str, value_col: str, agg_func: str = 'sum'):
    """
    Groups data by a category and applies an aggregation function (e.g., sum, mean).
    [cite_start]Useful for queries like "What is the total stock per warehouse?"[cite: 471].
    """
    if category_col not in df.columns or value_col not in df.columns:
        return None
        
    return df.groupby(category_col)[value_col].agg(agg_func).reset_index()