#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

import json, math, copy
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
import numpy as np
from notebook import notebookapp
from IPython.core.display import display, HTML
import geopandas as gpd

def write_LOG(param):
    #Create a new folder where GEO_CONFIG.js GEO_JSON.js VARIABLES.js will be saved
    oDir = 'ACM_' + param['filename_suffix']
    path = Path(oDir + '/data')
    path.mkdir(parents=True, exist_ok=True)
    
    contents = pprint.pformat(param)
    #print(oDir+"/data/param.log")
    #print(contents)
    #write new outfiles: GEO_CONFIG.js GEO_JSON.js VARIABLES.js
    ofile = open(oDir+"/data/param.log", "w", encoding="utf-8")
    create_at = datetime.now()
    ofile.write('%s %s\r\n' % (create_at.strftime('%Y-%m-%d'), create_at.strftime('%H:%M:%S')))
    #ofile.write('\r\n\r\n')
    ofile.write('  '+contents.replace('\n', '\n  '))
    ofile.close()

def write_INDEX_html(param):
    
    #Create a new folder where CONFIG.js GEO_JSON.js VARIABLES.js will be saved
    oDir = 'ACM_' + param['filename_suffix']
    path = Path(oDir + '/data')
    path.mkdir(parents=True, exist_ok=True)
    
    contents = []
    #open Adaptive_Choropleth_Mapper.html (the excutable file for the visualization)
    ifile = open("template/Adaptive_Choropleth_Mapper.html", "r", encoding="utf-8")
    contents = ifile.read()
    
    #Replace variables based on the user's selection in each of four files below.
    contents = contents.replace("Adaptive Choropleth Mapper", param['title'])
    contents = contents.replace("data/CONFIG.js", "data/CONFIG_"+param['filename_suffix']+".js")
    contents = contents.replace("data/GEO_JSON.js", "data/GEO_JSON_"+param['filename_suffix']+".js")
    contents = contents.replace("data/VARIABLES.js", "data/VARIABLES_"+param['filename_suffix']+".js")
    
    #write new outfiles: CONFIG.js GEO_JSON.js VARIABLES.js
    ofile = open(oDir+"/index.html", "w")
    ofile.write(contents)
    ofile.close()


def write_CONFIG_js(param):
    # read CONFIG.js
    ifile = open("template/CONFIG.js", "r", encoding="utf-8")
    contents = ifile.read()
    
    # Automatically identify variables for "NumOfMaps" and "InitialLayers"
    '''when the user selects more than one year among 1970, 1980, 1990, 200 and 2010, "NumOfMaps" will be equal to the number of the selected years. However, when the user selects only one year among 5 years, "NumOfMaps" will be the number of variables that the user selected. (The maximum number of maps that can be visualized is 15) In this case, when the user selects more than 15 variables, the first 15 maps will be created at the initial view, and the rest of variables will be available in the dropdown box of the top of each map. In brief, there is no limit in terms of variables that the user can visualize, but the user can visualize upto 15 maps at the same time.'''
    NumOfMaps = len(param['years'])
    chart = param['chart'] if 'chart' in param else ''
    if (chart == "Scatter Plot"): NumOfMaps = 2
    InitialLayers = []
    if (NumOfMaps > 1):
        for i, year in enumerate(param['years']):
            InitialLayers.append(str(year)+' '+param['labels'][0])
    else:
        NumOfMaps = len(param['labels'])
        if ('NumOfMaps' in param): NumOfMaps = param['NumOfMaps']
        if (NumOfMaps > 15): NumOfMaps = 15
        for i, variable in enumerate(param['labels']):
            InitialLayers.append(str(param['years'][0])+' '+variable)
    
    # Automatically set Map_width, Map_height. 
    Map_width = "350px"
    Map_height = "350px"
    if (NumOfMaps <= 5):
        Map_width = "400px"
        Map_height = "400px"
    if (NumOfMaps <= 4):
        Map_width = "500px"
        Map_height = "500px"
    if (NumOfMaps <= 3):
        Map_width = "650px"
        Map_height = "650px"
    if (NumOfMaps <= 1):
        Map_width = "1000px"
        Map_height = "1000px"
        
    # replace newly computed "NumOfMaps", "InitialLayers", "Map_width", "Map_height" in CONFIG.js. See the example replacement below
    '''
        NumOfMaps  :    4                ->    'var NumOfMaps = 4;'
        InitialLayers   :    [ … ]            ->    'var InitialLayers = ["1980 p_nonhisp_white_persons", "1980 p_nonhisp_black_persons", "1980 p_hispanic_persons", … ];'
        Map_width    :    "400px"    ->    'var Map_width = "400px";'
        Map_height   :    "400px"    ->    'var Map_height = "400px";'
    '''
    NumOfMaps = "var NumOfMaps = " + str(NumOfMaps) + ";"
    InitialLayers = "var InitialLayers = " + json.dumps(InitialLayers) + ";"
    Map_width = 'var Map_width  = "' + Map_width + '";'
    Map_height = 'var Map_height  = "' + Map_height + '";'
   
    contents = contents.replace("var NumOfMaps = 1;", NumOfMaps)
    contents = contents.replace("var InitialLayers = [];", InitialLayers)
    contents = contents.replace('var Map_width  = "400px";', Map_width)
    contents = contents.replace('var Map_height = "400px";', Map_height)
    
    chart = param['chart'] if 'chart' in param else ''
    #print('chart: ' + chart )
    #print(chart == "Stacked Chart")
    
    Stacked_Chart = "var Stacked_Chart = false;"
    Correlogram = "var Correlogram = false;"
    Scatter_Plot = "var Scatter_Plot = false;"
    Parallel_Coordinates_Plot = "var Parallel_Coordinates_Plot = false;"
    
    if (chart == "Stacked Chart"): Stacked_Chart = "var Stacked_Chart = true;"
    elif (chart == "Correlogram"): Correlogram = "var Correlogram = true;"
    elif (chart == "Scatter Plot"): Scatter_Plot = "var Scatter_Plot = true;"
    elif (chart == "Parallel Coordinates Plot"): Parallel_Coordinates_Plot = "var Parallel_Coordinates_Plot = true;"
    else: Stacked_Chart = "var Stacked_Chart = false;"
   
    contents = contents.replace("var Stacked_Chart = false;", Stacked_Chart)
    contents = contents.replace("var Correlogram = false;", Correlogram)
    contents = contents.replace("var Scatter_Plot = false;", Scatter_Plot)
    contents = contents.replace("var Parallel_Coordinates_Plot = false;", Parallel_Coordinates_Plot)

    #Write output including the replacement above
    filename_CONFIG = "ACM_" + param['filename_suffix'] + "/data/CONFIG_"+param['filename_suffix']+".js"
    ofile = open(filename_CONFIG, 'w')
    ofile.write(contents)
    ofile.close()


def write_GEO_JSON_js(community, param):
    # query geometry for each tract
    geoid = community.gdf.columns[0]
    tracts = community.gdf[[geoid, 'geometry']].copy()
    tracts.drop_duplicates(subset=geoid, inplace=True)                    # get unique geoid
    #print(tracts)
    
    # open GEO_JSON.js write heading for geojson format
    filename_GEO_JSON = "ACM_" + param['filename_suffix'] + "/data/GEO_JSON_"+param['filename_suffix']+".js"
    ofile = open(filename_GEO_JSON, 'w')
    ofile.write('var GEO_JSON =\n')
    ofile.write('{"type":"FeatureCollection", "features": [\n')
    
    #Convert geometry in GEOJSONP to geojson format
    for tract in tracts.itertuples():
        feature = {"type":"Feature"}
        if (tract.geometry is None):                                # check is NaN?
            #print(tract.geometry)
            continue
        feature["geometry"] = shapely.geometry.mapping(tract.geometry)
        #feature["properties"] = {geoid: tract.__getattribute__(geoid), "tractID": tract.__getattribute__(geoid)}
        feature["properties"] = {geoid: tract.__getattribute__(geoid)}
        ofile.write(json.dumps(feature)+',\n')
    # complete the geojosn format by adding parenthesis at the end.    
    ofile.write(']}\n')
    ofile.close()


def write_VARIABLES_js(community, param):
    #print(param)    
    geoid        =  community.gdf.columns[0]
    years        =  param['years']
    variables    =  param['variables']
    
    ## filtering by years
    #community.gdf = community.gdf[community.gdf.year.isin(years)]
    #print(community.gdf)
    #selectedCommunity = community.gdf[variables]
    #print(community.gdf)
    #return
    
    #make heading: community.gdf.columns[0] has "geoid" (string)
    heading = [geoid]
    for i, year in enumerate(years):
        for j, variable in enumerate(param['labels']):
            heading.append(str(year)+' '+variable)
    
    #Make Dictionary
    mydictionary = {}    # key: geoid, value: variables by heading
    h = -1
    selectedColumns = [geoid]
    selectedColumns.extend(variables)
    #print("selectedColumns:", type(selectedColumns), selectedColumns)
    for i, year in enumerate(years):
        aYearDF = community.gdf[community.gdf.year==year][selectedColumns]
        #print(year, type(aYearDF), aYearDF)
        for j, variable in enumerate(variables):
            h += 1
            for index, row in aYearDF.iterrows():
                #print(index, row)
                key = row[geoid]
                val = row[variable]
                if (math.isnan(val)): #converts Nan in GEOSNAP data to -9999
                    #print(i, j, key, year, val)
                    val = -9999
                if (key in mydictionary):
                    value = mydictionary[key]
                    value[h] = val
                else:
                    value = [-9999] * (len(heading) - 1)                
                    value[h] = val
                mydictionary[key] = value
                
    #Select keys in the Dictionary and sort
    keys = list(mydictionary.keys())
    keys.sort()
    # use Keys and Dictionary created above and write them VARIABLES.js
    filename_VARIABLES = "ACM_" + param['filename_suffix'] + "/data/VARIABLES_"+param['filename_suffix']+".js"
    ofile = open(filename_VARIABLES, 'w')
    ofile.write('var GEO_VARIABLES =\n')
    ofile.write('[\n')
    ofile.write('  '+json.dumps(heading)+',\n')
    for i, key in enumerate(keys):
        values = mydictionary[key]
        values.insert(0, key)
        #print(key, values)
        ofile.write('  '+json.dumps(values)+',\n')
    ofile.write(']\n')
    ofile.close()


def Adaptive_Choropleth_Mapper_viz(param):
    
    # convert year, variable to years, variables in the param
    if ('years' not in param and 'year' in param): param['years'] = [param['year']]
    if ('years' not in param and 'year' not in param and 'periods' in param): param['years'] = param['periods']
    if ('years' not in param and 'year' not in param and 'periods' not in param and 'period' in param): param['years'] = [param['period']]
    if ('variables' not in param and 'variable' in param): param['variables'] = [param['variable']]
    #print(param['years'])
    
    # select community by state_fips, msa_fips, county_fips
    community = None
    if ('msa_fips' in param and param['msa_fips']):
        community = Community.from_ltdb(years=param['years'], msa_fips=param['msa_fips'])
        #community = Community.from_ltdb(msa_fips=param['msa_fips'])
    elif ('county_fips' in param and param['county_fips']):
        community = Community.from_ltdb(years=param['years'], county_fips=param['county_fips'])
    elif ('state_fips' in param and param['state_fips']):
        community = Community.from_ltdb(years=param['years'], state_fips=param['state_fips'])
    #print(community.gdf)

# if the user enters CSV and shapefile, use the files from the user

#### This is executed when the user enter attributes in csv file and geometroy in shapefile ######################  
    if (community is None and 'inputCSV' in param):
        community = Community()
        #community.gdf = pd.read_csv(param['inputCSV'], dtype={'geoid':str})
        community.gdf = param["inputCSV"]
        #print(community.gdf)
        geoid = community.gdf.columns[0]
        #community.gdf = community.gdf.astype(str)
        #print("inputCSV:  " + community.gdf.geoid)        
        community.gdf[community.gdf.columns[0]] = community.gdf[geoid].astype(str)
        #print("community.gdf.columns[0]:", community.gdf.columns[0])
        
        # read shape file to df_shape
        #df_shape = gpd.read_file(param['shapefile'])
        df_shape = param['shapefile']
        df_shape = df_shape.astype(str)     
        #print("shapefile:  " + df_shape.GEOID10)
        geokey = df_shape.columns[0]
        #print(geokey)    
        df_shape = df_shape.set_index(geokey)
        
        # insert geometry to community.gdf
        geometry = []
        for index, row in community.gdf.iterrows():
            tractid = row[geoid]
            try:
                tract = df_shape.loc[tractid]
                geometry.append(shapely.wkt.loads(tract.geometry))
            except KeyError:
                #print("Tract ID [{}] is not found in the shape file {}".format(tractid, param['shapefile']))
                geometry.append(None)
       # print( "geometry" in community.gdf )        
        #f hasattr(community.gdf, "geoemtry"):
        #if (community.gdf["geoemtry"] is None):
        #   pass 
        #else:
        if(("geometry" in community.gdf) == False):
            community.gdf.insert(len(community.gdf.columns), "geometry", geometry)
        community.gdf.rename(columns={'period':'year'}, inplace=True)
        #print(community.gdf)
################################################################################################################      
    
    community.gdf = community.gdf.replace([np.inf, -np.inf], np.nan)
    # check if geometry is not null for Spatial Clustering  
    community.gdf = community.gdf[pd.notnull(community.gdf['geometry'])]
    #print(community.gdf)

    codebook = pd.read_csv('template/conversion_table_codebook.csv')
    codebook.set_index(keys='variable', inplace=True)
    labels = copy.deepcopy(param['variables'])
    label = 'short_name'                                             # default
    if (param['label'] == 'variable'): label = 'variable'
    if (param['label'] == 'full_name'): label = 'full_name'
    if (param['label'] == 'short_name'): label = 'short_name'
    if (label != 'variable'):
        for idx, variable in enumerate(param['variables']):
            try:
                codeRec = codebook.loc[variable]
                labels[idx] = codeRec[label]
            except:
                print("variable not found in codebook.  variable:", variable)
    param['labels'] = labels
    
    write_INDEX_html(param)
    write_CONFIG_js(param)
    write_VARIABLES_js(community, param)
    write_GEO_JSON_js(community, param)
    
    '''
    #Create directory for local machine
    local_dir = os.path.dirname(os.path.realpath(__file__))
    fname =urllib.parse.quote('index.html')
    template_dir = os.path.join(local_dir, 'ACM_' + param['filename_suffix'])
    url = 'file:' + os.path.join(template_dir, fname)
    webbrowser.open(url)
    
    print('Please run ' + '"ACM_' + param['filename_suffix']+'/index.html"'+' to your web browser.')
    print('Advanced options are available in ' + '"ACM_' + param['filename_suffix']+'/data/CONFIG.js"')
    '''

    #Create directory for Visualization    
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
    template_dir = os.path.join(local_dir1, 'ACM_' + param['filename_suffix'])
    #url = 'file:' + os.path.join(template_dir, fname)
    url = os.path.join(template_dir, fname)    
    webbrowser.open(url)
    print('To see your visualization, click the URL below (or locate the files):')
    print(url)    
    print('Advanced options are available in ')  
    print(local_dir2 + '/'+ 'ACM_' + param['filename_suffix']+'/data/CONFIG_' + param['filename_suffix']+'.js')       
    
    
if __name__ == '__main__':
    started_datetime = datetime.now()
    dateYYMMDD = started_datetime.strftime('%Y%m%d')
    timeHHMMSS = started_datetime.strftime('%H%M%S')
    print('This program started at %s %s' % (started_datetime.strftime('%Y-%m-%d'), started_datetime.strftime('%H:%M:%S')))
    
    #sample = "downloads/LTDB_Std_All_Sample.zip"
    #full = "downloads/LTDB_Std_All_fullcount.zip"
    #store_ltdb(sample=sample, fullcount=full)
    #store_census()
    #geosnap.io.store_census()

    input_attributes = pd.read_csv("attributes/Chicago_1980_1990_2000_2010.csv", dtype={'geoid':str})
    input_attributes = input_attributes.rename(columns={'geoid': 'tractID'})
    shapefile = gpd.read_file("shp/Cook_County_Tract.shp")
    shapefile = shapefile.rename(columns={'GEOID10': 'tractID'})

    param = {
        'title': "Adaptive Choropleth Mapper with Scatter Plot",
        'filename_suffix': "Chicago_ACM_Scatter",
        'inputCSV': input_attributes,   
        'shapefile': shapefile, 
        'year': 2000,
        'label': "short_name", #Pick variable,short_name,full_name from template/conversion_table_codebook.csv         
        'variables': [         #enter variable names of the column you selected above.
            "p_nonhisp_white_persons",
            "p_nonhisp_black_persons",
            "p_hispanic_persons",
            "p_asian_persons",
            "p_foreign_born_pop",
            "p_edu_college_greater",
            "p_unemployment_rate",
            "p_employed_manufacturing",
            "p_poverty_rate",
            "p_vacant_housing_units",
            "p_owner_occupied_units",
            "p_housing_units_multiunit_structures",
            "median_home_value",
            "p_structures_30_old",
            "p_household_recent_move",
            "p_persons_under_18",
            "p_persons_over_60",     
        ],
        'chart': "Scatter Plot", 
    }
    
    input_attributes = pd.read_csv("attributes/Chicago_1980_1990_2000_2010.csv", dtype={'geoid':str})
    input_attributes = input_attributes.rename(columns={'geoid': 'tractID'})
    shapefile = gpd.read_file("shp/Cook_County_Tract.shp")
    shapefile = shapefile.rename(columns={'GEOID10': 'tractID'})

    param1 = {
        'title': "Adaptive Choropleth Mapper with Correlogram",
        'filename_suffix': "Chicago_ACM_Correlogram",
        'inputCSV': input_attributes,   
        'shapefile': shapefile,
        'period': 2010,
        'NumOfMaps': 4,    
        'label': "short_name", #Pick variable,short_name,full_name from template/conversion_table_codebook.csv         
        'variables': [         #enter variable names of the column you selected above.
            "p_nonhisp_white_persons",
            "p_nonhisp_black_persons",
            "p_hispanic_persons",
            "p_asian_persons",          
            "p_other_language",
            "p_female_headed_families",
            "median_income_blackhh",
            "median_income_hispanichh",
            "median_income_asianhh",
            "per_capita_income",     
        ],
        'chart': "Correlogram", 
    }
    
    input_attributes = pd.read_csv("attributes/Copy of San_Diego_ACS_2010.csv", dtype={'geoid':str})
    shapefile = gpd.read_file("shp/San_Diego2010.shp")
    
    param2 = {
            'title': "Adaptive Choropleth Mapper with Correlogram",
            'filename_suffix': "SD_correlogram",
            'state_fips': None,
            'msa_fips': "41740",  #For more options: http://osnap.cloud/~suhan/LNE/pick_POI.html
            'county_fips': None,
            'year': 2000,
            'NumOfMaps': 6,
            'variables': [
                "p_other_language",
                "p_female_headed_families",
                "median_income_blackhh",
                "median_income_hispanichh",
                "median_income_asianhh",
                "per_capita_income",      
            ],
            'chart': "Correlogram",
            'label': "short_name",                                       # variable, short_name or full_name
    }
    input_attributes = pd.read_csv("attributes/Copy of San_Diego_ACS_2010.csv", dtype={'geoid':str})
    shapefile = gpd.read_file("shp/San_Diego2010.shp")

    param3 = {
            'title': "Adaptive Choropleth Mapper with Correlogram",
            'filename_suffix': "SD_correlogram_from_csv",
            'inputCSV': input_attributes,   
            'shapefile': shapefile,
            'year': 2000,
            'NumOfMaps': 6,
            'variables': [
                "p_other_language",
                "p_female_headed_families",
                "median_income_blackhh",
                "median_income_hispanichh",
                "median_income_asianhh",
                "per_capita_income",     
            ],
            'label': "short_name",                                       # variable, short_name or full_name
            #'chart': "Stacked Chart",    
            #'chart': "Correlogram",
            #'chart': "Scatter Plot",   
            #'chart': "Parallel Coordinates Plot",       
    }
    
    Adaptive_Choropleth_Mapper_viz(param)
    
    ended_datetime = datetime.now()
    elapsed = ended_datetime - started_datetime
    total_seconds = int(elapsed.total_seconds())
    hours, remainder = divmod(total_seconds,60*60)
    minutes, seconds = divmod(remainder,60)    
    print('This program ended at %s %s    Elapsed %02d:%02d:%02d' % (ended_datetime.strftime('%Y-%m-%d'), ended_datetime.strftime('%H:%M:%S'), hours, minutes, seconds))
    