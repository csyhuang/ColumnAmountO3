import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from netCDF4 import Dataset
from urllib import urlretrieve

def run(FILE_NAME):
    DATAFIELD_NAME = 'ColumnAmountO3'

    nc = Dataset(FILE_NAME)
    grp = nc.groups['HDFEOS'].groups['SWATHS'].groups['OMI Column Amount O3']
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
    
    DirURL = 'http://aura.gesdisc.eosdis.nasa.gov/data/Aura_OMI_Level2/OMTO3.003/2015/275/'
    fhand = open('list_of_files.txt')
    stacking = False
    for line in fhand:
        c = line.split()
        try:
            if c[0] == '[':
                hdffile = c[2]
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
    print 'eventually, shape of ts=',ts.shape    
    np.savetxt("Oct2_2015_ColumnAmountO3.txt", ts, fmt='%10.5f , %10.5f , %10.5f , %10.5f')
