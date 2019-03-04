# MagicBox Site Routing
Algorithms for site-to-site-routing for MagicBox data preprocessing.

## Overview
Given a list of points of interest in a country - e.g. a list of schools - we want to find the distance to the nearest other point of interest for each of these sites - e.g. for each school, we want to know the distance to the nearest vaccine delivery center or community health clinic. 

It's trivial to calculate the geographic distance from site-to-site, but more useful information would be distances based on the country's infrastructure network, such as its roads. While two sites may be close to other, infrastructure informs how individuals are able to travel from one to another based on mobility. 

For example, a nearby emergency center may be closer on foot, but it may be safer to travel via car based on the situation (e.g. pregnancy or severe injury), and vehicles are limited to roads. 

## Prep Work
 Country road networks are retrieved from OSMNX and convert to iGraph objects for fast distance calculations. 
 Straight-line distances are computed through a balltree algorithm. 
 See the magicbox-download-roads repository.

## Requirements
 Python 3.7 with the following installed libraries:
 - iGraph
 - OSMNX
 - Numpy, Pandas, Scikit-learn

## Usage with file paths 
 For both routed distance using road network graphs and straight-line distances:
 ```
 python site_routing.py <path to .csv of source sites> <path to .csv of target sites> <path to pickled iGraph> <name of output directory> <target site properties>
 ```
 This will output an updated copy of the source sites .csv, with new columns named "Routed distance to <target type>" and "Straight line distance to <target type>", as well as additional columns based on specified additional properties. The properties must be passed as additional separate arguments, and must match the columns of the target .csv.

 For straight-line distances only:
 ```
 python straight_line_dist.py <path to .csv of source sites> <path to .csv of target sites> <name of output directory> <target site properties>
 ```
 This will output an updated copy of the source sites .csv, with a new column named 'Straight line distance to <target type>', as well as additional columns based on specified additional properties. The properties must be passed as additional separate arguments, and must match the columns of the target .csv.

 Note that the named target type is dependent on how the .csv of target sites is named.

 All distances are in meters. 

 ### Example:
 ```
 python site_routing.py sle_schools.csv sle_healthsites.csv sle_roads_igraph.p type services
 ```

 Outputs "sle_schools_updated_routed_dist.csv" with new columns ""

## Usage in code
 For both routed distance using road network graphs and straight-line distances:
 ```
 from site_routing import routed_distance
 ```
 Function: routed_distance(src_points, tgt_tagged_points, rG, tgt_properties=[])
 Input: A list of source coordinates, a list of tagged target coordinates, an iGraph object, a list of target properties
 Output: routed_dist_data - A list of tuples, where for src_points[i], routed_dist_data[i] is a tuple of the form:
    (straight line distance to nearest target site, 
     routed distance to nearest target site,
     target site identifier,
     <additional properties of target site specified by tgt_properties>)


 For straight-line distances only:
 ```
 from straight_line_dist import straight_line_distance
 ```
 Function: straight_line_distance(src_points, tgt_tagged_points, tgt_properties=[])
 Input: A list of source coordinates, a list of tagged target coordinates a list of target properties
 Output: straight_line_dist_data - A list of tuples, where for src_points[i], straight_line_dist_data[i] is a tuple of the form:
    (straight line distance to nearest target site, 
     target site identifier,
     <additional properties of target site specified by tgt_properties>)

