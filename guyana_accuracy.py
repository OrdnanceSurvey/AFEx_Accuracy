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

# Test tile: GT1033, GT1014, GT2031

# Global Variables
global RASTER_DIR 
RASTER_DIR = r"O:\Guyana\shapefiles_test\rasterized"
global CLASSIFIED_DIR
CLASSIFIED_DIR = r"O:\tiled"


# HELPER FUNCTIONS
def normalize(img):
    """
    Converts an image into binary form (1 when class is present)
    Input: img array
    Output: binary img array
    """

    mini = img.min()
    
    # Set negatives to 0
    img[img == mini] = 0
    
    # Set positives to 1
    img[img > mini] = 1
    
    out = img.astype(np.uint8)
    return out

def calc_averages(df):
    """
    Calculates the simple mean F1 score over each test tile and an alternative mean 
    based on the average F1 score weighted by the number of True Positives present
    Input: result dataframe from 'calc_stats'
    Output: two percentages
    """
    F1 = df['F1']
    F1_simple_average = np.mean(F1)
    
    df['weighted_F1'] = df['F1'] * df['True Positives']
    F1_weighted_average = np.sum(df['weighted_F1']) / np.sum(df['True Positives'])
    
    print("F1 Simple Average: \t {:.2f}%".format(100 * F1_simple_average))
    print("F1 Weighted Average: \t {:.2f}%".format(100 * F1_weighted_average))
    
    return F1_simple_average, F1_weighted_average

def clip(cf_raster, gt_raster):
    """
    Calculates whether the classified raster is smaller than the grountruth raster or not 
    and clips them to make sure they are the same size. TODO: what if vastly different size?
    Input: classified raster, groundtruth raster (of varying shapes)
    Output: classified raster, groundtruth raster (of identical shape)
    TODO: actually want to crop to 3200 (or nearest multiple of 400)
    """
    cf_h, cf_w = cf_raster.shape
    gt_h, gt_w = gt_raster.shape
    min_h, min_w = np.min([cf_h, gt_h]), np.min([cf_w, gt_w])
    smallest_raster = np.argmin([cf_h, gt_h])
    if smallest_raster:
        print("Groundtruth is Smaller")
        cf_raster = cf_raster[: min_h, : min_w]
    else:
        print("Classified is Smaller")
        gt_raster = gt_raster[: min_h, : min_w]
    
    return cf_raster, gt_raster

def accuracy_metrics(raw):
    """
    Adds Recall, Precision and F1 scroes to the raw_matrix above
    Input: raw_matrix
    Output: same, with extra columns for Recall, Precision and F1
    """
    
    raw['Recall'] = raw['True Positives'] / (raw['True Positives'] + raw['False Negatives'])
    raw['Precision'] = raw['True Positives'] / (raw['True Positives'] + raw['False Positives'])
    raw['F1'] = 2 * (raw['Precision'] * raw['Recall']) / (raw['Precision'] + raw['Recall'])
    return raw


class GuyanaTile:
        
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
        return raster
    
    def get_classified_folder(self, appendage='HACK_IRG1'):
        TILE_DIR = os.path.join(self.__classified_dir, "{}_{}".format(self.__code, appendage))
        return TILE_DIR
    
    def get_classified_raster_path(self, appendage='HACK_IRG1', extras='', norm=2):
        TILE_DIR = self.get_classified_folder(appendage=appendage)
        OUTPUT_DIR = os.path.join(TILE_DIR, '{}_masks{}'.format(self.__class, str(extras)))
        raster_path = os.path.join(OUTPUT_DIR, '{}_normalized_{}.tif'.format(self.__code, str(norm)))
        return raster_path
    
    def read_classified_raster(self, appendage='HACK_IRG1', extras='', norm=2):
        raster_path = self.get_classified_raster_path(appendage=appendage, extras=extras, norm=norm)
        raster = imread(raster_path)
        return raster
        
    def calc_stats(self, appendage='HACK_IRG1',extras=''):
        
        # TODO: add total number of buildings present vs total number found
    
        tp = []
        fp = []
        tn = []
        fn = []
        
        gt = self.read_groundtruth_raster()
        cf = self.read_classified_raster(appendage=appendage, extras=extras, norm=2)
        
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
    frames = []
    for region in testTiles:
        print("Calculating Stats for: \t {}".format(region))
        tile = GuyanaTile(region, class_)
        tileAcc = tile.calc_stats(appendage=appendage, extras='')
        frames.append(tileAcc)
    
    result = pd.concat(frames)
    print(result)
    
    averages = calc_averages(result)
    
if __name__ == "__main__":
    main()    