var SubjectName = "NEIGHBORHOOD";
var InitialLayers = ["Neighborhood Type"];

// Define the number of maps and some configuration parameters that you want to visualize.

/* Map Extent and Zoom level will be automatically adjusted when you do not define map center and zoom level */
//var Initial_map_center = [34.0522, -117.9];  
//var Initial_map_zoom_level = 8;   

var Index_of_neighborhood_change = true;  //Index_of_neighborhood_change               //choropleth map: Maps representing INC of all metros
var Maps_of_Categorical_Data = true;					//choropleth map: Maps representing index of neighborhood Change
var Stacked_Chart = true;				//stacked chart: Temporal Change in Neighborhoods over years
var Parallel_Categories_Diagram = false;	//parallel categories diagram
var Chord_Diagram = false;					//chord diagram

var HeatmapType = false;                    //HeatmapType: Zscore_Means_across_Clusters
var HeatmapTitle = "Z Score Means across Different Neighborhood Types"

var HorizonalBarChart = false;                    //HorizonalBarChart: Zscore_Means_of_Each_Cluster
var Horizontal_Bar_Title = "Z Score Means in "

var Num_Of_Decimal_Places = 2;                             // default = 2

var Map_width  = "700px";                                  // min 350px
var Map_height = "700px";                                  // min 300px


/////////////////////////////////////////////////////////////////
// Options for only INC (Quant map)                            //
/////////////////////////////////////////////////////////////////

//option for class(the classification method): equal, quantile, std, arithmetic, geometric, quantile
//option for count(the number of classes): 1 to 9
//options for color: Green, Blue, Orange, Red, Pink

var mapAclassification = {class: 'equal', count: 8, color: 'Red'};