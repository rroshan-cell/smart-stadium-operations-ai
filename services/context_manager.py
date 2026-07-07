from typing import Dict, List, Any
from datetime import datetime

class ContextManager:
    def __init__(self):
        self.shared_state: Dict[str, Any] = {
            "last_update": datetime.now().isoformat(),
            "stadium_alerts": [],
            "agent_history": []
        }

    def update_state(self, key: str, value: Any):
        self.shared_state[key] = value
        self.shared_state["last_update"] = datetime.now().isoformat()

    def add_agent_output(self, agent_name: str, output: Dict[str, Any]):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "output": output
        }
        self.shared_state["agent_history"].append(entry)
        # Keep history manageable
        if len(self.shared_state["agent_history"]) > 20:
             self.shared_state["agent_history"].pop(0)

    def get_full_context(self) -> Dict[str, Any]:
        return self.shared_state

    def merge_alerts(self, new_alerts: List[Dict[str, Any]]):
        for alert in new_alerts:
            if alert not in self.shared_state["stadium_alerts"]:
                self.shared_state["stadium_alerts"].append(alert)
        # Maintain only active alerts
        if len(self.shared_state["stadium_alerts"]) > 50:
            self.shared_state["stadium_alerts"] = self.shared_state["stadium_alerts"][-50:]
