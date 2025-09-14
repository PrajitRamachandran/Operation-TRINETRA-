import geopandas as gpd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from geoalchemy2.functions import ST_Length
from geoalchemy2.types import Geography
import os
import sys

# Add app path to be able to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db.database import Base, engine, SessionLocal
from app.db.models import RoadSegment

def main():
    print("Loading processed data into the database...")
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    
    try:
        gdf = gpd.read_file("processed_data/processed_roads.geojson")
        
        for _, row in gdf.iterrows():
            # Calculate geographic length in meters
            length_meters = db.query(ST_Length(row['geometry'].wkt.cast(Geography))).scalar()
            
            segment = RoadSegment(
                geometry=row['geometry'].wkt,
                length=length_meters,
                terrain_type=row['terrain'],
                road_classification=row['road_class'],
                elevation=row['elevation']
            )
            db.add(segment)
            
        db.commit()
        print(f"Successfully loaded {len(gdf)} road segments.")
    except Exception as e:
        db.rollback()
        print(f"Failed to load data. Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()