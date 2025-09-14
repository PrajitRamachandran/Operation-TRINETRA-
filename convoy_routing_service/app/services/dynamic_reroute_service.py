from sqlalchemy.orm import Session
from ..db import crud
from . import ml_engine, convoy_manager, route_optimizer

HIGH_THRESHOLD = 0.75
CRITICAL_THRESHOLD = 0.90

def handle_new_threat(db: Session, threat_id: int):
    """
    The core workflow for handling a new threat.
    """
    threat = db.query(crud.models.ThreatIncident).filter(crud.models.ThreatIncident.id == threat_id).first()
    if not threat:
        return

    # 1. Find and update risk for nearby road segments
    affected_segments = crud.get_segments_near_point(db, threat.location.wkt, 15000) # 15km radius
    for segment in affected_segments:
        features = crud.get_features_for_segment(db, segment.id)
        category, score = ml_engine.predict_segment_risk(features)
        crud.update_segment_risk(db, segment.id, category, score)
        
        # 2. Trigger new alerts if thresholds are crossed
        if score >= CRITICAL_THRESHOLD:
            crud.create_alert(db, segment.id, crud.models.AlertSeverity.CRITICAL,
                              f"CRITICAL risk ({score:.2f}) on segment {segment.id} due to new threat.")
        elif score >= HIGH_THRESHOLD:
            crud.create_alert(db, segment.id, crud.models.AlertSeverity.HIGH,
                              f"HIGH risk ({score:.2f}) on segment {segment.id} due to new threat.")

    # 3. Check for affected active convoys and re-route them
    active_convoys = convoy_manager.get_all_active_convoys()
    affected_segment_ids = {seg.id for seg in affected_segments}
    
    for convoy in active_convoys:
        if any(seg_id in affected_segment_ids for seg_id in convoy.current_path):
            print(f"Re-routing convoy {convoy.call_sign} due to new threat...")
            # Placeholder for D* Lite re-routing logic
            # For now, we'll re-calculate with A* from the current location
            graph = route_optimizer.build_weighted_graph(db, "balance")
            start_node = route_optimizer.find_nearest_node(graph, convoy.current_location)
            end_node = route_optimizer.find_nearest_node(graph, convoy.destination)
            new_path_nodes = route_optimizer.find_astar_path(graph, start_node, end_node)
            
            if new_path_nodes:
                new_segment_ids = route_optimizer.get_path_segment_ids(graph, new_path_nodes)
                convoy_manager.update_convoy(convoy.id, {"status": "Re-routing", "current_path": new_segment_ids})
                # In a real app, a WebSocket push notification would be sent here.