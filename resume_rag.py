"""
resume_rag.py
-------------
Part A: RAG System Setup

Implements:
  - Document Processing Pipeline: load, chunk, embed, store in ChromaDB
  - Metadata Extraction: name, skills, experience years, education
  - Section-aware chunking that preserves Education, Experience, Skills sections
"""

import os
import re
import json
import time
import hashlib
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

import PyPDF2
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

load_dotenv()

# ─── Configuration ────────────────────────────────────────────────────────────
RESUMES_DIR = Path(os.getenv("RESUMES_DIR", "./resumes"))
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = "resume_chunks"
EMBEDDING_MODEL_NAME = os.getenv("HF_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_OVERLAP = 50  # words

# Section headers to detect for structured chunking
SECTION_PATTERNS = {
    "summary": r"(?i)(professional\s+summary|summary|objective|profile|about me)",
    "skills": r"(?i)(skills?|technical\s+skills?|core\s+competencies|technologies)",
    "experience": r"(?i)(professional\s+experience|work\s+experience|experience|employment\s+history)",
    "education": r"(?i)(education|academic\s+background|qualifications)",
    "certifications": r"(?i)(certifications?|licenses?|credentials?)",
    "projects": r"(?i)(projects?|side\s+projects?|personal\s+projects?)",
}


# ─── 1. Document Loading ───────────────────────────────────────────────────────

def load_pdf_text(pdf_path: Path) -> str:
    """Extract full text from a PDF file."""
    text_parts = []
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text.strip())
    except Exception as e:
        print(f"  [WARN] Could not read {pdf_path.name}: {e}")
        return ""
    return "\n".join(text_parts)


def load_txt_text(txt_path: Path) -> str:
    """Read plain-text resume file."""
    try:
        return txt_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  [WARN] Could not read {txt_path.name}: {e}")
        return ""


def load_all_resumes(resumes_dir: Path = RESUMES_DIR) -> list[dict]:
    """Load all PDF and TXT resumes from a directory.

    Returns:
        List of dicts with keys: path, filename, text
    """
    resumes = []
    all_files = sorted(list(resumes_dir.glob("*.pdf")) + list(resumes_dir.glob("*.txt")))
    if not all_files:
        raise FileNotFoundError(
            f"No PDF/TXT files found in '{resumes_dir}'. "
            "Run `python generate_resumes.py` first."
        )
    for resume_path in all_files:
        if resume_path.suffix.lower() == ".pdf":
            text = load_pdf_text(resume_path)
        else:
            text = load_txt_text(resume_path)
        if text:
            resumes.append({
                "path": str(resume_path),
                "filename": resume_path.name,
                "text": text,
            })
    print(f"[INFO] Loaded {len(resumes)} resumes from '{resumes_dir}'")
    return resumes


# ─── 2. Metadata Extraction ────────────────────────────────────────────────────

def extract_name_from_path(filepath: str) -> str:
    """Derive candidate name from PDF filename (e.g. alice_chen.pdf -> Alice Chen)."""
    stem = Path(filepath).stem  # e.g. alice_chen
    return " ".join(word.capitalize() for word in stem.split("_"))


def extract_years_experience(text: str) -> int:
    """Heuristically extract years of experience from resume text."""
    # Pattern: "X years of experience", "X+ years", etc.
    patterns = [
        r"(\d+)\+?\s+years?\s+of\s+experience",
        r"(\d+)\+?\s+years?\s+experience",
        r"(\d+)\+?\s+years?\s+in",
        r"over\s+(\d+)\s+years?",
        r"more\s+than\s+(\d+)\s+years?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))

    # Fallback: count duration mentions like "2020 - Present" or "2018 – 2023"
    duration_matches = re.findall(
        r"(\d{4})\s*[-–]\s*(Present|\d{4})", text, re.IGNORECASE
    )
    if duration_matches:
        total_years = 0
        current_year = 2025
        for start, end in duration_matches:
            end_year = current_year if end.lower() == "present" else int(end)
            total_years += max(0, end_year - int(start))
        return min(total_years, 50)  # cap at 50

    return 0


def extract_education(text: str) -> str:
    """Extract education section text."""
    edu_pattern = re.compile(
        r"(?i)(education.*?)(?=\n[A-Z]{2,}|\Z)", re.DOTALL
    )
    match = edu_pattern.search(text)
    if match:
        section = match.group(0).strip()
        return section[:500]  # truncate

    # Fallback: look for degree keywords
    degree_pattern = re.compile(
        r"(?i)(B\.?S\.?|M\.?S\.?|Ph\.?D\.?|B\.?A\.?|M\.?A\.?|MBA|B\.?Tech|M\.?Tech)[^.]*(?:University|College|Institute|School)[^.]*\.",
        re.MULTILINE,
    )
    matches = degree_pattern.findall(text)
    return " | ".join(matches[:3]) if matches else "Not specified"


def extract_skills(text: str) -> list[str]:
    """Extract skills from the skills section."""
    # Common tech skills to scan for
    known_skills = [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "Scala", "R",
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra",
        "TensorFlow", "PyTorch", "Scikit-learn", "Keras", "XGBoost", "Pandas", "NumPy",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Reinforcement Learning",
        "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform", "Ansible",
        "React", "Next.js", "Vue.js", "Node.js", "FastAPI", "Django", "Flask", "Spring Boot",
        "Kafka", "Spark", "Airflow", "Flink", "Hadoop", "dbt", "Snowflake",
        "MLflow", "Kubeflow", "Ray", "LangChain", "HuggingFace", "Transformers", "BERT", "GPT",
        "RAG", "Vector Database", "ChromaDB", "Pinecone", "Weaviate",
        "Git", "Linux", "Bash", "CI/CD", "Microservices", "REST APIs", "GraphQL", "gRPC",
        "Swift", "Kotlin", "Flutter", "React Native",
        "Solidity", "Blockchain", "Ethereum",
        "CUDA", "OpenCV", "ROS", "Prometheus", "Grafana",
    ]
    found_skills = []
    text_lower = text.lower()
    for skill in known_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    return found_skills


def extract_metadata(resume: dict) -> dict:
    """Extract structured metadata from resume text."""
    text = resume["text"]
    metadata = {
        "candidate_name": extract_name_from_path(resume["path"]),
        "resume_path": resume["path"],
        "filename": resume["filename"],
        "years_experience": extract_years_experience(text),
        "education_summary": extract_education(text),
        "skills": extract_skills(text),
        "skills_str": "|".join(extract_skills(text)),  # ChromaDB stores strings
    }
    return metadata


# ─── 3. Document Chunking ──────────────────────────────────────────────────────

def split_into_sections(text: str) -> dict[str, str]:
    """Split resume text into labeled sections."""
    lines = text.split("\n")
    sections = {}
    current_section = "header"
    current_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_lines.append(line)
            continue

        # Check if this line is a section header
        matched_section = None
        for section_name, pattern in SECTION_PATTERNS.items():
            if re.match(pattern, stripped) and len(stripped) < 60:
                matched_section = section_name
                break

        if matched_section:
            # Save previous section
            if current_lines:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = matched_section
            current_lines = [line]
        else:
            current_lines.append(line)

    # Save last section
    if current_lines:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections


def chunk_text_by_words(text: str, chunk_size: int = 250, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping word-based chunks."""
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        if end >= len(words):
            break
        start += chunk_size - overlap  # slide with overlap

    return chunks


def create_chunks(resume: dict, metadata: dict) -> list[dict]:
    """
    Create intelligent chunks from a resume, preserving section context.

    Returns:
        List of chunk dicts: {text, chunk_id, section, metadata, ...}
    """
    text = resume["text"]
    sections = split_into_sections(text)
    all_chunks = []

    chunk_sizes = {
        "header": 150,
        "summary": 150,
        "skills": 200,
        "experience": 200,
        "education": 150,
        "certifications": 100,
        "projects": 200,
    }

    for section_name, section_text in sections.items():
        if not section_text.strip():
            continue

        chunk_size = chunk_sizes.get(section_name, 200)
        text_chunks = chunk_text_by_words(section_text, chunk_size=chunk_size)

        for idx, chunk_text in enumerate(text_chunks):
            # Create a stable unique ID
            raw_id = f"{metadata['filename']}_{section_name}_{idx}"
            chunk_id = hashlib.md5(raw_id.encode()).hexdigest()[:16]

            all_chunks.append({
                "chunk_id": chunk_id,
                "section": section_name,
                "text": chunk_text,
                "text_with_context": f"[{section_name.upper()}]\n{chunk_text}",
                "metadata": {
                    **metadata,
                    "section": section_name,
                    "chunk_index": idx,
                },
            })

    return all_chunks


# ─── 4. Embedding Model ────────────────────────────────────────────────────────

class EmbeddingModel:
    """Wrapper for HuggingFace SentenceTransformer embeddings."""

    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        print(f"[INFO] Loading embedding model: {model_name}")
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.model_name = model_name

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts. Returns list of float vectors."""
        if not texts:
            return []
        embeddings = self.model.encode(texts, batch_size=32, show_progress_bar=False)
        return embeddings.tolist()

    def embed_single(self, text: str) -> list[float]:
        return self.embed([text])[0]


# ─── 5. Vector Store (ChromaDB) ────────────────────────────────────────────────

class ResumeVectorStore:
    """ChromaDB-backed vector store for resume chunks."""

    def __init__(self, persist_dir: str = CHROMA_DB_PATH):
        self.persist_dir = persist_dir
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        print(f"[INFO] ChromaDB initialized at '{persist_dir}' (collection: '{COLLECTION_NAME}')")

    def add_chunks(self, chunks: list[dict], embeddings: list[list[float]]):
        """Add chunk documents with embeddings to ChromaDB."""
        if not chunks:
            return

        ids = [c["chunk_id"] for c in chunks]
        documents = [c["text_with_context"] for c in chunks]
        metadatas = []
        for c in chunks:
            # ChromaDB metadata must be str/int/float/bool only
            meta = c["metadata"].copy()
            meta.pop("skills", None)  # remove list; keep skills_str
            metadatas.append(meta)

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        where: Optional[dict] = None,
    ) -> dict:
        """Run semantic search and return results."""
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where
        return self.collection.query(**kwargs)

    def count(self) -> int:
        return self.collection.count()

    def reset(self):
        """Delete and recreate collection."""
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        print("[INFO] Collection reset.")


# ─── 6. Main Indexing Pipeline ─────────────────────────────────────────────────

class ResumeRAG:
    """
    Full RAG pipeline for resume ingestion and retrieval.

    Usage:
        rag = ResumeRAG()
        rag.index_resumes()          # Build vector DB
        results = rag.retrieve(jd_text, top_k=10)
    """

    def __init__(self):
        self.embedder = EmbeddingModel()
        self.store = ResumeVectorStore()

    def index_resumes(self, force_reindex: bool = False):
        """Load resumes, chunk, embed, and store in ChromaDB."""
        if not force_reindex and self.store.count() > 0:
            print(f"[INFO] Vector store already has {self.store.count()} chunks. Skipping re-index.")
            print("[INFO] Pass force_reindex=True to rebuild.")
            return

        if force_reindex:
            self.store.reset()

        resumes = load_all_resumes()
        total_chunks = 0
        start_time = time.time()

        for resume in resumes:
            metadata = extract_metadata(resume)
            chunks = create_chunks(resume, metadata)
            if not chunks:
                continue

            # Embed all chunks
            texts = [c["text_with_context"] for c in chunks]
            embeddings = self.embedder.embed(texts)

            self.store.add_chunks(chunks, embeddings)
            total_chunks += len(chunks)
            print(f"  Indexed {metadata['candidate_name']}: {len(chunks)} chunks")

        elapsed = time.time() - start_time
        print(f"\n[INFO] Indexing complete: {total_chunks} chunks from {len(resumes)} resumes in {elapsed:.1f}s")
        print(f"[INFO] Total vectors in store: {self.store.count()}")

    def retrieve(
        self,
        query_text: str,
        top_k: int = 10,
        min_experience_years: Optional[int] = None,
    ) -> list[dict]:
        """
        Retrieve top-K most relevant resume chunks for a query.

        Args:
            query_text: Job description or search query.
            top_k: Number of results to return.
            min_experience_years: Optional filter for minimum years of experience.

        Returns:
            List of result dicts with chunk text, metadata, and similarity score.
        """
        query_embedding = self.embedder.embed_single(query_text)

        where = None
        if min_experience_years is not None:
            where = {"years_experience": {"$gte": min_experience_years}}

        total = self.store.count()
        if total == 0:
            return []
        raw = self.store.query(
            query_embedding=query_embedding,
            n_results=min(top_k * 3, total),  # fetch more, deduplicate by candidate
            where=where,
        )

        results = []
        if not raw["ids"] or not raw["ids"][0]:
            return results

        for doc, meta, dist in zip(
            raw["documents"][0],
            raw["metadatas"][0],
            raw["distances"][0],
        ):
            # Convert cosine distance to similarity score (0–1)
            similarity = 1.0 - dist
            results.append({
                "text": doc,
                "metadata": meta,
                "similarity": round(float(similarity), 4),
                "section": meta.get("section", "unknown"),
            })

        return results

    def get_store_stats(self) -> dict:
        """Return stats about the vector store."""
        count = self.store.count()
        return {
            "total_chunks": count,
            "collection_name": COLLECTION_NAME,
            "persist_dir": CHROMA_DB_PATH,
            "embedding_model": self.embedder.model_name,
        }


# ─── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Resume RAG System")
    parser.add_argument("--index", action="store_true", help="Index resumes into vector DB")
    parser.add_argument("--force", action="store_true", help="Force re-indexing")
    parser.add_argument("--stats", action="store_true", help="Show vector store stats")
    parser.add_argument("--query", type=str, help="Run a test query")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return")
    args = parser.parse_args()

    rag = ResumeRAG()

    if args.index or args.force:
        rag.index_resumes(force_reindex=args.force)

    if args.stats:
        stats = rag.get_store_stats()
        print("\n=== Vector Store Stats ===")
        for k, v in stats.items():
            print(f"  {k}: {v}")

    if args.query:
        print(f"\n=== Query: '{args.query}' (top {args.top_k}) ===")
        results = rag.retrieve(args.query, top_k=args.top_k)
        for i, r in enumerate(results[:args.top_k], 1):
            print(f"\n{i}. [{r['section']}] {r['metadata'].get('candidate_name', 'Unknown')} "
                  f"(score: {r['similarity']:.3f})")
            print(f"   {r['text'][:200]}...")
