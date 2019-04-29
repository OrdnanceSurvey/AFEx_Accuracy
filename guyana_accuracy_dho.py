# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 13:12:57 2019

@author: Jrainbow
"""

import skimage
from skimage.io import imread
import numpy as np
import os
from glob import glob
import pandas as pd

# Global Variables
global RASTER_DIR 
RASTER_DIR = r"O:\Guyana\shapefiles_test\rasterized"
global CLASSIFIED_DIR
CLASSIFIED_DIR = r"O:\tiled"

from accuracy_helpers import normalize, calc_averages, clip, accuracy_metrics

class GuyanaTile:
    STRIDE = 200
    SIZE = 400
    NORM = 3
    def __init__(self, code, class_):
        self.__code = code
        self.__class = class_
        self.__raster_dir = RASTER_DIR
        self.__classified_dir = CLASSIFIED_DIR
        
    def get_raster_path(self):
        raster_path = os.path.join(self.__raster_dir, '{}_{}.tif'.format(self.__code, self.__class))
        return raster_path
    
    def read_groundtruth_raster(self):
        raster_path = self.get_raster_path()
        raster = imread(raster_path)
        raster = self.norm_image(raster)
        return raster
    
    def get_classified_folder(self, appendage='HACK_IRG1'):
        TILE_DIR = os.path.join(self.__classified_dir, "{}_{}".format(self.__code, appendage))
        return TILE_DIR
    
    def get_classified_raster_path(self, appendage='HACK_IRG1', extras=''):
        norm = GuyanaTile.NORM
        TILE_DIR = self.get_classified_folder(appendage=appendage)
        OUTPUT_DIR = os.path.join(TILE_DIR, '{}_masks{}'.format(self.__class, str(extras)))
        raster_path = os.path.join(OUTPUT_DIR, '{}_normalized_{}.tif'.format(self.__code, str(norm)))
        return raster_path
    
    def calc_limits(self,raster):
        h, w = raster.shape
        w = GuyanaTile.STRIDE * int(w / GuyanaTile.STRIDE)
        h = GuyanaTile.STRIDE * int(h / GuyanaTile.STRIDE)
        return h, w
        
    def norm_image(self, img):
        im_height, im_width = self.calc_limits(img)
        h0 = GuyanaTile.STRIDE
        h1 = im_height - GuyanaTile.STRIDE
        w0 = GuyanaTile.STRIDE
        w1 = im_width - GuyanaTile.STRIDE
        if h0 > 0 and w0 > 0 and h1 > h0 and w1 > w0:
            img = img[h0: h1, w0: w1]
        else:
            print("raster data too small to clip.  Setting to zero")
            img = img[0: 0, 0: 0]
        return img
                
    def read_classified_raster(self, appendage='HACK_IRG1', extras=''):
        norm = GuyanaTile.NORM
        raster_path = self.get_classified_raster_path(appendage=appendage, extras=extras)
        raster = imread(raster_path)
        if norm != 0:
            raster = self.norm_image(raster)      
        return raster
           
    def calc_stats(self, appendage='HACK_IRG1',extras=''):
        
        # TODO: add total number of buildings present vs total number found
    
        tp = []
        fp = []
        tn = []
        fn = []
        
        gt = self.read_groundtruth_raster()
        cf = self.read_classified_raster(appendage=appendage, extras=extras)
        
        gt_norm = normalize(gt)
        cf_norm = normalize(cf)
        
        if gt_norm.shape != cf_norm.shape:
            # Clip if necessary
            cf_norm, gt_norm = clip(cf_norm, gt_norm)
        
        gt_inv = 1 - gt_norm
        cf_inv = 1 - cf_norm
            
        a = gt_norm & cf_norm
        b = gt_inv & cf_norm
        c = cf_inv & gt_norm
        d = cf_inv & gt_inv
        
        anz = np.count_nonzero(a)
        bnz = np.count_nonzero(b)
        cnz = np.count_nonzero(c)
        dnz = np.count_nonzero(d)
        
        tp.append(anz)
        fp.append(bnz)
        fn.append(cnz)
        tn.append(dnz)

        results = pd.DataFrame({"Tile:": self.__code,
                                "Class:": self.__class,
                                "True Positives": tp,
                                "False Positives": fp,
                                "True Negatives": tn,
                                "False Negatives": fn})   
    
        accuracy = accuracy_metrics(results)
#        print(accuracy)
        
        return accuracy
    
def main():

    testTiles = ['GT2031', 'GT1033', 'GT1014']
    appendage = 'HACK_RGB1'
    class_ = 'buildings'
    extras = '_epoch100'
    frames = []
    for region in testTiles:
        print("Calculating Stats for: \t {}".format(region))
        tile = GuyanaTile(region, class_)
        tileAcc = tile.calc_stats(appendage=appendage, extras=extras)
        frames.append(tileAcc)
    
    result = pd.concat(frames)
    print(result)
    
    averages = calc_averages(result)
    
if __name__ == "__main__":
    main()    