import pytest
import re
from app.services.preprocessor import clean_text, _VARIATION_SELECTOR_RE


def test_emoji_mapping():
    text, tokens = clean_text("I am so sad 😭")
    assert "heavy sobbing" in text
    assert "heavy sobbing" in tokens
    assert "😭" not in text


def test_url_stripping():
    text, _ = clean_text("Check this out https://example.com/help")
    assert "https://example.com/help" not in text
    assert "Check this out" in text


def test_whitespace_cleanup():
    text, _ = clean_text("Too    much   space\n\n\nlinebreaks")
    assert "Too much space linebreaks" == text


def test_combined_cleaning():
    raw = "HELP!!! 🆘 I'm drowning 🌊. Visit http://crisis.org"
    cleaned, tokens = clean_text(raw)
    assert "SOS emergency" in cleaned
    assert "wave overwhelming" in cleaned
    assert "http://crisis.org" not in cleaned
    assert "drowning" in cleaned
    assert len(tokens) == 2


def test_multi_codepoint_emoji_no_variation_selector():
    # ☹️ is U+2639 + U+FE0F (variation selector-16)
    # Old char-by-char loop would match ☹ and leave \uFE0F dangling
    text, tokens = clean_text("feeling ☹️ today")
    assert "frowning" in tokens
    assert not _VARIATION_SELECTOR_RE.search(text), "Dangling variation selector found in output"


def test_skull_crossbones_multi_codepoint():
    # ☠️ is U+2620 + U+FE0F
    text, tokens = clean_text("☠️")
    assert "skull and crossbones" in tokens
    assert not _VARIATION_SELECTOR_RE.search(text)


def test_red_heart_multi_codepoint():
    # ❤️ is U+2764 + U+FE0F
    text, tokens = clean_text("I love ❤️ life")
    assert "red heart love" in tokens
    assert not _VARIATION_SELECTOR_RE.search(text)


def test_no_emoji_unchanged():
    text, tokens = clean_text("Plain text with no emoji.")
    assert text == "Plain text with no emoji."
    assert tokens == []


def test_multiple_emoji_ordering():
    # Multi-codepoint variants should be matched before single-codepoint base
    text, tokens = clean_text("😭😢")
    assert tokens == ["heavy sobbing", "crying"]
