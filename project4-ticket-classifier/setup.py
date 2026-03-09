"""
Run once after pip install:
  python setup.py
"""
import os
import nltk

print("Downloading required NLTK data...")
# B15 FIX: 'punkt' renamed to 'punkt_tab' in NLTK 3.9+
nltk.download("punkt_tab", quiet=False)
nltk.download("stopwords", quiet=False)

os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("models/encoder_cache", exist_ok=True)

print("Setup complete. Run: python train_model.py")
