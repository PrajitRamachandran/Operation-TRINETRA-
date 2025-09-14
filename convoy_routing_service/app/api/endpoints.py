import uuid
from typing import Annotated
from fastapi import (APIRouter, Depends, HTTPException, status, Query, BackgroundTasks,
                     WebSocket, Path, WebSocketDisconnect)
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import io

from .. import services
from ..db import crud, database, models
from ..api import schemas, dependencies, websockets
from ..core import security

router = APIRouter(prefix="/api/v1")

# --- Block 3 & 7: Authentication and User Management ---
@router.post("/login", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(db: Session = Depends(database.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = security.create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users", status_code=201, response_model=schemas.User, dependencies=[Depends(dependencies.is_commander)], tags=["Admin - Settings"])
def create_new_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)
    
@router.get("/users", response_model=list[schemas.User], dependencies=[Depends(dependencies.is_commander)], tags=["Admin - Settings"])
def list_users(db: Session = Depends(database.get_db)):
    return crud.get_all_users(db)

# --- Block 4 & 8: Core Routing API ---
@router.post("/get_route", response_model=schemas.RouteResponse, dependencies=[Depends(dependencies.is_operator_or_commander)], tags=["Core API"])
def get_optimized_route(request: schemas.RouteRequest, db: Session = Depends(database.get_db)):
    graph = services.route_optimizer.build_weighted_graph(db, request.mode)
    start_node = services.route_optimizer.find_nearest_node(graph, (request.start_lon, request.start_lat))
    end_node = services.route_optimizer.find_nearest_node(graph, (request.end_lon, request.end_lat))
    path_nodes = services.route_optimizer.find_astar_path(graph, start_node, end_node)
    
    if not path_nodes:
        raise HTTPException(status_code=404, detail="No path found.")
        
    path_details = services.route_optimizer.get_path_details(graph, path_nodes)
    # Mocking external map service integration and fuel calculation
    fuel_estimate = (path_details['total_distance'] / 1000) * 0.2 # 0.2L per km
    heatmap_data = [[seg['risk_score'], *graph.nodes[node]['pos']] for node in path_nodes for seg in path_details['segments']]
    
    return {
        "path_geometry": {"type": "LineString", "coordinates": path_nodes},
        "total_distance_km": path_details['total_distance'] / 1000,
        "estimated_fuel_liters": fuel_estimate,
        "segments": path_details['segments'],
        "risk_heatmap": heatmap_data
    }

# --- Block 6 & 8: Threat Intelligence ---
@router.post("/update_threat", status_code=201, response_model=schemas.ThreatIncident, dependencies=[Depends(dependencies.is_analyst_or_commander)], tags=["Core API"])
async def update_threat_intelligence(threat_data: schemas.ThreatCreate, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    new_threat = crud.create_threat(db, threat_data)
    background_tasks.add_task(services.dynamic_reroute_service.handle_new_threat, db, new_threat.id)
    return new_threat

@router.get("/threats", response_model=list[schemas.ThreatIncident], dependencies=[Depends(dependencies.is_analyst_or_commander)], tags=["Threat Intelligence"])
def get_all_threats(
    status: Annotated[models.VerificationStatus | None, Query()] = None,
    classification: Annotated[models.ThreatClassification | None, Query()] = None,
    db: Session = Depends(database.get_db)
):
    return crud.get_threats_with_filters(db, status=status, classification=classification)
    
@router.get("/threat_heatmap", dependencies=[Depends(dependencies.is_analyst_or_commander)], tags=["Threat Intelligence"])
def get_threat_heatmap_data(db: Session = Depends(database.get_db)):
    return crud.generate_threat_density_grid(db)

# --- Block 3, 6, 8: Alerts ---
@router.get("/alerts", response_model=list[schemas.Alert], dependencies=[Depends(dependencies.is_operator_or_commander)], tags=["Core API"])
def get_active_alerts(db: Session = Depends(database.get_db)):
    return crud.get_alerts_by_status(db, status=models.AlertStatus.ACTIVE)

@router.post("/alerts/acknowledge/{alert_id}", status_code=200, dependencies=[Depends(dependencies.is_operator_or_commander)], tags=["Alerts"])
def acknowledge_alert(alert_id: int, db: Session = Depends(database.get_db)):
    alert = crud.update_alert_status(db, alert_id, models.AlertStatus.ACKNOWLEDGED)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return {"message": f"Alert {alert_id} has been acknowledged."}

# --- Block 5: Convoy Monitoring & Emergency Controls ---
@router.get("/convoy_status/{convoy_id}", response_model=schemas.ActiveConvoy, dependencies=[Depends(dependencies.is_operator_or_commander)], tags=["Convoy Monitoring"])
async def get_convoy_status(convoy_id: uuid.UUID):
    convoy = services.convoy_manager.get_convoy(convoy_id)
    if not convoy:
        raise HTTPException(status_code=404, detail="Convoy not found.")
    return convoy

@router.post("/convoy/{convoy_id}/stop", dependencies=[Depends(dependencies.is_commander)], tags=["Emergency Controls"])
async def command_convoy_stop(convoy_id: uuid.UUID):
    updated_convoy = services.convoy_manager.update_convoy(convoy_id, {"status": "Halted"})
    if not updated_convoy:
        raise HTTPException(status_code=404, detail="Convoy not found.")
    return {"message": "Stop command issued."}
# (Other emergency controls would follow the same pattern)

@router.websocket("/ws/convoy_updates/{convoy_id}")
async def websocket_endpoint(websocket: WebSocket, convoy_id: uuid.UUID = Path(...)):
    await websockets.manager.connect(convoy_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websockets.manager.disconnect(convoy_id, websocket)

# --- Block 7: Mission Reports & System Status ---
@router.get("/missions", response_model=list[schemas.CompletedMission], dependencies=[Depends(dependencies.is_analyst_or_commander)], tags=["Mission Reports"])
def list_completed_missions(db: Session = Depends(database.get_db)):
    return crud.get_all_completed_missions(db)

@router.get("/missions/{mission_id}/report", dependencies=[Depends(dependencies.is_analyst_or_commander)], tags=["Mission Reports"])
def generate_mission_report(mission_id: int, format: str = "pdf", db: Session = Depends(database.get_db)):
    mission = crud.get_completed_mission(db, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found.")
    if format == "pdf":
        pdf_bytes = services.report_generator.create_mission_pdf(mission)
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf")
    # (CSV logic would be similar)
    raise HTTPException(status_code=400, detail="Unsupported format.")

@router.get("/system_status", tags=["System Status"])
def get_system_status(db: Session = Depends(database.get_db)):
    # ... Implementation from Block 7 ...
    return {"status": "Online"}

# --- Block 8: Simulation & ML ---
@router.post("/simulate_mission", status_code=202, dependencies=[Depends(dependencies.is_analyst_or_commander)], tags=["Simulation"])
async def simulate_random_mission(background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    # ... Implementation from Block 8 ...
    return {"message": "New mission simulation started."}

@router.post("/reset_demo", dependencies=[Depends(dependencies.is_commander)], tags=["Simulation"])
def reset_demo_environment(db: Session = Depends(database.get_db)):
    services.convoy_manager.clear_all_convoys()
    crud.clear_all_threats(db)
    crud.clear_all_alerts(db)
    crud.reset_all_risk_scores(db)
    return {"message": "Demonstration environment has been reset."}