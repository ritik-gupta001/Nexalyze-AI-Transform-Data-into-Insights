# Nexalyze AI

AI-Powered Research & Automation Platform

## Overview

Nexalyze AI is an autonomous multi-agent research and automation platform that leverages LLMs, machine learning, and data processing tools to provide:
- Real-time news analysis and sentiment forecasting
- Document (PDF/DOCX/TXT) summarization and insight extraction
- Data (CSV/Excel) analysis, anomaly detection, and trend forecasting
- Automated report generation and visualization

## Architecture

- **Backend:** FastAPI (REST API), SQLAlchemy ORM, SQLite database
- **Frontend:** HTML5, CSS3, JavaScript (with Canvas effects)
- **AI/ML:** OpenAI LLM (via LangChain), custom ML models (scikit-learn), forecasting (linear regression)
- **File Storage:** Local for uploads, reports, and charts
- **Reports:** Generated in Markdown, PDF, and DOCX formats

### Key Modules
- `app/main.py`: FastAPI app, static file serving, API routing
- `app/api/routes_tasks.py`: Endpoints for text, document, and data analysis tasks
- `app/services/agent_orchestrator.py`: Orchestrates multi-step tasks using LLMs, ML, and tools
- `app/ml/`: Sentiment analysis and forecasting models
- `app/genai/llm_client.py`: OpenAI/LLM integration for task interpretation and planning
- `app/db/`: SQLAlchemy models and DB session management
- `app/core/`: Configuration and logging

## Features

- **News Analysis:** Real-time scraping, LLM-based task planning, ML sentiment scoring, trend forecasting
- **Document Analysis:** PDF/DOCX/TXT upload, LLM summarization, insight extraction
- **Data Analysis:** CSV/Excel upload, ML/statistical analysis, forecasting, visualization
- **Report Generation:** Automated Markdown/PDF/DOCX reports, downloadable from `/reports`
- **Visualization:** Chart generation for trends, sentiment, and data insights
- **Task Management:** Track status/results of all analysis tasks via API

## API Usage

### Analyze Text/News
`POST /api/v1/tasks/analyze-text`
```json
{
  "query": "Analyze recent news about Tesla and predict sentiment trend",
  "entity": "Tesla",
  "time_range": "last_7_days"
}
```

### Analyze Document
`POST /api/v1/tasks/analyze-doc` (multipart/form-data)
- Upload PDF/DOCX/TXT and provide instructions (e.g., "Summarize key findings")

### Analyze Data
`POST /api/v1/tasks/analyze-data` (multipart/form-data)
- Upload CSV/Excel and provide instructions (e.g., "Predict sales trends")

### Get Task Result
`GET /api/v1/tasks/{task_id}`

### List Tasks
`GET /api/v1/tasks/`

## Setup & Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Start the application:**
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
3. **Open your browser:** [http://127.0.0.1:8000](http://127.0.0.1:8000)

## File Structure
```
app/
  main.py
  api/
  core/
  db/
  genai/
  ml/
  models/
  services/
  static/
  templates/
data/
logs/
models/
tests/
uploads/
```

## Requirements
- Python 3.9+
- See `requirements.txt` for all dependencies

## Contributing
Pull requests are welcome! Please open an issue to discuss major changes.

## License
MIT License
