"""
Train and save the classifier. Run once before starting the app.
  python train_model.py
Requires Python 3.10+ (scikit-learn 1.7+ requirement).
"""
import os
import pandas as pd
import numpy as np
import joblib
from loguru import logger
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Load and validate data
df = pd.read_csv("data/sample_tickets.csv")
df.dropna(subset=["description", "category"], inplace=True)
df["description"] = df["description"].astype(str).str.strip()
df = df[df["description"].str.len() > 5]

logger.info(f"Loaded {len(df)} valid tickets")
logger.info(f"Category counts:\n{df['category'].value_counts().to_string()}")

os.makedirs("models/encoder_cache", exist_ok=True)

logger.info("Loading encoder model (cached after first download)...")
# L2 upgrade: multi-qa model is more accurate for Q&A support tickets
encoder = SentenceTransformer(
    "multi-qa-MiniLM-L6-cos-v1",
    cache_folder="models/encoder_cache",  # L4 FIX: prevents re-download on every run
)

logger.info("Encoding tickets...")
# B12 FIX: explicit convert_to_numpy for sentence-transformers 5.x
embeddings = encoder.encode(
    df["description"].tolist(),
    show_progress_bar=True,
    batch_size=32,
    convert_to_numpy=True,
)

# Stratified split so all categories appear in train and test
X_train, X_test, y_train, y_test = train_test_split(
    embeddings,
    df["category"],
    test_size=0.2,
    random_state=42,
    stratify=df["category"] if df["category"].nunique() > 1 else None,
)

# L3 FIX: class_weight='balanced' prevents bias toward majority categories
clf = RandomForestClassifier(
    n_estimators=200,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,  # Use all CPU cores
)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
logger.info("Model evaluation:\n" + classification_report(y_test, y_pred, zero_division=0))

joblib.dump(clf, "models/ticket_classifier.pkl")
joblib.dump(encoder, "models/sentence_encoder.pkl")
logger.success("Models saved. Run: streamlit run app.py")
