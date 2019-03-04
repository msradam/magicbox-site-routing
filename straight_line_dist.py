# straight_line_dist.py
# Implementation of straight line distance algorithm using balltree
# Author: Adam Munawar Rahman

from csv_utils import *
from nn_utils import *
import sys, os

def straight_line_distance(src_points, tgt_tagged_points, tgt_properties=[]):
    """
    Given a set of source coordinates and a set of tagged target coordinates, 
    and an optional list of target properties:

    Determines the nearest target site for each source site, and outputs
    a list of tuples indexed to the source sites, where for each source site,
    the corresponding tuple:
    (straight line distance to nearest target site, 
     target site identifier,
     <additional properties of target site specified by tgt_properties>)
    """

    print("Determining distances to nearest target sites ... ")
    
    tgt_points = [tagged_vector[0] for tagged_vector in tgt_tagged_points]
    # Uses balltree implementation to return distances to neighbors in meters, calculated with haversine
    nn_indices_and_dists = get_nearest_neighbors(src_points, tgt_points, 1)
    straight_line_dist_data = []
    for ix_and_dist in nn_indices_and_dists:
        ix,dist = ix_and_dist[0]
        tgt_info = tgt_tagged_points[ix]
        info_tuple = (dist, )
        for property in tgt_info[1:]:
            info_tuple += (property, )
        straight_line_dist_data.append(info_tuple)

    print("Completed nearest site calculation for {0} source sites!".format(len(src_points)))

    return(straight_line_dist_data) 

def main():    
    func_args = [arg for arg in sys.argv[1:]]

    src_path = func_args[0]
    tgt_path = func_args[1]
    out_path = func_args[2]
    out_file = func_args[3]
    tgt_properties = func_args[4:]

    updated_filename = os.path.splitext(src_path)[0].split('/')[1]

    try:
        tgt_name = tgt_path.split('_')[2].split('.')[0]
    except:
        try:
            tgt_name = tgt_path.split('-')[2].split('.')[0]
        except:
            tgt_name = "target site"

    col_names = ['Straight line distance to nearest ' + tgt_name + ' (meters)', 
                 'id']

    col_names += tgt_properties

    print("Retrieving latitude longitude points from {0} and {1} ...".format(src_path, tgt_path))
    src_points = [tagged_point[0] for tagged_point in getTaggedPoints(src_path)] 
    tgt_tagged_points = getTaggedPoints(tgt_path, tgt_properties)

    print("Done. Retrieved {0} source coordinates and {1} target coordinates.".format(len(src_points), len(tgt_tagged_points)))

    straight_line_dist_data = straight_line_distance(src_points, tgt_tagged_points, tgt_properties)

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    makeUpdatedCsv(straight_line_dist_data, col_names, src_path, out_path + "/" + out_file + '_updated_straight_line_dist.csv')

if __name__ == "__main__":
    main()