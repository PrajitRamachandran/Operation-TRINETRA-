import networkx as nx
from sqlalchemy.orm import Session
from ..db import crud

def get_risk_weight(mode: str) -> float:
    """Returns the risk multiplier based on the operational mode."""
    modes = {"stealth": 20.0, "speed": 5.0, "balance": 10.0}
    return modes.get(mode, 10.0)

def build_weighted_graph(db: Session, mode: str = "balance"):
    """Builds the NetworkX graph with dynamically calculated edge costs."""
    G = nx.Graph()
    segments = crud.get_all_road_segments(db)
    risk_weight = get_risk_weight(mode)

    for seg in segments:
        start_node = seg.geometry.coords[0]
        end_node = seg.geometry.coords[-1]
        cost = seg.length + (seg.danger_score * risk_weight)
        G.add_edge(start_node, end_node, weight=cost, segment_id=seg.id,
                   raw_distance=seg.length, raw_risk=seg.danger_score)
    return G

def find_nearest_node(graph, point_coords):
    """Finds the graph node closest to a given (lon, lat) point."""
    lon, lat = point_coords
    return min(graph.nodes(), key=lambda node: ((node[0] - lon)**2 + (node[1] - lat)**2)**0.5)

def heuristic_distance(a, b):
    """Calculates Euclidean distance for the A* heuristic."""
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5

def find_astar_path(graph, start_node, end_node):
    """Finds the shortest path using the A* algorithm."""
    try:
        return nx.astar_path(graph, source=start_node, target=end_node,
                             heuristic=heuristic_distance, weight='weight')
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None

def get_path_details(graph, path_nodes):
    """Extracts segment details and total distance from a path of nodes."""
    segments = []
    total_distance = 0
    for i in range(len(path_nodes) - 1):
        edge_data = graph.get_edge_data(path_nodes[i], path_nodes[i+1])
        total_distance += edge_data['raw_distance']
        segments.append({
            "segment_id": edge_data['segment_id'],
            "distance_km": edge_data['raw_distance'] / 1000,
            "risk_score": edge_data['raw_risk']
        })
    return {"segments": segments, "total_distance": total_distance}

def get_path_segment_ids(graph, path_nodes):
    """Converts a path of nodes to a list of segment IDs."""
    return [graph.get_edge_data(path_nodes[i], path_nodes[i+1])['segment_id'] 
            for i in range(len(path_nodes) - 1)]