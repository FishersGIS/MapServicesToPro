# Map Services To Pro

## 3-part process to prepare non-cached map services for ArcGIS Enterprise 11.1 and later  
- Converts ArcMap documents to ArcGIS Pro projects
- Optional metadata update/standardization feature
- Overwrite services using ArcGIS Pro

#### Set Up:  
1. Modify scripts with necessary URLs, paths, and values. Commented lines within the scripts provide additional instruction.
2. Create a Template ArcGIS Pro Project *without a map* in the parent folder. This should ultimately be a folder named "Template" with a file named "Template.aprx" within it.
3. Optionally, prepare a CSV file containing metadata. Fields should include (in order): the service name, the service summary, the service description, and the service tags. Credit metadata is applied universally in the code based on the value entered during script modification. By default, the metadata update functions are turned off in MXD-TO-APRX.py. As part of the first set up step, be sure to change the metadata variable value to 'TRUE', if desired.

### **Part 1:** MXD TO APRX  
Convert map documents to ArcGIS Pro Projects to prepare for new publishing workflows in ArcGIS Enterprise 11.1
Command Line Arguments
Process overview

### **Part 2:** Manual APRX Configuration  
For each newly created ArcGIS Pro Project...
1. Open the APRX file in ArcGIS Pro
2. From the Contents Pane-Project tab, expand the Maps section, then right-click the map and select "Open"
3. From Map Properties-General, check the box for "**Allow assignment of unique numeric IDs for sharing web layers**"
4. Save and close the project

### **Part 3:** Publish Like a Pro!  


