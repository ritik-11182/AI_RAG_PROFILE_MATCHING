"""
app.py
------
Streamlit web app for the RAG Profile Matching System.

Run with:
    streamlit run app.py
"""

import json
import time
import streamlit as st
from pathlib import Path

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Matcher | RAG Profile Matching",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  html, body, [class*="css"] {
      font-family: 'Inter', sans-serif;
  }

  .main { background: #0a0e1a; }

  /* Hero banner */
  .hero-banner {
      background: linear-gradient(135deg, #1a1f36 0%, #0d1117 50%, #1a1f36 100%);
      border: 1px solid rgba(99,102,241,0.3);
      border-radius: 20px;
      padding: 2.5rem 3rem;
      margin-bottom: 2rem;
      text-align: center;
      position: relative;
      overflow: hidden;
  }
  .hero-banner::before {
      content: '';
      position: absolute; inset: 0;
      background: radial-gradient(ellipse at 50% 0%, rgba(99,102,241,0.15) 0%, transparent 70%);
  }
  .hero-title {
      font-size: 2.8rem; font-weight: 800;
      background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #38bdf8 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      margin: 0; line-height: 1.2;
  }
  .hero-sub {
      color: #94a3b8; font-size: 1.05rem; margin-top: 0.6rem;
  }
  .hero-badges { margin-top: 1.2rem; display: flex; gap: 0.6rem; justify-content: center; flex-wrap: wrap; }
  .badge {
      background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.4);
      color: #a5b4fc; border-radius: 999px; padding: 4px 14px; font-size: 0.78rem; font-weight: 500;
  }

  /* Candidate card */
  .cand-card {
      background: linear-gradient(135deg, #141929 0%, #1e2440 100%);
      border: 1px solid rgba(99,102,241,0.25);
      border-radius: 16px; padding: 1.4rem 1.6rem; margin-bottom: 1rem;
      transition: transform 0.2s, border-color 0.2s;
  }
  .cand-card:hover {
      border-color: rgba(129,140,248,0.6);
      transform: translateY(-2px);
  }
  .cand-rank {
      font-size: 0.75rem; font-weight: 600; color: #6366f1; letter-spacing: 0.1em;
      text-transform: uppercase;
  }
  .cand-name { font-size: 1.25rem; font-weight: 700; color: #e2e8f0; margin: 0.2rem 0; }
  .score-pill {
      display: inline-block;
      padding: 4px 16px; border-radius: 999px; font-weight: 700; font-size: 0.9rem;
  }
  .score-high   { background: linear-gradient(135deg,#16a34a,#4ade80); color: #fff; }
  .score-medium { background: linear-gradient(135deg,#d97706,#fbbf24); color: #fff; }
  .score-low    { background: linear-gradient(135deg,#dc2626,#f87171); color: #fff; }

  .skill-tag {
      display: inline-block;
      background: rgba(99,102,241,0.18); border: 1px solid rgba(99,102,241,0.35);
      color: #a5b4fc; border-radius: 6px; padding: 2px 10px;
      font-size: 0.78rem; font-weight: 500; margin: 2px;
  }
  .excerpt-box {
      background: #0d1117; border-left: 3px solid #6366f1;
      border-radius: 0 8px 8px 0; padding: 0.8rem 1rem;
      color: #94a3b8; font-size: 0.83rem; line-height: 1.5;
      margin-top: 0.6rem; font-family: monospace;
  }
  .stat-card {
      background: linear-gradient(135deg, #141929, #1a2140);
      border: 1px solid rgba(99,102,241,0.2); border-radius: 12px;
      padding: 1rem 1.4rem; text-align: center;
  }
  .stat-value { font-size: 2rem; font-weight: 800; color: #818cf8; }
  .stat-label { font-size: 0.78rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
      background: #0d1117;
      border-right: 1px solid rgba(99,102,241,0.2);
  }

  /* Buttons */
  .stButton > button {
      background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
      color: white !important; border: none !important;
      border-radius: 10px !important; font-weight: 600 !important;
      padding: 0.5rem 1.5rem !important;
  }
  .stButton > button:hover {
      background: linear-gradient(135deg, #818cf8, #a78bfa) !important;
      box-shadow: 0 4px 20px rgba(99,102,241,0.4) !important;
  }

  /* Text areas */
  textarea { background: #0d1117 !important; border-color: rgba(99,102,241,0.3) !important; color: #e2e8f0 !important; }
  .stSelectbox select, .stSlider { color: #e2e8f0 !important; }

  div[data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #818cf8 !important; }
</style>
""", unsafe_allow_html=True)


# ─── Cache the matcher (singleton) ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_matcher():
    from job_matcher import JobMatcher
    return JobMatcher()


def load_jd_files():
    """Load available job descriptions from job_descriptions/ folder."""
    jd_dir = Path("./job_descriptions")
    if not jd_dir.exists():
        return {}
    return {f.stem.replace("_", " ").title(): f.read_text(encoding="utf-8") for f in sorted(jd_dir.glob("*.txt"))}


def score_class(score):
    if score >= 70:
        return "score-high"
    elif score >= 45:
        return "score-medium"
    return "score-low"


def render_candidate_card(rank, match):
    name = match.get("candidate_name", "Unknown")
    score = match.get("match_score", 0)
    skills = match.get("matched_skills", [])
    excerpts = match.get("relevant_excerpts", [])
    reasoning = match.get("reasoning", "")
    sections = match.get("sections_matched", [])
    exp = match.get("years_experience", 0)
    edu = match.get("education_summary", "")

    skill_tags = " ".join(f'<span class="skill-tag">{s}</span>' for s in skills[:10])
    sc = score_class(score)
    excerpt_html = ""
    if excerpts:
        excerpt_html = f'<div class="excerpt-box">📄 {excerpts[0][:250]}...</div>'

    st.markdown(f"""
    <div class="cand-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div>
            <div class="cand-rank">#{rank} Match</div>
            <div class="cand-name">{name}</div>
            <div style="color:#64748b; font-size:0.82rem; margin-top:2px;">
              🎓 {edu[:80] if edu and edu != 'Not specified' else 'Education N/A'} &nbsp;|&nbsp;
              💼 {exp} yrs experience &nbsp;|&nbsp;
              📁 Sections: {', '.join(sections)}
            </div>
          </div>
          <div style="text-align:right;">
            <span class="score-pill {sc}">{score}/100</span>
          </div>
        </div>
        <div style="margin-top:0.8rem;">{skill_tags}</div>
        {excerpt_html}
        <details style="margin-top:0.6rem;">
          <summary style="color:#6366f1; font-size:0.82rem; cursor:pointer;">🔍 View Reasoning</summary>
          <p style="color:#94a3b8; font-size:0.82rem; margin-top:0.4rem; line-height:1.6;">{reasoning}</p>
        </details>
    </div>
    """, unsafe_allow_html=True)


# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    top_k = st.slider("Top-K Candidates", 3, 20, 10)
    min_exp = st.number_input("Min Experience (years, 0=auto)", 0, 25, 0)
    sem_w = st.slider("Semantic Weight", 0.1, 0.9, 0.6, 0.05)
    kw_w = round(1 - sem_w, 2)
    st.info(f"Keyword Weight: {kw_w}")

    st.markdown("---")
    st.markdown("### 🗄️ Vector Store")
    if st.button("🔄 Force Re-Index"):
        with st.spinner("Re-indexing resumes..."):
            matcher = get_matcher()
            matcher.rag.index_resumes(force_reindex=True)
        st.success("Re-indexing complete!")

    if st.button("📊 Show Stats"):
        matcher = get_matcher()
        stats = matcher.rag.get_store_stats()
        st.json(stats)

    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown("""
**RAG Profile Matching** uses:
- 🔍 Semantic search (sentence-transformers)
- 🔑 Keyword hybrid matching
- 📊 ChromaDB vector store
- 🧩 Section-aware chunking
    """)


# ─── Main Layout ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <div class="hero-title">🧠 AI Resume Matcher</div>
  <div class="hero-sub">RAG-powered semantic profile matching engine</div>
  <div class="hero-badges">
    <span class="badge">🔍 Semantic Search</span>
    <span class="badge">🔑 Keyword Hybrid</span>
    <span class="badge">📦 ChromaDB</span>
    <span class="badge">🤗 sentence-transformers</span>
    <span class="badge">⚡ Real-time Scoring</span>
  </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🎯 Match Candidates", "📋 Job Descriptions", "📊 Analytics"])

# ─── Tab 1: Match ──────────────────────────────────────────────────────────────
with tab1:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("#### 📝 Job Description Input")
        input_mode = st.radio("Input Mode", ["📂 Load from file", "✏️ Type manually"], horizontal=True)

        jd_text = ""
        if input_mode == "📂 Load from file":
            jds = load_jd_files()
            if jds:
                selected = st.selectbox("Select a Job Description", list(jds.keys()))
                jd_text = jds[selected]
                st.text_area("Preview", value=jd_text[:600] + "...", height=260, disabled=True)
            else:
                st.warning("No JDs found in `job_descriptions/`.")
        else:
            jd_text = st.text_area(
                "Paste or type the Job Description",
                height=300,
                placeholder="We are looking for a Senior ML Engineer with 5+ years of experience in Python, PyTorch...",
            )

        run_btn = st.button("🚀 Find Matching Candidates", use_container_width=True)

    with col_right:
        st.markdown("#### 📈 Match Results")
        if run_btn and jd_text.strip():
            with st.spinner("🔍 Retrieving and ranking candidates..."):
                t0 = time.time()
                matcher = get_matcher()
                result = matcher.match(
                    jd_text,
                    top_k=top_k,
                    min_experience=min_exp if min_exp > 0 else None,
                    auto_detect_exp=(min_exp == 0),
                    semantic_weight=sem_w,
                    keyword_weight=kw_w,
                )
            elapsed = round((time.time() - t0) * 1000)

            # Stats row
            top_matches = result.get("top_matches", [])
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Candidates Found", result.get("total_candidates_evaluated", 0))
            c2.metric("Top Score", f"{top_matches[0]['match_score']}/100" if top_matches else "N/A")
            c3.metric("Latency", f"{result.get('retrieval_latency_ms', elapsed)}ms")
            c4.metric("JD Skills", len(result.get("jd_skills", [])))

            if result.get("jd_skills"):
                st.markdown(
                    "**Detected Skills:** " +
                    " ".join(f'<span class="skill-tag">{s}</span>' for s in result["jd_skills"]),
                    unsafe_allow_html=True,
                )

            if top_matches:
                st.markdown(f"---\n**Top {len(top_matches)} Candidates:**")
                for i, match in enumerate(top_matches, 1):
                    render_candidate_card(i, match)

                # Download JSON
                st.download_button(
                    "⬇️ Download Full Results (JSON)",
                    data=json.dumps(result, indent=2, default=str),
                    file_name="match_results.json",
                    mime="application/json",
                )
            else:
                st.info("No candidates found. Try re-indexing resumes first.")
        elif run_btn:
            st.warning("Please enter a job description.")

# ─── Tab 2: JD Library ─────────────────────────────────────────────────────────
with tab2:
    st.markdown("#### 📋 Available Job Descriptions")
    jds = load_jd_files()
    if jds:
        for title, content in jds.items():
            with st.expander(f"📄 {title}"):
                st.text(content)
    else:
        st.info("No job descriptions found. Add `.txt` files to `job_descriptions/`.")

# ─── Tab 3: Analytics ─────────────────────────────────────────────────────────
with tab3:
    st.markdown("#### 📊 System Analytics")
    matcher = get_matcher()
    stats = matcher.rag.get_store_stats()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Vectors", stats.get("total_chunks", 0))
    c2.metric("Collection", stats.get("collection_name", "N/A"))
    c3.metric("Embedding Model", stats.get("embedding_model", "N/A"))

    st.markdown("---")
    st.markdown("#### 🔍 Test Retrieval")
    test_query = st.text_input("Enter a test query", "Python machine learning engineer NLP")
    if st.button("Run Retrieval Test"):
        with st.spinner("Retrieving..."):
            results = matcher.rag.retrieve(test_query, top_k=5)
        if results:
            import pandas as pd
            df = pd.DataFrame([{
                "Candidate": r["metadata"].get("candidate_name"),
                "Section": r.get("section"),
                "Score": r["similarity"],
                "Exp Yrs": r["metadata"].get("years_experience"),
                "Skills": r["metadata"].get("skills_str", "")[:60],
            } for r in results])
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No results. Try re-indexing resumes.")
