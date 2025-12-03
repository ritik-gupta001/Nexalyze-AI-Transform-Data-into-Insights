# Nexanalyze AI - Transform Data Into Insights

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An autonomous multi-agent AI platform for intelligent research, data analysis, and automated insights generation.

## 🌟 Overview

Nexalyze AI is a cutting-edge research and automation platform that combines the power of Large Language Models (LLMs), Machine Learning, and advanced data processing to deliver:

📰 **Real-time News Analysis** - Scrape, analyze, and predict sentiment trends  
📄 **Document Intelligence** - Extract insights from PDFs, DOCX, and text files  
📊 **Data Analytics** - Discover patterns, anomalies, and forecasts from CSV/Excel data  
📝 **Automated Reporting** - Generate professional reports in Markdown, PDF, and DOCX formats  
📈 **Smart Visualizations** - Create interactive charts and graphs automatically

---

## 🌐 Live Demo

🚀 **Deployed on Koyeb:** possible-kessiah-ritikworkshop-f00d1514.koyeb.app/

---

## 🔍 Key Features

### 🎨 Intelligent Analysis
- **Multi-Agent Architecture**: Orchestrated AI agents for complex task decomposition
- **LLM-Powered Insights**: Uses OpenAI GPT models via LangChain for deep analysis
- **ML Sentiment Analysis**: Custom scikit-learn models for accurate sentiment scoring
- **Trend Forecasting**: Statistical models for predicting future trends

### 📁 Multi-Format Support
- **Documents**: PDF, DOCX, TXT
- **Data Files**: CSV, Excel (XLSX, XLS)
- **Web Content**: Real-time news scraping and analysis

### 📊 Advanced Analytics
- Statistical analysis and distribution analysis
- Correlation detection
- Anomaly detection
- Time series forecasting
- Sentiment trend prediction

### 📋 Professional Outputs
- **Reports**: Markdown, PDF, DOCX formats
- **Visualizations**: Sentiment charts, trend graphs, correlation matrices, distribution plots
- **Task Tracking**: Complete task history with downloadable artifacts

---

## 🧠 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                      │
├─────────────────────────────────────────────────────────┤
│  REST API  │  WebSocket  │  Static Files  │  Templates  │
├─────────────────────────────────────────────────────────┤
│              Agent Orchestrator (LangChain)             │
├─────────────┬──────────────┬────────────────────────────┤
│ News Scraper │  Doc Parser  │  Data Analyzer  │  LLM   │
├─────────────┼──────────────┼─────────────────────────────┤
│         ML Models (Sentiment, Forecasting)              │
├─────────────────────────────────────────────────────────┤
│            SQLite Database (Task Storage)               │
└─────────────────────────────────────────────────────────┘
```

### Tech Stack
- **Backend**: FastAPI, Python 3.10+
- **AI/ML**: OpenAI GPT, LangChain, scikit-learn, PyTorch
- **Database**: SQLAlchemy ORM with SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Koyeb (Docker-compatible)

---

## 📦 Prerequisites

- Python 3.10 or higher
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))
- pip package manager

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/ritik-gupta001/NexanalyzeAI--Transform-Data-Into-Insights.git
cd NexanalyzeAI--Transform-Data-Into-Insights
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
APP_NAME=Nexalyze AI
APP_VERSION=1.0.0
ENVIRONMENT=development

# Server Configuration
HOST=0.0.0.0
PORT=8000

# API Configuration
API_V1_PREFIX=/api/v1

# Database (SQLite)
DATABASE_URL=sqlite:///./pra_database.db
```

### 5. Run the Application
```bash
# Development mode with auto-reload
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6. Access the Application
- **Web UI**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs
- **OpenAPI**: http://127.0.0.1:8000/redoc

---

## 📚 API Documentation

### Endpoints

#### ✅ Health Check
```http
GET /api/v1/health
```

#### 📰 Analyze Text/News
```http
POST /api/v1/tasks/analyze-text
Content-Type: application/json

{
  "query": "Analyze recent news about Tesla and predict sentiment trend",
  "entity": "Tesla",
  "time_range": "last_7_days"
}
```

#### 📄 Analyze Document
```http
POST /api/v1/tasks/analyze-doc
Content-Type: multipart/form-data

file: <PDF/DOCX/TXT file>
instruction: "Summarize key findings and recommendations"
```

#### 📊 Analyze Data
```http
POST /api/v1/tasks/analyze-data
Content-Type: multipart/form-data

file: <CSV/Excel file>
instruction: "Find patterns and predict future trends"
```

#### 📦 Get Task Status
```http
GET /api/v1/tasks/{task_id}
```

#### 📋 List All Tasks
```http
GET /api/v1/tasks/?page=1&page_size=10
```

### Response Format
```json
{
  "task_id": "T-20241201-abc123",
  "status": "completed",
  "summary": "Analysis completed successfully...",
  "sentiment_summary": {
    "overall": "positive",
    "positive": 0.65,
    "neutral": 0.25,
    "negative": 0.10
  },
  "forecast": "Sentiment is predicted to remain positive over the next 7 days",
  "report_url": "/reports/T-20241201-abc123-report.md",
  "charts": [
    "/charts/T-20241201-abc123-sentiment.png",
    "/charts/T-20241201-abc123-trend.png"
  ],
  "created_at": "2024-12-01T10:00:00",
  "completed_at": "2024-12-01T10:05:30"
}
```

---

## 🌐 Deployment

### 🚀 Deploy to Koyeb

Koyeb provides fast, reliable deployment with generous free tier.

#### Quick Deploy

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to Koyeb"
   git push origin main
   ```

2. **Deploy on Koyeb**
   - Visit: possible-kessiah-ritikworkshop-f00d1514.koyeb.app/
   - Click **"Create App"**
   - Select **"GitHub"** as deployment method
   - Choose your repository: `NexanalyzeAI--Transform-Data-Into-Insights`
   - Branch: `main`

3. **Configure Deployment**
   - **Builder**: Docker
   - **Dockerfile**: `Dockerfile` (auto-detected)
   - **Port**: `8000`
   - **Instance Type**: Free (Eco)

4. **Environment Variables**
   Click **"Add Variable"** for each:
   - `OPENAI_API_KEY` = Your OpenAI API key
   - `ENVIRONMENT` = `production`
   - `DATABASE_URL` = `sqlite:///./pra_database.db`

5. **Deploy**
   - Click **"Deploy"**
   - Wait 2-3 minutes for build
   - Access your app at: `https://your-app-name.koyeb.app`

#### Health Check
- Visit: `https://your-app-name.koyeb.app/api/v1/health`
- API Docs: `https://your-app-name.koyeb.app/docs`

---


## 📁 Project Structure

```
nexalyze-ai/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── api/
│   │   ├── routes_health.py       # Health check endpoints
│   │   └── routes_tasks.py        # Task management endpoints
│   ├── core/
│   │   ├── config.py              # Configuration management
│   │   └── logger.py              # Logging setup
│   ├── db/
│   │   ├── base.py                # Database engine and session
│   │   ├── models.py              # SQLAlchemy models
│   │   └── init_db.py             # Database initialization
│   ├── genai/
│   │   ├── llm_client.py          # OpenAI/LangChain integration
│   │   └── prompts.py             # LLM prompt templates
│   ├── ml/
│   │   ├── sentiment_ml.py        # ML-based sentiment analysis
│   │   ├── sentiment_dl.py        # Deep learning sentiment (optional)
│   │   └── forecast_model.py      # Forecasting models
│   ├── services/
│   │   ├── agent_orchestrator.py  # Multi-agent task orchestration
│   │   ├── tools_news.py          # News scraping tools
│   │   ├── tools_docs.py          # Document processing tools
│   │   ├── tools_data.py          # Data analysis tools
│   │   ├── tools_visualization.py # Chart generation
│   │   └── tools_report.py        # Report generation
│   ├── models/
│   │   └── schemas_tasks.py       # Pydantic schemas
│   ├── static/
│   │   ├── style.css              # Frontend styles
│   │   └── app.js                 # Frontend JavaScript
│   ├── templates/
│   │   └── index.html             # Web UI template
│   ├── charts/                    # Generated charts (gitignored)
│   └── reports/                   # Generated reports (gitignored)
├── data/                          # Data files (gitignored)
├── logs/                          # Application logs (gitignored)
├── models/                        # Trained ML models
├── uploads/                       # Uploaded files (gitignored)
├── tests/
│   ├── test_api.py                # API tests
│   └── test_ml.py                 # ML model tests
├── examples/
│   └── usage_example.py           # API usage examples
├── .env                           # Environment variables (create this)
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Python dependencies
├── runtime.txt                    # Python version for Render
├── render.yaml                    # Render deployment config
└── README.md                      # This file
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py
```

---

## 📋 Example Usage

Check out `examples/usage_example.py` for comprehensive API usage examples:

```bash
python examples/usage_example.py
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Ritik Gupta**

- GitHub: [@ritik-gupta001](https://github.com/ritik-gupta001)
- Repository: [NexanalyzeAI--Transform-Data-Into-Insights](https://github.com/ritik-gupta001/NexanalyzeAI--Transform-Data-Into-Insights)

---

## 🙏 Acknowledgments

- OpenAI for GPT models
- FastAPI team for the amazing framework
- LangChain for LLM orchestration tools
- The open-source community

---

## 💬 Support

For support, please open an issue on GitHub or contact through the repository.





