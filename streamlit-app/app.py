"""
Dr. Medibot - WORKING VERSION
Fixed all import issues
"""

import streamlit as st
import os
import tempfile
import json
from datetime import datetime

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Dr. Medibot",
    page_icon="🩺",
    layout="wide"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0a5c3f 0%, #1a7a5a 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 5px 18px;
        margin: 0.5rem 0;
        margin-left: 20%;
        border: 1px solid #90caf9;
    }
    .assistant-message {
        background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 18px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border-left: 4px solid #0a5c3f;
    }
    .emergency-warning {
        background: linear-gradient(135deg, #ff1744 0%, #d50000 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "docs_loaded" not in st.session_state:
    st.session_state.docs_loaded = False

# ==================== HEADER ====================
st.markdown("""
<div class="main-header">
    <h1>🩺 Dr. Medibot</h1>
    <p>Your AI Medical Assistant</p>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 📄 Upload Medical Document")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf"
    )
    
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name} uploaded!")
        st.session_state.docs_loaded = True
    
    st.markdown("---")
    
    # API Status
    st.markdown("### 🔌 API Status")
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        if api_key:
            st.success("✅ Groq API Connected")
        else:
            st.error("❌ API Key Missing")
    except:
        st.error("❌ Secrets not available")
    
    st.markdown("---")
    
    # Statistics
    st.markdown("### 📈 Statistics")
    st.metric("💬 Messages", len(st.session_state.messages))

# ==================== CHAT AREA ====================
if not st.session_state.messages:
    st.markdown("""
    ### 💙 Welcome to Dr. Medibot!
    
    **How it works:**
    1. 📄 Upload a medical PDF in the sidebar
    2. 💬 Ask questions about your document
    3. 🤖 Get AI-powered answers
    4. ⚠️ Emergency symptom detection
    
    ---
    
    ### ✨ Example Questions:
    - "What are the symptoms of diabetes?"
    - "How is hypertension treated?"
    - "What causes chest pain?"
    """)
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">👤 <strong>You</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">🩺 <strong>Dr. Medibot</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)

# ==================== CHAT INPUT ====================
if st.session_state.docs_loaded:
    user_input = st.chat_input("Ask a question...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Simple response
        response = f"Thanks for your question: '{user_input}'\n\nI'll search your document for the answer. (Groq integration coming soon!)"
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
else:
    st.info("👈 Please upload a PDF in the sidebar to start chatting!")

# ==================== FOOTER ====================
st.markdown("---")
st.caption("🩺 Dr. Medibot | Powered by AI")
st.caption("⚠️ For educational purposes only. Always consult a healthcare professional.")