from transformers import pipeline
import requests
from bs4 import BeautifulSoup
import spacy
from collections import Counter
from data_utils import get_ticker

NEWS_API_KEY = "090f7d9ed44a41f4a8e982e5298ff9aa"

def load_models():
    summarizer = pipeline("summarization", model="./models/retro_summarizer")
    finbert = pipeline("text-classification", model="./models/finbert")
    return summarizer, finbert

def summarize_text(text: str, summarizer) -> str:
    """Returns summary as retro-style headline bullets."""
    out = summarizer(text, max_length=130, min_length=30, do_sample=False)
    summary = out[0]["summary_text"]
    bullets = ["► " + s.strip() for s in summary.replace("\n", " ").split(". ") if s]
    return "\n".join(bullets[:5])

def analyze_sentiment(text: str, finbert) -> dict:
    out = finbert(text[:512])[0]  # Truncate for speed
    label = out.get("label", "NEUTRAL").upper()
    score = float(out.get("score", 0.5))
    return {"label": label, "score": score}

# def detect_main_company(text: str, company_list: list) -> str:
#     """Detect main company by highest keyword frequency (simple TF heuristic)."""
#     text_lower = text.lower()
#     freq = {c.lower(): text_lower.count(c.lower()) for c in company_list}
#     main_company = max(freq, key=freq.get)
#     return main_company if freq[main_company] > 0 else None

nlp = spacy.load("en_core_web_sm")  # larger, better NER

def detect_main_company(article_text: str) -> str:
    """
    Detect main company in the article using NER and frequency.
    """
    try:
        doc = nlp(article_text)
        companies = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

        if companies:
            freq = Counter(companies)
            main_company = freq.most_common(1)[0][0]

            # Map to known ticker names using get_ticker
            ticker = get_ticker(main_company)
            if ticker:
                return main_company
        return None
    except Exception as e:
        print(f"Error detecting company: {e}")
        return None



