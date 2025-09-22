# clone the repo
```
git@github.com:smtaidev/uprankedmarting_neuro_night_backend_1.git
```

# create the .env file
```
OPENAI_API_KEY=
MONGODB_URL=
DATABASE_NAME=uprankedmartin-calling
CHROMADB_PATH=./vector_db

```

# Start Docker Engie

# run the dockerfile
```
docker-compose up --build
```
LeadGeneration
├── api
├   ├── __init__.py
├   ├── endpoints.py
├   └── models.py
├── core
├   ├── __init__.py
├   ├── circuit_breaker.py
├   ├── config.py
├   ├── database.py
├   └── rate_limiter.py
├── services
├   ├── __init__.py
├   ├── ai_allm.py
├   ├── qa_retrieval_service.py
├   ├── rag_services.py
├   └── vector_service.py
├── vector_db
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                               
├── .gitignore
└── README.md

├── vector_db
├   ├── 7bb7d07d-fc32-4ba1-b01f-75a4b7309b09
├   ├──  ├── data_level0.bin
├   ├──  ├── header.bin
├   ├──  ├── length.bin
├   ├──  └── link_lists.bin
├   ├── 47ff5ea9-6dba-4062-99d2-8d20dbd53151
├   ├──  ├── data_level0.bin
├   ├──  ├── header.bin
├   ├──  ├── length.bin
├   ├──  └── link_lists.bin

```