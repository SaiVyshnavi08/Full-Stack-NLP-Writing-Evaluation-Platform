import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load datasets
df_2017 = pd.read_csv("comment_level_metrics_2017.csv")
df_2018 = pd.read_csv("comment_level_metrics_2018.csv")
df_2024 = pd.read_csv("comment_level_metrics_2024.csv")

# Combine human baseline
df_human = pd.concat([df_2017, df_2018], ignore_index=True)
df_human["era"] = "Human (2017+2018)"
df_2024["era"] = "AI-era (2024)"

df_all = pd.concat([df_human, df_2024], ignore_index=True)

FEATURES = ["chars", "tokens", "ttr", "mtld", "mattr"]

for feature in FEATURES:
    plt.figure(figsize=(8,5))
    sns.kdeplot(data=df_all, x=feature, hue="era", common_norm=False)
    plt.title(f"{feature} Distribution — Human vs AI-era")
    plt.tight_layout()
    plt.show()
