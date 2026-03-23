# SENTI-MIND

**SentiMind** is an intelligent AI-powered application designed to analyze text and detect the user's emotional state and any clinical risks (like stress, anxiety, or suicidal thoughts). It then provides compassionate, AI-generated coping strategies to help the user.

## ✨ What Does This App Do?
When you type a sentence into SentiMind, it goes through a "pipeline" (a set of steps) to understand you:
1. **Cleans the text**: Removes noise and translates emojis into words.
2. **Detects Emotion**: Uses an AI model to figure out if you're sad, angry, happy, etc.
3. **Clinical Classification**: A custom trained Machine Learning model determines if the text shows signs of Depression, Anxiety, Stress, etc.
4. **Risk Assessment**: Checks for crisis keywords to see if you need immediate professional help.
5. **AI Insight**: An LLM (Large Language Model) reads all this data and replies with a warm, empathetic response and actionable coping strategies!

## 🛠️ The Tech Stack (What We Used)
- **Frontend (The User Interface)**: 
  - **React & Vite**: To build a fast, dynamic webpage.
  - **TailwindCSS**: For rendering beautiful "glassmorphism" styles and colorful UI components seamlessly.
- **Backend (The Brain)**:
  - **FastAPI & Uvicorn**: A blazing-fast Python server that handles the web requests securely.
  - **Scikit-Learn & Pandas**: For training our clinical Machine Learning classifier (`train_model.py`).
  - **spaCy**: For understanding subjects and contexts in sentences.
  - **OpenRouter**: The cloud AI provider that writes the empathetic insights.

---

## 🚀 How To Set It Up (Step-by-Step for Beginners)

### 1. Setting up the Backend (The Brain)
Open your terminal and type these commands exactly:

1. Go into the backend folder:
   `cd backend`
2. Create a virtual environment (a safe bubble for Python packages):
   `python -m venv .venv`
3. Activate the bubble (Windows):
   `.venv\Scripts\activate`
4. Install all the required brain power (dependencies):
   `pip install -r requirements.txt`
5. Download the language module:
   `python -m spacy download en_core_web_sm`
6. Rename the `.env.example` file to `.env` and put your API keys inside.
7. Start the server securely (this exact command bypasses annoying Windows errors!):
   `.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`

### 2. Setting up the Frontend (The Interface)
Open a **new** terminal window and type:

1. Go into the frontend folder:
   `cd frontend`
2. Install all the user interface packages:
   `npm install`
3. Run the website!
   `npm run dev`

Now, open your web browser and go to `http://localhost:5173`. You're done! 🎉
