import spacy
from spacy.tokens import Doc


class NLPProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")

    def analyze_descriptions(self, text: str) -> dict:
        """Extract semantic insights from descriptions"""
        doc = self.nlp(text)
        return {
            "entities": [(ent.text, ent.label_) for ent in doc.ents],
            "verbs": [token.lemma_ for token in doc if token.pos_ == "VERB"],
            "keywords": [chunk.text for chunk in doc.noun_chunks]
        }

    def suggest_property_name(self, original: str) -> str:
        """Improve property names using NLP"""
        doc = self.nlp(original)
        return "".join([
            token.text.capitalize()
            for token in doc
            if not token.is_stop
        ])