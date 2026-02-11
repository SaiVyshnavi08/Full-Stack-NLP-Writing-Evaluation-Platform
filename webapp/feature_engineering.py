import re
import string
import numpy as np
import spacy
from lexical_diversity import lex_div as ld
from spacy.lang.en.stop_words import STOP_WORDS

# Load spaCy once (fast)
nlp = spacy.load("en_core_web_sm", exclude=["parser"])
if "sentencizer" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer")

def clean_text(t: str) -> str:
    if not isinstance(t, str):
        return ""
    t = re.sub(r"<br\s*/?>", " ", t)
    t = re.sub(r"http\S+", "", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def tokenize_words(text: str):
    return re.findall(r"[A-Za-z][A-Za-z'-]*", text.lower())

def ttr_score(text: str) -> float:
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

def stopword_ratio(text: str) -> float:
    words = str(text).split()
    stopwords = [w for w in words if w.lower() in STOP_WORDS]
    return len(stopwords) / len(words) if words else 0.0

def punctuation_ratio(text: str) -> float:
    text = str(text)
    punct = sum(1 for c in text if c in string.punctuation)
    return punct / len(text) if text else 0.0

def repetition_ratio(text: str) -> float:
    words = str(text).split()
    unique = set(words)
    return 1 - (len(unique) / len(words)) if words else 0.0

def sentence_length_variance(text: str) -> float:
    text = str(text)
    sentences = text.split(".")
    lengths = [len(s.split()) for s in sentences if len(s.split()) > 0]
    return float(np.var(lengths)) if len(lengths) > 1 else 0.0


FEATURES = [
    "chars",
    "tokens",
    "ttr",
    "mtld",
    "mattr",
    "avg_word_length",
    "lexical_ratio",
    "ttr_mtld_interaction",
    "stopword_ratio",
    "punct_ratio",
    "repetition_ratio",
    "sentence_var",
    "token_char_ratio",
    "char_token_ratio",
    "sentence_token_ratio"
]

def compute_features(raw_text: str):
    text = raw_text if isinstance(raw_text, str) else ""
    clean = clean_text(text)

    chars, tokens, sentences = spacy_counts(text)

    ttr = ttr_score(clean)
    mtld = mtld_score(clean)
    mattr = mattr_score(clean)

    # Enforce stable inference same as training
    if mtld is None or mattr is None or tokens < 50:
        return None, {
            "error": "Text is too short. Please paste at least ~50 tokens (a longer paragraph).",
            "tokens": tokens
        }

    avg_word_length = chars / max(tokens, 1)
    lexical_ratio = mtld / max(tokens, 1)
    ttr_mtld_interaction = ttr * mtld

    sw_ratio = stopword_ratio(clean)
    p_ratio = punctuation_ratio(text)
    rep_ratio = repetition_ratio(clean)
    sent_var = sentence_length_variance(text)

    token_char_ratio = tokens / max(chars, 1)
    char_token_ratio = chars / max(tokens, 1)
    sentence_token_ratio = sentences / max(tokens, 1)

    feat_dict = {
    "chars": chars,
    "tokens": tokens,
    "sentences": sentences,
    "ttr": ttr,
    "mtld": mtld,
    "mattr": mattr,
    "avg_word_length": avg_word_length,
    "lexical_ratio": lexical_ratio,
    "ttr_mtld_interaction": ttr_mtld_interaction,
    "stopword_ratio": sw_ratio,
    "punct_ratio": p_ratio,
    "repetition_ratio": rep_ratio,
    "sentence_var": sent_var,
    "token_char_ratio": token_char_ratio,
    "char_token_ratio": char_token_ratio,
    "sentence_token_ratio": sentence_token_ratio,
}

    # return in correct order
    x = np.array([feat_dict[f] for f in FEATURES], dtype=float).reshape(1, -1)
    return x, feat_dict