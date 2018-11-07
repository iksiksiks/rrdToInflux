# rrdToInflux
## Script to convert rrd4j db files (from OpenHAB v.1) to Influx db (OpenHAB >v.2)

  Script used as wrapper to pass filenames (single or a group matching a defined pattern) to rrd2influxdb.jar [https://github.com/jhron/rrd2influxdb] written by https://github.com/jhron
  This wrapper can speed up the process of conversion from (OpenHAB v.1) generated RRD files to InfluxDB compatible data files and import them with same name, for using in OpenHAB v.>2

  Input argument can be a filename (without .rrd extension) or a pattern in the form of 'ROOT*' 
      where ROOT will be the root that will be used to search for, example:
          'Garden_*' will match all files starting with 'Garden_' and continuing with other chars for example: Garden_UV, Garden_IR, and so on

  Script will start in 'read only' mode: in this mode will only enumerate files in the rrd source path (set by 'folder_RRD' var) filtered by user input (first argument is mandatory)
 ###### Optional arguments:
      '-h':   Help
      '-c':   Set the commit flag to run process effectively converting files and writing to InfluxDB; a log file will be created in the same folder [migration.log]
      '-v':   Set the verbose flag when passing '-c' flag, this will print all bash output to screen
 
 ###### Process:
      1)  Download and place rrd2influxdb.jar in the same directory as this script
      2)  Configure InfluxDB server details - check 'USER OPTIONS' section
      3)  Configure RRD path (path to folder with RRD files)
      4)  python rrdToInflux.py [rrd] [flags]
      

  Thanks to https://github.com/jhron for his useful work
