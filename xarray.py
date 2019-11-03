# -*- coding: utf-8 -*-
"""
Forecast data for the upcoming 72 hours is downloaded from NDFD of: 
6-hour snow accumulation
6-hour ice accumulation
6-hour precipitation accumulation (QPF)
wind gust (hourly time steps)
temperature (hourly time steps)

From these data, additional parameters are calculated
total 72 hour snowfall
total 72 hour ice accumulation
maximum wind gust within each 6 hour period
6-hourly snowfall accumulation rate 
6-hourly snow-liquid ratio
72-hour average snow-liquid ratio

"""


#import numpy as np
#from osgeo import gdal, osr
#elementList = ['apt','snow','iceaccum','qpf','wgust']import glob
import glob
import shutil
import shutil
import numpy as np
import pandas as pd
import xarray as xr

#import numpy as np
from datetime import datetime, timedelta

elementList = ['apt']
varDict = dict([('apt', 'ApparentT_SFC'),('t', 'T_SFC'),('snow', 'SnowAmt_SFC'),('iceaccum', 'IceAccum_SFC'),
                ('qpf', 'QPF_SFC'),('wgust','WindGust_SFC')])
baseNCdir = 'C:\\degrib\\data\\'
nc_dest_dir = "C:/degrib/data/combined"

def copyFiles(src):
    for file in glob.glob(src):
        print(file)
        shutil.copy(file, nc_dest_dir)

def timeIntervals(projTime1):
    tt = pd.to_datetime(projTime1)
    f1 = tt.hour
    if (f1 >= 18):
        newTime = tt + timedelta(days=1)
        baseTime = newTime.replace(hour=0,minute=0,second=0, microsecond=0)
    elif (f1 >= 6):
        baseTime = tt.replace(hour=12,minute=0,second=0, microsecond=0) 
    else:
        baseTime = tt.replace(hour=0,minute=0,second=0, microsecond=0)

    datetimeList = pd.date_range(baseTime, periods=13, freq='6H')
    return datetimeList

    
for i, j in zip(range(0,len(elementList)),elementList):
    src = baseNCdir + j + '\\working\*.nc'
    copyFiles(src);

nc_dest_dir_files = nc_dest_dir + '/apt*.nc'

ds1 = xr.open_mfdataset(nc_dest_dir_files)
if i == 0:
    baseTime = ds1.ProjectionHr.values[0]
    intervals = timeIntervals(baseTime)

ds2 = ds1.sortby('ProjectionHr')
#ProjHrlabels = intervals[1:]
hrLabels = []
for i in range(1,13):
    hrLabels.append(int(i*6))
    
aptArr = ds2.ApparentT_SFC
ProjHrList = ds2.ProjectionHr.to_series()

binApt = aptArr.groupby_bins('ProjectionHr', intervals, right=False, squeeze=True, labels=hrLabels)
gg = sorted(binApt.groups.items())
slices = []
for i in range(0,len(gg)):
    slices.append(gg[i][1][0])
for j in range(1,len(slices)):
    print ProjHrList[slices[j-1]]
    aptArrSl = aptArr[dict(ProjectionHr=slice(slices[j-1],slices[j]))]
    dmax = aptArrSl.max('ProjectionHr')


    
    #ds1 = None
"""
dsDict = {}
for el in elementList:
    dsDict.update(el=[])
    src = baseNCdir + el + '\\working\*.nc'
    print src
    ds1 = xr.open_mfdataset(src)
    if el == elementList[0]:
        baseTime = ds1.ProjectionHr.values[0]
        intervals = timeIntervals(baseTime)
    for ts in range(1,len(intervals)):
        dsnew = ds1.sel(ProjectionHr=slice(intervals[ts-1],intervals[ts]))
        arr = evalInterval(el,dsnew)
        dsDict[el].append(arr)

#sumTotal
sumQPF = ds1.sum(dim='ProjectionHr')
qpf = sumQPF.QPF_SFC
#first 24 hours
dsnew = ds1.sel(ProjectionHr=slice(intervals[0],intervals[1]))
dsnew.attrs['title'] = varDict['wgust']
dsnew.attrs['comment'] = str(intervals[0])



import xarray as xr
import numpy as np

# create an example dataset
da = xr.DataArray(np.random.rand(10,30,40), dims=['time', 'lat', 'lon'])

# define a function to compute a linear trend of a timeseries
def minimum(x):
    pf = np.polyfit(x.time, x, 1)
    # we need to return a dataarray or else xarray's groupby won't be happy
    return xr.DataArray(pf[0])

# stack lat and lon into a single dimension called allpoints
stacked = da.stack(allpoints=['lat','lon'])
stacked = ds1.stack(allpoints=['XCells','YCells'])
# apply the function over allpoints to calculate the trend at each point
trend = stacked.groupby('allpoints').apply(linear_trend)
# unstack back to lat lon coordinates
trend_unstacked = trend.unstack('allpoints')


rastOut = 'C:\\data\\rasty.tif'
output_raster = gdal.GetDriverByName('GTiff').Create(rastOut,ncols, nrows, 1 ,gdal.GDT_Float32)
output_raster.SetGeoTransform(geotransform)
srs = osr.SpatialReference()
output_raster.SetProjection( srs.ExportToWkt() )   # Exports the coordinate system                                                # to the file
output_raster.GetRasterBand(1).WriteArray(grid2d)   # Writes my array to the raster
output_raster.FlushCache() 

from affine import Affine
da = xr.open_rasterio('C:\\data\\GIS\\ndfd-mini\\annual_snow.tif')
transform = Affine(*da.attrs['transform'])
nx, ny = da.sizes['x'], da.sizes['y']
x, y = np.meshgrid(np.arange(nx)+0.5, np.arange(ny)+0.5) * transform

from PIL import Image
im = Image.open('C:\\data\\GIS\\ndfd-mini\\annual_snow.tif')
im.show('C:\\data\\GIS\\ndfd-mini\\annual_snow.tif')


"""

