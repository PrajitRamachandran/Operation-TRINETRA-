from apscheduler.schedulers.background import BackgroundScheduler
from .convoy_manager import convoy_manager

# Global simulation state
SIMULATION_TIME_SCALE = 1.0
scheduler = BackgroundScheduler()
scheduler.start()

def set_time_scale(scale: int):
    global SIMULATION_TIME_SCALE
    SIMULATION_TIME_SCALE = float(scale)
    # Reschedule jobs with the new interval
    for job in scheduler.get_jobs():
        job.reschedule(trigger='interval', seconds=10 / SIMULATION_TIME_SCALE)

def run_convoy_movement(convoy_id: str):
    """
    A placeholder function for a background job that simulates convoy movement.
    This would update the convoy's current_location periodically.
    """
    print(f"Simulating movement for convoy {convoy_id}...")
    # In a real simulation, this would pop segments off the path and update the location.
    # For now, we just log that the task is running.
    pass