# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 17:30:07 2018

@author: Owner
"""
from osgeo import gdal, gdalnumeric, ogr, osr
import numpy as np
import os, sys
from netCDF4 import Dataset
from PIL import Image, ImageDraw
from scipy.interpolate import griddata
from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata

def gdal_error_handler(err_class, err_num, err_msg):
    errtype = {
            gdal.CE_None:'None',
            gdal.CE_Debug:'Debug',
            gdal.CE_Warning:'Warning',
            gdal.CE_Failure:'Failure',
            gdal.CE_Fatal:'Fatal'
    }
    err_msg = err_msg.replace('\n',' ')
    err_class = errtype.get(err_class, 'None')
    print 'Error Number: %s' % (err_num)
    print 'Error Type: %s' % (err_class)
    print 'Error Message: %s' % (err_msg)

def convertXY(xy_source, inproj, outproj):
    # function to convert coordinates

    shape = xy_source[0,:,:].shape
    size = xy_source[0,:,:].size

    # the ct object takes and returns pairs of x,y, not 2d grids
    # so the the grid needs to be reshaped (flattened) and back.
    ct = osr.CoordinateTransformation(inproj, outproj)
    xy_target = np.array(ct.TransformPoints(xy_source.reshape(2, size).T))

    xx = xy_target[:,0].reshape(shape)
    yy = xy_target[:,1].reshape(shape)

    return xx, yy

def GetExtent(gt,cols,rows):
    ''' Return list of corner coordinates from a geotransform

        @type gt:   C{tuple/list}
        @param gt: geotransform
        @type cols:   C{int}
        @param cols: number of columns in the dataset
        @type rows:   C{int}
        @param rows: number of rows in the dataset
        @rtype:    C{[float,...,float]}
        @return:   coordinates of each corner
    '''
    ext=[]
    xarr=[0,cols]
    yarr=[0,rows]

    for px in xarr:
        for py in yarr:
            x=gt[0]+(px*gt[1])+(py*gt[2])
            y=gt[3]+(px*gt[4])+(py*gt[5])
            ext.append([x,y])
            print x,y
        yarr.reverse()
    return ext

def ReprojectCoords(coords,src_srs,tgt_srs):
    ''' Reproject a list of x,y coordinates.

        @type geom:     C{tuple/list}
        @param geom:    List of [[x,y],...[x,y]] coordinates
        @type src_srs:  C{osr.SpatialReference}
        @param src_srs: OSR SpatialReference object
        @type tgt_srs:  C{osr.SpatialReference}
        @param tgt_srs: OSR SpatialReference object
        @rtype:         C{tuple/list}
        @return:        List of transformed [[x,y],...[x,y]] coordinates
    '''
    trans_coords=[]
    transform = osr.CoordinateTransformation( src_srs, tgt_srs)
    for x,y in coords:
        x,y,z = transform.TransformPoint(x,y)
        trans_coords.append([x,y])
    return trans_coords


def array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array):

    cols = array.shape[1]
    rows = array.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(4326)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()



def raster2array(rasterfn):
    raster = gdal.Open(rasterfn)
    band = raster.GetRasterBand(1)
    array = band.ReadAsArray()
    return array

varDict = dict([('apt', num36),('snow', num6),('iceaccum', num10),('qpf','QPF_SFC'),('wgust',num42),('maxt',num6)])

nc = Dataset('C:\\data\\qpf3.nc', 'r')
units = nc.variables['QPF_SFC'][:]
vs = nc.get_variables_by_attributes()
grid = np.array(units)
grid2d = np.reshape(grid, (grid.shape[1], grid.shape[2]))
gnew = grid2d.T
g2 = gnew.T


lat = nc.variables['latitude'][:]
lon = nc.variables['longitude'][:]

xmin,ymin,xmax,ymax = [lon.min(),lat.min(),lon.max(),lat.max()]
nrows,ncols = np.shape(grid2d)
xres = (xmax-xmin)/float(ncols)
yres = (ymax-ymin)/float(nrows)
geotransform=(xmin,xres,0,ymax,0, -yres) 

rastOut = 'C:\\data\\rasty.tif'
output_raster = gdal.GetDriverByName('GTiff').Create(rastOut,ncols, nrows, 1 ,gdal.GDT_Float32)
output_raster.SetGeoTransform(geotransform)
srs = osr.SpatialReference()
output_raster.SetProjection( srs.ExportToWkt() )   # Exports the coordinate system                                                # to the file
output_raster.GetRasterBand(1).WriteArray(grid2d)   # Writes my array to the raster
output_raster.FlushCache() 


ds = gdal.Open('C:\\data\\GIS\\land-tif.tif')

cols = ds.RasterXSize
rows = ds.RasterYSize
data = ds.ReadAsArray()
gt = ds.GetGeoTransform()
proj = ds.GetProjection()

xres = gt[1]
yres = gt[5]

# get the edge coordinates and add half the resolution 
# to go to center coordinates
xmin = gt[0] + xres * 0.5   #
xmax = gt[0] + (xres * ds.RasterXSize) - xres * 0.5
ymin = gt[3] + (yres * ds.RasterYSize) + yres * 0.5
ymax = gt[3] - yres * 0.5

xgrid = np.arange(xmin,xmax,xres)
ygrid = np.arange(ymax,ymin,yres)
X, Y = np.meshgrid(xgrid,ygrid)

origin = [gt[0],gt[3]]
ext=GetExtent(gt,cols,rows)

src_srs=osr.SpatialReference()
src_srs.ImportFromWkt(ds.GetProjection())
tgt_srs = src_srs.CloneGeogCS()

geo_ext=ReprojectCoords(ext,src_srs,tgt_srs)


npRaster = gdal.Dataset.ReadAsArray(ds)
blurred = gaussian_filter(npRaster, sigma=4)
rasterFinal = 'C:\\data\\GIS\\blur.tif'
array2raster(rasterFinal,origin,xres,yres,blurred)

ds = None

# create a grid of xy coordinates in the original projection
xy_source = np.mgrid[xmin:xmax+xres:xres, ymax+yres:ymin:yres]

xx, yy = convertXY(xy_source, src_srs, tgt_srs)

# plot the data (first layer)
im1 = plt.pcolormesh(xgrid, ygrid, blurred)

# annotate
#plt.drawcountries()
#plt.drawcoastlines(linewidth=.5)

plt.savefig('world.png',dpi=75)


# this allows GDAL to throw Python Exceptions
gdal.UseExceptions()

#
#  get raster datasource

srcband = rasterFinal

#
src_ds = gdal.Open(srcband)
if src_ds is None:
    print 'Unable to open %s'
    sys.exit(1)

srcband1 = src_ds.GetRasterBand(1)
#  create output datasource
#
dst_layername = "polygon"
drv = ogr.GetDriverByName("ESRI Shapefile")
dst_ds = drv.CreateDataSource( dst_layername + ".shp" )
dst_layer = dst_ds.CreateLayer(dst_layername, srs = None )

 #gdal_contour -a elev -i 50 st_helens_dem.tif st_helens_contours.shp

gdal.Polygonize(srcband1, None, dst_layer, -1, [], callback=None )