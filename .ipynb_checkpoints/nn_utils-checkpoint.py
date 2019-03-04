import osmnx as ox 
import networkx as nx
import numpy as np 
import pandas as pd 

try:
    from sklearn.neighbors import BallTree
except ImportError as e:
    BallTree = None


def nearest_neighbors_with_distances(src_vectors, dst_vectors):

    srcX = [vector[1] for vector in src_vectors]
    srcY = [vector[0] for vector in src_vectors]

    dstX = [vector[1] for vector in dst_vectors]
    dstY = [vector[0] for vector in dst_vectors]

    if not BallTree:
        raise ImportError('The scikit-learn package must be installed.')
    
    src_points = np.array([srcY, srcX]).T 
    src_points_rad = np.deg2rad(src_points).astype(np.float)
    print(src_points_rad)

    dst_points = np.array([dstY, dstX]).T
    dst_points_rad = np.deg2rad(src_points).astype(np.float)


    tree = BallTree(src_points_rad, metric='haversine')
    di_tuple = tree.query(dst_points_rad, k = 1)

    distances = list(map(lambda r : r * 6371 * 1000, 
                    [dArray[0] for dArray in di_tuple[0]]))    
    indices = [iArray[0] for iArray in di_tuple[1]]

    di_array = [(distances[j],indices[j]) for j in range(len(distances))]

    return(di_array)

def nearest_nodes_with_distances(G, vectors):

    X = [vector[1] for vector in vectors]
    Y = [vector[0] for vector in vectors]

    if not BallTree:
        raise ImportError('The scikit-learn package must be installed.')
    
    nodes = pd.DataFrame({'x':nx.get_node_attributes(G, 'x'),
                          'y':nx.get_node_attributes(G, 'y')})
    nodes_rad = np.deg2rad(nodes[['y', 'x']].astype(np.float))
    points = np.array([Y, X]).T
    points_rad = np.deg2rad(points)

    tree = BallTree(nodes_rad, metric='haversine')
    di_tuple = tree.query(points_rad, k=1)

    distances = list(map(lambda r : r * 6371 * 1000, 
                         [dArray[0] for dArray in di_tuple[0]]))    
    indices = [iArray[0] for iArray in di_tuple[1]]

    di_array = [(distances[j],indices[j]) for j in range(len(distances))]

    return(di_array)