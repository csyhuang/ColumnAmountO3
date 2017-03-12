import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from netCDF4 import Dataset
import urllib
import re
from OMI_L2_OMNO2_ColumnAmountO3_SWATHS import run

DirURL = 'http://aura.gesdisc.eosdis.nasa.gov/data/Aura_OMI_Level2/OMDOAO3.003/2015/275/' #DOAS

# Downloading all .he5 files from the web
html = urllib.urlopen(DirURL).read()
links = re.findall('href="(OMI-Aura_L2.*?)"', html)
for i in np.arange(0,len(links),4):
    hdffile = links[i]
    print hdffile
    dl = urllib.urlretrieve(DirURL+hdffile,hdffile) # This is the right line
   
    # convert hdffile to .txt
    #ts2 = OMI_L2_OMNO2_ColumnAmountO3_SWATHS.run(hdffile)
    run(hdffile)
    #try:
    #    ts = np.vstack((ts,ts2))
    #except:
    #    ts = ts2

# --- Do some simple statistics ---
#print 'Total number of recorded values:',ts.shape[0]
#print 'Number of -ve values:',np.sum(ts[:,3]<0)
#print 'Number of values<100:',np.sum(ts[:,3]<100)
#print 'Number of values>900:',np.sum(ts[:,3]>900)
#
#print 'eventually, shape of ts=',ts.shape
#np.savetxt("Oct2_2015_DOAS_ColumnAmountO3.txt", ts, fmt='%10.5f , %10.5f , %10.5f , %10.5f')
#
