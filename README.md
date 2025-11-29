# 🎓 Educational Personalized Learning Coach

> **Multi-Agent AI System** built with Google ADK for the Kaggle AI Agents Competition

A comprehensive educational platform demonstrating advanced agent orchestration with **Google ADK**, featuring two intelligent personas: a Student Practice Coach and a Teacher Analytics Assistant.

---

## 🌟 Features & ADK Capabilities Demonstrated

| Capability | Implementation |
|------------|----------------|
| **Multi-Agent Orchestration** | Root agents delegate to specialized sub-agents |
| **LlmAgent** | All agents use Gemini models for reasoning |
| **ParallelAgent** | Data fetching runs 3 sub-agents concurrently |
| **SequentialAgent** | Analysis pipeline processes data in order |
| **LoopAgent** | Curriculum optimizer iterates until valid |
| **AgentTool** | Sub-agents wrapped as callable tools |
| **Function Tools** | Question bank, database operations |
| **MCP Server** | Mastery calculation as external service |
| **A2A Protocol** | CrewAI RAG agent connected via A2A |
| **Session Memory** | Persistent sessions with DatabaseSessionService |
| **Long-Term Memory** | load_memory for returning student recognition |
| **Google Search** | Hint provider uses web search for help |

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Port 3000)                               │
│                      HTML + JavaScript + Tailwind CSS                        │
├─────────────────────────────────────────────────────────────────────────────┤
│   Landing Page  →  Student Chat Interface  |  Teacher Dashboard + Chat      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ADK WEB SERVER (Port 8000)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────┐              ┌──────────────────────────────────┐  │
│  │    STUDENT FLOW     │              │         TEACHER FLOW             │  │
│  │                     │              │                                  │  │
│  │  StudentPractice    │              │  TeacherAnalysis                 │  │
│  │  Coordinator        │              │  Coordinator                     │  │
│  │  (root_agent)       │              │  (root_agent)                    │  │
│  │        │            │              │        │                         │  │
│  │  ┌─────┼─────┐      │              │  ┌─────┼─────┬─────┐             │  │
│  │  ▼     ▼     ▼      │              │  ▼     ▼     ▼     ▼             │  │
│  │ Q.Pre Hint  Resp    │              │ Data  Analy Curri Report        │  │
│  │ senter vider lector │              │ Fetch sis   culum  Gen          │  │
│  └─────────────────────┘              └──────────────────────────────────┘  │
│                                                      │                       │
└──────────────────────────────────────────────────────│───────────────────────┘
                                                       │ A2A Protocol
                                                       ▼
                                       ┌───────────────────────────────┐
                                       │  CREWAI RAG AGENT (Port 10010)│
                                       │  PDF Textbook Search          │
                                       │  Google Embeddings            │
                                       └───────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google API Key (Gemini)

### 1. Clone & Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

Create `.env` file in project root:
```
GOOGLE_API_KEY=your_api_key_here
```

### 3. Run All Services

```bash
chmod +x start-all.sh
./start-all.sh
```

This starts:
- **Frontend** on http://localhost:3000
- **ADK API** on http://localhost:8000
- **A2A RAG Agent** on http://localhost:10010

### 4. Open in Browser

Go to **http://localhost:3000**

---

## 🎮 How to Use

### Student Mode
1. Click **Student** on landing page
2. Enter your name
3. Chat with the agent:
   - *"I want to practice Fractions, 3 questions"*
   - Answer questions, get hints if needed
   - Track your score

### Teacher Mode
1. Click **Teacher** on landing page
2. Enter your name
3. Query the assistant:
   - *"Show me weak topics for students"*
   - *"Search the textbook for fraction addition methods"*
   - *"Create a curriculum plan for struggling students"*

---

## 📁 Project Structure

```
Kaggle_Project/
├── .env                    # API keys (create this)
├── requirements.txt        # Python dependencies
├── start-all.sh           # Start all services
├── README.md              # This file
│
├── frontend/              # Web UI
│   ├── index.html         # Landing page
│   ├── student.html       # Student interface
│   ├── teacher.html       # Teacher dashboard
│   └── js/app.js          # API client
│
└── agents/                # ADK agents
    ├── student_flow/      # Student practice system
    │   ├── agent.py       # Root agent (memory-enabled)
    │   ├── sub_agents/    # Question, Hint, Response agents
    │   ├── tools/         # Question bank, DB writer
    │   └── data/          # Session database
    │
    └── Teacher_Flow/      # Teacher analytics system
        ├── agent.py       # Root agent
        ├── sub_agents/    # 4 workflow agents, 10 leaf agents
        ├── tools/         # Analytics, MCP server
        ├── a2a_rag_agent/ # CrewAI PDF search agent
        └── a2a_integration/ # A2A protocol connection
```

---

## 🛠️ Technologies

| Component | Technology |
|-----------|------------|
| **AI Framework** | Google ADK 1.2.1+ |
| **LLM** | Gemini 2.0/2.5 Flash |
| **A2A Agent** | CrewAI with PDFSearchTool |
| **Embeddings** | Google embedding-001 |
| **Database** | SQLite |
| **Frontend** | HTML, JavaScript, Tailwind CSS |
| **API** | FastAPI (via ADK) |

---

## 🔧 Manual Service Control

```bash
# Start individual services
source venv/bin/activate

# A2A RAG Agent
cd agents/Teacher_Flow && python -m a2a_rag_agent

# ADK Web Server
adk web --session_service_uri="sqlite:///agents/student_flow/data/student_sessions.db" --allow_origins="http://localhost:3000" agents/

# Frontend
cd frontend && python -m http.server 3000

# Stop all
pkill -f "adk web"; pkill -f "a2a_rag_agent"; pkill -f "http.server 3000"
```

---

## 📊 Agent Details

### Student Flow Agents
| Agent | Type | Purpose |
|-------|------|---------|
| StudentPracticeCoordinator | LlmAgent | Orchestrates practice sessions |
| QuestionPresenter | LlmAgent | Fetches and presents questions |
| HintProvider | LlmAgent | Provides hints using Google Search |
| ResponseCollector | LlmAgent | Records answers to database |

### Teacher Flow Agents
| Agent | Type | Purpose |
|-------|------|---------|
| TeacherAnalysisCoordinator | LlmAgent | Routes to appropriate workflow |
| DataFetcher | ParallelAgent | Fetches data from 3 sources |
| AnalysisPipeline | SequentialAgent | Scores → Patterns → Mastery |
| CurriculumOptimizer | LoopAgent | Generates valid curriculum |
| ReportGenerator | SequentialAgent | Creates summaries + recommendations |
| TextbookRAG | CrewAI (A2A) | Searches PDF textbooks |

---

## 📝 License

Built for the **Kaggle AI Agents Competition 2025**

---

## 🙏 Acknowledgments

- Google ADK Team
- Kaggle Competition Organizers
- CrewAI Framework

