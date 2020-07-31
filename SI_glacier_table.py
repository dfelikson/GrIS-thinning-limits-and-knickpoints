#!/usr/bin/env python


# For offline plots ...
import matplotlib
#matplotlib.use('Agg')

import os, sys, glob

from netCDF4 import Dataset

import scipy
import numpy as np
import matplotlib.pyplot as plt
from palettable.colorbrewer import sequential

import utils


# Setup
netcdf_dir = 'netcdfs'

basins_mtn = [1.2, 1.3, 2.2, 3.1, 3.2, 3.3, 4.1, 4.3, 5.0, 6.1, 7.2]
basins_gtl = [1.1, 1.4, 2.1, 4.2, 6.2, 7.1, 8.1, 8.2]

csv_output_file = 'SI_glacier_spreadsheet.csv'


# Processing
glaciers_all = glob.glob(netcdf_dir + '/glacier????.nc')

branches = dict()
for glacier in glaciers_all:
   if glacier.split('/')[-1][7].isalpha():
      branches['0' + glacier.split('/')[-1][8:11]] = [branch for branch in glaciers_all if branch.split('/')[-1][8:11] == glacier.split('/')[-1][8:11]]
   else:
      branches['0' + glacier.split('/')[-1][8:11]] = [glacier]

for parent in sorted(branches.keys()):

   PeX = dict()
   PeY = dict()
   PeD = dict()

   flux = 0.

   for branch in branches[parent]:
      ds = Dataset(branch, 'r')
      basin = float('{:3.1f}'.format(np.asarray(ds['basin'][:])[()]))
      flux = flux + np.asarray(ds['flux'][:])[()]
      name = ds.description

      flowline_groups, iteration_list = utils.get_flowline_groups(ds)
      knickpoint_slope_flowlines = list()
      has_knickpoint_flowlines = list()
      for flowline_group, iteration in zip(flowline_groups, iteration_list):
         x = flowline_group['x'][:]
         y = flowline_group['y'][:]
         d = flowline_group['d'][:]

         Pe1 = flowline_group['Pe']['AERO']['nominal'][:]
         Pe2 = flowline_group['Pe']['GIMP']['nominal'][:]
         
         # Find where Pe=3 along this flowline
         ID = 'glacier' + branch.split('/')[-1][7:11] + '_' + flowline_group.name.replace('flowline','') + '_' + iteration
         PeX[ID], PeY[ID], PeD[ID] = utils.get_Pe3(ID, x, y, d, Pe1, Pe2, PeThreshold=3.0)
      
         # Knickpoint
         has_knickpoint = np.asarray(flowline_group['knickpoint']['has_knickpoint'][:])[()]
         if has_knickpoint:
            knickpoint_slope = float(np.asarray(flowline_group['knickpoint']['knickpoint_slope'][:])[()])
            knickpoint_slope_flowlines.append(knickpoint_slope)
         has_knickpoint_flowlines.append(has_knickpoint)
         
      ds.close()

      # Glacier-wide
      has_knickpoint_flowlines = np.array(has_knickpoint_flowlines)
      knickpoint_slope_flowlines = np.array(knickpoint_slope_flowlines)
      if len(has_knickpoint_flowlines[has_knickpoint_flowlines == 1]) / len(has_knickpoint_flowlines) > 0.5:
         has_knickpoint_str = 'has knickpoint'
         knickpoint_slope = np.median(np.array(knickpoint_slope_flowlines)) * 180/np.pi # radians to degrees
      else:
         has_knickpoint_str = 'no'
         knickpoint_slope = np.nan

   # Calculate glacier-wide thinning limit
   statsDict = utils.get_stats(PeX, PeY, PeD)
   gwtl = utils.glacier_wide_thinning_limit(statsDict)

   print('{:s}, {:s}, {:3.1f}, {:6.1f}, {:6.1f}, {:s}, {:6.3f}\n'.format(parent, name, basin, gwtl/1000., flux, has_knickpoint_str, knickpoint_slope))


