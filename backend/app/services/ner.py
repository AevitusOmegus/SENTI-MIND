import spacy

_nlp = None

# Only keep entity types that are semantically meaningful for mental health journaling
_RELEVANT_TYPES = {"PERSON", "ORG", "GPE", "EVENT", "DATE", "TIME", "WORK_OF_ART"}

_MAX_CHARS = 1000


def _load_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def extract_entities(text: str) -> list[dict]:
    nlp = _load_nlp()
    doc = nlp(text[:_MAX_CHARS])
    seen: set[str] = set()
    entities: list[dict] = []
    for ent in doc.ents:
        if ent.label_ not in _RELEVANT_TYPES:
            continue
        key = (ent.text.lower(), ent.label_)
        if key in seen:
            continue
        seen.add(key)
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char,
        })
    return entities
