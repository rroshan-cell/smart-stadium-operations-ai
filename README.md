# 🏟️ FIFA World Cup 2026 – Smart Stadium Operations AI

> **An AI-powered Multi-Agent Command Center for intelligent stadium operations, real-time monitoring, incident response, and decision support during large-scale sporting events.**

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![License](https://img.shields.io/badge/License-MIT-blue)

---

# 📖 Overview

Managing a modern sports stadium during a tournament like the **FIFA World Cup 2026** requires continuous monitoring of thousands of events occurring simultaneously—from crowd movement and security incidents to weather changes, transportation, and emergency response.

Traditional monitoring dashboards display information but still require operators to manually analyze situations and decide what to do next.

**Smart Stadium Operations AI** combines a real-time simulation engine with a collaborative Multi-Agent AI architecture to assist operators by transforming live telemetry into structured operational insights and recommendations.

---

# 🎯 Problem Statement

Large sporting events involve managing:

- Crowd density
- Security threats
- Medical emergencies
- Weather disruptions
- Transportation flow
- Infrastructure maintenance
- Visitor assistance

Operators often receive large amounts of fragmented information from multiple systems, making rapid decision-making difficult.

This project demonstrates how AI agents can coordinate, analyze operational telemetry, and assist human operators with actionable recommendations.

---

# 💡 Solution

The platform combines:

- Real-time Stadium Simulation
- AI Multi-Agent Coordination
- Interactive Operations Dashboard
- Live Analytics
- Incident Management
- AI Decision Support

Each specialized AI agent focuses on a specific operational domain while a central **Coordinator Agent** synthesizes their outputs into a unified response.

---

# ✨ Key Features

## 🤖 Multi-Agent AI Architecture

Specialized agents collaborate together:

- Crowd Management Agent
- Security Agent
- Emergency Response Agent
- Transportation Agent
- Maintenance Agent
- Visitor Support Agent
- Weather Intelligence Agent

All communication is orchestrated through a **Coordinator Agent**.

---

## 🏟️ Real-Time Stadium Simulation

Supports multiple operational scenarios:

- ✅ Normal Match
- ✅ High Crowd Match
- ✅ Medical Emergency
- ✅ Security Threat
- ✅ Severe Weather
- ✅ Full Stadium Evacuation

Every scenario dynamically updates:

- Attendance
- Gate status
- Parking occupancy
- Queue times
- Weather
- Alerts
- AI recommendations

---

## 📊 Interactive Operations Dashboard

Features include:

- Live telemetry
- Animated attendance counter
- Dynamic gate visualization
- Incident feed
- KPI monitoring
- Analytics charts
- AI confidence score
- Operations log
- Real-time clock
- AI chat interface

---

## 📈 Analytics

Interactive charts display:

- Attendance trend
- Queue time trend
- Parking utilization
- Alert history

---

## ⚙️ Modular Frontend

The dashboard is organized into independent ES6 modules:

```
DashboardController
DashboardAPI
AttendanceAnimator
GateManager
IncidentFeed
SimulationController
ChatController
SidebarController
ClockManager
ToastManager
LoadingManager
Utils
```

This improves maintainability, scalability, and separation of concerns.

---

# 🏗️ System Architecture

```
                     Stadium Telemetry
                            │
                            ▼
                  Simulation Engine
                            │
                            ▼
                  Coordinator Agent
                            │
      ┌────────────┬────────────┬────────────┐
      ▼            ▼            ▼
 Crowd Agent   Security     Emergency
                  Agent        Agent

      ▼            ▼            ▼
Transport     Maintenance    Weather

              ▼
       Visitor Support

              ▼
        FastAPI Backend

              ▼
 Interactive Command Center
```

---

# 🛠 Technology Stack

## Backend

- Python 3.12
- FastAPI
- Pydantic
- AsyncIO

## AI

- Google Gemini API
- Multi-Agent Architecture

## Frontend

- HTML5
- CSS3
- Vanilla JavaScript (ES6 Modules)
- Chart.js

---

# 📂 Project Structure

```
backend/
│
├── routes/
├── dependencies.py
├── config.py
└── main.py

agents/

services/

models/

frontend/
│
├── js/
├── style.css
└── index.html

tests/

requirements.txt
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/rroshan-cell/smart-stadium-operations-ai.git

cd smart-stadium-operations-ai
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment

Create a `.env` file:

```env
GEMINI_API_KEY=YOUR_API_KEY
LOG_LEVEL=INFO
```

---

## Run Application

```bash
python -m uvicorn backend.main:app --reload
```

Open:

```
http://127.0.0.1:8000
```

---

# 🌐 API Endpoints

| Method | Endpoint | Description |
|----------|----------------------------|----------------------------------|
| GET | `/api/v1/simulation/state` | Get live telemetry |
| POST | `/api/v1/simulation/start` | Start simulation |
| POST | `/api/v1/chat` | AI operator chat |
| GET | `/api/v1/agents/status` | Agent status |
| GET | `/api/v1/agents/alerts` | Active alerts |
| GET | `/health` | Health check |

---

# 🧪 Testing

Run:

```bash
python -m pytest
```

Latest verified result:

```
==========================
3 passed
==========================
```

---

# 🔒 Security

- Environment-based API key configuration
- No secrets committed to Git
- Input validation using Pydantic
- Centralized exception handling
- Structured logging

---

# ♿ Accessibility

The dashboard includes:

- Semantic HTML
- ARIA-friendly structure
- Responsive layouts
- High-contrast interface
- Keyboard-friendly navigation where applicable

---

# 🚀 Deployment

The application is designed as a **single FastAPI application** that serves:

- Backend APIs
- Frontend static assets

This simplifies deployment on platforms such as:

- Render
- Railway
- Azure App Service
- Google Cloud Run

---

# 📸 Screenshots

> Add screenshots before final submission.

Suggested screenshots:

- Dashboard
- Analytics
- Medical Emergency Scenario
- Security Threat Scenario
- Incident Feed

---

# 🔮 Future Improvements

- IoT sensor integration
- Predictive crowd analytics
- CCTV/video intelligence
- Digital twin visualization
- Multi-stadium orchestration
- Support for multiple LLM providers

---

# 🎯 Challenge Alignment

This project addresses the **PromptWars Challenge 4 – Smart Stadiums & Tournament Operations** by demonstrating how AI-assisted operational intelligence can support large-scale sporting events through:

- Multi-Agent Collaboration
- Real-Time Monitoring
- Intelligent Decision Support
- Scenario Simulation
- Human-in-the-Loop Operations

---

# 👨‍💻 Author

**RITIK ROSHAN**

B.Tech Electronics & Communication Engineering

University of Lucknow

GitHub:
https://github.com/rroshan-cell

---

## ⭐ If you found this project interesting, consider giving it a star.