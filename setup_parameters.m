% Setup_parameters for ambient noise processing
%
% NJA, 4/2/2016
% JBR, 6/16/2016

addpath('./functions/');
addpath('./functions/calc_Rayleigh_disp/');

%%% --- Paths to important files --- %%%
parameters.workingdir = [pwd,'/'];

parameters.datapath = ['/Users/noah/AACES_Data_09_10_2018/XO_Test/']; %'../nomelt_data_5sta/';

parameters.PZpath = '../Users/noah/AACES_Data_09_10_2018/Instrument_TEST/'; % path to RESP files containing poles and zeros
parameters.ccfpath = './Users/noah/AACES_Data_09_10_2018/ccf_TEST/';
parameters.figpath = [parameters.workingdir,'figs/'];
parameters.seis_path = [parameters.workingdir,'seismograms/'];
parameters.orientation_path = './OBS_orientations.txt'; % Column 1: station name;   Column 2: H1 degrees CW from N
[stalist, stalat, stalon, staz] = textread(['stalist_good12.txt'],'%s %f %f %f\n');
parameters.stalist = stalist;
parameters.stalat = stalat;
parameters.stalon = stalon;
parameters.staz = staz;
parameters.nsta = length(parameters.stalist);

%%% --- Parameters to build up gaussian filters --- %%%
parameters.min_width = 0.18;
parameters.max_width = 0.30;

%%% --- Parameters for initial processing --- %%%
parameters.dt = 50; % sample rate
parameters.comp = 'HH'; % component
parameters.mindist = 1; % min. distance in kilometers

%%% --- Parameters for ccf_ambnoise --- %%%
parameters.winlength = 3; %hours
parameters.Nstart_sec = 50; % number of sections to offset start of seismogram

%%% --- Parameters for fitbessel --- %%%
parameters.npts = parameters.winlength*3600 / parameters.dt;

%%% --- Parameters for using Radon Transform picks --- %%%
parameters.path_LRT_picks = './mat-LRTdisp/LRT_picks/';
