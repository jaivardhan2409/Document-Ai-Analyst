import streamlit as st
import requests
import os
import json
from datetime import datetime, timedelta

# Backend URL Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

# Session duration in minutes
SESSION_DURATION_MINUTES = 15
SESSION_FILE = "/tmp/rag_session.json"

st.set_page_config(
    page_title="RAG AI Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# Premium CSS Injection
# ==========================================
st.markdown("""
<style>
/* ===== Google Font ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ===== Global Overrides ===== */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ===== Hide Streamlit Branding ===== */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ===== Custom Scrollbar ===== */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0f172a;
}
::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #475569;
}

/* ===== Sidebar Styling ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
    border-right: 1px solid #334155 !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdown"] h1,
[data-testid="stSidebar"] [data-testid="stMarkdown"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdown"] h3 {
    color: #f8fafc !important;
    font-weight: 600 !important;
}

/* ===== Button Styling ===== */
.stButton > button {
    background: linear-gradient(135deg, #818cf8 0%, #a78bfa 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.2rem !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(129, 140, 248, 0.25) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(129, 140, 248, 0.4) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ===== Text Input Styling ===== */
.stTextInput > div > div > input {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    color: #f8fafc !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.15) !important;
}

/* ===== Chat Input Styling ===== */
[data-testid="stChatInput"] {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    padding: 4px !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.15) !important;
}

[data-testid="stChatInput"] textarea {
    background-color: transparent !important;
    border: none !important;
    color: #f8fafc !important;
}

/* ===== Chat Message Styling ===== */
[data-testid="stChatMessage"] {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 16px !important;
    padding: 1rem 1.2rem !important;
    margin-bottom: 1rem !important;
    backdrop-filter: blur(10px) !important;
    animation: fadeInUp 0.3s ease-out;
}

/* ===== Select Box ===== */
.stSelectbox > div > div {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
}

/* ===== Expander Styling ===== */
.streamlit-expanderHeader {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
}

/* ===== File Uploader ===== */
[data-testid="stFileUploader"] {
    background-color: #1e293b !important;
    border: 1px dashed #334155 !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: #818cf8 !important;
}

/* ===== Tabs Styling ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: #1e293b !important;
    border-radius: 10px !important;
    border: 1px solid #334155 !important;
    color: #94a3b8 !important;
    padding: 0.5rem 1.5rem !important;
    font-weight: 500 !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #818cf8 0%, #a78bfa 100%) !important;
    border: none !important;
    color: white !important;
}

/* ===== Divider ===== */
[data-testid="stHorizontalBlock"] hr {
    border-color: #334155 !important;
}

/* ===== Success/Error Alerts ===== */
.stSuccess {
    background-color: rgba(52, 211, 153, 0.1) !important;
    border: 1px solid rgba(52, 211, 153, 0.3) !important;
    border-radius: 10px !important;
    color: #34d399 !important;
}

.stError {
    background-color: rgba(248, 113, 113, 0.1) !important;
    border: 1px solid rgba(248, 113, 113, 0.3) !important;
    border-radius: 10px !important;
}

/* ===== Info Alert (Sources) ===== */
.stAlert {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    color: #94a3b8 !important;
}

/* ===== Animations ===== */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

.streaming-cursor {
    animation: pulse 1s ease-in-out infinite;
    color: #818cf8;
    font-weight: bold;
}

/* ===== Login Page ===== */
.login-container {
    max-width: 440px;
    margin: 4rem auto;
    padding: 2.5rem;
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(20px);
    border: 1px solid #334155;
    border-radius: 20px;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
}

.login-header {
    text-align: center;
    margin-bottom: 2rem;
}

.login-header h1 {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

.login-header p {
    color: #94a3b8;
    font-size: 0.95rem;
}

/* ===== App Header ===== */
.app-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid #334155;
    margin-bottom: 1.5rem;
}

.app-header h1 {
    font-size: 1.6rem;
    font-weight: 700;
    background: linear-gradient(135deg, #818cf8, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

/* ===== Collection Badge ===== */
.collection-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(129, 140, 248, 0.15);
    border: 1px solid rgba(129, 140, 248, 0.3);
    color: #a5b4fc;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
}

/* ===== Stats Pills ===== */
.stats-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(129, 140, 248, 0.1);
    color: #94a3b8;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    margin-right: 6px;
}

/* ===== Section Headers ===== */
.section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 1rem 0 0.5rem 0;
}

/* ===== Supported Files Label ===== */
.file-types {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-top: 6px;
}

.file-type-badge {
    background: rgba(129, 140, 248, 0.1);
    border: 1px solid rgba(129, 140, 248, 0.2);
    color: #a5b4fc;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 500;
}

/* ===== Logout Button Override ===== */
.st-key-logout_btn > div > button {
    background: transparent !important;
    border: 1px solid #475569 !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
}

.st-key-logout_btn > div > button:hover {
    border-color: #f87171 !important;
    color: #f87171 !important;
    background: rgba(248, 113, 113, 0.1) !important;
    box-shadow: none !important;
}

/* ===== Delete Button Override ===== */
.st-key-delete_col_btn > div > button {
    background: transparent !important;
    border: 1px solid #475569 !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
    font-size: 0.8rem !important;
}

.st-key-delete_col_btn > div > button:hover {
    border-color: #f87171 !important;
    color: #f87171 !important;
    background: rgba(248, 113, 113, 0.1) !important;
    box-shadow: none !important;
}

/* ===== Clear Docs Button ===== */
.st-key-clear_docs_btn > div > button {
    background: transparent !important;
    border: 1px solid #475569 !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
    font-size: 0.8rem !important;
}

.st-key-clear_docs_btn > div > button:hover {
    border-color: #fbbf24 !important;
    color: #fbbf24 !important;
    background: rgba(251, 191, 36, 0.1) !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# Session Persistence
# ==========================================
def save_session(token):
    data = {
        "token": token,
        "expires_at": (datetime.now() + timedelta(minutes=SESSION_DURATION_MINUTES)).isoformat()
    }
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)

def load_session():
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
        expires_at = datetime.fromisoformat(data["expires_at"])
        if datetime.now() < expires_at:
            return data["token"]
        else:
            os.remove(SESSION_FILE)
            return None
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None

def clear_session():
    try:
        os.remove(SESSION_FILE)
    except FileNotFoundError:
        pass

# Initialize Session State
if "token" not in st.session_state:
    st.session_state.token = load_session()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_collection" not in st.session_state:
    st.session_state.active_collection = None

if "upload_status" not in st.session_state:
    st.session_state.upload_status = None

def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# ==========================================
# Authentication Functions
# ==========================================
def login(username, password):
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            st.session_state.token = token
            save_session(token)
            st.rerun()
        else:
            st.error("Invalid username or password")
    except Exception as e:
        st.error(f"Connection error: {e}")

def register(username, email, password):
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json={"username": username, "email": email, "password": password}
        )
        if response.status_code == 200:
            st.success("Account created! You can now log in.")
        else:
            detail = response.json().get("detail", "Registration failed")
            st.error(detail)
    except Exception as e:
        st.error(f"Connection error: {e}")

def logout():
    st.session_state.token = None
    st.session_state.messages = []
    st.session_state.active_collection = None
    clear_session()
    st.rerun()

# ==========================================
# LOGIN PAGE
# ==========================================
if not st.session_state.token:
    # Centered login card
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div class="login-header">
            <h1>🧠 RAG AI Assistant</h1>
            <p>Your intelligent document companion</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        with tab1:
            log_user = st.text_input("Username", key="log_user", placeholder="Enter your username")
            log_pass = st.text_input("Password", type="password", key="log_pass", placeholder="Enter your password")
            st.markdown("")  # Spacer
            if st.button("Sign In", use_container_width=True, key="login_btn"):
                if log_user and log_pass:
                    login(log_user, log_pass)
                else:
                    st.warning("Please fill in all fields")
                
        with tab2:
            reg_user = st.text_input("Username", key="reg_user", placeholder="Choose a username")
            reg_email = st.text_input("Email", key="reg_email", placeholder="your@email.com")
            reg_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="Create a password")
            st.markdown("")
            if st.button("Create Account", use_container_width=True, key="register_btn"):
                if reg_user and reg_email and reg_pass:
                    register(reg_user, reg_email, reg_pass)
                else:
                    st.warning("Please fill in all fields")
    
    st.stop()

# ==========================================
# MAIN APPLICATION
# ==========================================

# App Header
st.markdown("""
<div class="app-header">
    <h1>🧠 RAG AI Assistant</h1>
</div>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    # ---- Knowledge Bases ----
    st.markdown('<div class="section-header">📚 KNOWLEDGE BASES</div>', unsafe_allow_html=True)
    
    # Fetch collections
    try:
        cols_response = requests.get(
            f"{BACKEND_URL}/api/documents/collections",
            headers=auth_headers()
        )
        collections = cols_response.json() if cols_response.status_code == 200 else []
    except Exception:
        collections = []
    
    # Collection selector
    collection_names = ["Default"] + [c["name"] for c in collections]
    collection_ids = [None] + [c["id"] for c in collections]
    
    selected_idx = st.selectbox(
        "Active Knowledge Base",
        range(len(collection_names)),
        format_func=lambda i: collection_names[i],
        key="collection_selector",
        label_visibility="collapsed"
    )
    
    st.session_state.active_collection = collection_ids[selected_idx]
    
    # Show collection stats
    if selected_idx > 0:
        col_data = collections[selected_idx - 1]
        st.markdown(f"""
        <div style="margin: -0.5rem 0 0.5rem 0;">
            <span class="stats-pill">📄 {col_data['doc_count']} docs</span>
            <span class="stats-pill">🧩 {col_data['chunk_count']} chunks</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Create new collection
    with st.expander("➕ New Knowledge Base"):
        new_col_name = st.text_input("Name", key="new_col_name", placeholder="e.g. Research Papers")
        new_col_desc = st.text_input("Description", key="new_col_desc", placeholder="Optional description")
        if st.button("Create", key="create_col_btn", use_container_width=True):
            if new_col_name:
                try:
                    resp = requests.post(
                        f"{BACKEND_URL}/api/documents/collections",
                        headers=auth_headers(),
                        json={"name": new_col_name, "description": new_col_desc}
                    )
                    if resp.status_code == 200:
                        st.session_state.upload_status = ("success", f"Created '{new_col_name}'!")
                        st.rerun()
                    else:
                        st.error(resp.json().get("detail", "Failed"))
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Enter a name")
    
    # Delete collection
    if selected_idx > 0:
        if st.button("🗑️ Delete Collection", key="delete_col_btn", use_container_width=True):
            try:
                resp = requests.delete(
                    f"{BACKEND_URL}/api/documents/collections/{collection_ids[selected_idx]}",
                    headers=auth_headers()
                )
                if resp.status_code == 200:
                    st.session_state.active_collection = None
                    st.session_state.upload_status = ("success", "Collection deleted")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.markdown("---")
    
    # ---- Document Upload ----
    st.markdown('<div class="section-header">📤 UPLOAD DOCUMENT</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="file-types">
        <span class="file-type-badge">PDF</span>
        <span class="file-type-badge">TXT</span>
        <span class="file-type-badge">DOCX</span>
        <span class="file-type-badge">CSV</span>
        <span class="file-type-badge">MD</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    
    uploaded_file = st.file_uploader(
        "Drop your file here",
        type=["pdf", "txt", "docx", "csv", "md"],
        key="file_uploader",
        label_visibility="collapsed"
    )
    
    # Show upload status
    if st.session_state.upload_status:
        msg_type, msg_text = st.session_state.upload_status
        if msg_type == "success":
            st.success(msg_text)
        elif msg_type == "error":
            st.error(msg_text)
        st.session_state.upload_status = None
    
    if st.button("Upload & Process", key="upload_btn", use_container_width=True):
        if uploaded_file is not None:
            with st.spinner("Processing..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                params = {}
                if st.session_state.active_collection:
                    params["collection_id"] = st.session_state.active_collection
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/documents/upload",
                        headers=auth_headers(),
                        files=files,
                        params=params
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.upload_status = ("success", f"✅ {uploaded_file.name} — {data.get('chunks_created')} chunks")
                        st.rerun()
                    else:
                        st.session_state.upload_status = ("error", f"Failed: {response.text}")
                        st.rerun()
                except Exception as e:
                    st.session_state.upload_status = ("error", f"Error: {e}")
                    st.rerun()
        else:
            st.warning("Select a file first")
    
    # Clear documents button
    if st.button("🧹 Clear All Documents", key="clear_docs_btn", use_container_width=True):
        try:
            chroma = chroma_name if st.session_state.active_collection else "rag_collection"
            if st.session_state.active_collection:
                # Delete the custom collection
                col_id = st.session_state.active_collection
                resp = requests.delete(
                    f"{BACKEND_URL}/api/documents/collections/{col_id}",
                    headers=auth_headers()
                )
            else:
                # Clear default collection
                resp = requests.delete(
                    f"{BACKEND_URL}/api/documents/clear-default",
                    headers=auth_headers()
                )
            if resp.status_code == 200:
                st.session_state.upload_status = ("success", "🧹 All documents cleared!")
                st.rerun()
            else:
                st.error("Failed to clear")
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.markdown("---")
    
    # ---- Footer ----
    st.caption(f"⏱️ Session: {SESSION_DURATION_MINUTES} min")
    st.button("Sign Out", key="logout_btn", use_container_width=True, on_click=logout)

# ==========================================
# CHAT INTERFACE
# ==========================================

# Determine active collection
if st.session_state.active_collection:
    active_col = next(
        (c for c in collections if c["id"] == st.session_state.active_collection),
        None
    )
    if active_col:
        chroma_name = f"col_{active_col['id'][:8]}"
        st.caption(f"📚 Chatting with: **{active_col['name']}**")
    else:
        chroma_name = "rag_collection"
else:
    chroma_name = "rag_collection"
    st.caption("📚 Chatting with: **Default**")

st.markdown("")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander(f"📎 {len(message['sources'])} Sources"):
                for source in message["sources"]:
                    score = source['similarity']
                    st.markdown(f"**Relevance:** `{score:.3f}`")
                    st.info(source['text'][:300] + ("..." if len(source['text']) > 300 else ""))

# Chat input
if prompt := st.chat_input("Ask anything about your documents..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        payload = {
            "query": prompt,
            "top_k": 5,
            "collection_name": chroma_name
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/chat/query/stream",
                headers=auth_headers(),
                json=payload,
                stream=True
            )
            
            if response.status_code == 200:
                full_answer = ""
                sources = []
                
                for line in response.iter_lines(decode_unicode=True):
                    if line and line.startswith("data: "):
                        data_str = line[6:]
                        
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            event = json.loads(data_str)
                            if event["type"] == "text":
                                full_answer += event["content"]
                                message_placeholder.markdown(full_answer + " ▌")
                            elif event["type"] == "sources":
                                sources = event["content"]
                        except json.JSONDecodeError:
                            continue
                
                # Final render
                message_placeholder.markdown(full_answer)
                
                if sources:
                    with st.expander(f"📎 {len(sources)} Sources"):
                        for source in sources:
                            score = source['similarity']
                            st.markdown(f"**Relevance:** `{score:.3f}`")
                            st.info(source['text'][:300] + ("..." if len(source['text']) > 300 else ""))
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_answer,
                    "sources": sources
                })
            elif response.status_code == 401:
                message_placeholder.markdown("⏰ Session expired. Please sign in again.")
                st.session_state.token = None
                clear_session()
                st.rerun()
            else:
                message_placeholder.markdown(f"❌ Error: {response.text}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {response.text}"})
                
        except Exception as e:
            message_placeholder.markdown(f"❌ Connection error: {e}")
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
