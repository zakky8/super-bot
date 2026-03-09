"""
Run once after pip install:
  python setup.py
"""
import nltk

print("Downloading NLTK data...")
# B15 FIX: NLTK 3.9+ uses 'punkt_tab' not 'punkt'
nltk.download("punkt_tab", quiet=False)
nltk.download("stopwords", quiet=False)
print("Setup complete. Run: streamlit run dashboard.py")
