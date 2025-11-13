# # frontend/app.py

# import streamlit as st
# import requests

# st.set_page_config(page_title="Finance Audit RAG", layout="centered")
# st.title("📊 Finance Audit RAG Chat")

# # Input text box
# query = st.text_input("Ask a question about SOX / SEC filings:")

# # Backend URL (adjust if running on a different host/port)
# API_URL = "http://127.0.0.1:8000/query/"

# if st.button("Submit") and query:
#     with st.spinner("Fetching answer..."):
#         try:
#             response = requests.post(
#                 API_URL,
#                 json={"query": query},
#                 headers={"Content-Type": "application/json"}
#             )
#             if response.status_code == 200:
#                 answer = response.json().get("response", "No answer returned.")
#                 st.success(answer)
#             else:
#                 st.error(f"Error {response.status_code}: {response.text}")
#         except Exception as e:
#             st.error(f"Failed to connect to backend: {e}")

# # Optional: display a footer
# st.markdown("---")
# st.markdown("💡 This app queries the RAG pipeline via your FastAPI backend.")


# # frontend/app.py
# """
# Finance Audit RAG - Clean, Bright, No-Scroll Interface
# Pastel gradient with excellent readability
# """

# import streamlit as st
# import requests
# import time
# from datetime import datetime

# # ========================================
# # 🎨 PAGE CONFIGURATION
# # ========================================
# st.set_page_config(
#     page_title="Finance Audit RAG Pro",
#     page_icon="📊",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ========================================
# # 🎭 CUSTOM CSS - BRIGHT PASTEL GRADIENT
# # ========================================
# st.markdown("""
# <style>
#     /* BRIGHT Pastel Gradient - VERY SLOW animation */
#     .stApp {
#         background: linear-gradient(
#             135deg, 
#             #FFE5B4 0%,   /* Peach */
#             #FFDAB9 25%,  /* Light Orange */
#             #FFF8DC 50%,  /* Cream */
#             #E0FFE0 75%,  /* Mint Green */
#             #FFFACD 100%  /* Lemon Yellow */
#         );
#         background-size: 400% 400%;
#         animation: slowGradient 45s ease infinite;
#         min-height: 100vh;
#         overflow: hidden !important;
#     }
    
#     @keyframes slowGradient {
#         0% { background-position: 0% 50%; }
#         50% { background-position: 100% 50%; }
#         100% { background-position: 0% 50%; }
#     }
    
#     /* Remove ALL padding to maximize space */
#     .block-container {
#         padding-top: 1rem !important;
#         padding-bottom: 0.5rem !important;
#         padding-left: 1rem !important;
#         padding-right: 1rem !important;
#         max-width: 100% !important;
#         max-height: 100vh;
#         overflow: hidden !important;
#     }
    
#     /* Hide scrollbars completely */
#     .main, .stApp, [data-testid="stAppViewContainer"] {
#         overflow: hidden !important;
#         max-height: 100vh;
#     }
    
#     /* Main Title */
#     .main-title {
#         font-size: 2.5rem;
#         font-weight: 900;
#         color: #2C3E50;
#         text-align: center;
#         margin: 0 0 5px 0;
#         text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.8);
#     }
    
#     /* Subtitle */
#     .subtitle {
#         text-align: center;
#         color: #34495E;
#         font-size: 1rem;
#         margin: 0 0 15px 0;
#         font-weight: 600;
#     }
    
#     /* Input Box - CRYSTAL CLEAR */
#     .stTextInput input {
#         background: white !important;
#         border: 3px solid #FF6B6B !important;
#         border-radius: 12px !important;
#         color: #2C3E50 !important;
#         font-size: 1.2rem !important;
#         padding: 12px 15px !important;
#         font-weight: 600 !important;
#         height: 50px !important;
#     }
    
#     .stTextInput input::placeholder {
#         color: #7F8C8D !important;
#         font-weight: 500 !important;
#     }
    
#     .stTextInput input:focus {
#         border-color: #FF8C42 !important;
#         box-shadow: 0 0 15px rgba(255, 140, 66, 0.4) !important;
#     }
    
#     /* Label styling */
#     .stTextInput label {
#         color: #2C3E50 !important;
#         font-size: 1.1rem !important;
#         font-weight: 700 !important;
#         margin-bottom: 8px !important;
#     }
    
#     /* Button - BRIGHT and CLEAR */
#     .stButton button {
#         background: linear-gradient(135deg, #FF6B6B 0%, #FF8C42 100%) !important;
#         color: white !important;
#         border: none !important;
#         border-radius: 12px !important;
#         padding: 12px 30px !important;
#         font-size: 1.1rem !important;
#         font-weight: 700 !important;
#         height: 50px !important;
#         transition: all 0.3s ease !important;
#         box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3) !important;
#         text-transform: uppercase;
#         letter-spacing: 1px;
#     }
    
#     .stButton button:hover {
#         transform: translateY(-2px) !important;
#         box-shadow: 0 6px 20px rgba(255, 140, 66, 0.5) !important;
#     }
    
#     /* Success Box - WHITE BACKGROUND */
#     .stSuccess {
#         background: white !important;
#         border: 3px solid #2ECC71 !important;
#         border-radius: 12px !important;
#         padding: 20px !important;
#         color: #2C3E50 !important;
#         font-size: 1.05rem !important;
#         font-weight: 500 !important;
#         line-height: 1.6 !important;
#     }
    
#     /* Error Box */
#     .stError {
#         background: white !important;
#         border: 3px solid #E74C3C !important;
#         border-radius: 12px !important;
#         padding: 15px !important;
#         color: #2C3E50 !important;
#         font-weight: 600 !important;
#     }
    
#     /* Sidebar */
#     [data-testid="stSidebar"] {
#         background: rgba(255, 255, 255, 0.7) !important;
#         backdrop-filter: blur(10px) !important;
#         border-right: 3px solid #FF6B6B !important;
#     }
    
#     [data-testid="stSidebar"] h3 {
#         color: #2C3E50 !important;
#         font-weight: 800 !important;
#     }
    
#     [data-testid="stSidebar"] * {
#         color: #2C3E50 !important;
#     }
    
#     /* Metric styling */
#     [data-testid="stMetricValue"] {
#         color: #2C3E50 !important;
#         font-size: 2rem !important;
#         font-weight: 900 !important;
#     }
    
#     [data-testid="stMetricLabel"] {
#         color: #34495E !important;
#         font-weight: 700 !important;
#     }
    
#     /* Stat Badge */
#     .stat-badge {
#         display: inline-block;
#         background: linear-gradient(135deg, #FF6B6B 0%, #FF8C42 100%);
#         color: white;
#         padding: 6px 14px;
#         border-radius: 20px;
#         font-weight: 700;
#         margin: 3px;
#         font-size: 0.9rem;
#         box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
#     }
    
#     /* Expander */
#     .streamlit-expanderHeader {
#         background: white !important;
#         border: 2px solid #FF8C42 !important;
#         border-radius: 10px !important;
#         font-weight: 700 !important;
#         color: #2C3E50 !important;
#         padding: 10px !important;
#     }
    
#     .streamlit-expanderContent {
#         background: white !important;
#         border: 2px solid #FFE5B4 !important;
#         border-top: none !important;
#         border-radius: 0 0 10px 10px !important;
#         color: #2C3E50 !important;
#     }
    
#     /* Column spacing */
#     [data-testid="column"] {
#         padding: 0 10px !important;
#     }
    
#     /* Remove extra margins */
#     .element-container {
#         margin-bottom: 8px !important;
#     }
    
#     h3 {
#         margin-top: 5px !important;
#         margin-bottom: 10px !important;
#         color: #2C3E50 !important;
#     }
# </style>
# """, unsafe_allow_html=True)

# # ========================================
# # 💾 SESSION STATE
# # ========================================
# if 'query_history' not in st.session_state:
#     st.session_state.query_history = []
# if 'total_queries' not in st.session_state:
#     st.session_state.total_queries = 0
# if 'cache_hits' not in st.session_state:
#     st.session_state.cache_hits = 0

# # ========================================
# # 🔧 BACKEND CONFIG
# # ========================================
# API_URL = "http://127.0.0.1:8000/query/"
# CACHE_STATS_URL = "http://127.0.0.1:8000/query/cache/stats"

# # ========================================
# # 📊 SIDEBAR - MINIMAL
# # ========================================
# with st.sidebar:
#     st.markdown("### ⚙️ Stats")
    
#     try:
#         cache_response = requests.get(CACHE_STATS_URL, timeout=2)
#         if cache_response.status_code == 200:
#             cache_data = cache_response.json()
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.metric("Cached", cache_data.get('total_cached_queries', 0))
#             with col2:
#                 st.metric("Total", st.session_state.total_queries)
#     except:
#         st.metric("Queries", st.session_state.total_queries)
    
#     if st.session_state.total_queries > 0:
#         hit_rate = (st.session_state.cache_hits / st.session_state.total_queries) * 100
#         st.metric("Hit Rate", f"{hit_rate:.0f}%")
    
#     st.markdown("---")
#     st.markdown("### 💡 Quick Try")
    
#     if st.button("Section 302", use_container_width=True):
#         st.session_state.sample_query = "Explain Section 302 compliance"
#     if st.button("SOX 404", use_container_width=True):
#         st.session_state.sample_query = "What are SOX 404 requirements"
#     if st.button("SEC Rules", use_container_width=True):
#         st.session_state.sample_query = "SEC filing disclosure rules"

# # ========================================
# # 🎯 MAIN INTERFACE - ONE PAGE ONLY
# # ========================================

# st.markdown('<h1 class="main-title">📊 Finance Audit RAG Pro</h1>', unsafe_allow_html=True)
# st.markdown('<p class="subtitle">Intelligent SOX & SEC Compliance Assistant</p>', unsafe_allow_html=True)

# # Single row layout
# main_col, recent_col = st.columns([2, 1])

# with main_col:
#     # Query Input
#     default_query = st.session_state.get('sample_query', '')
#     if default_query:
#         query = st.text_input(
#             "Ask your question:",
#             value=default_query,
#             placeholder="e.g., What are Section 302 requirements?"
#         )
#         st.session_state.sample_query = ''
#     else:
#         query = st.text_input(
#             "Ask your question:",
#             placeholder="e.g., What are Section 302 requirements?"
#         )
    
#     submit_btn = st.button("🚀 Get Answer", use_container_width=True)
    
#     # Response Area (always visible, no scrolling)
#     if submit_btn and query:
#         start_time = time.time()
        
#         try:
#             response = requests.post(
#                 API_URL,
#                 json={"query": query},
#                 headers={"Content-Type": "application/json"},
#                 timeout=30
#             )
            
#             elapsed_time = time.time() - start_time
            
#             if response.status_code == 200:
#                 result = response.json()
#                 answer = result.get("response", "No answer returned.")
#                 is_cached = result.get("cached", False)
                
#                 st.session_state.total_queries += 1
#                 if is_cached:
#                     st.session_state.cache_hits += 1
                
#                 st.session_state.query_history.insert(0, {
#                     'query': query,
#                     'answer': answer,
#                     'cached': is_cached,
#                     'time': elapsed_time
#                 })
                
#                 # Force refresh to show updated stats
#                 st.rerun()
                
#             else:
#                 st.error(f"Error: {response.text}")
                
#         except Exception as e:
#             st.error(f"Connection failed: {str(e)}")
    
#     elif st.session_state.query_history:
#         # Show last answer if exists
#         last = st.session_state.query_history[0]
#         if last['cached']:
#             st.markdown('<span class="stat-badge">⚡ CACHED</span>', unsafe_allow_html=True)
#         else:
#             st.markdown('<span class="stat-badge">🆕 FRESH</span>', unsafe_allow_html=True)
#         st.markdown(f'<span class="stat-badge">⏱️ {last["time"]:.2f}s</span>', unsafe_allow_html=True)
#         st.success(last['answer'])

# with recent_col:
#     st.markdown("### 📜 Recent")
    
#     # Add scrollable container with fixed height
#     st.markdown("""
#         <style>
#         /* Make only the recent column scrollable */
#         [data-testid="column"]:last-child {
#             max-height: 70vh;
#             overflow-y: auto !important;
#             overflow-x: hidden;
#         }
        
#         /* Custom scrollbar for recent column */
#         [data-testid="column"]:last-child::-webkit-scrollbar {
#             width: 8px;
#             display: block !important;
#         }
        
#         [data-testid="column"]:last-child::-webkit-scrollbar-track {
#             background: rgba(255, 255, 255, 0.3);
#             border-radius: 10px;
#         }
        
#         [data-testid="column"]:last-child::-webkit-scrollbar-thumb {
#             background: #FF6B6B;
#             border-radius: 10px;
#         }
        
#         [data-testid="column"]:last-child::-webkit-scrollbar-thumb:hover {
#             background: #FF8C42;
#         }
#         </style>
#     """, unsafe_allow_html=True)
    
#     if st.session_state.query_history:
#         for idx, item in enumerate(st.session_state.query_history[:10]):  # Show up to 10
#             with st.expander(f"Q: {item['query'][:25]}...", expanded=False):
#                 st.markdown(f"**{item['query']}**")
#                 st.markdown(f"{item['answer']}")
#                 st.markdown(f"⏱️ {item['time']:.2f}s | {'⚡ Cached' if item['cached'] else '🆕 Fresh'}")
#     else:
#         st.info("No queries yet!")


"""
Finance Audit RAG - Professional, Mature Interface
Clean, corporate design with excellent readability
"""

import streamlit as st
import requests
import time
from datetime import datetime

# ========================================
# 🎨 PAGE CONFIGURATION
# ========================================
st.set_page_config(
    page_title="Finance Audit RAG Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# 🎭 CUSTOM CSS - PROFESSIONAL DESIGN
# ========================================
st.markdown("""
<style>
    /* Professional gradient background */
    .stApp {
        background: linear-gradient(
            135deg, 
            #f8f9fa 0%,
            #e9ecef 50%,
            #dee2e6 100%
        );
        min-height: 100vh;
    }
    
    /* Remove excessive padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }
    
    /* Main Title - Professional */
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a1a;
        text-align: center;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.5px;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #495057;
        font-size: 1rem;
        margin: 0 0 2rem 0;
        font-weight: 400;
    }
    
    /* Input Box - Professional */
    .stTextInput input {
        background: white !important;
        border: 1px solid #ced4da !important;
        border-radius: 4px !important;
        color: #212529 !important;
        font-size: 1rem !important;
        padding: 0.75rem 1rem !important;
        font-weight: 400 !important;
        transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out !important;
    }
    
    .stTextInput input::placeholder {
        color: #6c757d !important;
        font-weight: 400 !important;
    }
    
    .stTextInput input:focus {
        border-color: #0d6efd !important;
        box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25) !important;
        outline: 0 !important;
    }
    
    /* Label styling */
    .stTextInput label {
        color: #212529 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Button - Professional */
    .stButton button {
        background: #0d6efd !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        transition: all 0.15s ease-in-out !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12) !important;
    }
    
    .stButton button:hover {
        background: #0b5ed7 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Success Box - Professional with scrolling */
    .stSuccess {
        background: white !important;
        border-left: 4px solid #198754 !important;
        border-radius: 4px !important;
        padding: 1.25rem !important;
        color: #212529 !important;
        font-size: 0.95rem !important;
        font-weight: 400 !important;
        line-height: 1.6 !important;
        max-height: 400px !important;
        overflow-y: auto !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Custom scrollbar for success box */
    .stSuccess::-webkit-scrollbar {
        width: 8px;
    }
    
    .stSuccess::-webkit-scrollbar-track {
        background: #f8f9fa;
        border-radius: 4px;
    }
    
    .stSuccess::-webkit-scrollbar-thumb {
        background: #ced4da;
        border-radius: 4px;
    }
    
    .stSuccess::-webkit-scrollbar-thumb:hover {
        background: #adb5bd;
    }
    
    /* Error Box */
    .stError {
        background: white !important;
        border-left: 4px solid #dc3545 !important;
        border-radius: 4px !important;
        padding: 1rem !important;
        color: #212529 !important;
        font-weight: 400 !important;
    }
    
    /* Sidebar - Professional */
    [data-testid="stSidebar"] {
        background: white !important;
        border-right: 1px solid #dee2e6 !important;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #212529 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #212529 !important;
    }
    
    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton button {
        background: white !important;
        color: #0d6efd !important;
        border: 1px solid #0d6efd !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: #0d6efd !important;
        color: white !important;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #212529 !important;
        font-size: 1.75rem !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #6c757d !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Stat Badge - Professional */
    .stat-badge {
        display: inline-block;
        background: white;
        color: #495057;
        padding: 0.35rem 0.75rem;
        border-radius: 4px;
        font-weight: 500;
        margin: 0.25rem;
        font-size: 0.875rem;
        border: 1px solid #dee2e6;
    }
    
    .stat-badge.cached {
        background: #d1ecf1;
        color: #0c5460;
        border-color: #bee5eb;
    }
    
    .stat-badge.fresh {
        background: #d4edda;
        color: #155724;
        border-color: #c3e6cb;
    }
    
    /* Expander - Professional */
    .streamlit-expanderHeader {
        background: white !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 4px !important;
        font-weight: 500 !important;
        color: #212529 !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.9rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: #f8f9fa !important;
    }
    
    .streamlit-expanderContent {
        background: white !important;
        border: 1px solid #dee2e6 !important;
        border-top: none !important;
        border-radius: 0 0 4px 4px !important;
        color: #212529 !important;
        padding: 1rem !important;
    }
    
    /* Recent queries section with scrolling */
    .recent-container {
        max-height: 600px;
        overflow-y: auto;
        overflow-x: hidden;
        padding-right: 0.5rem;
    }
    
    /* Custom scrollbar for recent queries */
    .recent-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .recent-container::-webkit-scrollbar-track {
        background: #f8f9fa;
        border-radius: 4px;
    }
    
    .recent-container::-webkit-scrollbar-thumb {
        background: #ced4da;
        border-radius: 4px;
    }
    
    .recent-container::-webkit-scrollbar-thumb:hover {
        background: #adb5bd;
    }
    
    /* Column spacing */
    [data-testid="column"] {
        padding: 0 0.75rem !important;
    }
    
    /* Section headers */
    h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 1rem !important;
        color: #212529 !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
    }
    
    /* Divider */
    hr {
        margin: 1.5rem 0 !important;
        border-color: #dee2e6 !important;
    }
    
    /* Info box */
    .stInfo {
        background: #e7f3ff !important;
        border-left: 4px solid #0d6efd !important;
        border-radius: 4px !important;
        padding: 1rem !important;
        color: #212529 !important;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# 💾 SESSION STATE
# ========================================
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0
if 'cache_hits' not in st.session_state:
    st.session_state.cache_hits = 0

# ========================================
# 🔧 BACKEND CONFIG
# ========================================
API_URL = "http://127.0.0.1:8000/query/"
CACHE_STATS_URL = "http://127.0.0.1:8000/query/cache/stats"

# ========================================
# 📊 SIDEBAR
# ========================================
with st.sidebar:
    st.markdown("### ⚙️ System Statistics")
    
    try:
        cache_response = requests.get(CACHE_STATS_URL, timeout=2)
        if cache_response.status_code == 200:
            cache_data = cache_response.json()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Cached", cache_data.get('total_cached_queries', 0))
            with col2:
                st.metric("Total", st.session_state.total_queries)
    except:
        st.metric("Total Queries", st.session_state.total_queries)
    
    if st.session_state.total_queries > 0:
        hit_rate = (st.session_state.cache_hits / st.session_state.total_queries) * 100
        st.metric("Cache Hit Rate", f"{hit_rate:.1f}%")
    
    st.markdown("---")
    # st.markdown("### 💡 Quick Examples")
    
    # if st.button("Section 302 Compliance", use_container_width=True):
    #     st.session_state.sample_query = "Explain Section 302 compliance requirements"
    # if st.button("SOX 404 Internal Controls", use_container_width=True):
    #     st.session_state.sample_query = "What are SOX 404 requirements"
    # if st.button("SEC Disclosure Rules", use_container_width=True):
    #     st.session_state.sample_query = "SEC filing disclosure rules"

# ========================================
# 🎯 MAIN INTERFACE
# ========================================

st.markdown('<h1 class="main-title">📊 Finance Audit RAG Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Intelligent SOX & SEC Compliance Assistant</p>', unsafe_allow_html=True)

# Two column layout
main_col, recent_col = st.columns([2, 1])

with main_col:
    # Query Input
    default_query = st.session_state.get('sample_query', '')
    if default_query:
        query = st.text_input(
            "Enter your compliance question:",
            value=default_query,
            placeholder="e.g., What are the key differences between Section 404 and Section 302?"
        )
        st.session_state.sample_query = ''
    else:
        query = st.text_input(
            "Enter your compliance question:",
            placeholder="e.g., What are the key differences between Section 404 and Section 302?"
        )
    
    submit_btn = st.button("Get Answer", use_container_width=True)
    
    # Response Area
    if submit_btn and query:
        start_time = time.time()
        
        try:
            response = requests.post(
                API_URL,
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "No answer returned.")
                is_cached = result.get("cached", False)
                
                st.session_state.total_queries += 1
                if is_cached:
                    st.session_state.cache_hits += 1
                
                st.session_state.query_history.insert(0, {
                    'query': query,
                    'answer': answer,
                    'cached': is_cached,
                    'time': elapsed_time
                })
                
                # Force refresh to show updated stats
                st.rerun()
                
            else:
                st.error(f"API Error: {response.text}")
                
        except Exception as e:
            st.error(f"Connection Error: {str(e)}")
    
    elif st.session_state.query_history:
        # Show last answer if exists
        last = st.session_state.query_history[0]
        
        # Status badges
        if last['cached']:
            st.markdown('<span class="stat-badge cached">Cached Response</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="stat-badge fresh">Fresh Response</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="stat-badge">Response Time: {last["time"]:.2f}s</span>', unsafe_allow_html=True)
        
        # Answer box with scrolling enabled
        st.success(last['answer'])

with recent_col:
    st.markdown("### 📋 Recent Queries")
    
    if st.session_state.query_history:
        # Create scrollable container
        st.markdown('<div class="recent-container">', unsafe_allow_html=True)
        
        for idx, item in enumerate(st.session_state.query_history[:15]):
            # Truncate query for display
            display_query = item['query'][:40] + "..." if len(item['query']) > 40 else item['query']
            
            with st.expander(f"{idx + 1}. {display_query}", expanded=False):
                st.markdown(f"**Query:** {item['query']}")
                st.markdown("---")
                st.markdown(f"**Answer:** {item['answer'][:200]}..." if len(item['answer']) > 200 else f"**Answer:** {item['answer']}")
                st.markdown("---")
                status = "Cached" if item['cached'] else "Fresh"
                st.markdown(f"⏱️ {item['time']:.2f}s | {status}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No queries yet. Start by asking a question!")
