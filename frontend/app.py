import streamlit as st
import requests
import os
import json
from datetime import datetime, timedelta

# Backend URL Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Session duration in minutes
SESSION_DURATION_MINUTES = 15
SESSION_FILE = "/tmp/rag_session.json"

st.set_page_config(
    page_title="Document AI Analyst",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# Session Persistence & Initialization
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

# Initialize States
if "token" not in st.session_state:
    st.session_state.token = load_session()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_collection" not in st.session_state:
    st.session_state.active_collection = None

if "upload_status" not in st.session_state:
    st.session_state.upload_status = None

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "current_page" not in st.session_state:
    st.session_state.current_page = "chat" if st.session_state.token else "landing"

# Force routing if token state changes
if st.session_state.token and st.session_state.current_page in ["landing", "login", "register"]:
    st.session_state.current_page = "chat"
elif not st.session_state.token and st.session_state.current_page == "chat":
    st.session_state.current_page = "landing"

def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# ==========================================
# Dynamic Theme Variables
# ==========================================
DARK_VARS = """
    --bg-main: #0b0914;
    --bg-card: #13111f;
    --border: #2a2542;
    --text-main: #f8f7fa;
    --text-muted: #9e98b5;
    --accent: #8b5cf6;
    --accent-hover: #7c3aed;
    --input-bg: #1f1c2e;
    --input-text: #f8f7fa;
"""

LIGHT_VARS = """
    --bg-main: #f5f3ff;
    --bg-card: #ffffff;
    --border: #ddd6fe;
    --text-main: #1e1b4b;
    --text-muted: #6b7280;
    --accent: #6366f1;
    --accent-hover: #4f46e5;
    --input-bg: #ffffff;
    --input-text: #1e1b4b;
"""

# ==========================================
# Premium CSS Injection
# ==========================================
theme_vars = DARK_VARS if st.session_state.theme == "dark" else LIGHT_VARS

st.markdown(f"""
<style>
/* ===== Google Font ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {{
    {theme_vars}
}}

/* ===== Global Overrides ===== */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
}}

/* Force background colors on the main app and Streamlit base containers */
html, body, .stApp, [data-testid="stHeader"], [data-testid="stBottomBlockContainer"], [data-testid="stBottom"] > div, [data-testid="stBottom"] {{
    background-color: var(--bg-main) !important;
    color: var(--text-main) !important;
}}

/* Force transparent/card backgrounds on specific dark-retaining components */
[data-testid="stFileUploadDropzone"], [data-testid="stFileUploader"] section, [data-testid="stChatInput"], [data-testid="stChatInput"] textarea {{
    background-color: var(--bg-card) !important;
    color: var(--text-main) !important;
}}

/* Fix file uploader and buttons inside it */
[data-testid="stFileUploadDropzone"] *, [data-testid="stFileUploader"] button {{
    color: var(--text-main) !important;
}}

[data-testid="stFileUploader"] button {{
    background-color: var(--bg-main) !important;
    border: 1px solid var(--border) !important;
}}

/* Ensure all text assumes primary color by default */
p, h1, h2, h3, h4, h5, h6, span, div {{
    color: var(--text-main) !important;
}}

/* ===== Hide Streamlit Branding ===== */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

/* ===== Custom Scrollbar ===== */
::-webkit-scrollbar {{
    width: 6px;
    height: 6px;
}}
::-webkit-scrollbar-track {{
    background: transparent;
}}
::-webkit-scrollbar-thumb {{
    background: var(--border);
    border-radius: 3px;
}}

/* ===== Sidebar Styling ===== */
[data-testid="stSidebar"] {{
    background-color: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}}

/* ===== Button Styling ===== */
.stButton > button {{
    background-color: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.2rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
}}

.stButton > button:hover {{
    background-color: var(--accent-hover) !important;
}}

/* Reduce Streamlit default top padding */
.block-container {{
    padding-top: 2rem !important;
}}

/* ===== Landing Page Styling ===== */
.hero-container {{
    text-align: center;
    margin-top: 1rem;
    margin-bottom: 3rem;
}}
.hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.9rem;
    color: var(--accent) !important;
    margin-bottom: 2rem;
}}
.hero-title {{
    font-size: 3.5rem;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 1rem;
}}
.hero-title span {{
    background: linear-gradient(90deg, var(--accent), #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
}}
.hero-subtitle {{
    font-size: 1.2rem;
    color: var(--text-muted) !important;
    max-width: 600px;
    margin: 0 auto 2.5rem auto;
    line-height: 1.6;
    display: inline-block;
}}

.feature-card {{
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    height: 100%;
    transition: transform 0.2s;
}}
.feature-card:hover {{
    border-color: var(--accent);
}}
.feature-icon {{
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: var(--accent) !important;
}}
.feature-title {{
    font-weight: 600;
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
}}
.feature-desc {{
    font-size: 0.9rem;
    color: var(--text-muted) !important;
    line-height: 1.5;
}}

/* ===== Login Modal Styling ===== */
.login-wrapper {{
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 80vh;
}}
.login-card {{
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2.5rem;
    width: 100%;
    max-width: 420px;
    margin: 0 auto;
}}
.login-header {{
    text-align: center;
    margin-bottom: 2rem;
}}
.login-icon {{
    background-color: rgba(59, 130, 246, 0.1);
    color: var(--accent) !important;
    width: 48px;
    height: 48px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    font-size: 1.5rem;
    margin-bottom: 1rem;
}}
.login-title {{
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}}
.login-subtitle {{
    color: var(--text-muted) !important;
    font-size: 0.9rem;
}}

/* Auth Input Styling Override */
.stTextInput > div > div > input {{
    background-color: var(--input-bg) !important;
    border: none !important;
    border-radius: 8px !important;
    color: var(--input-text) !important;
    padding: 0.8rem 1rem !important;
}}
.stTextInput > div > div > input:focus {{
    box-shadow: 0 0 0 2px var(--accent) !important;
}}

/* Auth specific buttons */
.st-key-auth_btn > div > button {{
    width: 100% !important;
    padding: 0.8rem !important;
    font-size: 1rem !important;
    margin-top: 1rem !important;
}}

/* Link styling */
.auth-link-container {{
    text-align: center;
    margin-top: 1.5rem;
    font-size: 0.9rem;
    color: var(--text-muted) !important;
}}

/* ===== Chat Input Styling ===== */
[data-testid="stChatInput"], 
.stChatInput,
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] textarea {{
    background-color: var(--bg-card) !important;
    color: var(--text-main) !important;
    border-color: var(--border) !important;
    border-radius: 12px !important;
    padding: 4px !important;
}}

/* Fix placeholder color */
[data-testid="stChatInput"] textarea::placeholder {{
    color: var(--text-muted) !important;
}}

[data-testid="stChatInput"]:focus-within {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
}}

/* ===== Chat Message Styling ===== */
[data-testid="stChatMessage"] {{
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1rem 1.2rem !important;
    margin-bottom: 1rem !important;
}}

/* ===== General UI Components ===== */
.stSelectbox > div > div {{
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
}}

.streamlit-expanderHeader {{
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-muted) !important;
}}

[data-testid="stFileUploader"] {{
    background-color: var(--bg-card) !important;
    border: 1px dashed var(--border) !important;
}}

/* ===== Alerts ===== */
.stSuccess {{
    background-color: rgba(52, 211, 153, 0.1) !important;
    border: 1px solid rgba(52, 211, 153, 0.3) !important;
    color: #34d399 !important;
}}

.stError {{
    background-color: rgba(248, 113, 113, 0.1) !important;
    border: 1px solid rgba(248, 113, 113, 0.3) !important;
}}

/* ===== Badges & Pills ===== */
.collection-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(59, 130, 246, 0.3);
    color: var(--accent) !important;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
}}

.stats-pill {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(59, 130, 246, 0.1);
    color: var(--text-muted) !important;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    margin-right: 6px;
}}

.file-type-badge {{
    background: var(--border);
    color: var(--text-muted) !important;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 500;
}}

/* ===== Special Buttons Override ===== */
.st-key-secondary_btn > div > button,
.st-key-clear_docs_btn > div > button,
.st-key-delete_col_btn > div > button,
.st-key-logout_btn > div > button {{
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text-muted) !important;
}}

.st-key-secondary_btn > div > button:hover {{
    border-color: var(--text-main) !important;
    color: var(--text-main) !important;
}}

/* ===== App Header Area ===== */
.app-header-flex {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}}
.app-header-title {{
    font-size: 1.4rem;
    font-weight: 600;
    margin: 0;
}}
</style>
""", unsafe_allow_html=True)


# ==========================================
# Authentication API Calls
# ==========================================
def api_login(username, password):
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            st.session_state.token = token
            st.session_state.current_page = "chat"
            save_session(token)
            st.rerun()
        else:
            st.error("Invalid username or password")
    except Exception as e:
        st.error(f"Connection error: {e}")

def api_register(username, email, password):
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json={"username": username, "email": email, "password": password}
        )
        if response.status_code == 200:
            st.success("Account created! Please sign in.")
            st.session_state.current_page = "login"
            st.rerun()
        else:
            detail = response.json().get("detail", "Registration failed")
            st.error(detail)
    except Exception as e:
        st.error(f"Connection error: {e}")

def logout():
    st.session_state.token = None
    st.session_state.messages = []
    st.session_state.active_collection = None
    st.session_state.current_page = "landing"
    clear_session()

# ==========================================
# PAGE ROUTERS
# ==========================================

def render_landing_page():
    # Hide sidebar on landing page using CSS hack
    st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">
            <span style="font-size:1.1rem;">✨</span> Next-Gen AI Document Analysis
        </div>
        <h1 class="hero-title">Unlock the Power of <br><span>Your Documents</span></h1>
        <p class="hero-subtitle">Experience the future of research. Upload your most complex PDFs, reports, and contracts, and let our Enterprise Agentic RAG system instantly extract precise, cited insights.</p>
    </div>
    """, unsafe_allow_html=True)

    # Use tighter symmetrical columns to center the two buttons properly without stretching
    col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1.5])
    with col2:
        if st.button("Get Started Free", key="get_started", use_container_width=True):
            st.session_state.current_page = "register"
            st.rerun()
    with col3:
        if st.button("Sign In", key="secondary_btn", use_container_width=True):
            st.session_state.current_page = "login"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Feature Grid
    features = [
        {"icon": "📄", "title": "Multi-Format Upload", "desc": "PDF, DOCX, TXT, and Markdown with smart chunking."},
        {"icon": "🔍", "title": "Semantic Search", "desc": "Two-stage retrieval with high-precision embeddings."},
        {"icon": "💬", "title": "Streaming Chat", "desc": "Real-time AI responses with inline source citations."},
        {"icon": "⚡", "title": "Instant Insights", "desc": "Extract key facts, summaries, and complex data points."},
        {"icon": "🛡️", "title": "Data Isolation", "desc": "Per-user vector collections for complete privacy."},
        {"icon": "🤖", "title": "Advanced LLMs", "desc": "Powered by the robust Google Gemini ecosystem."}
    ]

    for i in range(0, len(features), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(features):
                f = features[i + j]
                cols[j].markdown(f"""
                <div class="feature-card">
                    <div class="feature-icon">{f["icon"]}</div>
                    <div class="feature-title">{f["title"]}</div>
                    <div class="feature-desc">{f["desc"]}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Signature
    st.markdown("""
        <div style="text-align: center; margin-top: 4rem; padding: 2rem 0; border-top: 1px solid var(--border); color: var(--text-muted); font-size: 0.95rem; letter-spacing: 0.5px;">
            Made with ❤️ by <strong style="color: var(--text-main);">Jaivardhan2409</strong>
        </div>
    """, unsafe_allow_html=True)

def render_login_page():
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    /* Target the middle column to act as the login card */
    [data-testid="column"]:nth-of-type(2) {
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-top: 10vh;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
            <div class="login-header">
                <div class="login-icon">🧠</div>
                <h1 class="login-title">Welcome back</h1>
                <p class="login-subtitle">Sign in to your Document AI Analyst account</p>
            </div>
        """, unsafe_allow_html=True)
        
        log_user = st.text_input("Username", key="log_user", label_visibility="collapsed", placeholder="Username")
        log_pass = st.text_input("Password", type="password", key="log_pass", label_visibility="collapsed", placeholder="Password")
        
        if st.button("Sign In", key="auth_btn"):
            if log_user and log_pass:
                api_login(log_user, log_pass)
            else:
                st.warning("Please fill in all fields")
                
        st.markdown("""
            <div class="auth-link-container">
                Don't have an account? 
            </div>
        """, unsafe_allow_html=True)
        if st.button("Create one", key="secondary_btn", use_container_width=True):
            st.session_state.current_page = "register"
            st.rerun()

def render_register_page():
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    /* Target the middle column to act as the register card */
    [data-testid="column"]:nth-of-type(2) {
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-top: 10vh;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
            <div class="login-header">
                <div class="login-icon">✨</div>
                <h1 class="login-title">Create account</h1>
                <p class="login-subtitle">Join Document AI Analyst today</p>
            </div>
        """, unsafe_allow_html=True)
        
        reg_user = st.text_input("Username", key="reg_user", label_visibility="collapsed", placeholder="Username")
        reg_email = st.text_input("Email", key="reg_email", label_visibility="collapsed", placeholder="Email address")
        reg_pass = st.text_input("Password", type="password", key="reg_pass", label_visibility="collapsed", placeholder="Password")
        
        if st.button("Create Account", key="auth_btn"):
            if reg_user and reg_email and reg_pass:
                api_register(reg_user, reg_email, reg_pass)
            else:
                st.warning("Please fill in all fields")
                
        st.markdown("""
            <div class="auth-link-container">
                Already have an account? 
            </div>
        """, unsafe_allow_html=True)
        if st.button("Sign In", key="secondary_btn", use_container_width=True):
            st.session_state.current_page = "login"
            st.rerun()

def render_chat_page():
    # ==========================================
    # HEADER AREA (With Theme Toggle)
    # ==========================================
    h_col1, h_col2 = st.columns([5, 1])
    with h_col1:
        st.markdown("""
        <div class="app-header-flex">
            <h1 class="app-header-title">🧠 Document AI Analyst</h1>
        </div>
        """, unsafe_allow_html=True)
    with h_col2:
        theme_icon = "☀️ Light" if st.session_state.theme == "dark" else "🌙 Dark"
        if st.button(theme_icon, key="secondary_btn", use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()

    # ==========================================
    # SIDEBAR
    # ==========================================
    with st.sidebar:
        st.markdown('<div style="font-weight: 600; color: var(--text-muted); margin-bottom: 0.5rem; font-size: 0.85rem;">📚 KNOWLEDGE BASES</div>', unsafe_allow_html=True)
        
        # Fetch collections
        try:
            cols_response = requests.get(
                f"{BACKEND_URL}/api/documents/collections",
                headers=auth_headers()
            )
            collections = cols_response.json() if cols_response.status_code == 200 else []
        except Exception:
            collections = []
        
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
        
        if selected_idx > 0:
            col_data = collections[selected_idx - 1]
            st.markdown(f"""
            <div style="margin: -0.5rem 0 0.5rem 0;">
                <span class="stats-pill">📄 {col_data['doc_count']} docs</span>
                <span class="stats-pill">🧩 {col_data['chunk_count']} chunks</span>
            </div>
            """, unsafe_allow_html=True)
        
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
        
        st.markdown('<div style="font-weight: 600; color: var(--text-muted); margin-bottom: 0.5rem; font-size: 0.85rem;">📤 UPLOAD DOCUMENT</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px;">
            <span class="file-type-badge">PDF</span>
            <span class="file-type-badge">TXT</span>
            <span class="file-type-badge">DOCX</span>
            <span class="file-type-badge">CSV</span>
            <span class="file-type-badge">MD</span>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Drop your file here",
            type=["pdf", "txt", "docx", "csv", "md"],
            key="file_uploader",
            label_visibility="collapsed"
        )
        
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
        
        if st.button("🧹 Clear All Documents", key="clear_docs_btn", use_container_width=True):
            try:
                if st.session_state.active_collection:
                    col_id = st.session_state.active_collection
                    resp = requests.delete(f"{BACKEND_URL}/api/documents/collections/{col_id}", headers=auth_headers())
                else:
                    resp = requests.delete(f"{BACKEND_URL}/api/documents/clear-default", headers=auth_headers())
                if resp.status_code == 200:
                    st.session_state.upload_status = ("success", "🧹 All documents cleared!")
                    st.rerun()
                else:
                    st.error("Failed to clear")
            except Exception as e:
                st.error(f"Error: {e}")
        
        st.markdown("---")
        st.caption(f"⏱️ Session: {SESSION_DURATION_MINUTES} min")
        st.button("Sign Out", key="logout_btn", use_container_width=True, on_click=logout)

    # ==========================================
    # MAIN CHAT AREA
    # ==========================================
    if st.session_state.active_collection:
        active_col = next((c for c in collections if c["id"] == st.session_state.active_collection), None)
        if active_col:
            chroma_name = f"col_{active_col['id'][:8]}"
            st.caption(f"📚 Chatting with: **{active_col['name']}**")
        else:
            chroma_name = "rag_collection"
    else:
        chroma_name = "rag_collection"
        st.caption("📚 Chatting with: **Default**")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander(f"📎 {len(message['sources'])} Sources"):
                    for source in message["sources"]:
                        score = source['similarity']
                        st.markdown(f"**Relevance:** `{score:.3f}`")
                        st.info(source['text'][:300] + ("..." if len(source['text']) > 300 else ""))

    if prompt := st.chat_input("Ask anything about your documents..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            payload = {"query": prompt, "top_k": 5, "collection_name": chroma_name}
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
                            if data_str == "[DONE]": break
                            try:
                                event = json.loads(data_str)
                                if event["type"] == "text":
                                    full_answer += event["content"]
                                    message_placeholder.markdown(full_answer + " ▌")
                                elif event["type"] == "sources":
                                    sources = event["content"]
                            except json.JSONDecodeError: continue
                    message_placeholder.markdown(full_answer)
                    if sources:
                        with st.expander(f"📎 {len(sources)} Sources"):
                            for source in sources:
                                score = source['similarity']
                                st.markdown(f"**Relevance:** `{score:.3f}`")
                                st.info(source['text'][:300] + ("..." if len(source['text']) > 300 else ""))
                    st.session_state.messages.append({"role": "assistant", "content": full_answer, "sources": sources})
                elif response.status_code == 401:
                    message_placeholder.markdown("⏰ Session expired. Please sign in again.")
                    logout()
                else:
                    message_placeholder.markdown(f"❌ Error: {response.text}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {response.text}"})
            except Exception as e:
                message_placeholder.markdown(f"❌ Connection error: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})

# ==========================================
# APP ROUTER
# ==========================================
if st.session_state.current_page == "landing":
    render_landing_page()
elif st.session_state.current_page == "login":
    render_login_page()
elif st.session_state.current_page == "register":
    render_register_page()
elif st.session_state.current_page == "chat":
    render_chat_page()
