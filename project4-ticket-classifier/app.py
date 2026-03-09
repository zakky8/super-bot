import streamlit as st
from classifier import classify_ticket

st.set_page_config(page_title="Ticket Classifier", page_icon="🎫", layout="wide")
st.title("🎫 AI Support Ticket Classifier")
st.caption("sentence-transformers 5.2.3 + scikit-learn 1.8.0 + multi-qa-MiniLM-L6-cos-v1")

PRIORITY_ICONS = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}

EXAMPLES = [
    "I cannot withdraw my funds — shows insufficient balance",
    "Someone claiming to be from support DMed me and stole my ETH",
    "My KYC was rejected but my documents are valid",
    "How do I change the email address on my account?",
    "MetaMask keeps timing out when I try to connect",
]

col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Ticket Input")
    with st.expander("Load an example"):
        sel = st.selectbox("Examples:", EXAMPLES, label_visibility="collapsed")
        if st.button("Use this example"):
            st.session_state["ticket"] = sel

    text = st.text_area(
        "Paste ticket here:",
        value=st.session_state.get("ticket", ""),
        height=200,
        label_visibility="collapsed",
        placeholder="Enter support ticket text...",
    )
    run = st.button("🔍 Classify", type="primary", use_container_width=True)

with col2:
    st.subheader("📊 Result")
    if run and text.strip():
        with st.spinner("Classifying..."):
            result = classify_ticket(text)

        icon = PRIORITY_ICONS.get(result.priority, "⚪")
        m1, m2, m3 = st.columns(3)
        m1.metric("Category", result.category.replace("_", " ").title())
        m2.metric("Confidence", f"{result.confidence:.0%}")
        m3.metric("Priority", f"{icon} {result.priority.upper()}")

        if result.confidence < 0.55:
            st.warning("⚠️ Low confidence — recommend human review before responding")
        if result.priority in ("urgent", "high"):
            st.error(f"{icon} {result.priority.upper()} — respond immediately")

        st.subheader("💬 Suggested Response")
        st.info(result.suggested_response)

    elif run:
        st.warning("Please enter a ticket before classifying.")
    else:
        st.caption("Result will appear here after classification.")
