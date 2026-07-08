import time
from typing import Dict, Any, List
from datetime import datetime

class SimulationEngine:
    def __init__(self):
        self.is_active = False
        self.current_scenario = "Normal Match"
        self.world_state = self._get_initial_state()
        self.history = []

    def _get_initial_state(self) -> Dict[str, Any]:
        return {
            "attendance": 70000,
            "max_capacity": 82500,
            "gates": {"gate-a": "green", "gate-b": "green", "gate-c": "green", "gate-d": "green"},
            "weather": {"temp": 24, "condition": "Clear", "lightning": False},
            "parking": 75,
            "avg_queue_time": 3,
            "active_alerts": []
        }

    def set_scenario(self, scenario_name: str):
        # Reset to clean baseline first so previous scenario state does not bleed through
        self.world_state = self._get_initial_state()
        self.current_scenario = scenario_name
        self.is_active = True

        if scenario_name == "High Crowd Match":
            self.world_state["attendance"] = 82000
            self.world_state["avg_queue_time"] = 12
            self.world_state["gates"]["gate-c"] = "yellow"
        elif scenario_name == "Medical Emergency":
            self.world_state["active_alerts"].append({
                "id": "MED-1", "title": "Cardiac Issue - Sector 201", "priority": "critical"
            })
        elif scenario_name == "Severe Weather":
            self.world_state["weather"] = {"temp": 18, "condition": "Thunderstorm", "lightning": True}
        elif scenario_name == "Security Threat":
            self.world_state["active_alerts"].append({
                "id": "SEC-1", "title": "Suspicious Package - North Gate", "priority": "critical"
            })
        elif scenario_name == "Full Stadium Evacuation":
            # All gates open for egress; no red gates during controlled evacuation
            self.world_state["gates"] = {"gate-a": "green", "gate-b": "green", "gate-c": "green", "gate-d": "green"}
            self.world_state["active_alerts"].append({
                "id": "EVAC-1", "title": "GLOBAL EVACUATION INITIATED", "priority": "critical"
            })

    def update_cycle(self):
        """Slightly mutate data to simulate life."""
        if not self.is_active: return
        
        # Natural jitter
        self.world_state["attendance"] += (time.time() % 5) - 2
        self.world_state["parking"] = min(100, max(0, self.world_state["parking"] + (time.time() % 3 - 1)))
        
        # Scenario specific drift
        if self.current_scenario == "High Crowd Match":
             self.world_state["avg_queue_time"] = min(20, self.world_state["avg_queue_time"] + 0.1)

    def get_state(self) -> Dict[str, Any]:
        self.update_cycle()
        return {
            "scenario": self.current_scenario,
            "telemetry": self.world_state,
            "timestamp": datetime.now().isoformat()
        }
