#!/usr/bin/env python
# coding: utf-8
import json, math, copy, sys, re
import pandas as pd
import shapely.wkt
import shapely.geometry
from datetime import datetime, timezone
from datetime import timedelta
from dateutil import tz
from pathlib import Path
import urllib.parse
import webbrowser
import os
import pprint
from sklearn.preprocessing import minmax_scale
import numpy as np
from scipy import stats
#from notebook import notebookapp
from IPython.core.display import display, HTML
from IPython.display import Javascript
import geopandas as gpd

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
local_dir1 = servers1 + cwd + '/'
local_dir2 = servers2 + cwd + '/' 

def write_INDEX_html(param, oDir):
    #open Adaptive_Choropleth_Mapper.html (the excutable file for the visualization)
    ifile = open("template/Adaptive_Choropleth_Mapper.html", "r", encoding="utf-8")
    contents = ifile.read()
    
    #Replace variables based on the user's selection in each of four files below.
    contents = contents.replace("Adaptive Choropleth Mapper", param['title'])
    contents = contents.replace("data/CONFIG.js", "data/CONFIG_"+param['filename_suffix']+".js")
    contents = contents.replace("data/GEO_JSON.js", "data/GEO_JSON_"+param['filename_suffix']+".js")
    contents = contents.replace("data/VARIABLES.js", "data/VARIABLES_"+param['filename_suffix']+".js")
    
    #write new outfiles: GEO_CONFIG.js GEO_JSON.js VARIABLES.js
    ofile = open(oDir+"/index.html", "w", encoding="utf-8")
    ofile.write(contents)
    ofile.close()
    #print (contents)    

   
def write_CONFIG_js(param, oDir):
    # read ACM_GEO_CONFIG.js
    ifile = open("template/ACM_CONFIG.js", "r", encoding="utf-8")
    contents = ifile.read()
    
    # get valid varables from contents
    vlist = re.findall(r'(\nvar +(\S+) *= *(.+))', contents)

    # replace the value of the file to the value in the parameter 
    vdict = {vtuple[1]: vtuple for vtuple in vlist}
    for i, (key, value) in enumerate(param.items()):
        if (key in vdict):
            jstatement = '\nvar ' + key + ' = ' + json.dumps(value) + ';'           # create js statement
            contents = contents.replace(vdict[key][0], jstatement)
    
    #Write output including the replacement above
    filename_GEO_CONFIG = oDir + "/data/CONFIG_"+param['filename_suffix']+".js"
    ofile = open(filename_GEO_CONFIG, 'w', encoding="utf-8")
    ofile.write(contents)
    ofile.close()    
    #print (contents)          

def write_VARIABLES_js(community, param, oDir):
    #print(param)    
    geoid        =  community.columns[0]
    years        =  param['years']
    variables    =  param['variables']

    #make heading: community.columns[0] has "geoid" (string)
    heading = [geoid]
    for i, year in enumerate(years):
        for j, variable in enumerate(param['labels']):
            heading.append(str(year)+'_'+variable)
    #Make Dictionary
    mydictionary = {}    # key: geoid, value: variables by heading
    h = -1
    selectedColumns = [geoid]
    selectedColumns.extend(variables)
    #print("selectedColumns:", type(selectedColumns), selectedColumns)
    for i, year in enumerate(years):
        aYearDF = community[community.year==year][selectedColumns]
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
    
def write_GEO_JSON_js(param, oDir):    
    # read shape file to df_shape
    df_shapes = param['shapefile']
    df_shapes = df_shapes.astype(str)
    geoid = df_shapes.columns[0]
    name = df_shapes.columns[1]
    
    df_shapes = df_shapes[pd.notnull(df_shapes['geometry'])]
    
    # open GEO_JSON.js write heading for geojson format
    filename_GEO_JSON = oDir + "/data/GEO_JSON_"+param['filename_suffix']+".js"
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
        feature["properties"] = {geoid: shape.geoid, name: shape.name}
        wCount += 1
        ofile.write(json.dumps(feature)+',\n')

    # complete the geojosn format by adding parenthesis at the end.	
    ofile.write(']}\n')
    ofile.close()
def varName(p):
    for k, v in globals().items():
        if id(p) == id(v):
            return k
            
# write param.log file from param into the new folder of result
def write_LOG(param, oDir):
    # convert param to pretty print data structures
    del param['inputCSV']
    del param['shapefile']
    del param['periods']
    del param['years']    
    contents = pprint.pformat(param, compact=True, sort_dicts=False)        # depth=1, 
    ofile = open(oDir+"/data/param.log", "w")
    create_at = datetime.now()
    ofile.write('%s %s\n\n' % (create_at.strftime('%Y-%m-%d %H:%M:%S'), oDir))
    ofile.write('  '+contents.replace('\n', '\n  '))
    ofile.close()


def Adaptive_Choropleth_Mapper_log(param):
    #Create a new folder where GEO_CONFIG.js GEO_JSON.js VARIABLES.js will be saved
    oDir = 'ACM_' + param['filename_suffix']
    path = Path(oDir + '/data')
    path.mkdir(parents=True, exist_ok=True)
    
    # build array of logs from directory of 'ACM_'
    logs = []
    dirname = os.getcwd()
    subnames = os.listdir(dirname)
    for subname in subnames:
        fullpath = os.path.join(dirname, subname)
        if (not os.path.isdir(fullpath)): continue
        if (not subname.startswith('ACM_')): continue
        indexfile = os.path.join(fullpath, 'index.html')
        logfile = os.path.join(fullpath, 'data/param.log')
        if (not os.path.exists(indexfile)): continue
        if (not os.path.exists(logfile)): continue
        ifile = open(logfile, "r")
        wholetext = ifile.read()
        contents = wholetext.split('\n', maxsplit=1)
        if (len(contents) != 2): continue
        cols = contents[0].split(' ', maxsplit=3)
        create_at = contents[0]
        out_dir = ""
        if (len(cols) >= 3): 
            create_at = cols[0] + ' ' + cols[1]
            out_dir = cols[2]       
        create_at = datetime.fromisoformat(create_at).replace(tzinfo=timezone.utc)
        param = contents[1]
        logs.append({'indexfile': local_dir1+'/'+subname+'/'+'index.html', 'create_at': create_at.isoformat(), 'out_dir': out_dir, 'param': param})
    logs = sorted(logs, key=lambda k: k['create_at']) 
    
    #Write output to log.html
    filename_LOG = "ACM_log.html"
    ofile = open(filename_LOG, 'w')
    ofile.write('<!DOCTYPE html>\n')
    ofile.write('<html>\n')
    ofile.write('<head>\n')
    ofile.write('  <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n')
    ofile.write('  <title>Neighborhood Analysis Logging</title>\n')
    ofile.write('</head>\n')
    ofile.write('<body>\n')
    ofile.write('  <header>\n')
    ofile.write('    <h1>Logging</h1><p style="color:#6495ED;"><i>*Copy the URL using the button and paste it to your browser to see visualizations you created before.</i></p>\n')
    ofile.write('  </header>\n')
    
    for idx, val in enumerate(logs):
        params = val['param'].split('\n')
        html = '\n'
        html += '<div style="margin:10px; float:left; border: 1px solid #99CCFF; border-radius: 5px;">\n'
        html += '  <table>\n'
        html += '    <tr>\n'
        html += '      <td>\n'
        html += '      <span style="color:#CD5C5C;"><strong>' + str(idx+1) + '. ' + val['out_dir'] + '</strong></span>'
        html += '        <span style="display: inline-block; width:380px; text-align: right;">' + '<span class="utcToLocal">'+ val['create_at'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'        
        html += '        <input type="text" value=' + val['indexfile']+ ' id="myInput' + str(idx+1) + '">'
        html += '        <button onclick="myFunction' + str(idx+1) + '()">Copy</button></span>\n'        
        html += '      </td>\n'
        html += '    </tr>\n'
        html += '    <tr>\n'
        html += '      <td>\n'
        html += '<pre>\n'
        for param in params:
            html += param + '\n'
        html += '</pre>\n'
        html += '      </td>\n'
        html += '    </tr>\n'
        html += '  </table>\n'
        html += '</div>\n'
        
        html += '<script>'
        html += 'function myFunction' + str(idx+1) + '() {'
        html += '  var copyText = document.getElementById("myInput' + str(idx+1) + '");' #Get the text field
        html += '  copyText.select();'                                 #Select the text field
        html += '  copyText.setSelectionRange(0, 99999);'              #For mobile devices
        html += '  navigator.clipboard.writeText(copyText.value);'     #Copy the text inside the text field
        html += '  alert("The URL has been copied to the clipboard. Paste it to the browser to see your visualizations: " + copyText.value);'       #Alert the copied text
        html += '};'
        html += 'document.querySelectorAll(".utcToLocal").forEach('
        html += '  function (i) {'
        html += '    const options = {hour12: false, hour:"2-digit", minute:"2-digit", timeZoneName: "short", year: "numeric", month: "numeric", day: "numeric"};'
        html += '    i.innerHTML = new Date(i.innerText).toLocaleString("en-US",options);'
        html += '  }'
        html += ');'
        html += '</script>\n'
        ofile.write(html)   
    ofile.write('</body>\n')
    ofile.write('</html>')
    ofile.close()
    
    local_dir = os.path.dirname(os.path.realpath(__file__))
    #local_dir = os.getcwd()
    fname =urllib.parse.quote(filename_LOG)
    url = 'file:' + os.path.join(local_dir, fname)
    #url = os.path.join(template_dir, fname)    
    webbrowser.open(url)


def Adaptive_Choropleth_Mapper_viz(param):
    
    # if no 'periods' or 'periods' == 'All', get 'periods' from 'inputCSV' in the param.
    if ('periods' in param and isinstance(param['periods'], str) and (param['periods'].lower() == "all" or param['periods'] == "")):    
        df_input = param['inputCSV']
        nameOf1stColumn = df_input.columns[0]       # name of the 1st column may be 'geoid'
        nameOf2ndColumn = df_input.columns[1]       # name of the 2nd column may be 'year'
        #print(nameOf1stColumn, nameOf2ndColumn)
        param['periods'] = sorted(list(set(df_input[nameOf2ndColumn].tolist())));

    
    # if no 'NumOfCLC' or 'NumOfCLC' == 0, get 'NumOfCLC' from length of the 'periods' in the param.
    if ('NumOfCLC' not in param or isinstance(param['NumOfCLC'], (int, float)) and param['NumOfCLC'] <= 0):
        if ('periods' in param): param['NumOfCLC'] = len(param['periods']);
    
    # convert year, variable to years, variables in the param
    if ('years' not in param and 'year' in param): param['years'] = [param['year']]
    if ('years' not in param and 'year' not in param and 'periods' in param): param['years'] = param['periods']
    if ('years' not in param and 'year' not in param and 'periods' not in param and 'period' in param): param['years'] = [param['period']]
    if ('variables' not in param and 'variable' in param): param['variables'] = [param['variable']]
    
    # select community by state_fips, msa_fips, county_fips
    community = None
    if ('msa_fips' in param and param['msa_fips']):
        community = Community.from_ltdb(years=param['years'], msa_fips=param['msa_fips'])
    elif ('county_fips' in param and param['county_fips']):
        community = Community.from_ltdb(years=param['years'], county_fips=param['county_fips'])
    elif ('state_fips' in param and param['state_fips']):
        community = Community.from_ltdb(years=param['years'], state_fips=param['state_fips'])

# if the user enters CSV and shapefile, use the files from the user

#### This is executed when the user enter attributes in csv file and geometroy in shapefile #####
    if (community is None and 'inputCSV' in param):
        community = param["inputCSV"]
        geoid = community.columns[0]      
        community[community.columns[0]] = community[geoid].astype(str)

        # read shape file to df_shape
        df_shape = param['shapefile']
        df_shape = df_shape.astype(str)     
        geokey = df_shape.columns[0]  
        df_shape = df_shape.set_index(geokey)
        
        # insert geometry to community
        geometry = []
        for index, row in community.iterrows():
            tractid = row[geoid]
            try:
                tract = df_shape.loc[tractid]
                geometry.append(shapely.wkt.loads(tract.geometry))
            except KeyError:
                geometry.append(None)
        if(("geometry" in community) == False):
            community.insert(len(community.columns), "geometry", geometry)
        community.rename(columns={'period':'year'}, inplace=True)
      
    community = community.replace([np.inf, -np.inf], np.nan)
 
    community = community[pd.notnull(community['geometry'])]


    codebook = pd.read_csv('template/conversion_table_codebook.csv')
    codebook.set_index(keys='variable', inplace=True)
    labels = copy.deepcopy(param['variables'])

    if ('label' in param):
        label = 'short_name'  # default
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
    param['labels'] = labels
    

    #Create a new folder where GEO_CONFIG.js GEO_JSON.js VARIABLES.js will be saved
    oDir = 'ACM_' + param['filename_suffix']
    path = Path(oDir + '/data')
    path.mkdir(parents=True, exist_ok=True)
    
    print('output directory :  {}'.format(oDir))
    write_INDEX_html(param, oDir)
    write_CONFIG_js(param, oDir)
    write_VARIABLES_js(community, param, oDir)
    write_GEO_JSON_js(param, oDir)
    write_LOG(param, oDir)

    fname =urllib.parse.quote('index.html')
    template_dir = os.path.join(local_dir1, 'ACM_' + param['filename_suffix'])
    url = os.path.join(template_dir, fname)    
    webbrowser.open(url)
    print('To see your visualization, click the URL below (or locate the files):')
    print(url)
    print('To access all visualizations that you have created, click the URL below (or locate the files):')
    print(local_dir1 + '/ACM_log.html')    
    print('Advanced options are available in ')  
    print(local_dir2 + 'ACM_' + param['filename_suffix']+'/data/CONFIG_' + param['filename_suffix']+'.js')
    #display(Javascript('window.open("{url}");'.format(url=url)))

    
if __name__ == '__main__':
    started_datetime = datetime.now()
    print('Scenario_Analysis_Mapper start at %s' % (started_datetime.strftime('%Y-%m-%d %H:%M:%S')))


    input_attributes_hiv = pd.read_csv("attributes/HIV_US_multiple_long.csv", dtype={'geoid':str})
    input_attributes_hiv = input_attributes_hiv.rename(columns={'geoid': 'geoid'})
    
    shapefile_us = gpd.read_file("shp/US/counties.shp")
    
    param_MLC_HIV = {
        'title': "Adaptive Choropleth Mapper with Multiple Line Charts",
        'Subject': "Temporal Patterns",
        'filename_suffix': "HIV_MLC",                                      # max 30 character    
        'inputCSV': input_attributes_hiv,   
        'shapefile': shapefile_us, 
        'periods': "All",
        'variables': [         #enter variable names of the column you selected above.
                "HIV",
                "Health Care Center (/100k pop)"
            ],
        'NumOfMaps':2,
        'Initial_map_center':[37, -97],
        'Initial_map_zoom_level':4,    
        'Map_width':"650px",
        'Top10_Chart': True,     
        'Multiple_Line_Chart': True,
        'NumOfMLC':2,
        'DefaultRegion_MLC':"36061" 
    }
    
    param_CLC_HIV = {
        'title': "Adaptive Choropleth Mapper with Comparison Line Chart",
        'Subject': "Temporal Patterns",
        'filename_suffix': "HIV_CLC",                                      # max 30 character  
        'inputCSV': input_attributes_hiv,   
        'shapefile': shapefile_us, 
        'periods': [2012, 2013, 2014, 2015, 2016, 2017, 2018],
        'variables': [         #enter variable names of the column you selected above.
                "HIV",
                #"Health Care Center (/100k pop)"    
            ],
        'NumOfMaps':2,
        'Initial_map_center':[37, -97],
        'Initial_map_zoom_level':4,
        'Map_width':"650px",
        'Top10_Chart': True,     
        'Comparision_Chart': True,
        'DefaultRegion_CLC': ["36061", "12086"] #New York, NY VS Miami-Dade, FL 
    }
    
    param_PCP_hiv = {
        'title': "Adaptive Choropleth Mapper with Paralle Coordinate Plot",
        'filename_suffix': "HIV_PCP",                                      # max 30 character  
        #'inputCSV': "data_imputedx.csv",     
        'inputCSV': input_attributes_hiv,   
        'shapefile': shapefile_us, 
        'periods': [2012, 2013, 2014, 2015, 2016, 2017, 2018],
        'variables': [         #enter variable names of the column you selected above.
                "HIV",
                #"Health Care Center (/100k pop)"
            ],
        'NumOfMaps':2,
        'Initial_map_center':[37, -97],
        'Initial_map_zoom_level':4,    
        'Map_width':"650px",
        'Top10_Chart': True,    
        'Parallel_Coordinates_Plot': True,
        'NumOfPCP':7,
    }
 
    input_attributes = pd.read_csv("attributes/Los_Angeles_1980_1990_2000_2010.csv", dtype={'geoid':str})
    input_attributes = input_attributes.rename(columns={'geoid': 'geoid'})

    shapefile = gpd.read_file("shp/Los_Angeles_tract/Los_Angeles_2.shp")
    shapefile = shapefile.rename(columns={'tractID': 'geoid', 'tract_key': 'name'})

    param_MLC = {
    'title': "Adaptive Choropleth Mapper with Multiple Line Charts",
    'Subject': "Temporal Patterns",
    'filename_suffix': "Census_MLC",                                      # max 30 character      
    'inputCSV': input_attributes,   
    'shapefile': shapefile, 
    'periods': [1980, 1990, 2000, 2010],
    'variables': [         #enter variable names of the column you selected above.
            "p_nonhisp_white_persons",
            "p_nonhisp_black_persons",
            "p_hispanic_persons",
            "p_asian_persons",         
        ],
    'label': "short_name", #Pick variable,short_name,full_name from template/conversion_table_codebook.csv 
    'NumOfMaps':2,
    'Map_width':"650px",
    'Top10_Chart': True,     
    'Multiple_Line_Chart': True,
    'NumOfMLC':4,
    'InitialVariableMLC': ["1980 % white (non-Hispanic)", "1980 % black (non-Hispanic)", "1980 % Hispanic", "1980 % Asian and Pacific Islander race"],
    'DefaultRegion_MLC':"06037237201" 
}

    param_CLC = {
    'title': "Adaptive Choropleth Mapper with Multiple Line Charts",
    'Subject': "Temporal Patterns",
    'filename_suffix': "Census_CLC",                                      # max 30 character   
    'inputCSV': input_attributes,   
    'shapefile': shapefile, 
    'periods': [1980, 1990, 2000, 2010],
    'variables': [         #enter variable names of the column you selected above.
            "p_nonhisp_white_persons",
            "p_nonhisp_black_persons",
            "p_hispanic_persons",
            "p_asian_persons",         
        ],
    'label': "short_name", #Pick variable,short_name,full_name from template/conversion_table_codebook.csv 
    'NumOfMaps':2,
    'Map_width':"650px",
    'Top10_Chart': True,     
    'Comparision_Chart': True,
    'NumOfCLC': 4, # set the number of x value of the Comparision_Chart
    'InitialVariableCLC':["1980_% white (non-Hispanic)", "1990_% white (non-Hispanic)", "2000_% white (non-Hispanic)", "2010_% white (non-Hispanic)"],
    'DefaultRegion_CLC': ["06037102105", "06037103300"]
}
    param_PCP = {
    'title': "Adaptive Choropleth Mapper with Paralle Coordinate Plot",
    'filename_suffix': "Census_PCP",                                      # max 30 character  
    #'inputCSV': "data_imputedx.csv",     
    'inputCSV': input_attributes,   
    'shapefile': shapefile, 
    'periods': [2010],
    'variables': [         #enter variable names of the column you selected above.
            "p_nonhisp_white_persons",
            "p_nonhisp_black_persons",
            "p_hispanic_persons",
            "p_asian_persons",
            "p_employed_manufacturing",
            "p_poverty_rate",
            "p_foreign_born_pop",
            "p_persons_under_18",
            "p_persons_over_60",  
            "p_edu_college_greater",
            "p_unemployment_rate",
            "p_employed_professional",
            "p_vacant_housing_units",
            "p_owner_occupied_units",
            "p_housing_units_multiunit_structures",
            "median_home_value",
            "p_structures_30_old",
            "p_household_recent_move",
      
        ],
    'label': "short_name", #Pick variable,short_name,full_name from template/conversion_table_codebook.csv 
    'NumOfMaps':2,
    'Map_width':"650px",
    'Top10_Chart': True,    
    'Parallel_Coordinates_Plot': True,
    'NumOfPCP':10,
    'InitialVariablePCP': ["2010_% white (non-Hispanic)", "2010_% black (non-Hispanic)", "2010_% Hispanic", "2010_% Asian & PI race", "2010_% professional employees", "2010_% manufacturing employees", "2010_% in poverty", "2010_% foreign born", "2010_% 17 and under (total)", "2010_% 60 and older"]
}
    param_Scatter = {
        'title': "Adaptive Choropleth Mapper with Correlogram",
        'filename_suffix': "LA_Scatter",
        'inputCSV': input_attributes,   
        'shapefile': shapefile,
        'periods': [2010],
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
        'Scatter_Plot': True,        
    }
    
    param_Correlogram = {
        'title': "Adaptive Choropleth Mapper with Correlogram",
        'filename_suffix': "LA_Correlogram",
        'inputCSV': input_attributes,   
        'shapefile': shapefile,
        'NumOfMaps':4,
        'periods': [2010],
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
        'Map_width':"370px",
        'Map_height':"370px",
        'Correlogram': True,        
    } 

    param_Stacked = {
        'title': "Adaptive Choropleth Mapper with Stacked Chart",
        'filename_suffix': "LA_Stacked",
        'inputCSV': input_attributes,   
        'shapefile': shapefile,
        'periods': [1980, 1990, 2000, 2010],
        'NumOfMaps': 5,
        'label': "short_name", #Pick variable,short_name,full_name from template/conversion_table_codebook.csv         
        'variables': [         #enter variable names of the column you selected above.
            "p_asian_persons",    
        ],
        'Stacked_Chart': True,  #Comment out if you do not want to visualize this chart      
    }  

    param_bar = {
        'title': "Adaptive Choropleth Mapper with Stacked Chart",
        'filename_suffix': "LA_ACM",
        'inputCSV': input_attributes,   
        'shapefile': shapefile,
        'periods': [1980, 1990, 2000, 2010],
        'NumOfMaps': 3,
        'label': "short_name", #Pick variable,short_name,full_name from template/conversion_table_codebook.csv         
        'variables': [         #enter variable names of the column you selected above.           
            "p_other_language",
            "p_female_headed_families",
            "per_capita_income",     
        ],
        'Top10_Chart': True,  #Comment out if you do not want to visualize this chart      
    }
    Covid_Visits = pd.read_csv("attributes/Covid_Visits.csv", dtype={'geoid':str})
    Covid_Visits = Covid_Visits.rename(columns={'geoid': 'geoid'})
     
    shapefile_MSA = gpd.read_file("shp/MSA_country/msa_country.shp", dtype={'GEOID':str})
    shapefile_MSA = shapefile_MSA.rename(columns={'GEOID': 'geoid', 'NAME_1':'name'})

    param_MLC_COVID = {
        'title': "Covid-19 Risk Assessment using Twitter, Metropolitan Statistical Areas, USA",
        'Subject': "Temporal Patterns",
        'filename_suffix': "COVID_MLC",                                      # max 30 character      
        'inputCSV': Covid_Visits,   
        'shapefile': shapefile_MSA, 
        'periods': "All",
        'variables': [         #enter variable names of the column you selected above.
                "Confirmed Rate",
                "Death Rate",
                "The Number of Visits from Outside to Inside of the selected MSA"
            ],
        'NumOfMaps':2,
        'InitialLayers':["2020-04-19_Confirmed Rate" , "2020-11-01_Confirmed Rate"],
        'Initial_map_center':[37, -97],
        'Initial_map_zoom_level':4,    
        'Map_width':"650px",
        'Top10_Chart': True,     
        'Multiple_Line_Chart': True,
        'NumOfMLC':3,
        'titlesOfMLC':["1. COVID-19 Confirmed Cases (/100k pop)", "2. COVID-19 Death Cases (/100k pop)", "3. The Number of Visitors"],
        'DefaultRegion_MLC':"35620" 
    }

    param_CLC_COVID = {
        'title': "Comparison of COVID-19 Confirmed Rate between Metropolitan Statistical Areas, USA",
        'Subject': "Temporal Patterns",
        'filename_suffix': "COVID_CLC",                                      # max 30 character      
        'inputCSV': Covid_Visits,   
        'shapefile': shapefile_MSA, 
        'periods': "All",
        'variables': [         #enter variable names of the column you selected above.
                "Confirmed Rate"
            ],
        'NumOfMaps':2,
        'InitialLayers':["2020-04-19_Confirmed Rate" , "2020-11-01_Confirmed Rate"],
        'Initial_map_center':[37, -97],
        'Initial_map_zoom_level':4,    
        'Map_width':"650px",
        'Top10_Chart': True,     
        'Comparision_Chart': True,
        'NumOfCLC': 46,
        'DefaultRegion_CLC': ["35620", "16980"] 
    }
    
    # param_MLC, param_CLC, param_PCP, 
    # param_MLC_HIV, param_CLC_HIV, 
    # param_MLC_COVID, param_CLC_COVID, param_PCP_hiv, param_PCP, param_Scatter, param_Correlogram, param_Stacked, param_bar
    
    #Adaptive_Choropleth_Mapper_viz(param_PCP)
    
    Adaptive_Choropleth_Mapper_viz(param_MLC_HIV)
    Adaptive_Choropleth_Mapper_viz(param_CLC_HIV)
    
    Adaptive_Choropleth_Mapper_viz(param_MLC)
    Adaptive_Choropleth_Mapper_viz(param_CLC)
    
    Adaptive_Choropleth_Mapper_viz(param_MLC_COVID)
    Adaptive_Choropleth_Mapper_viz(param_CLC_COVID)
    Adaptive_Choropleth_Mapper_viz(param_PCP)
    Adaptive_Choropleth_Mapper_viz(param_Scatter)
    Adaptive_Choropleth_Mapper_viz(param_Correlogram)
    Adaptive_Choropleth_Mapper_viz(param_Stacked)
    Adaptive_Choropleth_Mapper_viz(param_bar)
    
    ended_datetime = datetime.now()
    elapsed = ended_datetime - started_datetime
    total_seconds = int(elapsed.total_seconds())
    hours, remainder = divmod(total_seconds,60*60)
    minutes, seconds = divmod(remainder,60)	
    print('Scenario_Analysis_Mapper ended at %s    Elapsed %02d:%02d:%02d' % (ended_datetime.strftime('%Y-%m-%d %H:%M:%S'), hours, minutes, seconds))