# SENTI-MIND

**SentiMind** is an intelligent AI-powered application designed to analyze text and detect the user's emotional state and any clinical risks (like stress, anxiety, or suicidal thoughts). It then provides compassionate, AI-generated coping strategies to help the user.

## Description
When you type a sentence into SentiMind, it goes through a "pipeline" (a set of steps) to understand you:
1. **Cleans the text**: Removes noise and translates emojis into words.
2. **Detects Emotion**: Uses an AI model to figure out if you're sad, angry, happy, etc.
3. **Clinical Classification**: A custom trained Machine Learning model determines if the text shows signs of Depression, Anxiety, Stress, etc.
4. **Risk Assessment**: Checks for crisis keywords to see if you need immediate professional help.
5. **AI Insight**: An LLM (Large Language Model) reads all this data and replies with a warm, empathetic response and actionable coping strategies!

## Team member
- **Abdullah Mushtaq** (23L-0892)

## Tech Stack
- **Frontend**: React, Vite, TailwindCSS (for glassmorphism style UI)
- **Backend**: Python, FastAPI, Uvicorn, Scikit-Learn, Pandas, spaCy
- **AI/ML**: LinearSVC (Custom trained clinical classifier), HuggingFace (Emotion extraction), OpenRouter/Xiaomi (LLM insight generation)
- **Database**: *(Planned for future sprints)* Supabase (PostgreSQL)

---

## How to run using link and locally

### 🌍 Live Link (Deployed)
You can instantly access and interact with the live, deployed application without installing anything:
👉 **[SentiMind Live Web App](https://senti-mind-mocha.vercel.app/)**

### 💻 Running Locally
Open your terminal and follow these steps to run the fully functioning pipeline on your own machine.

#### 1. Setting up the Backend
> [!CAUTION]
> **Python 3.11 or 3.12 required.** Python 3.14 is currently NOT supported by our core Machine Learning dependencies.

1. Go into the backend folder:
   `cd backend`
2. Create and activate a virtual environment (Windows):
   `python -m venv .venv`
   `.venv\Scripts\activate`
3. Install dependencies:
   `pip install -r requirements.txt`
4. Download the language module:
   `python -m spacy download en_core_web_sm`
5. Rename the `.env.example` file to `.env` and put your API keys inside.
6. Start the server securely (this exact command bypasses annoying Windows errors!):
   `.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`

#### 2. Setting up the Frontend
Open a **new** terminal window and type:

1. Go into the frontend folder:
   `cd frontend`
2. Install the user interface packages:
   `npm install`
3. Run the website!
   `npm run dev`

Now, open your web browser and go to `http://localhost:5173`. You're done! 🎉
