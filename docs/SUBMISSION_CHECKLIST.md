# Darukaa.Earth — Submission Checklist & Reviewer Guide

## 1. Project & Repository Links

* **GitHub Repository**: `[INSERT_GITHUB_REPOSITORY_URL_HERE]`
* **Live Demo / Deployment**: `[INSERT_LIVE_DEMO_URL_HERE]` (or run locally per instructions below)
* **Hackathon Track**: AI for Biodiversity & Climate Resilience / Environmental Intelligence

---

## 2. Environment & Service Startup

### A. Ollama LLM Setup
1. Install [Ollama](https://ollama.ai/).
2. Pull the required model:
   ```bash
   ollama pull mistral:7b
   ```
3. Ensure Ollama service is running:
   ```bash
   # Default URL: http://localhost:11434
   curl http://localhost:11434/api/tags
   ```
   *Note: If Ollama is not running, the application automatically falls back to deterministic scientific Demo Mode without crashing.*

### B. Backend Startup
```bash
cd backend
python -m venv .venv

# Activate venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt

# Populate SQLite DB and ingest 25 ChromaDB evidence records
python scripts/seed_database.py
python scripts/ingest_knowledge.py

# Launch FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### C. Frontend Startup
```bash
cd frontend
npm install
npm run build
npm run start
# Server runs on http://localhost:3000
```

---

## 3. Verification Commands

### Automated Test Suite (27/27 Passing)
Tests execute with a mocked Ollama provider so CI/CD does not require a live GPU/LLM daemon:
```bash
cd backend
python -m pytest tests/ -v
```
Expected output:
```
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_system_status PASSED
tests/test_extractor.py::test_extract_environmental_profile PASSED
tests/test_extractor.py::test_detect_user_intent PASSED
tests/test_extractor.py::test_soc_variants PASSED
tests/test_extractor.py::test_no_monoculture_from_wheat_farm PASSED
tests/test_extractor.py::test_full_sentence_extraction PASSED
tests/test_llm.py::test_prompt_contains_environmental_profile PASSED
tests/test_llm.py::test_prompt_contains_retrieved_evidence PASSED
tests/test_llm.py::test_prompt_contains_reasoning_context PASSED
tests/test_llm.py::test_system_prompt_includes_no_hallucination_rules PASSED
tests/test_llm.py::test_system_prompt_requires_multi_stressor_reasoning PASSED
tests/test_llm.py::test_structured_output_parsing PASSED
tests/test_llm.py::test_malformed_json_returns_empty PASSED
tests/test_llm.py::test_unsupported_citations_are_rejected PASSED
tests/test_llm.py::test_valid_citations_are_kept PASSED
tests/test_llm.py::test_hallucinated_numerical_claims_not_in_schema PASSED
tests/test_llm.py::test_ollama_unavailable_fallback PASSED
tests/test_llm.py::test_ollama_available_selected PASSED
tests/test_llm.py::test_ollama_parse_failure_falls_back PASSED
tests/test_missing_info.py::test_missing_info_for_biodiversity PASSED
tests/test_missing_info.py::test_complete_profile_no_clarification PASSED
tests/test_reasoning.py::test_reasoning_engine PASSED
tests/test_reasoning.py::test_biodiversity_reasoning PASSED
tests/test_retrieval.py::test_retrieval_soil_organic_carbon PASSED
tests/test_retrieval.py::test_retrieval_wheat_monoculture PASSED
tests/test_retrieval.py::test_retrieval_low_rainfall PASSED
======================= 27 passed, 4 warnings in ~15s =======================
```

### Frontend Code Quality
```bash
cd frontend
npm run lint    # Zero ESLint warnings or errors
npm run build   # Production compile passes
```

---

## 4. Key Verification Scenarios for Reviewers

### Standard Benchmark Query
Input:
> *"My wheat farm in Maharashtra has low rainfall and I noticed biodiversity declining. Soil organic carbon is only 0.3%. What should I do?"*

Expected Verification Results:
1. **Header Badge**: Displays `Ollama LLM Active` (green brain badge) when connected to local Ollama; `Demo Mode Active` (yellow) if Ollama is offline.
2. **Context Profile Extraction**:
   * `region`: Maharashtra
   * `soil.organic_carbon_percent`: 0.3% (correctly extracted from natural language)
   * `land_use.crop`: wheat
   * `land_use.cropping_system`: Missing (system strictly avoids false monoculture inference)
   * `climate.rainfall_pattern`: low
   * `biodiversity.species_richness` / `habitat_diversity`: low
3. **Multi-Metric Interventions**:
   * Generates actionable recommendations such as drought-tolerant legume cover cropping, agroforestry buffers, and in-situ water harvesting.
   * Impacts metrics like `soil_organic_carbon`, `water_retention`, and `biodiversity`.
4. **Scientific Grounding**:
   * Supporting evidence quotes authentic publications from FAO, CIFOR, ICAR, etc.
   * Evidence drawer displays source, year, topic, variables, and excerpt.
5. **Calibrated Confidence**:
   * Assigned `Medium` confidence due to missing baseline variables (soil pH, moisture, cropping history).

---

## 5. Known Limitations & Reviewer Notes

1. **Hardware / LLM Inference Time**: Running `mistral:7b` locally on CPU or mid-tier hardware typically requires 20–45 seconds per response. Ensure client timeout is at least 120 seconds (set in `.env`).
2. **Docker Environment**: Docker configuration files (`docker-compose.yml`, `Dockerfile`) are included, but were not tested in environments where Docker daemon was unavailable. Bare-metal local execution is the tested and verified deployment mode.
3. **No Paid APIs**: The application is completely functional without any paid cloud LLM credentials (OpenAI/Anthropic/Gemini).
4. **Strict Evidence Ingestion**: ChromaDB holds 25 curated, non-fabricated scientific records. If a new domain is introduced, additional documents can be added to `backend/data/seed/evidence_records.json` and re-indexed.
