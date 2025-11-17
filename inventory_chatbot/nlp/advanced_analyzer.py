import re

FORECAST_KEYWORDS = [
    "forecast", "predict", "future demand", "future sales",
    "next", "upcoming", "prediction", "projection",
    "predict demand", "predict sales", "next day", "next week"
]

PLOT_KEYWORDS = [
    "plot", "chart", "graph", "visualize", "show graph", "bar chart",
    "line chart", "scatter", "visualization"
]

SUMMARY_KEYWORDS = [
    "how many", "count", "total", "sum", "number of",
    "list items", "show all"
]


def detect_intent(text: str) -> str:
    t = text.lower()

    for kw in FORECAST_KEYWORDS:
        if kw in t:
            return "FORECAST"

    for kw in PLOT_KEYWORDS:
        if kw in t:
            return "PLOT"

    for kw in SUMMARY_KEYWORDS:
        if kw in t:
            return "SUMMARY"

    return "GENERAL_CHAT"


def extract_entities(text: str) -> dict:
    t = text.lower()

    item = None
    store = None
    horizon = 7

    m = re.search(r"item\s+(\d+)", t)
    if m:
        item = int(m.group(1))

    s = re.search(r"store\s+(\d+)", t)
    if s:
        store = int(s.group(1))

    h = re.search(r"next\s+(\d+)\s+days", t)
    if h:
        horizon = int(h.group(1))

    return {"item": item, "store": store, "horizon": horizon}


def suggest_chart_type(text: str) -> str:
    t = text.lower()
    if "bar" in t:
        return "bar"
    if "line" in t:
        return "line"
    return "line"
