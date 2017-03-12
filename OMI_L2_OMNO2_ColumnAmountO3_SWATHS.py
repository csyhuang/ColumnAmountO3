import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from netCDF4 import Dataset
from urllib import urlretrieve
import tables, os, math, sys

def run2(FILE_NAME):
    #filename  = "OMI-Aura_L2-OMCLDO2_2007m1017t0009-o17311_v002-2007m1017t172248.he5"
    swathname = 'ColumnAmountO3'
    
    # Open the HDF-file, and offset the root so that path references become shorter
    hdf5ref = tables.openFile(FILE_NAME, mode="r", rootUEP="/HDFEOS/SWATHS/"+swathname)
    
    # get references to the geolocation and data fileds
    geo = hdf5ref.getNode("/","Geolocation Fields")
    data = hdf5ref.getNode("/","Data Fields")
    
    # read the data
    latitude = geo.Latitude.read()
    longitude = geo.Longitude.read()
    ColumnAmountO3 = data.CloudFraction.read()
    
    # close access to the file
    hdf5ref.close()
    return latitude,longitude,ColumnAmountO3

def run(FILE_NAME):
    DATAFIELD_NAME = 'ColumnAmountO3'

    print 'FILE_NAME=',FILE_NAME
    nc = Dataset(FILE_NAME)
    #grp = nc.groups['HDFEOS'].groups['SWATHS'].groups['OMI Column Amount O3'] 
    grp = nc.groups['HDFEOS'].groups['SWATHS'].groups[DATAFIELD_NAME] # DOAS
    var = grp.groups['Data Fields'].variables[DATAFIELD_NAME]
    
    # netCDF4 doesn't quite handle the scaling correctly in this case since
    # the attributes are "ScaleFactor" and "AddOffset" instead of
    # "scale_factor" and "add_offset".  We'll do the scaling and conversion
    # to a masked array ourselves.
    var.set_auto_maskandscale(False)

    data = var[:].astype(np.float64)

    # Retrieve any attributes that may be needed later.
    scale = var.ScaleFactor
    offset = var.Offset
    title = var.Title
    missing_value = var.MissingValue
    fill_value = var._FillValue
    units = var.Units

    # Retrieve the geolocation data.
    latitude = grp.groups['Geolocation Fields'].variables['Latitude'][:]
    #print latitude[100,:]
    longitude = grp.groups['Geolocation Fields'].variables['Longitude'][:]
    time = grp.groups['Geolocation Fields'].variables['Time'][:]    
    print 'latitude.shape',latitude.shape
    print 'longitude.shape',longitude.shape
    print 'time.shape=',time.shape
    
    time2 = time[:,np.newaxis]*np.ones_like(latitude)
    print 'time2.shape=',time2.shape

    #endif USE_NETCDF4

    data[data == missing_value] = np.nan
    data[data == fill_value] = np.nan
    data = scale * (data - offset)
    
    datam = np.ma.masked_where(np.isnan(data), data)
    print 'datam.shape=',datam.shape

    
    # Try to output data here?
    ttlength = datam.shape[0]*data.shape[1]
    print 'ttlength',ttlength
    #to_save = np.vstack((latitude.reshape((ttlength)),longitude.reshape((ttlength)),time2.reshape((ttlength)),datam.reshape((ttlength))))
    to_save = np.vstack((latitude.reshape((ttlength)),\
    longitude.reshape((ttlength)),\
    time2.reshape((ttlength)),\
    datam.reshape((ttlength))))
    to_save = np.swapaxes(to_save,0,1)
    print 'to_save.shape',to_save.shape    
    to_save = to_save[~np.isnan(to_save).any(axis=1)]
    
    print 'to_save.shape',to_save.shape
    np.savetxt(hdffile[:-4]+".txt",to_save)
    #np.savetxt(hdffile[:-4]+".txt", to_save, fmt='%10.5f , %10.5f , %10.5f , %10.5f')
    return to_save

if __name__ == "__main__":

    # If a certain environment variable is set, look there for the input
    # file, otherwise look in the current directory.
    
    #fhand = open('list_of_files.txt')
    fhand = open('list_of_files_DOAS.txt')    
    #DirURL = 'http://aura.gesdisc.eosdis.nasa.gov/data/Aura_OMI_Level2/OMTO3.003/2015/275/' #
    DirURL = 'http://aura.gesdisc.eosdis.nasa.gov/data/Aura_OMI_Level2/OMDOAO3.003/2015/275/' #DOAS
    #DirURL = fhand.readline() # First line to be downloading URL
    print 'DirURL=',DirURL
    #stacking = False
    for line in fhand:
        c = line.split()
        try:
            if c[0] == '[':
                hdffile = c[2]
                print 'hdffile=',hdffile
                aa = urlretrieve(DirURL+hdffile,hdffile)
                print aa    
            #    while dl:
            #        aa = urlretrieve(DirURL+c[2],c[2])
            #        print aa
            #        dl = False
            else:
                continue
        except:
            break        
        #hdffile = 'OMI-Aura_L2-OMTO3_2015m1002t0123-o59645_v003-2015m1002t074907.he5'
        plt.close('all')
        ts2 = run(hdffile)
        try:
            ts = np.vstack((ts,ts2))
        except:
            ts = ts2
        #if ~stacking:
        #    ts = run(hdffile)
        #    stacking = True
        #else:
        #    ts = np.vstack((ts,run(hdffile)))
        
        # --- Do some simple statistics ---
        print 'Total number of recorded values:',ts.shape[0]
        print 'Number of -ve values:',np.sum(ts[:,3]<0)
        print 'Number of values<100:',np.sum(ts[:,3]<100)
        print 'Number of values>900:',np.sum(ts[:,3]>900)
        
    print 'eventually, shape of ts=',ts.shape    
    #np.savetxt("Oct2_2015_ColumnAmountO3.txt", ts, fmt='%10.5f , %10.5f , %10.5f , %10.5f')
    np.savetxt("Oct2_2015_DOAS_ColumnAmountO3.txt", ts, fmt='%10.5f , %10.5f , %10.5f , %10.5f')
