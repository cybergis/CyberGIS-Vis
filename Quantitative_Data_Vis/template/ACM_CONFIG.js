// Define subject of this visaulize
var Subject = "";

// Define the number of maps that you want to visualize. upto 15 maps are supported.
var NumOfMaps = 2;


// Define the order to show the drop-down list fo the Layer. "compare" or "temporal" 
var SortLayers = "";


// Define the number of variable that you want to visaulize Parallel Coordinates Plot. 
var NumOfPCP = 0;
//Define variables that you want to visualize at PCP.
var InitialVariablePCP = [];


// Define the number of variable that you want to visaulize Comparision Line Chart. 
var NumOfCLC = 0;
// Define variables that you want to visualize at CLC (Comparision Line Chart).
//var InitialVariableCLC = ["2012_HIV Rate", "2013_HIV Rate", "2014_HIV Rate", "2015_HIV Rate", "2016_HIV Rate", "2017_HIV Rate", "2018_HIV Rate", "2019_HIV Rate", "2020_HIV Rate", "2021_HIV Rate", "2022_HIV Rate"]
var InitialVariableCLC = []; 
var DefaultRegion_CLC = ""; //Set Defaul Region

// Define the number of variable that you want to visualize Multiple Synchronized Line Chart. 
var NumOfMLC = 0;
// Define variables that you want to visualize at MLC (Multiple Synchronized Line Chart).
//var InitialVariableMLC = ["HIV Rate", "HIV Test (/100k pop)", "Rate of Illicit Drug Use", "Health Care Center (/100k pop)"]
var InitialVariableMLC = []
// Define titles that you want to visualize at MLC (Multiple Synchronized Line Chart).
//var titlesOfMLC = ["1. HIV Rate", "2. HIV Test (/100k pop)", "3. Rate of Illicit Drug Use", "4. Health Care Center (/100k pop)"];
var titlesOfMLC = [];
// Define beginning and ending of highlighted areas of MLC. You can do multiple times
// [["begin_X_value","end_X_value","color"], ["begin_X_value","end_X_value","color"]…] 
var DefaultRegion_MLC = ""; //Set Default region
var HighlightMLC = []; //Set  highlighted ranges for x value
var MultipleLineChart_width = "";

//Define the geographic id or name to be display on the top-right corner of the map
//var NameDisplayed = "geoname";

// Define variables that you want to visualize at initial map views. For example, 
// enter five variables when the NumOfMaps is equal to 5.
var InitialLayers = [];

/*Define initial map center and zoom level below. Map Extent and Zoom level will be automatically adjusted when you do not define map center and zoom level. Double-slashes  in the front need to be deleted to make them effective*/
var Initial_map_center = null;  
var Initial_map_zoom_level = null;


// It appears only when the map extent and the class intervals of all maps are same.
// To make all maps have the same map extent and class intervals, 
// enable "Grouping All" or click "Sync" on one of maps
var Stacked_Chart = false;
var Correlogram = false;
var Scatter_Plot = false;
var Top10_Chart = false;
var Parallel_Coordinates_Plot = false;
var Comparision_Chart = false;
var Multiple_Line_Chart = false;

// The number of digit after the decial point.
var Num_Of_Decimal_Places = 2;                              // default = 2 

//Adjust the size of maps
var Map_width  = "";                              // min 350px
var Map_height  = "";                             // min 300px



