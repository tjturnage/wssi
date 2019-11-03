# -*- coding: utf-8 -*-
"""
Created on Sat Jun 16 10:37:33 2018

@author: Owner
"""
def array2raster(rasterfn,newRasterfn,array):
    raster = gdal.Open(rasterfn)
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    cols = raster.RasterXSize
    rows = raster.RasterYSize

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Float32)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt(raster.GetProjectionRef())
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()

import netCDF4
from matplotlib import pyplot as plt
myFile = 'C:\\data\\qpf3.nc'

varDict = dict([('apt', 'ApparentT_SFC'),('snow', 'SnowAmt_SFC'),
                ('iceaccum', 'IceAccum_SFC'),('qpf', 'QPF_SFC'),
                ('wgust','WindGust_SFC')])

nc = netCDF4.Dataset(myFile)
ncv = nc.variables
ncv.keys()

# subset and subsample
lon = ncv['longitude'][:,:]
lat = ncv['latitude'][:][:]
# read the 1st time step
itime = 0
qpf = ncv['QPF_SFC'][itime,:,:]

plt.pcolormesh(lon,lat,qpf);
plt.colorbar();

#array2raster('C:\\data\\qpfraster.tif', )