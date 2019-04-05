# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 11:35:27 2019

@author: Jrainbow
"""

from skimage.io import imread
import numpy as np


groundtruth_raster_path = r"U:\EOResearch\Ecopia\Topo\AllRasterized\topo_rasterized_building_clipped.tif"
comparison_raster_path = r"U:\EOResearch\Ecopia\Aerial_27700\AllRasterized\ecopia_rasterized_building_clipped.tif"

gt = imread(groundtruth_raster_path)
cp = imread(comparison_raster_path)






