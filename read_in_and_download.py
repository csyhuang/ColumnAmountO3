# -*- coding: utf-8 -*-
from urllib import urlretrieve

# To read in the list_of_files.txt

DirURL = 'http://aura.gesdisc.eosdis.nasa.gov/data/Aura_OMI_Level2/OMTO3.003/2015/275/'
fhand = open('list_of_files.txt')
dl = True
for line in fhand:
    c = line.split()
    if c[0] == '[':
        print c[2]
        while dl:
            aa = urlretrieve(DirURL+c[2],c[2])
            print aa
            dl = False
    else:
        continue
