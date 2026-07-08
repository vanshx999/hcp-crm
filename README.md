# HCP CRM — AI-First Interaction Logger

> **Life Sciences CRM Module** — Log and manage HCP interactions through an AI-powered conversational interface.

---

## Overview

A split-screen CRM application where a **LangGraph-powered AI agent** manages a structured HCP interaction form entirely through natural conversation. The form on the left is **read-only to the user** — every field is populated, edited, validated, and enriched by the AI assistant on the right.

---

## Tech Stack

| Layer       | Technology                              |
|-------------|-----------------------------------------|
| Frontend    | React 18, TypeScript, Redux Toolkit, Tailwind CSS, Vite |
| Backend     | Python 3.11+, FastAPI, WebSocket        |
| AI Agent    | LangGraph (StateGraph)                  |
| LLM         | Groq — `gemma2-9b-it`                  |
| Database    | PostgreSQL via SQLAlchemy               |
| Font        | Google Inter                            |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Browser (React)                       │
│  ┌────────────────────────┐  ┌────────────────────────┐  │
│  │   Interaction Form     │  │   AI Chat Panel        │  │
│  │   (Read-only, Redux)   │  │   (WebSocket Client)   │  │
│  └──────────┬─────────────┘  └───────────┬────────────┘  │
│             │                             │               │
└─────────────┼─────────────────────────────┼───────────────┘
              │                             │
              │     HTTP/WS (localhost:8000) │
              │                             │
┌─────────────┼─────────────────────────────┼───────────────┐
│             ▼                             ▼               │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              FastAPI Backend                          │ │
│  │  ┌──────────────────────────────────────────────┐    │ │
│  │  │         LangGraph Agent                       │    │ │
│  │  │  ┌──────────┐  ┌──────────────────────┐      │    │ │
│  │  │  │ Parse &  │─>│ Router (intent detect)│      │    │ │
│  │  │  │ Route    │  └──────┬───┬───┬───┬───┘      │    │ │
│  │  │  └──────────┘         │   │   │   │          │    │ │
│  │  │         ┌─────────────┘   │   │   └─────┐    │    │ │
│  │  │         ▼                 ▼   ▼         ▼    │    │ │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │    │ │
│  │  │  │Log Inter.│  │Edit Inter│  │Validate  │   │    │ │
│  │  │  ├──────────┤  ├──────────┤  ├──────────┤   │    │ │
│  │  │  │Search HCP│  │Suggest   │  │Response  │   │    │ │
│  │  │  └──────────┘  └──────────┘  └──────────┘   │    │ │
│  │  └──────────────────────────────────────────────┘    │ │
│  │                     │                                 │ │
│  │              ┌──────▼──────┐                          │ │
│  │              │  PostgreSQL  │                          │ │
│  │              └─────────────┘                          │ │
│  └──────────────────────────────────────────────────────┘ │
│                         Python                             │
└──────────────────────────────────────────────────────────┘
```

---

## LangGraph Agent — 5 Tools

### 1. Log Interaction (`log_interaction`)
Extracts structured interaction data from natural language using Groq LLM. Fields extracted: HCP name, interaction type, date, duration, sentiment, specialty, region, products discussed, discussion points, action items, follow-up date, and notes.

**Example:** _"I met with Dr. Sarah Chen today, discussed our new cardiology drug. She was very receptive and wants to see clinical data."_

### 2. Edit Interaction (`edit_interaction`)
Updates specific fields in the existing interaction record based on user instructions. Only the fields mentioned in the edit request are modified; all others remain unchanged.

**Example:** _"Change the sentiment to Negative and add that she had concerns about pricing."_

### 3. Search HCP (`search_hcp`)
Searches for HCP records by name, specialty, or region. Returns matching results from the database.

**Example:** _"Search for cardiologists in San Francisco."_

### 4. Suggest Next Steps (`suggest_next_steps`)
Analyzes the current interaction data and generates strategic follow-up suggestions with priority levels and timeframes.

**Example:** _"Suggest next steps for this interaction."_

### 5. Validate Interaction (`validate`)
Checks the interaction record for completeness, identifies missing required fields, and provides recommendations.

**Example:** _"Validate the current interaction record."_

---

## Graph Flow

```
[User Message]
      │
      ▼
[Parse & Route] ──(intent detection)──>
      │      │        │        │       │
      ▼      ▼        ▼        ▼       ▼
   log     edit    search   suggest  validate
      │      │        │        │       │
      └──────┴────────┴────────┴───────┘
                      │
                      ▼
            [Generate Response]
                      │
                      ▼
                 [Return to User]
```

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or SQLite for development)
- Groq API key ([get one free](https://console.groq.com))

### 1. Clone & Install Backend

```bash
# From project root
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env .env.local
# Edit .env.local with your Groq API key and database URL
```

### 3. Run Backend

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Install & Run Frontend

```bash
cd ../frontend
npm install
npm run dev
```

### 5. Open in Browser

```
http://localhost:5173
```

---

## Using the Application

1. The **left panel** displays the structured interaction form — all fields are read-only and managed by AI.
2. The **right panel** is the AI chat interface.
3. Type naturally about your HCP interaction. Examples:
   - _"I had a call with Dr. Emily Patel today, discussed diabetes management products. She was interested in our new insulin pen."_
   - _"Change the interaction type to Meeting."_
   - _"Search for oncologists in New York."_
   - _"Suggest next steps."_
   - _"Validate the record."_
4. The AI processes your message through the LangGraph agent and updates the form automatically.

---

## Project Structure

```
hcp-crm/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI server + WebSocket endpoint
│   │   ├── agent.py         # LangGraph StateGraph agent
│   │   ├── tools.py         # 5 LangGraph tool implementations
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── database.py      # Database connection & session
│   │   └── config.py        # Environment configuration
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InteractionForm.tsx   # Read-only form panel
│   │   │   └── ChatPanel.tsx         # AI chat interface
│   │   ├── store/
│   │   │   ├── index.ts              # Redux store config
│   │   │   └── interactionSlice.ts   # Redux state + actions
│   │   ├── api/
│   │   │   └── agentApi.ts           # WebSocket client
│   │   ├── App.tsx                   # Split-screen layout
│   │   ├── main.tsx                  # Entry point
│   │   └── index.css                 # Tailwind imports
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── postcss.config.js
└── README.md
```

---

## API Endpoints

| Method   | Path          | Description              |
|----------|---------------|--------------------------|
| `GET`    | `/api/health` | Health check             |
| `WS`     | `/ws/chat`    | WebSocket chat endpoint  |

### WebSocket Message Format

**Request:**
```json
{
  "message": "I met with Dr. Sarah Chen...",
  "conversation_id": null
}
```

**Response:**
```json
{
  "reply": "I've logged the interaction with Dr. Sarah Chen...",
  "interaction": { "hcp_name": "Dr. Sarah Chen", ... },
  "conversation_id": "uuid-here",
  "tool_called": "detected_automatically"
}
```

---

## License

MIT
