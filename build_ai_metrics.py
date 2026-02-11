import re
import pandas as pd
import spacy
from lexical_diversity import lex_div as ld

INPUT_CSV = "comments_5000_combined.csv"
OUTPUT_CSV = "comment_level_metrics_ai_manual.csv"

nlp = spacy.load("en_core_web_sm", exclude=["parser"])
if "sentencizer" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer")

def clean_text(t):
    if not isinstance(t, str):
        return ""
    t = re.sub(r"<br\s*/?>", " ", t)
    t = re.sub(r"http\S+", "", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def tokenize_words(text: str):
    return re.findall(r"[A-Za-z][A-Za-z'-]*", text.lower())

def ttr(text: str) -> float:
    toks = tokenize_words(text)
    return (len(set(toks)) / len(toks)) if toks else 0.0

def mtld_score(text: str):
    toks = tokenize_words(text)
    if len(toks) < 50:
        return None
    return float(ld.mtld(toks))

def mattr_score(text: str, window_size: int = 50):
    toks = tokenize_words(text)
    if len(toks) < window_size:
        return None
    return float(ld.mattr(toks, window_size))

def spacy_counts(text: str):
    doc = nlp(text)
    chars = len(text)
    tokens = sum(1 for t in doc if not t.is_punct and not t.is_space)
    sents = sum(1 for _ in doc.sents)
    return chars, tokens, sents

def metrics(text: str):
    chars, tokens, sents = spacy_counts(text)
    return pd.Series({
        "chars": chars,
        "tokens": tokens,
        "sentences": sents,
        "ttr": ttr(text),
        "mtld": mtld_score(text),
        "mattr": mattr_score(text),
    })

df = pd.read_csv(INPUT_CSV)
print("Loaded:", df.shape)
print("Columns:", df.columns.tolist())

if "text" not in df.columns:
    raise ValueError("CSV must contain a 'text' column.")

df["clean_text"] = df["text"].apply(clean_text)

m = df["clean_text"].apply(metrics)
df = pd.concat([df, m], axis=1)

df = df[df["tokens"] >= 50].copy()
df = df.dropna(subset=["mtld", "mattr"]).copy()

df["label"] = 1

df_out = df[[
    "text", "clean_text",
    "chars", "tokens", "sentences",
    "ttr", "mtld", "mattr",
    "label"
]].copy()

df_out.to_csv(OUTPUT_CSV, index=False)

print("Saved:", OUTPUT_CSV)
print("Rows:", len(df_out))
print("Min tokens:", df_out["tokens"].min())