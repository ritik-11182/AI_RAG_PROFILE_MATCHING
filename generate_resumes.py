"""
generate_resumes.py
-------------------
Generates 35+ diverse synthetic resumes as PDF files for the RAG pipeline.
Covers a wide range of roles, experience levels, and skill sets.
"""

import os
import random
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors

# ─── Output directory ───────────────────────────────────────────────────────
OUTPUT_DIR = Path("resumes")
OUTPUT_DIR.mkdir(exist_ok=True)

# ─── Candidate pool data ─────────────────────────────────────────────────────
CANDIDATES = [
    # ── Machine Learning / AI ──────────────────────────────────────────────
    {
        "name": "Alice Chen",
        "email": "alice.chen@email.com",
        "phone": "+1-415-555-0101",
        "location": "San Francisco, CA",
        "summary": "Senior Machine Learning Engineer with 7 years of experience building production ML systems. Expert in deep learning, NLP, and MLOps. Led teams delivering large-scale recommendation and ranking systems.",
        "skills": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "MLflow", "Kubeflow", "Docker", "Kubernetes", "SQL", "Spark", "AWS SageMaker", "BERT", "Transformers", "Feature Engineering", "A/B Testing"],
        "experience": [
            {
                "title": "Senior ML Engineer",
                "company": "TechCorp Inc.",
                "duration": "2020 - Present",
                "bullets": [
                    "Designed and deployed a real-time recommendation engine serving 50M+ users, increasing CTR by 18%.",
                    "Built end-to-end MLOps pipeline with MLflow and Kubeflow, reducing model deployment time by 60%.",
                    "Led a team of 4 engineers to fine-tune BERT-based NLP models for sentiment analysis at scale.",
                ]
            },
            {
                "title": "ML Engineer",
                "company": "DataDriven LLC",
                "duration": "2017 - 2020",
                "bullets": [
                    "Developed churn prediction models achieving 92% AUC-ROC using ensemble methods.",
                    "Implemented feature stores and data pipelines using Apache Spark and AWS S3.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Computer Science (Machine Learning)", "school": "Stanford University", "year": "2017"},
            {"degree": "B.S. Mathematics", "school": "UC Berkeley", "year": "2015"},
        ],
        "years_exp": 7,
    },
    {
        "name": "Bob Martinez",
        "email": "bob.martinez@email.com",
        "phone": "+1-512-555-0102",
        "location": "Austin, TX",
        "summary": "Data Scientist with 5 years of experience in predictive analytics, computer vision, and NLP. Passionate about converting raw data into actionable business insights.",
        "skills": ["Python", "R", "Scikit-learn", "Keras", "OpenCV", "Pandas", "NumPy", "Tableau", "SQL", "PostgreSQL", "GCP", "BigQuery", "Statistics", "Time Series Analysis", "XGBoost"],
        "experience": [
            {
                "title": "Data Scientist",
                "company": "Analytics Pro",
                "duration": "2021 - Present",
                "bullets": [
                    "Built computer vision pipeline for defect detection reducing manufacturing errors by 35%.",
                    "Developed time series forecasting models for supply chain optimization saving $2M annually.",
                ]
            },
            {
                "title": "Junior Data Scientist",
                "company": "InsightGen",
                "duration": "2019 - 2021",
                "bullets": [
                    "Created NLP pipelines for customer feedback classification with 89% accuracy.",
                    "Automated reporting dashboards using Tableau, saving 10 hours/week of analyst time.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Data Science", "school": "UT Austin", "year": "2019"},
            {"degree": "B.S. Statistics", "school": "Texas A&M University", "year": "2017"},
        ],
        "years_exp": 5,
    },
    {
        "name": "Carol Johnson",
        "email": "carol.johnson@email.com",
        "phone": "+1-206-555-0103",
        "location": "Seattle, WA",
        "summary": "AI Research Scientist with 9 years specializing in reinforcement learning, generative models, and large language models. Published 12 papers in top-tier venues (NeurIPS, ICML, ICLR).",
        "skills": ["Python", "PyTorch", "JAX", "Reinforcement Learning", "GANs", "Diffusion Models", "LLMs", "GPT", "RLHF", "Transformers", "CUDA", "C++", "Research", "Academic Writing", "Experimentation"],
        "experience": [
            {
                "title": "AI Research Scientist",
                "company": "AI Labs",
                "duration": "2019 - Present",
                "bullets": [
                    "Pioneered RLHF techniques for aligning large language models, contributing to internal 70B parameter model.",
                    "Published 8 papers on generative models at NeurIPS, ICML, and ICLR.",
                    "Mentored 5 junior researchers and interns in deep learning research.",
                ]
            },
            {
                "title": "Research Scientist",
                "company": "University Research Lab",
                "duration": "2015 - 2019",
                "bullets": [
                    "Developed novel RL algorithms for robotics control tasks, achieving state-of-the-art performance.",
                    "Collaborated with industry partners on applied AI research projects.",
                ]
            }
        ],
        "education": [
            {"degree": "Ph.D. Computer Science (AI)", "school": "MIT", "year": "2015"},
            {"degree": "B.S. Computer Science", "school": "Caltech", "year": "2010"},
        ],
        "years_exp": 9,
    },
    {
        "name": "David Park",
        "email": "david.park@email.com",
        "phone": "+1-212-555-0104",
        "location": "New York, NY",
        "summary": "Full-Stack Software Engineer with 6 years building scalable web applications. Proficient in React, Node.js, and cloud-native architectures. Strong focus on performance optimization and developer experience.",
        "skills": ["JavaScript", "TypeScript", "React", "Next.js", "Node.js", "Express", "GraphQL", "PostgreSQL", "Redis", "Docker", "AWS", "CI/CD", "Git", "REST APIs", "Microservices"],
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "WebScale Inc.",
                "duration": "2021 - Present",
                "bullets": [
                    "Architected and built React-based SPA serving 2M monthly active users with 99.9% uptime.",
                    "Migrated monolithic backend to microservices, reducing p99 latency by 45%.",
                    "Led adoption of GraphQL federation across 6 engineering teams.",
                ]
            },
            {
                "title": "Software Engineer",
                "company": "StartupXYZ",
                "duration": "2018 - 2021",
                "bullets": [
                    "Built RESTful APIs with Node.js/Express powering the core product backend.",
                    "Implemented real-time features using WebSockets and Redis Pub/Sub.",
                ]
            }
        ],
        "education": [
            {"degree": "B.S. Computer Science", "school": "Columbia University", "year": "2018"},
        ],
        "years_exp": 6,
    },
    {
        "name": "Emma Wilson",
        "email": "emma.wilson@email.com",
        "phone": "+1-415-555-0105",
        "location": "San Francisco, CA",
        "summary": "Backend Engineer with 4 years of experience in Python and Go, specializing in distributed systems and high-throughput data pipelines. AWS Certified Solutions Architect.",
        "skills": ["Python", "Go", "Golang", "FastAPI", "Django", "Kafka", "RabbitMQ", "PostgreSQL", "MongoDB", "Redis", "AWS", "Terraform", "Docker", "Kubernetes", "gRPC"],
        "experience": [
            {
                "title": "Backend Engineer",
                "company": "StreamFlow",
                "duration": "2022 - Present",
                "bullets": [
                    "Designed Kafka-based event streaming platform processing 1M+ events/second.",
                    "Built FastAPI services with async I/O achieving 10x throughput improvement.",
                ]
            },
            {
                "title": "Junior Backend Engineer",
                "company": "DataPipe",
                "duration": "2020 - 2022",
                "bullets": [
                    "Developed data ingestion pipelines in Python processing 5TB of data daily.",
                    "Maintained PostgreSQL database schemas and query optimization.",
                ]
            }
        ],
        "education": [
            {"degree": "B.S. Computer Engineering", "school": "UC San Diego", "year": "2020"},
        ],
        "years_exp": 4,
    },
    {
        "name": "Frank Thompson",
        "email": "frank.thompson@email.com",
        "phone": "+1-512-555-0106",
        "location": "Austin, TX",
        "summary": "DevOps Engineer with 8 years of experience automating infrastructure, building CI/CD pipelines, and managing cloud environments at scale. Expertise in AWS, Kubernetes, and Infrastructure as Code.",
        "skills": ["AWS", "Azure", "GCP", "Kubernetes", "Docker", "Terraform", "Ansible", "Jenkins", "GitHub Actions", "Prometheus", "Grafana", "Helm", "Python", "Bash", "Linux"],
        "experience": [
            {
                "title": "Senior DevOps Engineer",
                "company": "CloudOps Corp",
                "duration": "2019 - Present",
                "bullets": [
                    "Managed Kubernetes clusters of 500+ nodes across 3 AWS regions with 99.99% availability.",
                    "Reduced cloud infrastructure costs by 40% through right-sizing and spot instance automation.",
                    "Built GitOps-based deployment pipelines reducing release cycle from weekly to daily.",
                ]
            },
            {
                "title": "DevOps Engineer",
                "company": "TechOps LLC",
                "duration": "2016 - 2019",
                "bullets": [
                    "Implemented infrastructure as code using Terraform managing 200+ AWS resources.",
                    "Set up centralized monitoring with Prometheus and Grafana alerting system.",
                ]
            }
        ],
        "education": [
            {"degree": "B.S. Information Technology", "school": "Georgia Tech", "year": "2016"},
        ],
        "years_exp": 8,
    },
    {
        "name": "Grace Lee",
        "email": "grace.lee@email.com",
        "phone": "+1-312-555-0107",
        "location": "Chicago, IL",
        "summary": "Data Engineer with 6 years building scalable data lakes, ETL pipelines, and analytical platforms. Experienced with Spark, Airflow, and cloud data warehousing solutions.",
        "skills": ["Python", "Apache Spark", "Apache Airflow", "dbt", "Snowflake", "BigQuery", "Redshift", "Kafka", "Flink", "SQL", "Scala", "AWS", "GCP", "Delta Lake", "Data Modeling"],
        "experience": [
            {
                "title": "Senior Data Engineer",
                "company": "DataHub Inc.",
                "duration": "2021 - Present",
                "bullets": [
                    "Architected petabyte-scale data lake on AWS using Delta Lake and Apache Spark.",
                    "Built 50+ production Airflow DAGs for data orchestration across 10+ source systems.",
                    "Implemented real-time streaming pipelines with Kafka and Flink for fraud detection.",
                ]
            },
            {
                "title": "Data Engineer",
                "company": "Analytics Corp",
                "duration": "2018 - 2021",
                "bullets": [
                    "Migrated legacy ETL processes to dbt + Snowflake, reducing pipeline run time by 70%.",
                    "Developed data quality frameworks catching 95% of data issues before reaching dashboards.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Information Systems", "school": "Northwestern University", "year": "2018"},
            {"degree": "B.S. Computer Science", "school": "University of Illinois", "year": "2016"},
        ],
        "years_exp": 6,
    },
    {
        "name": "Henry Zhang",
        "email": "henry.zhang@email.com",
        "phone": "+1-415-555-0108",
        "location": "San Jose, CA",
        "summary": "iOS Developer with 5 years creating high-quality mobile applications. Expert in Swift, SwiftUI, and performance optimization. Published 8 apps with 4.8+ App Store ratings.",
        "skills": ["Swift", "SwiftUI", "UIKit", "Objective-C", "Xcode", "Core Data", "Combine", "TestFlight", "REST APIs", "Git", "Firebase", "Push Notifications", "App Store Connect", "Instruments", "Core Animation"],
        "experience": [
            {
                "title": "Senior iOS Developer",
                "company": "MobileFirst Inc.",
                "duration": "2021 - Present",
                "bullets": [
                    "Led iOS development for fintech app with 1M+ downloads and 4.9 App Store rating.",
                    "Migrated UIKit codebase to SwiftUI, reducing boilerplate code by 40%.",
                    "Implemented end-to-end encryption for sensitive financial transactions.",
                ]
            },
            {
                "title": "iOS Developer",
                "company": "AppStudio",
                "duration": "2019 - 2021",
                "bullets": [
                    "Built and published 4 consumer apps generating $500K annual revenue.",
                    "Optimized app launch time by 50% through lazy loading and memory management.",
                ]
            }
        ],
        "education": [
            {"degree": "B.S. Software Engineering", "school": "San Jose State University", "year": "2019"},
        ],
        "years_exp": 5,
    },
    {
        "name": "Isabel Rodriguez",
        "email": "isabel.rodriguez@email.com",
        "phone": "+1-305-555-0109",
        "location": "Miami, FL",
        "summary": "Android Developer with 4 years building robust mobile applications using Kotlin and Jetpack Compose. Focused on clean architecture and test-driven development.",
        "skills": ["Kotlin", "Java", "Jetpack Compose", "Android SDK", "MVVM", "Coroutines", "Room", "Retrofit", "Hilt", "Firebase", "Git", "JUnit", "Espresso", "Google Play Console", "Material Design"],
        "experience": [
            {
                "title": "Android Developer",
                "company": "AppDev Corp",
                "duration": "2022 - Present",
                "bullets": [
                    "Built Jetpack Compose-based e-commerce app with 500K+ downloads.",
                    "Implemented offline-first architecture using Room and WorkManager.",
                ]
            },
            {
                "title": "Junior Android Developer",
                "company": "MobileLab",
                "duration": "2020 - 2022",
                "bullets": [
                    "Developed and maintained 3 client Android applications.",
                    "Wrote 80%+ unit test coverage using JUnit and Mockito.",
                ]
            }
        ],
        "education": [
            {"degree": "B.S. Computer Science", "school": "University of Miami", "year": "2020"},
        ],
        "years_exp": 4,
    },
    {
        "name": "James Cooper",
        "email": "james.cooper@email.com",
        "phone": "+1-703-555-0110",
        "location": "Washington, DC",
        "summary": "Cybersecurity Engineer with 10 years protecting enterprise environments. Expert in penetration testing, threat hunting, and zero-trust architecture. CISSP and CEH certified.",
        "skills": ["Penetration Testing", "SIEM", "Splunk", "CrowdStrike", "Metasploit", "Burp Suite", "Python", "Bash", "Wireshark", "NIST Framework", "Zero-Trust", "SOC", "Incident Response", "CISSP", "CEH"],
        "experience": [
            {
                "title": "Principal Security Engineer",
                "company": "SecureNet Corp",
                "duration": "2018 - Present",
                "bullets": [
                    "Led zero-trust architecture implementation for 10,000-employee enterprise.",
                    "Managed SOC team of 8, achieving 15-minute mean time to detect (MTTD).",
                    "Conducted red team exercises identifying 200+ vulnerabilities across 3 years.",
                ]
            },
            {
                "title": "Security Engineer",
                "company": "CyberDefense LLC",
                "duration": "2014 - 2018",
                "bullets": [
                    "Performed 50+ penetration tests for Fortune 500 clients.",
                    "Deployed Splunk SIEM solution monitoring 5B+ security events daily.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Information Security", "school": "Carnegie Mellon University", "year": "2014"},
            {"degree": "B.S. Computer Science", "school": "Virginia Tech", "year": "2012"},
        ],
        "years_exp": 10,
    },
    {
        "name": "Karen White",
        "email": "karen.white@email.com",
        "phone": "+1-415-555-0111",
        "location": "San Francisco, CA",
        "summary": "Product Manager with 7 years driving product strategy for B2B SaaS companies. Skilled at stakeholder management, roadmap prioritization, and data-driven decision making.",
        "skills": ["Product Strategy", "Roadmap Planning", "Agile", "Scrum", "JIRA", "User Research", "A/B Testing", "SQL", "Mixpanel", "Amplitude", "Figma", "OKRs", "Go-to-Market", "Market Analysis", "Stakeholder Management"],
        "experience": [
            {
                "title": "Senior Product Manager",
                "company": "SaaS Leader Inc.",
                "duration": "2020 - Present",
                "bullets": [
                    "Grew annual recurring revenue from $5M to $25M by launching 3 major product features.",
                    "Led cross-functional team of 15 (engineering, design, data) to ship 40+ releases.",
                    "Defined and tracked OKRs achieving 95% of quarterly goals.",
                ]
            },
            {
                "title": "Product Manager",
                "company": "GrowthCo",
                "duration": "2017 - 2020",
                "bullets": [
                    "Launched mobile app reaching 100K users in 6 months.",
                    "Ran 30+ A/B experiments to optimize conversion funnel, improving by 22%.",
                ]
            }
        ],
        "education": [
            {"degree": "MBA", "school": "Wharton School, UPenn", "year": "2017"},
            {"degree": "B.S. Industrial Engineering", "school": "Cornell University", "year": "2015"},
        ],
        "years_exp": 7,
    },
    {
        "name": "Liam Brown",
        "email": "liam.brown@email.com",
        "phone": "+1-617-555-0112",
        "location": "Boston, MA",
        "summary": "Quantitative Analyst and Data Scientist with 6 years in financial services. Expert in risk modeling, algorithmic trading strategies, and statistical analysis.",
        "skills": ["Python", "R", "MATLAB", "SQL", "Machine Learning", "Time Series", "Risk Modeling", "Monte Carlo Simulation", "Bloomberg Terminal", "Pandas", "NumPy", "Statsmodels", "QuantLib", "Fixed Income", "Derivatives"],
        "experience": [
            {
                "title": "Senior Quantitative Analyst",
                "company": "CapitalEdge Partners",
                "duration": "2020 - Present",
                "bullets": [
                    "Developed systematic trading strategies generating 15% alpha over benchmark.",
                    "Built risk models for $2B fixed income portfolio management.",
                    "Automated factor analysis reducing research cycle from 2 weeks to 2 days.",
                ]
            },
            {
                "title": "Quantitative Analyst",
                "company": "FinTech Analytics",
                "duration": "2018 - 2020",
                "bullets": [
                    "Created pricing models for exotic derivatives using Monte Carlo methods.",
                    "Developed credit risk models with 88% predictive accuracy.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Financial Engineering", "school": "MIT Sloan", "year": "2018"},
            {"degree": "B.S. Mathematics and Statistics", "school": "Harvard University", "year": "2016"},
        ],
        "years_exp": 6,
    },
    {
        "name": "Maya Patel",
        "email": "maya.patel@email.com",
        "phone": "+1-408-555-0113",
        "location": "Mountain View, CA",
        "summary": "NLP Engineer with 5 years specializing in conversational AI, dialogue systems, and LLM fine-tuning. Experienced building chatbots and voice assistants at scale.",
        "skills": ["Python", "HuggingFace", "Transformers", "BERT", "GPT", "LangChain", "Rasa", "SpaCy", "NLTK", "DialogFlow", "AWS Lex", "Vector Databases", "RAG", "Fine-tuning", "Prompt Engineering"],
        "experience": [
            {
                "title": "NLP Engineer",
                "company": "ConvAI Labs",
                "duration": "2021 - Present",
                "bullets": [
                    "Built production RAG system for enterprise Q&A handling 100K daily queries.",
                    "Fine-tuned LLaMA-2 on domain-specific data achieving 35% improvement in task accuracy.",
                    "Developed multi-turn dialogue system with 92% user satisfaction rating.",
                ]
            },
            {
                "title": "ML Engineer - NLP",
                "company": "ChatTech",
                "duration": "2019 - 2021",
                "bullets": [
                    "Created intent classification system with 96% accuracy for customer service chatbot.",
                    "Deployed NER models for automated information extraction from legal documents.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Computational Linguistics", "school": "Stanford University", "year": "2019"},
            {"degree": "B.Tech Computer Science", "school": "IIT Bombay", "year": "2017"},
        ],
        "years_exp": 5,
    },
    {
        "name": "Nathan Davis",
        "email": "nathan.davis@email.com",
        "phone": "+1-206-555-0114",
        "location": "Seattle, WA",
        "summary": "Cloud Solutions Architect with 11 years designing enterprise-grade cloud infrastructures. AWS Solutions Architect Professional certified. Expertise in serverless, multi-cloud, and cost optimization.",
        "skills": ["AWS", "Azure", "GCP", "Terraform", "CloudFormation", "Lambda", "ECS", "EKS", "API Gateway", "S3", "RDS", "DynamoDB", "CDK", "Serverless", "Cost Optimization"],
        "experience": [
            {
                "title": "Principal Cloud Architect",
                "company": "CloudMatrix",
                "duration": "2017 - Present",
                "bullets": [
                    "Architected multi-cloud strategy for Fortune 100 client, achieving $10M annual savings.",
                    "Designed serverless platform handling 500M API calls/month with 99.999% SLA.",
                    "Led cloud migration of 200+ applications from on-premises to AWS.",
                ]
            },
            {
                "title": "Cloud Engineer",
                "company": "InfraCloud",
                "duration": "2013 - 2017",
                "bullets": [
                    "Implemented AWS VPC architectures and security groups for 50+ enterprise clients.",
                    "Reduced infrastructure costs by 30% through Reserved Instance strategy.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Distributed Systems", "school": "University of Washington", "year": "2013"},
            {"degree": "B.S. Computer Science", "school": "UCLA", "year": "2011"},
        ],
        "years_exp": 11,
    },
    {
        "name": "Olivia Turner",
        "email": "olivia.turner@email.com",
        "phone": "+1-312-555-0115",
        "location": "Chicago, IL",
        "summary": "Frontend Engineer and UX enthusiast with 5 years crafting pixel-perfect, accessible web experiences. Proficient in React, Vue.js, and design systems.",
        "skills": ["JavaScript", "TypeScript", "React", "Vue.js", "CSS", "SCSS", "Figma", "Storybook", "Webpack", "Vite", "Testing Library", "Cypress", "Accessibility (WCAG)", "Performance Optimization", "Design Systems"],
        "experience": [
            {
                "title": "Senior Frontend Engineer",
                "company": "DesignFirst Co.",
                "duration": "2022 - Present",
                "bullets": [
                    "Built company design system used by 20 engineering teams, reducing UI dev time by 35%.",
                    "Achieved Lighthouse performance score of 98+ across all product pages.",
                    "Implemented WCAG 2.1 AA compliance across entire web application.",
                ]
            },
            {
                "title": "Frontend Developer",
                "company": "UXStudio",
                "duration": "2019 - 2022",
                "bullets": [
                    "Developed Vue.js single-page applications for 10+ enterprise clients.",
                    "Reduced initial page load by 60% through code splitting and lazy loading.",
                ]
            }
        ],
        "education": [
            {"degree": "B.S. Computer Science", "school": "DePaul University", "year": "2019"},
        ],
        "years_exp": 5,
    },
    {
        "name": "Peter Kim",
        "email": "peter.kim@email.com",
        "phone": "+1-415-555-0116",
        "location": "San Francisco, CA",
        "summary": "Blockchain Developer with 5 years building decentralized applications on Ethereum, Solana, and Polygon. Expert in smart contract development, DeFi protocols, and Web3 integrations.",
        "skills": ["Solidity", "Rust", "Ethereum", "Solana", "Polygon", "Hardhat", "Truffle", "Web3.js", "Ethers.js", "DeFi", "NFTs", "Smart Contracts", "IPFS", "TypeScript", "Security Auditing"],
        "experience": [
            {
                "title": "Senior Blockchain Developer",
                "company": "DeFiCore",
                "duration": "2021 - Present",
                "bullets": [
                    "Architected and launched DeFi lending protocol with $50M+ TVL.",
                    "Conducted security audits identifying and fixing 15 critical vulnerabilities.",
                    "Built cross-chain bridge handling $100M+ in token transfers.",
                ]
            },
            {
                "title": "Smart Contract Developer",
                "company": "Web3Studio",
                "duration": "2019 - 2021",
                "bullets": [
                    "Developed and deployed 20+ ERC-20 and ERC-721 smart contracts.",
                    "Built NFT marketplace with secondary royalties handling 10K+ transactions.",
                ]
            }
        ],
        "education": [
            {"degree": "B.S. Computer Science", "school": "UC Irvine", "year": "2019"},
        ],
        "years_exp": 5,
    },
    {
        "name": "Quinn Anderson",
        "email": "quinn.anderson@email.com",
        "phone": "+1-415-555-0117",
        "location": "San Francisco, CA",
        "summary": "MLOps Engineer with 6 years building ML platforms and infrastructure. Expert in model serving, monitoring, and scalable ML systems architecture.",
        "skills": ["Python", "Kubernetes", "Docker", "MLflow", "Kubeflow", "Ray", "Seldon", "BentoML", "Prometheus", "Grafana", "Apache Airflow", "Terraform", "AWS", "Feature Stores", "Model Monitoring"],
        "experience": [
            {
                "title": "Senior MLOps Engineer",
                "company": "MLPlatform Co.",
                "duration": "2020 - Present",
                "bullets": [
                    "Built internal ML platform serving 100+ models with automated A/B testing.",
                    "Reduced model deployment time from 2 weeks to 2 hours through automation.",
                    "Implemented model drift detection reducing incidents by 80%.",
                ]
            },
            {
                "title": "ML Infrastructure Engineer",
                "company": "AIScale",
                "duration": "2018 - 2020",
                "bullets": [
                    "Developed feature store supporting 500+ features for 20 ML models.",
                    "Optimized model inference latency by 70% using ONNX and TensorRT.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Computer Science", "school": "Georgia Tech", "year": "2018"},
            {"degree": "B.S. Computer Science", "school": "UIUC", "year": "2016"},
        ],
        "years_exp": 6,
    },
    {
        "name": "Rachel Green",
        "email": "rachel.green@email.com",
        "phone": "+1-212-555-0118",
        "location": "New York, NY",
        "summary": "Database Architect and Backend Engineer with 8 years designing high-performance database systems. Expert in PostgreSQL, MongoDB, and distributed database architectures.",
        "skills": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "Python", "Java", "SQL", "Database Design", "Query Optimization", "Sharding", "Replication", "TimescaleDB", "ClickHouse"],
        "experience": [
            {
                "title": "Database Architect",
                "company": "DataSystems Inc.",
                "duration": "2019 - Present",
                "bullets": [
                    "Designed sharded PostgreSQL cluster handling 5M writes/second.",
                    "Optimized complex SQL queries reducing average query time from 30s to 200ms.",
                    "Implemented ClickHouse for analytics workloads processing 1TB/day.",
                ]
            },
            {
                "title": "Backend Engineer",
                "company": "ScaleDB",
                "duration": "2016 - 2019",
                "bullets": [
                    "Built Elasticsearch search platform indexing 100M+ documents.",
                    "Implemented database replication and failover achieving 99.99% availability.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Computer Science", "school": "NYU", "year": "2016"},
            {"degree": "B.S. Information Systems", "school": "Rutgers University", "year": "2014"},
        ],
        "years_exp": 8,
    },
    {
        "name": "Samuel Wright",
        "email": "samuel.wright@email.com",
        "phone": "+1-408-555-0119",
        "location": "Palo Alto, CA",
        "summary": "Computer Vision Engineer with 7 years building real-time vision systems for robotics and autonomous vehicles. Deep expertise in object detection, segmentation, and 3D perception.",
        "skills": ["Python", "C++", "PyTorch", "TensorFlow", "OpenCV", "YOLO", "Detectron2", "Point Clouds", "LiDAR", "SLAM", "ROS", "CUDA", "TensorRT", "3D Perception", "Autonomous Driving"],
        "experience": [
            {
                "title": "Senior Computer Vision Engineer",
                "company": "AutonomousDrive Inc.",
                "duration": "2020 - Present",
                "bullets": [
                    "Developed real-time 3D object detection for autonomous vehicles using LiDAR + camera fusion.",
                    "Improved pedestrian detection mAP from 78% to 94% through novel data augmentation.",
                    "Optimized inference pipeline with TensorRT achieving 60 FPS on embedded hardware.",
                ]
            },
            {
                "title": "Computer Vision Engineer",
                "company": "VisionTech",
                "duration": "2017 - 2020",
                "bullets": [
                    "Built defect detection system for semiconductor manufacturing with 99.5% accuracy.",
                    "Implemented semantic segmentation for medical imaging assisting radiologists.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Electrical Engineering (Computer Vision)", "school": "Stanford University", "year": "2017"},
            {"degree": "B.S. Electronics Engineering", "school": "IIT Delhi", "year": "2015"},
        ],
        "years_exp": 7,
    },
    {
        "name": "Tina Foster",
        "email": "tina.foster@email.com",
        "phone": "+1-617-555-0120",
        "location": "Boston, MA",
        "summary": "Business Intelligence Analyst with 4 years turning complex data into clear insights. Proficient in SQL, Tableau, and Python for analytics. Strong business acumen in e-commerce and retail domains.",
        "skills": ["SQL", "Python", "Tableau", "Power BI", "Excel", "Google Analytics", "A/B Testing", "Cohort Analysis", "Pandas", "Matplotlib", "Looker", "Snowflake", "BigQuery", "Statistics", "Business Intelligence"],
        "experience": [
            {
                "title": "Senior BI Analyst",
                "company": "RetailAnalytics",
                "duration": "2022 - Present",
                "bullets": [
                    "Built executive dashboards tracking $500M revenue across 50+ KPIs.",
                    "Performed cohort analysis identifying customer segments with 40% higher LTV.",
                ]
            },
            {
                "title": "Data Analyst",
                "company": "EcomInsights",
                "duration": "2020 - 2022",
                "bullets": [
                    "Analyzed customer behavior data to optimize product recommendation algorithms.",
                    "Created automated reporting reducing manual reporting effort by 15 hours/week.",
                ]
            }
        ],
        "education": [
            {"degree": "B.S. Business Analytics", "school": "Boston University", "year": "2020"},
        ],
        "years_exp": 4,
    },
    {
        "name": "Uma Krishnan",
        "email": "uma.krishnan@email.com",
        "phone": "+1-512-555-0121",
        "location": "Austin, TX",
        "summary": "Embedded Systems Engineer with 9 years designing firmware and hardware-software interfaces for IoT and automotive systems. Expert in C/C++, RTOS, and CAN bus protocols.",
        "skills": ["C", "C++", "Python", "RTOS", "FreeRTOS", "CAN bus", "SPI", "I2C", "UART", "ARM Cortex", "Linux Kernel", "Device Drivers", "AUTOSAR", "Automotive", "IoT"],
        "experience": [
            {
                "title": "Senior Embedded Engineer",
                "company": "AutoTech Systems",
                "duration": "2018 - Present",
                "bullets": [
                    "Developed AUTOSAR-compliant ECU software for electric vehicle battery management system.",
                    "Reduced boot time of embedded Linux system from 45s to 8s through kernel optimization.",
                    "Led team of 5 engineers delivering safety-critical firmware for ISO 26262 certification.",
                ]
            },
            {
                "title": "Embedded Engineer",
                "company": "IoTWorks",
                "duration": "2015 - 2018",
                "bullets": [
                    "Developed RTOS-based firmware for industrial IoT sensors.",
                    "Implemented low-power algorithms extending battery life from 1 to 5 years.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Electrical Engineering", "school": "UT Austin", "year": "2015"},
            {"degree": "B.Tech Electronics", "school": "NIT Trichy", "year": "2013"},
        ],
        "years_exp": 9,
    },
    {
        "name": "Victor Hayes",
        "email": "victor.hayes@email.com",
        "phone": "+1-206-555-0122",
        "location": "Seattle, WA",
        "summary": "QA Automation Engineer with 6 years building comprehensive test frameworks. Expert in Selenium, Playwright, and API testing. Advocate for shift-left testing and quality culture.",
        "skills": ["Python", "JavaScript", "Selenium", "Playwright", "Cypress", "JUnit", "PyTest", "Rest Assured", "Postman", "JIRA", "TestRail", "CI/CD", "Performance Testing", "JMeter", "Load Testing"],
        "experience": [
            {
                "title": "Senior QA Automation Engineer",
                "company": "QualityFirst Tech",
                "duration": "2021 - Present",
                "bullets": [
                    "Built end-to-end automation framework reducing regression testing time from 2 days to 3 hours.",
                    "Implemented API testing suite covering 500+ endpoints with 98% coverage.",
                    "Led performance testing initiative identifying bottlenecks before production launch.",
                ]
            },
            {
                "title": "QA Engineer",
                "company": "TestCraft",
                "duration": "2018 - 2021",
                "bullets": [
                    "Automated 300+ test cases using Selenium WebDriver and Python.",
                    "Reduced production defects by 60% through comprehensive test planning.",
                ]
            }
        ],
        "education": [
            {"degree": "B.S. Computer Science", "school": "University of Washington", "year": "2018"},
        ],
        "years_exp": 6,
    },
    {
        "name": "Wendy Scott",
        "email": "wendy.scott@email.com",
        "phone": "+1-415-555-0123",
        "location": "San Francisco, CA",
        "summary": "Game Developer with 5 years building immersive 3D games using Unity and Unreal Engine. Passionate about gameplay mechanics, physics simulation, and graphics optimization.",
        "skills": ["C#", "C++", "Unity", "Unreal Engine", "Blueprints", "HLSL", "Shader Programming", "3D Math", "Physics", "AI Pathfinding", "Multiplayer Networking", "Git", "Asset Pipeline", "VR/AR", "Mobile Games"],
        "experience": [
            {
                "title": "Senior Game Developer",
                "company": "PixelCraft Studios",
                "duration": "2021 - Present",
                "bullets": [
                    "Lead developer for RPG game with 500K+ downloads on Steam.",
                    "Implemented procedural world generation system creating infinite unique landscapes.",
                    "Built multiplayer netcode handling 100 concurrent players with lag compensation.",
                ]
            },
            {
                "title": "Game Developer",
                "company": "GameLab",
                "duration": "2019 - 2021",
                "bullets": [
                    "Developed mobile games achieving top-10 ranking in App Store strategy category.",
                    "Optimized rendering pipeline achieving stable 60 FPS on mid-range devices.",
                ]
            }
        ],
        "education": [
            {"degree": "B.S. Computer Science (Game Design)", "school": "DigiPen Institute", "year": "2019"},
        ],
        "years_exp": 5,
    },
    {
        "name": "Xavier Nguyen",
        "email": "xavier.nguyen@email.com",
        "phone": "+1-408-555-0124",
        "location": "San Jose, CA",
        "summary": "Generative AI Engineer with 4 years building production AI applications using LLMs, diffusion models, and RAG systems. Experienced with OpenAI, Anthropic, and open-source models.",
        "skills": ["Python", "LangChain", "LlamaIndex", "OpenAI API", "Anthropic Claude", "RAG", "Vector Databases", "ChromaDB", "Pinecone", "Weaviate", "Prompt Engineering", "Fine-tuning", "FastAPI", "Streamlit", "HuggingFace"],
        "experience": [
            {
                "title": "Generative AI Engineer",
                "company": "GenAI Ventures",
                "duration": "2022 - Present",
                "bullets": [
                    "Built enterprise RAG system processing 10M+ documents with 95% retrieval accuracy.",
                    "Developed AI code assistant reducing developer coding time by 30%.",
                    "Implemented multi-agent orchestration framework for complex task automation.",
                ]
            },
            {
                "title": "ML Engineer",
                "company": "AIStartup",
                "duration": "2020 - 2022",
                "bullets": [
                    "Fine-tuned GPT-3 models for domain-specific tasks achieving 40% improvement.",
                    "Built Stable Diffusion pipeline for automated product image generation.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Computer Science (AI)", "school": "Carnegie Mellon University", "year": "2020"},
            {"degree": "B.S. Computer Science", "school": "UC Davis", "year": "2018"},
        ],
        "years_exp": 4,
    },
    {
        "name": "Yara Collins",
        "email": "yara.collins@email.com",
        "phone": "+1-212-555-0125",
        "location": "New York, NY",
        "summary": "Site Reliability Engineer with 7 years ensuring high availability and performance of distributed systems. Expert in incident management, capacity planning, and chaos engineering.",
        "skills": ["Python", "Go", "Kubernetes", "Prometheus", "Grafana", "PagerDuty", "Chaos Engineering", "SLO/SLI/SLA", "Terraform", "AWS", "Load Balancing", "Linux", "Shell Scripting", "Distributed Systems", "Observability"],
        "experience": [
            {
                "title": "Senior SRE",
                "company": "ReliableCloud",
                "duration": "2020 - Present",
                "bullets": [
                    "Maintained 99.99% uptime for platform serving 10M+ daily active users.",
                    "Reduced MTTR from 45 minutes to 8 minutes through improved observability.",
                    "Led chaos engineering program eliminating 90% of infrastructure-related outages.",
                ]
            },
            {
                "title": "SRE",
                "company": "CloudOps",
                "duration": "2017 - 2020",
                "bullets": [
                    "Defined and maintained SLOs for 50+ production services.",
                    "Built on-call runbooks reducing resolution time for common incidents by 60%.",
                ]
            }
        ],
        "education": [
            {"degree": "B.S. Computer Science", "school": "Fordham University", "year": "2017"},
        ],
        "years_exp": 7,
    },
    {
        "name": "Zoe Harrison",
        "email": "zoe.harrison@email.com",
        "phone": "+1-206-555-0126",
        "location": "Seattle, WA",
        "summary": "Machine Learning Engineer specializing in recommendation systems and personalization with 6 years experience. Built systems serving billions of users at top tech companies.",
        "skills": ["Python", "TensorFlow", "Spark", "Collaborative Filtering", "Matrix Factorization", "Deep Learning", "Feature Engineering", "Hadoop", "Kafka", "Flink", "AWS", "Scala", "A/B Testing", "Experimentation", "SQL"],
        "experience": [
            {
                "title": "ML Engineer - Recommendations",
                "company": "StreamMax",
                "duration": "2020 - Present",
                "bullets": [
                    "Built deep learning recommendation system increasing user engagement by 25%.",
                    "Implemented two-tower neural network for candidate retrieval at billion-scale.",
                    "Designed experimentation platform running 200+ simultaneous A/B tests.",
                ]
            },
            {
                "title": "Data Scientist",
                "company": "ShopAI",
                "duration": "2018 - 2020",
                "bullets": [
                    "Developed collaborative filtering algorithms for e-commerce personalization.",
                    "Improved recommendation click-through rate by 18% through feature engineering.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Statistics", "school": "University of Washington", "year": "2018"},
            {"degree": "B.S. Mathematics", "school": "University of Michigan", "year": "2016"},
        ],
        "years_exp": 6,
    },
    {
        "name": "Aaron Mitchell",
        "email": "aaron.mitchell@email.com",
        "phone": "+1-415-555-0127",
        "location": "San Francisco, CA",
        "summary": "HR Technology Product Manager with 5 years building AI-powered talent acquisition platforms. Bridges technical and business stakeholders to deliver people analytics solutions.",
        "skills": ["Product Management", "HR Tech", "ATS Systems", "Python", "SQL", "Data Analysis", "AI/ML Concepts", "Workday", "Greenhouse", "Lever", "People Analytics", "HRIS", "API Integration", "Agile", "OKRs"],
        "experience": [
            {
                "title": "Product Manager - HR Tech",
                "company": "TalentAI",
                "duration": "2021 - Present",
                "bullets": [
                    "Launched AI-powered candidate matching feature reducing time-to-hire by 40%.",
                    "Built people analytics dashboard used by 500+ HR professionals.",
                    "Integrated 15+ ATS platforms via API partnerships.",
                ]
            },
            {
                "title": "HR Systems Analyst",
                "company": "PeopleTech",
                "duration": "2019 - 2021",
                "bullets": [
                    "Managed implementation of Workday HRIS for 5,000-employee company.",
                    "Built automated onboarding workflow reducing HR admin time by 25%.",
                ]
            }
        ],
        "education": [
            {"degree": "MBA (HR and Technology)", "school": "UC Berkeley Haas", "year": "2019"},
            {"degree": "B.S. Human Resources", "school": "Penn State University", "year": "2017"},
        ],
        "years_exp": 5,
    },
    {
        "name": "Bella Turner",
        "email": "bella.turner@email.com",
        "phone": "+1-617-555-0128",
        "location": "Cambridge, MA",
        "summary": "Robotics Software Engineer with 6 years developing autonomous systems for industrial and research robotics. Expert in motion planning, control systems, and ROS ecosystem.",
        "skills": ["Python", "C++", "ROS", "ROS2", "SLAM", "Motion Planning", "MoveIt", "Control Systems", "Computer Vision", "Gazebo", "OpenCV", "Point Clouds", "Navigation", "Manipulation", "Simulation"],
        "experience": [
            {
                "title": "Robotics Software Engineer",
                "company": "RoboSystems Inc.",
                "duration": "2020 - Present",
                "bullets": [
                    "Developed autonomous warehouse robot navigation system achieving 99.8% success rate.",
                    "Implemented SLAM algorithm reducing localization error by 60%.",
                    "Built ROS2 control stack for 6-DOF robotic arm with sub-millimeter precision.",
                ]
            },
            {
                "title": "Junior Robotics Engineer",
                "company": "AutoBot Labs",
                "duration": "2018 - 2020",
                "bullets": [
                    "Developed path planning algorithms for mobile robots in dynamic environments.",
                    "Integrated computer vision for object recognition and grasping.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Robotics", "school": "Carnegie Mellon University", "year": "2018"},
            {"degree": "B.S. Mechanical Engineering", "school": "MIT", "year": "2016"},
        ],
        "years_exp": 6,
    },
    {
        "name": "Chris Evans",
        "email": "chris.evans@email.com",
        "phone": "+1-617-555-0129",
        "location": "Boston, MA",
        "summary": "Bioinformatics Scientist with 7 years applying computational methods to genomics and drug discovery. Expert in sequence analysis, ML for biology, and large-scale genomic data pipelines.",
        "skills": ["Python", "R", "Biopython", "Nextflow", "Snakemake", "GATK", "BWA", "STAR", "DESeq2", "Pandas", "NumPy", "Bash", "HPC", "AWS", "Machine Learning for Biology"],
        "experience": [
            {
                "title": "Senior Bioinformatics Scientist",
                "company": "GenomicsTech",
                "duration": "2019 - Present",
                "bullets": [
                    "Built end-to-end genomic variant calling pipeline processing 10,000+ patient samples.",
                    "Applied ML models for cancer biomarker discovery achieving 88% sensitivity.",
                    "Reduced pipeline runtime from 72 hours to 8 hours through parallelization.",
                ]
            },
            {
                "title": "Bioinformatics Analyst",
                "company": "BioData Inc.",
                "duration": "2017 - 2019",
                "bullets": [
                    "Performed RNA-seq analysis for 50+ clinical studies.",
                    "Developed automated quality control pipeline for NGS data.",
                ]
            }
        ],
        "education": [
            {"degree": "Ph.D. Computational Biology", "school": "Harvard University", "year": "2017"},
            {"degree": "B.S. Bioinformatics", "school": "UC Santa Cruz", "year": "2012"},
        ],
        "years_exp": 7,
    },
    {
        "name": "Diana Foster",
        "email": "diana.foster@email.com",
        "phone": "+1-404-555-0130",
        "location": "Atlanta, GA",
        "summary": "Junior Data Scientist with 2 years experience in machine learning and data analysis. Eager to apply Python, sklearn, and deep learning skills to solve real-world problems.",
        "skills": ["Python", "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Seaborn", "TensorFlow", "SQL", "Jupyter", "Git", "Statistics", "Linear Algebra", "Machine Learning", "Data Visualization", "Excel"],
        "experience": [
            {
                "title": "Junior Data Scientist",
                "company": "DataStart Inc.",
                "duration": "2023 - Present",
                "bullets": [
                    "Built classification models for customer churn prediction with 85% accuracy.",
                    "Created data visualization dashboards for business stakeholders.",
                ]
            },
            {
                "title": "Data Science Intern",
                "company": "Analytics Hub",
                "duration": "Summer 2022",
                "bullets": [
                    "Cleaned and preprocessed 500K+ records for ML model training.",
                    "Implemented regression models for price prediction.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Data Science", "school": "Georgia Tech", "year": "2023"},
            {"degree": "B.S. Statistics", "school": "University of Georgia", "year": "2021"},
        ],
        "years_exp": 2,
    },
    {
        "name": "Ethan Brooks",
        "email": "ethan.brooks@email.com",
        "phone": "+1-512-555-0131",
        "location": "Austin, TX",
        "summary": "Software Architect with 14 years designing complex enterprise systems. Expert in distributed systems, domain-driven design, and event-driven architectures.",
        "skills": ["Java", "Spring Boot", "Scala", "Kafka", "gRPC", "REST", "Microservices", "DDD", "CQRS", "Event Sourcing", "PostgreSQL", "Redis", "AWS", "Design Patterns", "System Design"],
        "experience": [
            {
                "title": "Principal Software Architect",
                "company": "Enterprise Systems Corp",
                "duration": "2016 - Present",
                "bullets": [
                    "Architected event-driven microservices platform handling 100M daily transactions.",
                    "Led migration from monolith to microservices for 3M-user enterprise application.",
                    "Established engineering standards and best practices across 10 development teams.",
                ]
            },
            {
                "title": "Senior Software Engineer",
                "company": "TechGiant",
                "duration": "2010 - 2016",
                "bullets": [
                    "Designed distributed caching layer reducing database load by 70%.",
                    "Built real-time messaging system using Kafka handling 50K messages/second.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Computer Science", "school": "UT Austin", "year": "2010"},
            {"degree": "B.S. Computer Science", "school": "Texas Tech University", "year": "2008"},
        ],
        "years_exp": 14,
    },
    {
        "name": "Fiona Campbell",
        "email": "fiona.campbell@email.com",
        "phone": "+1-312-555-0132",
        "location": "Chicago, IL",
        "summary": "Marketing Analytics Manager with 5 years leveraging data to drive marketing performance. Expert in attribution modeling, customer segmentation, and digital marketing analytics.",
        "skills": ["SQL", "Python", "Google Analytics", "Google Ads", "Facebook Ads", "Tableau", "Looker", "Attribution Modeling", "Customer Segmentation", "Email Marketing", "SEO/SEM", "CRM", "Salesforce", "HubSpot", "A/B Testing"],
        "experience": [
            {
                "title": "Marketing Analytics Manager",
                "company": "GrowthMarketing Co.",
                "duration": "2021 - Present",
                "bullets": [
                    "Built multi-touch attribution model improving marketing ROI by 35%.",
                    "Created customer segmentation model increasing email conversion rate by 28%.",
                    "Managed $5M monthly paid media budget achieving 320% ROAS.",
                ]
            },
            {
                "title": "Digital Marketing Analyst",
                "company": "DigitalFirst",
                "duration": "2019 - 2021",
                "bullets": [
                    "Optimized Google Ads campaigns reducing CPA by 40%.",
                    "Implemented Google Analytics 4 migration with custom event tracking.",
                ]
            }
        ],
        "education": [
            {"degree": "M.S. Marketing Analytics", "school": "Northwestern University", "year": "2019"},
            {"degree": "B.S. Business Administration", "school": "University of Illinois", "year": "2017"},
        ],
        "years_exp": 5,
    },
    {
        "name": "George Rivera",
        "email": "george.rivera@email.com",
        "phone": "+1-415-555-0133",
        "location": "San Francisco, CA",
        "summary": "AI Product Engineer with 3 years building LLM-powered products. Specialist in prompt engineering, RAG architectures, and AI agent systems. Experienced with GPT-4, Claude, and Gemini.",
        "skills": ["Python", "Prompt Engineering", "LangChain", "LlamaIndex", "OpenAI", "Anthropic", "Gemini", "Vector Databases", "RAG", "AI Agents", "FastAPI", "Streamlit", "React", "TypeScript", "SQL"],
        "experience": [
            {
                "title": "AI Product Engineer",
                "company": "AIProducts Inc.",
                "duration": "2022 - Present",
                "bullets": [
                    "Built customer-facing AI assistant handling 50K daily conversations.",
                    "Designed RAG pipeline improving answer accuracy from 65% to 91%.",
                    "Implemented multi-agent system automating complex research workflows.",
                ]
            },
            {
                "title": "Software Engineer",
                "company": "TechStartup",
                "duration": "2021 - 2022",
                "bullets": [
                    "Developed Python backends for AI-powered SaaS products.",
                    "Implemented real-time streaming responses using SSE and WebSockets.",
                ]
            }
        ],
        "education": [
            {"degree": "B.S. Computer Science", "school": "UCLA", "year": "2021"},
        ],
        "years_exp": 3,
    },
    {
        "name": "Helen Adams",
        "email": "helen.adams@email.com",
        "phone": "+1-214-555-0134",
        "location": "Dallas, TX",
        "summary": "Network Engineer with 12 years designing and maintaining enterprise and data center networks. Cisco CCIE certified. Expert in SD-WAN, BGP, and network security.",
        "skills": ["Cisco IOS", "BGP", "OSPF", "MPLS", "SD-WAN", "VPN", "Firewall", "Palo Alto", "Juniper", "Python", "Ansible", "CCIE", "Network Security", "Data Center Networking", "Wireless"],
        "experience": [
            {
                "title": "Principal Network Engineer",
                "company": "NetworkPro Corp",
                "duration": "2017 - Present",
                "bullets": [
                    "Designed and deployed SD-WAN solution across 200+ branch offices.",
                    "Architected data center network with 400G spine-leaf topology.",
                    "Automated network provisioning reducing deployment time from days to minutes.",
                ]
            },
            {
                "title": "Senior Network Engineer",
                "company": "TelecomGiant",
                "duration": "2012 - 2017",
                "bullets": [
                    "Managed BGP routing for 50Gbps internet peering infrastructure.",
                    "Implemented MPLS VPN for enterprise clients achieving 99.99% uptime.",
                ]
            }
        ],
        "education": [
            {"degree": "B.S. Network Engineering", "school": "University of Texas", "year": "2012"},
        ],
        "years_exp": 12,
    },
    {
        "name": "Ivan Stone",
        "email": "ivan.stone@email.com",
        "phone": "+1-404-555-0135",
        "location": "Atlanta, GA",
        "summary": "Recent Computer Science graduate with strong foundation in algorithms, data structures, and software development. Completed internships in backend development and data engineering.",
        "skills": ["Python", "Java", "C++", "SQL", "Git", "React", "Node.js", "PostgreSQL", "Docker", "Data Structures", "Algorithms", "REST APIs", "Agile", "Linux", "AWS"],
        "experience": [
            {
                "title": "Software Engineering Intern",
                "company": "BigTech Corp",
                "duration": "Summer 2024",
                "bullets": [
                    "Built REST API endpoints in Java Spring Boot serving 10K+ users.",
                    "Wrote unit tests achieving 90% code coverage for assigned components.",
                ]
            },
            {
                "title": "Data Engineering Intern",
                "company": "DataStartup",
                "duration": "Summer 2023",
                "bullets": [
                    "Developed Python ETL scripts to process 1M+ records daily.",
                    "Contributed to Apache Airflow DAG development.",
                ]
            }
        ],
        "education": [
            {"degree": "B.S. Computer Science", "school": "Georgia Institute of Technology", "year": "2024"},
        ],
        "years_exp": 1,
    },
]


# ─── PDF Generation ───────────────────────────────────────────────────────────

def build_styles():
    styles = getSampleStyleSheet()
    name_style = ParagraphStyle(
        "CandidateName",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=2,
        alignment=TA_CENTER,
    )
    contact_style = ParagraphStyle(
        "Contact",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#555555"),
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=11,
        textColor=colors.HexColor("#16213e"),
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#333333"),
        spaceAfter=3,
        leading=13,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#333333"),
        leftIndent=15,
        spaceAfter=2,
        leading=13,
    )
    job_title_style = ParagraphStyle(
        "JobTitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#0f3460"),
        fontName="Helvetica-Bold",
        spaceAfter=1,
    )
    return {
        "name": name_style,
        "contact": contact_style,
        "section_header": section_header_style,
        "body": body_style,
        "bullet": bullet_style,
        "job_title": job_title_style,
    }


def create_resume_pdf(candidate: dict, output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )
    styles = build_styles()
    story = []

    # Header
    story.append(Paragraph(candidate["name"], styles["name"]))
    story.append(
        Paragraph(
            f"{candidate['email']}  |  {candidate['phone']}  |  {candidate['location']}",
            styles["contact"],
        )
    )
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1a1a2e")))
    story.append(Spacer(1, 6))

    # Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", styles["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 4))
    story.append(Paragraph(candidate["summary"], styles["body"]))

    # Skills
    story.append(Paragraph("SKILLS", styles["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 4))
    skills_text = "  |  ".join(candidate["skills"])
    story.append(Paragraph(skills_text, styles["body"]))

    # Experience
    story.append(Paragraph("PROFESSIONAL EXPERIENCE", styles["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 4))
    for exp in candidate["experience"]:
        story.append(
            Paragraph(
                f"<b>{exp['title']}</b> - {exp['company']}  ({exp['duration']})",
                styles["job_title"],
            )
        )
        for bullet in exp["bullets"]:
            story.append(Paragraph(f"- {bullet}", styles["bullet"]))
        story.append(Spacer(1, 4))

    # Education
    story.append(Paragraph("EDUCATION", styles["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 4))
    for edu in candidate["education"]:
        story.append(
            Paragraph(
                f"<b>{edu['degree']}</b> | {edu['school']} ({edu['year']})",
                styles["body"],
            )
        )

    doc.build(story)
    print(f"  Generated: {output_path.name}")


def main():
    print(f"\nGenerating {len(CANDIDATES)} resume PDFs into '{OUTPUT_DIR}/'")
    for candidate in CANDIDATES:
        safe_name = candidate["name"].lower().replace(" ", "_")
        output_path = OUTPUT_DIR / f"{safe_name}.pdf"
        create_resume_pdf(candidate, output_path)
    print(f"\nDone! {len(CANDIDATES)} resumes saved to '{OUTPUT_DIR}/'")


if __name__ == "__main__":
    main()
