from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ConfidenceScore(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str

class Recommendation(BaseModel):
    action: str
    priority: str
    target_zone: str
    justification: str

class SystemAlert(BaseModel):
    level: str  # e.g., "INFO", "WARNING", "CRITICAL"
    message: str
    timestamp: str

class AgentResponse(BaseModel):
    agent_name: str
    analysis: str
    recommendations: List[Recommendation]
    confidence: ConfidenceScore
    priority: str = "MEDIUM"
    next_actions: List[str] = []
    requires_human_approval: bool = False
    alerts: List[SystemAlert] = []

class AgentRequest(BaseModel):
    query: str
    telemetry: Dict[str, Any]
    history: List[Dict[str, Any]] = []
    metadata: Optional[Dict[str, Any]] = {}
