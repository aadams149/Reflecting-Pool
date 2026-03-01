"""Tests for VADER sentiment analysis used in app.py."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def get_sentiment(text: str) -> float:
    """Mirror of the app.py get_sentiment function."""
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(text)["compound"]


class TestSentiment:
    def test_positive_text(self):
        score = get_sentiment("I had a wonderful, amazing, fantastic day!")
        assert score > 0.3

    def test_negative_text(self):
        score = get_sentiment("This was a terrible, awful, horrible experience.")
        assert score < -0.3

    def test_neutral_text(self):
        score = get_sentiment("The meeting is at three o'clock.")
        assert -0.3 <= score <= 0.3

    def test_empty_string(self):
        score = get_sentiment("")
        assert score == 0.0

    def test_score_range(self):
        for text in ["Great!", "Terrible!", "Okay", "I love this", "I hate this"]:
            score = get_sentiment(text)
            assert -1.0 <= score <= 1.0

    def test_mixed_sentiment(self):
        score = get_sentiment("The food was great but the service was terrible.")
        assert -0.5 <= score <= 0.5
