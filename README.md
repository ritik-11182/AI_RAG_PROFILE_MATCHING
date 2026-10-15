# AI RAG Profile Matching System

> AirTribe Assignment – Milestone 2: RAG-based Semantic Resume Matching

A production-ready **RAG (Retrieval-Augmented Generation)** pipeline that semantically matches job descriptions against a corpus of resumes using vector embeddings, ChromaDB, and hybrid keyword scoring.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Resumes (if not already done)
```bash
python generate_resumes.py
```

### 3. Index Resumes into Vector DB
```bash
python resume_rag.py --index
# Force re-index:
python resume_rag.py --index --force
```

### 4. Run Job Matching
```bash
# Demo mode (ML Engineer JD)
python job_matcher.py

# Match against a JD file
python job_matcher.py --jd job_descriptions/ml_engineer.txt --top-k 10

# Match all JDs in job_descriptions/
python job_matcher.py --all-jds

# Match with inline text
python job_matcher.py --query "Senior Python developer with AWS and Kubernetes 5 years"
```

### 5. Launch Streamlit UI
```bash
streamlit run app.py
```

### 6. Run the Jupyter Notebook
```bash
jupyter notebook RAG_Profile_Matching.ipynb
```

---

## 📁 Project Structure

```
AI_RAG_Profile_Matching/
├── resume_rag.py           # Part A: RAG indexing pipeline
├── job_matcher.py          # Part B: Job matching engine
├── generate_resumes.py     # Generates 45+ synthetic resumes as PDFs
├── app.py                  # Streamlit web UI
├── RAG_Profile_Matching.ipynb  # Jupyter notebook (analysis + metrics)
├── requirements.txt
├── .env                    # Configuration (API keys, paths)
├── resumes/                # 45 resume PDFs + TXTs
├── job_descriptions/       # 7 job description text files
│   ├── ml_engineer.txt
│   ├── data_engineer.txt
│   ├── fullstack_engineer.txt
│   ├── devops_engineer.txt
│   ├── nlp_engineer.txt
│   ├── data_scientist.txt
│   └── security_engineer.txt
└── chroma_db/              # ChromaDB vector store (auto-created)
```

---

## 🏗️ Architecture

```
Job Description Input
        │
        ▼
┌─────────────────┐    ┌──────────────────────┐
│  JD Embedding   │    │   Keyword Extractor   │
│ (sentence-trans)│    │ (skills, exp years)   │
└────────┬────────┘    └──────────┬────────────┘
         │                        │
         ▼                        │
┌─────────────────┐               │
│  ChromaDB Query │               │
│  (cosine sim)   │               │
└────────┬────────┘               │
         │                        │
         ▼                        ▼
┌──────────────────────────────────────┐
│         Candidate Aggregation        │
│   (group chunks by candidate name)   │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│         Hybrid Scoring (0-100)       │
│  60% semantic + 40% keyword overlap  │
│  + section diversity bonus           │
│  - experience shortfall penalty      │
└──────────────────┬───────────────────┘
                   │
                   ▼
           Ranked Top-K Output
```

---

## 📊 Output Format

```json
{
  "job_description": "Senior ML Engineer...",
  "jd_skills": ["Python", "PyTorch", "MLflow", ...],
  "min_experience_required": 5,
  "top_matches": [
    {
      "candidate_name": "Alice Chen",
      "resume_path": "resumes/alice_chen.pdf",
      "match_score": 92,
      "matched_skills": ["Python", "PyTorch", "MLflow", "Kubeflow", "BERT"],
      "relevant_excerpts": ["Built production ML pipeline serving 50M users..."],
      "reasoning": "Semantic similarity: 0.89 across sections [experience, skills]. Keyword match: 12/15 required skills. Experience: 7 years.",
      "sections_matched": ["experience", "skills", "education"],
      "years_experience": 7
    }
  ],
  "retrieval_latency_ms": 312,
  "total_candidates_evaluated": 45
}
```

---

## 🔧 Configuration (.env)

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `huggingface` | `huggingface` or `openai` |
| `HF_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace model name |
| `CHROMA_DB_PATH` | `./chroma_db` | ChromaDB persistence directory |
| `RESUMES_DIR` | `./resumes` | Directory containing resume PDFs/TXTs |
| `JD_DIR` | `./job_descriptions` | Directory containing JD .txt files |
| `TOP_K` | `10` | Default top-K results |

---

## 📈 Performance

| Metric | Value |
|---|---|
| Resumes indexed | 45 |
| Total vector chunks | 238 |
| Avg indexing time | ~10s for 45 resumes |
| Avg query latency | < 500ms |
| Embedding model | `all-MiniLM-L6-v2` (384-dim) |
| Vector DB | ChromaDB (cosine similarity) |

---

## 🧠 Technical Details

### Part A: RAG System (resume_rag.py)
- **Document loading**: PDF + TXT support
- **Section-aware chunking**: Splits resumes by section (Summary, Skills, Experience, Education, Projects, Certifications)
- **Metadata extraction**: Name, skills list, years of experience, education summary
- **Embedding**: `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace)
- **Vector store**: ChromaDB with cosine similarity index

### Part B: Job Matching (job_matcher.py)
- **Semantic search**: JD → embedding → nearest-neighbor retrieval
- **Hybrid scoring**: 60% semantic similarity + 40% keyword overlap
- **Section diversity bonus**: Extra score for matching multiple resume sections
- **Experience penalty**: 15-point deduction if below minimum requirement
- **Candidate aggregation**: De-duplicates chunks into single candidate scores

---

## 📹 Demo

Run `streamlit run app.py` for the interactive web UI with:
- Job description input (file or manual)
- Real-time candidate ranking with scores
- Skill tag visualization
- Relevant excerpt display
- JSON export
