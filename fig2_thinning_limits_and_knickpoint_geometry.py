#!/usr/bin/env python

import numpy as np
import glob

from moving_average import moving_average

from netCDF4 import Dataset
from matplotlib import pyplot as plt

# Setup
netcdf_dir = 'netcdfs'
flowlines = ['flowline03', 'flowline04', 'flowline05', 'flowline06', 'flowline07', 'flowline08']


# Processing
d_threshold_list = list()
d_bed_sealevel_list = list()

for ncfile in glob.glob(netcdf_dir + '/glacier0001.nc'): #glob.glob(netcdf_dir + '/*nc'):
   ds = Dataset(ncfile, 'r')
   for flowline in flowlines:
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

      d_threshold_list.append(d_threshold)

      # Bed = sea level
      bed = ds[flowline]['geometry']['bed']['BedMachine']['nominal']['h_mvavg'][:]
      valid = ~np.isnan(bed)
      idx = np.where(bed[valid] > geoid[valid])[0]
      if len(idx) > 0:
         d_bed_sealevel_list.append(d[valid][np.min(idx)])
      else:
         d_bed_sealevel_list.append(np.nan)

d_threshold = np.array(d_threshold_list)
d_bed_sealevel = np.array(d_bed_sealevel_list)

plt.plot(d_threshold, d_bed_sealevel)
plt.show()

