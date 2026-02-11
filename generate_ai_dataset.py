import pandas as pd
from openai import OpenAI
import time
import uuid

# 1) Set how many AI samples you want
N = 1000   # start with 1000 to test, then 5000–10000

# 2) Choose prompts that look like NYT/reddit comments (short + medium + long)
PROMPTS = [
    "Write a short, opinionated comment (40–80 words) reacting to a news article.",
    "Write a medium-length comment (120–200 words) with a clear argument and a counterpoint.",
    "Write a comment (80–150 words) that uses a casual, human tone and one personal example.",
    "Write a skeptical comment (60–120 words) that challenges the article's framing.",
]

client = OpenAI()

rows = []
for i in range(N):
    prompt = PROMPTS[i % len(PROMPTS)]

    # Responses API (recommended)
    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0.9
    )

    text = resp.output_text.strip()
    rows.append({
        "id": str(uuid.uuid4()),
        "text": text,
        "label": 1
    })

    # be polite to rate limits
    if i % 50 == 0:
        print("Generated:", i)
        time.sleep(0.5)

df = pd.DataFrame(rows)
df.to_csv("ai_generated_texts.csv", index=False)
print("Saved ai_generated_texts.csv with", len(df), "rows")
