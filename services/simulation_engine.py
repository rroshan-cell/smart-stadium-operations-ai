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
            "weather": {"temp": 24, "condition": "Clear", "lightning": False, "precipitation": 0},
            "parking": 75,
            "avg_queue_time": 3,
            "active_alerts": [],
            "fan_zones": {"north": 40, "south": 75, "east": 45, "west": 70},
            "power_status": "grid_optimal",  # grid_optimal, battery_backup, substation_failure
            "transit_status": "optimal"      # optimal, heavy_traffic, train_suspended
        }

    def set_scenario(self, scenario_name: str):
        # Reset to base state to prevent state carryover
        self.world_state = self._get_initial_state()
        self.current_scenario = scenario_name
        self.is_active = True

        now_str = datetime.now().strftime("%H:%M:%S")

        if scenario_name == "Normal Match":
            pass

        elif scenario_name == "Kickoff Rush":
            self.world_state["attendance"] = 79500
            self.world_state["parking"] = 90
            self.world_state["gates"] = {"gate-a": "yellow", "gate-b": "yellow", "gate-c": "yellow", "gate-d": "yellow"}
            self.world_state["avg_queue_time"] = 14
            self.world_state["fan_zones"] = {"north": 75, "south": 95, "east": 65, "west": 90}
            self.world_state["active_alerts"].append({
                "id": "CRD-1",
                "title": "Kickoff Rush Inflow",
                "priority": "warning",
                "message": "Heavy gate inflow queue buildup before kickoff.",
                "area": "Gates A/B/C/D Plaza",
                "action": "Open secondary ticket inspection lanes.",
                "timestamp": now_str
            })

        elif scenario_name == "Gate Congestion":
            self.world_state["attendance"] = 72000
            self.world_state["parking"] = 80
            self.world_state["gates"] = {"gate-a": "green", "gate-b": "green", "gate-c": "red", "gate-d": "yellow"}
            self.world_state["avg_queue_time"] = 18
            self.world_state["active_alerts"].append({
                "id": "CRD-2",
                "title": "Gate C Turnstile Failure",
                "priority": "critical",
                "message": "Gate C turnstile network failure causing severe concourse backup.",
                "area": "Gate C Concourse",
                "action": "Redirect fans to Gate B and dispatch network technicians.",
                "timestamp": now_str
            })

        elif scenario_name == "VIP Arrival":
            self.world_state["attendance"] = 71500
            self.world_state["parking"] = 82
            self.world_state["gates"] = {"gate-a": "yellow", "gate-b": "green", "gate-c": "green", "gate-d": "green"}
            self.world_state["avg_queue_time"] = 6
            self.world_state["active_alerts"].append({
                "id": "SEC-VIP",
                "title": "VIP Arrival Protocol",
                "priority": "warning",
                "message": "VIP motorcade transit at West perimeter VIP gate.",
                "area": "West Security Gate A",
                "action": "Enforce temporary motorcade corridor lock.",
                "timestamp": now_str
            })

        elif scenario_name == "Fan Zone Congestion":
            self.world_state["attendance"] = 73000
            self.world_state["parking"] = 85
            self.world_state["fan_zones"] = {"north": 50, "south": 98, "east": 55, "west": 85}
            self.world_state["active_alerts"].append({
                "id": "CRD-FZN",
                "title": "South Fan Zone Overload",
                "priority": "warning",
                "message": "South Fan Zone density exceeds safety thresholds.",
                "area": "South Plaza Fan Zone",
                "action": "Restrict entry and route overflow crowd to East Plaza.",
                "timestamp": now_str
            })

        elif scenario_name == "Parking Overflow":
            self.world_state["attendance"] = 76000
            self.world_state["parking"] = 99
            self.world_state["transit_status"] = "heavy_traffic"
            self.world_state["active_alerts"].append({
                "id": "TRA-PKO",
                "title": "Parking Lots Full",
                "priority": "warning",
                "message": "Parking Lots A & B full. Initiating lot C redirection signs.",
                "area": "Parking Lots A/B",
                "action": "Update dynamic road signage to Route 3 South Lot C.",
                "timestamp": now_str
            })

        elif scenario_name == "Medical Emergency":
            self.world_state["attendance"] = 70000
            self.world_state["weather"]["temp"] = 28
            self.world_state["weather"]["condition"] = "Hazy"
            self.world_state["active_alerts"].append({
                "id": "MED-1",
                "title": "Cardiac Issue - Sector 201",
                "priority": "critical",
                "message": "Cardiac Incident reporting in Sector 201. Medical dispatch initiated.",
                "area": "Stand Sector 201",
                "action": "Dispatch Medical Triage Unit 3 via Elevator 2.",
                "timestamp": now_str
            })

        elif scenario_name == "Suspicious Package":
            self.world_state["attendance"] = 70000
            self.world_state["gates"] = {"gate-a": "red", "gate-b": "green", "gate-c": "green", "gate-d": "green"}
            self.world_state["avg_queue_time"] = 11
            self.world_state["active_alerts"].append({
                "id": "SEC-PKG",
                "title": "Suspicious Package Gate A",
                "priority": "critical",
                "message": "Unattended bag located at Gate A plaza. Bomb squad deployed.",
                "area": "Gate A Entrance Plaza",
                "action": "Lockdown Gate A, establish 100m perimeter safety cordon.",
                "timestamp": now_str
            })

        elif scenario_name == "Security Threat":
            self.world_state["attendance"] = 70000
            self.world_state["gates"] = {"gate-a": "yellow", "gate-b": "yellow", "gate-c": "green", "gate-d": "green"}
            self.world_state["avg_queue_time"] = 15
            self.world_state["active_alerts"].append({
                "id": "SEC-THR",
                "title": "Perimeter Breach Threat",
                "priority": "critical",
                "message": "Coordinated perimeter breach attempt reports. Tightening inspections.",
                "area": "Outer Security Fence North",
                "action": "Mobilize Security Reserve Group B to Gate A and B perimeters.",
                "timestamp": now_str
            })

        elif scenario_name == "Drone Intrusion":
            self.world_state["attendance"] = 70500
            self.world_state["active_alerts"].append({
                "id": "SEC-DRN",
                "title": "Drone Intrusion Over Stands",
                "priority": "critical",
                "message": "Unauthorized drone flying over South Stand. Threat mitigation active.",
                "area": "South Stand Bowl airspace",
                "action": "Deploy RF jammer and locate ground operator.",
                "timestamp": now_str
            })

        elif scenario_name == "Fire Alarm":
            self.world_state["attendance"] = 70000
            self.world_state["gates"] = {"gate-a": "green", "gate-b": "red", "gate-c": "green", "gate-d": "green"}
            self.world_state["active_alerts"].append({
                "id": "FIR-1",
                "title": "Concession Fire Alarm",
                "priority": "critical",
                "message": "Smoke alarm in Concessions Block B. Suppress & dispatch active.",
                "area": "Level 1 Concourse Block B",
                "action": "Isolate power to concessions grid B, evacuate Zone B concourse.",
                "timestamp": now_str
            })

        elif scenario_name == "Power Failure":
            self.world_state["attendance"] = 70000
            self.world_state["power_status"] = "substation_failure"
            self.world_state["gates"] = {"gate-a": "green", "gate-b": "green", "gate-c": "yellow", "gate-d": "yellow"}
            self.world_state["avg_queue_time"] = 12
            self.world_state["active_alerts"].append({
                "id": "MNT-PWR",
                "title": "Main substation outage",
                "priority": "critical",
                "message": "Main substation outage. Concourse backup generators running.",
                "area": "Stadium-wide Infrastructure",
                "action": "Engage generator backup feeds, restrict elevators to emergency services.",
                "timestamp": now_str
            })

        elif scenario_name == "Severe Weather":
            self.world_state["attendance"] = 68000
            self.world_state["weather"] = {"temp": 16, "condition": "Thunderstorm", "lightning": False, "precipitation": 80}
            self.world_state["avg_queue_time"] = 8
            self.world_state["active_alerts"].append({
                "id": "WEA-STM",
                "title": "Heavy Rain & Storm Warning",
                "priority": "warning",
                "message": "Heavy rainfall warning. Fans moving under concourse roofs.",
                "area": "MetLife Open Air Bowl",
                "action": "Activate wet weather slips-and-falls warning signs on staircases.",
                "timestamp": now_str
            })

        elif scenario_name == "Lightning Delay":
            self.world_state["attendance"] = 65000
            self.world_state["weather"] = {"temp": 15, "condition": "Severe Thunderstorm", "lightning": True, "precipitation": 95}
            self.world_state["avg_queue_time"] = 10
            self.world_state["active_alerts"].append({
                "id": "WEA-LTG",
                "title": "Lightning Evacuation Protocol",
                "priority": "critical",
                "message": "Lightning strike within 8km. FIFA Lightning Protocol activated.",
                "area": "Full Stadium Airspace",
                "action": "Evacuate upper tier stands, direct spectators to sheltered concourses.",
                "timestamp": now_str
            })

        elif scenario_name == "Transportation Failure":
            self.world_state["attendance"] = 74000
            self.world_state["parking"] = 80
            self.world_state["transit_status"] = "train_suspended"
            self.world_state["active_alerts"].append({
                "id": "TRA-FLD",
                "title": "NJ Transit Rail Suspended",
                "priority": "critical",
                "message": "NJ Transit rail line suspended. Deploying backup shuttle bus fleet.",
                "area": "West Transit Loop Terminal",
                "action": "Deploy dynamic transit signs and dispatch emergency shuttle bus fleet.",
                "timestamp": now_str
            })

        elif scenario_name == "Full Stadium Evacuation":
            self.world_state["attendance"] = 70000
            self.world_state["gates"] = {"gate-a": "green", "gate-b": "green", "gate-c": "green", "gate-d": "green"}
            self.world_state["avg_queue_time"] = 12
            self.world_state["active_alerts"].append({
                "id": "EVAC-1",
                "title": "GLOBAL EVACUATION ORDER",
                "priority": "critical",
                "message": "GLOBAL COORD STADIUM EVACUATION ORDER ISSUED.",
                "area": "MetLife Stadium (All Sectors)",
                "action": "Open all egress gates, direct PA systems, guide shuttle priority lanes.",
                "timestamp": now_str
            })

    def update_cycle(self):
        """Slightly mutate data over time to simulate active stadium dynamics."""
        if not self.is_active: 
            return
        
        # Jitter attendance
        if self.current_scenario == "Full Stadium Evacuation":
            # Evacuation drains crowd
            self.world_state["attendance"] = max(0, self.world_state["attendance"] - 2500)
        else:
            # Natural attendance adjustments
            self.world_state["attendance"] = min(self.world_state["max_capacity"], max(10000, self.world_state["attendance"] + int((time.time() % 9) - 4)))

        # Jitter parking
        self.world_state["parking"] = min(100.0, max(0.0, self.world_state["parking"] + (time.time() % 3 - 1) * 0.1))

    def get_state(self) -> Dict[str, Any]:
        self.update_cycle()
        
        # Calculate Advanced Telemetry Metrics
        attendance = self.world_state["attendance"]
        max_capacity = self.world_state["max_capacity"]
        gates = self.world_state["gates"]
        weather = self.world_state["weather"]
        active_alerts = self.world_state["active_alerts"]
        
        crowd_density = round((attendance / max_capacity) * 100, 1)
        parking_util = round(self.world_state["parking"], 1)
        
        # Fan Zone Average Load
        fz = self.world_state["fan_zones"]
        fz_load = round(sum(fz.values()) / len(fz), 1)
        
        # Gate utilization / offline status
        num_gates = len(gates)
        red_gates = sum(1 for status in gates.values() if status == "red")
        yellow_gates = sum(1 for status in gates.values() if status == "yellow")
        gate_util = round(((red_gates * 100 + yellow_gates * 50 + (num_gates - red_gates - yellow_gates) * 20) / num_gates), 1)

        # Weather Risk
        weather_risk = 10
        if weather["lightning"]:
            weather_risk = 95
        elif weather["condition"] == "Thunderstorm":
            weather_risk = 70
        elif weather["temp"] > 35 or weather["temp"] < 5:
            weather_risk = 50

        # Incident Severity & Risk Score
        incident_severity = "LOW"
        risk_score = 15
        
        if active_alerts:
            has_critical = any(a.get("priority") == "critical" for a in active_alerts)
            has_warning = any(a.get("priority") == "warning" for a in active_alerts)
            if has_critical:
                incident_severity = "CRITICAL"
                risk_score = 85
            elif has_warning:
                incident_severity = "HIGH"
                risk_score = 55
        
        # Queue Wait Prediction (Minutes)
        queue_prediction = self.world_state["avg_queue_time"]
        
        # Evacuation Readiness
        evacuation_readiness = 98
        if red_gates > 0:
            evacuation_readiness -= (red_gates * 15)
        if self.world_state["power_status"] == "substation_failure":
            evacuation_readiness -= 20
            
        # Emergency Readiness
        emergency_readiness = 95
        if incident_severity == "CRITICAL":
            emergency_readiness = 80  # high dispatch stress

        # AI Confidence
        ai_confidence = 0.95
        if incident_severity == "CRITICAL":
            ai_confidence = 0.91
            
        # Command Readiness
        command_readiness = 98
        if self.world_state["power_status"] == "substation_failure":
            command_readiness -= 25
        if red_gates > 0:
            command_readiness -= 10
        if incident_severity == "CRITICAL":
            command_readiness -= 10
            
        command_readiness = max(20, command_readiness)
        evacuation_readiness = max(10, evacuation_readiness)

        # Build response priorities description
        response_time = "Normal (No active triage)"
        if incident_severity == "CRITICAL":
            response_time = "3-5 mins (Tactical Rescue & Dispatch)"
        elif incident_severity == "HIGH":
            response_time = "8-10 mins (Urgent Response)"

        metrics = {
            "risk_score": risk_score,
            "crowd_density": crowd_density,
            "incident_severity": incident_severity,
            "queue_prediction": queue_prediction,
            "response_time": response_time,
            "parking_utilization": parking_util,
            "fan_zone_load": fz_load,
            "gate_utilization": gate_util,
            "weather_risk": weather_risk,
            "emergency_readiness": emergency_readiness,
            "evacuation_readiness": evacuation_readiness,
            "ai_confidence": ai_confidence,
            "command_readiness": command_readiness
        }

        return {
            "scenario": self.current_scenario,
            "telemetry": self.world_state,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
