"""
SENTI-MIND Clinical Text Preprocessor (v3)
Single source of truth — used by both training and inference.

Features
--------
- Contraction expansion
- Extended negation scope (3-word window)
- Intensity markers (amplifiers / diminishers)
- Temporal markers (past-tense recovery detection)
- Crisis indicator injection (high-severity only)
- Whitespace normalisation
"""

import re

from app.core.constants import CRISIS_KEYWORDS

# ── Contraction expansion ──────────────────────────────────────────────
CONTRACTIONS = {
    "i'm": "i am", "i've": "i have", "i'll": "i will", "i'd": "i would",
    "you're": "you are", "you've": "you have", "you'll": "you will",
    "you'd": "you would", "he's": "he is", "he'll": "he will",
    "he'd": "he would", "she's": "she is", "she'll": "she will",
    "she'd": "she would", "it's": "it is", "it'll": "it will",
    "we're": "we are", "we've": "we have", "we'll": "we will",
    "we'd": "we would", "they're": "they are", "they've": "they have",
    "they'll": "they will", "they'd": "they would",
    "isn't": "is not", "aren't": "are not", "wasn't": "was not",
    "weren't": "were not", "hasn't": "has not", "haven't": "have not",
    "hadn't": "had not", "doesn't": "does not", "don't": "do not",
    "didn't": "did not", "won't": "will not", "wouldn't": "would not",
    "shan't": "shall not", "shouldn't": "should not",
    "can't": "can not", "cannot": "can not",
    "couldn't": "could not", "mustn't": "must not",
    "let's": "let us", "that's": "that is", "who's": "who is",
    "what's": "what is", "here's": "here is", "there's": "there is",
    "where's": "where is", "when's": "when is", "why's": "why is",
    "how's": "how is",
    "ain't": "am not",
}
_CONTRACTION_RE = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in CONTRACTIONS) + r")\b",
    re.IGNORECASE,
)

# ── Negation handling ──────────────────────────────────────────────────
NEGATION_TRIGGERS = {
    "not", "no", "never", "neither", "nor", "nowhere", "nothing",
    "nobody", "none", "hardly", "scarcely", "barely",
}
# Negation scope ends at punctuation or clause boundary
_NEG_SCOPE_END = re.compile(r"[.!?,;:\-—]")
NEG_WINDOW = 3  # words after the trigger to negate

# ── Intensity markers ─────────────────────────────────────────────────
AMPLIFIERS = {
    "extremely", "incredibly", "absolutely", "completely", "totally",
    "utterly", "deeply", "severely", "profoundly", "intensely",
    "very", "really", "so", "terribly", "horribly", "desperately",
    "overwhelmingly", "unbearably", "excessively", "immensely",
}
DIMINISHERS = {
    "slightly", "somewhat", "a bit", "a little", "mildly",
    "marginally", "faintly", "barely", "hardly", "scarcely",
    "sort of", "kind of", "a tad",
}

# ── Temporal markers ──────────────────────────────────────────────────
PAST_RECOVERY_PATTERNS = [
    r"\bi used to\b",
    r"\bi was\b",
    r"\bi had been\b",
    r"\bi have been\b.*\bbut\b.*\b(better|improved|recovered|fine|good|great|okay)\b",
    r"\bin the past\b",
    r"\blast year\b",
    r"\byears ago\b",
    r"\bmonths ago\b",
    r"\bi overcame\b",
    r"\bi got over\b",
    r"\bi recovered\b",
    r"\bi am (better|fine|good|okay|great) now\b",
    r"\bi'm (better|fine|good|okay|great) now\b",
    r"\bno longer\b",
    r"\bnot anymore\b",
]
_PAST_RECOVERY_RES = [re.compile(p, re.IGNORECASE) for p in PAST_RECOVERY_PATTERNS]

# Crisis indicators imported from constants.py (single source of truth)
# Only use high-severity entries (weight >= 0.7) for preprocessing markers
CRISIS_INDICATORS = {k: v for k, v in CRISIS_KEYWORDS.items() if v >= 0.7}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Public API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def expand_contractions(text: str) -> str:
    """Expand English contractions to their full form."""
    return _CONTRACTION_RE.sub(
        lambda m: CONTRACTIONS.get(m.group(0).lower(), m.group(0)), text
    )


def apply_negation_scope(text: str) -> str:
    """
    Mark words within a negation window with NEG_ prefix.
    E.g. "I am not feeling sad" → "I am not NEG_feeling NEG_sad"
    """
    words = text.split()
    result = []
    neg_remaining = 0

    for word in words:
        clean = re.sub(r"[^\w]", "", word).lower()
        # Check for clause boundary — reset negation
        if _NEG_SCOPE_END.search(word):
            neg_remaining = 0
            result.append(word)
            continue

        if clean in NEGATION_TRIGGERS:
            neg_remaining = NEG_WINDOW
            result.append(word)
            continue

        if neg_remaining > 0:
            result.append(f"NEG_{word}")
            neg_remaining -= 1
        else:
            result.append(word)

    return " ".join(result)


def add_intensity_markers(text: str) -> str:
    """Inject INTENSE_ / DIM_ markers for amplifiers and diminishers."""
    text_lower = text.lower()
    for amp in AMPLIFIERS:
        if amp in text_lower:
            text += " INTENSE_marker "
            break
    for dim in DIMINISHERS:
        if dim in text_lower:
            text += " DIM_marker "
            break
    return text


def add_temporal_markers(text: str) -> str:
    """Inject PAST_RECOVERY marker if the text references past/recovered states."""
    for pat in _PAST_RECOVERY_RES:
        if pat.search(text):
            text += " PAST_RECOVERY "
            break
    return text


def add_crisis_markers(text: str) -> str:
    """Inject CRISIS_ markers for high-severity phrases."""
    text_lower = text.lower()
    for indicator, weight in CRISIS_INDICATORS.items():
        if indicator in text_lower:
            tag = indicator.replace(" ", "_").replace("-", "_")
            text += f" CRISIS_{tag}_W{int(weight * 10)} "
    return text


def has_negated_crisis(text: str) -> bool:
    """
    Check whether crisis terms appear in a negated context.
    E.g. "I am not suicidal" → True
    """
    text_lower = text.lower()
    # Quick patterns for negated crisis language
    negated_patterns = [
        r"\b(not|no|never|don'?t|doesn'?t|didn'?t|isn'?t|aren'?t|wasn'?t|am not)\b.{0,15}\b(suicidal|suicide|kill myself|end my life|want to die|self.?harm)\b",
        r"\b(suicidal|suicide)\b.{0,10}\b(not|no|never)\b",
    ]
    for pat in negated_patterns:
        if re.search(pat, text_lower):
            return True
    return False


def preprocess(text: str) -> str:
    """
    Full preprocessing pipeline.

    Steps:
    1. Lowercase + strip
    2. Expand contractions
    3. Apply negation scope
    4. Add intensity markers
    5. Add temporal markers
    6. Add crisis markers
    7. Normalise whitespace
    """
    if not isinstance(text, str):
        return ""

    text = text.lower().strip()
    text = expand_contractions(text)
    text = apply_negation_scope(text)
    text = add_intensity_markers(text)
    text = add_temporal_markers(text)
    text = add_crisis_markers(text)

    # Normalise whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text
