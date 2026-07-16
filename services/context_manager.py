import threading
from typing import Dict, List, Any, Optional
from datetime import datetime

class ContextManager:
    def __init__(self):
        self._lock = threading.Lock()
        self.shared_state: Dict[str, Any] = {
            "last_update": datetime.now().isoformat(),
            "telemetry": {},
            "active_incidents": [],  # List of dicts to preserve backward compatibility
            "resolved_incidents": [],
            "stadium_alerts": [],
            "agent_history": [],
            "incident_timeline": [],  # Old key
            "timeline": [],           # New key
            "telemetry_snapshots": [],
            "command_history": {},
            "risk_history": [],
            "incident_ownership": {},
            "command_status": "NORMAL"
        }

    def update_state(self, key: str, value: Any):
        with self._lock:
            self.shared_state[key] = value
            self.shared_state["last_update"] = datetime.now().isoformat()

    def update_telemetry(self, telemetry: Dict[str, Any]):
        with self._lock:
            self.shared_state["telemetry"] = telemetry
            self.shared_state["last_update"] = datetime.now().isoformat()

    def add_agent_output(self, agent_name: str, output: Dict[str, Any]):
        with self._lock:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "agent": agent_name,
                "output": output
            }
            self.shared_state["agent_history"].append(entry)
            if len(self.shared_state["agent_history"]) > 50:
                self.shared_state["agent_history"].pop(0)
            self.shared_state["last_update"] = datetime.now().isoformat()

    def get_full_context(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self.shared_state)

    def merge_alerts(self, new_alerts: List[Dict[str, Any]]):
        with self._lock:
            for alert in new_alerts:
                is_duplicate = False
                for existing in self.shared_state["stadium_alerts"]:
                    if existing.get("id") == alert.get("id") or (existing.get("message") == alert.get("message") and existing.get("level") == alert.get("level")):
                        is_duplicate = True
                        break
                if not is_duplicate:
                    self.shared_state["stadium_alerts"].append(alert)
            if len(self.shared_state["stadium_alerts"]) > 50:
                self.shared_state["stadium_alerts"] = self.shared_state["stadium_alerts"][-50:]
            self.shared_state["last_update"] = datetime.now().isoformat()

    # --- Thread-Safe Blackboard Operations ---

    def add_incident(
        self,
        incident_id: str,
        title: str = "",
        priority: str = "",
        area: str = "",
        description: str = "",
        owner: str = "Unassigned",
        severity: Optional[str] = None,
        zone: Optional[str] = None
    ):
        with self._lock:
            # Detect signature variation: add_incident(self, title, severity, zone, description)
            # if incident_id is a title and priority/area are empty, check if it's the old signature
            is_old_sig = False
            # Check prefix for structured IDs
            prefixes = ["INC-", "SEC-", "MED-", "EVAC-", "WEA-", "MNT-", "FIR-", "TRA-", "CRD-"]
            has_valid_prefix = any(incident_id.startswith(p) for p in prefixes)
            
            if not has_valid_prefix:
                is_old_sig = True

            if is_old_sig:
                old_title = incident_id
                old_severity = title
                old_zone = priority
                old_description = area
                
                # Auto-generate ID and map fields
                generated_id = f"INC-{len(self.shared_state['active_incidents']) + len(self.shared_state['resolved_incidents']) + 1}"
                incident = {
                    "id": generated_id,
                    "title": old_title,
                    "severity": old_severity,
                    "priority": old_severity.upper(),
                    "zone": old_zone,
                    "area": old_zone,
                    "description": old_description,
                    "owner": "Unassigned",
                    "status": "ACTIVE",
                    "created_at": datetime.now().isoformat(),
                    "reported_at": datetime.now().isoformat(),
                    "resolved_at": None,
                    "resolution": None
                }
                self.shared_state["active_incidents"].append(incident)
                self.shared_state["incident_ownership"][generated_id] = "Unassigned"
                self._add_timeline_event_unlocked(f"{old_title} detected at {old_zone}")
                
                if old_severity.upper() in ["HIGH", "CRITICAL"]:
                    self.shared_state["command_status"] = "HIGH ALERT"
            else:
                # New structured signature
                incident = {
                    "id": incident_id,
                    "title": title,
                    "severity": priority,  # keep both keys for safety
                    "priority": priority,
                    "zone": area,          # keep both keys for safety
                    "area": area,
                    "description": description,
                    "owner": owner,
                    "status": "ACTIVE",
                    "created_at": datetime.now().isoformat(),
                    "reported_at": datetime.now().isoformat(),
                    "resolved_at": None,
                    "resolution": None
                }
                self.shared_state["active_incidents"].append(incident)
                self.shared_state["incident_ownership"][incident_id] = owner
                self._add_timeline_event_unlocked(f"Incident {incident_id} ({title}) reported in {area} [Priority: {priority}]")
                
                if priority.upper() in ["HIGH", "CRITICAL"]:
                    self.shared_state["command_status"] = "HIGH ALERT"

            self.shared_state["last_update"] = datetime.now().isoformat()

    def resolve_incident(self, incident_id: str, resolution_details: str = "Resolved by Operations"):
        with self._lock:
            found_idx = -1
            for idx, incident in enumerate(self.shared_state["active_incidents"]):
                if incident["id"] == incident_id:
                    found_idx = idx
                    break
            
            if found_idx != -1:
                incident = self.shared_state["active_incidents"].pop(found_idx)
                incident["status"] = "RESOLVED"
                incident["resolved_at"] = datetime.now().isoformat()
                incident["resolution"] = resolution_details
                self.shared_state["resolved_incidents"].append(incident)
                self._add_timeline_event_unlocked(f"Incident {incident_id} ({incident['title']}) resolved: {resolution_details}")
                
                # Remove from active stadium alerts if matches id
                self.shared_state["stadium_alerts"] = [
                    a for a in self.shared_state["stadium_alerts"] if a.get("id") != incident_id
                ]

            # Recalculate command status
            has_active_critical = any(
                i.get("priority", "").upper() in ["HIGH", "CRITICAL"] or i.get("severity", "").upper() in ["HIGH", "CRITICAL"]
                for i in self.shared_state["active_incidents"]
            )
            if has_active_critical:
                self.shared_state["command_status"] = "HIGH ALERT"
            else:
                self.shared_state["command_status"] = "NORMAL"
                
            self.shared_state["last_update"] = datetime.now().isoformat()

    def assign_incident_ownership(self, incident_id: str, agent_name: str):
        with self._lock:
            for incident in self.shared_state["active_incidents"]:
                if incident["id"] == incident_id:
                    incident["owner"] = agent_name
            self.shared_state["incident_ownership"][incident_id] = agent_name
            self._add_timeline_event_unlocked(f"Incident {incident_id} assigned to agent {agent_name}")
            self.shared_state["last_update"] = datetime.now().isoformat()

    def add_timeline_event(self, message: str):
        with self._lock:
            self._add_timeline_event_unlocked(message)

    def _add_timeline_event_unlocked(self, message: str):
        # Support both new/old formats
        event = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "timestamp": datetime.now().isoformat(),
            "event": message,
            "description": message
        }
        self.shared_state["incident_timeline"].append(event)
        self.shared_state["timeline"].append(event)
        
        if len(self.shared_state["incident_timeline"]) > 100:
            self.shared_state["incident_timeline"].pop(0)
        if len(self.shared_state["timeline"]) > 100:
            self.shared_state["timeline"].pop(0)

    def add_telemetry_snapshot(self, telemetry: Dict[str, Any]):
        with self._lock:
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "telemetry": telemetry
            }
            self.shared_state["telemetry_snapshots"].append(snapshot)
            if len(self.shared_state["telemetry_snapshots"]) > 50:
                self.shared_state["telemetry_snapshots"].pop(0)
            self.shared_state["last_update"] = datetime.now().isoformat()

    def update_command_status(self, command_id: str, status: str, details: str = ""):
        with self._lock:
            self.shared_state["command_history"][command_id] = {
                "status": status,
                "details": details,
                "updated_at": datetime.now().isoformat()
            }
            self._add_timeline_event_unlocked(f"Command {command_id} status updated to {status}: {details}")
            self.shared_state["last_update"] = datetime.now().isoformat()

    def add_risk_score(self, score: float, details: str = ""):
        with self._lock:
            self.shared_state["risk_history"].append({
                "timestamp": datetime.now().isoformat(),
                "score": score,
                "details": details
            })
            if len(self.shared_state["risk_history"]) > 50:
                self.shared_state["risk_history"].pop(0)
            self.shared_state["last_update"] = datetime.now().isoformat()