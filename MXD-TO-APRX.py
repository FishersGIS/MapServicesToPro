## MXD-TO-APRX.py
## Created: 2023
## Created by: Brandon Katz
## Purpose: Convert map documents to ArcGIS Pro Projects to prepare for new publishing workflows in ArcGIS Enterprise 11.1 and later
## Setup:
##    1. Replace paths, URLs, and values in lines 155-156.
##    2. Prepare a template ArcGIS Pro Project named 'Template' without a map within it. The result should be a file named 'Template.aprx' within a folder named 'Template'.
##    3. If utilizing the metadata features in a run, prepare a CSV file including desired information. Fields should include Title, Summary, Description, and Tags.

import os, sys, shutil, glob, csv, atexit
from arcpy import mp
from arcpy import metadata as md
from arcgis.gis.server.catalog import ServicesDirectory

def log_error(error,e):

    tb = sys.exc_info()[2]
    log_output["ERRORS"].append(" ".join([error,f"ERROR @ LINE: {tb.tb_lineno}",f"ERROR DETAILS: {e}"]))

    return

def aprx_cleanup(aprx_delete):
    
    """Removes copied Template.aprx files from newly created ArcGIS Pro Projects if failed during normal processing. Included due to differences in file locking behavior from ArcGIS Pro 3.1.0 to 3.1.1"""

    for aprx in aprx_delete:
        os.remove(aprx)

def get_services():
    
    """Accesses REST Services Directory via URL to obtain a list of all published services, then filters out any that are not non-cached map services."""

    try:
        print("\tAccessing services directory...")
        services_directory = ServicesDirectory(mode["rest_url"])
        services = [service.url.split('/')[-2] for service in services_directory.list() if "MapServer" in service.url and not '"singleFusedMapCache": true' in str(service.properties)]
        print(f"\t\t{len(services)} services received.")
    except Exception as e:
        error = "ERROR: Could not access services directory."
        log_error(error, e)
        print("\t\tERROR: Could not access services directory. Program will terminate.")
        exit()

    return services

def check_args(services):

    """Checks for and applies secondary and tertiary input arguments"""

    if len(sys.argv) > 2:
        if not sys.argv[2].isnumeric():
            input_args = sys.argv[2].split(",")
            service_names = [service for service in input_args if service in services]
            unmatched = [service for service in input_args if not service in services]
            print(f"\tNumber of input values matched to published service names: {len(service_names)}")
            if len(unmatched) > 0:
                log_output["ERRORS"].append(" ".join(["ERROR: One or more input values did not match a published service name.", f"Number of unmatched input values: {len(unmatched)}", f"Unmatched input values: {unmatched}"]))
                print(f"\tNumber of input values not matched to published service names: {len(unmatched)}\n\t\tView MXD-TO-APRX_output.txt for details on unmatched input values.")
        else:
            if len(sys.argv) > 3:
                start = sys.argv[2]
                end = sys.argv[3]
            else:
                start = 0
                end = sys.argv[2]
            service_names = services[int(start):int(end)]
        print(f"\tThis run will include the following: {new_line}\t\t{', '.join(service_names)}")
    else:
        service_names = services

    return service_names

def mxd_to_aprx(mode, service, error_hold):

    """Copies the contents of the Template ArcGIS Pro Project folder to a new folder named the same as the service. Imports the old map document to the copied Template.aprx file, saves the imported map as the same name as the service, then copies the file again to a new file named the same as the service. Removes the copied Template.aprx file that is no longer needed."""

    def get_metadata(service):
        
        """Searches CSV for metadata relevant to the service. Uses the service name as metadata if no results are found."""

        print(f"\t\t\tGetting metadata for {service}...")
        md_csv = list(csv.reader(open("Metadata.csv", "r"), delimiter=","))
        service_md = [i for i in md_csv if service.lower() == str(i[0]).strip(" ").lower()]
        if len(service_md) > 0:
            if type(service_md[0]) == list:
                service_md = service_md[0]
                print("\t\t\t\tMetadata found.")
        else:
            service_md = [service, service, service, service]
            error_hold.append(f"ERROR: Could not locate metadata for {service}")
            print(f"\t\t\t\tNo metadata found.")

        return service_md

    def set_metadata(service,map,map_md):

        """Applies metadata to map."""

        try:
            print(f"\t\t\tSetting metadata for {service}...")
            metadata = md.Metadata()
            metadata.title = map_md[0]
            metadata.summary = map_md[1]
            metadata.description = map_md[2]
            metadata.tags = map_md[3]
            metadata.credits = mode["credits"]
            map_md = map.metadata
            if not map_md.isReadOnly:
                map_md.copy(metadata)
                map_md.save()
                print("\t\t\t\tMetadata set.")    
            else:
                error_hold.append(f"Error setting metadata for {service}")
                print(f"\t\t\t\tError setting metadata for {service}")
        except Exception as e:
            error = f"ERROR: {service}"
            log_error(error, e)
            print(f"\t\t\t\tError setting metadata for {service}")

        return        
    
    try:
        service_folder = os.path.join(mode["parent_folder"], service)
        copy_aprx = os.path.join(service_folder, mode["template_aprx"])
        service_aprx = os.path.join(service_folder, service + ".aprx")
        mxd_path = mode["parent_folder"] + service + ".mxd"
        shutil.copytree(mode["template_folder"], service_folder) # Copies the template ArcGIS Pro Project folder contents to new folder with a name similar to the service
        aprx = mp.ArcGISProject(copy_aprx)
        aprx.importDocument(mxd_path) # Imports map document file (MXD) into ArcGIS Pro Project file (APRX)
        map = aprx.listMaps()[0]
        map.name = service # Sets the map name similar to the service
        if mode["metadata"] is True:
            map_md = get_metadata(service)
            set_metadata(service,map,map_md)
        aprx.saveACopy(service_aprx) # Copies the copied template APRX file to an APRX file with a name similar to the service
        del aprx
        try:
            os.remove(copy_aprx) # Delete copied template APRX file
        except Exception as e:
            error = f"ERROR: Cannot delete {os.path.join(mode['template_folder'], mode['template_aprx'])}. Will attempt again at program completion. Check service folder for verification of removal."
            log_error(error,e)
            aprx_trash.append(copy_aprx)
    except Exception as e:
        error = f"ERROR: {service}"
        log_error(error, e)
        print(f"\t\t\tERROR: {service}")

    return

if __name__ == "__main__":

    # Initialization
    
    print("\n\nStarting process...\n")
    production = {"rest_url":"<URL>", "parent_folder": "<C:\\PATH\\TO\\FOLDER\\>","output_log_folder": "<C:\\PATH\\TO\\FOLDER\\>", "template_folder": "<C:\\PATH\\TO\\FOLDER\\>", "template_aprx": "Template.aprx", "credits": "<VALUE>", "metadata": False}
    debug = {"rest_url":"<URL>", "parent_folder": "<C:\\PATH\\TO\\FOLDER\\>", "output_log_folder": "<C:\\PATH\\TO\\FOLDER\\>", "template_folder": "<C:\\PATH\\TO\\FOLDER\\>", "template_aprx": "Template.aprx", "credits": "<VALUE>", "metadata": False}
    log_output = {"COMPLETED":[],"SKIPPED":[],"ERRORS":[]}
    new_line = '\n'
    aprx_trash = []
    if len(sys.argv) > 1 and sys.argv[1] == "p":
        mode = production
    elif len(sys.argv) > 1 and sys.argv[1] == "d":
        mode = debug
    else:
        print("\nSpecify p (for production) or d (for debug) as the first argument, followed by optional specification arguments.\n")
        print("<path-to-file> p\n\tRuns in production mode\n\n<path-to-file> d\n\tRuns in debug/test mode\n\n<path-to-file> p 10\n\tRuns in production mode, gets first 10 services\n\tNo range checking implemented\n\n<path-to-file> d 2 15\n\tRuns in debug mode, gets services 2-14\n\tNo range checking implemented\n\n<path-to-file> p ServiceName\n\tRuns in production mode, gets one specified service\n\tCase-sensitive\n\n<path-to-file> d ServiceName,Service_Name,servicename\n\tRuns in debug mode, gets multiple specified services\n\tCase-sensitive\n\tMust be separated by commas (no space after)\n")
        exit()

    # Processing

    services = get_services()
    service_names = check_args(services)
    print("\tAttempting conversions from MXD to APRX...")
    os.chdir(mode["parent_folder"]) 
    service_mxds = [mxd[:-4] for mxd in glob.glob("*.mxd")]
    for service in service_names:
        error_hold = []
        if service in service_mxds:
            try:
                print(f"\t\tStarting {service} conversion...")
                mxd_to_aprx(mode, service, error_hold)
                if len(error_hold) > 0:
                    log_output["ERRORS"].append(" ".join([f"{service} errors:", f"{new_line.join(error_hold)}"]))
                log_output["COMPLETED"].append(f"{service}")
                print(f"\t\t\t{service} conversion complete.")
            except Exception as e:
                error = f"ERROR: {service}"
                log_output["SKIPPED"].append(service)
                log_error(error, e)
                print(f"\t\t{service} encountered an error.")
        else:
            error = f"ERROR: {service} was skipped because no matching mxd file was found"
            log_output["SKIPPED"].append(service)
            log_output["ERRORS"].append(error)
            print(f"\t\tNo MXD found for {service}... Skipped.")
    
    # Post-Processing

    atexit.register(aprx_cleanup,aprx_trash)
    if len(log_output) < 1:
        print("\nProcess completed without errors.\n\n")
    else:
        error_count = len(log_output["ERRORS"])
        os.chdir(mode["log_output_folder"])
        with open("MXD-TO-APRX_output.txt", 'w') as output:
            for key, value in log_output.items():
                output.write(f"{key}:{new_line}{new_line.join(value)}{new_line}{new_line}")
        print(f"\nProcess completed with {error_count} error(s)...\n\tView MXD-TO-APRX_output.txt for error details.\n\n")