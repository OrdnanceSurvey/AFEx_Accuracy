# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 16:28:07 2019

@author: Jrainbow
"""

import fiona 
import rasterio
import rasterio.mask
import os

groundtruth_shape = r"U:\EOResearch\Ecopia\Topo\buildings_gt100sqft.shp"
comparison_shape = r"U:\EOResearch\Ecopia\Aerial_27700\Classes\ecopia_buildings.shp"

groundtruth_folder = os.path.dirname(groundtruth_shape)
comparison_folder = os.path.dirname(comparison_shape)

groundtruth_raster_path = os.path.join(groundtruth_folder, "rasterized")
comparison_raster_path = os.path.join(comparison_folder, "rasterized")
if not os.path.exists(groundtruth_raster_path):
    os.mkdir(groundtruth_raster_path)
else:
    print("Folder already exists")
if not os.path.exists(comparison_raster_path):
    os.mkdir(comparison_raster_path)
else:
    print("Folder already exists")

# RASTERIZE VECTOR FILE
with fiona.open(groundtruth_shape, "r") as shapefile:
    features = [feature["geometry"] for feature in shapefile]


with rasterio.open(os.path.join(groundtruth_raster_path, "buildings.tif")) as src:
    out_image, out_transform = rasterio.mask.mask(src, features, crop=True)
    out_meta = src.meta.copy()
    
out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
with rasterio.open(os.path.join(groundtruth_raster_path, "buildings.tif")) as dest:
    dest.write(out_image)











