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
#This is for CyberGISX. Uncomment a command line below when you run in CyberGIX Environmen
from jupyter_server import serverapp
import geopandas as gpd

## Retrieve Server URL that Jupyter is running
jupyter_envs = {k: v for k, v in os.environ.items() if k.startswith('JUPYTER')}
temp_server = jupyter_envs['JUPYTER_INSTANCE_URL']

# Define Paths for Visualization (Jupyter Lab)
servers = list(serverapp.list_running_servers())
servers1 = temp_server+servers[0]["base_url"]+ 'view'
servers2 = temp_server+servers[0]["base_url"]+ 'edit'

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
    # vlist = [ ('\nvar Subject = "";', 'Subject', '"";')
    #           ('\nvar NumOfMaps = 2;', 'NumOfMaps', '2;')
    #           ('\nvar NumOfPCP = 7;', 'NumOfPCP', '7;')
    #           ('\nvar NumOfCLC = 7;', 'NumOfCLC', '7;')
    #           ('\nvar NumOfMLC = 4;', 'NumOfMLC', '4;')
    #           ...                                         ]
    
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
    periods      =  param['periods']
    variables    =  param['variables']
    
    ## filtering by years
    #community = community[community.year.isin(years)]
    #print(community)
    #selectedCommunity = community[variables]
    #print(community)
    #return
    
    #make heading: community.columns[0] has "geoid" (string)
    heading = [geoid]
    for i, period in enumerate(periods):
        #for j, variable in enumerate(param['labels']):
        #    #heading.append(str(period)+' '+variable)
        #    heading.append(str(period)+'_'+variable)
        for j, variable in enumerate(variables):
            if (variable in param['labels']): shortLabel = param['labels'][variable]
            else: shortLabel = variable
            heading.append(str(period)+'_'+shortLabel)
    #Make Dictionary
    mydictionary = {}    # key: geoid, value: variables by heading
    h = -1
    selectedColumns = [geoid]
    selectedColumns.extend(variables)
    #print("selectedColumns:", type(selectedColumns), selectedColumns)
    for i, period in enumerate(periods):
        aYearDF = community[community.period==period][selectedColumns]
        #print(period, type(aYearDF), aYearDF)
        for j, variable in enumerate(variables):
            h += 1
            for index, row in aYearDF.iterrows():
                #print(index, row)
                key = row[geoid]
                val = row[variable]
                if (math.isnan(val)): #converts Nan in GEOSNAP data to -9999
                    #print(i, j, key, period, val)
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
    #print(df_shapes)
    #df_shapes = df_shapes.rename(columns={'GEOID10': 'geoid'})
    #df_shapes = param['shapefile']
    #print(df_shapes.dtypes)
    df_shapes = df_shapes.astype(str)
    #print(df_shapes.dtypes)
    
    geoid = df_shapes.columns[0]
    name = df_shapes.columns[1]
    #print(df_shapes.columns[0], df_shapes.columns[1])
    
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
        #print(type(shape))
        #print(shape.geoid)
        #print(shape.name)
        feature["geometry"] = shapely.geometry.mapping(aShape)
        #feature["properties"] = {geoid: tract.__getattribute__(geoid), "tractID": tract.__getattribute__(geoid)}
        feature["properties"] = {geoid: shape.geoid, name: shape.name}
        wCount += 1
        ofile.write(json.dumps(feature)+',\n')
    #print("GEO_JSON.js write count:", wCount)
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
    del param['labels']
    contents = pprint.pformat(param, compact=True, sort_dicts=False)        # depth=1, 
    #print("==============================")
    #print(param)
    #write new outfiles: GEO_CONFIG.js GEO_JSON.js VARIABLES.js
    ofile = open(oDir+"/data/param.log", "w")
    create_at = datetime.now()
    #print(create_at)
    #print(create_at.strftime('%y-%m-%d %H:%M:%S'))  
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
        #print(local_dir1+fullpath)
        if (not os.path.isdir(fullpath)): continue
        if (not subname.startswith('ACM_')): continue
        #print(os.path.join(fullpath, 'index.html'))
        indexfile = os.path.join(fullpath, 'index.html')
        logfile = os.path.join(fullpath, 'data/param.log')
        if (not os.path.exists(indexfile)): continue
        if (not os.path.exists(logfile)): continue
        #print(fullpath, logfile)
        # read param.log
        ifile = open(logfile, "r")
        wholetext = ifile.read()
        contents = wholetext.split('\n', maxsplit=1)
        if (len(contents) != 2): continue
        cols = contents[0].split(' ', maxsplit=3)
        #create_at = contents[0] if (len(cols) <= 2) else cols[0] + ' ' + cols[1] + ' &nbsp; ' + cols[2]
        create_at = contents[0]
        out_dir = ""
        if (len(cols) >= 3): 
            create_at = cols[0] + ' ' + cols[1]
            out_dir = cols[2]
        #create_at = datetime.fromisoformat(create_at).replace(tzinfo=timezone.utc).astimezone(tz=tz.tzlocal())
        
        #current_time = datetime.now().isoformat()
        #created_at = datetime.fromisoformat(current_time)
        #print(create_at)        
        create_at = datetime.fromisoformat(create_at).replace(tzinfo=timezone.utc)
        #print(create_at)        
        param = contents[1]
        #print(subname+'/'+'index.html')
        #print(create_at)
        #print(param)
        #logs.append({'indexfile': subname+'/'+'index.html', 'create_at': create_at, 'out_dir': out_dir, 'param': param})
        #logs.append({'indexfile': local_dir1+subname+'/'+'index.html', 'create_at': create_at, 'out_dir': out_dir, 'param': param})
        logs.append({'indexfile': local_dir1+'/'+subname+'/'+'index.html', 'create_at': create_at.isoformat(), 'out_dir': out_dir, 'param': param})
    logs = sorted(logs, key=lambda k: k['create_at']) 
    #print(logs)
    
    #Write output to log.html
    filename_LOG = "ACM_log.html"
    ofile = open(filename_LOG, 'w')
    ofile.write('<!DOCTYPE html>\n')
    ofile.write('<html>\n')
    ofile.write('<head>\n')
    ofile.write('  <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n')
    ofile.write('  <title>Neighborhood Analysis Logging</title>\n')
    ofile.write('<script src="template/Adaptive_Choropleth_Mapper/lib/sweetalert/sweetalert.min.js"></script>')
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
        #html += '        <span style="display: inline-block; width:380px; text-align: right;">' + val['create_at'] + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
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
        html += '  swal("Copied!","The URL has been copied to the clipboard. Paste it to the browser to see your visualizations.");'       #Alert the copied text
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
    
    # check column in input CSV
    if ('inputCSV' in param):
        dfName = 'inputCSV'
        if (CheckColumnName(dfName, param[dfName], 'geoid', 0) == False): return
        if (CheckColumnName(dfName, param[dfName], 'period') == False): return
    # check column in shape file
    if ('shapefile' in param):
        dfName = 'shapefile'
        if (CheckColumnName(dfName, param[dfName], 'geoid', 0) == False): return
        if (CheckColumnName(dfName, param[dfName], 'name', 1) == False): return
    
    # Checks if period and periods are mutually exclusive in the param.
    if ('period' in param and 'periods' in param):
        print("Both period and periods exist in the param.")
        print("Please confirm below the param list.")
        print("period: {}".format(param['period']))
        print("periods: {}".format(param['periods']))
        return
    
    # If periods does not exist in the param, it is created from period as a list.
    if ('period' in param and 'periods' not in param): 
        param['periods'] = [param['period']]
    # Also, if periods do not exist in the param, create them from inputCSV.
    if ('periods' not in param or isinstance(param['periods'], str) and 
        (param['periods'].lower() == "all" or param['periods'] == "")):
        df_input = param['inputCSV']
        param['periods'] = sorted(list(set(df_input['period'].tolist())));
        #print("default param ['periods']:", param['periods'])
    
    # If NumOfCLC is not in the param, it will be the length of periods.
    if ('Comparision_Chart' in param and 
        isinstance(param['Comparision_Chart'], bool) and param['Comparision_Chart'] == True):
        if ('NumOfCLC' not in param or 
            isinstance(param['NumOfCLC'], int) and param['NumOfCLC'] <= 0):
            if ('periods' in param): 
                param['NumOfCLC'] = len(param['periods']);
                #print("default param ['NumOfCLC']:", param['NumOfCLC'])
    
    # If variables does not exist in the param, it is created from variable as a list.
    if ('variables' not in param and 'variable' in param): 
        param['variables'] = [param['variable']]
        #print("default param ['variables']:", param['variables'])
    
    community = None
    # select community by state_fips, msa_fips, county_fips  ->  reserved for future use (RFU)
    #if ('msa_fips' in param and param['msa_fips']):
    #    community = Community.from_ltdb(years=param['years'], msa_fips=param['msa_fips'])
    #    #community = Community.from_ltdb(msa_fips=param['msa_fips'])
    #elif ('county_fips' in param and param['county_fips']):
    #    community = Community.from_ltdb(years=param['years'], county_fips=param['county_fips'])
    #elif ('state_fips' in param and param['state_fips']):
    #    community = Community.from_ltdb(years=param['years'], state_fips=param['state_fips'])
    #print(community)
    
    #### This is executed when the user enter attributes in csv file and geometroy in shapefile 
    if ('inputCSV' in param and 'shapefile' in param):
        community = param["inputCSV"]
        geoid = community.columns[0]      
        community[community.columns[0]] = community[geoid].astype(str)
        #print("community.columns[0]:", community.columns[0])
        
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
                #print("Tract ID [{}] is not found in the shape file {}".format(tractid, param['shapefile']))
                geometry.append(None)
        
        if(("geometry" in community) == False):
            community.insert(len(community.columns), "geometry", geometry)
    ####
    
    community = community.replace([np.inf, -np.inf], np.nan)
    # check if geometry is not null for Spatial Clustering  
    community = community[pd.notnull(community['geometry'])]
    #print(community)

    # read short label and convert it to dict
    ##  param['labels'] = {}
    ##  if ('shortLabelCSV' in param):
    ##      df_shortLabel = pd.read_csv(param['shortLabelCSV']).set_index('variable')
    ##      param['labels'] = df_shortLabel.to_dict()['short_name']
    ##      print(param['labels'])
    param['labels'] = {}
    if ('shortLabelCSV' in param):
        df_shortLabel = pd.read_csv(param['shortLabelCSV'])
        for index, row in df_shortLabel.iterrows():
            variable = row['variable']
            shortName = row['short_name']
            if (shortName == ""): shortName = variable
            if (variable not in param['labels']): param['labels'][variable] = shortName
            else: print("duplicate in shortLabelCSV. [{}] '{}': '{}'".format(index, variable, shortName))
    #print(param['labels'])
    
    
    #Create a new folder where GEO_CONFIG.js GEO_JSON.js VARIABLES.js will be saved
    oDir = 'ACM_' + param['filename_suffix']
    path = Path(oDir + '/data')
    path.mkdir(parents=True, exist_ok=True)
    
    print('output directory :  {}'.format(oDir))
    write_INDEX_html(param, oDir)
    write_CONFIG_js(param, oDir)
    write_VARIABLES_js(community, param, oDir)
    #write_GEO_JSON_js(community, param)
    write_GEO_JSON_js(param, oDir)
    write_LOG(param, oDir)
        
    #print(local_dir)
    fname =urllib.parse.quote('index.html')
    template_dir = os.path.join(local_dir1, 'ACM_' + param['filename_suffix'])
    #url = 'file:' + os.path.join(template_dir, fname)
    url = os.path.join(template_dir, fname)    
    webbrowser.open(url)
    print('To see your visualization, click the URL below (or locate the files):')
    print(url)
    print('To access all visualizations that you have created, click the URL below (or locate the files):')
    print(local_dir1 + '/ACM_log.html')    
    print('Advanced options are available in ')  
    print(local_dir2 + 'ACM_' + param['filename_suffix']+'/data/CONFIG_' + param['filename_suffix']+'.js')
    #display(Javascript('window.open("{url}");'.format(url=url)))


# Check if column exists in a data frame.
# If necessary, you can even check its position.
def CheckColumnName(df_name, df, columnName, pos=-1):
    
    if (columnName not in df):
        print("Column '{}' is not in {}.".format(columnName, df_name))
        print("Please confirm below columns name list.")
        print(df.columns.tolist())
        return False   
    if (pos >= 0 and df.columns.get_loc(columnName) != pos):
        p = pos + 1
        strPos = '{}th'.format(p)
        if (p == 1): strPos = '{}st'.format(p)
        if (p == 2): strPos = '{}nd'.format(p)
        if (p == 3): strPos = '{}rd'.format(p)
        print("Column '{}' is not {} column in {}.".format(columnName, strPos, df_name))
        print("Please confirm below columns name list.")
        print(df.columns.tolist())
        return False
    return True

    
if __name__ == '__main__':
    started_datetime = datetime.now()
    print('Scenario_Analysis_Mapper start at %s' % (started_datetime.strftime('%Y-%m-%d %H:%M:%S')))

    input_attributes = pd.read_csv("attributes/Los_Angeles_1980_1990_2000_2010.csv", dtype={'geoid':str})
    #input_attributes = input_attributes.rename(columns={'geoid': 'geoid'})
    input_attributes = input_attributes.rename(columns={'year': 'period'})
    #print(input_attributes.columns.tolist())
    shapefile = gpd.read_file("shp/Los_Angeles_tract/Los_Angeles_2.shp")
    shapefile = shapefile.rename(columns={'tractID': 'geoid', 'tract_key': 'name'})
    #print(shapefile) 

    input_attributes_hiv = pd.read_csv("attributes/HIV_US_multiple_long.csv", dtype={'geoid':str})
    #input_attributes_hiv = input_attributes_hiv.rename(columns={'geoid': 'geoid'})
    #input_attributes_hiv = input_attributes_hiv.rename(columns={'period': 'period'})
    #print(input_attributes_hiv.columns.tolist())    
    shapefile_us = gpd.read_file("shp/US/counties.shp")
    #print(shapefile_us) 
    
    param_MLC = {
    'title': "Adaptive Choropleth Mapper with Multiple Line Charts",
    'Subject': "Temporal Patterns",
    'filename_suffix': "Census_MLC_v2",                                      # max 30 character  
    #'inputCSV': "data_imputedx.csv",     
    'inputCSV': input_attributes,   
    'shapefile': shapefile, 
    #'period': 2000,
    'periods': [1980, 1990, 2000, 2010],
    'variables': [         #enter variable names of the column you selected above.
            "p_nonhisp_white_persons",
            "p_nonhisp_black_persons",
            "p_hispanic_persons",
            "p_asian_persons",         
        ],
    #'label': "short_name", #Pick variable,short_name,full_name from template/conversion_table_codebook.csv
    'shortLabelCSV': "attributes/Los_Angeles_1980_1990_2000_2010_ShortLabel.csv",
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
    #'inputCSV': "data_imputedx.csv",     
    'inputCSV': input_attributes,   
    'shapefile': shapefile, 
    #'period': 2000,
    'periods': [1980, 1990, 2000, 2010],
    'variables': [         #enter variable names of the column you selected above.
            "p_nonhisp_white_persons",
            "p_nonhisp_black_persons",
            "p_hispanic_persons",
            "p_asian_persons",         
        ],
    #'label': "short_name", #Pick variable,short_name,full_name from template/conversion_table_codebook.csv 
    'shortLabelCSV': "attributes/Los_Angeles_1980_1990_2000_2010_ShortLabel.csv",
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
    #'period': 2000,
    'periods': [1980, 1990, 2000, 2010],
    'variables': [         #enter variable names of the column you selected above.
            "p_nonhisp_white_persons",
            "p_nonhisp_black_persons",
            "p_hispanic_persons",
            "p_asian_persons",         
        ],
    #'label': "short_name", #Pick variable,short_name,full_name from template/conversion_table_codebook.csv 
    'shortLabelCSV': "attributes/Los_Angeles_1980_1990_2000_2010_ShortLabel.csv",
    'NumOfMaps':2,
    'Map_width':"650px",
    'Top10_Chart': True,    
    'Parallel_Coordinates_Plot': True,
    'NumOfPCP':4,
    'InitialVariablePCP': ["1980 % white (non-Hispanic)", "1980 % black (non-Hispanic)", "1980 % Hispanic", "1980 % Asian and Pacific Islander race"]
}
################################################################################
    param_Correlogram = {
        'title': "Adaptive Choropleth Mapper with Correlogram",
        'filename_suffix': "LA_Correlogram",
        'inputCSV': input_attributes,   
        'shapefile': shapefile,
        'period': 2010,
        'NumOfMaps': 4,    
        #'label': "short_name", #Pick variable,short_name,full_name from template/conversion_table_codebook.csv         
        'shortLabelCSV': "attributes/Los_Angeles_1980_1990_2000_2010_ShortLabel.csv",
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
        'Correlogram': True,        
    }

    param_Scatter = {
        'title': "Adaptive Choropleth Mapper with Correlogram",
        'filename_suffix': "LA_Scatter",
        'inputCSV': input_attributes,   
        'shapefile': shapefile,
        'period': 2010,
        #'periods': [2000, 2010],
        #'periods': "",
        #'label': "short_name", #Pick variable,short_name,full_name from template/conversion_table_codebook.csv
        'shortLabelCSV': "attributes/Los_Angeles_1980_1990_2000_2010_ShortLabel.csv",
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

    param_MLC_HIV = {
        'title': "Adaptive Choropleth Mapper with Multiple Line Charts",
        'Subject': "Temporal Patterns",
        'filename_suffix': "HIV_MLC",                                      # max 30 character  
        #'inputCSV': "data_imputedx.csv",     
        'inputCSV': input_attributes_hiv,   
        'shapefile': shapefile_us, 
        #'period': 2000,
        #'periods': [2012, 2013, 2014, 2015, 2016, 2017, 2018],
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
        #'InitialVariableMLC': ['2012_HIV', '2013_HIV', '2014_HIV', '2015_HIV', '2016_HIV', '2017_HIV', '2018_HIV'],
        'DefaultRegion_MLC':"36061",
        #'Top10_NoDisplay': ["HIV"]
    }
    
    param_CLC_hiv = {
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
        #'NumOfCLC': 0, # set the number of x value of the Comparision_Chart
        #'InitialVariableCLC': ['2012_HIV', '2013_HIV', '2014_HIV', '2015_HIV', '2016_HIV', '2017_HIV', '2018_HIV'],
        #'InitialVariableCLC': ['2012_Health Care Center (/100k pop)', '2013_Health Care Center (/100k pop)', '2014_Health Care Center (/100k pop)', '2015_Health Care Center (/100k pop)', '2016_Health Care Center (/100k pop)', '2017_Health Care Center (/100k pop)', '2018_Health Care Center (/100k pop)'],
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
        #'InitialVariablePCP':['2012_HIV', '2013_HIV', '2014_HIV', '2015_HIV', '2016_HIV', '2017_HIV', '2018_HIV']
    }
    
    param_Correlogram = {
        'title': "Adaptive Choropleth Mapper with Correlogram",
        'filename_suffix': "LA_Correlogram",
        'inputCSV': input_attributes,   
        'shapefile': shapefile,
        'NumOfMaps':4,
        'period': 2010,
        #'label': "short_name", #Pick variable,short_name,full_name from template/conversion_table_codebook.csv         
        'shortLabelCSV': "attributes/Los_Angeles_1980_1990_2000_2010_ShortLabel.csv",
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
        #'label': "short_name", #Pick variable,short_name,full_name from template/conversion_table_codebook.csv         
        'shortLabelCSV': "attributes/Los_Angeles_1980_1990_2000_2010_ShortLabel.csv",
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
        #'label': "short_name", #Pick variable,short_name,full_name from template/conversion_table_codebook.csv         
        'shortLabelCSV': "attributes/Los_Angeles_1980_1990_2000_2010_ShortLabel.csv",
        'variables': [         #enter variable names of the column you selected above.           
            "p_other_language",
            "p_female_headed_families",
            "per_capita_income",     
        ],
        'Top10_Chart': True,  #Comment out if you do not want to visualize this chart      
    }
    
    '''
    Covid_Visits = pd.read_csv("attributes/Covid_Visits_old.csv", dtype={'geoid':str})
    Covid_Visits = Covid_Visits.rename(columns={'geoid': 'geoid'})
     
    shapefile_MSA = gpd.read_file("shp/MSA_country/msa_country.shp", dtype={'GEOID':str})
    shapefile_MSA = shapefile_MSA.rename(columns={'GEOID': 'geoid', 'NAME_1':'name'})

    param_MLC_COVID = {
        'title': "Covid-19 Risk Assessment using Twitter, Metropolitan Statistical Areas, USA",
        'Subject': "Temporal Patterns",
        'filename_suffix': "COVID_MLC",                                      # max 30 character      
        'inputCSV': Covid_Visits,   
        'shapefile': shapefile_MSA, 
        'periods': ["2020-02-16", "2020-02-23", "2020-03-01", "2020-03-08", "2020-03-15", "2020-03-22", "2020-03-29", "2020-04-05", "2020-04-12", "2020-04-19", "2020-04-26", "2020-05-03", "2020-05-10", "2020-05-17", "2020-05-24", "2020-05-31", "2020-06-07", "2020-06-14", "2020-06-21", "2020-06-28", "2020-07-05", "2020-07-12", "2020-07-19", "2020-07-26", "2020-08-02", "2020-08-09", "2020-08-16", "2020-08-23", "2020-08-30", "2020-09-06", "2020-09-13", "2020-09-20", "2020-09-27", "2020-10-04", "2020-10-11", "2020-10-18", "2020-10-25", "2020-11-01", "2020-11-08", "2020-11-15", "2020-11-22", "2020-11-29", "2020-12-06", "2020-12-13", "2020-12-20", "2020-12-27"],
        'variables': [         #enter variable names of the column you selected above.
                "Confirmed Rate",
                "Death Rate",
                "The Number of Visits from Outside to Inside of the selected MSA"
            ],
        'NumOfMaps':2,
        #'InitialLayers':["419_confirmed" , "1101_confirmed"],
        'InitialLayers':["2020-04-19_Confirmed Rate" , "2020-11-01_Confirmed Rate"],
        'Initial_map_center':[37, -97],
        'Initial_map_zoom_level':4,    
        'Map_width':"650px",
        'Top10_Chart': True,     
        'Multiple_Line_Chart': True,
        'NumOfMLC':3,
        'titlesOfMLC':["1. COVID-19 Confirmed Cases (/100k pop)", "2. COVID-19 Death Cases (/100k pop)", "3. The Number of Visitors"],
        #'InitialVariableMLC': ['2012_HIV', '2013_HIV', '2014_HIV', '2015_HIV', '2016_HIV', '2017_HIV', '2018_HIV'],
        'HighlightMLC': [["2020-02-16", "2020-04-05", "#fdff32"],["2020-10-04", "2020-12-27", "#fdff32"]],
        'DefaultRegion_MLC':"35620" 
    }
    '''
    
    Covid = pd.read_csv("attributes/SD_Confirmed_Vaccine_Final_v5.csv", dtype={'Zipcode':str})
    Covid = Covid.astype({'Zipcode':'string'})
    Covid = Covid.rename(columns={'Zipcode': 'geoid','variable': 'period'})
    
    shapefile_SD = gpd.read_file("shp/San_Diego_Zip/SanDiego_Zip_COVID.shp", dtype={'zipcode':str, 'community':str})
    shapefile_SD = shapefile_SD.rename(columns={'zipcode': 'geoid', 'community':'name'})
    
    param_MLC_COVID_San_Diego = {
        'title': "Visualizing the Impact of Covid-19: Temporal Trends in Crude and Vaccination Rates by Zip Code in San Diego",
        'Subject': "Tracking Covid-19 Confirmed and Vaccination Rates over Time in San Diego's Selected Zip Codes",
        'filename_suffix': "COVID_MLC_SD",  # max 30 character      
        'inputCSV': Covid,   
        'shapefile': shapefile_SD, 
        'periods': "All",
        'variables': [         #enter variable names of the column you entered above.
                "Confirmed_Cases_per_10k_pop", 
                "vaccinated_per_10k_pop",    
                "Confirmed_total_per_10k_pop",        
                "vaccinated_total_per_10k_pop",
            ],
        'NumOfMaps':2,
        'SortLayers': "temporal",  #Enter “compare” or “temporal”.  compare mode is for comparing variables at a specific point of time.
                                                    # temporal mode is for displaying spatiotemporal patterns of the same variable using multiple maps.            
        
        'InitialLayers':["2020-04-01_Confirmed_Cases_per_10k_pop" , "2020-12-27_Confirmed_Cases_per_10k_pop"],
        'Initial_map_center':[33.01, -116.77],
        'Initial_map_zoom_level':9,  
        'Map_width':"550px",
        'Map_height':"420px", 
        'Top10_Chart': True,     
        'Multiple_Line_Chart': True,
        'NumOfMLC':4,
        'titlesOfMLC':[],
        'titlesOfMLC':["1. COVID-19 Crude Rate (Confirmed Cases per 10k population)", "2. Vaccinated Rate (Vaccinated People per 10k population)", "3. Cumulative Confirmed Rate", "4. Cumulative Vaccinated Rate (Vaccinated People per 10k population)"],
        'DefaultRegion_MLC':"92109",
        #'MultipleLineChart_width':"300px"        
    }
    
    '''
    param_CLC_COVID = {
        'title': "Comparison of COVID-19 Confirmed Rate between Metropolitan Statistical Areas, USA",
        'Subject': "Temporal Patterns",
        'filename_suffix': "COVID_CLC",                                      # max 30 character      
        'inputCSV': Covid_Visits,   
        'shapefile': shapefile_MSA, 
        'periods': ["2020-02-16", "2020-02-23", "2020-03-01", "2020-03-08", "2020-03-15", "2020-03-22", "2020-03-29", "2020-04-05", "2020-04-12", "2020-04-19", "2020-04-26", "2020-05-03", "2020-05-10", "2020-05-17", "2020-05-24", "2020-05-31", "2020-06-07", "2020-06-14", "2020-06-21", "2020-06-28", "2020-07-05", "2020-07-12", "2020-07-19", "2020-07-26", "2020-08-02", "2020-08-09", "2020-08-16", "2020-08-23", "2020-08-30", "2020-09-06", "2020-09-13", "2020-09-20", "2020-09-27", "2020-10-04", "2020-10-11", "2020-10-18", "2020-10-25", "2020-11-01", "2020-11-08", "2020-11-15", "2020-11-22", "2020-11-29", "2020-12-06", "2020-12-13", "2020-12-20", "2020-12-27"],
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
        'HighlightCLC': [["2020-02-16", "2020-04-05", "#fdff32"],["2020-10-04", "2020-12-27", "#fdff32"]],
        'DefaultRegion_CLC': ["35620", "16980"] 
    }
    '''
    
    # param_MLC, param_CLC, param_PCP, 
    # param_MLC_HIV, param_CLC_hiv, 
    # param_MLC_COVID, param_CLC_COVID, param_PCP_hiv, param_PCP, param_Scatter, param_Correlogram, param_Stacked, param_bar
    
    #Adaptive_Choropleth_Mapper_viz(param_Scatter)
    
    #Adaptive_Choropleth_Mapper_viz(param_MLC_HIV)
    #Adaptive_Choropleth_Mapper_viz(param_CLC_hiv)
    
    Adaptive_Choropleth_Mapper_viz(param_MLC_COVID_San_Diego)
    Adaptive_Choropleth_Mapper_log(param_MLC_COVID_San_Diego)
    
    #Adaptive_Choropleth_Mapper_viz(param_MLC_COVID)
    #Adaptive_Choropleth_Mapper_log(param_MLC_COVID)
    #Adaptive_Choropleth_Mapper_viz(param_CLC_COVID)
    #Adaptive_Choropleth_Mapper_log(param_CLC_COVID)
    #Adaptive_Choropleth_Mapper_viz(param_PCP_hiv)
    #Adaptive_Choropleth_Mapper_log(param_PCP_hiv)
    #Adaptive_Choropleth_Mapper_viz(param_Scatter)
    #Adaptive_Choropleth_Mapper_log(param_Scatter)
    #Adaptive_Choropleth_Mapper_viz(param_Correlogram)
    #Adaptive_Choropleth_Mapper_log(param_Correlogram)
    #Adaptive_Choropleth_Mapper_viz(param_Stacked)
    #Adaptive_Choropleth_Mapper_log(param_Stacked)
    #Adaptive_Choropleth_Mapper_viz(param_bar)
    #Adaptive_Choropleth_Mapper_log(param_bar)
    
    ended_datetime = datetime.now()
    elapsed = ended_datetime - started_datetime
    total_seconds = int(elapsed.total_seconds())
    hours, remainder = divmod(total_seconds,60*60)
    minutes, seconds = divmod(remainder,60)	
    print('Scenario_Analysis_Mapper ended at %s    Elapsed %02d:%02d:%02d' % (ended_datetime.strftime('%Y-%m-%d %H:%M:%S'), hours, minutes, seconds))
