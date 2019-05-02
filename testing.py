# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 14:08:37 2019

@author: Jrainbow
"""

from guyana_accuracy import GuyanaTile
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
import numpy as np
from tqdm import tqdm



mytile = GuyanaTile('GT1033', 'buildings')

#cf_raster = mytile.read_classified_raster()
cf_raster = mytile.read_classified_raster(appendage='HACK_RGB1', extras='_epoch50')
gt_raster = mytile.read_groundtruth_raster()[:3333,:3333]

#plt.imshow(cf_raster)
plt.imshow(gt_raster)

labelled = label(gt_raster)
numBuildings = len(np.unique(labelled))
print("{} buildings present".format(numBuildings))

#for i in range(numBuildings):
#    region = gt_raster
props = regionprops(labelled)
blank = np.zeros_like(gt_raster)
buildingsFound = 0
for seg in tqdm(range(len(np.unique(labelled)))):
    region = np.where(labelled == seg)
    if np.isin(cf_raster[region], 255).any():
#        overlap = (cf_raster[region] == 1).sum()
#        mismatch = (cf_raster[region] == 0).sum()
        buildingsFound += 1
##        if mismatch < 500:
#        if 5 * overlap > mismatch and mismatch < 2000:
#            blank[region] = 1   
print("{} buildings (at least partially) found by algorithm".format(buildingsFound))









