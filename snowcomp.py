# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# snowcomp.py
# Created from WSII.py, which was created on: 2013-10-18 09:00:37.00000
#   (generated by ArcGIS/ModelBuilder) and updated in November/December 2014
# This script will take archived NDFD snow forecast information, observed
# snowfall information from RIDGE2, and create a difference map for a 24
# hour period.
# By:  Mike Sutton, ITO WFO GRR
# ---------------------------------------------------------------------------
print "Starting the SnowComp Creation Script"
print "Please be patient while the files needed"
print "for this process are loaded."
# Import arcpy module
import arcview, arcpy, os, shutil, ftplib, datetime, re, sys
from arcpy import env
from datetime import datetime
from dateutil import tz
from_zone = tz.tzutc()
to_zone = tz.tzlocal()

# Check out any necessary liceaccumnses
arcpy.CheckOutExtension("spatial")

arcpy.env.overwriteOutput = True

from arcpy.sa import *

# Process the archived NDFD snow data
# Read the filename of the archived data that is passed to the program via command line
filename = "P:\\GIS\\NDFD\\archive\\" + sys.argv[1]

#Variable Declarations
elementList = ['snow']
numlist = ['1','2','3','4','5','6']
degribdir = 'C:/degrib/bin/' #This is the directory where the degrib.exe file exists
validtimesdict= {}
monthDict= {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}

for grid in elementList:
#    try:
        datadir = 'P:\\GIS\\snowcomp\\' #This is the directory where the output shapefiles will be created
        workdir = 'P:\\GIS\\snowcomp\\'
        #Use DeGrib to create text file
        os.chdir(degribdir)
        cmd = 'degrib.exe -I -in ' + str(filename) + ' >' + str(datadir) + str(grid) + '.txt'
#        os.system(cmd)
        file = datadir + str(grid) + '.txt'

        #Create Each Shapefile and Graphic
        data = open(file, 'r')
        headerline = data.readline()
        headerline = headerline.strip()
        lines = str(data.read()).splitlines()
        print 'Converting Each ' + str(grid) + ' Time Step Into Individual Shapefiles'
        for line in lines:
            if line != str(headerline):
                line = line.split(',')
                msgnum = line[0]
                msgnum = msgnum.split('.')
                msgnum = msgnum[0]
                if msgnum in numlist:
                    namestyle = ' -nameStyle ' + '"' + str(grid) + str(msgnum) + '.txt"'
                    cmd = 'degrib.exe -in ' + str(filename) + ' -C -msg ' + str(msgnum) + ' -Met -Flt -namePath ' + str(workdir) + str(namestyle)
#                    os.system(cmd)
                    valid = line[6]
                    valid = valid.strip()
                    valid = valid.split(" ")
                    validdate = valid[0]
                    validtime = valid[1]
                    validtime = validtime.split(":")
                    validhr = validtime[0]
                    validmin = validtime[1]
                    validdate = validdate.split("/")
                    year = validdate[2]
                    month = validdate[0]
                    day = validdate[1]

                    ValidString = str(month) + '/' + str(day) + '/' + str(year) + ' ' + str(validhr) + ':' + str(validmin)
                    print str(ValidString)

                    #Convert Valid String To Local Time
                    utc = datetime.strptime(str(ValidString), '%m/%d/%Y %H:%M')
                    utc = utc.replace(tzinfo=from_zone)
                    Valid = utc.astimezone(to_zone)
                    Valid = str(Valid).split(" ")
                    Validdate = Valid[0]
                    Validdate = Validdate.split('-')
                    Validyr = Validdate[0]
                    Validmo = Validdate[1]
                    Validdy = Validdate[2]
                    Validtime = Valid[1]
                    Validtime = Validtime.split(":")
                    Validhr = Validtime[0]

                    if int(Validhr) == 00:
                        Validhr = 12
                        AMPM = 'AM'
                    else:
                        if int(Validhr) >= 01 and int(Validhr) < 12:
                            AMPM = 'AM'
                        if int(Validhr) > 12:
                            Validhr = int(Validhr) - 12
                            AMPM = 'PM'
                        if int(Validhr) == 12:
                            AMPM = 'PM'
                               
                    Validmn = Validtime[1] 
                    AltValidmo = monthDict[int(Validmo)]                   
                    ValidLocalTIME =  AltValidmo + ' ' + Validdy + ', ' + Validyr + ' ' + str(Validhr) + ':' + Validmn + ' ' + AMPM
                    print ValidLocalTIME             
#        except:
#            traceback.print_exc()
print 'SUCCESS!!!!! Part 1 has ended...  Now for part 2'
# we want snow grids 3, 4, 5, and 6.
### Local variables:
#snow1_flt = "C:\\degrib\\data\\snow\\snow1.flt"
#snow2_flt = "C:\\degrib\\data\\snow\\snow2.flt"
snow3_flt = "P:\\GIS\\snowcomp\\snow3.flt"
snow4_flt = "P:\\GIS\\snowcomp\\snow4.flt"
snow5_flt = "P:\\GIS\\snowcomp\\snow5.flt"
snow6_flt = "P:\\GIS\\snowcomp\\snow6.flt"
fcst_snow = "P:\\GIS\\snowcomp\\fcst_snow"
obs = "P:\\GIS\\snowcomp\\obs"

# Add up the 6 hour snowfall forecast float files
env.workspace = r"P:/GIS/snowcomp"
rasterList = arcpy.ListRasters("*.flt", "ALL")
fcst_snow=CellStatistics(rasterList, "SUM", "NODATA")
arcpy.DefineProjection_management(fcst_snow, "PROJCS['NDFD',GEOGCS['GCS_Unknown',DATUM['D_unknown',SPHEROID['Sphere',6371000.0,0.0]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['false_easting',0.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-95.0],PARAMETER['standard_parallel_1',25.0],PARAMETER['standard_parallel_2',25.0],PARAMETER['latitude_of_origin',25.0],UNIT['Meter',1.0]]")
fcst_snow.save("P:/GIS/snowcomp/fcst.tif")

# Convert the 24 hour RIDGE2 observed snowfall shapefile into something we can use
obs_snow = "P:/GIS/snowcomp/obs.tif"
print "converting feature to raster"
arcpy.FeatureToRaster_conversion("P:\\GIS\\snowcomp\\snowfall24\\snowfall.shp","amount",obs_snow)

# Create the snow difference grid
diff_snow = arcpy.sa.Minus("fcst.tif","obs.tif" )
diff_snow.save("P:/GIS/snowcomp/diff_snow.tif")
arcpy.DefineProjection_management(obs_snow, "PROJCS['NDFD',GEOGCS['GCS_Unknown',DATUM['D_unknown',SPHEROID['Sphere',6371000.0,0.0]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['false_easting',0.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-95.0],PARAMETER['standard_parallel_1',25.0],PARAMETER['standard_parallel_2',25.0],PARAMETER['latitude_of_origin',25.0],UNIT['Meter',1.0]]")
arcpy.DefineProjection_management(diff_snow, "PROJCS['NDFD',GEOGCS['GCS_Unknown',DATUM['D_unknown',SPHEROID['Sphere',6371000.0,0.0]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['false_easting',0.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-95.0],PARAMETER['standard_parallel_1',25.0],PARAMETER['standard_parallel_2',25.0],PARAMETER['latitude_of_origin',25.0],UNIT['Meter',1.0]]")
# Create the image
mapName = "P:/gis/snowcomp/snowbias_michigan.mxd" #FULL PATH file name of an existing map
mxd = arcpy.mapping.MapDocument(mapName) #create a mapDocument object
arcpy.mapping.ExportToPNG(mxd, r'P:\gis\snowcomp\snowbias.png', resolution=96)