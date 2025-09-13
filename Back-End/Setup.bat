@echo off
REM Batch script to generate folder structure for convoy_routing_service

REM Root folder
mkdir convoy_routing_service
cd convoy_routing_service

REM App folder and subfolders
mkdir app
cd app
type nul > __init__.py
type nul > main.py

mkdir api
cd api
type nul > __init__.py
type nul > dependencies.py
type nul > endpoints.py
type nul > schemas.py
type nul > websockets.py
cd ..

mkdir core
cd core
type nul > __init__.py
type nul > config.py
type nul > security.py
cd ..

mkdir db
cd db
type nul > __init__.py
type nul > crud.py
type nul > database.py
type nul > models.py
cd ..

mkdir services
cd services
type nul > __init__.py
type nul > convoy_manager.py
type nul > dynamic_reroute_service.py
type nul > ml_engine.py
type nul > report_generator.py
type nul > route_optimizer.py
type nul > simulation_service.py
cd ..\..

REM Data processing folder
mkdir data_processing
cd data_processing
type nul > __init__.py
type nul > load_data_to_db.py
type nul > preprocess_dataset.py
cd ..

REM Models folder
mkdir models
cd models
type nul > placeholder.txt
cd ..

REM Tests folder
mkdir tests
cd tests
type nul > placeholder.txt
cd ..

REM Root files
cd ..
type nul > .env
type nul > requirements.txt

echo Folder structure created successfully!
pause
