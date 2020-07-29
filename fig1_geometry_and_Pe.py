#!/usr/bin/env python

import numpy as np

import utils

from netCDF4 import Dataset
from matplotlib import pyplot as plt

# Setup
netcdf_dir = 'netcdfs'
glaciers = ['glacier0098.nc'];                  plot_dh = False; plot_filename = 'fig1a.pdf'
#glaciers = ['glaciera199.nc','glacierb199.nc']; plot_dh = True; plot_filename = 'fig1b.pdf'

fig, ax = plt.subplots(2, 1, sharex=True)
# Processing
for glacier in glaciers:
   ds = Dataset(netcdf_dir + '/' + glacier, 'r')
   
   flowline_groups, _ = utils.get_flowline_groups(ds) 
   for flowline_group in flowline_groups:
      x = flowline_group['x'][:]
      y = flowline_group['y'][:]
      d = flowline_group['d'][:]
   
      s = flowline_group['geometry']['surface']['GIMP']['nominal']['h_mvavg'][:]
      b = flowline_group['geometry']['bed']['BedMachine']['nominal']['h_mvavg'][:]
      ax[0].plot(d/1000., s, 'b')
      ax[0].plot(d/1000., b, 'k')
      
      if plot_dh:
         dh = flowline_group['dh']['AERO-Arctic']['nominal']['dh'][:]
         d_threshold = utils.get_percentUnitVol89(x, y, d, dh)
         idx = np.where(d <= d_threshold)[0]
         if len(idx) > 0:
            s_at_d_threshold = s[idx[-1]]
            ax[0].plot(d_threshold/1000., s_at_d_threshold, 'kd', markersize=8, linewidth=1., zorder=10.)
   
      if flowline_group['knickpoint']['has_knickpoint'][:]:
         knickpoint_start_idx = np.where(d == flowline_group['knickpoint']['knickpoint_start_d'][:])[0][0]
         knickpoint_end_idx = np.where(d == flowline_group['knickpoint']['knickpoint_end_d'][:])[0][0]
         ax[0].plot(d[knickpoint_start_idx:knickpoint_end_idx]/1000., b[knickpoint_start_idx:knickpoint_end_idx], 'r')
   
      Pe = flowline_group['Pe']['GIMP']['nominal'][:]
      ax[1].plot(d/1000., Pe, 'k')
      
      idx = np.where(Pe >= 3.)[0]
      if len(idx) > 0:
         ax[1].plot(d[idx[0]]/1000., Pe[idx[0]], 'gd', markersize=8, linewidth=1., zorder=10.)
   
   ds.close()

ax[1].plot(d/1000., 3 * np.ones(d.shape), 'r--', zorder=-10)
   
ax[0].set_ylabel('bed elevation (m)')
ax[1].set_ylabel('Pe')
ax[0].set_ylim((-1000, 3000))
ax[1].set_ylim((-5,10))
ax[1].set_xlabel('distance from terminus (km)')
plt.xlim(0, 200)
#plt.show()
plt.savefig(plot_filename, bbox_inches='tight')

