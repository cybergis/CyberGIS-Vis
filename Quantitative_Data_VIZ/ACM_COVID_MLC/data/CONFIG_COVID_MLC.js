// Define subject of this visaulize
var Subject = "Temporal Patterns";

// Define the number of maps that you want to visualize. upto 15 maps are supported.
var NumOfMaps = 2;


// Define the number of variable that you want to visaulize Parallel Coordinates Plot. 
var NumOfPCP = 0;
//Define variables that you want to visualize at PCP.
var InitialVariablePCP = [];


// Define the number of variable that you want to visaulize Comparision Line Chart. 
var NumOfCLC = 46;
// Define variables that you want to visualize at CLC (Comparision Line Chart).
//var InitialVariableCLC = ["2012_HIV Rate", "2013_HIV Rate", "2014_HIV Rate", "2015_HIV Rate", "2016_HIV Rate", "2017_HIV Rate", "2018_HIV Rate", "2019_HIV Rate", "2020_HIV Rate", "2021_HIV Rate", "2022_HIV Rate"]
var InitialVariableCLC = [];
var DefaultRegion_CLC = "";

// Define the number of variable that you want to visualize Multiple Synchronized Line Chart. 
var NumOfMLC = 3;
// Define variables that you want to visualize at MLC (Multiple Synchronized Line Chart).
//var InitialVariableMLC = ["HIV Rate", "HIV Test (/100k pop)", "Rate of Illicit Drug Use", "Health Care Center (/100k pop)"]
var InitialVariableMLC = []
// Define titles that you want to visualize at MLC (Multiple Synchronized Line Chart).
//var titlesOfMLC = ["1. HIV Rate", "2. HIV Test (/100k pop)", "3. Rate of Illicit Drug Use", "4. Health Care Center (/100k pop)"];
var titlesOfMLC = ["1. COVID-19 Confirmed Cases (/100k pop)", "2. COVID-19 Death Cases (/100k pop)", "3. The Number of Visitors"];
// Define beginning and ending of highlighted areas of MLC. You can do multiple times
// [["begin_X_value","end_X_value","color"], ["begin_X_value","end_X_value","color"]…] 
var DefaultRegion_MLC = "35620";
var HighlightMLC = []; //Set default region


//Define the geographic id or name to be display on the top-right corner of the map
//var NameDisplayed = "geoname";

// Define variables that you want to visualize at initial map views. For example, 
// enter five variables when the NumOfMaps is equal to 5.
var InitialLayers = ["2020-04-19_Confirmed Rate", "2020-11-01_Confirmed Rate"];

/*Define initial map center and zoom level below. Map Extent and Zoom level will be automatically adjusted when you do not define map center and zoom level. Double-slashes  in the front need to be deleted to make them effective*/
var Initial_map_center = [37, -97];
var Initial_map_zoom_level = 4;


// It appears only when the map extent and the class intervals of all maps are same.
// To make all maps have the same map extent and class intervals, 
// enable "Grouping All" or click "Sync" on one of maps
var Stacked_Chart = false;
var Correlogram = false;
var Scatter_Plot = false;
var Top10_Chart = true;
var Parallel_Coordinates_Plot = false;
var Comparision_Chart = false;
var Multiple_Line_Chart = true;

// The number of digit after the decial point.
var Num_Of_Decimal_Places = 2;                              // default = 1 

//Adjust the size of maps
var Map_width = "650px";
var Map_height  = "400px";                                  // min 300px

//Adjust the size of the stacked chart. Double-slashes in the front need to be deleted to make them effective
var Chart_width  = "350px";									// min 350px
var Chart_height = "350px";									// min 300px


