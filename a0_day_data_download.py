# %%
# Load the necessary libraries
import os
import obspy
from obspy.clients.fdsn import Client
from obspy import UTCDateTime  
from obspy.core import AttribDict
from obspy.io.sac import SACTrace
from obspy.geodetics import gps2dist_azimuth, locations2degrees
import numpy as np
import pandas as pd
from io import StringIO
from datetime import datetime
import calendar
import urllib
import requests
from setup_parameter_py import *

# %% DIRECTORY SETUP
input_directory = f"{PROJECTdir}/{PROJECTname}/"
output_directory = f"{PROJECTdir}/{PROJECTname}/{SACdaydir}/"
os.makedirs(output_directory, exist_ok=True)  # Create directory if it doesn't exist

# LOAD CLIENT
client = Client(webservice)
print(client)

# LOAD STATIONS AND DAYS
stations_dict = {}
days_dict = {}

# Read station files for each network
for network in networks:
    file_path = os.path.join(input_directory, f"{network}_{stasuff}.txt")
    with open(file_path, 'r') as file:
        stations = file.read().splitlines()
        stations_dict[network] = stations

    # Read day file
    day_file_path = os.path.join(input_directory, f"{network}_{daysuff}.txt")
    with open(day_file_path, 'r') as file:
        days = file.read().splitlines()
        days_dict[network] = [UTCDateTime(day) for day in days]

# RETRIEVE OBSIC ORIENTATIONS FOR ALL NETWORKS/STATIONS
orientation_dict = {}  # Will store {(network, station): {'orientation': value, 'error': value}}

for network in networks:
    url = f"https://obsic-metrics.whoi.edu/{network}/csv"
    try:
        urlresponse = requests.get(url, timeout=10)
        if urlresponse.status_code == 200:
            df = pd.read_csv(StringIO(urlresponse.text))
            for station in stations_dict[network]:
                station_row = df[df['Station'] == station]
                if not station_row.empty:
                    orientation = station_row['Orientation, degrees'].values[0]
                    error = station_row['Error, degrees'].values[0]
                    # Replace '--' with 999
                    if orientation == '--':
                        print(f"No orientation for station {network}.{station}.")
                        orientation = 999
                        error = 999
                    else:
                        orientation = float(orientation)
                        error = float(error)
                    orientation_dict[(network, station)] = {'orientation': orientation, 'error': error}
                else:
                    print(f"Station {network}.{station} not found in orientation table.")
                    orientation_dict[(network, station)] = {'orientation': 999, 'error': 999}
        else:
            print(f"Failed to retrieve orientation file for network {network}. Status code: {urlresponse.status_code}")
            # Set default values for all stations in this network
            for station in stations_dict[network]:
                orientation_dict[(network, station)] = {'orientation': 999, 'error': 999}
    except requests.exceptions.RequestException as e:
        print(f"Connection error retrieving orientations for network {network}: {e}")
        # Set default values for all stations in this network
        for station in stations_dict[network]:
            orientation_dict[(network, station)] = {'orientation': 999, 'error': 999}

# Loop over each network, station, and day to download data
for network, stations in stations_dict.items():
    print(f"Downloading data for network {network}")
    for day in days_dict[network]:
        print(f"Downloading data for day {day}")
        tbeg = day
        tend = tbeg + trlen 
        # Set up folder structure for saving SAC files
        date = datetime.strptime(str(tbeg),'%Y-%m-%dT%H:%M:%S.%fZ')
        dayname = date.strftime('%Y%m%d%H%M')
        daydir = output_directory + dayname + '/'
        if not os.path.exists(daydir):
            os.makedirs(daydir)

        for station in stations:
            print(f"Downloading data for station {station}")

            # Get orientation from pre-loaded dictionary
            orientation = orientation_dict[(network, station)]['orientation']
            error = orientation_dict[(network, station)]['error']

            for icomp, comp in enumerate(comps):
                sac_out = daydir + dayname + '.' + network + '.' + station + '.' + comp + '.sac'
                # Check if the file already exists and skip if overwrite is disabled
                if not isoverwrite and os.path.exists(sac_out):
                    print(f"File {sac_out} already exists. Skipping download.")
                    continue

                # Query OBSIC Database for good and bad days of data
                if OBSIC_metrics == 1:
                    # Try different channel prefixes if the original fails
                    comp_variants = [comp]
                    if comp.startswith('L'):
                        comp_variants.extend([f'H{comp[1:]}', f'B{comp[1:]}'])
                    
                    urlresponse = None
                    for comp_variant in comp_variants:
                        url = f"https://obsic-metrics.whoi.edu/static/images/quality/{network}/{station}_{comp_variant}.txt"
                        try:
                            urlresponse = requests.get(url, timeout=10)
                            if urlresponse.status_code == 200:
                                print(f"Successfully retrieved OBSIC metrics using channel {comp_variant}")
                                break
                        except requests.exceptions.RequestException as e:
                            print(f"Connection error for {comp_variant}: {e}")
                            continue
                    
                    if urlresponse and urlresponse.status_code == 200:
                        lines = urlresponse.text.splitlines()  # Read lines from the response text
                        good_hours = 0  # Counter for good hours
                        date_found = False  # Flag to check if date is found
                        for line in lines[2:]:  # Skip the first two header lines
                            date, quality = line.split(",")
                            if date == tbeg.strftime("%Y-%m-%d"):
                                good_hours = quality.count('1')
                                date_found = True
                                break
                        if not date_found:
                            print(f"Skipping {tbeg.strftime('%Y-%m-%d')} for station {station}:{comp} as date is not present in the response file")
                            continue
                        if good_hours < good_hours_threshold: # Require all good hours in a day for download
                            print(f"Skipping {tbeg.strftime('%Y-%m-%d')} for station {station}:{comp} due to insufficient good data hours ({good_hours} hours)")
                            continue
                    else:
                        print(f"Failed to retrieve OBSIC metrics for all channel variants. Proceeding without quality check.")

                # Get station metadata
                try:
                    sta_inventory = client.get_stations(network=network, station=station, location="*", channel=comp, starttime=tbeg, endtime=tend, level="response")
                except:
                    print(f"Missing station: {station}")
                    continue
                stel = sta_inventory.networks[0].stations[0].elevation
                stla = sta_inventory.networks[0].stations[0].latitude
                stlo = sta_inventory.networks[0].stations[0].longitude
                stazimuth = sta_inventory.networks[0].stations[0].channels[0].azimuth
                stadip = sta_inventory.networks[0].stations[0].channels[0].dip
                sensor = sta_inventory.networks[0].stations[0].channels[0].sensor.description
                sta_deploy = sta_inventory.networks[0].stations[0].start_date
                sta_recover = sta_inventory.networks[0].stations[0].end_date
                if sta_recover is None:
                    sta_recover = UTCDateTime("2599-12-31")

                # Download waveform data
                try:
                    st = client.get_waveforms(network=network, station=station, location="*", channel=comp, starttime=tbeg, endtime=tend, attach_response=True)
                except:
                    print(f"Missing data for station: {station}")
                    continue
                if len(st) > 1:  # Check for data gaps and fill with 0's
                    try:
                        st.merge(method=1, fill_value=0)
                    except:
                        print(f"Skipping... issue merging data across gaps: {station} {tbeg}") 
                        continue
                sr = st[0].stats.sampling_rate
                if is_removeresp:
                    try:
                        # Check whether pressure channel, if so use "VEL" option which doesn't add or remove zeros
                        if st[0].stats.response.instrument_sensitivity.input_units.upper() == 'PA':
                            st.remove_response(output='VEL', zero_mean=True, taper=True, taper_fraction=0.05, pre_filt=[0.001, 0.0025, sr/3, sr/2], water_level=600)
                            units = 'PA'
                        else:
                            st.remove_response(output=outunits, zero_mean=True, taper=True, taper_fraction=0.05, pre_filt=[0.001, 0.0025, sr/3, sr/2], water_level=600)
                            units = outunits
                    except:
                        print(f'Skipping... issue removing response: {station} {tbeg}')
                        continue
                else:
                    units = 'RAW'
                st.trim(starttime=tbeg, endtime=tend, pad=True, nearest_sample=False, fill_value=0)  # make sure correct length
                st.detrend(type='demean')
                st.detrend(type='linear')
                st.taper(type="cosine", max_percentage=0.05)
                if is_downsamp == 1:
                    st.filter('lowpass', freq=0.4 * sr_new, zerophase=True)  # anti-alias filter
                    st.resample(sampling_rate=sr_new)
                    st.detrend(type='demean')
                    st.detrend(type='linear')
                    st.taper(type="cosine", max_percentage=0.05)

                # convert to SAC and fill out station/event header info
                sac = SACTrace.from_obspy_trace(st[0])
                sac.stel = stel
                sac.stla = stla
                sac.stlo = stlo
                sac.cmpaz = stazimuth
                sac.cmpinc = stadip+90 # stadip SEED convention, cmpinc is SAC convention
                sac.kuser0 = units
                sac.kuser1 = sta_deploy.strftime('%Y%m%d')  # Convert to string in YYYYMMDD format
                sac.kuser2 = sta_recover.strftime('%Y%m%d')  # Convert to string in YYYYMMDD format
                sac.kinst = sensor # NOTE: SAC kinst is only 8 characters long, may be truncated, this routinely is truncated
                sac.user0 = orientation # add the OBSIC horizontal orientation to SAC header
                sac.user1 = error

                sac.write(sac_out)