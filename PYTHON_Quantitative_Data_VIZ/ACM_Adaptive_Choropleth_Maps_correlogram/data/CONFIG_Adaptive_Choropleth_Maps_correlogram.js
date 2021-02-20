// Define the number of maps that you want to visualize. upto 15 maps are supported.
var NumOfMaps = 4;

//Define variables that you want to visualize at initial views. For example, enter five variables when the NumOfMaps is equal to 5.
var InitialLayers = ["2010 % white (non-Hispanic)", "2010 % black (non-Hispanic)", "2010 % Hispanic", "2010 % Asian and Pacific Islander race", "2010 % foreign born", "2010 % with 4-year college degree or more", "2010 % unemployed", "2010 % manufacturing employees", "2010 % in poverty (total)", "2010 % vacant units", "2010 % owner-occupied units", "2010 % multi-family units", "2010 Median home value", "2010 % structures more than 30 years old", "2010 % HH in neighborhood 10 years or less", "2010 % 17 and under (total)", "2010 % 60 and older (total)"];

/*Define initial map center and zoom level below. Map Extent and Zoom level will be automatically adjusted when you do not define map center and zoom level. Double-slashes  in the front need to be deleted to make them effective*/
//var Initial_map_center = [34.0522, -117.9];  
//var Initial_map_zoom_level = 8;   

/* It shows the change in the number of polygons belonging to each class intervals in different 
   It appears only when the map extent and the class intervals of all maps are same.
   To make all maps have the same map extent and class intervals, enable "Grouping All" or click "Sync" on one of maps   */
var Stacked_Chart = false;
var Correlogram = true;
var Scatter_Plot = false;
var Parallel_Coordinates_Plot = false;

// The number of digit after the decial point.
var Num_Of_Decimal_Places = 2;                             // default = 1 

//Adjust the size of maps
var Map_width  = "400px";                                  // min 350px
var Map_height  = "400px";                                  // min 300px

//Adjust the size of the stacked chart. Double-slashes in the front need to be deleted to make them effective
//var Chart_width  = "350px";                                // min 350px
//var Chart_height = "350px";                                // min 300px


