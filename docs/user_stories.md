# SentiMind - Agile User Stories & NFRs

Based on the implemented features and the 6-layer clinical pipeline developed for SentiMind, here is the breakdown of the completed User Stories, Sub-Stories, and Non-Functional Requirements (NFRs).

---

## 📖 Epic: Core Sentiment & Clinical Analysis Pipeline

### **US1: Text Input and Submission**
**As a** user,
**I want to** input my thoughts and feelings into a clean interface,
**So that** I can receive a rapid analysis of my mental state.
* **Sub-Story 1.1**: Develop a React frontend with a text area for user input.
* **Sub-Story 1.2**: Create a FastAPI backend endpoint (`/analysis/`) to receive the payload.
* **Sub-Story 1.3**: Implement a Layer 0 Preprocessor to clean noise and translate emojis into text before processing.

### **US2: Emotional Spectrum Detection**
**As a** user,
**I want** the system to detect my underlying emotions,
**So that** I can visually understand the complex emotional spectrum of my input.
* **Sub-Story 2.1**: Integrate Hugging Face DistilRoBERTa (Layer 1) to extract 7 core emotional intensities.
* **Sub-Story 2.2**: Build an interactive `EmotionChart` component in the frontend to visually graph the returned emotion scores.

### **US3: Clinical Categorization**
**As a** user,
**I want to** know if my syntax reflects specific clinical conditions,
**So that** I gain awareness of my potential mental health baseline.
* **Sub-Story 3.1**: Train a Custom Machine Learning Classifier (LinearSVC with balanced weights) on Kaggle data to categorize text into 7 states (Anxiety, Depression, Normal, Bipolar, Personality Disorder, Stress, Suicidal).
* **Sub-Story 3.2**: Develop a cross-validation script (`train_model.py`) to systematically fine-tune the model parameters via `GridSearchCV`.

### **US4: Crisis Risk Assessment**
**As a** user or clinician,
**I want** the application to identify critical distress signals,
**So that** high-risk situations are immediately flagged for safety protocols.
* **Sub-Story 4.1**: Implement spaCy NER (Context Mapper) to extract subjects and semantic context.
* **Sub-Story 4.2**: Build a Risk Logic Engine (Layer 4) to calculate a weighted risk score based on suicidal confidence, distress keywords, and fearful/sad emotions.
* **Sub-Story 4.3**: Design a dynamic `RiskBadge` UI component that visually alerts the user to Low, Medium, High, or Critical risk tiers.

### **US5: Compassionate AI Insights & Strategy**
**As a** user in distress,
**I want** personalized, empathetic feedback and coping strategies,
**So that** I have constructive, actionable ways to manage my current state.
* **Sub-Story 5.1**: Integrate a Large Language Model (Layer 5 via OpenRouter) injected with the calculated clinical context to synthesize a compassionate response.
* **Sub-Story 5.2**: Develop an elegant, custom Markdown parser (`InsightModal.jsx`) on the frontend to beautifully style the AI's core insight and bulleted coping strategies using glassmorphism.

---

## ⚙️ Non-Functional Requirements (NFRs)

**1. Performance & Latency:**
- The 6-layer analysis pipeline must process NLP tasks and return the final API payload efficiently.
- Asynchronous integration with external LLMs must include strict timeout fallbacks (e.g., 30s) to prevent the UI from freezing, falling back to a statically generated compassionate response if the LLM fails.

**2. Security & Privacy:**
- API access must be rigorously locked down utilizing explicit Cross-Origin Resource Sharing (CORS) configurations, securely fetching `ALLOWED_ORIGINS` from production environment variables.
- Sensitive API keys (OpenRouter, HuggingFace, JWT Secrets) must be strictly isolated from the codebase via `.env` management.

**3. Deployability & Compatibility:**
- The application backend must be strictly compatible with Python 3.11/3.12 (bypassing specific Pydantic v1 compilation issues in Python 3.14).
- The infrastructure must be fully containerized/dynamically stateless to support zero-downtime automated deployment on Platforms as a Service (Vercel for Frontend, Render for Backend).

**4. Usability & Aesthetics (UI/UX):**
- The frontend must adhere to modern UI/UX principles, specifically utilizing a calming "Sage" color palette and responsive glassmorphism structures via TailwindCSS to minimize user anxiety while interacting with mental health data.
