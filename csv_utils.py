import pandas as pd
import numpy as np
import multiprocessing as mp

def getTaggedPoints(csv_path, additional_params=[]):
    df = pd.read_csv(csv_path)
    tagged_points = []
    lat_key, lng_key, id_key = '', '', ''
    for key in list(df):
        key_lower = key.lower()
        if lat_key == '':
            if 'lat' in key_lower or key_lower == 'latitude' or 'features__geometry__coordinates__002' in key_lower or key_lower == 'x':
                lat_key = key
        if lng_key == '':
            if 'lon' in key_lower or key_lower == 'longitude' or 'features__geometry__coordinates__001' in key_lower or key_lower == 'y':
                lng_key = key
        if id_key == '':
            if 'id' in key_lower[-2:] or ' id' in key_lower:
                id_key = key
        else:
            pass

    for i in range(len(df)):
        # Appends a tuple of (id, (lat, lng)) to the list of points
        tagged_point = ()
        if np.isnan(df[lat_key][i]) or np.isnan(df[lng_key][i]):
            tagged_point += ((0.0, 0.0), "no data", )
        else:
            coors = (df[lat_key][i], df[lng_key][i])
            if id_key == '':   
               id = str(i)
            else:
               id = str(df[id_key][i])
            tagged_point += (coors, id, )
            if additional_params != []:
                for param in additional_params:
                    if df[param][i] == 'nan':
                        tagged_point += ("no data", )
                    else:
                        tagged_point += (df[param][i], )
        tagged_points.append( tagged_point )
       
    
    return tagged_points
        

def makeUpdatedCsv(data, column_names, infile, outfile):
    df = pd.read_csv(infile)
    i = 0
    while i < len(column_names):
        col_name = column_names[i]
        column_data = []
        for j in range(len(data)):
            column_data.append(data[j][i])
        df[col_name] = column_data
        i += 1
    df.to_csv(outfile)
