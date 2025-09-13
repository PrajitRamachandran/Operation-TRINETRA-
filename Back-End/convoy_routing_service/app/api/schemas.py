import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from ..db.models import UserRole, ThreatClassification, ThreatSource, VerificationStatus, AlertSeverity, AlertStatus

# Base Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None

# User Schemas (Block 3 & 7)
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: UserRole

class User(UserBase):
    id: int
    role: UserRole
    class Config:
        from_attributes = True

# Threat Schemas (Block 1 & 6)
class ThreatCreate(BaseModel):
    lat: float
    lon: float
    classification: ThreatClassification
    source_type: ThreatSource
    verified_status: VerificationStatus

class ThreatIncident(ThreatCreate):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

# Route Schemas (Block 4)
class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    mode: str = Field("balance", pattern="^(stealth|speed|balance)$")

class SegmentDetail(BaseModel):
    segment_id: int
    distance_km: float
    risk_score: float

class RouteResponse(BaseModel):
    path_geometry: dict # GeoJSON LineString
    total_distance_km: float
    estimated_fuel_liters: float
    segments: list[SegmentDetail]
    risk_heatmap: list[list[float]]

# Alert Schemas (Block 3)
class Alert(BaseModel):
    id: int
    segment_id: int
    severity: AlertSeverity
    message: str
    timestamp: datetime
    status: AlertStatus
    class Config:
        from_attributes = True

# Convoy Schemas (Block 5)
class SensorState(BaseModel):
    thermal: str = "Nominal"
    comms: str = "Online"
    environment: str = "Clear"

class ActiveConvoy(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    call_sign: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    current_location: tuple[float, float]
    destination: tuple[float, float]
    current_path: list[int]
    speed_kmph: int = 60
    eta: datetime | None = None
    last_update_time: datetime = Field(default_factory=datetime.utcnow)
    sensors: SensorState = Field(default_factory=SensorState)
    status: str = "En Route"

# Mission Schemas (Block 7)
class CompletedMission(BaseModel):
    id: int
    convoy_id: str
    call_sign: str
    start_time: datetime
    end_time: datetime
    total_distance_km: float
    final_status: str
    route_taken: dict
    alerts_triggered: list[dict]
    class Config:
        from_attributes = True

class UserPreferences(BaseModel):
    theme: str = "dark"
    map_style: str = "satellite"
    notification_sound: bool = True