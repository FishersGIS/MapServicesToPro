# Map Services To Pro

3-part process to prepare non-cached map services for publishing workflows in ArcGIS Enterprise 11.1 and later  
- Converts ArcMap documents to ArcGIS Pro projects
- Optional metadata update/standardization feature
- Overwrite services using ArcGIS Pro

### Set Up:  
1. Modify scripts with necessary URLs, paths, and values (commented lines within the scripts provide additional instruction).
2. Create a Template ArcGIS Pro Project *without a map* in the parent folder. This should ultimately be a folder named "Template" with a file named "Template.aprx" within it.
3. Optionally, prepare a CSV file containing metadata. Fields should include (in order): the service name, the service summary, the service description, and the service tags. Credit metadata is applied universally in the code based on the value entered during script modification. A [template CSV file](Metadata.csv) is provided as a formatting guide. By default, the metadata update functions are turned off in MXD-TO-APRX.py. As part of the first set up step, be sure to change the metadata variable value to **TRUE**, if desired.

## **Part 1:** MXD TO APRX  
Convert map documents to ArcGIS Pro Projects to prepare for publishing workflows in ArcGIS Enterprise 11.1 and later with [MXD-TO-APRX.py](MXD-TO-APRX.py)  

### Command Line Arguments  
#### Run Modes (Inclusion is required)  
- Production Mode  
  - Ex: `path\to\MXD-TO-APRX.py p`  
- Debug Mode  
  - Ex: `path\to\MXD-TO-APRX.py d`  
***Note: Debug mode does not contain unique functionality. Instead, it enables more convenient interaction with two separate environments for testing purposes. Use accordingly.***

#### Service Specifications (Inclusion is optional, all services are included by default)  
- Single Service Name  
   - Ex: `path\to\MXD-TO-APRX.py p ServiceName`  
- List of Service Names  
  - Ex: `path\to\MXD-TO-APRX.py p ServiceName,Service_Name,servicename`  
- To or From/To according to alphabetical order of REST Services Directory  
  - Ex: `path\to\MXD-TO-APRX.py p 10`  
  - Ex: `path\to\MXD-TO-APRX.py p 1,10`  
***Note: If entering one or more service names, entries are case-sensitive and spaces should not be included.***  

#### Process overview:  
1. Accesses REST Service Directory to obtain a list of published services
2. Iterates through map documents in a specified location and identifies matches to published service names
3. For each match...
  1. Copies the contents of the template project folder to a new folder named the same as the service
  2. Imports the map document as a map into the copied template APRX file, names the same as the service
  3. Applies metadata from the CSV to the map, if applicable
  4. Copies template APRX file to a new APRX file named the same as the service
  5. Deletes the copied template APRX file

## **Part 2:** Manual APRX Configuration  
For each newly created ArcGIS Pro Project...
1. Open the APRX file in ArcGIS Pro
2. From the Contents Pane-Project tab, expand the Maps section, then right-click the map and select "Open"
3. From Map Properties-General, check the box for "**Allow assignment of unique numeric IDs for sharing web layers**"
4. Save and close the project

## **Part 3:** Publish Like a Pro!  
Overwrite non-cached map services on a Stand Alone ArcGIS Server using ArcGIS Pro Projects with [overwrite_map_services.py](overwrite_map_services.py)  
