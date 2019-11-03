print "Starting the GIS Ice Accum Forecast Script"
print "Please be patient while files needed"
print "for this process are loaded."
import arcview, arcpy
import os,re
import shutil
import urllib2
import linecache
import datetime, time
import traceback
from datetime import datetime
from dateutil import tz
from_zone = tz.tzutc()
to_zone = tz.tzlocal()

try:
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
    else:
        raise LicenseError

except LicenseError:
    print "Spatial Analyst license is unavailable"  

from arcpy import env
from arcpy.sa import *
arcpy.env.overwriteOutput = True

#Variable Declarations
degribdir = 'C:/degrib/bin/' #This is the directory where the degrib.exe file exists

#GridList declaration
elementList = ['apt', 'snow', 'iceaccum', 'qpf', 'wgust']

validtimesdict= {}
monthDict= {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}

for grid in elementList:
    try:
        datadir = 'C:/degrib/data/' + str(grid) + '/' #This is the directory where the output shapefiles will be created
        workdir = 'C:/degrib/data/' + str(grid) + '/'
        if grid == 'apt':
            numlist = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36']
            tifname = "C://degrib//data//apt//apt.tif"
        if grid == 'snow':
            numlist = ['1','2','3','4','5','6']
            tifname = "C://degrib//data//snow//snow.tif"
        if grid == 'iceaccum':
            numlist = ['1','2','3','4','5','6','7','8','9','10']
            tifname = "C://degrib//data//iceaccum//iceaccum.tif"
        if grid == 'qpf':
            numlist = ['1','2','3','4','5','6','7','8','9','10']
            tifname = "C://degrib//data//qpf//qpf.tif"
        if grid == 'wgust':
            numlist = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42']
            tifname = "C://degrib//data//wgust//wgust.tif"
        filename = 'ds.' + grid + '.bin'      
        file = datadir + str(grid) + '.txt'
        data = open(file, 'r')
        headerline = data.readline()
        headerline = headerline.strip()
        lines = str(data.read()).splitlines()
        for line in lines:
            if line != str(headerline):
                line = line.split(',')
                msgnum = line[0]
                msgnum = msgnum.split('.')
                msgnum = msgnum[0]
                if msgnum in numlist:
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

                    rasname = str(datadir) + str(grid) + str(msgnum) + '.flt'
                    print rasname
                    arcpy.FloatToRaster_conversion(rasname,tifname)
                    arcpy.DefineProjection_management(tifname, "PROJCS['NDFD',GEOGCS['GCS_Unknown',DATUM['D_unknown',SPHEROID['Sphere',6371000.0,0.0]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['false_easting',0.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-95.0],PARAMETER['standard_parallel_1',25.0],PARAMETER['standard_parallel_2',25.0],PARAMETER['latitude_of_origin',25.0],UNIT['Meter',1.0]]")
                    DATA = ValidLocalTIME
                    if grid == 'apt':
                        mxd = arcpy.mapping.MapDocument(r"P://GIS//ndfd//wsii//apt.mxd")
                        PNGinfo = r"P://GIS//ndfd//apt//apt_" + str(msgnum)+'.png'
                    if grid == 'snow':
                        mxd = arcpy.mapping.MapDocument(r"P://GIS//ndfd//wsii//snowamount.mxd")
                        PNGinfo = r"P://GIS//ndfd//snow//snow_" + str(msgnum)+ '.png'
                    if grid == 'iceaccum':
                        mxd = arcpy.mapping.MapDocument(r"P://GIS//ndfd//wsii//iceaccum.mxd")
                        PNGinfo = r"P://GIS//ndfd//iceaccum//iceaccum_" + str(msgnum)+'.png'
                    if grid == 'qpf':
                        mxd = arcpy.mapping.MapDocument(r"P://GIS//ndfd//wsii//qpf.mxd")
                        PNGinfo = r"P://GIS//ndfd//qpf//qpf_" + str(msgnum)+'.png'
                    if grid == 'wgust':
                        mxd = arcpy.mapping.MapDocument(r"P://GIS//ndfd//wsii//wgust.mxd")
                        PNGinfo = r"P://GIS//ndfd//wgust//wgust_" + str(msgnum)+'.png'
                    for textElement in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
                        if textElement.text == "Valid":
                            print 'Changing: ' + str(textElement.text)
                            textElement.text = 'Data Ending '+ str(DATA) + ' EST'
                    from datetime import tzinfo,timedelta,datetime
                    utc_datetime = datetime.utcnow().strftime("%Y-%m-%d-%H%MZ")
                    arcpy.mapping.ExportToPNG(mxd, PNGinfo, resolution=96)
                    del mxd
    except:
        traceback.print_exc()
print 'SUCCESS!!!!!  '
