from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ConfidenceScore(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = ""

class Recommendation(BaseModel):
    action: str
    priority: str
    target_zone: str
    justification: str

class SystemAlert(BaseModel):
    level: str  # e.g., "INFO", "WARNING", "CRITICAL"
    message: str
    timestamp: str

class RoutingDecision(BaseModel):
    selected_agents: List[str] = Field(..., description="List of agents selected to handle the query")
    reason: str = Field(..., description="A clear, logical explanation of why these agents were selected")
    confidence: float = Field(..., ge=0.0, le=1.0, description="The confidence score of the routing decision")
    evidence: str = Field(..., description="The key telemetry indicators or keywords that triggered this routing")
    operational_explanation: str = Field(..., description="A tactical explanation of how these agents will cooperate")

class AgentResponse(BaseModel):
    agent_name: str
    analysis: str
    recommendations: List[Recommendation]
    confidence: ConfidenceScore
    priority: str = "MEDIUM"
    next_actions: List[str] = []
    requires_human_approval: bool = False
    alerts: List[SystemAlert] = []
    routing_decision: Optional[RoutingDecision] = None  # Added for Explainable AI Routing

class AgentRequest(BaseModel):
    query: str
    telemetry: Dict[str, Any]
    history: List[Dict[str, Any]] = []
    metadata: Optional[Dict[str, Any]] = {}

class HealthResponse(BaseModel):
    status: str
    version: str
