// Define the number of maps and some configuration parameters that you want to visualize.
var SubjectName = "NEIGHBORHOOD";
var InitialLayers = ["1980", "1990", "2000", "2010"];

/* Map Extent and Zoom level will be automatically adjusted when you do not define map center and zoom level */
//var Initial_map_center = [34.0522, -117.9];  
//var Initial_map_zoom_level = 8;   

var Maps_of_Categorical_Data = true;							//choropleth map: Maps representing categorical data 
var Stacked_Chart = true;				//stacked chart: Temporal Change
var Parallel_Categories_Diagram = true;	//parallel categories diagram
var Chord_Diagram = true;					//chord diagram
  
var Num_Of_Decimal_Places = 2;                             // default = 2

var Map_width  = "400px";                                  // min 350px
var Map_height = "400px";                                  // min 300px