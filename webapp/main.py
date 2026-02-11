from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import joblib

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

from feature_engineering import compute_features

# -----------------------------
# Load model + scaler
# -----------------------------
xgb_model = joblib.load("xgb_model.pkl")
scaler = joblib.load("scaler.pkl")

app = FastAPI(title="Writing Analytics + Rewrite Coach")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# -----------------------------
# Schemas
# -----------------------------
class TextIn(BaseModel):
    text: str


class CompareIn(BaseModel):
    original: str
    revised: str


# -----------------------------
# Summarizer (offline)
# -----------------------------
def make_summary(text: str, n_sentences: int = 3) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    if len(text.split()) < 80:
        return text  # already short
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = TextRankSummarizer()
    sents = summarizer(parser.document, n_sentences)
    return " ".join(str(s) for s in sents).strip()


# -----------------------------
# Simple writing scores (demo-friendly)
# -----------------------------
def style_scores(feats: dict) -> dict:
    tokens = feats["tokens"]
    sentences = feats["sentences"]
    mtld = feats["mtld"]
    mattr = feats["mattr"]
    repetition = feats["repetition_ratio"]
    punct = feats["punct_ratio"]
    stopw = feats["stopword_ratio"]
    sentence_var = feats["sentence_var"]

    avg_sentence_len = tokens / max(sentences, 1)

    # Clarity: target ~15–25 words/sentence, penalize high variance
    clarity = 100.0
    if avg_sentence_len > 28:
        clarity -= (avg_sentence_len - 28) * 2.0
    if avg_sentence_len < 10:
        clarity -= (10 - avg_sentence_len) * 2.0
    clarity -= min(30.0, sentence_var * 0.6)
    clarity = max(0.0, min(100.0, clarity))

    # Conciseness: penalize repetition
    conciseness = 100.0 - min(60.0, repetition * 120.0)
    conciseness = max(0.0, min(100.0, conciseness))

    # Richness: MTLD + MATTR heuristic
    richness = 0.6 * min(100.0, (mtld / 120.0) * 100.0) + 0.4 * min(100.0, (mattr / 0.85) * 100.0)
    richness = max(0.0, min(100.0, richness))

    # Formality proxy: penalize extreme stopwords + heavy punctuation
    formality = 70.0
    if stopw > 0.62:
        formality -= (stopw - 0.62) * 120.0
    if stopw < 0.42:
        formality -= (0.42 - stopw) * 120.0
    if punct > 0.06:
        formality -= (punct - 0.06) * 800.0
    formality = max(0.0, min(100.0, formality))

    overall = 0.30 * clarity + 0.25 * conciseness + 0.25 * richness + 0.20 * formality
    overall = max(0.0, min(100.0, overall))

    return {
        "overall": round(overall, 1),
        "clarity": round(clarity, 1),
        "conciseness": round(conciseness, 1),
        "richness": round(richness, 1),
        "formality": round(formality, 1),
        "avg_sentence_len": round(avg_sentence_len, 2),
    }


def coaching_tips(feats: dict) -> dict:
    tips = []
    flags = []

    tokens = feats["tokens"]
    sentences = feats["sentences"]
    repetition = feats["repetition_ratio"]
    stopw = feats["stopword_ratio"]
    punct = feats["punct_ratio"]
    sentence_var = feats["sentence_var"]

    avg_sentence_len = tokens / max(sentences, 1)

    if tokens < 80:
        flags.append("Text is short; analysis is less stable.")
        tips.append("Aim for 120–200 words for a better academic-style check.")

    if repetition > 0.35:
        flags.append("High repetition detected.")
        tips.append("Remove repeated phrases and combine similar sentences.")

    if avg_sentence_len > 30:
        flags.append("Sentences may be too long.")
        tips.append("Split long sentences (aim ~15–25 words per sentence).")

    if avg_sentence_len < 10:
        flags.append("Sentences may be choppy.")
        tips.append("Combine short sentences to improve flow.")

    if sentence_var > 40:
        flags.append("Large variation in sentence length.")
        tips.append("Keep sentence lengths more consistent for readability.")

    if stopw > 0.62:
        flags.append("High stopword ratio (may sound less formal).")
        tips.append("Replace filler phrases with specific nouns/verbs.")

    if punct > 0.06:
        flags.append("High punctuation density.")
        tips.append("Reduce excessive punctuation; prefer clear sentence structure.")

    if not tips:
        tips.append("Looks solid. For improvement, add one concrete example and a clearer transition sentence.")

    return {"flags": flags, "tips": tips}


# -----------------------------
# Routes
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
def analyze(payload: TextIn):
    x, feats_or_error = compute_features(payload.text)
    if x is None:
        return {"ok": False, **feats_or_error}

    # model style score (we don't call it "AI probability")
    x_scaled = scaler.transform(x)
    style_score = float(xgb_model.predict_proba(x_scaled)[0, 1])

    summary = make_summary(payload.text, n_sentences=3)
    scores = style_scores(feats_or_error)
    coach = coaching_tips(feats_or_error)

    return {
        "ok": True,
        "summary": summary,
        "scores": scores,
        "coach": coach,
        "style_score": style_score,
        "features": feats_or_error,
    }


@app.post("/compare")
def compare(payload: CompareIn):
    x1, f1 = compute_features(payload.original)
    if x1 is None:
        return {"ok": False, "which": "original", **f1}

    x2, f2 = compute_features(payload.revised)
    if x2 is None:
        return {"ok": False, "which": "revised", **f2}

    s1 = style_scores(f1)
    s2 = style_scores(f2)

    delta = {k: round(s2[k] - s1[k], 2) for k in s1.keys()}

    return {
        "ok": True,
        "before": {"scores": s1, "features": f1},
        "after": {"scores": s2, "features": f2},
        "delta": delta,
    }