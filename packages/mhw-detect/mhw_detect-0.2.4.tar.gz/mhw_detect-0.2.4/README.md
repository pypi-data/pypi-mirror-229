# MHW Detector

Marine heatwaves detector based on https://github.com/ecjoliver/marineHeatWaves.

This package integrates a numba optimised version of ecjoliver's implementation for MHW detection with multiprocessing capabilities to compute detection over every coordinates of the dataset.

This code is not only for detecting MHW. It can also be used to detect extrem events of any variables like chla, pH, O2, etc ...

## Installation
> pip install mhw-detect


### Dependencies
- xarray
- numba
- scipy
- dask
- numpy
- pandas
- netcdf4
- click
- pyarrow

## Usage
### Configuration file
With mhw-detect no need for kilometers of parameters in command line. You just need to write a configuration file in which you put every parameters like an identity card of your next detection.

```yaml
data:
  data :
    path : '/folder/sst.nc'
    var : 'sst'
  clim :
    path : '/folder_clim/clim.nc'
    var : 'sst'
  percent :
    path : '/folder_percent/percentile.nc'
    var : 'sst'
  # Optionnal
  offset :
    path : '/folder_offset/offset.nc'
    var : 'sst'

params:
    depth : 0
    climatologyPeriod : [null, null] # ex: [1983, 2012]
    pctile : 90
    windowHalfWidth : 5
    smoothPercentile : True
    smoothPercentileWidth : 31
    minDuration : 5
    joinAcrossGaps : True
    maxGap : 2
    maxPadLength: False
    coldSpells : False
    Ly : False

cut:
  nb_lat : 157
  nb_lon : 72

output_detection : '/my/path/to/folder_result/'
```

- `data` : specifies the paths and variables you want to use. Do not specify clim and percent if you want them to be computed during the detection. Offset is an optionnal parameter as a 2D dataset to add an offset to the percentile.
- `params` : specifies the parameters of the detection. See section below.
- `cut` : specifies the number of latitude and longitude for geospatial dataset cutting.
- `output_detection` : specifies the folder in which to save the results.


### Detection parameters
From https://github.com/ecjoliver/marineHeatWaves.

```
climatologyPeriod      Period over which climatology is calculated, specified
                        as list of start and end years. Default ([null, null]) is to calculate
                        over the full range of years in the supplied time series.
                        Alternate periods suppled as a list e.g. [1983,2012].
                        Unused if precalculated clim and percentile are set.

pctile                 Threshold percentile (%) for detection of extreme values
                        (DEFAULT = 90)

windowHalfWidth        Width of window (one sided) about day-of-year used for
                        the pooling of values and calculation of threshold percentile
                        (DEFAULT = 5 [days])

smoothPercentile       Boolean switch indicating whether to smooth the threshold
                        percentile timeseries with a moving average (DEFAULT = True)

smoothPercentileWidth  Width of moving average window for smoothing threshold
                        (DEFAULT = 31 [days])

minDuration            Minimum duration for acceptance detected MHWs
                        (DEFAULT = 5 [days])

joinAcrossGaps         Boolean switch indicating whether to join MHWs
                        which occur before/after a short gap (DEFAULT = True)

maxGap                 Maximum length of gap allowed for the joining of MHWs
                        (DEFAULT = 2 [days])

maxPadLength           Specifies the maximum length [days] over which to interpolate
                        (pad) missing data (specified as nans) in input temp time series.
                        i.e., any consecutive blocks of NaNs with length greater
                        than maxPadLength will be left as NaN. Set as an integer.
                        (DEFAULT = False, interpolates over all missing values).

coldSpells             Specifies if the code should detect cold events instead of
                        heat events. (DEFAULT = False)
```

### Datasets coordinates
All datasets must have lat/latitude, lon/longitude and time as coordinates. `depth` coordinate is allowed for the main dataset. Currently, the depth as to be specified via its index in the coordinate array. Giving directly the wanted depth will be added later.

The percentile dataset (and offset if used) must have a `quantile` coordinate as a dimension for the variable. It is useful in the case you want to do the detection with different quantile (90, 99).

### Step 1 : Geospatial cutting (optionnal but recommended)
To use multiprocessing efficiently, the datasets must be cut in several smaller datasets over the lat/lon dimensions. Call `mhw-cut` with your config file to make it happen. Each sub-datasets will be called Cut_X.nc where X is the number of the cut (that is why your datasets (data, clim, percentile) must be in different folders).

The number of cuts does not matter, chunk size does. To find suitables nb_lat and nb_lon, it is better to use a notebook.
>import xarray as xr
ds = xr.open_dataset('dataset.nc', chunks={'latitude': nb_lat, 'longitude': nb_lon})
ds

nb_lat and nb_lon should be multiples of the latitude and longitude dimensions and choose carefully to have chunks of size over 10Mb (see Dask documentation for more details). Printing ds on a notebook gives you the size of the chunk (cut).

Please note that this step will double the space used in your disk.


### Step 2 : Detection
Call `mhw-detect` to detect MHW. With multiprocessing, each cut is processed in parallel. For a cut, you will get in `output_detection` a text file with the results of the detection. Finally, when all the detections are done, every text files are concatenated into one csv (with ; as a separator).

If you do not want to use multiprocessing just to make a detection on a small geospatial subset, you can give the option `-g lat_min lat_max lon_min lon_max` to the command.


### Commands
#### Geospatial cut
```
Usage: mhw-cut [OPTIONS]

  Cut datasets in multiple files

Options:
  -c, --config PATH  Specify configuration file  [required]
  --help             Show this message and exit.
```

#### Detection
```
Usage: mhw-detect [OPTIONS]

  Detect extreme events

Options:
  -c, --config PATH               Specify configuration file  [required]

  -g, --geographical-subset <FLOAT RANGE FLOAT RANGE FLOAT RANGE FLOAT RANGE>...
                                  The geographical subset as minimal latitude,
                                  maximal latitude, minimal longitude and
                                  maximal longitude.

                                  If set, the detection will be done on the
                                  subsetted global dataset given in config
                                  file (not the cuts) and sequentially.

  --categ-map TEXT                Generate category map in a netcdf file.

  --output-df TEXT                Give a name to the output dataframe. Two
                                  extensions are available: csv and parquet
                                  (default).     Save in csv if you want to
                                  open the dataframe with excel. Parquet is
                                  more efficient and takes less disk space.
                                  [default: data.parquet]

  --help                          Show this message and exit.
  ```


## Output
Here is an example of the output csv file. Every detected MHW are listed.
|     |      lat     |     lon     |   time_deb   |   time_end   |   time_peak  |  duration  |  duration_mod  |  duration_str  |  duration_sev  |  duration_ext  |  categ  |     imax    |     imean     |     ivar    |  rate_onset  |  rate_decline |
|:---:|:------------:|:-----------:|:------------:|:------------:|:------------:|:----------:|:--------------:|:--------------:|:--------------:|:--------------:|:-------:|:-----------:|:-------------:|:-----------:|:------------:|:-------------:|
|  0  |  -76.916664  |  -180.0     |  2003-01-01  |  2003-01-18  |  2003-01-04  |  18        |  5.0           |  2.0           |  5.0           |  6.0           |  4.0    |  2.341543   |  1.415663     |  0.551971   |  0.1867      |  0.2049       |
|  1  |  -76.916664  |  -180.0     |  2003-12-18  |  2003-12-23  |  2003-12-21  |  6         |  0.0           |  1.0           |  2.0           |  3.0           |  4.0    |  2.325211   |  1.858383     |  0.367969   |  0.482987    |  0.613132     |
|  2  |  -76.916664  |  -179.9166  |  2003-01-01  |  2003-01-18  |  2003-01-04  |  18        |  5.0           |  2.0           |  5.0           |  6.0           |  4.0    |  2.327172   |  1.420817     |  0.544248   |  0.182604    |  0.203315     |

## To do
- Add shapefile usage.
- Add an option to remove text files.

## Contribution
- Install [poetry](https://python-poetry.org/) in your python/conda environment.
- Clone this repository and checkout to your branch.
- Create a poetry environment for dev by running `poetry install`.
- Make your dev.
- Test your dev with the command `poetry run python monscript.py ...`.
- Commit and push.
- Ask for a merge request.



## References

Hobday, A.J. et al. (2016), A hierarchical approach to defining marine heatwaves, Progress in Oceanography, 141, pp. 227-238, doi: 10.1016/j.pocean.2015.12.014 [pdf](http://passage.phys.ocean.dal.ca/~olivere/docs/Hobdayetal_2016_PO_HierarchMHWDefn.pdf)
