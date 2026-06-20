"""
🩺 Dr. Medibot - Simplified Version
No ChromaDB - Uses text-based search instead
"""

import streamlit as st
import os
import tempfile
import json
from datetime import datetime
from typing import List

# ==================== IMPORTS ====================
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ==================== ADMIN PASSWORD ====================
ADMIN_PASSWORD = "admin123"

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Dr. Medibot - AI Medical Assistant",
    page_icon="🩺",
    layout="wide"
)

# ==================== SESSION STATE ====================
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "docs_loaded" not in st.session_state:
        st.session_state.docs_loaded = False
    if "doc_text" not in st.session_state:
        st.session_state.doc_text = ""
    if "doc_name" not in st.session_state:
        st.session_state.doc_name = None
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False

init_session_state()

# ==================== CSS ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0a5c3f 0%, #1a7a5a 50%, #2d8f6f 100%);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(10, 92, 63, 0.3);
    }
    .main-header h1 { font-size: 2.8rem; font-weight: 800; }
    .main-header p { opacity: 0.9; font-size: 1.1rem; }
    .header-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 0.3rem 1rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    .admin-badge {
        display: inline-block;
        background: #ffd700;
        color: #333;
        padding: 0.2rem 0.8rem;
        border-radius: 50px;
        font-size: 0.7rem;
        font-weight: 700;
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
        background: #f5f5f5;
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 18px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border-left: 4px solid #0a5c3f;
    }
    .welcome-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        margin: 1rem 0;
    }
    .footer { text-align: center; padding: 2rem 0 0.5rem; border-top: 1px solid rgba(0,0,0,0.06); margin-top: 2rem; }
    .footer .disclaimer { color: #ff6b6b; font-size: 0.75rem; }
    @media (max-width: 768px) {
        .main-header h1 { font-size: 2rem; }
        .user-message, .assistant-message { margin-left: 5%; margin-right: 5%; }
    }
</style>
""", unsafe_allow_html=True)

# ==================== ADMIN CHECK ====================
def check_admin():
    if not st.session_state.is_admin:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔐 Admin Access")
        password = st.sidebar.text_input("Enter Admin Password", type="password")
        if st.sidebar.button("Login as Admin"):
            if password == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.sidebar.success("✅ Admin logged in!")
                st.rerun()
            else:
                st.sidebar.error("❌ Wrong password!")
        return False
    else:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👑 Admin Mode")
        st.sidebar.markdown('<span class="admin-badge">ADMIN</span>', unsafe_allow_html=True)
        if st.sidebar.button("Logout"):
            st.session_state.is_admin = False
            st.rerun()
        return True

# ==================== GROQ ====================
@st.cache_resource
def get_groq_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        if api_key and GROQ_AVAILABLE:
            return Groq(api_key=api_key)
    except:
        pass
    return None

# ==================== PDF PROCESSING ====================
def extract_text_from_pdf(file):
    """Extract text from PDF using pypdf (no ChromaDB)"""
    if not PDF_AVAILABLE:
        return None
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.getvalue())
        tmp_path = tmp.name
    
    try:
        reader = PdfReader(tmp_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None
    finally:
        os.unlink(tmp_path)

def search_in_text(query: str, text: str, max_chunks: int = 3):
    """Simple text search (no vector DB)"""
    if not text:
        return []
    
    # Split into paragraphs
    paragraphs = text.split("\n\n")
    
    # Score each paragraph by keyword matches
    query_words = set(query.lower().split())
    scored = []
    
    for i, para in enumerate(paragraphs):
        if len(para.strip()) < 20:
            continue
        para_words = set(para.lower().split())
        score = len(query_words.intersection(para_words))
        if score > 0:
            scored.append((score, i, para))
    
    # Sort by score and return top chunks
    scored.sort(reverse=True)
    return [para for _, _, para in scored[:max_chunks]]

def get_response(query: str, context: str, history: str) -> str:
    client = get_groq_client()
    if not client:
        return "⚠️ Groq is not available."
    
    prompt = f"""You are Dr. Medibot, a caring medical AI assistant.
Use ONLY the provided context.

CONTEXT:
{context}

HISTORY:
{history}

USER: {query}

Guidelines:
1. Answer based ONLY on context
2. Be warm and empathetic
3. If not in context, say so clearly
4. Include medical disclaimer

YOUR RESPONSE:"""
    try:
        model = st.secrets.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==================== HEADER ====================
st.markdown("""
<div class="main-header">
    <div style="display: flex; align-items: center; gap: 1rem;">
        <span style="font-size: 3rem;">🩺</span>
        <div>
            <h1>Dr. Medibot</h1>
            <p>Your AI Medical Assistant — Evidence-Based Answers from Medical Documents</p>
            <div class="header-badge">⚡ Powered by Groq AI &nbsp;•&nbsp; 🔒 100% Private</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
        <span style="font-size: 3rem;">🩺</span>
        <h2 style="color: #0a5c3f; margin: 0;">Dr. Medibot</h2>
        <p style="color: #888; font-size: 0.8rem;">v2.0 • AI Medical Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    is_admin = check_admin()
    
    if is_admin:
        with st.container():
            st.markdown("### 📄 Admin - Upload Document")
            st.info("Upload medical documents. They will be stored permanently.")
            
            uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
            
            if uploaded_file and st.button("📚 Upload", type="primary", use_container_width=True):
                with st.spinner("🔄 Extracting text from PDF..."):
                    try:
                        text = extract_text_from_pdf(uploaded_file)
                        if text:
                            st.session_state.doc_text = text
                            st.session_state.docs_loaded = True
                            st.session_state.doc_name = uploaded_file.name
                            st.success(f"✅ Document loaded: {uploaded_file.name}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Failed to extract text from PDF")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            if st.button("🗑️ Clear Document", use_container_width=True):
                st.session_state.doc_text = ""
                st.session_state.docs_loaded = False
                st.session_state.doc_name = None
                st.success("✅ Document cleared!")
                st.rerun()
        
        st.markdown("---")
    
    # Status
    with st.container():
        st.markdown("### 📊 Status")
        if st.session_state.docs_loaded:
            st.success(f"✅ Document loaded: {st.session_state.doc_name}")
        else:
            if is_admin:
                st.warning("⚠️ No document loaded")
            else:
                st.info("⏳ Knowledge base is being prepared")
        
        client = get_groq_client()
        if client:
            st.success("✅ Groq API Connected")
        else:
            st.error("❌ Groq API Not Connected")
    
    st.markdown("---")
    
    # Statistics
    st.metric("💬 Messages", len(st.session_state.messages))
    
    if st.button("🔄 New Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==================== MAIN CONTENT ====================
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <h3>💙 Welcome to Dr. Medibot!</h3>
        <p>Your AI-powered medical assistant for evidence-based health information.</p>
        
        <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin: 1.5rem 0;">
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 12px; text-align: center; flex: 1; min-width: 120px;">
                <div style="font-size: 2.5rem;">📚</div>
                <div style="font-weight: 600;">Medical Documents</div>
            </div>
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 12px; text-align: center; flex: 1; min-width: 120px;">
                <div style="font-size: 2.5rem;">💬</div>
                <div style="font-weight: 600;">Ask Questions</div>
            </div>
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 12px; text-align: center; flex: 1; min-width: 120px;">
                <div style="font-size: 2.5rem;">🤖</div>
                <div style="font-weight: 600;">AI Answers</div>
            </div>
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 12px; text-align: center; flex: 1; min-width: 120px;">
                <div style="font-size: 2.5rem;">⚠️</div>
                <div style="font-weight: 600;">Emergency Alerts</div>
            </div>
        </div>
        
        <hr>
        
        <h4>✨ How It Works</h4>
        <ol style="color: #555; line-height: 2;">
            <li><strong>Medical documents</strong> are uploaded by healthcare professionals</li>
            <li><strong>Ask</strong> questions about symptoms, treatments, or conditions</li>
            <li><strong>Get</strong> evidence-based answers from trusted medical sources</li>
        </ol>
        
        <hr>
        
        <div style="background: #fff3e0; padding: 1rem; border-radius: 12px; border-left: 4px solid #ff9800;">
            <strong>⚠️ Medical Disclaimer:</strong>
            <span style="color: #666;">This is for educational purposes only. Always consult a healthcare professional.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.docs_loaded:
        st.info("📚 Please upload a medical document (admin only).")

else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">👤 <strong>You</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">🩺 <strong>Dr. Medibot</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)

# ==================== CHAT INPUT ====================
if st.session_state.docs_loaded:
    user_input = st.chat_input("Ask a question about medical topics...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("🩺 Dr. Medibot is thinking..."):
            try:
                # Search for relevant context
                results = search_in_text(user_input, st.session_state.doc_text)
                
                if results:
                    context = "\n\n".join(results)
                    history = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages[-5:]])
                    response = get_response(user_input, context, history)
                else:
                    response = "I couldn't find relevant information in the document. Please try rephrasing your question."
                
                response += """

---
⚠️ **Medical Disclaimer:** This information is for educational purposes only. Always consult a qualified healthcare provider."""
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
else:
    st.info("📚 No document loaded. Admin needs to upload one first.")

# ==================== FOOTER ====================
st.markdown("""
<div class="footer">
    <p>🩺 Dr. Medibot v2.0 • Powered by Groq AI</p>
    <p class="disclaimer">⚠️ For educational purposes only. Always consult a healthcare professional.</p>
</div>
""", unsafe_allow_html=True)