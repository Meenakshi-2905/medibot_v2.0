"""
🩺 Dr. Medibot - Medical AI Assistant
Admin-only document upload | Persistent storage | Auto-load on startup
"""

import streamlit as st
import os
import tempfile
import json
import hashlib
import shutil
from datetime import datetime
from typing import List, Dict, Any
import pickle

# ==================== IMPORTS ====================
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_community.vectorstores import FAISS
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

# ==================== ADMIN PASSWORD ====================
ADMIN_PASSWORD = "admin123"  # ← CHANGE THIS!

# ==================== PERSISTENT STORAGE ====================
PERSIST_DIR = "./medibot_db"
METADATA_FILE = os.path.join(PERSIST_DIR, "metadata.json")
VECTORSTORE_PATH = os.path.join(PERSIST_DIR, "vectorstore")

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
    * { margin: 0; padding: 0; box-sizing: border-box; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e8edf5 100%); }
    
    .main-header {
        background: linear-gradient(135deg, #0a5c3f 0%, #1a7a5a 50%, #2d8f6f 100%);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(10, 92, 63, 0.3);
        position: relative;
        overflow: hidden;
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
    
    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 5px 18px;
        margin: 0.5rem 0;
        margin-left: 20%;
        border: 1px solid #90caf9;
        animation: slideInRight 0.4s ease;
    }
    .assistant-message {
        background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 18px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border-left: 4px solid #0a5c3f;
        animation: slideInLeft 0.4s ease;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .emergency-warning {
        background: linear-gradient(135deg, #ff1744 0%, #d50000 100%);
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        animation: pulse 1.5s infinite;
        box-shadow: 0 8px 30px rgba(255,23,68,0.3);
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.9; transform: scale(1.01); }
    }
    
    .welcome-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.04);
        margin: 1rem 0;
    }
    .welcome-card h3 { color: #0a5c3f; font-size: 1.5rem; }
    
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.04);
    }
    .stat-card .number { font-size: 1.8rem; font-weight: 700; color: #0a5c3f; }
    .stat-card .label { font-size: 0.8rem; color: #888; }
    
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
    
    .admin-badge {
        display: inline-block;
        background: #ffd700;
        color: #333;
        padding: 0.2rem 0.8rem;
        border-radius: 50px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    
    .footer { text-align: center; padding: 2rem 0 0.5rem; border-top: 1px solid rgba(0,0,0,0.06); margin-top: 2rem; }
    .footer p { color: #999; font-size: 0.8rem; margin: 0.2rem 0; }
    .footer .disclaimer { color: #ff6b6b; font-size: 0.75rem; }
    
    @media (max-width: 768px) {
        .main-header h1 { font-size: 2rem; }
        .user-message, .assistant-message { margin-left: 5%; margin-right: 5%; }
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "docs_loaded" not in st.session_state:
        st.session_state.docs_loaded = False
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    if "symptoms" not in st.session_state:
        st.session_state.symptoms = []
    if "emergency" not in st.session_state:
        st.session_state.emergency = False
    if "doc_name" not in st.session_state:
        st.session_state.doc_name = None
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
    if "initialized" not in st.session_state:
        st.session_state.initialized = False

init_session_state()

# ==================== PERSISTENT STORAGE FUNCTIONS ====================
def ensure_storage_dir():
    """Create storage directory if it doesn't exist"""
    os.makedirs(PERSIST_DIR, exist_ok=True)

def save_metadata(doc_name: str, chunk_count: int):
    """Save document metadata"""
    ensure_storage_dir()
    metadata = {
        "doc_name": doc_name,
        "chunk_count": chunk_count,
        "uploaded_at": datetime.now().isoformat(),
        "version": "1.0"
    }
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)

def load_metadata():
    """Load document metadata"""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return None

def is_vectorstore_persistent():
    """Check if vectorstore exists in persistent storage"""
    return os.path.exists(VECTORSTORE_PATH) and os.path.exists(os.path.join(VECTORSTORE_PATH, "index.pkl"))

def load_persistent_vectorstore():
    """Load vectorstore from persistent storage"""
    if not RAG_AVAILABLE:
        return None, None
    
    try:
        if is_vectorstore_persistent():
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vectorstore = Chroma(persist_directory=VECTORSTORE_PATH, embedding_function=embeddings)
            metadata = load_metadata()
            return vectorstore, metadata
    except Exception as e:
        print(f"Error loading vectorstore: {e}")
    
    return None, None

def save_vectorstore(vectorstore):
    """Save vectorstore to persistent storage"""
    try:
        ensure_storage_dir()
        vectorstore.persist()
        return True
    except Exception as e:
        print(f"Error saving vectorstore: {e}")
        return False

def clear_persistent_storage():
    """Clear all persistent storage"""
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)
    ensure_storage_dir()

# ==================== INITIALIZATION ====================
def initialize_app():
    """Load persistent data on app startup"""
    if st.session_state.initialized:
        return
    
    try:
        vectorstore, metadata = load_persistent_vectorstore()
        
        if vectorstore and metadata:
            st.session_state.vectorstore = vectorstore
            st.session_state.docs_loaded = True
            st.session_state.doc_name = metadata.get("doc_name", "Unknown")
            st.session_state.initialized = True
            
            if not st.session_state.messages:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"📚 Knowledge base loaded: {metadata.get('doc_name', 'Medical Documents')}\n\nI'm ready to answer your medical questions based on the uploaded documents."
                })
    except Exception as e:
        print(f"Error initializing app: {e}")
    
    st.session_state.initialized = True

initialize_app()

# ==================== ADMIN AUTHENTICATION ====================
def check_admin():
    """Check if user is admin"""
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
        st.sidebar.markdown(f"### 👑 Admin Mode")
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

# ==================== RAG FUNCTIONS ====================
def process_pdf(file):
    """Process uploaded PDF and save to persistent storage"""
    if not RAG_AVAILABLE:
        return None, 0
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.getvalue())
        tmp_path = tmp.name
    
    try:
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        vectorstore = Chroma.from_documents(
            chunks, 
            embeddings,
            persist_directory=VECTORSTORE_PATH
        )
        vectorstore.persist()
        save_metadata(file.name, len(chunks))
        return vectorstore, len(chunks)
    finally:
        os.unlink(tmp_path)

def extract_symptoms(text: str) -> List[str]:
    import re
    patterns = [
        (r"(headache|migraine)", "Headache"),
        (r"(fever|temperature|chills)", "Fever"),
        (r"(cough|phlegm)", "Cough"),
        (r"(pain|ache|hurt)", "Pain"),
        (r"(nausea|vomiting|dizzy)", "Nausea/Dizziness"),
        (r"(rash|itch|redness)", "Rash"),
        (r"(fatigue|tired|exhaustion)", "Fatigue"),
        (r"(shortness of breath|difficulty breathing)", "Breathing Difficulty"),
        (r"(chest pain)", "Chest Pain"),
        (r"(palpitations|racing heart)", "Palpitations"),
    ]
    symptoms = set()
    text_lower = text.lower()
    for pattern, symptom in patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            symptoms.add(symptom)
    return list(symptoms)

def check_emergency(text: str) -> List[str]:
    keywords = ["chest pain", "shortness of breath", "severe bleeding", "loss of consciousness", "stroke", "heart attack", "seizure", "choking"]
    found = []
    text_lower = text.lower()
    for keyword in keywords:
        if keyword in text_lower:
            found.append(keyword)
    return found

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
4. Use bullet points
5. Include medical disclaimer

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
            
            col1, col2 = st.columns(2)
            with col1:
                if uploaded_file and st.button("📚 Upload", type="primary", use_container_width=True):
                    with st.spinner("🔄 Processing and saving..."):
                        try:
                            vectorstore, chunk_count = process_pdf(uploaded_file)
                            if vectorstore:
                                st.session_state.vectorstore = vectorstore
                                st.session_state.docs_loaded = True
                                st.session_state.doc_name = uploaded_file.name
                                st.success(f"✅ Saved {chunk_count} sections")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Failed to process document")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            
            with col2:
                if st.button("🗑️ Clear Storage", use_container_width=True):
                    clear_persistent_storage()
                    st.session_state.vectorstore = None
                    st.session_state.docs_loaded = False
                    st.session_state.doc_name = None
                    st.success("✅ Storage cleared!")
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
                <div class="number">{len(st.session_state.symptoms)}</div>
                <div class="label">🩺 Symptoms</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.messages:
        with st.container():
            st.markdown("""
            <div class="sidebar-section">
                <h3>💾 Export Chat</h3>
            """, unsafe_allow_html=True)
            
            if st.button("📥 Download Chat", use_container_width=True):
                chat_data = {
                    "conversation_id": st.session_state.conversation_id,
                    "timestamp": datetime.now().isoformat(),
                    "messages": st.session_state.messages
                }
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(chat_data, indent=2),
                    file_name=f"chat_{st.session_state.conversation_id}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🔄 New Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.symptoms = []
        st.session_state.emergency = False
        st.rerun()

# ==================== MAIN CONTENT (PUBLIC) ====================
if st.session_state.emergency:
    st.markdown(f"""
    <div class="emergency-warning">
        <strong>🚨 EMERGENCY SYMPTOMS DETECTED:</strong> {', '.join(st.session_state.emergency)}
        <br><br>
        <strong>Please seek immediate medical attention!</strong>
    </div>
    """, unsafe_allow_html=True)

if not st.session_state.messages:
    # ADDED unsafe_allow_html=True HERE TO FIX YOUR FRONTEND LAYOUT
    st.markdown("""
    <div class="welcome-card">
        <h3>💙 Welcome to Dr. Medibot!</h3>
        <p class="subtitle">Your AI-powered medical assistant for evidence-based health information.</p>
        
        <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin: 1.5rem 0;">
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 12px; text-align: center; flex: 1; min-width: 120px;">
                <div style="font-size: 2.5rem;">📚</div>
                <div style="font-weight: 600; font-size: 0.85rem;">Medical Documents</div>
            </div>
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 12px; text-align: center; flex: 1; min-width: 120px;">
                <div style="font-size: 2.5rem;">💬</div>
                <div style="font-weight: 600; font-size: 0.85rem;">Ask Questions</div>
            </div>
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 12px; text-align: center; flex: 1; min-width: 120px;">
                <div style="font-size: 2.5rem;">🤖</div>
                <div style="font-weight: 600; font-size: 0.85rem;">AI Answers</div>
            </div>
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 12px; text-align: center; flex: 1; min-width: 120px;">
                <div style="font-size: 2.5rem;">⚠️</div>
                <div style="font-weight: 600; font-size: 0.85rem;">Emergency Alerts</div>
            </div>
        </div>
        
        <hr>
        
        <h4>✨ How It Works</h4>
        <ol style="color: #555; line-height: 2;">
            <li><strong>Medical documents</strong> are pre-loaded by healthcare professionals</li>
            <li><strong>Ask</strong> questions about symptoms, treatments, or conditions</li>
            <li><strong>Get</strong> evidence-based answers from trusted medical sources</li>
            <li><strong>Receive</strong> emergency warnings for critical symptoms</li>
        </ol>
        
        <hr>
        
        <h4>💡 Example Questions</h4>
        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
            <span style="background: #e8f5e9; padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.85rem;">What are the symptoms of diabetes?</span>
            <span style="background: #e8f5e9; padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.85rem;">How is hypertension treated?</span>
            <span style="background: #e8f5e9; padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.85rem;">What causes chest pain?</span>
            <span style="background: #e8f5e9; padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.85rem;">What medications are used for heart disease?</span>
        </div>
        
        <hr>
        
        <div style="background: #fff3e0; padding: 1rem; border-radius: 12px; border-left: 4px solid #ff9800;">
            <strong>⚠️ Medical Disclaimer:</strong>
            <span style="color: #666; font-size: 0.9rem;">This is for educational purposes only. Always consult a healthcare professional for medical advice.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.docs_loaded:
        st.info("📚 Medical knowledge base is being prepared. Please check back soon!")

else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">👤 <strong>You</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">🩺 <strong>Dr. Medibot</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)

if st.session_state.docs_loaded:
    user_input = st.chat_input("Ask a question about medical topics...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        emergency = check_emergency(user_input)
        if emergency:
            st.session_state.emergency = emergency
        
        symptoms = extract_symptoms(user_input)
        st.session_state.symptoms.extend(symptoms)
        
        with st.spinner("🩺 Dr. Medibot is thinking..."):
            try:
                if RAG_AVAILABLE and st.session_state.vectorstore:
                    results = st.session_state.vectorstore.similarity_search(user_input, k=4)
                    if results:
                        context = "\n\n".join([r.page_content for r in results])
                        history = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages[-5:]])
                        response = get_response(user_input, context, history)
                        
                        with st.expander("📚 Sources"):
                            for i, doc in enumerate(results):
                                page = doc.metadata.get("page", "Unknown")
                                st.caption(f"Source {i+1} - Page {page}")
                                st.text(doc.page_content[:300] + "...")
                                st.divider()
                    else:
                        response = "I couldn't find relevant information in the medical documents. Please try rephrasing your question."
                else:
                    response = f"Thanks for your question: '{user_input}'\n\nI'll search the medical documents for the answer."
                
                response += """

---
⚠️ **Medical Disclaimer:** This information is for educational purposes only. Always consult a qualified healthcare provider."""
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
else:
    st.info("📚 The medical knowledge base is being prepared. Please check back soon!")

st.markdown("""
<div class="footer">
    <p>🩺 Dr. Medibot v2.0 • Powered by Groq AI</p>
    <p class="disclaimer">⚠️ For educational purposes only. Always consult a healthcare professional.</p>
    <p style="font-size: 0.7rem; color: #ccc;">Made with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)