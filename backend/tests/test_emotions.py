import pytest
from app.models.emotions import detect_emotions
from app.services.preprocessor import clean_text

pytestmark = pytest.mark.asyncio

async def test_emotion_detection_joy():
    text, _ = clean_text("I am so incredibly happy today!")
    emotions = await detect_emotions(text)
    top_emo = emotions[0]['label']
    assert top_emo in ("joy", "neutral")

async def test_emotion_detection_anger():
    text, _ = clean_text("This makes me furious and I hate it.")
    emotions = await detect_emotions(text)
    top_emo = emotions[0]['label']
    assert top_emo in ("anger", "neutral")

async def test_emotion_detection_fear():
    text, _ = clean_text("I'm terrified of what might happen.")
    emotions = await detect_emotions(text)
    top_emo = emotions[0]['label']
    assert top_emo in ("fear", "neutral")

async def test_emotion_detection_emojis():
    text, _ = clean_text("\U0001f62d\U0001f62d\U0001f62d")
    emotions = await detect_emotions(text)
    top_emo = emotions[0]['label']
    assert top_emo in ("sadness", "neutral")

async def test_emotion_detection_empty():
    emotions = await detect_emotions("")
    top_emo = emotions[0]['label']
    assert top_emo == "neutral"
    assert emotions[0]['score'] == 1.0
