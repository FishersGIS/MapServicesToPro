## overwrite_map_services.py
## Created: 3/20/2023
## Created by: Melissa Brenneman
## Purpose: Overwrite non-cached map services on a Stand Alone
##          ArcGIS Server using ArcGIS Pro Projects
## Processes:
##  1. Start a log file
##  2. Get a list of running, non-cached, public map services from an ArcGIS REST services directory
##  3. For each service, pass it to a function that tries to overwrite the service
##      Note: The starting script has the lines passing the service to the overwrite function commented
##            so that you can test listing the services first, as overwriting should be done with caution.
##            When you are ready to overwrite services, you can uncomment those lines
##      a. overwrite function operations
##        -If it does not already exist, create a drafts folder to hold the .sddraft and .sd files
##        -If previous versions of the .sddraft and .sd files exist, delete them
##        -Reference the project and map to publish
##        -Create a service definition draft and write it to a .sddraft file
##        -Use XML to set properties for the .sddraft file
##        -Stage the Service (convert the .sddraft to an .sd file)
##        -Upload/Publish the Service
##  4. If the overwrite function is successful, continue to the next service, if not successful, stop the script
##
## Important:
##    Use this script with caution: It is intended to overwrite ArcGIS Map Services.
##    If variables are not set properly, you may accidentally overwrite services that
##    you did not intend to overwrite. Be very careful and use the settings in the code
##    to test it before running in any final environment. It is reccommended to make a
##    snapshot of your ArcGIS Server machine before running this script.
##
## Note: The author has no control over the script after it has been shared. If you are not
##    receiving this script from the Author, it may have been altered and the operations it
##    performs may have been changed. Many times, operations are altered by others without updating
##    the comments that describe the operation. Be sure to review the comments and operations
##    and make sure they are correct for your situation. 


# import libraries
import arcpy
import os
import sys
import datetime
import xml.dom.minidom as DOM
from arcgis.gis.server.catalog import ServicesDirectory

def main():
    try:
        # Locals
        # Get the path and parent folder for the script
        script_full_path = os.path.realpath(__file__)
        script_full_dir = os.path.dirname(script_full_path)

        # Modify any items below surrounded by brackets (<...>) to match your environment
        
        # The overwrite_service function is based on the following:
        #   -all pro project folders are in a single parent folder
        #   -each pro project folder name exactly matches the associated service name
        #   -each pro project contains a map whose name exactly matches the associated service name
        pro_project_parent_dir = r"<parent folder>" # example: D:\pro_projects
        
        # The out_draft_dir is a folder to store the .sddraft and .sd files that are part of the publishing
        # process. This folder does not need to be in any specific location in your environment and
        # can be deleted when the script finishes successfully
        out_draft_dir = os.path.join(script_full_dir, "<drafts folder>") # example: drafts
        
        # Set the target server connection to an arcgis server connection file
        target_server_connection = os.path.join(script_full_dir, "<server connection file>") # example: arcgis(admin).ags
        
        # Set a max_record_count property for all services
        max_record_count = "4000" # example: 4000

        # Inser the URL of your ArcGIS REST services directory below
        svc_directory = ServicesDirectory("<ArcGIS REST Services Directory>") # example: https://maps.fishers.in.us/arcgis/rest/services

        # The following counters help with testing and allow you to specify a range of services on which to run
        # the code. For example, when running for the first time, you might like to test it on just the first 5
        # services in the list of services. In that case, you would set the following:
        # start = 1
        # end = 6
        start = 1 # the service you would like to start
        end = 200 # the number of the service you would like to end before

        # Start a simple log file in the same folder as the script
        nowstart = datetime.datetime.now()
        time_stamp = nowstart.strftime("%Y_%m%d_%H%M")
        log_full_name = script_full_path[:-3] + "_log_" + time_stamp + ".txt"
        log_file = open(log_full_name, "w")      

        # Get running, non-cached, public map services from your REST services directory
        # To get the full list of running non-cached map services, use the following
        svc_names = [svc.url.split("/")[-2] for svc in svc_directory.list() if "MapServer" in svc.url and not '"singleFusedMapCache": true' in str(svc.properties)] #production

        # To test and run on a single specific service, uncomment the line below and insert the name of the service
##        svc_names = ["Addresses_Demo"] #example: Addresses

        # For each service, pass it to the overwrite_service function
        log_results(log_file, "Overwriting services...", True)
        counter = start
        for service_name in svc_names[start-1:end-1]:
            log_results(log_file, f"   {counter}-service_name: {service_name}", True)
            counter += 1
            # If the overwrite_service function is successful, continue to the next service, if not successful, stop the script
            # To test stepping through your services and writing their number and name, leave the following four lines commented
            # When you are ready to execute the overwrite, uncomment the following four lines
##            if overwrite_service(service_name, target_server_connection, pro_project_parent_dir, out_draft_dir, max_record_count, log_file): pass
##            else:
##                log_results(log_file, "      Script Terminated", True)
##                return

    except Exception as e:
        if type(e) is arcpy.ExecuteError:
            log_results(log_file, f"{arcpy.GetMessages(2)}", True)
        tb = sys.exc_info()[2]
        log_results(log_file, f"ERROR @ Line {tb.tb_lineno}", True)
        log_results(log_file, f"ERROR: {sys.exc_info()[1]}", True)

def overwrite_service(service, server_connection, input_dir, output_draft_dir, record_count, log_file):
    try:
        log_results(log_file, f"   {service}...", True)
        # Set output file names
        sddraft_output_filename = os.path.join(output_draft_dir, f"{service}.sddraft")
        sd_output_filename = os.path.join(output_draft_dir, f"{service}.sd")

        # Create output drafts folder if it does not exist
        if not os.path.exists(output_draft_dir):
            log_results(log_file, f"      Output Drafts folder did not exist", True)
            log_results(log_file, f"         Creating {output_draft_dir}...", True)
            os.makedirs(output_draft_dir)
        
        # Delete previous output files if they exist
        for s in (sddraft_output_filename, sd_output_filename):
            if os.path.exists(s):
                os.remove(s)

        # Reference map to publish
        log_results(log_file, "      Getting project and map...", True)
        aprx_name = service + ".aprx"
        aprx = arcpy.mp.ArcGISProject(os.path.join(input_dir, service, aprx_name))
        m = aprx.listMaps(service)[0]

        # Create MapServiceDraft, set overwrite property, set metadata
        log_results(log_file, "      Creating sddraft and setting metadata...", True)
        sddraft = arcpy.sharing.CreateSharingDraft("STANDALONE_SERVER", "MAP_SERVICE", service, m)
        sddraft.targetServer = server_connection
        sddraft.overwriteExistingService = True

        # Create Service Definition Draft file
        sddraft.exportToSDDraft(sddraft_output_filename)

        # parse XML and change properties to use the shared instance and set the Max Records Returned
        xml = sddraft_output_filename
        doc = DOM.parse(xml)
        def_childnodes = doc.getElementsByTagName("Definition")[0].childNodes
        log_results(log_file, "      Changing service properties...", True)
        for def_node in def_childnodes:
            # Change provider to shared instance
            if def_node.nodeName == "Props":
                for node in def_node.childNodes[0].childNodes:
                    # Change the provider to modify instance type
                    # provider="DMaps" for shared or "ArcObjects11" for dedicated
                    if node.firstChild.firstChild.data == "provider":
                        log_results(log_file, "         Setting Provider to shared instance...", True)
                        node.lastChild.firstChild.data = "DMaps"
            # Change the maxRecordCount
            if def_node.nodeName == "ConfigurationProperties":
                for node in def_node.childNodes[0].childNodes:
                    if node.firstChild.firstChild.data == "maxRecordCount":
                        log_results(log_file, f"         Setting MaxRecordCount to {record_count}", True)
                        node.lastChild.firstChild.data = record_count
                        
                        
        # Write to the .sddraft file
        log_results(log_file, "      Writing sddraft...", True)
        f = open(sddraft_output_filename, "w")
        doc.writexml(f)
        f.close()

        # Stage Service
        log_results(log_file, "      Staging...", True)
        arcpy.server.StageService(sddraft_output_filename, sd_output_filename)
        
        # Publish to server
        log_results(log_file, "      Uploading...", True)
        arcpy.server.UploadServiceDefinition(sd_output_filename, server_connection)
    
        log_results(log_file, "      Finished Publishing", True)
        return True
    
    except Exception as e:
        if type(e) is arcpy.ExecuteError:
            log_results(log_file, f"      {arcpy.GetMessages(2)}", True)
        tb = sys.exc_info()[2]
        log_results(log_file, f"      ERROR @ Line {tb.tb_lineno}", True)
        log_results(log_file, f"      ERROR: {sys.exc_info()[1]}", True)
        return False
        
def log_results(file, message, echo=False):
    if echo: print(message)
    file.write(f"{message}\n")
    file.flush()
    return

if __name__ == "__main__":
    main()
