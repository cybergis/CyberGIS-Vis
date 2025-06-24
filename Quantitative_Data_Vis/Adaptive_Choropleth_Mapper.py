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
import geopandas as gpd
#This is for CyberGISX. Uncomment a command line below when you run in CyberGIX Environment
from jupyter_server import serverapp
import ipywidgets as widgets
from IPython.display import display, clear_output
import inspect
from dateutil.parser import isoparser

globals_from_jupyter = None
parser = isoparser()

#This is for CyberGISX. Uncomment a command line below when you run in CyberGIX Environment
# Retrieve Server URL that Jupyter is running
jupyter_envs = {k: v for k, v in os.environ.items() if k.startswith('JUPYTER')}
temp_server = jupyter_envs['JUPYTER_INSTANCE_URL']

#This is for CyberGISX. Uncomment a command line below when you run in CyberGIX Environment
# Define Paths for Visualization (Jupyter Lab)
servers = list(serverapp.list_running_servers())
servers1 = temp_server+servers[0]["base_url"]+ 'view'
servers2 = temp_server+servers[0]["base_url"]+ 'edit'

cwd = os.getcwd()
prefix_cwd = "/home/jovyan/work"
cwd = cwd.replace(prefix_cwd, "")

# This is for Jupyter notebbok installed in your PC
#local_dir1 = cwd
#local_dir2 = cwd  

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
    periods      =  set(param['periods'])
    variables    =  param['variables']
    
    index_col = "geoid"
    field_col = "period"
    community=community.rename(columns=param['labels'])
    value_col = [param['labels'][v] if v in param['labels'] else v for v in variables]
    
    pivoted = community.replace([np.inf, -np.inf], np.nan).query("period in @periods").pivot(columns=field_col, index=index_col, values=value_col)
    pivoted = pivoted.swaplevel(0, 1, axis=1)
    # fill NA
    pivoted = pivoted.fillna(-9999)
    # update header
    pivoted.columns = ['_'.join([str(c) for c in col]).strip() for col in pivoted.columns.values]
    # # if integer columns exist, convert them
    # for column in pivoted.columns:
    #     if pd.api.types.is_float_dtype(pivoted[column]):
    #         # Check if all values in the column are effectively integers
    #         if all(pivoted[column] % 1 == 0):
    #             pivoted[column] = pivoted[column].astype(int)
    # format the dataframe to array structure
    tight_dict = pivoted.reset_index().to_dict(orient='tight')

    # use Keys and Dictionary created above and write them VARIABLES.js
    filename_VARIABLES = "ACM_" + param['filename_suffix'] + "/data/VARIABLES_"+param['filename_suffix']+".js"
    ofile = open(filename_VARIABLES, 'w')
    with open(filename_VARIABLES, "w") as f:
        f.writelines('var GEO_VARIABLES =[\n')
        f.writelines(str(tight_dict["columns"]))
        tmp_text = str(tight_dict["data"])
        f.write(","+tmp_text[1:])
                
    
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
    for k, v in globals_from_jupyter.items():
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
    write_VARIABLES_js(param["inputCSV"].copy(), param, oDir)
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
    print(local_dir1 + 'ACM_log.html')    
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

# Function to wrap widgets with tooltips
def widget_with_tooltip(widget, tooltip_text):
    """
    Wraps a widget with a tooltip that appears on hover.
    """
    tooltip = widgets.HTML(
        value=f"""
        <div class="tooltip-container">
            {widget._repr_html_()}
            <span class="tooltip-text">{tooltip_text}</span>
        </div>
        """
    )
    return tooltip


# Check date format for periods.
def check_dateformat(text):
    try:
        parser.parse_isodate(str(text))
    except:
        return False
    return True

def Initial_Layers(file):
    # Pre-compute the heading for debugging or display
    # Define the output file for the heading
    output_heading_file = "heading_output.csv"
    input_attributes = file
    # Clear the file before use
    with open(output_heading_file, 'w') as file:
        pass
    
    # Generate the heading variable as per the user's code
    periods = input_attributes[input_attributes.columns[1]].unique().tolist()  # Unique values of the second column
    variables = input_attributes.columns[2:].tolist()
    heading_initial = []
    
    for period in periods:
        for variable in variables:
            heading_initial.append(f"{period}_{variable}")
    
    # Convert heading to a DataFrame and export to CSV
    heading_df = pd.DataFrame(heading_initial, columns=["Heading"])
    heading_df.to_csv(output_heading_file, index=False)
    
    # Display all rows and columns
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    print(heading_df.to_string())


# Function to create the GUI
def MLC(map_center=None, map_zoom=None):
    # Set default values based on passed arguments
    map_center_default = "" if map_center is None else f"{map_center[0]}, {map_center[1]}"
    map_zoom_default = "" if map_zoom is None else str(map_zoom)
    
    # Currentframe is this python file. f_back enabling going back to the frame where MLC is called.
    frame = inspect.currentframe().f_back
    globals_from_jupyter = frame.f_globals  # we can bring both global or local. For making globals_from_jupyter accessible from outside.
    
    #print(caller_gloables.get("input_attributes"))
    # Widget definitions
    input_csv_widget = widgets.Text(
        description='Input Attribute:',
        value='attributes',
        style={'description_width': '160px'},
        layout=widgets.Layout(width='400px'),
        #tooltip='Enter the CSV file name containing the attribute data.'
    )
    input_csv_help = widgets.Label(value='Enter the CSV file variable name containing the attribute data.')
    
    shapefile_widget = widgets.Text(
        description='Input Shapefile:',
        value='shapefile',
        style={'description_width': '160px'},
        layout=widgets.Layout(width='400px'),
        #tooltip='Enter the shapefile (.shp) variable name containing geographic data.'
    )
    shapefile_help = widgets.Label(value='Enter the shapefile (.shp) variable name containing geographic data.')    
    
    title_widget = widgets.Text(
        description='Title:',
        value='Spatiotemporal Dynamics of COVID-19 Cases and Deaths in U.S. Counties',
        layout=widgets.Layout(width='600px'),
        style={'description_width': '160px'},
        #tooltip='Enter the title for the result visualization.'
    )
    title_help = widgets.Label(value='Enter the title for the result visualization.')  
    
    subject_widget = widgets.Text(
        description="Chart Title:",
        value="Temporal Patterns of COVID-19 Risk Factors",
        layout=widgets.Layout(width='600px'),
        style={'description_width': '160px'},
        #tooltip='Enter the text to be displayed at the top of all line charts. For example: "Temporal Patterns of Risk Factors..'
    )
    subject_help = widgets.Label(value="Enter the text to be displayed at the top of the line charts, such as 'Temporal Patterns of COVID-19 Rates.'")  
    
    filename_suffix_widget = widgets.Text(
        description="Output Folder Name:",
        value="COVID_MLC",
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Enter the name of the output folder for generated files.'
    )
    filename_suffix_help = widgets.Label(value='Enter the name of the output folder for generated files.')      
    
    periods_widget = widgets.SelectMultiple(
        description='Periods:',
        options=['All'],
        value=['All'],
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Specify the periods as comma-separated values for specific periods or select "All" to display all available periods.'
    )
    periods_help = widgets.Label(value='Select time ranges for temporal charts; "All" for all ranges. Use "Ctrl" for multiple choices. Acceptable formats: YYYY, MM-DD, or MM-DD-YYYY')
    
    num_of_maps_widget = widgets.IntSlider(
        description="The Number of Maps:",
        value=2,
        min=1,
        max=10,
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Specify the number of maps to be displayed. Multiple maps can be displayed.'
    )
    num_of_maps_help = widgets.Label(value='Specify the number of maps to visualize.')      

    # Widget for map center (latitude and longitude)
    map_center_widget = widgets.Text(
        description="Map Center (Lat, Lon):",
        value=map_center_default,  # Set from parameter or empty string
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Specify the map center as "latitude, longitude" (e.g., 38, -97).'
    )
    
    # Widget for map zoom level
    map_zoom_widget = widgets.Text(
        description="Map Zoom Level:",
        value=map_zoom_default,  # Set from parameter or empty string
        layout=widgets.Layout(width='300px'),
        style={'description_width': '160px'},
        #tooltip='Specify the initial zoom level of the map (optional).'
    )
         
    sort_layers_widget = widgets.Dropdown(
        options=['temporal', 'compare'],
        description='Sort Layers:',
        value='temporal',
        style={'description_width': '160px'},
        layout=widgets.Layout(width='400px'),
        #tooltip='"temporal" for examining temporal changes of distribution, "compare" for comparing different attributes for a specific year.'
    )
    sort_layers_help = widgets.Label(value='Choose "Temporal" to compare the same variable at different points in time or "Compare" to compare different variables at the same point in time.')  
    
    initial_layers_widget = widgets.Textarea(
        description="Initial Layers:",
        value="2020-04-06_confirmed_rate,2020-07-20_confirmed_rate",
        layout=widgets.Layout(width='600px', height='150px'),
        style={'description_width': '160px'},
        #tooltip='Specify default names of map layers displayed on the first view of maps. It should not exceed the number of maps you specified. \n Try Initial_Layers(attributes) to see all possible options. E.g., 2020-04-06_confirmed_rate, 2020-07-20_confirmed_rate'
    )
    initial_layers_help = widgets.Label(value='Specify default names of map layers displayed on the first view of maps. It should not exceed the number of maps you specified.\nTry Initial_Layers(attributes) to see all possible options. E.g., 2020-04-06_confirmed_rate, 2020-07-20_confirmed_rate')
    
    variables_widget = widgets.SelectMultiple(
        description="Variables:",
        layout=widgets.Layout(width='600px', height='150px', overflow='auto'),
        style={'description_width': '160px'},
        #tooltip='Enter at least one variable. "Ctrl" for selecting multiple variables.'
    )
    variables_help = widgets.Label(value='Enter at least one variable. "Ctrl" for selecting multiple variables.')  
    
    map_width_widget = widgets.Text(
        description="Map Width (px):",
        value="650px",
        layout=widgets.Layout(width='300px'),
        style={'description_width': '160px'},
        #tooltip='Specify the width of the map in pixels.'
    )
    
    map_height_widget = widgets.Text(
        description="Map Height (px):",
        value="450px",
        layout=widgets.Layout(width='300px'),
        style={'description_width': '160px'},
        #tooltip='Specify the height of the map in pixels.'
    )

    chart_info = widgets.HTML(
        value="Select the chart to be visualized.",
        layout=widgets.Layout(width='600px')
    )
    
    top10_chart_widget = widgets.Checkbox(
        description="Top 10 Chart",
        value=True,
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Enable or disable the display of the top 10 chart.'
    )
    
    mlc_widget = widgets.Checkbox(
        description="Multiple Line Chart (MLC):",
        value=True,
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Enable or disable the Multiple Line Chart (MLC) feature.'
    )
    
    # Number of MLCs widget
    num_mlc_widget = widgets.IntSlider(
        description="The number of MLC:",
        value=0,  # Default to 0 initially
        min=0,  # Allow 0 as the minimum
        max=0,  # Will be updated dynamically based on variable selection
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Select the number of Multiple Line Charts (MLCs) to display.'
    )
    num_mlc_info = widgets.HTML(
        value="Enter the number of line charts to be visualized.",
        layout=widgets.Layout(width='600px')
    )
    
    titles_mlc_widget = widgets.Textarea(
        description="Titles of MLCs:",
        value="1. Confirmed Rate (Confirmed Cases per 10k population), 2. Death Rate (Deaths per 10k population), 3. Cumulative Confirmed Rate, 4. Cumulative Death Rate, 5. Visitor Flows from the Selected Region",
        layout=widgets.Layout(width='600px', height='90px'),
        style={'description_width': '160px'},
        #tooltip='Titles for each line chart in order. The number of titles should be equal to the number of MLCs you specified. \n For example, "1. Confirmed Rate, 2. Death Rate, 3. Cumulative Confirmed Rate"'
    )
    titles_mlc_help = widgets.Label(value='Provide titles for each line chart in order, separated by commas. Ensure the number of titles matches the number of MLCs specified. For example, "1. Confirmed Rate (Confirmed Cases per 10k population), 2. Death Rate (Deaths per 10k population), 3. Cumulative Confirmed Rate, 4. Cumulative Death Rate, 5. Visitor Flows from the Selected Region"')  #1. Confirmed Rate, 2. Death Rate, 3. Cumulative Confirmed Rate

    default_region_info_MLC = widgets.HTML(
        value="Select the region to display temporal patterns in the initial view of the Multipe Line Chart (MLC):",
        layout=widgets.Layout(width='600px')
    )
    
    default_region_widget = widgets.Combobox(
        description='Default Region (Geoid):',
        options=[],  # Will be populated based on shapefile
        ensure_option=True,  # Allow only options from the provided list
        placeholder='Type to search...',
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Select the default region (Geoid) to focus on initially.'
    )
    
    # Run button
    run_button = widgets.Button(
        description="Generate Visualization",
        button_style="success",
        layout=widgets.Layout(width='300px', height='50px'),
        #tooltip='Click to generate the visualization based on the specified parameters.'
    )
    output_area = widgets.Output()

    # Layout definition
    data_widgets = widgets.VBox([
        widgets.HBox([input_csv_widget, input_csv_help]),
        widgets.HBox([shapefile_widget, shapefile_help]),
        widgets.HBox([title_widget, title_help]),
        widgets.HBox([subject_widget, subject_help]),
        widgets.HBox([filename_suffix_widget, filename_suffix_help]),
        widgets.HBox([periods_widget, periods_help]),
        widgets.HBox([variables_widget, variables_help]),
        #variables_widget,        
        #num_of_maps_widget,
        widgets.HBox([num_of_maps_widget, num_of_maps_help]),
        #sort_layers_widget,
        widgets.HBox([sort_layers_widget, sort_layers_help]),
    ], layout=widgets.Layout(padding='10px'))

    map_widgets = widgets.VBox([
        chart_info,
        top10_chart_widget,
        mlc_widget,
        num_mlc_info,
        num_mlc_widget,
        default_region_info_MLC,
        default_region_widget      
    ], layout=widgets.Layout(padding='10px'))

    optional_settings_widgets = widgets.VBox([
        map_center_widget,
        map_zoom_widget,         
        widgets.HBox([map_width_widget]),
        widgets.HBox([map_height_widget]),
        #initial_layers_widget,
        widgets.HBox([initial_layers_widget]),
        initial_layers_help,
        titles_mlc_widget,
        titles_mlc_help
    ], layout=widgets.Layout(padding='10px'))

    map_settings_widgets = widgets.VBox([
        widgets.HBox([map_width_widget]),
        titles_mlc_widget
    ], layout=widgets.Layout(padding='10px'))
    



    # Full layout including the run button and output
    tab = widgets.Tab([
        widgets.VBox([data_widgets, map_widgets], layout=widgets.Layout(padding='10px')),
        optional_settings_widgets
    ])
    tab.set_title(0, 'Required parameters')
    tab.set_title(1, 'Optional parameters')

    gui = widgets.VBox([
        tab,
        run_button,
        output_area
    ], layout=widgets.Layout(padding='10px', width='100%', align_items='flex-start'))

    display(gui)

    # Function to update variable options based on selected CSV
    def update_default_region_options():
        """
        Updates the 'Default Region (Geoid):' options based on the shapefile widget's value.
        Displays the second column for user selection but assigns the corresponding value from the first column.
        """
        try:
            shapefile = globals_from_jupyter.get(shapefile_widget.value)  # Retrieve the GeoDataFrame
            if isinstance(shapefile, gpd.GeoDataFrame):
                # Ensure the shapefile has at least two columns
                if shapefile.shape[1] >= 2:
                    # Create a mapping from the second column to the first column
                    display_values = shapefile.iloc[:, 1].astype(str).tolist()  # Second column for display
                    actual_values = shapefile.iloc[:, 0].astype(str).tolist()  # First column for actual values
                    default_region_mapping = dict(zip(display_values, actual_values))
                    
                    # Populate the options and set the mapping
                    default_region_widget.options = display_values
                    default_region_widget.mapping = default_region_mapping
                    default_region_widget.value = ""  # Set to an empty string instead of None
                else:
                    print("Error: Shapefile must have at least two columns.")
                    default_region_widget.options = []
                    default_region_widget.value = ""  # Set to an empty string
            else:
                print("Error: Shapefile is not a valid GeoDataFrame.")
                default_region_widget.options = []
                default_region_widget.value = ""  # Set to an empty string
        except Exception as e:
            print(f"Error updating default region options: {e}")
            default_region_widget.options = []
            default_region_widget.value = ""  # Set to an empty string
    


    
    def handle_default_region_selection(change):
        """
        Removes the first option from 'Default Region (Geoid):' when a region is selected by the user.
        """
        try:
            selected_region = change['new']
            if selected_region and selected_region in default_region_widget.options:
                # Remove the first option after the user selects a region
                default_region_widget.options = [
                    region for region in default_region_widget.options if region != selected_region
                ]
        except Exception as e:
            print(f"Error handling default region selection: {e}")

            
            
    # Function to update variable options based on selected CSV
    def update_variables_options(change=None):
        try:
            # Retrieve the input CSV variable name from the widget
            input_csv_name = input_csv_widget.value
            # Get the corresponding DataFrame from globals
            
            #print(globals_from_jupyter.get("input_attributes"))
            df = globals_from_jupyter.get(input_csv_name, None)
            #df = globals().get(input_csv_name, None)

            if isinstance(df, pd.DataFrame):
                # Update the "Variables" widget with the column names starting from the third column
                variables_widget.options = df.columns[2:]

                # Update the "Periods" widget with 'All' and unique values from the second column
                if df.shape[1] > 1:  # Ensure the DataFrame has at least two columns
                    unique_periods = df.iloc[:, 1].dropna().astype(str).unique().tolist()
                    periods_widget.options = ['All'] + unique_periods
                    periods_widget.value = ['All']
                else:
                    periods_widget.options = ['All']
                    periods_widget.value = ['All']
            else:
                # Reset options if the CSV is invalid
                variables_widget.options = []
                periods_widget.options = ['All']
                periods_widget.value = ['All']
                print(f"Error: {input_csv_name} is not a valid DataFrame.")
        except Exception as e:
            # Fallback for unexpected errors
            variables_widget.options = []
            periods_widget.options = ['All']
            periods_widget.value = ['All']
            print(f"Error updating variables and periods: {e}")

    # Function to update the max and default value of the Number of MLCs widget
    def update_num_mlc(change):
        selected_variables = list(change['new'])
        num_mlc_widget.max = len(selected_variables)  # Update max based on selected variables
        num_mlc_widget.value = num_mlc_widget.max  # Set default value to the maximum

    # Force update of periods widget on initialization or when input changes
    def force_update_periods():
        update_variables_options({'new': input_csv_widget.value})
        num_mlc_widget.max = len(change['new'])
        if num_mlc_widget.value > len(change['new']):
            num_mlc_widget.value = len(change['new'])

            
    # Function to handle visualization generation
    def generate_visualization(_):
        with output_area:
            clear_output()
            try:
                # Parse map center input
                map_center = map_center_widget.value.strip()
                if map_center:
                    try:
                        lat_lon = map_center.split(',')
                        if len(lat_lon) != 2:
                            raise ValueError("Map Center must have exactly two values: latitude and longitude.")
                        lat, lon = map(float, lat_lon)
                        if not (-90 <= lat <= 90):
                            raise ValueError("Latitude must be between -90 and 90.")
                        if not (-180 <= lon <= 180):
                            raise ValueError("Longitude must be between -180 and 180.")
                        map_center = [lat, lon]
                    except ValueError:
                        raise ValueError("Map Center must be in the format 'latitude, longitude' (e.g., 38, -97).")
                else:
                    map_center = None  # Default to None if not provided
    
                # Parse map zoom level input
                map_zoom = map_zoom_widget.value
                if map_zoom:
                    try:
                        map_zoom = int(map_zoom)
                        if not (1 <= map_zoom <= 20):
                            raise ValueError("Zoom level must be between 1 and 20.")
                    except ValueError:
                        raise ValueError("Map Zoom Level must be an integer between 1 and 20.")
                else:
                    map_zoom = None  # Default to None if not provided
                
                
                # Check if at least one variable is selected
                if not variables_widget.value:
                    print("Error: At least one variable should be selected.")
                    return  # Halt execution if no variables are selected
                
                # Load the input CSV and shapefile dynamically
                input_csv = globals_from_jupyter.get(input_csv_widget.value, None)
                shapefile = globals_from_jupyter.get(shapefile_widget.value, None)
    
                # Validate inputs
                if not isinstance(input_csv, pd.DataFrame):
                    raise ValueError('Input CSV is not a valid DataFrame or variable does not exist in the current scope')
                if not isinstance(shapefile, gpd.GeoDataFrame):
                    raise ValueError('Shapefile is not a valid GeoDataFrame or variable does not exist in the current scope')
    
                # Retrieve the selected region and map it to the corresponding actual value
                selected_region_display = default_region_widget.value
                selected_region = None
                if selected_region_display and hasattr(default_region_widget, 'mapping'):
                    selected_region = default_region_widget.mapping.get(selected_region_display)

    
                # Parse and validate periods
                periods = 'All' if 'All' in periods_widget.value else [p for p in periods_widget.value if check_dateformat(p)]
                
                # check if all values are YYYY
                year_periods = True
                for p in periods_widget.value:
                    # it means YYYY
                    if not p.isdigit():
                        year_periods = False
                
                if year_periods:
                    periods = []
                    for p in periods_widget.value:
                        periods.append(int(p))
                        
                if not periods:
                    print("Error: Invalid or empty period selection.")
                    return
            
                # Parse parameters
                params = {
                    'title': title_widget.value,
                    'Subject': subject_widget.value,
                    'filename_suffix': filename_suffix_widget.value if filename_suffix_widget.value else "default_suffix",
                    'inputCSV': input_csv,
                    'shapefile': shapefile,
                    'periods': (
                        'All' if 'All' in periods 
                        else periods
                     ),
                    'variables': list(variables_widget.value),
                    'NumOfMaps': num_of_maps_widget.value,
                    'Initial_map_center': map_center,
                    'Initial_map_zoom_level': int(map_zoom_widget.value) if map_zoom_widget.value else None,
                    'SortLayers': sort_layers_widget.value,
                    #'InitialLayers': initial_layers_widget.value.split(","),
                    'InitialLayers': [layer.strip() for layer in initial_layers_widget.value.split(",")],
                    'Map_width': map_width_widget.value,
                    'Map_height': map_height_widget.value,
                    'Top10_Chart': top10_chart_widget.value,
                    'Multiple_Line_Chart': mlc_widget.value,
                    'NumOfMLC': num_mlc_widget.value,
                    'titlesOfMLC': titles_mlc_widget.value.split(","),
                    'DefaultRegion_MLC': selected_region,
                }
            
                # Include the Short Label CSV only if it's provided
                #if short_label_csv_widget.value.strip():
                #    params['shortLabelCSV'] = short_label_csv_widget.value.strip()    
                    
                # Print the selected region and entered parameters for debugging
                #print(f"Selected Region (Geoid): {selected_region}")
                #print(f"Parameters: {params}") #######################################################################
    
                # Call visualization and logging functions
                try:
                    Adaptive_Choropleth_Mapper_viz(params)
                    print("Visualization generated successfully!")
                except Exception as viz_error:
                    print(f"Error generating visualization: {viz_error}")
                Adaptive_Choropleth_Mapper_log(params)
            except Exception as e:
                print(f"Error: {e}")
    
    
    # Remove redundant observers and keep only the necessary ones
    run_button.on_click(generate_visualization)
    input_csv_widget.observe(update_variables_options, names='value')
    # Attach observer for Variables widget to update Number of MLCs widget
    variables_widget.observe(update_num_mlc, names='value')

    shapefile_widget.observe(lambda change: update_default_region_options(), names='value')
    # Attach observer to default_region_widget for the selection change
    default_region_widget.observe(handle_default_region_selection, names='value')

    # Initialize variable options and other widget settings
    update_variables_options({'new': input_csv_widget.value})
    update_default_region_options()
    
# Function to create the GUI
def CLC(map_center=None, map_zoom=None):
    # Set default values based on passed arguments
    map_center_default = "" if map_center is None else f"{map_center[0]}, {map_center[1]}"
    map_zoom_default = "" if map_zoom is None else str(map_zoom)
    
    # Currentframe is this python file. f_back enabling going back to the frame where CLC is called.
    frame = inspect.currentframe().f_back
    globals_from_jupyter = frame.f_globals  # we can bring both global or local. For making globals_from_jupyter accessible from outside.
    
    #print(caller_gloables.get("input_attributes"))
    # Widget definitions
    input_csv_widget = widgets.Text(
        description='Input Attribute:',
        value='attributes',
        style={'description_width': '160px'},
        layout=widgets.Layout(width='400px'),
        #tooltip='Enter the CSV file name containing the attribute data.'
    )
    input_csv_help = widgets.Label(value='Enter the CSV file variable name containing the attribute data.')
    
    shapefile_widget = widgets.Text(
        description='Input Shapefile:',
        value='shapefile',
        style={'description_width': '160px'},
        layout=widgets.Layout(width='400px'),
        #tooltip='Enter the shapefile (.shp) variable name containing geographic data.'
    )
    shapefile_help = widgets.Label(value='Enter the shapefile (.shp) variable name containing geographic data.')    
    
    title_widget = widgets.Text(
        description='Title:',
        value='Comparison of Temporal Patterns of Covid-19 Confirmed Rate between US Counties',
        layout=widgets.Layout(width='600px'),
        style={'description_width': '160px'},
        #tooltip='Enter the title for the result visualization.'
    )
    title_help = widgets.Label(value='Enter the title for the result visualization.')  
    
    subject_widget = widgets.Text(
        description="Chart Title:",
        value="Temporal Patterns of COVID-19 Cases per 10,000 Population in Two Selected Regions",
        layout=widgets.Layout(width='600px'),
        style={'description_width': '160px'},
        #tooltip='Enter the text to be displayed at the top of all line charts. For example: "Temporal Patterns of Risk Factors..'
    )
    subject_help = widgets.Label(value="Enter the text to be displayed at the top of the line charts, such as 'Temporal Patterns of COVID-19 Rates.'")  
    
    filename_suffix_widget = widgets.Text(
        description="Output Folder Name:",
        value="COVID_CLC",
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Enter the name of the output folder for generated files.'
    )
    filename_suffix_help = widgets.Label(value='Enter the name of the output folder for generated files.')      
    
    periods_widget = widgets.SelectMultiple(
        description='Periods:',
        options=['All'],
        value=['All'],
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Specify the periods as comma-separated values for specific periods or select "All" to display all available periods.'
    )
    periods_help = widgets.Label(value='Select time ranges for temporal charts; "All" for all ranges. Use "Ctrl" for multiple choices. Acceptable formats: YYYY, MM-DD, or MM-DD-YYYY')
    

    # Widget for map center (latitude and longitude)
    map_center_widget = widgets.Text(
        description="Map Center (Lat, Lon):",
        value=map_center_default,  # Set from parameter or empty string
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Specify the map center as "latitude, longitude" (e.g., 38, -97).'
    )
    
    # Widget for map zoom level
    map_zoom_widget = widgets.Text(
        description="Map Zoom Level:",
        value=map_zoom_default,  # Set from parameter or empty string
        layout=widgets.Layout(width='300px'),
        style={'description_width': '160px'},
        #tooltip='Specify the initial zoom level of the map (optional).'
    ) 

    num_of_maps_widget = widgets.IntSlider(
        description="The Number of Maps:",
        value=2,
        min=1,
        max=5,
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Specify the number of maps to be displayed. Multiple maps can be displayed.'
    )
    
    sort_layers_widget = widgets.Dropdown(
        options=['temporal', 'compare'],
        description='Sort Layers:',
        value='temporal',
        style={'description_width': '160px'},
        layout=widgets.Layout(width='400px'),
        #tooltip='"temporal" for examining temporal changes of distribution, "compare" for comparing different attributes for a specific year.'
    )
    sort_layers_help = widgets.Label(value='Choose "Temporal" to compare the same variable at different points in time or "Compare" to compare different variables at the same point in time.')
    
    initial_layers_widget = widgets.Textarea(
        description="Initial Layers:",
        value="2020-04-06_confirmed_rate,2020-07-20_confirmed_rate",
        layout=widgets.Layout(width='600px', height='150px'),
        style={'description_width': '160px'},
        #tooltip='Specify default names of map layers displayed on the first view of maps. It should not exceed the number of maps you specified. \n Try Initial_Layers(attributes) to see all possible options. E.g., 2020-04-06_confirmed_rate, 2020-07-20_confirmed_rate'
    )
    initial_layers_help = widgets.Label(value='Specify default names of map layers displayed on the first view of the two maps. \nTry Initial_Layers(attributes) to see all possible options. E.g., 2020-04-06_confirmed_rate, 2020-07-20_confirmed_rate')
    
    
    # Change from SelectMultiple to Dropdown for single selection
    variables_widget = widgets.Dropdown(
        description="Variable:",
        options=[],  # Options will be dynamically updated
        layout=widgets.Layout(width='600px'),
        style={'description_width': '160px'},
        #tooltip='Select a single variable to include in the visualization. Columns are dynamically populated from the input CSV.'
    )
    variables_help = widgets.Label(value='Select a single variable to include in the visualization.') 
    
    '''
    variables_widget = widgets.SelectMultiple(
        description="Variables:",
        layout=widgets.Layout(width='600px', height='150px', overflow='auto'),
        style={'description_width': '200px'},
        #tooltip='Enter at least one variable. "Ctrl" for selecting multiple variables.'
    )
    '''
    
    map_width_widget = widgets.Text(
        description="Map Width (px):",
        value="650px",
        layout=widgets.Layout(width='300px'),
        style={'description_width': '160px'},
        #tooltip='Specify the width of the map in pixels.'
    )
    
    map_height_widget = widgets.Text(
        description="Map Height (px):",
        value="450px",
        layout=widgets.Layout(width='300px'),
        style={'description_width': '160px'},
        #tooltip='Specify the height of the map in pixels.'
    )

    chart_info = widgets.HTML(
        value="Select the chart to be visualized.",
        layout=widgets.Layout(width='600px')
    )
    
    top10_chart_widget = widgets.Checkbox(
        description="Top 10 Chart",
        value=True,
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Enable or disable the display of the top 10 chart.'
    )
    
    clc_widget = widgets.Checkbox(
        description="Comparison Line Chart (CLC):",
        value=True,
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Enable or disable the Multiple Line Chart (MLC) feature.'
    )
    
    
    num_clc_widget = widgets.IntSlider(
        description="The number of CLC:",
        value=0,  # Default to 0 initially
        min=0,  # Allow 0 as the minimum
        max=0,  # Will be updated dynamically based on variable selection
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Select the number of periods, x values'
    )
    
    # Number of MLCs widget
    num_mlc_widget = widgets.IntSlider(
        description="The number of CLC:",
        value=0,  # Default to 0 initially
        min=0,  # Allow 0 as the minimum
        max=0,  # Will be updated dynamically based on variable selection
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Select the number of Multiple Line Charts (MLCs) to display.'
    )
    num_mlc_info = widgets.HTML(
        value="<i>This number cannot be greater than the variables you selected above.</i>",
        layout=widgets.Layout(width='600px')
    )
    
    titles_mlc_widget = widgets.Textarea(
        description="Titles of MLCs:",
        value="",
        layout=widgets.Layout(width='600px', height='90px'),
        style={'description_width': '160px'},
        #tooltip='Titles for each line chart in order. The number of titles should be equal to the number of MLCs you specified. \n For example, "1. Confirmed Rate, 2. Death Rate, 3. Cumulative Confirmed Rate"'
    )
    #titles_mlc_help = widgets.Label(value='Titles for each line chart in order. The number of titles should be equal to the number of MLCs you specified.\nFor example, "1. Confirmed Rate, 2. Death Rate, 3. Cumulative Confirmed Rate"')

    #Select the region to visualize temporal patterns at initial view of the Comparison Line Chart (CLC):
    # Combobox widgets for Default Region CLC

    default_region_info_CLC = widgets.HTML(
        value="Select the region to display temporal patterns in the initial view of the Comparison Line Chart (CLC):",
        layout=widgets.Layout(width='600px')
    )
 
    default_region_clc_widget_1 = widgets.Combobox(
        description='Default Region 1:',
        options=[],  # Will be populated dynamically based on the shapefile
        ensure_option=True,  # Allow only options from the provided list
        placeholder='Type to search...',  # Placeholder text
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Select the first default region (Geoid) for Comparison Line Chart (CLC).'
    )
    
    default_region_clc_widget_2 = widgets.Combobox(
        description='Default Region 2:',
        options=[],  # Will be populated dynamically based on the shapefile
        ensure_option=True,  # Allow only options from the provided list
        placeholder='Type to search...',  # Placeholder text
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Select the second default region (Geoid) for Comparison Line Chart (CLC).'
    )     
    
    
    default_region_widget = widgets.Combobox(
        description='Default Region (Geoid):',
        options=[],  # Will be populated based on shapefile
        ensure_option=True,  # Allow only options from the provided list
        placeholder='Type to search...',
        layout=widgets.Layout(width='400px'),
        style={'description_width': '160px'},
        #tooltip='Select the default region (Geoid) to focus on initially.'
    )
    
    # Run button
    run_button = widgets.Button(
        description="Generate Visualization",
        button_style="success",
        layout=widgets.Layout(width='300px', height='50px'),
        #tooltip='Click to generate the visualization based on the specified parameters.'
    )
    output_area = widgets.Output()

    # Layout definition
    data_widgets = widgets.VBox([
        widgets.HBox([input_csv_widget, input_csv_help]),
        widgets.HBox([shapefile_widget, shapefile_help]),
        widgets.HBox([title_widget, title_help]),
        widgets.HBox([subject_widget, subject_help]),
        widgets.HBox([filename_suffix_widget, filename_suffix_help]),
        widgets.HBox([periods_widget, periods_help]),        
        widgets.HBox([variables_widget, variables_help]),     
        widgets.HBox([sort_layers_widget, sort_layers_help]),
    ], layout=widgets.Layout(padding='10px'))

    map_widgets = widgets.VBox([
        chart_info,
        top10_chart_widget,
        #mlc_widget,
        #num_mlc_widget,
        clc_widget,  
        #num_clc_widget, 
        #num_mlc_info,
        #default_region_widget,
        default_region_info_CLC,
        default_region_clc_widget_1,
        default_region_clc_widget_2
    ], layout=widgets.Layout(padding='10px'))

    optional_settings_widgets = widgets.VBox([
        map_center_widget,
        map_zoom_widget,         
        widgets.HBox([map_width_widget]),
        widgets.HBox([map_height_widget]),
        initial_layers_widget,
        initial_layers_help,
        #titles_mlc_widget,
        #titles_mlc_help
    ], layout=widgets.Layout(padding='10px'))

    map_settings_widgets = widgets.VBox([
        widgets.HBox([map_width_widget]),
        #titles_mlc_widget
    ], layout=widgets.Layout(padding='10px'))
    



    # Full layout including the run button and output
    tab = widgets.Tab([
        widgets.VBox([data_widgets, map_widgets], layout=widgets.Layout(padding='10px')),
        optional_settings_widgets
    ])
    tab.set_title(0, 'Required parameters')
    tab.set_title(1, 'Optional parameters')

    gui = widgets.VBox([
        tab,
        run_button,
        output_area
    ], layout=widgets.Layout(padding='10px', width='100%', align_items='flex-start'))

    display(gui)

    # Function to update variable options based on selected CSV
    def update_default_region_options():
        """
        Updates the 'Default Region (Geoid):' options based on the shapefile widget's value.
        Displays the second column for user selection but assigns the corresponding value from the first column.
        """
        try:
            shapefile = globals_from_jupyter.get(shapefile_widget.value)  # Retrieve the GeoDataFrame  #eval should be changed to globals_from_jupyter
            #shapefile = eval(shapefile_widget.value)
            if isinstance(shapefile, gpd.GeoDataFrame):
                # Ensure the shapefile has at least two columns
                if shapefile.shape[1] >= 2:
                    # Create a mapping from the second column to the first column
                    display_values = shapefile.iloc[:, 1].astype(str).tolist()  # Second column for display
                    actual_values = shapefile.iloc[:, 0].astype(str).tolist()  # First column for actual values
                    default_region_mapping = dict(zip(display_values, actual_values))
                    
                    # Populate the options and set the mapping
                    # default_region_widget.options = display_values
                    default_region_clc_widget_1.options = display_values
                    default_region_clc_widget_2.options = display_values
                    
                    # default_region_widget.mapping = default_region_mapping
                    default_region_clc_widget_1.mapping = default_region_mapping
                    default_region_clc_widget_2.mapping = default_region_mapping
                    
                    # default_region_widget.value = ""  # Set to an empty string instead of None
                    default_region_clc_widget_1.value = ""  # Set to an empty string instead of None
                    default_region_clc_widget_2.value = ""  # Set to an empty string instead of None
                else:
                    print("Error: Shapefile must have at least two columns.")
                    # default_region_widget.options = []
                    default_region_clc_widget_1.options = []
                    default_region_clc_widget_2.options = []
                    
                    # default_region_widget.value = ""  # Set to an empty string
                    default_region_clc_widget_1.value = ""  # Set to an empty string
                    default_region_clc_widget_2.value = ""  # Set to an empty string
            else:
                print("Error: Shapefile is not a valid GeoDataFrame.")
                # default_region_widget.options = []
                default_region_clc_widget_1.options = []
                default_region_clc_widget_2.options = []
                
                # default_region_widget.value = ""  # Set to an empty string
                default_region_clc_widget_1.value = ""  # Set to an empty string
                default_region_clc_widget_2.value = ""  # Set to an empty string
        except Exception as e:
            print(f"Error updating default region options: {e}")
            # default_region_widget.options = []
            default_region_clc_widget_1.options = []
            default_region_clc_widget_2.options = []
            
            # default_region_widget.value = ""  # Set to an empty string
            default_region_clc_widget_1.value = ""  # Set to an empty string
            default_region_clc_widget_2.value = ""  # Set to an empty string
    


    
    def handle_default_region_selection(change):
        """
        Removes the first option from 'Default Region (Geoid):' when a region is selected by the user.
        """
        try:
            selected_region = change['new']
            if selected_region and selected_region in default_region_widget.options:
                # Remove the first option after the user selects a region
                default_region_widget.options = [
                    region for region in default_region_widget.options if region != selected_region
                ]
        except Exception as e:
            print(f"Error handling default region selection: {e}")

        try:
            selected_region = change['new']
            if selected_region and selected_region in default_region_clc_widget_1.options:
                # Remove the first option after the user selects a region
                default_region_clc_widget_1.options = [
                    region for region in default_region_clc_widget_1.options if region != selected_region
                ]
        except Exception as e:
            print(f"Error handling default region selection: {e}")
            
        try:
            selected_region = change['new']
            if selected_region and selected_region in default_region_clc_widget_2.options:
                # Remove the first option after the user selects a region
                default_region_clc_widget_2.options = [
                    region for region in default_region_clc_widget_2.options if region != selected_region
                ]
        except Exception as e:
            print(f"Error handling default region selection: {e}")            

            
            
    # Function to update variable options based on selected CSV
    def update_variables_options(change=None):
        try:
            # Retrieve the input CSV variable name from the widget
            input_csv_name = input_csv_widget.value
            # Get the corresponding DataFrame from globals
            df = globals_from_jupyter.get(input_csv_name, None)

            if isinstance(df, pd.DataFrame):
                # Update the "Variables" widget with the column names starting from the third column
                # Update the "Variables" widget with the column names starting from the third column
                column_options = df.columns[2:]
                variables_widget.options = list(column_options)
    
                # Set the default value to the first column if available
                if column_options.any():
                    variables_widget.value = column_options[0]
                else:
                    variables_widget.value = None

                # Update the "Periods" widget with 'All' and unique values from the second column
                if df.shape[1] > 1:  # Ensure the DataFrame has at least two columns
                    unique_periods = df.iloc[:, 1].dropna().astype(str).unique().tolist()
                    periods_widget.options = ['All'] + unique_periods
                    periods_widget.value = ['All']
                else:
                    periods_widget.options = ['All']
                    periods_widget.value = ['All']
            else:
                # Reset options if the CSV is invalid
                variables_widget.options = []
                variables_widget.value = None
                periods_widget.options = ['All']
                periods_widget.value = ['All']
                print(f"Error: {input_csv_name} is not a valid DataFrame.")
        except Exception as e:
            # Fallback for unexpected errors
            variables_widget.options = []
            variables_widget.value = None
            periods_widget.options = ['All']
            periods_widget.value = ['All']
            print(f"Error updating variables and periods: {e}")

    # Function to update the max and default value of the Number of MLCs widget
    def update_num_mlc(change):
        selected_variables = list(change['new'])
        num_mlc_widget.max = len(selected_variables)  # Update max based on selected variables
        num_mlc_widget.value = num_mlc_widget.max  # Set default value to the maximum

    # Force update of periods widget on initialization or when input changes
    def force_update_periods():
        update_variables_options({'new': input_csv_widget.value})
        num_mlc_widget.max = len(change['new'])
        if num_mlc_widget.value > len(change['new']):
            num_mlc_widget.value = len(change['new'])

    def update_num_clc_widget_max():
        """
        Updates the maximum value of "The number of CLC:" slider 
        based on the number of unique values in the second column of the input CSV data.
        """
        try:
            # Retrieve the input CSV DataFrame
            input_csv = globals_from_jupyter.get(input_csv_widget.value, None)
    
            if isinstance(input_csv, pd.DataFrame):
                # Ensure the DataFrame has at least two columns
                if input_csv.shape[1] > 1:
                    unique_values = input_csv.iloc[:, 1].dropna().unique()  # Get unique values in the second column
                    num_clc_widget.max = len(unique_values)  # Set the maximum value of the slider
                    num_clc_widget.value = num_clc_widget.max  # Set default value to the maximum
                else:
                    num_clc_widget.max = 0
                    num_clc_widget.value = 0
                    print("Error: The input DataFrame must have at least two columns.")
            else:
                num_clc_widget.max = 0
                num_clc_widget.value = 0
                print(f"Error: '{input_csv_widget.value}' is not a valid DataFrame.")
        except Exception as e:
            print(f"Error updating 'The number of CLC:' widget max: {e}")
            num_clc_widget.max = 0
            num_clc_widget.value = 0

        
    # Function to handle visualization generation
    def generate_visualization(_):
        with output_area:
            clear_output()
            try:
                # Parse map center input
                map_center = map_center_widget.value.strip()
                if map_center:
                    try:
                        lat_lon = map_center.split(',')
                        if len(lat_lon) != 2:
                            raise ValueError("Map Center must have exactly two values: latitude and longitude.")
                        lat, lon = map(float, lat_lon)
                        if not (-90 <= lat <= 90):
                            raise ValueError("Latitude must be between -90 and 90.")
                        if not (-180 <= lon <= 180):
                            raise ValueError("Longitude must be between -180 and 180.")
                        map_center = [lat, lon]
                    except ValueError:
                        raise ValueError("Map Center must be in the format 'latitude, longitude' (e.g., 38, -97).")
                else:
                    map_center = None  # Default to None if not provided
    
                # Parse map zoom level input
                map_zoom = map_zoom_widget.value
                if map_zoom:
                    try:
                        map_zoom = int(map_zoom)
                        if not (1 <= map_zoom <= 20):
                            raise ValueError("Zoom level must be between 1 and 20.")
                    except ValueError:
                        raise ValueError("Map Zoom Level must be an integer between 1 and 20.")
                else:
                    map_zoom = None  # Default to None if not provided
                    
                # Check if at least one variable is selected
                if not variables_widget.value:
                    print("Error: At least one variable should be selected.")
                    return  # Halt execution if no variables are selected
                
                # Load the input CSV and shapefile dynamically
                input_csv = globals_from_jupyter.get(input_csv_widget.value, None)
                shapefile = globals_from_jupyter.get(shapefile_widget.value, None)
    
                # Validate inputs
                if not isinstance(input_csv, pd.DataFrame):
                    raise ValueError('Input CSV is not a valid DataFrame or variable does not exist in the current scope')
                if not isinstance(shapefile, gpd.GeoDataFrame):
                    raise ValueError('Shapefile is not a valid GeoDataFrame or variable does not exist in the current scope')
    
                # Process the selected variable (ensure it's treated as a list)
                selected_variable = [variables_widget.value]  # Wrap the single value in a list
                
        
                # Retrieve the selected region and map it to the corresponding actual value
                selected_region_display = default_region_widget.value
                selected_region = None
                if selected_region_display and hasattr(default_region_widget, 'mapping'):
                    selected_region = default_region_widget.mapping.get(selected_region_display)

                # Retrieve the selected region and map it to the corresponding actual value
                selected_region_clc_1_display = default_region_clc_widget_1.value
                selected_region_clc_1 = None
                if selected_region_clc_1_display and hasattr(default_region_clc_widget_1, 'mapping'):
                    selected_region_clc_1 = default_region_clc_widget_1.mapping.get(selected_region_clc_1_display)                    

                # Retrieve the selected region and map it to the corresponding actual value
                selected_region_clc_2_display = default_region_clc_widget_2.value
                selected_region_clc_2 = None
                if selected_region_clc_2_display and hasattr(default_region_clc_widget_2, 'mapping'):
                    selected_region_clc_2 = default_region_clc_widget_2.mapping.get(selected_region_clc_2_display)                     
                
                # Retrieve the selected regions for CLC
                default_region_clc = [
                    selected_region_clc_1,
                    selected_region_clc_2
                ]
                
                # Parse and validate periods
                periods = 'All' if 'All' in periods_widget.value else [p for p in periods_widget.value if check_dateformat(p)]
                
                # check if all values are YYYY
                year_periods = True
                for p in periods_widget.value:
                    # it means YYYY
                    if not p.isdigit():
                        year_periods = False
                
                if year_periods:
                    periods = []
                    for p in periods_widget.value:
                        periods.append(int(p))
                        
                if not periods:
                    print("Error: Invalid or empty period selection.")
                    return
            
                # Parse parameters
                params = {
                    'title': title_widget.value,
                    'Subject': subject_widget.value,
                    'filename_suffix': filename_suffix_widget.value if filename_suffix_widget.value else "default_suffix",
                    'inputCSV': input_csv,
                    'shapefile': shapefile,
                    'periods': (
                        'All' if 'All' in periods 
                        else periods
                     ),
                    'variables': selected_variable,
                    #'NumOfMaps': num_of_maps_widget.value,
                    'Initial_map_center': map_center,
                    'Initial_map_zoom_level': int(map_zoom_widget.value) if map_zoom_widget.value else None,                    
                    'SortLayers': sort_layers_widget.value,
                    #'InitialLayers': initial_layers_widget.value.split(","),
                    'InitialLayers': [layer.strip() for layer in initial_layers_widget.value.split(",")],
                    'Map_width': map_width_widget.value,
                    'Map_height': map_height_widget.value,
                    'Top10_Chart': top10_chart_widget.value,
                    'Comparision_Chart': clc_widget.value,
                    'DefaultRegion_CLC': default_region_clc,
                }
                
                #print(f"Parameters: {params}")
    
                # Call visualization and logging functions
                try:
                    Adaptive_Choropleth_Mapper_viz(params)
                    print("Visualization generated successfully!")
                except Exception as viz_error:
                    print(f"Error generating visualization: {viz_error}")
                Adaptive_Choropleth_Mapper_log(params)
            except Exception as e:
                print(f"Error: {e}")
    
    
    # Remove redundant observers and keep only the necessary ones
    run_button.on_click(generate_visualization)
    input_csv_widget.observe(update_variables_options, names='value')
    # Attach observer for Variables widget to update Number of MLCs widget
    variables_widget.observe(update_num_mlc, names='value')
    
    # Attach observer to update the "The number of CLC:" slider when the input CSV changes
    '''
    input_csv_widget.observe(lambda change: update_num_clc_widget_max(), names='value')
    update_num_clc_widget_max()
    '''

    shapefile_widget.observe(lambda change: update_default_region_options(), names='value')
    # Attach observer to default_region_widget for the selection change
    default_region_widget.observe(handle_default_region_selection, names='value')
    # Attach observer to update Default Region CLC widgets when shapefile changes

    # Initialize variable options and other widget settings
    update_variables_options({'new': input_csv_widget.value})
    update_default_region_options()

    
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
    
    #Adaptive_Choropleth_Mapper_viz(param_MLC_COVID_San_Diego)
    #Adaptive_Choropleth_Mapper_log(param_MLC_COVID_San_Diego)
    
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
