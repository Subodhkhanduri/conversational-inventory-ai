# inventory_chatbot/analytics/core_analytics.py

import pandas as pd
from typing import Dict
from fastapi import UploadFile

SESSION_DATASETS: Dict[str, pd.DataFrame] = {}

def load_dataset_for_session(file: UploadFile, session_id: str) -> pd.DataFrame:
    print("\n--- UPLOAD DEBUG ---")
    print("session_id received on UPLOAD:", session_id)

    df = pd.read_csv(file.file)
    SESSION_DATASETS[session_id] = df

    print("Stored session IDs now:", list(SESSION_DATASETS.keys()))
    print("----------------------\n")

    return df


def get_session_dataframe(session_id: str) -> pd.DataFrame | None:
    print("\n--- ASK DEBUG ---")
    print("session_id received on ASK:", session_id)
    print("Available session IDs:", list(SESSION_DATASETS.keys()))

    df = SESSION_DATASETS.get(session_id)

    if df is None:
        print("❌ NO dataset found for this session!")
    else:
        print("✅ Dataset FOUND for session.")

    print("----------------------\n")
    return df
