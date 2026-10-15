"""
job_matcher.py
--------------
Part B: Job Matching Engine

Implements:
  - Semantic search: JD -> embedding -> vector similarity retrieval
  - Hybrid search: semantic + keyword matching for critical skills
  - Ranking & scoring (0-100 scale)
  - Match reasoning with section-level evidence
  - Filtering by must-have requirements (min experience)
  - Structured JSON output

Usage:
    python job_matcher.py                        # demo
    python job_matcher.py --jd job_descriptions/ml_engineer.txt --top-k 10
    python job_matcher.py --query "Python ML engineer 5 years" --min-exp 3
    python job_matcher.py --all-jds              # run all JDs in job_descriptions/
"""

import os
import re
import json
import time
from pathlib import Path
from dotenv import load_dotenv

from resume_rag import ResumeRAG

load_dotenv()

TOP_K = int(os.getenv("TOP_K", "10"))
JD_DIR = Path(os.getenv("JD_DIR", "./job_descriptions"))

CRITICAL_SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#", "Scala", "R",
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra",
    "TensorFlow", "PyTorch", "Scikit-learn", "Keras", "XGBoost", "Pandas", "NumPy",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Reinforcement Learning",
    "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform", "Ansible",
    "React", "Next.js", "Vue.js", "Node.js", "FastAPI", "Django", "Flask", "Spring Boot",
    "Kafka", "Spark", "Airflow", "Flink", "Hadoop", "dbt", "Snowflake",
    "MLflow", "Kubeflow", "Ray", "LangChain", "HuggingFace", "Transformers", "BERT", "GPT",
    "RAG", "ChromaDB", "Pinecone", "Weaviate", "LlamaIndex",
    "Git", "Linux", "Bash", "CI/CD", "Microservices", "REST APIs", "GraphQL", "gRPC",
    "Swift", "Kotlin", "Flutter", "React Native",
    "Solidity", "Blockchain", "Ethereum",
    "CUDA", "OpenCV", "ROS", "Prometheus", "Grafana",
    "Selenium", "Playwright", "Cypress", "JUnit", "PyTest",
    "Tableau", "Power BI", "Looker", "BigQuery", "Redshift",
]


def extract_skills_from_jd(jd_text):
    """Extract known tech skills mentioned in a job description."""
    found = []
    text_lower = jd_text.lower()
    for skill in CRITICAL_SKILLS:
        if skill.lower() in text_lower:
            found.append(skill)
    return found


def extract_min_experience(jd_text):
    """Heuristically detect minimum years of experience requirement."""
    patterns = [
        r"(\d+)\+?\s*years?\s+of\s+experience",
        r"(\d+)\+?\s*years?\s+experience",
        r"minimum\s+(\d+)\s+years?",
        r"at\s+least\s+(\d+)\s+years?",
        r"(\d+)-\d+\s+years?",
    ]
    for pat in patterns:
        m = re.search(pat, jd_text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return None


def compute_keyword_score(candidate_skills_str, jd_skills):
    """Keyword overlap score (0.0 to 1.0)."""
    if not jd_skills:
        return 0.5
    cand_lower = candidate_skills_str.lower()
    matched = sum(1 for s in jd_skills if s.lower() in cand_lower)
    return matched / len(jd_skills)


def aggregate_candidate_chunks(raw_results):
    """Group retrieved chunks by candidate name."""
    candidates = {}
    for result in raw_results:
        meta = result["metadata"]
        name = meta.get("candidate_name", "Unknown")
        if name not in candidates:
            candidates[name] = {
                "candidate_name": name,
                "resume_path": meta.get("resume_path", ""),
                "years_experience": meta.get("years_experience", 0),
                "skills_str": meta.get("skills_str", ""),
                "education_summary": meta.get("education_summary", ""),
                "sections_matched": set(),
                "chunks": [],
            }
        candidates[name]["sections_matched"].add(result.get("section", "unknown"))
        candidates[name]["chunks"].append({
            "similarity": result["similarity"],
            "text": result["text"],
            "section": result.get("section", "unknown"),
        })
    for name in candidates:
        candidates[name]["chunks"].sort(key=lambda x: x["similarity"], reverse=True)
    return candidates


def score_candidate(candidate, jd_skills, min_experience, semantic_weight=0.6, keyword_weight=0.4):
    """
    Compute a 0-100 composite match score.
    Score = 60% semantic similarity + 40% keyword overlap.
    Experience shortfall applies a soft 15-point penalty.
    """
    chunks = candidate["chunks"]
    if not chunks:
        return {
            **{k: v for k, v in candidate.items() if k not in ("chunks", "sections_matched")},
            "match_score": 0,
            "matched_skills": [],
            "relevant_excerpts": [],
            "reasoning": "No matching chunks found.",
            "sections_matched": [],
        }

    # Semantic score: average of top-3 chunks + section diversity bonus
    avg_top3 = sum(c["similarity"] for c in chunks[:3]) / min(3, len(chunks))
    section_bonus = min(0.05 * len(candidate["sections_matched"]), 0.15)
    semantic_score = min(avg_top3 + section_bonus, 1.0)

    # Keyword score
    keyword_score = compute_keyword_score(candidate["skills_str"], jd_skills)

    # Composite (0-100)
    composite = (semantic_weight * semantic_score) + (keyword_weight * keyword_score)
    match_score = round(composite * 100)

    # Experience penalty
    exp_penalty = 0
    exp_note = ""
    if min_experience is not None:
        years = candidate.get("years_experience", 0)
        if years < min_experience:
            exp_penalty = 15
            exp_note = (
                f"Candidate has {years} yrs experience (JD requires {min_experience}+). "
            )
    match_score = max(0, match_score - exp_penalty)

    # Matched skills list
    cand_lower = candidate["skills_str"].lower()
    matched_skills = [s for s in jd_skills if s.lower() in cand_lower]

    # Relevant excerpts (top-3 chunks, cleaned)
    excerpts = []
    for chunk in chunks[:3]:
        clean = re.sub(r"^\[[A-Z_]+\]\n", "", chunk["text"]).strip()
        excerpts.append(clean[:300])

    # Build reasoning
    best_sim = chunks[0]["similarity"]
    section_list = ", ".join(sorted(candidate["sections_matched"]))
    reasoning = (
        f"Semantic similarity: {best_sim:.2f} (best chunk) across sections [{section_list}]. "
        f"Keyword match: {len(matched_skills)}/{len(jd_skills) if jd_skills else 0} required skills. "
        f"Experience: {candidate.get('years_experience', 0)} yrs. "
        + exp_note
        + (f"Top matched skills: {', '.join(matched_skills[:8])}." if matched_skills else "")
    )

    return {
        "candidate_name": candidate["candidate_name"],
        "resume_path": candidate["resume_path"],
        "years_experience": candidate["years_experience"],
        "match_score": match_score,
        "matched_skills": matched_skills,
        "relevant_excerpts": excerpts,
        "reasoning": reasoning,
        "sections_matched": sorted(candidate["sections_matched"]),
        "education_summary": candidate.get("education_summary", ""),
    }


class JobMatcher:
    """
    High-level job matching engine combining semantic RAG retrieval
    with keyword-based hybrid scoring.

    Usage:
        matcher = JobMatcher()
        result = matcher.match(jd_text, top_k=10)
        print(json.dumps(result, indent=2))
    """

    def __init__(self):
        self.rag = ResumeRAG()
        if self.rag.store.count() == 0:
            print("[INFO] Vector store is empty. Indexing resumes first...")
            self.rag.index_resumes()

    def match(
        self,
        jd_text,
        top_k=TOP_K,
        min_experience=None,
        auto_detect_exp=True,
        semantic_weight=0.6,
        keyword_weight=0.4,
    ):
        """
        Run full matching pipeline for a job description.

        Returns dict with keys:
            job_description, jd_skills, min_experience_required,
            top_matches, retrieval_latency_ms, total_candidates_evaluated
        Each top_match has:
            candidate_name, resume_path, match_score, matched_skills,
            relevant_excerpts, reasoning, sections_matched, education_summary
        """
        t0 = time.time()

        jd_skills = extract_skills_from_jd(jd_text)
        if auto_detect_exp and min_experience is None:
            min_experience = extract_min_experience(jd_text)

        print(f"[INFO] JD skills detected ({len(jd_skills)}): {jd_skills}")
        if min_experience:
            print(f"[INFO] Min experience detected: {min_experience} years")

        fetch_k = min(top_k * 5, max(self.rag.store.count(), 1))
        raw_results = self.rag.retrieve(
            query_text=jd_text,
            top_k=fetch_k,
            min_experience_years=None,
        )

        if not raw_results:
            return {
                "job_description": jd_text[:500],
                "jd_skills": jd_skills,
                "min_experience_required": min_experience,
                "top_matches": [],
                "retrieval_latency_ms": round((time.time() - t0) * 1000),
                "total_candidates_evaluated": 0,
            }

        candidates = aggregate_candidate_chunks(raw_results)

        scored = [
            score_candidate(
                cand,
                jd_skills=jd_skills,
                min_experience=min_experience,
                semantic_weight=semantic_weight,
                keyword_weight=keyword_weight,
            )
            for cand in candidates.values()
        ]
        scored.sort(key=lambda x: x["match_score"], reverse=True)

        elapsed_ms = round((time.time() - t0) * 1000)
        print(f"[INFO] Ranked {len(candidates)} candidates in {elapsed_ms}ms")

        return {
            "job_description": jd_text[:500] + ("..." if len(jd_text) > 500 else ""),
            "jd_skills": jd_skills,
            "min_experience_required": min_experience,
            "top_matches": scored[:top_k],
            "retrieval_latency_ms": elapsed_ms,
            "total_candidates_evaluated": len(candidates),
        }

    def match_from_file(self, jd_path, top_k=TOP_K, **kwargs):
        path = Path(jd_path)
        if not path.exists():
            raise FileNotFoundError(f"JD file not found: {jd_path}")
        jd_text = path.read_text(encoding="utf-8")
        print(f"[INFO] Loaded JD: {path.name} ({len(jd_text)} chars)")
        return self.match(jd_text, top_k=top_k, **kwargs)

    def load_all_jds(self, jd_dir=None):
        d = Path(jd_dir) if jd_dir else JD_DIR
        return {f.stem: f.read_text(encoding="utf-8") for f in sorted(d.glob("*.txt"))} if d.exists() else {}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RAG-based Resume Matcher")
    parser.add_argument("--jd", type=str, help="Path to job description .txt file")
    parser.add_argument("--query", type=str, help="Job description as inline text")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--min-exp", type=int, default=None)
    parser.add_argument("--output", type=str, default=None, help="Save JSON results to file")
    parser.add_argument("--index", action="store_true", help="Force re-index resumes")
    parser.add_argument("--all-jds", action="store_true", help="Run all JDs in job_descriptions/")
    args = parser.parse_args()

    matcher = JobMatcher()

    if args.index:
        matcher.rag.index_resumes(force_reindex=True)

    if args.all_jds:
        jds = matcher.load_all_jds()
        if not jds:
            print(f"[WARN] No .txt files found in {JD_DIR}")
        for jd_name, jd_text in jds.items():
            print(f"\n{'='*60}\nJD: {jd_name}\n{'='*60}")
            result = matcher.match(jd_text, top_k=args.top_k, min_experience=args.min_exp)
            out_path = f"match_results_{jd_name}.json"
            with open(out_path, "w") as fp:
                json.dump(result, fp, indent=2, default=str)
            for i, m in enumerate(result["top_matches"][:5], 1):
                print(f"  {i}. {m['candidate_name']:30s} Score={m['match_score']:3d}/100  Skills={m['matched_skills'][:4]}")
            print(f"[SAVED] {out_path}")

    elif args.jd:
        result = matcher.match_from_file(args.jd, top_k=args.top_k, min_experience=args.min_exp)
        output = json.dumps(result, indent=2, default=str)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            print(f"[SAVED] {args.output}")
        else:
            print(output)

    elif args.query:
        result = matcher.match(args.query, top_k=args.top_k, min_experience=args.min_exp)
        print(json.dumps(result, indent=2, default=str))

    else:
        # Default demo
        demo_jd = """
        Senior Machine Learning Engineer - 5+ years experience required.
        We need strong expertise in: Python, PyTorch or TensorFlow, MLflow or Kubeflow,
        Large Language Models (LLMs), RAG systems, HuggingFace Transformers, NLP.
        Cloud platforms: AWS or GCP. Docker and Kubernetes. Fine-tuning LLMs on domain data.
        Experience with vector databases (ChromaDB, Pinecone, Weaviate) is a plus.
        """
        print("=== Demo: Senior ML Engineer Matching ===")
        result = matcher.match(demo_jd, top_k=5)
        print(f"\nTop 5 Candidates:")
        for i, m in enumerate(result["top_matches"], 1):
            print(f"\n  {i}. {m['candidate_name']} | Score: {m['match_score']}/100 | Exp: {m['years_experience']} yrs")
            print(f"     Skills: {', '.join(m['matched_skills'][:6])}")
            print(f"     {m['reasoning'][:220]}")
