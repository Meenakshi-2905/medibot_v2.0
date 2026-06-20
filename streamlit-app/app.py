"""
🩺 Dr. Medibot - Complete Medical AI Assistant
Beautiful UI with all features including Groq AI integration
"""

import streamlit as st
import os
import tempfile
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any

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
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

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
    /* ===== GLOBAL ===== */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8edf5 100%);
    }
    
    /* ===== MAIN HEADER ===== */
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
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 50%;
        pointer-events: none;
    }
    
    .main-header::after {
        content: '';
        position: absolute;
        bottom: -40%;
        left: 10%;
        width: 200px;
        height: 200px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 50%;
        pointer-events: none;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
    }
    
    .main-header h1 span {
        background: rgba(255, 255, 255, 0.15);
        padding: 0.1rem 0.8rem;
        border-radius: 12px;
        display: inline-block;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
        position: relative;
        z-index: 1;
    }
    
    .header-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.3rem 1rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.5rem;
        backdrop-filter: blur(10px);
        position: relative;
        z-index: 1;
    }
    
    /* ===== SIDEBAR ===== */
    .css-1d391kg, .css-1lcbmhc {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 0 20px 20px 0;
    }
    
    .sidebar-section {
        background: white;
        padding: 1.2rem;
        border-radius: 16px;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(0, 0, 0, 0.04);
    }
    
    .sidebar-section h3 {
        color: #0a5c3f;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* ===== CHAT MESSAGES ===== */
    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 5px 18px;
        margin: 0.5rem 0;
        margin-left: 20%;
        border: 1px solid #90caf9;
        box-shadow: 0 2px 8px rgba(144, 202, 249, 0.2);
        animation: slideInRight 0.4s ease;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 18px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border-left: 4px solid #0a5c3f;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        animation: slideInLeft 0.4s ease;
    }
    
    .assistant-message strong {
        color: #0a5c3f;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* ===== EMERGENCY WARNING ===== */
    .emergency-warning {
        background: linear-gradient(135deg, #ff1744 0%, #d50000 100%);
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        animation: pulse 1.5s infinite;
        box-shadow: 0 8px 30px rgba(255, 23, 68, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .emergency-warning strong {
        font-size: 1.1rem;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.9; transform: scale(1.01); }
    }
    
    /* ===== WELCOME CARD ===== */
    .welcome-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(0, 0, 0, 0.04);
        margin: 1rem 0;
    }
    
    .welcome-card h3 {
        color: #0a5c3f;
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .welcome-card .subtitle {
        color: #666;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .feature-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        transition: all 0.3s;
    }
    
    .feature-item:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    .feature-item .icon {
        font-size: 2rem;
        display: block;
        margin-bottom: 0.3rem;
    }
    
    .feature-item .label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #333;
    }
    
    /* ===== STATS CARDS ===== */
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(0, 0, 0, 0.04);
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
    
    /* ===== STATUS INDICATOR ===== */
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
    
    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        padding: 2rem 0 0.5rem;
        border-top: 1px solid rgba(0, 0, 0, 0.06);
        margin-top: 2rem;
    }
    
    .footer p {
        color: #999;
        font-size: 0.8rem;
        margin: 0.2rem 0;
    }
    
    .footer .disclaimer {
        color: #ff6b6b;
        font-size: 0.75rem;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        .main-header {
            padding: 1.5rem;
        }
        .user-message, .assistant-message {
            margin-left: 5%;
            margin-right: 5%;
        }
        .feature-grid {
            grid-template-columns: 1fr 1fr;
        }
    }
    
    @media (max-width: 480px) {
        .feature-grid {
            grid-template-columns: 1fr;
        }
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

init_session_state()

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
    """Process uploaded PDF and create vector store"""
    if not RAG_AVAILABLE:
        return None, 0
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.getvalue())
        tmp_path = tmp.name
    
    try:
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = splitter.split_documents(docs)
        
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(
            chunks, 
            embeddings,
            persist_directory="./medibot_db"
        )
        vectorstore.persist()
        
        return vectorstore, len(chunks)
    
    finally:
        os.unlink(tmp_path)

def extract_symptoms(text: str) -> List[str]:
    import re
    symptom_patterns = [
        (r"(headache|migraine|head pain)", "Headache"),
        (r"(fever|temperature|chills)", "Fever"),
        (r"(cough|phlegm|mucus)", "Cough"),
        (r"(pain|ache|hurt|sore)", "Pain"),
        (r"(nausea|vomiting|dizzy|dizziness)", "Nausea/Dizziness"),
        (r"(rash|itch|redness|hives)", "Rash"),
        (r"(fatigue|tired|exhaustion|weakness)", "Fatigue"),
        (r"(shortness of breath|difficulty breathing|SOB)", "Breathing Difficulty"),
        (r"(sore throat|hoarse)", "Sore Throat"),
        (r"(runny nose|congestion|stuffy)", "Nasal Congestion"),
        (r"(abdominal pain|stomach ache|cramping)", "Abdominal Pain"),
        (r"(chest pain|heart pain)", "Chest Pain"),
        (r"(palpitations|racing heart)", "Palpitations"),
        (r"(joint pain|arthritis)", "Joint Pain"),
        (r"(back pain)", "Back Pain"),
    ]
    
    symptoms = set()
    text_lower = text.lower()
    for pattern, symptom in symptom_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            symptoms.add(symptom)
    return list(symptoms)

def check_emergency(text: str) -> List[str]:
    emergency_keywords = [
        "chest pain", "shortness of breath", "severe bleeding",
        "loss of consciousness", "stroke", "heart attack",
        "seizure", "difficulty breathing", "choking",
        "severe allergic reaction", "anaphylaxis"
    ]
    emergency_found = []
    text_lower = text.lower()
    for keyword in emergency_keywords:
        if keyword in text_lower:
            emergency_found.append(keyword)
    return emergency_found

def get_response(query: str, context: str, history: str) -> str:
    """Generate response using Groq"""
    client = get_groq_client()
    
    if not client:
        return "⚠️ Groq is not available. Please check your API key."
    
    prompt = f"""You are Dr. Medibot, a caring and professional medical AI assistant.
Use ONLY the provided context to answer questions.

CONTEXT (from medical documents):
{context}

CONVERSATION HISTORY:
{history}

USER QUESTION: {query}

Guidelines:
1. Answer based ONLY on the context provided
2. Be warm, empathetic, and professional
3. If the context doesn't contain the answer, say so clearly
4. Keep responses concise but informative
5. Use bullet points for clarity when appropriate
6. Always include a disclaimer about consulting a real doctor

YOUR RESPONSE:"""

    try:
        model = st.secrets.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024,
            top_p=0.9,
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
            <p>Your AI Medical Assistant — Evidence-Based Answers from Your Documents</p>
            <div class="header-badge">
                ⚡ Powered by Groq AI &nbsp;•&nbsp; 🔒 100% Private
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    # --- Brand ---
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
        <span style="font-size: 3rem;">🩺</span>
        <h2 style="color: #0a5c3f; margin: 0;">Dr. Medibot</h2>
        <p style="color: #888; font-size: 0.8rem;">v2.0 • AI Medical Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- Document Upload ---
    with st.container():
        st.markdown("""
        <div class="sidebar-section">
            <h3>📄 Upload Document</h3>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload medical books, research papers, or clinical guidelines"
        )
        
        if uploaded_file and st.button("📚 Process Document", type="primary", use_container_width=True):
            with st.spinner("🔄 Processing document..."):
                try:
                    st.session_state.doc_name = uploaded_file.name
                    vectorstore, chunk_count = process_pdf(uploaded_file)
                    if vectorstore:
                        st.session_state.vectorstore = vectorstore
                        st.session_state.docs_loaded = True
                        st.success(f"✅ Loaded {chunk_count} sections from {uploaded_file.name}")
                        st.balloons()
                    else:
                        st.error("❌ RAG libraries not installed. Please install langchain, chromadb, etc.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # --- Status ---
    with st.container():
        st.markdown("""
        <div class="sidebar-section">
            <h3>📊 Status</h3>
        """, unsafe_allow_html=True)
        
        if st.session_state.docs_loaded:
            st.success(f"✅ Document loaded: {st.session_state.doc_name}")
        else:
            st.warning("⚠️ No document loaded")
        
        # API Status
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
    
    # --- Statistics ---
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
    
    # --- Export ---
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
                json_str = json.dumps(chat_data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"chat_{st.session_state.conversation_id}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # --- Clear ---
    st.markdown("---")
    if st.button("🔄 New Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.symptoms = []
        st.session_state.emergency = False
        st.rerun()

# ==================== MAIN CONTENT ====================
# --- Emergency Warning ---
if st.session_state.emergency:
    st.markdown(f"""
    <div class="emergency-warning">
        <strong>🚨 EMERGENCY SYMPTOMS DETECTED:</strong> {', '.join(st.session_state.emergency)}
        <br><br>
        <strong>Please seek immediate medical attention:</strong>
        <br>• Call emergency services (911 in US / 112 in EU)
        <br>• Go to the nearest emergency room
        <br>• Do not wait for symptoms to improve
    </div>
    """, unsafe_allow_html=True)

# --- Chat Display ---
if not st.session_state.messages:
    # Welcome Screen
    st.markdown("""
    <div class="welcome-card">
        <h3>💙 Welcome to Dr. Medibot!</h3>
        <p class="subtitle">Your AI-powered medical assistant for evidence-based health information.</p>
        
        <div class="feature-grid">
            <div class="feature-item">
                <span class="icon">📄</span>
                <span class="label">Upload PDF</span>
            </div>
            <div class="feature-item">
                <span class="icon">💬</span>
                <span class="label">Ask Questions</span>
            </div>
            <div class="feature-item">
                <span class="icon">🤖</span>
                <span class="label">AI Answers</span>
            </div>
            <div class="feature-item">
                <span class="icon">⚠️</span>
                <span class="label">Emergency Alerts</span>
            </div>
        </div>
        
        <hr>
        
        <h4>✨ How It Works</h4>
        <ol style="color: #555; line-height: 2;">
            <li><strong>Upload</strong> a medical PDF in the sidebar</li>
            <li><strong>Ask</strong> questions about symptoms, treatments, or conditions</li>
            <li><strong>Get</strong> evidence-based answers from your documents</li>
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
        st.info("👈 Please upload a medical PDF in the sidebar to start chatting!")

else:
    # Chat History
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">👤 <strong>You</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">🩺 <strong>Dr. Medibot</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)

# --- Chat Input ---
if st.session_state.docs_loaded:
    user_input = st.chat_input("Ask a question about your medical document...")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Check for emergency
        emergency = check_emergency(user_input)
        if emergency:
            st.session_state.emergency = emergency
        
        # Extract symptoms
        symptoms = extract_symptoms(user_input)
        st.session_state.symptoms.extend(symptoms)
        
        # Generate response
        with st.spinner("🩺 Dr. Medibot is thinking..."):
            try:
                if RAG_AVAILABLE and st.session_state.vectorstore:
                    # Search documents
                    results = st.session_state.vectorstore.similarity_search(user_input, k=4)
                    
                    if results:
                        context = "\n\n".join([r.page_content for r in results])
                        
                        # Build history
                        history = "\n".join([
                            f"{m['role'].upper()}: {m['content']}" 
                            for m in st.session_state.messages[-5:]
                        ])
                        
                        response = get_response(user_input, context, history)
                        
                        # Show sources
                        with st.expander("📚 Sources"):
                            for i, doc in enumerate(results):
                                page = doc.metadata.get("page", "Unknown")
                                st.caption(f"Source {i+1} - Page {page}")
                                st.text(doc.page_content[:300] + "...")
                                st.divider()
                    else:
                        response = "I couldn't find relevant information in your document. Please try rephrasing your question."
                else:
                    # Fallback if RAG not available
                    response = f"""Thanks for your question: "{user_input}"

I'll search your document for the answer. 

💡 **Note:** For full AI-powered answers with document search, please install the required RAG libraries (langchain, chromadb, etc.).

**Based on your document:** I'll provide evidence-based answers once the RAG system is properly configured."""
                
                # Add disclaimer
                response += """

---
⚠️ **Medical Disclaimer:** This information is for educational purposes only and should not replace professional medical advice. Always consult a qualified healthcare provider."""
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
else:
    st.info("👈 Please upload a medical PDF in the sidebar to start chatting!")

# ==================== FOOTER ====================
st.markdown("""
<div class="footer">
    <p>🩺 Dr. Medibot v2.0 • Powered by Groq AI</p>
    <p class="disclaimer">⚠️ For educational purposes only. Always consult a healthcare professional.</p>
    <p style="font-size: 0.7rem; color: #ccc;">Made with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)