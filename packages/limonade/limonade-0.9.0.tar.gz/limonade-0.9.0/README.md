# Limonade

Limonade is a library meant to simplify handling of list mode data from different sources. To make this possible a 
framework of data storage is defined. All details of the data are defined by configuration of the detector and the plot 
using configuration files written in json.

Once in Limonade format, the data can be retrieved and histogrammed using powerful selection tools in the plot module. 
With Limonade you can
- Select events by time interval
- Define extra data, such as coordinates or boolean flags
- Define gates for any data for any channel and define (anti)coincidence logic for them.
- Chain-load multiple data files
- Create 1d- and 2d-histograms of any data.

## Installation
Install with 

        pip install limonade

preferably using virtual environment or --user flag to prevent any clashes with permissions.

After installation one needs to set the configuration and data directories using commands

        set-limonade-config path/to/config-dir
        set-limonade-data path/data/dir

Now you need to make a detector. Next command creates a basic detector configuration with a dummy calibration and basic 
plots for each channel. The automatically generated configuration is very basic. You may want to modify it manually 
later.

        add-limonade-detector detname 2 g4

where 2 is the number of channels and standard is a type of data (name of loader) defined in 
limonade.loaders.loader_dict.