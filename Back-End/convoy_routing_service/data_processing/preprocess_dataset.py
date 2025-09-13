import pandas as pd
import geopandas as gpd
from shapely import wkt

def main():
    print("Preprocessing raw dataset...")
    # Assume a raw CSV with columns: wkt_geom, terrain, road_class, elevation
    # df = pd.read_csv("raw_data/roads.csv")
    # For demo, create a dummy dataframe
    data = {'wkt_geom': ['LINESTRING (10 10, 20 20)', 'LINESTRING (20 20, 30 15)'],
            'terrain': ['forest', 'desert'],
            'road_class': ['primary', 'secondary'],
            'elevation': [100, 150.5]}
    df = pd.DataFrame(data)

    # Convert WKT to geometry objects
    df['geometry'] = gpd.GeoSeries.from_wkt(df['wkt_geom'])
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

    # Save to a file for the loading script
    gdf.to_file("processed_data/processed_roads.geojson", driver='GeoJSON')
    print("Preprocessing complete. Output saved to processed_data/processed_roads.geojson")

if __name__ == "__main__":
    main()