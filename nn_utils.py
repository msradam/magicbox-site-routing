import pandas as pd
import numpy as np

try:
    from sklearn.neighbors import BallTree
except ImportError as e:
    BallTree = None


def get_nearest_neighbors(src_vectors, tgt_vectors, num_neighbors=5):

    if not BallTree:
        raise ImportError('The scikit-learn package must be installed')

    src_latlng = np.radians(np.array(src_vectors))
    tgt_latlng = np.radians(np.array(tgt_vectors))

    tree = BallTree(tgt_latlng, metric='haversine')
    di_tuple = tree.query(src_latlng, k=num_neighbors)

    ix_dist_array = []
    for i in range(len(src_vectors)):
        nn_index_and_dist = []
        for j in range(num_neighbors):
            index  = di_tuple[1][i][j]
            distance = di_tuple[0][i][j] * 6367 * 1000
            nn_index_and_dist.append( (index, distance) )
        ix_dist_array.append(nn_index_and_dist)

    return ix_dist_array




def get_nearest_nodes_ig(G_ig, vectors):
    import igraph as ig

    if not BallTree:
        raise ImportError('The scikit-learn package must be installed')

    points = np.radians(np.array(vectors))

    graph_lats = dict( (v.attributes()['name'], v.attributes()['x']) for v in G_ig.vs )
    graph_lngs = dict( (v.attributes()['name'], v.attributes()['y']) for v in G_ig.vs )

    nodes = pd.DataFrame({'x':graph_lats, 'y':graph_lngs})
    nodes_rad = np.radians(nodes[['y', 'x']].astype(np.float))

    tree = BallTree(nodes_rad, metric='haversine')
    di_tuple = tree.query(points, k=1)
    distances = list(map(lambda r : r * 6367 * 1000, 
                         [dArray[0] for dArray in di_tuple[0]]))
    indices = [iArray[0] for iArray in di_tuple[1]]
    node_dist_array = [(indices[j], distances[j]) for j in range(len(distances))]

    return node_dist_array