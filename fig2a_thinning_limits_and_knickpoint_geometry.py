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
basins_2categories = dict()
diffs = dict()

for ncfile in glob.glob(netcdf_dir + '/glacier????.nc'):
   print(ncfile)
   ds = Dataset(ncfile, 'r')
   basin = float('{:3.1f}'.format(np.asarray(ds['basin'][:])[()]))

   glacier = ncfile.split('/')[-1].split('.')[0]
   diffs[glacier] = dict()
   
   flowline_groups, iteration_list = utils.get_flowline_groups(ds)
   for flowline_group, iteration in zip(flowline_groups, iteration_list):
      x = flowline_group['x'][:]
      y = flowline_group['y'][:]
      d = flowline_group['d'][:]

      # Get flowline length
      flowline_length = utils.getFlowlineLength(glacier, flowline_group.name.replace('flowline',''), iterID=iteration)

      Pe1 = flowline_group['Pe']['AERO']['nominal'][:]
      Pe2 = flowline_group['Pe']['GIMP']['nominal'][:]
      lastvalid = np.max( ~np.isnan(Pe1) )
      Pe = np.hstack( (Pe1[:lastvalid], Pe2[lastvalid:]) )
      geoid = flowline_group['geometry']['geoid']['h'][:]

      ID = glacier + '_' + flowline_group.name.replace('flowline','')
      _, _, PeD = utils.get_Pe3(ID, x, y, d, Pe1, Pe2)

      # Bed = sea level
      bed = flowline_group['geometry']['bed']['BedMachine']['nominal']['h_mvavg'][:]
      valid = ~np.isnan(bed)
      idx = np.where(bed[valid] > geoid[valid])[0]
      if len(idx) > 0:
         d_bed_sealevel = d[valid][np.min(idx)]
      else:
         d_bed_sealevel = flowline_length

      # Collect all data
      diffs[glacier][flowline_group.name + '_' + iteration] = (PeD - d_bed_sealevel)/1000.

   ds.close()

   if basin in basins_mtn:
      basins_2categories[glacier] = 'mountainous'
   elif basin in basins_gtl:
      basins_2categories[glacier] = 'gentle'

utils.violin_plot(diffs, basins_2categories, ['gentle', 'mountainous'], 'fig2a.pdf') #, highlight=highlight)

