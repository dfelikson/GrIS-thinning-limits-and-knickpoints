#!/usr/bin/env python

import numpy as np

from netCDF4 import Dataset
from matplotlib import pyplot as plt

# Setup
netcdf_dir = 'netcdfs'
flowlines = ['flowline03', 'flowline04', 'flowline05', 'flowline06', 'flowline07', 'flowline08']

# Processing
#ds = Dataset(netcdf_dir + '/glaciera199.nc', 'r')
ds = Dataset(netcdf_dir + '/glacier0001.nc', 'r')

fig, ax = plt.subplots(2, 1, sharex=True)
for flowline in flowlines:
   d = ds[flowline]['d'][:]

   s = ds[flowline]['geometry']['surface']['GIMP']['nominal']['h_mvavg'][:]
   b = ds[flowline]['geometry']['bed']['BedMachine']['nominal']['h_mvavg'][:]
   ax[0].plot(d/1000., s, 'b')
   ax[0].plot(d/1000., b, 'k')

   if ds[flowline]['knickpoint']['has_knickpoint'][:]:
      knickpoint_start_idx = np.where(d == ds[flowline]['knickpoint']['knickpoint_start_d'][:])[0][0]
      knickpoint_end_idx = np.where(d == ds[flowline]['knickpoint']['knickpoint_end_d'][:])[0][0]
      ax[0].plot(d[knickpoint_start_idx:knickpoint_end_idx]/1000., b[knickpoint_start_idx:knickpoint_end_idx], 'r')

   Pe = ds[flowline]['Pe']['GIMP']['nominal'][:]
   ax[1].plot(d/1000., Pe, 'k')
   
   idx = np.where(Pe >= 3.)[0]
   if len(idx) > 0:
      ax[1].plot(d[idx[0]]/1000., Pe[idx[0]], 'gd', markersize=8, linewidth=1., zorder=10.)

ax[1].plot(d/1000., 3 * np.ones(d.shape), 'r--', zorder=-10)

#plt.title()
ax[0].set_ylabel('bed elevation (m)')
ax[1].set_ylabel('Pe')
ax[0].set_ylim((-1000, 3000))
ax[1].set_ylim((-5,10))
ax[1].set_xlabel('distance from terminus (km)')
plt.xlim(0, 200)
plt.show()
import pdb; pdb.set_trace()

