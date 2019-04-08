# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 11:35:27 2019

@author: Jrainbow
"""

from skimage.io import imread
import numpy as np
import pandas as pd


groundtruth_raster_path_road = r"U:\EOResearch\Ecopia\Topo\AllRasterized\topo_rasterized_road_clipped.tif"
comparison_raster_path_road = r"U:\EOResearch\Ecopia\Aerial_27700\AllRasterized\ecopia_rasterized_road_clipped.tif"
groundtruth_raster_path_building = r"U:\EOResearch\Ecopia\Topo\AllRasterized\topo_rasterized_building_clipped.tif"
comparison_raster_path_building = r"U:\EOResearch\Ecopia\Aerial_27700\AllRasterized\ecopia_rasterized_building_clipped.tif"

#image_dict = {"buildings": [groundtruth_raster_path_building, comparison_raster_path_building],
#              "roads": [groundtruth_raster_path_road, comparison_raster_path_road]}

image_dict = {"buildings": [comparison_raster_path_building, groundtruth_raster_path_building],
              "roads": [comparison_raster_path_road, groundtruth_raster_path_road]}



def normalize(img):
#    maxi = img.max()
    mini = img.min()
    
    # Set negatives to 0
    img[img == mini] = 0
    
    # Set positives to 1
    img[img > mini] = 1
    
    out = img.astype(np.uint8)
    return out


def calc_iou(groundtruth, comparison):

    gt = imread(groundtruth, as_gray=True)
    cp = imread(comparison, as_gray=True)
    
    gt_norm = normalize(gt)
    cp_norm = normalize(cp)
    
    a = gt_norm & cp_norm
    b = gt_norm | cp_norm
        
    anz = np.count_nonzero(a)
    bnz = np.count_nonzero(b)
    
    iou = anz / bnz
    print("Intersection over Union is {}%".format(iou * 100))
    return gt_norm, cp_norm, iou


    
def raw_matrix(image_dictionary):
    
    tp = []
    fp = []
    tn = []
    fn = []
    
    for clz in image_dictionary:
    
        gt = imread(image_dictionary[clz][0], as_gray=True)
        cp = imread(image_dictionary[clz][1], as_gray=True)
        
        gt_norm = normalize(gt)
        cp_norm = normalize(cp)
        
        gt_inv = 1 - gt_norm
        cp_inv = 1 - cp_norm
    
        a = gt_norm & cp_norm
        b = gt_inv & cp_norm
        c = cp_inv & gt_norm
        d = cp_inv & gt_inv

        anz = np.count_nonzero(a)
        bnz = np.count_nonzero(b)
        cnz = np.count_nonzero(c)
        dnz = np.count_nonzero(d)
        
        tp.append(anz)
        fp.append(bnz)
        fn.append(cnz)
        tn.append(dnz)

    results = pd.DataFrame({"Class:": list(image_dictionary.keys()),
                            "True Positives": tp,
                            "False Positives": fp,
                            "True Negatives": tn,
                            "False Negatives": fn})   

    return results     

def accuracy_metrics(raw):
    raw['Recall'] = raw['True Positives'] / (raw['True Positives'] + raw['False Negatives'])
    raw['Precision'] = raw['True Positives'] / (raw['True Positives'] + raw['False Positives'])
    raw['F1'] = 2 * (raw['Precision'] * raw['Recall']) / (raw['Precision'] + raw['Recall'])
    return raw
    
    
    
    
raw = raw_matrix(image_dict)






