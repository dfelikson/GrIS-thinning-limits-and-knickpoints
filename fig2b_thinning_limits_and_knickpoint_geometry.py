#!/usr/bin/env python

import numpy as np
import glob

from netCDF4 import Dataset

import utils
from matplotlib import pyplot as plt

# Setup
netcdf_dir = 'netcdfs'

basins_mtn = [1.2, 1.3, 2.2, 3.1, 3.2, 3.3, 4.1, 4.3, 5.0, 6.1, 7.2]
basins_gtl = [1.1, 1.4, 2.1, 4.2, 6.2, 7.1, 8.1, 8.2]

# Processing
knickpoint_slope_list = list()
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

         knickpoint_slope_list.append(knickpoint_slope * 180./np.pi) # radians to degrees
         basin_category_list.append(basin_category)

   ds.close()

knickpoint_slopes = np.array(knickpoint_slope_list)
basin_categories  = np.array(basin_category_list)

bin_edges = np.arange(0, 15, 0.3)

color1 = [0, 0.4470, 0.7410]
color2 = [0.8500, 0.3250, 0.0980]
plt.hist(knickpoint_slopes[basin_categories == 0.], bins=bin_edges, density=False, facecolor=color1, edgecolor=color1, linewidth=2, alpha=0.25, histtype='stepfilled', label='gentle')
plt.hist(knickpoint_slopes[basin_categories == 1.], bins=bin_edges, density=False, facecolor=color2, edgecolor=color2, linewidth=2, alpha=0.25, histtype='stepfilled', label='mountainous')
plt.xlabel('knickpoint slope (deg)')
plt.ylabel('number of flowlines')
plt.legend()
plt.savefig('fig2b.pdf', bbox_inches='tight')

