## setup_parameter_py.py
# Set up parameters for downloading and processing seismic data
# Ensure all files and directories are consistent with matlab setup parameters

webservice = "IRIS" # Web service to use for data download

# DIRECTORIES AND FOLDERS
PROJECTdir = "./"
PROJECTname = "ExampleProject" # This is name of folder where all data will be saved
# Folders in Project Directory
SACdaydir = 'SAC_days' # where downloaded daily SAC files will be saved
SACevtdir = 'SAC_evts' # where downloaded event SAC files will be saved

# NETWORKS, DAYS, STATIONS
networks = ["7D", "ZA"] # list of networks
# station, day, and event file suffixes - these files should already exist in the PROJECTname folder before running
stasuff = 'stations' # suffix designator for station list file (should be [NETWORK]_stasuff.txt)
daysuff = 'days' # suffix designator for day list file, created ahead of running

# DOWNLOAD PARAMETERS
isoverwrite = 0 # Overwrite existing files?
trlen = 86400 # Length of daily time series (sec)
T = 7200 # Length of times series for correction (sec)
#comps = ["HHZ", "HH1", "HH2", "HDH"] # Components to download WARNING! List the full channel names. Do not use wildcards. Bad things will happen...
#comps = ["LHZ", "LH1", "LH2", "LDH"] # Components to download WARNING! List the full channel names. Do not use wildcards. Bad things will happen...
#comps = ["BHZ", "BH1", "BH2", "BDH"] # Components to download WARNING! List the full channel names. Do not use wildcards. Bad things will happen...
comps = ["HHZ", "HH1", "HH2", "HDH", "BHZ", "BH1", "BH2", "BDH"] # Components to download WARNING! List the full channel names. Do not use wildcards. Bad things will happen...

# PROCESSING PARAMETERS  
is_downsamp = 1 # Downsample? 1 for yes, 0 for no
sr_new = 5 # Downsample Hz (samples/sec), use original if no downsampling
is_removeresp = 1 # Remove response? 1 for yes, 0 for no
outunits = 'DISP' # Response removal output units; DISP, VEL, ACC for seismograms

# OBSIC METRICS QC
OBSIC_metrics = 1 # Query OBSIC metrics for good and bad days of data? Applies to daily download only
good_hours_threshold = 15 # Threshold for good hours of data (0-24) to consider a day as good

# DOWNLOAD EVENT PARAMETERS
min_mag = 6.0 # Minimum magnitude for events to download
max_mag = 10.0 # Maximum magnitude for events to download
cenlat = 57 # Latitude of center point for event search (degrees) 
cenlon = -153 # Longitude of center point for event search (degrees)
min_dist = 0.0 # Minimum distance from station to event (degrees)
max_dist = 180.0 # Maximum distance from station to event (degrees)
evt_starttime = "2015-03-01T00:00:00" # Start time for event search (UTC)
evt_endtime = "2015-03-30T00:00:00" # End time for event search (UTC)
evtsuff = 'events' # suffix designator for event list file, populated by event download script
OBSIC_metrics_evt = 1 # Query OBSIC metrics for good and bad data segments? If bad overlaps with event window, will skip