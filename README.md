# CyberGIS-Vis

<p align="center">
<img height=100 src="images/CyberGIS_Viz.PNG" alt="CyberGIS_Vis.PNG"/>
</p>

<h2 align="center" style="margin-top:-10px">CyberGIS-Vis is an open-source software tool for interactive geospatial visualization and scalable visual analytics.</h2> 
<br/>


CyberGIS-Vis integrates cutting-edge cyberGIS and online visualization capabilities into a suite of software modules for visualization and visual analytical approaches to knowledge discovery based on geospatial data. Key features of the current CyberGIS-Vis implementation include: (1) comparative visualization of spatiotemporal patterns through choropleth maps; (2) dynamic cartographic mapping linked with charts to explore high-dimensional data; (3) reproducible visual analytics through integration with CyberGIS-Jupyter; and (4) multi-language support including both Python and Javascript. [Firefox is the recommended web browser for reaping the best performance of CyberGIS-Vis.](https://www.mozilla.org/en-US/firefox/new/)

<br/><br/>

## QuickStart

**Example visaulizations are available in the two folders below:**<br/>
*	Quantitative_Data_Vis <br/>
*	Categorical_Data_Vis <br/>

## CyberGISX
**You can run CyberGIS-Vis in your Jupyter Notebook installed on your PC as well as in CybearGISX. We recommend that you use CyberGISX because all the required packages have been integrated in CyberGISX.**<br/><br/>

**To use it in CyberGISX, follow steps below:**
1. If you do not have a CyerGISX account, create a CyberGISX account with your GitHub id at https://cybergisxhub.cigi.illinois.edu
2. Open up the CyberGIX, click the "new" button on the top right corner, and select python3 and enter the command line below to download CyberGIS-Vis.
```bash
	    !git clone https://github.com/cybergis/CyberGIS-Vis
```    
3. Open Jupyter notebook below and run.
```bash
        Quantitative_Data_Vis/Adaptive_Chropleth_Mapper.ipynb
        Categorical_Data_Vis/Qualitative_Analysis_Mapper.ipynb
``` 
<br/><br/>
**To run in the loca environment, follow steps below.**
1. Download and install Anaconda at https://www.anaconda.com/.
2. After installation is done, open "Anaconda Prompt" and enter command lines below to create an environment.
```bash
        conda create -n geo-env -c conda-forge geopandas
        conda activate geo-env
        conda install -c conda-forge jupyterlab
        jupyter lab
``` 
3. Open Python Script below.
```bash
        Quantitative_Data_Vis/Adaptive_Chropleth_Mapper.py
        Categorical_Data_Vis/Qualitative_Analysis_Mapper.py
```
4. Comment and uncomment out like below. These are related to create URLs in the Jupyter Server. 
```bash
	#from notebook import notebookapp
	#servers = list(notebookapp.list_running_servers())
        #servers1 = 'https://cybergisx.cigi.illinois.edu'+servers[0]["base_url"]+ 'view'
        #servers2 = 'https://cybergisx.cigi.illinois.edu'+servers[0]["base_url"]+ 'edit'
	local_dir1 = cwd
	local_dir2 = cwd 
	#local_dir1 = servers1 + cwd + '/'
	#local_dir2 = servers2 + cwd + '/' 

```   
5. Open Jupyter notebook below and run.
```bash
        Quantitative_Data_Vis/Adaptive_Chropleth_Mapper.ipynb
        Categorical_Data_Vis/Qualitative_Analysis_Mapper.ipynb
``` 
<br/><br/>
## Visualization Modules
<font color="green">
Images below show visualizations that you can create using CyberGIS-Vis. Click the image to see the full size.</font >

###  Quntitative Data Visualization
<ul>
        <li>Adaptive Choropleth Mapper (ACM)</li>
        <ul><li><a href="http://su-gis.iptime.org/ACM">Click to see more information</a></li></ul>   
		<li>Adaptive Choropleth Mapper with Stacked Chart
	        <ul><li> The Stacked Chart visualizes the temporal change. Click to see 
			 <a href="http://su-gis.iptime.org/CyberGIS-Vis/videos/VIZ_Stacked_Chart.mp4"> demo.</a>
			</li></ul>    
       </li> 
        <img height=100px src="http://su-gis.iptime.org/CyberGIS-Vis/images/ACM.PNG" alt="ACM"/>
		<li>Adaptive Choropelth Mapper with Correlogram
	        <ul><li> Click to see 
			 <a href="http://su-gis.iptime.org/CyberGIS-Vis/videos/VIZ_Correlogram_Tutorial.mp4"> Tutorial </a> and 
			 <a href="http://su-gis.iptime.org/CyberGIS-Vis/videos/VIZ_Correlogram_demo.mp4"> Demo </a> 
			</li></ul> 		
		</li>
        <img height=250px src="http://su-gis.iptime.org/CyberGIS-Vis/images/ACM_Correlogram.PNG" alt="ACM_Correlogram"/>
        <li>Adaptive Choropleth Mapper with Scatter Plot
	        <ul><li> Click to see 
			 <a href="http://su-gis.iptime.org/CyberGIS-Vis/videos/VIZ_Scatter_Tutorial.mp4"> Tutorial </a> and 
			 <a href="http://su-gis.iptime.org/CyberGIS-Vis/videos/VIZ_Scatter_Demo.mp4"> Demo </a> 
			</li></ul> 	
		</li>
		<img height=150px src="http://su-gis.iptime.org/CyberGIS-Vis/images/ACM_Scatter.png" alt="ACM_Scatter"/>
        <li>Adaptive Choropleth Mapper with Parallel Coordinate Plot (PCP) 
	        <ul><li> Click to see 
			 <a href="http://su-gis.iptime.org/CyberGIS-Vis/videos/VIZ_PCP_Tutorial.mp4"> Tutorial </a> and 
			 <a href="http://su-gis.iptime.org/CyberGIS-Vis/videos/VIZ_PCP_demo.mp4"> Demo </a> 
			</li></ul> 	
		</li>
        <img height=200px src="http://su-gis.iptime.org/CyberGIS-Vis/images/ACM_PCP.PNG" alt="ACM_PCP"/>
        <li>Adaptive Choropleth Mapper with Multiple Linked Chart (MLC) 
	        <ul><li> Click to see 
			 <a href="http://su-gis.iptime.org/CyberGIS-Vis/videos/ACM_MLC.mp4"> Demo </a> 
			</li></ul> 	
		</li>
        <img height=200px src="http://su-gis.iptime.org/CyberGIS-Vis/images/ACM_MLC.PNG" alt="ACM_MLC"/>
		<li>Adaptive Choropleth Mapper with Comparison Linke Chart (CLC)
	        <ul><li> Click to see 
			 <a href="http://su-gis.iptime.org/CyberGIS-Vis/videos/ACM_CLC.mp4"> Demo </a> 
			</li></ul> 	
		</li>
        <img height=200px src="http://su-gis.iptime.org/CyberGIS-Vis/images/ACM_CLC.PNG" alt="ACM_CLC"/>
</ul>     
             
###  Categorical Data Visualization

<ul>
        <li>Qualitative_Analysis_Mapper</li>
        <img height=100px src="http://su-gis.iptime.org/CyberGIS-Vis/images/Qual.PNG" alt="Qual"/>
        <li>Qualitative_Analysis_Mapper with Stacked Chart</li>
        <ul><li> The Stacked Chart visualizes the temporal change of categorical data in a quantitative way.  <a href="http://su-gis.iptime.org/GEOSNAP/NAM_SD_1_neighborhood">Click to see demo.</a></li></ul>    
        <img height=100px src="http://su-gis.iptime.org/CyberGIS-Vis/images/Qual_Stacked.PNG" alt="Qual_Stacked"/>
        <li>Qualitative_Analysis_Mapper with Parallel Categories Diagram</li>
             <ul><li> Parallel Categories Diagram represents how the categorical data changes over time in quantity. <a href="http://su-gis.iptime.org/GEOSNAP/NAM_SD_3_sequence_neighborhood_categoriesDiagram">Click to see demo.</a></li></ul>    
      <img height=200px src="http://su-gis.iptime.org/CyberGIS-Vis/images/Qual_PCD.PNG" alt="Qual_PCD"/>
        <li>Qualitative_Analysis_Mapper with Chord Diagram</li>
        <ul><li> The Chord Diagram quantifies changes of categorical data between the two periods. <a href="http://su-gis.iptime.org/GEOSNAP/NAM_SD_4_sequence_neighborhood_chordDiagram">Click to see demo.</a></li></ul></li></ul> 
         <img height=200px src="http://su-gis.iptime.org/CyberGIS-Vis/images/Qual_CD.PNG" alt="Qual_CD"/> 
</ul> 

## Data
Visualizations created by CyberGIS-Vis are using a small subset of [LTDB](https://s4.ad.brown.edu/projects/diversity/researcher/LTDB.htm). [LTDB](https://s4.ad.brown.edu/projects/diversity/researcher/LTDB.htm) provides socioeconomic and demographic data with harmonized boundaries from 1970 to 2010 decennially. If you need the entire dataset, visit this [website](https://s4.ad.brown.edu/projects/diversity/researcher/LTDB.htm) to download.

## Related Resources
* [CyberGISX](https://cybergisxhub.cigi.illinois.edu/) 
* [Leaflet](https://leafletjs.com) 
* [PlotlyJS](https://plot.ly/javascript/) 
* [D3](https://d3js.org/) 
* [GEOSNAP VIZ](https://github.com/spatialucr/geosnap-viz) 

## Contributors

The lead developer of CyberGIS-Vis is Dr. Su Yeon Han at the [CyberGIS Center for Advanced Digital and Spatial Studies (CyberGIS Center)](https://cybergis.illinois.edu/) and the Principal Investigator of CyberGIS-Vis is Dr. Shaowen Wang at CyberGIS Center. This software repository is primarily maintained by [CyberGIS Center](https://cybergis.illinois.edu/). Please email any questions to [help@cybergis.org](mailto:help@cybergis.org).

## License

**This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/cybergis/CyberGIS-Vis/blob/master/LICENSE) file for details.**

## Funding

The CyberGIS-Vis project is supported by the CyberGIS Center for Advanced Digital and Spatial Studies at the University of Illinois at Urbana-Champaign.




