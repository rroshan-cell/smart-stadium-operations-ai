# FIFA World Cup 2026: Smart Stadium AI Command Center

## 🏟️ Project Overview
This is a production-quality GenAI-powered web application designed to optimize FIFA World Cup 2026 stadium operations. The system leverages a multi-agent architectural pattern to manage crowd safety, security incidents, weather risks, and tournament logistics in real-time.

### 🌟 Key Features
- **Multi-Agent Orchestration**: Powered by Google Gemini, a central `CoordinatorAgent` dynamically routes tasks to specialized domain experts (Crowd, Security, Emergency, Transit, etc.).
- **Live Simulation Engine**: 6 operationally realistic scenarios including "High Crowd", "Severe Weather", and "Full Stadium Evacuation".
- **Glassmorphism Dashboard**: A premium, real-time command center interface with SVG mapping and animated telemetry.
- **Intelligent Response Loop**: AI-driven reasoning that provides actionable "Recommendations" and "Decision Timelines" with measurable confidence scores.
- **Enterprise-Ready Backend**: FastAPI-based architecture with structured logging, async processing, and Pydantic validation.

## 🏗️ Architecture
- **Frontend**: Vanilla JS, HTML5, CSS3 (No frameworks, 0ms build time).
- **Backend**: Python FastAPI.
- **AI Integration**: Google Gemini 1.5 Pro.
- **State Management**: Blackboard pattern with a shared context vector-store.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Gemini API Key (from Google AI Studio)

### Installation
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**:
   Create a `.env` file in the root:
   ```env
   GEMINI_API_KEY=your_key_here
   LOG_LEVEL=INFO
   ```
4. **Run the Application**:
   ```bash
   uvicorn backend.main:app --reload
   ```
5. **Access the Dashboard**:
   Open `frontend/index.html` in your browser.

## 🔬 Multi-Agent System
- **Coordinator**: Routes requests and synthesizes conflicting agent outputs.
- **CrowdManagement**: Monitors surge density and gate flow.
- **Security**: Triage and response for venue incidents.
- **EmergencyResponse**: Life-safety and medical dispatch.
- **Transportation**: Transit intervals and parking capacity.
- **VisitorSupport**: Multilingual wayfinding and support.
- **Maintenance**: Predictive infrastructure health.
- **WeatherIntelligence**: Lightning and climate risk monitoring.

## 🛡️ Security & Compliance
- **Security**: OAuth2 token support, input sanitization, and PII redaction.
- **Accessibility**: WCAG 2.1 Level AA inspired design with full ARIA support.
- **Observability**: Structured JSON logging with unique Request IDs for auditability.

---
*Built for PromptWars Challenge 04: "Smart Stadiums & Tournament Operations"*
