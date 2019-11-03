                                   
'''
"NDFD download and map creator"
Created on May 11, 2013
Modified on November 21, 2014
Program which downloads Apparent Temperature, QPF, Snow, Ice, and Wind Gust
NDFD data as FLT files.  The NDFD data is then used as input for the WSII script.
Author: Mike Sutton WFO GRR - based on the work of Nathan Foster (WFO BTV) & Charles.Gant (WFO GSP)
Modified on 12/5/2014 to add a second go around for converting the NDFD files into flt files, since
I have noticed that the data may be there, but not all hours are converted to flt.  Might save us a
bit of download space.
Updated on January 6, 2015 to reduce the iceaccum and qpf data checks to look for file 9 and not file 10
which will help in the afternoon when there are only 9 periods available.
'''
import arcview, arcpy
import os,re
import shutil
import urllib2
import ftplib
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

#-------------------------------------------------------------------------
# The concept here is to establish which parameters to download, determine
# how many files are contained in each download, then process each element
# into flt files.

elementList = ['apt', 'snow', 'iceaccum', 'qpf', 'wgust']

print 'Cleaning Out Existing Files From the Working Directories'

for grid in elementList:
    for root, dirs, files in os.walk('C:\\degrib\\data\\' + grid + '\\working'):
        print 'Cleaning out ' + grid + ' files from the working directory'
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    for root, dirs, files in os.walk('C:\\degrib\\data\\' + grid):
        print 'Cleaning out ' + grid + ' files from the data directory'
        for f in files:
            os.unlink(os.path.join(root, f))

print 'Finished Existing File Clean Out'

try:
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
    else:
        raise LicenseError

except LicenseError:
    print "Spatial Analyst license is unavailable"  

#Variable Declarations
degribdir = 'C:/degrib/bin/' #This is the directory where the degrib.exe file exists
numlist = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36']
validtimesdict= {}
monthDict= {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}

for grid in elementList:
#    try:
        datadir = 'C:/degrib/data/' + grid + '/' #This is the directory where the output shapefiles will be created
        workdir = 'C:/degrib/data/' + grid + '/'
        if grid == 'apt':
            numlist = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36'] 
        if grid == 'snow':
            numlist = ['1','2','3','4','5','6']
        if grid == 'iceaccum':
            numlist = ['1','2','3','4','5','6','7','8','9','10']
        if grid == 'qpf':
            numlist = ['1','2','3','4','5','6','7','8','9','10']
        if grid == 'wgust':
            numlist = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42']
        #Download NDFD data
        filename = 'ds.' + grid + '.bin'
        fullurl = 'http://weather.noaa.gov/pub/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/VP.001-003/' + str(filename) #Change Region in URL To Fit Desired Region
        print 'Downloading ' + str(grid) + ' NDFD Grids'
        f = urllib2.urlopen(fullurl)
        html = f.read()
        f.close()
        fout = open(str(datadir) + str(filename) , "wb")
        fout.write(html)
        fout.close()
        print 'Download of ' + str(grid) + ' NDFD Grids is Complete'
        
        #Use DeGrib to create text file
        os.chdir(degribdir)
        cmd = 'degrib.exe -I -in ' + str(datadir) + str(filename) + ' >' + str(datadir) + str(grid) + '.txt'
        os.system(cmd)
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
                    cmd = 'degrib.exe -in ' + str(datadir) + str(filename) + ' -C -msg ' + str(msgnum) + ' -Met -Flt -namePath ' + str(workdir) + str(namestyle)
                    os.system(cmd)
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
print 'SUCCESS!!!!! - or so we think - let us check to see if we downloaded all of the data for each element'

for grid in elementList:
#    try:
        datadir = 'C:/degrib/data/' + grid + '/' #This is the directory where the output shapefiles will be created
        workdir = 'C:/degrib/data/' + grid + '/'
        if grid == 'apt':
            PATH = 'C:/degrib/data/apt/apt36.flt'
            if os.path.isfile(PATH):
                print str(PATH) + ' exists so we do not need to download it again'
                elementList.remove(grid)
            else:
                numlist = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36'] 
        if grid == 'snow':
            PATH = 'C:/degrib/data/snow/snow6.flt'
            if os.path.isfile(PATH):
                print str(PATH) + ' exists so we do not need to download it again'
                elementList.remove(grid)
            else:
                numlist = ['1','2','3','4','5','6']
        if grid == 'iceaccum':
            PATH = 'C:/degrib/data/iceaccum/iceaccum9.flt'
            if os.path.isfile(PATH):
                print str(PATH) + ' exists so we do not need to download it again'
                elementList.remove(grid)
            else:
                numlist = ['1','2','3','4','5','6','7','8','9','10']
        if grid == 'qpf':
            PATH = 'C:/degrib/data/qpf/qpf9.flt'
            if os.path.isfile(PATH):
                print str(PATH) + ' exists so we do not need to download it again'
                elementList.remove(grid)
            else:
                numlist = ['1','2','3','4','5','6','7','8','9','10']
        if grid == 'wgust':
            PATH = 'C:/degrib/data/wgust/wgust42.flt'
            if os.path.isfile(PATH):
                print str(PATH) + ' exists so we do not need to download it again'
                elementList.remove(grid)
            else:
                numlist = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42']

# Attempt to process the NDFD data again
for grid in elementList:
    datadir = 'C:/degrib/data/' + grid + '/' #This is the directory where the output shapefiles will be created
    workdir = 'C:/degrib/data/' + grid + '/'
    if grid == 'apt':
        numlist = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36']
    if grid == 'snow':
        numlist = ['1','2','3','4','5','6']
    if grid == 'iceaccum':
        numlist = ['1','2','3','4','5','6','7','8','9','10']
    if grid == 'qpf':
        numlist = ['1','2','3','4','5','6','7','8','9','10']
    if grid == 'wgust':
        numlist = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42']

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
                cmd = 'degrib.exe -in ' + str(datadir) + str(filename) + ' -C -msg ' + str(msgnum) + ' -Met -Flt -namePath ' + str(workdir) + str(namestyle)
                os.system(cmd)
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
# Check for completeness one last time
for grid in elementList:
#    try:
        datadir = 'C:/degrib/data/' + grid + '/' #This is the directory where the output shapefiles will be created
        workdir = 'C:/degrib/data/' + grid + '/'
        if grid == 'apt':
            PATH = 'C:/degrib/data/apt/apt36.flt'
            if os.path.isfile(PATH):
                print str(PATH) + ' exists so we do not need to download it again'
                elementList.remove(grid)
            else:
                numlist = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36'] 
        if grid == 'snow':
            PATH = 'C:/degrib/data/snow/snow6.flt'
            if os.path.isfile(PATH):
                print str(PATH) + ' exists so we do not need to download it again'
                elementList.remove(grid)
            else:
                numlist = ['1','2','3','4','5','6']
        if grid == 'iceaccum':
            PATH = 'C:/degrib/data/iceaccum/iceaccum9.flt'
            if os.path.isfile(PATH):
                print str(PATH) + ' exists so we do not need to download it again'
                elementList.remove(grid)
            else:
                numlist = ['1','2','3','4','5','6','7','8','9','10']
        if grid == 'qpf':
            PATH = 'C:/degrib/data/qpf/qpf9.flt'
            if os.path.isfile(PATH):
                print str(PATH) + ' exists so we do not need to download it again'
                elementList.remove(grid)
            else:
                numlist = ['1','2','3','4','5','6','7','8','9','10']
        if grid == 'wgust':
            PATH = 'C:/degrib/data/wgust/wgust42.flt'
            if os.path.isfile(PATH):
                print str(PATH) + ' exists so we do not need to download it again'
                elementList.remove(grid)
            else:
                numlist = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42']
# Since that failed, attempt to download the data again for the missing items
for grid in elementList:
        datadir = 'C:/degrib/data/' + grid + '/' #This is the directory where the output shapefiles will be created
        workdir = 'C:/degrib/data/' + grid + '/'
        #Download NDFD data
        filename = 'ds.' + grid + '.bin'
        fullurl = 'http://weather.noaa.gov/pub/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/VP.001-003/' + str(filename) #Change Region in URL To Fit Desired Region
        print 'Downloading ' + str(grid) + ' NDFD Grids for the second time'
        f = urllib2.urlopen(fullurl)
        html = f.read()
        f.close()
        fout = open(str(datadir) + str(filename) , "wb")
        fout.write(html)
        fout.close()
        print 'Download of ' + str(grid) + ' NDFD Grids is Complete'
        
        #Use DeGrib to create text file
        os.chdir(degribdir)
        cmd = 'degrib.exe -I -in ' + str(datadir) + str(filename) + ' >' + str(datadir) + str(grid) + '.txt'
        os.system(cmd)
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
                    cmd = 'degrib.exe -in ' + str(datadir) + str(filename) + ' -C -msg ' + str(msgnum) + ' -Met -Flt -namePath ' + str(workdir) + str(namestyle)
                    os.system(cmd)
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

# Assuming all is well, archive the downloaded ndfd files
elementList = ['apt', 'snow', 'iceaccum', 'qpf', 'wgust']

print 'Archiving the NDFD data to P:\GIS\ndfd\archive for later use'

for grid in elementList:
#    rawtime = datetime.datetime.now()
    localtime= time.strftime("%Y%m%d%H%M")
    src = 'C:\\degrib\\data\\' + grid + '\\ds.' + grid + '.bin'
    dst = 'P:\\GIS\\ndfd\\archive\\' + localtime + 'ds.' + grid + '.bin'
    shutil.copyfile(src, dst)
print 'Finished archiving the NDFD data'
