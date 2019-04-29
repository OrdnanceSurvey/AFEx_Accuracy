# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 14:23:52 2019

@author: Jrainbow
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 16:32:24 2019

@author: Jrainbow
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 11:14:10 2019

@author: Jrainbow
"""

import numpy as np
from skimage.io import imread, imsave
import matplotlib.pyplot as plt
import pandas as pd
import re
from glob import glob
import os

# Stats for Guyana mosaic saved at "U:\EOResearch\Guyana\Mosaic\mosaic_stats.csv"

def calc_stats(image, lower_percentile, upper_percentile, channels_first=True):
    """
    Calculates the mean and standard deviation of each channel of image
    """
    print("Calculating Stats...")
    if channels_first:    
        channels = [i for i in range(image.shape[0])]       
        means = [np.mean(image[channel,:,:]) for channel in range(image.shape[0])]
        stds = [np.std(image[channel,:,:]) for channel in range(image.shape[0])]
        stretches = [np.percentile(image[channel,:,:], [upper_percentile, lower_percentile]) for channel in range(image.shape[0])]
    else:
        print("Make channels first!")
    print("Calculated Stats.")
    return channels, means, stds, stretches

def gaussian_norm(band, mean, std):
    """
    Normalizes a single image channel about Gaussian distribution
    """
    print("Normalizing about 0...")
    result = (band - mean) / std
    print("Normalized.")
    return result

def clip(arr, min_thresh, max_thresh):
    """
    Clips all values to lie within prescribed range
    """
    print("Clipping upper and lower values...")
    # remove maxes
    size = arr.size
    uppers = np.count_nonzero(arr > max_thresh)
    lowers = np.count_nonzero(arr < min_thresh)
    arr[arr > max_thresh] = max_thresh
    # remove mins
    arr[arr < min_thresh] = min_thresh 
    print("Clipped. \n Percentage clipped from top: \t\t {} \n Percentage clipped from bottom: \t {}".format(100 * (uppers / size), 100 * (lowers / size)))    
    return arr

def linear_percent_stretch(arr, val_lower, val_upper):
    """
    Clips all values above the top (100 - val) % and below the bottom (val) %
    Lower val_upper brightens light regions
    Higher val_lower darkens shadows
    """
    upper_thresh, lower_thresh = np.percentile(arr, [val_upper, val_lower])
    print("Clipping upper and lower values...")
    # remove maxes
    size = arr.size
    uppers = np.count_nonzero(arr > upper_thresh)
    lowers = np.count_nonzero(arr < lower_thresh)
    arr[arr > upper_thresh] = upper_thresh
    # remove mins
    arr[arr < lower_thresh] = lower_thresh 
    print("Clipped. \n Percentage clipped from top: \t\t {} \n Percentage clipped from bottom: \t {}".format(100 * (uppers / size), 100 * (lowers / size)))    
    return arr

def linear_stretch(arr, val_lower, val_upper):
    """
    Clips all values above the absolute value val_upper to val_upper and all values below the \
    absolute val_lower to val_lower
    """
    print("Clipping upper and lower values...")
    # remove maxes
    size = arr.size
    uppers = np.count_nonzero(arr > val_upper)
    lowers = np.count_nonzero(arr < val_lower)
    arr[arr > val_upper] = val_upper
    # remove mins
    arr[arr < val_lower] = val_lower 
    print("Clipped. \n Percentage clipped from top: \t\t {} \n Percentage clipped from bottom: \t {}".format(100 * (uppers / size), 100 * (lowers / size)))    
    return arr
    
    
def convert_to_8_bit(arr):
    """
    Coerce result of single channel into 8-bit array
    """
    print("Converting to 8-bit")
    mini = arr.min()
    maxi = arr.max()
    result = (255 * ((arr - mini) / (maxi - mini))).astype(np.uint8)
    print("Converted to 8-bit")
    return result

def extract_georef(img_path):
    """
    Find the geotransform metadata of the original raster
    """
    from osgeo import gdal
#    src_filename = r"U:\EOResearch\Guyana\Imagery\OrderedPriority\1_GT2031.tif"
    src_filename = img_path
    
    crd_dataset = gdal.Open(src_filename)
    gt = crd_dataset.GetGeoTransform()
    return gt

def create_geotiff(arr, original_image_path, new_image_path):
    """
    Geo-encodes image array to the region filled by the original raster file and writes this to file
    """
    from osgeo import gdal, osr
    # find shape of desired raster GeoTiff
    height, width, channels = arr.shape
    
    # create destination dataset
    dst_ds = gdal.GetDriverByName('GTiff').Create(new_image_path, width, height, 3, gdal.GDT_Byte)
    
    # find geocoding from original image
    gt = extract_georef(original_image_path)
    
    dst_ds.SetGeoTransform(gt)    # specify coords
    srs = osr.SpatialReference()            # establish encoding
    srs.ImportFromEPSG(32621)                # WGS84 lat/long
    dst_ds.SetProjection(srs.ExportToWkt()) # export coords to file
    dst_ds.GetRasterBand(1).WriteArray(arr[:,:,0])   # write r-band to the raster
    dst_ds.GetRasterBand(2).WriteArray(arr[:,:,1])   # write g-band to the raster
    dst_ds.GetRasterBand(3).WriteArray(arr[:,:,2])   # write b-band to the raster
    dst_ds.FlushCache()                     # write to disk
    dst_ds = None
    
    print("Written GeoTIFF") 
        

if __name__ == '__main__':   
    
#    img_path = r"U:\EOResearch\Guyana\Imagery\OrderedPriority\1_GT2031.tif"
    subset = 'Train'
    subset_path = r"U:\EOResearch\Guyana\Imagery\{}\8band".format(subset)
    tile_list = [os.path.basename(os.path.normpath(tile)).split('.')[0] for tile in glob('{}\*.tif'.format(subset_path))]
    for tile in tile_list:
#    tile = "GT2050"
        print("Tile: {}".format(tile))
        img_path = r"U:\EOResearch\Guyana\Imagery\{}\8band\{}.tif".format(subset, tile)
        print("Loading image...")
        img = imread(img_path)
        print("Image loaded.")
    
        # Calculate Global Stats
        stats = pd.read_csv(r"U:\EOResearch\Guyana\Mosaic\mosaic_stats.csv")
        channels = stats['Band']
        means = stats['Mean']
        stds = stats['Std']
        stretches = stats['1-98% Stretch Limits']
        
    
        # Choose particular bands
        # IRG is [6,4,2], RGB is [4,2,1]
    #    bands = [4,2,1]
        bands = [6,4,2]
        out_img = []
        for band in bands:
    #        band = 5
            channel, mean, std = img[band, :, :], means[band], stds[band]
            stretch_str = stretches[band]
            stretch_list = re.findall(r'\d+', stretch_str)
            stretch = list(map(int, stretch_list))
            
            norm = gaussian_norm(channel, mean, std)
            stretch_norm = (stretch - mean) / std
            
            # Clip top and bottom values
            min_thresh = -1
            max_thresh = 1
    #        stretched = linear_percent_stretch(norm, 1, 98)
    #        works better for RGB
            stretched = linear_stretch(norm, stretch_norm[1], stretch_norm[0] + 0.5)
    #        stretched = linear_stretch(norm, stretch_norm[1], stretch_norm[0])
            
            # Coerce to 8-bit
            output = convert_to_8_bit(stretched)
            out_img.append(output)
        out_img = np.array(out_img)
        channels_last = np.moveaxis(out_img, 0, -1)
        
    #    out_path = r"U:\EOResearch\Guyana\Mosaic\GT2031_RGB_test.tif"
        out_path = r"U:\EOResearch\Guyana\Imagery\{}\IRG\{}_05.tif".format(subset, tile)
        
        create_geotiff(channels_last, img_path, out_path)
        
            
    #        # Plot
    #        fig, ax = plt.subplots(1,1, figsize=(20,20))
    #        ax.imshow(output)
        
    
        