# CyberGIS-Viz

<p align="center">
<img height=100 src="images/CyberGIS_Viz.PNG" alt="CyberGIS_Viz.PNG"/>
</p>

<h2 align="center" style="margin-top:-10px">CyberGIS-Viz is an open-source software tool for interactive geospatial visualization and scalable visual analytics.</h2> 
<br/>


CyberGIS-Viz integrates cutting-edge cyberGIS and online visualization capabilities into a suite of software modules for visualization and visual analytical approaches to knowledge discovery based on geospatial data. Key features of the current CyberGIS-Viz implementation include: (1) comparative visualization of spatiotemporal patterns through choropleth maps; (2) dynamic cartographic mapping linked with charts to explore high-dimensional data; (3) reproducible visual analytics through integration with CyberGIS-Jupyter; and (4) multi-language support including both Python and Javascript. [Firefox is the recommended web browser for reaping the best performance of CyberGIS-Viz.](https://www.mozilla.org/en-US/firefox/new/)

<br/><br/>

## QuickStart
### CyberGIS-Viz_JS
&nbsp;&nbsp;&nbsp;&nbsp;For Javascript users, example visaulizations are available in the two folders below:<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;JS_Quantitative_Data_VIZ<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;JS_Categorical_Data_VIZ<br/>
### CyberGIS-Viz_PYTHON
&nbsp;&nbsp;&nbsp;&nbsp;For python users, example visaulizations are available in the two folders below:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;PYTHON_Quantitative_Data_VIZ/Adaptive_Choropleth_Mapper.ipynb
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;PYTHON_Quantitative_Data_VIZ/Adaptive_Choropleth_Mapper_geosnap.ipynb
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;PYTHON_Categorical_Data_VIZ/Qualitative_Analysis_Mapper.ipynb

## CyberGISX
**You can run CyberGIS-Viz in your Jupyter Notebook installed on your PC as well as in CybearGISX. We recommend that you use CyberGISX because all the required packages have been integrated in CyberGISX**.<br/>
&nbsp;&nbsp;&nbsp;&nbsp;To use it in CyberGISX, follow steps below:
1. If you do not have a CyerGISX account, create a CyberGISX account with your GitHub id at https://cybergisxhub.cigi.illinois.edu
2. Open up the CyberGIX, click the "new" button on the top right corner, and select python3 and enter the command line below to download CyberGIS-Viz.
```bash
	!git clone https://github.com/cybergis/CyberGIS-Viz
```    
3. This example (PYTHON_Quantitative_Data_VIZ/Adaptive_Choropleth_Mapper_geosnap.ipynb) uses data from [LTDB](https://s4.ad.brown.edu/projects/diversity/researcher/LTDB.htm). In order to use the data from [LTDB](https://s4.ad.brown.edu/projects/diversity/researcher/LTDB.htm), please follow insturctions in Install_geosnap.ipynb.
4. Uncomment out the code below:

```bash  
	#This is for CyberGISX. Uncomment two command lines below when you run in CyberGIX Environment
	#local_dir1 = servers1 + cwd 
	#local_dir2 = servers2 + cwd
```   
&nbsp;&nbsp;&nbsp;&nbsp;in the python code below: <br/>

```bash  
	PYTHON_Quantitative_Data_VIZ/Adaptive_Choropleth_Mapper.py
	PYTHON_Quantitative_Data_VIZ/Adaptive_Choropleth_Mapper_geosnap.py
	PYTHON_Categorical_Data_VIZ/Qualitative_Analysis_Mapper.py  
``` 
<br/><br/>
## Visualization Modules
<font color="green">
Images below show visualizations that you can create using CyberGIS-Viz. Click the image to see the full size.</font >

###  Quntitative Data Visualization
<ul>
        <li>Adaptive Choropleth Mapper (ACM)</li>
        <ul><li> <a href="http://su-gis.iptime.org/ACM">Click to see more information.</a></li></ul>   
        <li>Adaptive Choropleth Mapper with Stacked Chart
	        <ul><li> The Stacked Chart visualizes the temporal change </li></ul>    
       </li>    
        <img height=100px src="http://su-gis.iptime.org/MapLinksPlot/images/ACM.PNG" alt="MapLinksPlot"/>
        <li>Adaptive Choropelth Mapper with Correlogram</li>
        <img height=250px src="http://su-gis.iptime.org/MapLinksPlot/images/ACM_Correlogram.PNG" alt="MapLinksPlot"/>
        <li>Adaptive Choropleth Mapper with Scatter Plot</li>
      <img height=150px src="http://su-gis.iptime.org/MapLinksPlot/images/ACM_Scatter.PNG" alt="MapLinksPlot"/>
        <li>Adaptive Choropleth Mapper with Parallel Coordinate Plot </li>
         <img height=200px src="http://su-gis.iptime.org/MapLinksPlot/images/ACM_PCP.PNG" alt="MapLinksPlot"/>
</ul>     
             
###  Categorical Data Visualization

<ul>
        <li>Qualitative_Analysis_Mapper</li>
        <img height=100px src="http://su-gis.iptime.org/MapLinksPlot/images/Qual.PNG" alt="MapLinksPlot"/>
        <li>Qualitative_Analysis_Mapper with Stacked Chart</li>
        	        <ul><li> The Stacked Chart visualizes the temporal change </li></ul>    
        <img height=100px src="http://su-gis.iptime.org/MapLinksPlot/images/Qual_Stacked.PNG" alt="MapLinksPlot"/>
        <li>Qualitative_Analysis_Mapper with Parallel Categories Diagram</li>
                	        <ul><li> Parallel Categories Diagram represents how the categorical data changes over time in quantity. <a href="https://plotly.com/javascript/parallel-categories-diagram">Click to see more info.</a></li></ul>    
      <img height=200px src="http://su-gis.iptime.org/MapLinksPlot/images/Qual_PCD.PNG" alt="MapLinksPlot"/>
        <li>Qualitative_Analysis_Mapper with Chord Diagram</li>
        <ul><li> The Chord Diagram quantifies changes of categorical data between the two periods </li></ul> 
         <img height=200px src="http://su-gis.iptime.org/MapLinksPlot/images/Qual_CD.PNG" alt="MapLinksPlot"/>
</ul> 

## Data
Visualizations created by CyberGIS-Viz are using a small subset of [LTDB](https://s4.ad.brown.edu/projects/diversity/researcher/LTDB.htm). [LTDB](https://s4.ad.brown.edu/projects/diversity/researcher/LTDB.htm) provides socioeconomic and demographic data with harmonized boundaries from 1970 to 2010 decennially. If you need the entire dataset, visit this [website](https://s4.ad.brown.edu/projects/diversity/researcher/LTDB.htm) to download.

## Related Resources

* [Leaflet](https://leafletjs.com) 
* [PlotlyJS](https://plot.ly/javascript/) 
* [D3](https://d3js.org/) 
* [CyberGISX](https://github.com/cybergis) 
* [GEOSNAP VIZ](https://github.com/spatialucr/geosnap-viz) 

## Contributors

The lead developer of CyberGIS-Viz is Dr. Su Yeon Han at the [CyberGIS Center for Advanced Digital and Spatial Studies (CyberGIS Center)](https://cybergis.illinois.edu/) and the Principal Investigator of CyberGIS-Viz is Dr. Shaowen Wang at CyberGIS Center. This software repository is primarily maintained by [CyberGIS Center](https://cybergis.illinois.edu/). Please email any questions to [help@cybergis.org](mailto:help@cybergis.org).

## License

**This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/cybergis/CyberGIS-Viz/blob/master/LICENSE) file for details.**

## Funding

The CyberGIS-Viz project is supported by the CyberGIS Center for Advanced Digital and Spatial Studies at the University of Illinois at Urbana-Champaign.




