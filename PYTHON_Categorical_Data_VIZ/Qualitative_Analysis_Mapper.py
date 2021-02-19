#!/usr/bin/env python
# coding: utf-8
import json, math, copy, sys
from geosnap.io import store_ltdb
from geosnap import Community, datasets
from geosnap.io import store_census
import pandas as pd
import shapely.wkt
import shapely.geometry
from datetime import datetime
from datetime import timedelta
from pathlib import Path
import urllib.parse
import webbrowser
import os
import pprint
from sklearn.preprocessing import minmax_scale
import numpy as np
from scipy import stats
from notebook import notebookapp
from IPython.core.display import display, HTML
import geopandas as gpd

def Clustering_viz(param):
    write_INDEX_html(param)
    write_CONFIG_js(param)
    write_VARIABLES_js(param)
    write_GEO_JSON_js(param)
    
    #Create directory for VIZ 
    servers = list(notebookapp.list_running_servers())
    servers1 = 'https://cybergisx.cigi.illinois.edu'+servers[0]["base_url"]+ 'view'
    servers2 = 'https://cybergisx.cigi.illinois.edu'+servers[0]["base_url"]+ 'edit'      
    cwd = os.getcwd()
    prefix_cwd = "/home/jovyan/work"
    cwd = cwd.replace(prefix_cwd, "")
    
    # This is for Jupyter notebbok installed in your PC
    local_dir1 = cwd
    local_dir2 = cwd  
    
    #This is for CyberGISX. Uncomment two command lines below when you run in CyberGIX Environment
    #local_dir1 = servers1 + cwd
    #local_dir2 = servers2 + cwd 
    
    #print(local_dir)
    fname =urllib.parse.quote('index.html')
    template_dir = os.path.join(local_dir1, 'QUAL_' + param['filename_suffix'])
    #url = 'file:' + os.path.join(template_dir, fname)
    url = os.path.join(template_dir, fname)    
    webbrowser.open(url)
    print('To see your visualization, Click the URL below (or locate files):')
    print(url)    
    print('Advanced options are available in ')  
    print(local_dir2 + '/'+ 'QUAL_' + param['filename_suffix']+'/data/CONFIG_' + param['filename_suffix']+'.js')    

    
def write_INDEX_html(param):
    #Create a new folder where GEO_CONFIG.js GEO_JSON.js VARIABLES.js will be saved
    oDir = 'QUAL_' + param['filename_suffix']
    path = Path(oDir + '/data')
    path.mkdir(parents=True, exist_ok=True)
    
    contents = []
    #open Neighborhood_Analysis_Mapper.html (the excutable file for the visualization)
    ifile = open("template/Qualitative_Analysis_Mapper.html", "r", encoding="utf-8")
    contents = ifile.read()
    
    #Replace variables based on the user's selection in each of four files below.
    contents = contents.replace("Neighborhood Analysis Mapper", param['title'])
    contents = contents.replace("data/CONFIG.js", "data/CONFIG_"+param['filename_suffix']+".js")
    contents = contents.replace("data/GEO_JSON.js", "data/GEO_JSON_"+param['filename_suffix']+".js")
    contents = contents.replace("data/VARIABLES.js", "data/VARIABLES_"+param['filename_suffix']+".js")
    
    #write new outfiles: GEO_CONFIG.js GEO_JSON.js VARIABLES.js
    ofile = open(oDir+"/index.html", "w", encoding="utf-8")
    ofile.write(contents)
    ofile.close()
    #print (contents)    
    
def write_CONFIG_js(param):
    # read ACM_GEO_CONFIG.js
    ifile = open("template/QUAL_CONFIG.js", "r", encoding="utf-8")
    contents = ifile.read()
    
    SubjectName = "";
    Maps_of_Categorical_Data = True;               
    Stacked_Chart = True;
    Parallel_Categories_Diagram = True;
    Chord_Diagram = True;
    
    if ('subject' in param): SubjectName =  param['subject']
    if ('Maps_of_Categorical_Data' in param): Maps_of_Categorical_Data =  param['Maps_of_Categorical_Data']
    if ('Stacked_Chart' in param): Stacked_Chart =  param['Stacked_Chart']
    if ('Parallel_Categories_Diagram' in param): Parallel_Categories_Diagram =  param['Parallel_Categories_Diagram']
    if ('Chord_Diagram' in param): Chord_Diagram =  param['Chord_Diagram']
    
    InitialLayers = []
    if (len(param['layers']) <= 1): InitialLayers = []
    for i, year in enumerate(param['layers']):
        InitialLayers.append(str(year))

    NumOfMaps = len(InitialLayers)
    # Automatically set Map_width, Map_height. 
    Map_width = "300px"
    Map_height = "300px"
    if (NumOfMaps <= 6):
        Map_width = "300px"
        Map_height = "300px"	
    if (NumOfMaps <= 5):
        Map_width = "350px"
        Map_height = "350px"
    if (NumOfMaps <= 4):
        Map_width = "400px"
        Map_height = "400px"
    if (NumOfMaps <= 3):
        Map_width = "400px"
        Map_height = "400px"
    if (NumOfMaps <= 2):
        Map_width = "450px"
        Map_height = "450px"
    if (NumOfMaps ==	1):
        Map_width = "800px"
        Map_height = "800px"
    
    # replace newly computed "NumOfMaps", "InitialLayers", "Map_width", "Map_height" in CONFIG.js. See the example replacement below
    InitialLayers = "var InitialLayers = " + json.dumps(InitialLayers) + ";"
    SubjectName = 'var SubjectName = "' + SubjectName + '";'
    Maps_of_Categorical_Data = "var Maps_of_Categorical_Data = " + json.dumps(Maps_of_Categorical_Data)+ ";"
    Stacked_Chart = "var Stacked_Chart = " + json.dumps(Stacked_Chart)+ ";"
    Parallel_Categories_Diagram = "var Parallel_Categories_Diagram = " + json.dumps(Parallel_Categories_Diagram)+ ";"
    Chord_Diagram = "var Chord_Diagram = " + json.dumps(Chord_Diagram)+ ";"
    Map_width = 'var Map_width  = "' + Map_width + '";'
    Map_height = 'var Map_height = "' + Map_height + '";'
    
    contents = contents.replace("var InitialLayers = [];", InitialLayers)
    contents = contents.replace('var SubjectName = "";', SubjectName)
    contents = contents.replace("var Maps_of_Categorical_Data = true;", Maps_of_Categorical_Data)
    contents = contents.replace("var Stacked_Chart = true;", Stacked_Chart)
    contents = contents.replace("var Parallel_Categories_Diagram = true;", Parallel_Categories_Diagram)
    contents = contents.replace("var Chord_Diagram = true;", Chord_Diagram)
    contents = contents.replace('var Map_width  = "400px";', Map_width)
    contents = contents.replace('var Map_height = "400px";', Map_height)
    
    #Write output including the replacement above
    filename_GEO_CONFIG = "QUAL_" + param['filename_suffix'] + "/data/CONFIG_"+param['filename_suffix']+".js"
    ofile = open(filename_GEO_CONFIG, 'w', encoding="utf-8")
    ofile.write(contents)
    ofile.close()    
    #print (contents)        

def write_GEO_JSON_js(param):    
    # read shape file to df_shape
    #df_shapes = gpd.read_file(param['shapefile'])
    #df_shapes = df_shapes.rename(columns={'GEOID10': 'geoid'})
    df_shapes = param['shapefile']
    df_shapes = df_shapes.astype(str)
    geoid = df_shapes.columns[0]
    #print(geoid)
    df_shapes = df_shapes[pd.notnull(df_shapes['geometry'])]
    
    # open GEO_JSON.js write heading for geojson format
    filename_GEO_JSON = "QUAL_" + param['filename_suffix'] + "/data/GEO_JSON_"+param['filename_suffix']+".js"
    ofile = open(filename_GEO_JSON, 'w')
    ofile.write('var GEO_JSON =\n')
    ofile.write('{"type":"FeatureCollection", "features": [\n')
    
    #Convert geometry in GEOJSONP to geojson format
    wCount = 0
    for shape in df_shapes.itertuples():
        feature = {"type":"Feature"}
        if (type(shape.geometry) is float):								# check is NaN?
            #print(tract.geometry)
            continue
        #print(tract.geometry)
        aShape = shapely.wkt.loads(shape.geometry)
        feature["geometry"] = shapely.geometry.mapping(aShape)
        #feature["properties"] = {geoid: tract.__getattribute__(geoid), "tractID": tract.__getattribute__(geoid)}
        feature["properties"] = {geoid: shape.__getattribute__(geoid)}
        wCount += 1
        ofile.write(json.dumps(feature)+',\n')
    #print("GEO_JSON.js write count:", wCount)
    # complete the geojosn format by adding parenthesis at the end.	
    ofile.write(']}\n')
    ofile.close()    
    
    
def write_VARIABLES_js(param):
    #if ('Sequence' not in param or not param['Sequence']): df_pivot.drop(columns=['Sequence'], inplace=True)
    #df_pivot = pd.read_csv(param["inputCSV"])

    df_pivot = param["inputCSV"] 
    geoid = df_pivot.columns 
    #print(df_pivot)     
    #df_pivot.set_index(geoid[0], inplace=True)
    #print(df_pivot) 
    # write df_wide to GEO_VARIABLES.js
    filename_GEO_VARIABLES = "QUAL_" + param['filename_suffix'] + "/data/VARIABLES_"+param['filename_suffix']+".js"
    ofile = open(filename_GEO_VARIABLES, 'w')
    ofile.write('var GEO_VARIABLES =\n')
    ofile.write('[\n')
    
    #heading = [geoid[0]]
    heading = []
    heading.extend(list(map(str, df_pivot.columns.tolist())))
    ofile.write('  '+json.dumps(heading)+',\n')
    wCount = 0
    #for i, row in df_pivot.reset_index().iterrows():
    for i, row in df_pivot.iterrows():        
        aLine = row.tolist()
        for j, col in enumerate(aLine[2:], 2):
            try:
                aLine[j] = int(col)                                  # convert float to int
            except ValueError:
                aLine[j] = -9999                                     # if Nan, set -9999
        wCount += 1 
        ofile.write('  '+json.dumps(aLine)+',\n')
    #print("GEO_VARIABLES.js write count:", wCount)
    ofile.write(']\n')
    ofile.close()
    
if __name__ == '__main__':
    started_datetime = datetime.now()
    dateYYMMDD = started_datetime.strftime('%Y%m%d')
    timeHHMMSS = started_datetime.strftime('%H%M%S')
    print('GEOSNAP2NAM start at %s %s' % (started_datetime.strftime('%Y-%m-%d'), started_datetime.strftime('%H:%M:%S')))

    input_attributes = pd.read_csv("attributes/Cateogrical_data_tract_time.csv")
    #input_attributes.set_index('tractID', inplace=True)
    #input_attributes.set_index('tractID', inplace=True)
    input_attributes
    
    shapefile = gpd.read_file('shp/Cook_County_Tract.shp')
    shapefile = shapefile.rename(columns={'GEOID10': 'tractID'})
    shapefile

    param = {
        'title': "Neighborhood, Cook County (tract level)",
        'subject': "NEIGHBORHOOD",
        'filename_suffix': "Cook_2018_from_ACS_tract_from_file", 
        'layers': [1980,1990,2000, 2010],
        'inputCSV': input_attributes,   
        'shapefile': shapefile, 
        'Maps_of_Categorical_Data': True,                #choropleth map: Maps representing clustering result		
        'Stacked_Chart': True,    #stacked chart: Temporal Change in Neighborhoods over years		
        'Parallel_Categories_Diagram': True,
        'Chord_Diagram': False
    }
    
    #Clustering_viz(param)
    ended_datetime = datetime.now()
    elapsed = ended_datetime - started_datetime
    total_seconds = int(elapsed.total_seconds())
    hours, remainder = divmod(total_seconds,60*60)
    minutes, seconds = divmod(remainder,60)	
    print('GEOSNAP2NAM ended at %s %s    Elapsed %02d:%02d:%02d' % (ended_datetime.strftime('%Y-%m-%d'), ended_datetime.strftime('%H:%M:%S'), hours, minutes, seconds))