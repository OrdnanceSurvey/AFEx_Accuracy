# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 16:28:07 2019

@author: Jrainbow
"""

import fiona 
import rasterio
import rasterio.mask
import os

#groundtruth_shape = r"U:\EOResearch\Ecopia\Topo\buildings_gt100sqft.shp"
#comparison_shape = r"U:\EOResearch\Ecopia\Aerial_27700\Classes\ecopia_buildings.shp"
#
#groundtruth_folder = os.path.dirname(groundtruth_shape)
#comparison_folder = os.path.dirname(comparison_shape)
#
#groundtruth_raster_path = os.path.join(groundtruth_folder, "rasterized")
#comparison_raster_path = os.path.join(comparison_folder, "rasterized")
#if not os.path.exists(groundtruth_raster_path):
#    os.mkdir(groundtruth_raster_path)
#else:
#    print("Folder already exists")
#if not os.path.exists(comparison_raster_path):
#    os.mkdir(comparison_raster_path)
#else:
#    print("Folder already exists")
#
## RASTERIZE VECTOR FILE
#with fiona.open(groundtruth_shape, "r") as shapefile:
#    features = [feature["geometry"] for feature in shapefile]
#
#
#with rasterio.open(os.path.join(groundtruth_raster_path, "buildings.tif")) as src:
#    out_image, out_transform = rasterio.mask.mask(src, features, crop=True)
#    out_meta = src.meta.copy()
#    
#out_meta.update({"driver": "GTiff",
#                 "height": out_image.shape[1],
#                 "width": out_image.shape[2],
#                 "transform": out_transform})
#with rasterio.open(os.path.join(groundtruth_raster_path, "buildings.tif")) as dest:
#    dest.write(out_image)




"U:\EOResearch\Ecopia\Imagery\mosaic.jpg"


# A script to rasterise a shapefile to the same projection & pixel resolution as a reference image.
from osgeo import ogr, gdal
import subprocess
from image_tiler import Tile
import skimage
import skimage.io
import matplotlib.pyplot as plt

def rasterizer(shape, output, background):

    InputVector = shape
    OutputImage = output
    
    
    mytile = Tile(tile)
    RefImage = mytile.get_image_path()
    
#    RefImage = r"X:\Imagery\Latest\SJ\{}.JPG".format(tile)
    
    gdalformat = 'GTiff'
    datatype = gdal.GDT_Byte
    burnVal = 1 #value for the output image pixels
    ##########################################################
    # Get projection info from reference image
    Image = gdal.Open(RefImage, gdal.GA_ReadOnly)
    
    # Open Shapefile
    Shapefile = ogr.Open(InputVector)
    Shapefile_layer = Shapefile.GetLayer()
    
    # Rasterise
    print("Rasterising shapefile...")
    Output = gdal.GetDriverByName(gdalformat).Create(OutputImage, Image.RasterXSize, Image.RasterYSize, 1, datatype, options=['COMPRESS=DEFLATE'])
    Output.SetProjection(Image.GetProjectionRef())
    Output.SetGeoTransform(Image.GetGeoTransform()) 
    
    # Write data to band 1
    Band = Output.GetRasterBand(1)
    Band.SetNoDataValue(0)
    gdal.RasterizeLayer(Output, [1], Shapefile_layer, burn_values=[burnVal])
    
    # Close datasets
    Band = None
    Output = None
    Image = None
    Shapefile = None
    
    # Build image overviews
    subprocess.call("gdaladdo --config COMPRESS_OVERVIEW DEFLATE "+OutputImage+" 2 4 8 16 32 64", shell=True)
    print("Done.")
    return OutputImage
#
#
#
#
#
#
#
#
