#!/usr/bin/env python

import numpy as np
import glob

from netCDF4 import Dataset

from moving_average import moving_average

import utils
from matplotlib import pyplot as plt

# Setup
netcdf_dir = 'netcdfs'
flowlines = ['flowline03', 'flowline04', 'flowline05', 'flowline06', 'flowline07', 'flowline08']

basins_gtl = [1.2, 1.3, 2.2, 3.1, 3.2, 3.3, 4.1, 4.3, 5.0, 6.1, 7.2]
basins_mtn = [1.1, 1.4, 2.1, 4.2, 6.2, 7.1, 8.1, 8.2]

# Processing
for ncfile in glob.glob(netcdf_dir + '/glacier????.nc'):
   print(ncfile)
   ds = Dataset(ncfile, 'r')
   basin = np.asarray(ds['basin'][:])[()]

   glacier = ncfile.split('/')[-1].split('.')[0]
   
   for flowline in flowlines:
      if flowline in ds.groups.keys():
         d = ds[flowline]['d'][:]

         has_knickpoint = basin = np.asarray(ds[flowline]['knickpoint']['has_knickpoint'][:])[()]
         if has_knickpoint:
            
         import pdb; pdb.set_trace()

   ds.close()

   if (np.abs(basin - basins_mtn) < 0.01).any():
      basins_2categories[glacier] = 'mountainous'
   elif (np.abs(basin - basins_gtl) < 0.01).any():
      basins_2categories[glacier] = 'gentle'

import pdb; pdb.set_trace()

