# Project 4 — AI Support Ticket Classifier

> Classifies support tickets by category and priority using sentence-transformers + scikit-learn. Interactive Streamlit dashboard.

## What It Does
- Classifies tickets into 8 categories: account_access, withdrawal_issue, deposit_issue, kyc_verification, trading_problem, wallet_connection, scam_report, general_inquiry
- Assigns priority: urgent, high, medium, low
- Provides suggested responses for each category
- Flags low-confidence results for human review
- Interactive Streamlit UI with example tickets

## Tech Stack
- Python 3.12 (minimum 3.10 — scikit-learn 1.7+ requirement)
- sentence-transformers 5.2.3 (multi-qa-MiniLM-L6-cos-v1 model)
- scikit-learn 1.8.0 (RandomForestClassifier)
- streamlit 1.55.0
- Deployed on: Streamlit Cloud (free)

## Setup

1. Install: `cd project4-ticket-classifier && pip install -r requirements.txt`
2. Setup NLTK: `python setup.py`
3. Train model: `python train_model.py`
4. Start app: `streamlit run app.py`

## Architecture
Two-stage pipeline: SentenceTransformer encodes tickets into 384-dim vectors, RandomForest classifies. Model is cached to disk — only downloaded once. `convert_to_numpy=True` explicitly set for sentence-transformers 5.x compatibility.
