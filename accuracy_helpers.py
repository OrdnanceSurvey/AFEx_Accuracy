# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 10:51:48 2019

@author: Jrainbow
"""
import numpy as np
import pandas as pd

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


