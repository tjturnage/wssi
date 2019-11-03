import os,re
import shutil
from shutil import copyfile
import urllib2
import datetime, time
from datetime import datetime, timedelta
from dateutil import tz
from_zone = tz.tzutc()
to_zone = tz.tzlocal()

def downloadDegribNDFD(grid):
    filename = 'ds.' + grid + '.bin'
    fullurl = 'http://tgftp.nws.noaa.gov/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/VP.001-003/' + str(filename) #Change Region in URL To Fit Desired Region
    print 'Downloading ' + str(grid) + ' NDFD Grids'
    f = urllib2.urlopen(fullurl)
    html = f.read()
    f.close()
    fout = open(str(datadir) + grid + "\\" + str(filename) , "wb")
    fout.write(html)
    fout.close()
    print 'Download of ' + str(grid) + ' NDFD Grids is Complete'

def stageArcFiles(prefix,elements):
    for f in elements:
        src = 'C:/data/GIS/ndfd/archive/' + prefix + 'ds.' + f + '.bin'
        dst = 'C:/degrib/data/' + f + '/ds.' + f + '.bin'
        shutil.copyfile(src, dst)
    
def getValidTime(grid):
        baseDir = datadir + grid + '/'  # example: C:/degrib/data/wgust/
        fileName = baseDir + 'ds.' + grid + '.bin'
        workdir = baseDir + '/working/'

        numlist = numDict[grid]
        print "numlist: " + str(numlist)
        os.chdir(degribdir)        
        cmd = 'degrib.exe -I -in ' + str(fileName) + ' >' + str(datadir) + str(grid) + '.txt'
        os.system(cmd)
        file = str(datadir) + str(grid) + '.txt'
        data = open(file, 'r')
        headerline = data.readline()
        headerline = headerline.strip()
        print headerline
        lines = str(data.read()).splitlines()
        print 'Converting Each ' + str(grid) + ' Time Step Into Individual Shapefiles'
        for line in lines:
            if line != str(headerline):
                line = line.split(',')
                msgnum = line[0]
                print line[0]
                msgnum = msgnum.split('.')
                msgnum = msgnum[0]
                print "msgnum: " + str(msgnum)
                if msgnum in numlist:
                    #namestyle = ' -nameStyle ' + '"' + str(grid) + str(msgnum) + '.nc"'
                    nameGrid = grid + str(msgnum) + '.nc'
                    #cmd1 = 'degrib.exe -in ' + str(fileName) + ' -C -msg ' + str(msgnum) + ' -Met -nFlt -NetCDF 4 -namePath ' + str(workdir) + str(namestyle)
                    cmd1 = 'degrib.exe -in ' + str(fileName) + ' -C -msg ' + str(msgnum) + ' -Met -nFlt -NetCDF 4 -out ' + str(workdir) + nameGrid
                    print cmd1
                    os.system(cmd1)
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


def cleanFiles(elementList):
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

#------------------------------------------
hrList = []
for i in range(0,73):
    hr = str(i)
    hrList.append(hr)
numPrecip = hrList[1:13]  # 1...12 for 6hrly thru 72hr  
#num72 = hrList[1:13]  # 1...72 for 1hrly thru 72hr
num72 = hrList[1:52]  # 1...42 for 1hrly thru 36 then 3hrly through 48

numDict = dict([('apt', num72),('snow', numPrecip),('iceaccum', numPrecip),
                ('qpf', numPrecip),('wgust',num72)])

                
datadir = 'C:/degrib/data/'
degribdir = 'C:/ndfd/degrib/bin' #This is the directory where the degrib.exe file exists
monthDict= {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June',
            7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
 

elementList = ['apt','snow','iceaccum','qpf','wgust']
cleanFiles(elementList); #purge already existing files

# this is for using an old case for testing purposes
binPrefix = '201804130904' # or None
if binPrefix is not None:
    stageArcFiles(binPrefix,elementList);
    
os.chdir(degribdir)
for grid in elementList:
    #downloadDegribNDFD(grid)
    getValidTime(grid)

#if not archived case, check that all grids were acquired
if binPrefix is None:
    for grid in elementList:
        numlist = numDict[grid]
        lastFileNum = str(numlist[-1])
        #PATH = datadir + grid + "/" + grid + lastFileNum + ".bin"
        PATH = datadir + grid + "/" + grid + lastFileNum + ".nc"
        if os.path.isfile(PATH):
            print str(PATH) + ' exists so we do not need to download it again'
        else:
            getValidTime(grid)
        
#Archive assuming all is well and not already archived
if binPrefix is not None:
    print 'Nothing to copy... data already archived'
else:
    print 'Archiving NDFD data for later use'
    for grid in elementList:
       # localtime= time.strftime("%Y%m%d%H%M")
        localtime= time.strftime("%Y%m%d%H")
        src = 'C:\\degrib\\data\\' + grid + '\\ds.' + grid + '.bin'
        dst = 'C:\\data\\GIS\\ndfd\\archive\\' + localtime + 'ds.' + grid + '.bin'
        shutil.copyfile(src, dst)
    print 'Finished archiving the NDFD data'
