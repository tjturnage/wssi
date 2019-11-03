# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 20:44:17 2018

@author: Owner
"""

from osgeo import gdal, osr, gdal_array, gdalconst
import numpy as np
from netCDF4 import Dataset
import xarray as xr


src = 'C:\\data\\GIS\\ndfd-mini\\annual_snow.tif'
ncsrc = 'C:\degrib\data\combined\\apt1.nc'
ds1 = xr.open_mfdataset(ncsrc)

rtgroup = Dataset(ncsrc, 'r')

dsr = gdal.Open(src, gdal.GA_ReadOnly)
for x in range(1, dsr.RasterCount + 1):
    band = dsr.GetRasterBand(x)
    sn = band.ReadAsArray()

geotransform = dsr.GetGeoTransform()
print geotransform

#ds1 = xr.open_mfdataset('C:\degrib\data\combined\*.nc')

import matplotlib.pyplot as plt
plt.imshow(sn)
plt.show()
plt.imshow(sn, vmin=0.0, vmax=250.0)
plt.show()


inputfile =  'C:\\data\\qpf3.nc'
input = gdal.Open(inputfile, gdalconst.GA_ReadOnly)
inputProj = input.GetProjection()
inputTrans = input.GetGeoTransform()

#referencefile = #Path to reference file
reference = gdal.Open(referencefile, gdalconst.GAReadOnly)
referenceProj = reference.GetProjection()
referenceTrans = reference.GetGeoTransform()
bandreference = reference.GetRasterBand(1)    
x = reference.RasterXSize 
y = reference.RasterYSize


#outputfile = #Path to output file
driver= gdal.GetDriverByName('GTiff')
output = driver.Create(outputfile,x,y,1,bandreference.DataType)
output.SetGeoTransform(referenceTrans)
output.SetProjection(referenceProj)

gdal.ReprojectImage(input,output,inputProj,referenceProj,gdalconst.GRA_Bilinear)

del output



