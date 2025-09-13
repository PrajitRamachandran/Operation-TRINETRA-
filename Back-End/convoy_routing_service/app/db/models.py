import enum
import datetime
import uuid
from sqlalchemy import (Column, Integer, String, Float, DateTime, Enum as SAEnum, ForeignKey, JSON)
from geoalchemy2 import Geometry
from .database import Base

# Block 3: User Model
class UserRole(str, enum.Enum):
    COMMANDER = "commander"
    OPERATOR = "operator"
    ANALYST = "analyst"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False)

# Block 1: Road & Threat Models
class RoadSegment(Base):
    __tablename__ = 'road_segments'
    id = Column(Integer, primary_key=True, index=True)
    geometry = Column(Geometry(geometry_type='LINESTRING', srid=4326), nullable=False)
    length = Column(Float, nullable=False) # Store pre-calculated length in meters
    terrain_type = Column(String(50))
    road_classification = Column(String(50))
    elevation = Column(Float)
    danger_score = Column(Float, default=0.0) # Continuous score
    risk_category = Column(String(50), default="Low") # Categorical risk

# Block 6: Enhanced Threat Model
class ThreatClassification(str, enum.Enum):
    IED = "ied"
    AMBUSH = "ambush"
    ROADBLOCK = "roadblock"
    SNIPER = "sniper"
    UNKNOWN = "unknown"

class ThreatSource(str, enum.Enum):
    SIGINT = "sigint"
    UAV = "uav"
    HUMINT = "humint"
    MANUAL = "manual"

class VerificationStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    UNCONFIRMED = "unconfirmed"
    FALSE_POSITIVE = "false_positive"

class ThreatIncident(Base):
    __tablename__ = 'threat_incidents'
    id = Column(Integer, primary_key=True, index=True)
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    classification = Column(SAEnum(ThreatClassification), default=ThreatClassification.UNKNOWN)
    source_type = Column(SAEnum(ThreatSource), default=ThreatSource.MANUAL)
    verified_status = Column(SAEnum(VerificationStatus), default=VerificationStatus.UNCONFIRMED)

# Block 3: Alert Model
class AlertSeverity(str, enum.Enum):
    HIGH = "High"
    CRITICAL = "Critical"

class AlertStatus(str, enum.Enum):
    ACTIVE = "Active"
    ACKNOWLEDGED = "Acknowledged"

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, index=True)
    segment_id = Column(Integer, ForeignKey('road_segments.id'))
    severity = Column(SAEnum(AlertSeverity), nullable=False)
    message = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(SAEnum(AlertStatus), default=AlertStatus.ACTIVE)

# Block 7: Completed Mission Model
class CompletedMission(Base):
    __tablename__ = 'completed_missions'
    id = Column(Integer, primary_key=True, index=True)
    convoy_id = Column(String(36), unique=True, nullable=False)
    call_sign = Column(String(50), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, default=datetime.datetime.utcnow)
    total_distance_km = Column(Float)
    final_status = Column(String(50))
    route_taken = Column(JSON)
    alerts_triggered = Column(JSON)