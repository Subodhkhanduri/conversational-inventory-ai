from .basic_analyzer import clean_text
from .advanced_analyzer import detect_intent, extract_entities, suggest_chart_type


class NLPProcessor:

    def analyze(self, query: str):
        cleaned = clean_text(query)
        intent = detect_intent(cleaned)
        entities = extract_entities(cleaned)
        chart_type = suggest_chart_type(cleaned)

        return {
            "intent": intent,
            "entities": entities,
            "chart_type": chart_type
        }
