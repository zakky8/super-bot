import joblib
import numpy as np
from dataclasses import dataclass
from loguru import logger

URGENT_KW = ["stolen", "hacked", "fraud", "lost funds", "unauthorized", "scam"]
HIGH_KW = ["cannot withdraw", "account locked", "cannot login", "funds missing"]

RESPONSES = {
    "account_access": (
        "For account access issues, try resetting your password via the login page. "
        "If locked, our team will verify your identity within 24 hours."
    ),
    "withdrawal_issue": (
        "Withdrawals are handled urgently. Ensure KYC is verified and banking details "
        "are correct. Our team will review within 4 hours."
    ),
    "deposit_issue": (
        "Deposits typically arrive within 1-3 hours. Check your transaction on the "
        "blockchain explorer. Contact support with the transaction ID if not arrived after 3 hours."
    ),
    "kyc_verification": (
        "KYC rejections are reviewed manually. Re-upload clear, valid documents. "
        "Allow 2-3 business days for review."
    ),
    "trading_problem": (
        "For trading errors, clear your browser cache and retry. "
        "If the issue persists, provide a screenshot for our team."
    ),
    "wallet_connection": (
        "Wallet connection issues are often resolved by refreshing your wallet "
        "extension and reconnecting. Ensure you are on the correct network."
    ),
    "scam_report": (
        "Thank you for reporting this. Our security team has been immediately notified. "
        "Do not send any further funds. We will investigate and respond within 1 hour."
    ),
    "general_inquiry": (
        "Thank you for your message. A support agent will respond within 24 hours."
    ),
}


@dataclass
class ClassificationResult:
    category: str
    confidence: float
    priority: str
    suggested_response: str


try:
    clf = joblib.load("models/ticket_classifier.pkl")
    encoder = joblib.load("models/sentence_encoder.pkl")
    logger.info("Classifier models loaded")
except FileNotFoundError:
    raise RuntimeError(
        "Models not found. Run 'python train_model.py' first."
    )


def classify_ticket(ticket_text: str) -> ClassificationResult:
    if not ticket_text or not ticket_text.strip():
        return ClassificationResult(
            "general_inquiry", 0.0, "low", RESPONSES["general_inquiry"]
        )

    # B12 FIX: explicit convert_to_numpy for sentence-transformers 5.x
    embedding = encoder.encode([ticket_text], convert_to_numpy=True)
    predicted = clf.predict(embedding)[0]
    confidence = float(np.max(clf.predict_proba(embedding)[0]))

    lower = ticket_text.lower()
    if any(kw in lower for kw in URGENT_KW):
        priority = "urgent"
    elif any(kw in lower for kw in HIGH_KW):
        priority = "high"
    elif confidence < 0.55:
        priority = "medium"
    else:
        priority = "low"

    return ClassificationResult(
        category=predicted,
        confidence=confidence,
        priority=priority,
        suggested_response=RESPONSES.get(predicted, RESPONSES["general_inquiry"]),
    )
