#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 13:34:18 2021

@author: hmc
"""
from PIL import Image, ImageDraw
import numpy as np
import os
import re
import yaml

def split_str(in_str):
    str = re.sub('[^a-zA-Z]', '', in_str)
    int = re.sub('[^0-9]', '', in_str)
    return str, int

def inner_convert(polygon):
    for idx, vertice in enumerate(polygon):
        polygon[idx] = tuple(vertice)
    return polygon

def poly_mask(shape, *vertices, value=np.nan):
    width, height = shape[:2]
    
    img = Image.new(mode='L', size=(width, height), color = 0)  # mode L -> 8-bit pixels
    draw = ImageDraw.Draw(img)
    for polygon in vertices:
        draw.polygon(inner_convert(polygon), fill=1, outline=1)
    
    mask = np.array(img).astype(float)
    mask[np.where(mask == 0)] = value
    return mask

class label_list():
    def __init__(self, list_path : str):
        
        if list_path == None:
            raise Exception("Insert a path of label list file")
        if os.path.isfile(list_path)!=True:
            raise Exception("Check the path of label list file")
            
        self.catlist_path = list_path
        self.sup_map = {}  # key : string name, value : integer id
        self.inv_sup_map = {}  # key : integer id, value : string name
        self.cat_map = {}
        self.inv_cat_map = {}
        self.COCO_LIKE_MAP = []
        self.make_map()
        
    def make_map(self):
        """
        COCO Basic structure : list of dictionary
          dictionary structure
            - supercategory (string)
            - id (object category id)
            - name(object)
        
        list file content rule.
        supercategory_id supercategory_string category_id category_string 
        
        example)
        0 furniture 0 chair
        0 furniture 1 bed
        1 fruits 2 apple
        2 cosmetic 3 lipstick

        with open(yaml_path, 'r') as _f:
            cfg = yaml.load(_f, Loader=yaml.FullLoader)['cvt_cfg']
        _f.close()
        self.label_list.append(
                        {"super category number": len(self.sup_check)-1,
                         "super category": text_1,
                         "category number": len(self.cat_check),
                         "category": text_2,
                         }
                    )
        """
        with open(self.catlist_path, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        
        for idx, item in enumerate(data):

            self.sup_map[item['super category']] = item['super category number']

            self.cat_map[item['category']] = item['category number']
            
            self.inv_sup_map[item['super category number']] = item['super category']
            self.inv_cat_map[item['category number']] = item['category']
            self.COCO_LIKE_MAP.append(
                dict(
                    supercategory=item['super category'],
                    id=item['category number'],
                    name=item['category'],
                    )
                )
    
    def cat_mapping(self, mode : bool, **args):
        """
        mode : 
        - True -> from id(integer) to category name(string)
        - False -> from category name(string) to id(integer)
        double stars argument : input_name = key, value = value.
        example) 
        - cat_mapping(True, cat_id = 1)
        Description of this function
        - This function returns integer type encoded value about the label name.
        """
        
        _key = args.get('cat_id', None) if mode else args.get('cat_name', None)
        
        if _key == None:
            raise Exception("Invalid argument.\n Available arguemnt names : cat_id, cat_name")
        
        if mode == True:
            return self.inv_cat_map[_key]
        else:
            return self.cat_map[_key]
    
    def supcat_mapping(self, mode: bool, **args):
        """
        Description of this function
        - This function returns integer type encoded value about the super category name.
        """
        _key = args.get('cat_id', None) if mode else args.get('cat_name', None)
        
        if _key == None:
            raise Exception("Invalid argument.\n Available arguemnt names : cat_id, cat_name")
        if mode == True:
            return self.inv_sup_map[_key]
        else:
            return self.sup_map[_key]

