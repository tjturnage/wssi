# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 15:15:50 2018

@author: Owner
"""


import netCDF4
from osgeo import gdal, osr
from osgeo.gdalnumeric import *
from osgeo.gdalconst import *

def NetCDFtoTIFF(fin, fout):
    src_ds = gdal.Open( fin )
    format = "GTiff"
    driver = gdal.GetDriverByName( format )
    dst_ds = driver.CreateCopy( fout, src_ds, 0 )
    dst_ds = None
    src_ds = None
    
source = 'C:\\degrib\\data\\qpf\\working\\qpf7.nc'
dest = 'C:\\data\\qpftiftest.tif'
NetCDFtoTIFF(source, dest)

bandNum1 = 0
bandNum2 = 200

outFile = "out.tiff"

#Open the dataset
#ds1 = gdal.Open(fileName, GA_ReadOnly )
ds1 = gdal.Open(fileName)
band1 = ds1.GetRasterBand(bandNum1)
band2 = ds1.GetRasterBand(bandNum2)

#Read the data into numpy arrays
data1 = BandReadAsArray(band1)
data2 = BandReadAsArray(band2)

#The actual calculation
dataOut = numpy.sqrt(data1*data1+data2*data2)

#Write the out file
driver = gdal.GetDriverByName("GTiff")
dsOut = driver.Create("out.tiff", ds1.RasterXSize, ds1.RasterYSize, 1, band1.DataType)
CopyDatasetInfo(ds1,dsOut)
bandOut=dsOut.GetRasterBand(1)
BandWriteArray(bandOut, dataOut)

