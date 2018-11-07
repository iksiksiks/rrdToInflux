# rrdToInflux.py, version 1.0
# November 7, 2018
# Written by Marino Bandi
# GNU GPLv3 license
#
#   Script used as wrapper to pass filenames (single or a group matching a defined pattern) to rrd2influxdb.jar [https://github.com/jhron/rrd2influxdb] written by https://github.com/jhron
#   This wrapper can speed up the process of conversion from (OpenHAB v.1) generated RRD files to InfluxDB compatible data files and import them with same name, for using in OpenHAB v.>2
#
#   Input argument can be a filename (without .rrd extension) or a pattern in the form of 'ROOT*' 
#       where ROOT will be the root that will be used to search for, example:
#           'Garden_*' will match all files starting with 'Garden_' and continuing with other chars for example: Garden_UV, Garden_IR, and so on
#
#   Script will start in 'read only' mode: in this mode will only enumerate files in the rrd source path (set below by 'folder_RRD' var) filtered by user input (first argument is mandatory)
#   Optional arguments:
#       '-h':   Help
#       '-c':   Set the commit flag to run process effectively converting files and writing to InfluxDB; a log file will be created in the same folder [migration.log]
#       '-v':   Set the verbose flag when passing '-c' flag, this will print all bash output to screen
#   
#   Process:
#       1)  Download and place rrd2influxdb.jar in the same directory as this script
#       2)  Configure InfluxDB server details (network address, socket, database name, database user and database password) - check 'USER OPTIONS' section
#       3)  Configure RRD path (path to folder with RRD files)
#       4)  python rrdToInflux.py [rrd] [flags]
#       
#
#   Thanks to https://github.com/jhron for his useful work
#
#

import sys, traceback, os, argparse, logging
from datetime              import datetime,date
from subprocess            import *


#################################################################################[ USER OPTIONS ]##############################################################################################

folder_RRD = "/tmp/rrd/" 
db_srv = 'localhost'
db_skt = '8086'
db_oh  = 'openhab_db'
db_usr = 'openhab'
db_psw = 'password'

#############################################################################[ END OF USER OPTIONS ]###########################################################################################

VERBOSE  = False
CHECK_ONLY = True

folderScript, fname = os.path.split(os.path.abspath(__file__))
folderScript = folderScript + "/"  

logging.basicConfig(
    filename=folderScript  + 'migration.log',
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger()

def	toErrLog(e):
    logging.error(traceback.format_exc())
    #print(traceback.format_exc())

def runCmd(cmd):
    try:
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
        output = p.communicate()[0]
        return output
    except Exception as e: 
        toErrLog(e)   
        print "Shell command error, exiting. Check log"          
        sys.exit()    
    
def multiImport(path,start,ext):
    list_dir = []
    try:
        list_dir = os.listdir(path)    
    except Exception as e: 
        toErrLog(e)   
        print "RRD Folder not found, check config. Exiting."          
        sys.exit()    
    cnt_enum = 0
    cnt_db = 0
    try:
        for file in list_dir:
                if file.endswith(ext): 
                    if file.startswith(start):
                        dest = str(file)[:-4]
                        cnt_enum += 1
                        if(not CHECK_ONLY): 
                            try:
                                output_src = runCmd("java -jar " + folderScript + "rrd2influxdb.jar -i " + folder_RRD + str(file) + " -o " + folderScript +  dest + ".txt")
                                if(VERBOSE): 
                                    print "rrd2influxdb.jar (export) output: "
                                    print output_src
                                try:
                                    output_dst = runCmd("curl -i -XPOST 'http://" + db_srv + ":"+ db_skt + "/write?db=" + db_oh + "&precision=s' -u " + db_usr + ":" + db_psw + " --data-binary @" + dest + ".txt")                
                                    if(VERBOSE):
                                        print "InfluxDB (import) output: "
                                        print output_dst
                                    print dest + " COMPLETED"
                                    logging.info('Converted from rrd4j and imported to InfluxDB: ' + str(dest))
                                    cnt_db += 1
                                    try:
                                        if(os.path.isfile(folderScript + dest + ".txt")):
                                            os.remove(folderScript + dest + ".txt")
                                    except Exception as e: 
                                        toErrLog(e)                                 
                                        print "Error removing txt file"                                    
                                except Exception as e: 
                                    toErrLog(e)  
                                    print "Error in data import, check log. Exiting"
                            except Exception as e: 
                                toErrLog(e)  
                                print "Error in data export, check log. Exiting"                        
                        else: 
                            print "[RRD] " + dest + " detected"

        return cnt_enum, cnt_db
    except Exception as e: 
        toErrLog(e)       
        sys.exit()


parser = argparse.ArgumentParser(description='Export all rrd files matching user input pattern and import data with same name into InfluxDB')
parser.add_argument('rrd4j', metavar='Source rrd', type=str, nargs='+',
                   help='RRD4j file or pattern matching filename*.rrd, without ANY extension')
parser.add_argument('-c','--commit', metavar='Commit', required=False, default=False, const=True, nargs='?',
                    help='Convert rrd files and import to InfluxDB')
parser.add_argument('-v','--verbose', metavar='Verbose', required=False, default=False, const=True, nargs='?',
                    help='Print bash output')

args, leftovers = parser.parse_known_args()
args = parser.parse_args()
source_rrd = args.rrd4j[0]

if args.commit:
    CHECK_ONLY = False
    
if args.verbose:
    VERBOSE = True

cnt_all, cnt_proc = multiImport(folder_RRD,source_rrd ,'.rrd')
if(CHECK_ONLY): print "***   CHECK FILE NAMES, READ ONLY MODE   ***"
if(cnt_all > 0) : print "Processed " + str(cnt_proc) + " / " + str(cnt_all) + " files, check log for details"  
else: print "ERROR: Check filename or pattern, no rrd file(s) found"
