"""
LLM/NLP-assisted concept extraction from unstructured Finance/Tax text.

Uses spaCy where available to pull candidate entities (ORG, MONEY, LAW, GPE)
out of a regulatory sentence and map them onto ontology classes. Falls back to
a lightweight regex tagger when the spaCy model is not installed, so the demo
always runs.

This is the "LLM-assisted ontology generation" hook the job flags as a plus:
extracted spans become candidate individuals to be reviewed and asserted into
the graph.
"""
import re

# ontology class each entity label maps to
LABEL_TO_CLASS = {
    "ORG": "LegalEntity",
    "MONEY": "Transaction",
    "LAW": "RegulatoryConcept",
    "GPE": "Jurisdiction",
    "PERCENT": "VATCategory",
}


def extract_spacy(text: str):
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return [(e.text, e.label_, LABEL_TO_CLASS.get(e.label_, "Concept"))
            for e in doc.ents if e.label_ in LABEL_TO_CLASS]


def extract_fallback(text: str):
    """Regex tagger so the demo runs without the spaCy model downloaded."""
    hits = []
    for m in re.finditer(r"\b\d+(?:\.\d+)?\s?%", text):
        hits.append((m.group(), "PERCENT", "VATCategory"))
    for m in re.finditer(r"[€$]\s?\d[\d,\.]*", text):
        hits.append((m.group(), "MONEY", "Transaction"))
    for m in re.finditer(r"\b(?:MiFID II|IFRS \d+|VAT Directive|GDPR|Basel III)\b", text):
        hits.append((m.group(), "LAW", "RegulatoryConcept"))
    for m in re.finditer(r"\b[A-Z][a-zA-Z]+ (?:GmbH|AG|Ltd|Inc|LLC)\b", text):
        hits.append((m.group(), "ORG", "LegalEntity"))
    return hits


def extract(text: str):
    try:
        return extract_spacy(text)
    except Exception:
        return extract_fallback(text)


if __name__ == "__main__":
    sample = (
        "Under the EU VAT Directive, Muster GmbH applied a reduced rate of 7% "
        "to an invoice of €12,500, while IFRS 15 governed the revenue recognition."
    )
    print("Candidate ontology individuals extracted from text:\n")
    for span, label, cls in extract(sample):
        print(f"  {span:<18} [{label:<7}] -> ft:{cls}")
