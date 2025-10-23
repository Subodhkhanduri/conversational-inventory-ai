import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

def plot_bar_chart(data: pd.DataFrame, x_col: str, y_col: str, title: str, xlabel: str, ylabel: str):
    """
    Generates a bar chart and returns it as a base64 encoded string.
    """
    plt.figure(figsize=(10, 6))
    plt.bar(data[x_col], data[y_col])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Encode buffer to base64 string
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    return img_str

def plot_line_chart(data: pd.DataFrame, x_col: str, y_col: str, title: str, xlabel: str, ylabel: str):
    """
    Generates a line chart and returns it as a base64 encoded string.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(data[x_col], data[y_col], marker='o')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()

    return img_str

def plot_forecast_chart(dates, sales_data, title):
    """
    Generates a line chart specifically for forecast data.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(dates, sales_data, marker='o', linestyle='-', color='b')
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Predicted Sales")
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Encode buffer to base64 string
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    return img_str
