"""
🩺 Dr. Medibot - Complete Working Version
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
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    /* Reset */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    /* Background */
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 50%, #bcccdc 100%);
    }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #0a5c3f 0%, #1a7a5a 40%, #2d8f6f 80%, #3da87a 100%);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(10, 92, 63, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
    }
    .main-header p {
        opacity: 0.92;
        font-size: 1.1rem;
        margin: 0.3rem 0 0 0;
    }
    .header-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 0.3rem 1.2rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.5rem;
        border: 1px solid rgba(255,255,255,0.15);
    }
    
    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    }
    .sidebar-section {
        background: white;
        padding: 1.2rem;
        border-radius: 16px;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.04);
    }
    .sidebar-section h3 {
        color: #0a5c3f;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }
    
    /* Chat Messages */
    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #90caf9 100%);
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 5px 18px;
        margin: 0.5rem 0;
        margin-left: 20%;
        border: 1px solid rgba(144, 202, 249, 0.3);
        box-shadow: 0 2px 8px rgba(144, 202, 249, 0.15);
        animation: slideInRight 0.4s ease;
        color: #1a237e;
    }
    .assistant-message {
        background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%);
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 18px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border-left: 4px solid #0a5c3f;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        animation: slideInLeft 0.4s ease;
        color: #1a2a3a;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Emergency Warning */
    .emergency-warning {
        background: linear-gradient(135deg, #ff1744 0%, #d50000 100%);
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        animation: pulse 1.5s infinite;
        box-shadow: 0 8px 30px rgba(255,23,68,0.35);
        border: 1px solid rgba(255,255,255,0.15);
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.92; transform: scale(1.01); }
    }
    
    /* Welcome Card */
    .welcome-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.5);
        margin: 1rem 0;
    }
    .welcome-card h3 {
        color: #0a5c3f;
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    
    /* Icon Boxes */
    .icon-box {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.2rem 0.8rem;
        border-radius: 14px;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid rgba(10, 92, 63, 0.08);
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        height: 100%;
    }
    .icon-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(10, 92, 63, 0.12);
        border-color: rgba(10, 92, 63, 0.15);
    }
    .icon-box .icon {
        font-size: 2.5rem;
        line-height: 1.2;
        margin-bottom: 0.3rem;
    }
    .icon-box .label {
        font-weight: 600;
        font-size: 0.85rem;
        color: #1a2a3a;
    }
    
    /* Stat Cards */
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.04);
    }
    .stat-card .number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0a5c3f;
    }
    .stat-card .label {
        font-size: 0.8rem;
        color: #888;
    }
    
    /* Status Online */
    .status-online {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: #e8f5e9;
        color: #2e7d32;
        padding: 0.3rem 1rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-online .dot {
        width: 8px;
        height: 8px;
        background: #4caf50;
        border-radius: 50%;
        animation: pulse-dot 2s infinite;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    /* Admin Badge */
    .admin-badge {
        display: inline-block;
        background: linear-gradient(135deg, #ffd700 0%, #f9a825 100%);
        color: #333;
        padding: 0.2rem 0.8rem;
        border-radius: 50px;
        font-size: 0.7rem;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
    }
    
    /* Section Divider */
    .section-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(10, 92, 63, 0.15), transparent);
        margin: 1.5rem 0;
    }
    
    /* How It Works Box */
    .how-it-works-box {
        background: #f8fafc;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #0a5c3f;
        margin: 1rem 0;
    }
    .how-it-works-box ol {
        color: #333;
        line-height: 2.2;
        margin-left: 0;
        padding-left: 1.2rem;
    }
    .how-it-works-box ol li strong {
        color: #0a5c3f;
    }
    
    /* Disclaimer Box */
    .disclaimer-box {
        background: #fff3e0;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    .disclaimer-box strong {
        color: #e65100;
    }
    .disclaimer-box span {
        color: #555;
        font-size: 0.9rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0 0.5rem;
        border-top: 1px solid rgba(0,0,0,0.06);
        margin-top: 2rem;
    }
    .footer p {
        color: #888;
        font-size: 0.8rem;
        margin: 0.2rem 0;
    }
    .footer .disclaimer {
        color: #e57373;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    @media (max-width: 768px) {
        .main-header h1 { font-size: 2rem; }
        .main-header { padding: 1.5rem; }
        .user-message, .assistant-message {
            margin-left: 5% !important;
            margin-right: 5% !important;
        }
        .welcome-card { padding: 1.2rem; }
    }
    
    @media (max-width: 480px) {
        .main-header h1 { font-size: 1.5rem; }
        .icon-box .icon { font-size: 2rem; }
        .icon-box .label { font-size: 0.75rem; }
    }
</style>
""", unsafe_allow_html=True)

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

# ==================== GROQ SETUP ====================
@st.cache_resource
def get_groq_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        if api_key and GROQ_AVAILABLE:
            return Groq(api_key=api_key)
    except:
        pass
    return None

# ==================== PDF FUNCTIONS ====================
def extract_text_from_pdf(file):
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
    if not text:
        return []
    paragraphs = text.split("\n\n")
    query_words = set(query.lower().split())
    scored = []
    for para in paragraphs:
        if len(para.strip()) < 20:
            continue
        para_words = set(para.lower().split())
        score = len(query_words.intersection(para_words))
        if score > 0:
            scored.append((score, para))
    scored.sort(reverse=True)
    return [para for _, para in scored[:max_chunks]]

def get_response(query: str, context: str, history: str) -> str:
    client = get_groq_client()
    if not client:
        return "⚠️ Groq is not available. Please check your API key."
    
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
            st.markdown("""
            <div class="sidebar-section">
                <h3>📄 Admin - Upload Document</h3>
            """, unsafe_allow_html=True)
            
            st.info("👑 Upload medical documents. They will be stored permanently.")
            
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
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
    
    with st.container():
        st.markdown("""
        <div class="sidebar-section">
            <h3>📊 Status</h3>
        """, unsafe_allow_html=True)
        
        if st.session_state.docs_loaded:
            st.success(f"✅ Knowledge Base Ready")
            st.caption(f"📚 {st.session_state.doc_name}")
        else:
            if is_admin:
                st.warning("⚠️ No documents loaded")
            else:
                st.info("⏳ Knowledge base is being prepared")
        
        client = get_groq_client()
        if client:
            st.markdown("""
            <div class="status-online">
                <span class="dot"></span>
                Groq API Connected
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"Model: {st.secrets.get('GROQ_MODEL', 'llama-3.3-70b-versatile')}")
        else:
            st.error("❌ Groq API Not Connected")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="sidebar-section">
            <h3>📈 Statistics</h3>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="number">{len(st.session_state.messages)}</div>
                <div class="label">💬 Messages</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="number">0</div>
                <div class="label">🩺 Symptoms</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🔄 New Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==================== MAIN CONTENT ====================
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <h3>💙 Welcome to Dr. Medibot!</h3>
        <p style="color: #555; font-size: 1rem; margin-bottom: 1.5rem;">Your AI-powered medical assistant for evidence-based health information.</p>
    """, unsafe_allow_html=True)
    
    # ICON BOXES
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="icon-box">
            <div class="icon">📚</div>
            <div class="label">Medical Documents</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="icon-box">
            <div class="icon">💬</div>
            <div class="label">Ask Questions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="icon-box">
            <div class="icon">🤖</div>
            <div class="label">AI Answers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="icon-box">
            <div class="icon">⚠️</div>
            <div class="label">Emergency Alerts</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    
    # HOW IT WORKS
    st.markdown("#### ✨ How It Works")
    st.markdown("""
    <div class="how-it-works-box">
        <ol>
            <li><strong>Medical documents</strong> are uploaded by healthcare professionals</li>
            <li><strong>Ask</strong> questions about symptoms, treatments, or conditions</li>
            <li><strong>Get</strong> evidence-based answers from trusted medical sources</li>
            <li><strong>Receive</strong> emergency warnings for critical symptoms</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    
    # EXAMPLE QUESTIONS
    st.markdown("#### 💡 Example Questions")
    
    questions = [
        ("🩸 What are the symptoms of diabetes?", "What are the symptoms of diabetes?"),
        ("❤️ How is hypertension treated?", "How is hypertension treated?"),
        ("🫀 What causes chest pain?", "What causes chest pain?"),
        ("💊 What medications are used for heart disease?", "What medications are used for heart disease?")
    ]
    
    cols = st.columns(2)
    for i, (display_text, actual_question) in enumerate(questions):
        with cols[i % 2]:
            if st.button(display_text, use_container_width=True):
                st.session_state._example_question = actual_question
                st.rerun()
    
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    
    # DISCLAIMER
    st.markdown("""
    <div class="disclaimer-box">
        <strong>⚠️ Medical Disclaimer:</strong>
        <span>This is for educational purposes only. Always consult a healthcare professional for medical advice.</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
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
    
    if hasattr(st.session_state, '_example_question'):
        user_input = st.session_state._example_question
        del st.session_state._example_question
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("🩺 Dr. Medibot is thinking..."):
            try:
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
    <p style="font-size: 0.7rem; color: #ccc;">Made with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)