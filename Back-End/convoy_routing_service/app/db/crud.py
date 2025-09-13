from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_Length
from geoalchemy2.types import Geography
from ..api import schemas  # <-- CORRECTED IMPORT (was 'from . import models, schemas')
from . import models
from ..core import security
import random

# User CRUD (Block 3 & 7)
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_all_users(db: Session):
    return db.query(models.User).all()

# Threat CRUD (Block 1, 6, 8)
def create_threat(db: Session, threat: schemas.ThreatCreate):
    db_threat = models.ThreatIncident(
        location=f'POINT({threat.lon} {threat.lat})',
        classification=threat.classification,
        source_type=threat.source_type,
        verified_status=threat.verified_status
    )
    db.add(db_threat)
    db.commit()
    db.refresh(db_threat)
    return db_threat

def get_threats_with_filters(db: Session, status: models.VerificationStatus | None, classification: models.ThreatClassification | None):
    query = db.query(models.ThreatIncident)
    if status:
        query = query.filter(models.ThreatIncident.verified_status == status)
    if classification:
        query = query.filter(models.ThreatIncident.classification == classification)
    return query.all()

def clear_all_threats(db: Session):
    db.query(models.ThreatIncident).delete()
    db.commit()

# Road Segment CRUD (Block 1, 2, 8)
def get_segments_near_point(db: Session, point_wkt: str, radius_meters: int):
    point = func.ST_GeomFromText(point_wkt, 4326)
    return db.query(models.RoadSegment).filter(
        ST_DWithin(
            models.RoadSegment.geometry.cast(Geography),
            point.cast(Geography),
            radius_meters
        )
    ).all()

def update_segment_risk(db: Session, segment_id: int, category: str, score: float):
    db.query(models.RoadSegment).filter(models.RoadSegment.id == segment_id).update(
        {"risk_category": category, "danger_score": score}
    )
    db.commit()

def get_features_for_segment(db: Session, segment_id: int) -> dict | None:
    segment = db.query(models.RoadSegment).filter(models.RoadSegment.id == segment_id).first()
    if not segment:
        return None
    # In a real system, this would calculate dynamic features
    return {
        "terrain": segment.terrain_type,
        "road_class": segment.road_classification,
        "elevation": segment.elevation,
        "threats_within_2km_last_24h": 0, # Placeholder
    }

def get_all_road_segments(db: Session):
    return db.query(models.RoadSegment).all()
    
def get_random_nodes(db: Session):
    # This is a simplified way to get random start/end points for simulation
    segment1 = db.query(models.RoadSegment).order_by(func.rand()).first()
    segment2 = db.query(models.RoadSegment).filter(models.RoadSegment.id != segment1.id).order_by(func.rand()).first()
    return segment1.geometry.coords[0], segment2.geometry.coords[-1]

def reset_all_risk_scores(db: Session):
    db.query(models.RoadSegment).update({"danger_score": 0.0, "risk_category": "Low"})
    db.commit()

# Alert CRUD (Block 3, 6, 8)
def create_alert(db: Session, segment_id: int, severity: models.AlertSeverity, message: str):
    db_alert = models.Alert(segment_id=segment_id, severity=severity, message=message)
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def get_alerts_by_status(db: Session, status: models.AlertStatus):
    return db.query(models.Alert).filter(models.Alert.status == status).all()

def update_alert_status(db: Session, alert_id: int, status: models.AlertStatus):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if alert:
        alert.status = status
        db.commit()
        db.refresh(alert)
    return alert

def get_alert_count(db: Session, status: models.AlertStatus):
    return db.query(models.Alert).filter(models.Alert.status == status).count()

def clear_all_alerts(db: Session):
    db.query(models.Alert).delete()
    db.commit()

# Mission CRUD (Block 7)
def create_completed_mission(db: Session, mission_data: dict):
    db_mission = models.CompletedMission(**mission_data)
    db.add(db_mission)
    db.commit()
    db.refresh(db_mission)
    return db_mission

def get_all_completed_missions(db: Session):
    return db.query(models.CompletedMission).all()

def get_completed_mission(db: Session, mission_id: int):
    return db.query(models.CompletedMission).filter(models.CompletedMission.id == mission_id).first()

# Geospatial Helper Functions
def calculate_distance(db: Session, geom1, geom2):
    return db.query(ST_Distance(geom1.cast(Geography), geom2.cast(Geography))).scalar()

def generate_threat_density_grid(db: Session):
    # Placeholder for a more complex geospatial aggregation query
    threats = db.query(models.ThreatIncident.location).filter(models.ThreatIncident.verified_status == 'confirmed').all()
    return [[threat.location.y, threat.location.x, 1] for threat in threats]