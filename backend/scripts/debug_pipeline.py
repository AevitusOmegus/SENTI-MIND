import asyncio
import os
import sys
import traceback
from dotenv import load_dotenv

# Load env before imports
load_dotenv()

# Add current dir to path for imports
sys.path.append(os.getcwd())

from app.services.preprocessor import clean_text
from app.models.emotions import detect_emotions
from app.models.classifier import classifier
from app.services.ner import extract_entities
from app.services.risk_engine import assess_risk
from app.models.llm import generate_insight

async def test_pipeline():
    with open("debug_output.txt", "w", encoding="utf-8") as f:
        f.write("--- STARTING DEBUG PIPELINE ---\n")
        text = "I feel so hopeless 😭. I want to end it all."
        f.write(f"Input text: {text}\n\n")
        
        try:
            f.write("L0: Cleaning text...\n")
            cleaned, emojis = clean_text(text)
            f.write(f"L0 OK: {cleaned}\n\n")
            
            f.write("L1: Detecting emotions...\n")
            # This might be the source of 410 if HF API changed
            emotions = await detect_emotions(cleaned)
            f.write(f"L1 OK: {emotions[:2]}\n\n")
            
            f.write("L2: Clinical Classifier...\n")
            classifier.load()
            clinical = classifier.predict(cleaned)
            f.write(f"L2 OK: {clinical['category']}\n\n")
            
            f.write("L3: Context Mapper (NER)...\n")
            entities = extract_entities(cleaned)
            f.write(f"L3 OK: Found {len(entities)} entities\n\n")
            
            f.write("L4: Risk Engine...\n")
            risk = assess_risk(cleaned, emotions, clinical)
            f.write(f"L4 OK: Level={risk['level']}\n\n")
            
            f.write("L5: LLM (Gemini)...\n")
            # This might be the source of 410 if model name is wrong/retired
            insight = await generate_insight(cleaned, emotions, clinical, risk)
            f.write(f"L5 OK: insight length={len(insight)}\n")
            f.write(f"L5 Preview: {insight[:100]}...\n\n")  # type: ignore
            
            f.write("--- PIPELINE SUCCESSFUL ---\n")
            
        except Exception as e:
            f.write("\n❌ ERROR IN LAYER:\n")
            f.write(str(e) + "\n")
            f.write(traceback.format_exc())
            print(f"FAILED: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
