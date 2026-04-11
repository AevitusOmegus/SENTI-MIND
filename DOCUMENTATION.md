# SENTI-MIND Project Documentation

## Project Overview

SENTI-MIND is an AI-powered mental health text analysis application that detects emotional states and clinical risks (depression, anxiety, suicidal thoughts, etc.) and provides compassionate AI-generated coping strategies.

**Location:** `C:\Users\Aeonis\Documents\GitHub\SENTI-MIND`

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                               FRONTEND (React + Vite)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ EmotionChart │  │  RiskBadge   │  │ InsightModal │  │  AnalysisForm  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ HTTP POST /api/v1/analysis/
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (FastAPI)                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                           API Layer (app/api/analysis.py)               │ │
│  │  POST /api/v1/analysis/ → analyze_text()                              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│  ┌─────────────────────────────────┼─────────────────────────────────────┐ │
│  │                    Service Pipeline (Parallel/Sync)                  │ │
│  │                                                                     │ │
│  │   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐              │ │
│  │   │ Preprocessor │ │    NER       │ │   Clinical   │              │ │
│  │   │ (clean_text) │ │ (extract)    │ │  Classifier  │              │ │
│  │   └──────────────┘ └──────────────┘ │ (predict)    │              │ │
│  │                                     └──────────────┘              │ │
│  │   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐              │ │
│  │   │    Emotion   │ │  Risk Engine │ │     LLM      │              │ │
│  │   │  (detect)    │ │  (assess)    │ │  (insight)   │              │ │
│  │   └──────────────┘ └──────────────┘ └──────────────┘              │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐│
│  │                         Model Layer                                   ││
│  │  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐   ││
│  │  │ LinearSVC +     │  │ HuggingFace      │  │ OpenRouter       │   ││
│  │  │ TF-IDF          │  │ distilroberta    │  │ mimo-v2-omni     │   ││
│  │  │ (Clinical)      │  │ (Emotion)        │  │ (Insights)       │   ││
│  │  └─────────────────┘  └──────────────────┘  └──────────────────┘   ││
│  └────────────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.x | UI framework |
| Vite | 4.x | Build tool & dev server |
| TailwindCSS | 3.x | Styling |
| Recharts | 2.x | Radar chart for emotions |
| Lucide React | Latest | Icons |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.100+ | Web framework |
| Uvicorn | Latest | ASGI server |
| scikit-learn | 1.3+ | LinearSVC, TF-IDF, CalibratedClassifierCV |
| spaCy | 3.x | Named Entity Recognition |
| httpx | 0.24+ | Async HTTP client |
| joblib | 1.3+ | Model serialization |
| pandas | 2.x | Data manipulation |
| numpy | 1.24+ | Numerical operations |

### External APIs
| Service | Model/Endpoint | Purpose |
|---------|---------------|---------|
| HuggingFace | `j-hartmann/emotion-english-distilroberta-base` | 7-class emotion detection |
| OpenRouter | `xiaomi/mimo-v2-omni` | LLM insight generation |

---

## File Structure

```
SENTI-MIND/
├── backend/                              # FastAPI Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                       # FastAPI app entry point
│   │   ├── api/
│   │   │   ├── __init__.py               # API router aggregator
│   │   │   └── analysis.py               # Main POST /analysis endpoint
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                 # Settings (env vars)
│   │   │   └── constants.py              # Thresholds, categories
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── classifier.py             # ClinicalClassifier (LinearSVC)
│   │   │   ├── emotions.py               # HuggingFace emotion detection
│   │   │   ├── llm.py                    # OpenRouter insight generation
│   │   │   └── schemas.py                # Pydantic request/response models
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── ner.py                    # spaCy entity extraction
│   │       ├── preprocessor.py           # Text cleaning
│   │       ├── risk_engine.py            # Original risk assessment
│   │       └── risk_engine_improved.py   # Enhanced risk assessment
│   ├── data/                             # Model artifacts & training data
│   │   ├── Combined Data.csv             # 1,050 training samples (7 classes)
│   │   ├── sentiment_model_improved.joblib  # Trained LinearSVC (98.6%)
│   │   ├── vectorizer_improved.joblib    # TF-IDF vectorizer
│   │   └── model_metadata.json           # Training metrics
│   ├── scripts/
│   │   ├── generate_training_data.py    # Synthetic data generator
│   │   ├── migrate_to_improved_model.py  # Model migration utility
│   │   └── train_model_improved.py       # Training pipeline
│   ├── tests/
│   │   ├── test_preprocessor.py          # Preprocessor unit tests
│   │   ├── test_risk_engine.py         # Risk engine tests
│   │   └── test_risk_engine_improved.py # Enhanced risk engine tests
│   ├── model_evaluation.py               # Manual evaluation script
│   └── requirements.txt                  # Python dependencies
├── frontend/                             # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── EmotionChart.jsx        # Radar chart (Recharts)
│   │   │   ├── InsightModal.jsx        # AI insight display
│   │   │   └── RiskBadge.jsx           # Risk level indicator
│   │   ├── hooks/
│   │   │   └── useAnalysis.js          # React hook for API calls
│   │   ├── services/
│   │   │   └── api.js                  # Axios/Fetch wrapper
│   │   ├── App.jsx                     # Main app component
│   │   └── main.jsx                      # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── docs/                                 # Documentation
    └── DATA_VISUALIZATION_STRATEGY.md    # UI/UX guidelines

```

---

## Component Details

### 1. Analysis Pipeline (`app/api/analysis.py`)

**Entry Point:** `POST /api/v1/analysis/`

**Flow:**
1. Receive `AnalysisRequest` (text input)
2. Preprocess text (`clean_text`)
3. Run parallel analysis:
   - **Emotions**: `detect_emotions()` → HuggingFace API
   - **Clinical**: `classifier.predict()` → Local LinearSVC
   - **NER**: `extract_entities()` → spaCy
4. Calculate **Risk**: `assess_risk()` combines clinical + emotions + keywords
5. Generate **Insight**: `generate_insight()` → OpenRouter LLM (if API key set)
6. Return `AnalysisResponse`

**Key Code:**
```python
@router.post("/", response_model=AnalysisResponse)
async def analyze_text(payload: AnalysisRequest):
    cleaned_text, emoji_tokens = clean_text(raw_text)
    emotions = await detect_emotions(cleaned_text)
    clinical = classifier.predict(cleaned_text)
    entities = extract_entities(cleaned_text)
    risk = assess_risk(cleaned_text, emotions, clinical)
    insight = await generate_insight(cleaned_text, emotions, clinical, risk)
    return AnalysisResponse(...)
```

---

### 2. Clinical Classifier (`app/models/classifier.py`)

**Class:** `ClinicalClassifier`

**Purpose:** Classify text into 7 mental health categories

**Pipeline:**
1. **Preprocessing** (`ClinicalTextPreprocessor`):
   - Lowercase, strip
   - Negation handling: `"not happy"` → `NEG_not_happy`
   - Crisis markers: `"suicide"` → adds `CRISIS_suicide_W10`
   - Mental health term markers: `"depression"` → `DEP_depression`

2. **Vectorization**: TF-IDF (15K features, 1-3 grams, sublinear TF)

3. **Classification**: Calibrated LinearSVC → probability estimates

**Output:**
```python
{
    "category": "Depression",
    "confidence": 0.876,
    "top_categories": [
        {"category": "Depression", "confidence": 0.876},
        {"category": "Suicidal", "confidence": 0.123},
        ...
    ]
}
```

**Model Files:**
- `data/sentiment_model_improved.joblib` (calibrated LinearSVC)
- `data/vectorizer_improved.joblib` (TF-IDF)

**Training:** Run `scripts/train_model_improved.py` with `data/Combined Data.csv`

---

### 3. Emotion Detection (`app/models/emotions.py`)

**Function:** `async def detect_emotions(text: str) → list[dict]`

**API:** HuggingFace Inference API

**Model:** `j-hartmann/emotion-english-distilroberta-base`

**Output (7 emotions):**
```python
[
    {"label": "joy", "score": 0.968},
    {"label": "neutral", "score": 0.019},
    {"label": "sadness", "score": 0.008},
    {"label": "anger", "score": 0.001},
    {"label": "surprise", "score": 0.001},
    {"label": "fear", "score": 0.001},
    {"label": "disgust", "score": 0.001},
]
```

**Configuration:** Set `HF_API_TOKEN` in `.env`

---

### 4. Risk Engine (`app/services/risk_engine.py` and `risk_engine_improved.py`)

**Function:** `assess_risk(text, emotions, clinical) → dict`

**Calculation (Improved Version):**
```
Risk Score = (clinical_score * 0.50) + (keyword_score * 0.35) + (emotion_score * 0.15)
```

**Components:**
- **Clinical** (50%): Confidence if category is Suicidal/Depression/Anxiety
- **Keywords** (35%): Crisis keywords with severity weights
- **Emotions** (15%): sadness/fear → higher risk

**Crisis Keywords (weighted):**
- High (1.0): suicide, kill myself, end my life, want to die
- Medium (0.7): hopeless, worthless, no reason to live
- Low (0.3): depressed, anxious, stressed

**Output:**
```python
{
    "level": "high",          # low | medium | high | critical
    "score": 0.85,
    "triggers": ["suicide", "hopeless"],
    "safety_protocol": True   # If suicidal confidence > 0.70
}
```

---

### 5. LLM Insight (`app/models/llm.py`)

**Function:** `async def generate_insight(text, emotions, clinical, risk) → str`

**API:** OpenRouter (`xiaomi/mimo-v2-omni`)

**Prompt Template:**
```
You are a compassionate mental-health analyst.
Analyzed text: "{text}"
- Top emotions: {emotions}
- Clinical classification: {category} ({confidence})
- Risk level: {level}
- Crisis keywords: {triggers}

Respond with:
**Insight:** [2-3 sentence empathetic observation]
**Coping Strategies:**
1. [Specific strategy]
2. [Specific strategy]
```

**Fallback:** If no API key, returns generic empathetic response

---

### 6. Schemas (`app/models/schemas.py`)

**Key Models:**

```python
class AnalysisRequest(BaseModel):
    text: str  # User input

class AnalysisResponse(BaseModel):
    raw_text: str
    preprocessed_text: str
    emotions: List[EmotionResult]       # From HuggingFace
    clinical: ClinicalResult            # From LinearSVC
    entities: List[EntityResult]        # From spaCy
    risk: RiskAssessment                # Calculated
    insight: str                        # From LLM
```

---

## Configuration

### Environment Variables (`.env`)

```bash
# Required
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxx  # HuggingFace token

# Optional (for LLM insights)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxx   # OpenRouter API key
GEMINI_API_KEY=xxxxx                      # Alternative LLM

# App
SECRET_KEY=change-me-in-production
ALLOWED_ORIGINS=http://localhost:5173

# Model Paths (optional)
SENTIMIND_MODEL_PATH=data/sentiment_model_improved.joblib
SENTIMIND_VECTORIZER_PATH=data/vectorizer_improved.joblib
```

---

## Data Flow

### Request Flow (Single Analysis)

```
User Input
    │
    ▼
[Frontend] POST /api/v1/analysis/ {text: "I feel sad"}
    │
    ▼
[Backend] app/api/analysis.py::analyze_text()
    │
    ├─► [Preprocessor] clean_text()
    │   └─ Remove URLs, normalize whitespace, handle emojis
    │
    ├─► [Emotion Model] detect_emotions() ────────────► HuggingFace API
    │   └─ Returns: [{joy: 0.01}, {sadness: 0.98}, ...]
    │
    ├─► [Clinical Model] classifier.predict()
    │   ├─ Preprocess: negation + crisis markers
    │   ├─ TF-IDF vectorize
    │   └─ LinearSVC predict_proba
    │   └─ Returns: {category: "Depression", confidence: 0.87, top_categories: [...]}
    │
    ├─► [NER] extract_entities()
    │   └─ spaCy: en_core_web_sm
    │   └─ Returns: [{text: "work", label: "ORG"}]
    │
    ├─► [Risk Engine] assess_risk()
    │   ├─ Clinical (50%) + Keywords (35%) + Emotions (15%)
    │   └─ Returns: {level: "high", score: 0.75, triggers: [...]}
    │
    └─► [LLM] generate_insight() ───────────────────► OpenRouter
        └─ Returns: "**Insight:** You seem to be struggling...\n**Coping Strategies:**..."
    │
    ▼
[Response] AnalysisResponse JSON
    │
    ▼
[Frontend] Display: EmotionChart, RiskBadge, InsightModal
```

---

## Training Pipeline

### Data Format (`data/Combined Data.csv`)

```csv
statement,status
"I feel empty and hopeless",Depression
"My heart races with anxiety",Anxiety
"I want to end my life",Suicidal
"Work is overwhelming",Stress
...
```

**Classes (7 total):**
- Depression (150 samples)
- Anxiety (150 samples)
- Suicidal (150 samples)
- Stress (150 samples)
- Bipolar (150 samples)
- Normal (150 samples)
- Personality disorder (150 samples)

**Total:** 1,050 samples

### Training Script (`scripts/train_model_improved.py`)

```python
# Pipeline
TextPreprocessor → TfidfVectorizer(ngram_range=(1,3), max_features=15000)
                → CalibratedClassifierCV(LinearSVC())

# Evaluation
- Train/test split: 80/20 stratified
- Cross-validation: 5-fold stratified
- Metrics: accuracy, macro F1, per-class F1

# Output
- sentiment_model_improved.joblib
- vectorizer_improved.joblib
- model_metadata.json
```

**Run Training:**
```bash
cd backend
python scripts/train_model_improved.py
```

---

## Testing

### Run Tests

```bash
cd backend
pytest tests/
```

### Manual Evaluation

```bash
cd backend
python model_evaluation.py
```

### Test Coverage
- `test_preprocessor.py`: Emoji, URL, whitespace handling
- `test_risk_engine.py`: Risk level calculations
- `test_risk_engine_improved.py`: Negation, crisis keywords

---

## Frontend Integration

### API Client (`frontend/src/services/api.js`)

```javascript
const API_URL = "http://localhost:8000/api/v1";

export async function analyzeText(text) {
    const response = await fetch(`${API_URL}/analysis/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
    });
    return response.json();
}
```

### Key Components

1. **EmotionChart** (`EmotionChart.jsx`)
   - Recharts RadarChart
   - Displays 7 emotions as radar
   - Props: `emotions` array

2. **RiskBadge** (`RiskBadge.jsx`)
   - Shows risk level (low/medium/high/critical)
   - Progress bar with color coding
   - Crisis triggers as pills
   - Props: `level`, `score`, `triggers`, `safety_protocol`

3. **InsightModal** (`InsightModal.jsx`)
   - Markdown-formatted AI insight
   - Coping strategies section

---

## Security Considerations

1. **CORS**: Configured in `main.py` via `ALLOWED_ORIGINS`
2. **API Keys**: Stored in `.env`, never committed
3. **Input Validation**: Pydantic schemas validate requests
4. **Rate Limiting**: Not implemented (add via middleware if needed)
5. **Safety Protocol**: Hardcoded at 70% suicidal threshold

---

## Performance

### Model Performance

| Model | Accuracy | Latency |
|-------|----------|---------|
| Clinical (LinearSVC) | 98.6% | ~10ms local |
| Emotion (HF API) | 95%+ | ~500ms API |
| Risk Engine | N/A | ~5ms local |
| LLM Insight | N/A | ~2s API |

### Bottlenecks
- HuggingFace API call (~500ms)
- OpenRouter API call (~2s)
- Mitigation: Both are async and can be cached

---

## Troubleshooting

### Common Issues

1. **Model not found**
   - Check `data/sentiment_model_improved.joblib` exists
   - Run `scripts/migrate_to_improved_model.py`

2. **HuggingFace API error**
   - Verify `HF_API_TOKEN` in `.env`
   - Check token has inference access

3. **spaCy model missing**
   - Run: `python -m spacy download en_core_web_sm`

4. **CORS errors**
   - Update `ALLOWED_ORIGINS` in `.env` or `main.py`

---

## Future Improvements

1. **Caching**: Add Redis for emotion API responses
2. **Rate Limiting**: Implement per-user limits
3. **Analytics**: Track model performance over time
4. **Fine-tuning**: Retrain on user feedback
5. **Offline Mode**: Download emotion model locally
6. **Conversation History**: Context-aware risk assessment

---

## Quick Reference

### Start Backend
```bash
cd backend
.venv\Scripts\activate  # Windows
uvicorn app.main:app --reload
```

### Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### Run Evaluation
```bash
cd backend
python model_evaluation.py
```

### Generate Training Data
```bash
cd backend
python scripts/generate_training_data.py
```

---

**Last Updated:** 2026-04-10  
**Version:** 2.0 (Improved Model)  
**Maintainer:** Future agents - read this before making changes!
