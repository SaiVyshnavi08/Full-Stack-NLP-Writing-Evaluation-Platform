# 🧠 Full-Stack-NLP-Writing-Evaluation-Platform

> A full-stack NLP-powered application that evaluates academic writing style in real time using lexical diversity metrics and machine learning.

---

## 🚀 Overview

This project analyzes writing structure and vocabulary richness using engineered linguistic features and a trained machine learning model.

It provides:

- 📊 Writing Style Scoring  
- 📝 Academic Clarity Evaluation  
- 🔄 Rewrite Comparison Analysis  
- 📈 Feature-Level Technical Breakdown  
- ⚡ Real-Time Inference  

---

## 🏗 System Architecture

### 🔹 Backend

- **FastAPI** – REST API framework  
- **spaCy** – NLP preprocessing  
- **lexical-diversity** – MTLD & MATTR computation  
- **XGBoost** – Style classification model  
- **scikit-learn** – Feature scaling & evaluation  

### 🔹 Frontend

- HTML, CSS, JavaScript  
- Dynamic tab-based interface  
- Real-time analysis dashboard  
- Modern gradient UI design  

---

## 📊 Dataset

- ~70,000+ New York Times comments  
  - Years: 2017, 2018, 2024  
- Balanced human vs AI-era samples  
- Feature-engineered structured dataset  
- Cleaned, tokenized, and standardized text  

---

## 🧮 Engineered Features

The model uses 15+ handcrafted linguistic features, including:

- Type-Token Ratio (TTR)  
- MTLD (Measure of Textual Lexical Diversity)  
- MATTR  
- Stopword Ratio  
- Punctuation Ratio  
- Repetition Ratio  
- Sentence Length Variance  
- Token/Character Ratios  
- Interaction Features (e.g., TTR × MTLD)  

---

## 🤖 Model Performance

Models trained and evaluated:

- Logistic Regression  
- Random Forest  
- XGBoost ✅ (Best Performer)  

**Final Model Performance**


ROC-AUC: ~0.73
Balanced dataset
Cross-validation applied
---

## 🌐 Application Modes

### 📝 Analyzer Mode

- Real-time writing evaluation  
- Style probability score  
- Academic scoring dashboard  
- Feature-level transparency  

### 🔄 Rewrite Coach Mode

- Compare original vs revised text  
- Detect clarity & richness improvements  
- Display score deltas  
- Side-by-side analysis  

---
![Dashboard Preview](https://github.com/user-attachments/assets/837e3d2b-48ba-4152-95c0-0632333ea655)

<img width="1882" height="1418" alt="image" src="https://github.com/user-attachments/assets/d7e80f9c-f22d-4d95-8e71-7bde6225b0f4" />
<img width="2086" height="1506" alt="image" src="https://github.com/user-attachments/assets/aa17ccc8-a921-4f41-a0b4-32f080e716c4" />
<img width="1984" height="1360" alt="image" src="https://github.com/user-attachments/assets/6771d8fa-1987-4b3a-a701-590418f463b5" />




## 🛠 Installation & Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn main:app --reload

Visit: http://127.0.0.1:8000

🎯 What This Project Demonstrates

End-to-end ML pipeline design

Advanced NLP feature engineering

Model training & evaluation

Production-ready inference API

Full-stack integration

Real-time interactive UI



