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

basins_mtn = [1.2, 1.3, 2.2, 3.1, 3.2, 3.3, 4.1, 4.3, 5.0, 6.1, 7.2]
basins_gtl = [1.1, 1.4, 2.1, 4.2, 6.2, 7.1, 8.1, 8.2]

# Processing
basins_2categories = dict()
diffs = dict()

for ncfile in glob.glob(netcdf_dir + '/glacier000?.nc'):
   print(ncfile)
   ds = Dataset(ncfile, 'r')
   basin = np.asarray(ds['basin'][:])[()]

   glacier = ncfile.split('/')[-1].split('.')[0]
   diffs[glacier] = dict()
   
   for flowline in flowlines:
      if flowline in ds.groups.keys():
         d = ds[flowline]['d'][:]
         Pe1 = ds[flowline]['Pe']['AERO']['nominal'][:]
         Pe2 = ds[flowline]['Pe']['GIMP']['nominal'][:]
         lastvalid = np.max( ~np.isnan(Pe1) )
         Pe = np.hstack( (Pe1[:lastvalid], Pe2[lastvalid:]) )
         geoid = ds[flowline]['geometry']['geoid']['h'][:]

         dh = ds[flowline]['dh']['AERO-Arctic']['nominal']['dh'][:]
         dh1 = ds[flowline]['dh']['GIMP-Arctic']['nominal']['dh'][:]

         dhavg, dhstddev = moving_average(d, dh, 20)
         dhmax = np.nanmin(dhavg)
         dhpercent = 100.0 * (dhavg/dhmax)

         dhthinning = np.where(dhavg < 0, dhavg, np.nan)
         dhcumtotal = np.nansum(dhthinning)
         dhcumsum = np.cumsum(np.where(~np.isnan(dhthinning), dhthinning, 0))
         dhcumpercent = 100.0 * (dhcumsum / dhcumtotal)

         # Find where unit volume loss is 93%
         dhcumpercentThreshold = 93.
         idx = np.where(dhcumpercent >= dhcumpercentThreshold)[0]
         if len(idx) > 0:
            d_threshold = d[np.min(idx)]
         else:
            d_threshold = np.nan

         # Bed = sea level
         bed = ds[flowline]['geometry']['bed']['BedMachine']['nominal']['h_mvavg'][:]
         valid = ~np.isnan(bed)
         idx = np.where(bed[valid] > geoid[valid])[0]
         if len(idx) > 0:
            d_bed_sealevel = d[valid][np.min(idx)]
         else:
            d_bed_sealevel = np.nan

         # Collect all data
         diffs[glacier][flowline] = (d_threshold-d_bed_sealevel)/1000.

   ds.close()

   if (np.abs(basin - basins_mtn) < 0.01).any():
      basins_2categories[glacier] = 'mountainous'
   elif (np.abs(basin - basins_gtl) < 0.01).any():
      basins_2categories[glacier] = 'gentle'

utils.violin_plot(diffs, basins_2categories, ['gentle', 'mountainous'], 'fig2.pdf') #, highlight=highlight)

