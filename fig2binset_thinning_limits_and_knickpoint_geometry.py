#!/usr/bin/env python

import numpy as np
import glob

from netCDF4 import Dataset

import utils
from matplotlib import pyplot as plt

import matplotlib
matplotlib.rcParams.update({'font.size': 16})

# Setup
netcdf_dir = 'netcdfs'

basins_mtn = [1.2, 1.3, 2.2, 3.1, 3.2, 3.3, 4.1, 4.3, 5.0, 6.1, 7.2]
basins_gtl = [1.1, 1.4, 2.1, 4.2, 6.2, 7.1, 8.1, 8.2]

# Processing
knickpoint_slope_list = list()
trough_elev_list = list()
upglacier_elev_list = list()
basin_category_list = list()

for ncfile in glob.glob(netcdf_dir + '/glacier????.nc'):
   print(ncfile)
   glacier = ncfile.split('/')[-1].split('.')[0]

   ds = Dataset(ncfile, 'r')
   
   basin = float('{:3.1f}'.format(np.asarray(ds['basin'][:])[()]))
   if basin in basins_mtn:
      basin_category = 0.
   elif basin in basins_gtl:
      basin_category = 1.
   
   flowline_groups, _ = utils.get_flowline_groups(ds) 
   for flowline_group in flowline_groups:
      x = flowline_group['x'][:]
      y = flowline_group['y'][:]
      d = flowline_group['d'][:]

      has_knickpoint = np.asarray(flowline_group['knickpoint']['has_knickpoint'][:])[()]
      if has_knickpoint:
         knickpoint_slope = float(np.asarray(flowline_group['knickpoint']['knickpoint_slope'][:])[()])
         trough_elev = float(np.asarray(flowline_group['knickpoint']['mean_trough_elev'][:])[()])
         upglacier_elev = float(np.asarray(flowline_group['knickpoint']['mean_upglacier_elev'][:])[()])

         knickpoint_slope_list.append(knickpoint_slope) # radians to degrees
         trough_elev_list.append(trough_elev)
         upglacier_elev_list.append(upglacier_elev)
         basin_category_list.append(basin_category)

   ds.close()

knickpoint_slopes = np.array(knickpoint_slope_list)
trough_elevs      = np.array(trough_elev_list)
upglacier_elevs   = np.array(upglacier_elev_list)
basin_categories  = np.array(basin_category_list)

knickpoint_slope_gtl = np.median( knickpoint_slopes[basin_categories == 1.] )
knickpoint_slope_mtn = np.median( knickpoint_slopes[basin_categories == 0.] )
trough_elev_gtl = np.median( trough_elevs[basin_categories == 1.] )
trough_elev_mtn = np.median( trough_elevs[basin_categories == 0.] )
upglacier_elev_gtl = np.median( upglacier_elevs[basin_categories == 1.] )
upglacier_elev_mtn = np.median( upglacier_elevs[basin_categories == 0.] )

color1 = [0, 0.4470, 0.7410]
color2 = [0.8500, 0.3250, 0.0980]

# Plot troughs
d_trough = np.array([-20000, trough_elev_gtl / knickpoint_slope_gtl])
b_trough = trough_elev_gtl * np.ones(d_trough.shape)
plt.plot(d_trough/1000, b_trough, '-', color=color1, linewidth=2, markersize=20)
d_trough = np.array([-20000, trough_elev_mtn / knickpoint_slope_mtn])
b_trough = trough_elev_mtn * np.ones(d_trough.shape)
plt.plot(d_trough/1000, b_trough, '-', color=color2, linewidth=2, markersize=20)

# Plot knickpoints
d_knickpoint = np.array([trough_elev_gtl / knickpoint_slope_gtl, upglacier_elev_gtl / knickpoint_slope_gtl])
b_knickpoint = knickpoint_slope_gtl*d_knickpoint
plt.plot(d_knickpoint/1000, b_knickpoint, '-', color=color1, linewidth=2, markersize=20)
d_knickpoint = np.array([trough_elev_mtn / knickpoint_slope_mtn, upglacier_elev_mtn / knickpoint_slope_mtn])
b_knickpoint = knickpoint_slope_mtn*d_knickpoint
plt.plot(d_knickpoint/1000, b_knickpoint, '-', color=color2, linewidth=2, markersize=20)

# Plot upglacier
d_upglacier = np.array([upglacier_elev_gtl / knickpoint_slope_gtl, 40000])
b_upglacier = upglacier_elev_gtl * np.ones(d_upglacier.shape)
plt.plot(d_upglacier/1000, b_upglacier, '-', color=color1, linewidth=2, markersize=20)
d_upglacier = np.array([upglacier_elev_mtn / knickpoint_slope_mtn, 40000])
b_upglacier = upglacier_elev_mtn * np.ones(d_upglacier.shape)
plt.plot(d_upglacier/1000, b_upglacier, '-', color=color2, linewidth=2, markersize=20)

plt.xlabel('distance along flow (km)')
plt.ylabel('elevation (m)')
plt.title('prototypical knickpoint geometry')
plt.ylim(-400, 1100)

plt.savefig('fig2binset.pdf', bbox_inches='tight')

