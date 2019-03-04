# site_routing.py
# Implementation of routing algorithms using faster iGraph library
# Author: Adam Munawar Rahman

from csv_utils import *
from nn_utils import *
from functools import reduce
from collections import defaultdict
from tqdm import tqdm

import pickle, sys, os
import igraph as ig
import pathos.multiprocessing as mp

def routed_distance(src_points, tgt_tagged_points, rG, tgt_properties=[]):
    """
    Given a set of source coordinates, a set of tagged target coordinates, 
    an iGraph object, and a list of target properties:

    Determines the nearest target site for each source site, and outputs
    a list of tuples indexed to the source sites, where for each source site,
    the corresponding tuple:
    (straight line distance to nearest target site, 
     routed distance to nearest target site,
     target site identifier,
     <additional properties of target site specified by tgt_properties>)

    """
    num_cores = mp.cpu_count()

    tgt_points = [tagged_point[0] for tagged_point in tgt_tagged_points]
    # Determine the nearest health site through balltree nearest neighbors
    print("Determining smallest straight line distances between sites ... ")
    nn_indices_and_dists = get_nearest_neighbors(src_points, tgt_points, 5)   
    straight_line_dists = [ix_and_dist[0][1] for ix_and_dist in nn_indices_and_dists] 
    # Retrieve the indices and straight line distances of nearest neighbors
    nearest_tgt_indices = [[id[0] for id in ix_and_dist] for ix_and_dist in nn_indices_and_dists]
    for i in tqdm(range(len(nn_indices_and_dists))):
        pass
    print("Done. Determining nearest road points to given sites ... ")
    src_nodes_with_distances  = get_nearest_nodes_ig(rG, src_points)
    tgt_nodes_with_distances  = get_nearest_nodes_ig(rG, tgt_points)
    # The list of target nodes and distances is indexed to the source points
    
    # We maintain a table of distances from source to target road nodes
    # to avoid re-computation
    edge_dist_table = defaultdict(dict)    

    def dist_to_nearest_tgt(i):
        '''
        Given the index of the source node we are currently on, 
        computes distance to nearest target site to that node
        '''
        def epath_to_dist(epath):
            """
            Given a path of edge ID's, returns the distance traversed
            """
            if epath == []:
                return float('inf')
            else:
                return reduce(lambda d1, d2: d1 + d2, list(map(lambda e: rG.es[e]['length'], epath)))

        # If the straight line distance is 2.5 km, based on average human walking speed in 0.5 hour
        # don't determine routed distance since 
        if straight_line_dists[i] < 2500:
            return (straight_line_dists[i], nearest_tgt_indices[i][0])

        else: 
            dist_and_node = src_nodes_with_distances[i]
            src_node, dist_to_src = dist_and_node[0], dist_and_node[1]

            dists = []

            for j in range(len(nearest_tgt_indices[i])):
                current_index = nearest_tgt_indices[i][j]

                tgt_node, node_dist_to_tgt = tgt_nodes_with_distances[j][0], tgt_nodes_with_distances[j][1]

                if src_node in list(edge_dist_table.keys()) and tgt_node in list(edge_dist_table[src_node].keys()):
                    dists.append( (dist_to_src + edge_dist_table[src_node][tgt_node] + node_dist_to_tgt, current_index) )

                else:
                    # We retrieve the list of edges traversed for shortest path to adjust time based on terrain
                    edge_path = list(rG.get_shortest_paths(src_node, to=tgt_node, weights='length', output='epath'))[0]
                    dist = epath_to_dist(edge_path)
                    edge_dist_table[src_node][tgt_node] = dist

                    dists.append( (dist_to_src + dist + node_dist_to_tgt, current_index) )

            if (i % 100 == 0): print("Completed nearest site calculation for {0} source sites!".format(i))

            return min(dists, key = lambda t: t[0])

    print("Initializing routed distance computation on source sites ... ") 
    pool = mp.Pool(processes=num_cores)
    routed_dists = list(pool.map(dist_to_nearest_tgt, tqdm(range(len(src_nodes_with_distances))) ))
    # routed_dists = [dist_to_nearest_tgt(src_nodes_with_distances[i],i) for i in range(len(src_nodes_with_distances)))]
    routed_dist_data = [ (straight_line_dists[i], routed_dists[i][0], ) for i in range(len(src_points)) ]

    for i in range(len(routed_dists)):
        tgt_ix = routed_dists[i][1]
        for property in tgt_tagged_points[tgt_ix][1:]:
            routed_dist_data[i] += (property, )

    return routed_dist_data

def main():    
    func_args = [arg for arg in sys.argv[1:]]

    src_path = func_args[0]
    tgt_path = func_args[1]
    g_path = func_args[2]
    out_path = func_args[3]
    out_file = func_args[4]
    tgt_properties = func_args[5:]

    try:
        tgt_name = tgt_path.split('_')[2].split('.')[0]
    except:
        try:
            tgt_name = tgt_path.split('-')[2].split('.')[0]
        except:
            tgt_name = "target site"

    col_names = ['Straight line distance to nearest ' + tgt_name + ' (meters)', 
                 'Routed distance to nearest ' + tgt_name + ' (meters)', 
                 'id']

    col_names += tgt_properties

    print("Retrieving roads iGraph from " + g_path + " ... ")
    rG = pickle.load( open(g_path, 'rb') )
    for i in tqdm(range(rG.vcount())):
        pass
    print("Done. Retrieved roads graph with {0} edges and {1} vertices.".format(rG.ecount(), rG.vcount()))
    

    print("Retrieving latitude longitude points from {0} and {1} ...".format(src_path, tgt_path))
    src_points = [tagged_point[0] for tagged_point in getTaggedPoints(src_path)] 
    tgt_tagged_points = getTaggedPoints(tgt_path, tgt_properties)
    for i in tqdm(len(src_points)):
        pass
    print("Done. Retrieved {0} source coordinates and {1} target coordinates.".format(len(src_points), len(tgt_tagged_points)))

    routed_dist_data = routed_distance(src_points, tgt_tagged_points, rG, tgt_properties)
    makeUpdatedCsv(routed_dist_data, col_names, src_path, out_path + "/" + out_file  +  '_updated_routed_dist.csv')

    print("Done. Updated file is located at " + out_path + "/" + out_file +  '_updated_routed_dist.csv')

if __name__ == "__main__":
    main()