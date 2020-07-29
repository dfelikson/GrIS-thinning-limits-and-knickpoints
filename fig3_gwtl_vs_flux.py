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

gwtl_flux_plot_filename = 'fig3a.pdf'


# Processing
glaciers_all = glob.glob(netcdf_dir + '/glacier????.nc')

branches = dict()
for glacier in glaciers_all:
   if glacier.split('/')[-1][7].isalpha():
      branches['0' + glacier.split('/')[-1][8:11]] = [branch for branch in glaciers_all if branch.split('/')[-1][8:11] == glacier.split('/')[-1][8:11]]
   else:
      branches['0' + glacier.split('/')[-1][8:11]] = [glacier]

gwtl_list = list()
flux_list = list()
basins_list = list()
for parent in sorted(branches.keys()):
   print(parent)

   PeX = dict()
   PeY = dict()
   PeD = dict()

   flux = 0.

   for branch in branches[parent]:
      ds = Dataset(branch, 'r')
      basin = float('{:3.1f}'.format(np.asarray(ds['basin'][:])[()]))
      flux = flux + np.asarray(ds['flux'][:])[()]

      flowline_groups, iteration_list = utils.get_flowline_groups(ds)
      for flowline_group, iteration in zip(flowline_groups, iteration_list):
         x = flowline_group['x'][:]
         y = flowline_group['y'][:]
         d = flowline_group['d'][:]

         Pe1 = flowline_group['Pe']['AERO']['nominal'][:]
         Pe2 = flowline_group['Pe']['GIMP']['nominal'][:]
         
         # Find where Pe=3 along this flowline
         ID = 'glacier' + branch.split('/')[-1][7:11] + '_' + flowline_group.name.replace('flowline','') + '_' + iteration
         PeX[ID], PeY[ID], PeD[ID] = utils.get_Pe3(ID, x, y, d, Pe1, Pe2, PeThreshold=3.0)
      
      ds.close()

   # Calculate glacier-wide thinning limit
   statsDict = utils.get_stats(PeX, PeY, PeD)
   gwtl = utils.glacier_wide_thinning_limit(statsDict)

   gwtl_list.append(gwtl/1000.)
   flux_list.append(flux)
   basins_list.append(basin)


gwtl_norm = gwtl_list / np.max(gwtl_list)
flux_norm = flux_list / np.max(flux_list)
distance = np.sqrt( gwtl_norm**2 + flux_norm**2 )

basins_list = np.array(basins_list)
terrain_idx = np.array([1 if b in basins_mtn else 2 for b in basins_list])

# Establish colors
cmap = sequential.Reds_3.mpl_colormap
cmap = plt.get_cmap('hot_r')
cmap_start = 0.20
cmap_end   = 1.00;
f = scipy.interpolate.interp1d( (0., np.max(distance)), (cmap_start, cmap_end))
colors = np.array([f(d) for d in distance])

# Colorbar figure
gradient = np.linspace(cmap_start, cmap_end, 256)
gradient = np.vstack((gradient, gradient))
fig = plt.figure(figsize=(8, 1))
ax = fig.add_axes([0.05, 0.5, 0.9, 0.45])
ax.imshow(gradient, aspect='auto', cmap=cmap, vmin=0., vmax=1.)
ax.set_axis_off()
plt.savefig('GrIS_susceptibility_colorbar.png', bbox_inches='tight', dpi=300)
plt.close()

# Scatter plot
fig, ax = plt.subplots(figsize=[5, 4])
ax.scatter(np.array(flux_list)[terrain_idx==1], np.array(gwtl_list)[terrain_idx==1], marker='s', c=colors[terrain_idx==1], edgecolors='k', cmap=cmap, vmin=0., vmax=1.)
ax.scatter(np.array(flux_list)[terrain_idx==2], np.array(gwtl_list)[terrain_idx==2], marker='o', c=colors[terrain_idx==2], edgecolors='k', cmap=cmap, vmin=0., vmax=1.)

# Contours
xlim = plt.xlim()
ylim = plt.ylim()
x = np.arange(0.0, np.max(flux_list), 1.0)
y = np.arange(0.0, np.max(gwtl_list), 1.0)
X, Y = np.meshgrid(x, y)
x = np.linspace(0.0, np.max(flux_norm), len(x))
y = np.linspace(0.0, np.max(gwtl_norm), len(y))
X_norm, Y_norm = np.meshgrid(x, y)
Z = np.sqrt( X_norm**2 + Y_norm**2 )
ax.contour(X, Y, Z, colors='k', linewidths=0.25, zorder=-1)
plt.xlim(xlim)
plt.ylim(ylim)

# # X marks the spot
# for id in x_marks_the_spot:
#    idx = centerline_ids_list.index(id)
#    ax.plot(glacier_flux_list[idx], gwtl_list[idx], 'wx', markeredgewidth=0.5)

ax.set_xlabel('flux (km$^3$/yr)')
ax.set_ylabel('glacier-wide thinning limit (km)')

plt.savefig(gwtl_flux_plot_filename, bbox_inches='tight')
