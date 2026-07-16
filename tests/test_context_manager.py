import pytest
import threading
from datetime import datetime
from services.context_manager import ContextManager

def test_context_manager_basic_updates(context_manager):
    """Verify update_state and update_telemetry work and change update time."""
    initial_time = context_manager.shared_state["last_update"]
    
    # Update state
    context_manager.update_state("test_key", "test_val")
    state = context_manager.get_full_context()
    assert state["test_key"] == "test_val"
    assert state["last_update"] > initial_time

    # Update telemetry
    telemetry_payload = {"attendance": 50000, "avg_queue_time": 5}
    context_manager.update_telemetry(telemetry_payload)
    state = context_manager.get_full_context()
    assert state["telemetry"] == telemetry_payload

def test_context_manager_incident_lifecycle(context_manager):
    """Test incident registration, ownership assignment, and resolution."""
    # Add new signature incident
    context_manager.add_incident(
        incident_id="INC-1",
        title="Power Substation Flickering",
        priority="HIGH",
        area="South Gate Concourse",
        description="Substation B voltage drop detected",
        owner="Unassigned"
    )
    
    state = context_manager.get_full_context()
    assert len(state["active_incidents"]) == 1
    assert state["active_incidents"][0]["id"] == "INC-1"
    assert state["active_incidents"][0]["status"] == "ACTIVE"
    assert state["command_status"] == "HIGH ALERT"

    # Assign Ownership
    context_manager.assign_incident_ownership("INC-1", "MaintenanceAgent")
    assert context_manager.shared_state["incident_ownership"]["INC-1"] == "MaintenanceAgent"
    assert context_manager.shared_state["active_incidents"][0]["owner"] == "MaintenanceAgent"

    # Resolve Incident
    context_manager.resolve_incident("INC-1", "Backups stabilized and generator online")
    state = context_manager.get_full_context()
    assert len(state["active_incidents"]) == 0
    assert len(state["resolved_incidents"]) == 1
    assert state["resolved_incidents"][0]["status"] == "RESOLVED"
    assert state["command_status"] == "NORMAL"

def test_context_manager_signature_compatibility(context_manager):
    """Verify both old and new signatures of add_incident are processed successfully."""
    # 1. Old Signature: add_incident(self, title, severity, zone, description)
    context_manager.add_incident(
        "South Fan Overcrowd",  # incident_id maps to title (as it has no valid prefix)
        "CRITICAL",             # title maps to severity/priority
        "South Plaza",          # priority maps to zone/area
        "Crowd backing up outside entry gate" # area maps to description
    )
    
    state = context_manager.get_full_context()
    assert len(state["active_incidents"]) == 1
    incident = state["active_incidents"][0]
    assert incident["id"].startswith("INC-")
    assert incident["title"] == "South Fan Overcrowd"
    assert incident["severity"] == "CRITICAL"
    assert incident["priority"] == "CRITICAL"
    assert incident["zone"] == "South Plaza"
    assert incident["area"] == "South Plaza"
    assert incident["description"] == "Crowd backing up outside entry gate"

    # 2. New Signature: add_incident(self, incident_id, title, priority, area, description, ...)
    context_manager.add_incident(
        incident_id="SEC-501",
        title="Unauthorized Drone Spotted",
        priority="HIGH",
        area="South Stand Skyspace",
        description="DJI drone floating near stadium screen"
    )
    
    state = context_manager.get_full_context()
    assert len(state["active_incidents"]) == 2
    drone_incident = [i for i in state["active_incidents"] if i["id"] == "SEC-501"][0]
    assert drone_incident["title"] == "Unauthorized Drone Spotted"
    assert drone_incident["priority"] == "HIGH"
    assert drone_incident["area"] == "South Stand Skyspace"

def test_context_manager_alert_deduplication(context_manager):
    """Verify merge_alerts successfully removes identical or duplicate alerts."""
    alerts = [
        {"id": "ALT-1", "level": "WARNING", "message": "Heavy Rain"},
        {"id": "ALT-1", "level": "WARNING", "message": "Heavy Rain"}, # Duplicate ID
        {"id": "ALT-2", "level": "WARNING", "message": "Heavy Rain"}  # Duplicate message + level
    ]
    context_manager.merge_alerts(alerts)
    state = context_manager.get_full_context()
    assert len(state["stadium_alerts"]) == 1

def test_context_manager_timeline_and_snaps(context_manager):
    """Verify timeline logging and snapshots overflow handles limits safely."""
    # Test timeline event logs
    for i in range(150):
        context_manager.add_timeline_event(f"Event log {i}")
        
    state = context_manager.get_full_context()
    # Length capped at 100
    assert len(state["timeline"]) == 100
    assert state["timeline"][-1]["event"] == "Event log 149"

    # Test snapshots overflow
    for i in range(75):
        context_manager.add_telemetry_snapshot({"data": i})
        
    state = context_manager.get_full_context()
    # Capped at 50
    assert len(state["telemetry_snapshots"]) == 50

def test_context_manager_command_status_and_risk(context_manager):
    """Verify tracking of command status and risk scores."""
    context_manager.update_command_status("CMD-01", "EXECUTED", "Route lock deployed")
    state = context_manager.get_full_context()
    assert state["command_history"]["CMD-01"]["status"] == "EXECUTED"

    context_manager.add_risk_score(42.5, "Heavy congestion risk")
    state = context_manager.get_full_context()
    assert len(state["risk_history"]) == 1
    assert state["risk_history"][0]["score"] == 42.5

def test_context_manager_thread_safety(context_manager):
    """Verify thread-safety when updates occur concurrently."""
    threads = []
    
    def worker(i):
        context_manager.update_state(f"concurrent_key_{i}", i)
        context_manager.add_timeline_event(f"Timeline concurrently added {i}")
        context_manager.add_incident(
            incident_id=f"TRA-{i}",
            title=f"Incident {i}",
            priority="LOW",
            area=f"Zone {i}",
            description=f"Logistics backlog {i}"
        )

    # Spawn 20 threads to run modifications concurrently
    for i in range(20):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    # Wait for all threads to join cleanly
    for t in threads:
        t.join()

    state = context_manager.get_full_context()
    assert len(state["active_incidents"]) == 20
    # 20 events added via add_timeline_event + 20 added via add_incident
    assert len(state["timeline"]) == 40
