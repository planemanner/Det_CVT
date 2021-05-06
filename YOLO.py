#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 17:20:49 2021

@author: hmc

YOLO BBOX FORMAT

(centerX, centerY, w, h) -> ratio.

Yolo Format  : 0 0.256 0.315 0.506 0.593
(class, x, y, w, h)
txt 하나 -> 하나의 영상        

"""
import os
from PIL import Image
import json
from glob import glob
import base64
import numpy as np
from utils import label_list
"""
Warning : glob do not return basename
"""
def coorcvt2yolo(size, box):
    '''FROM RAW TO RATIO TYPE'''
    '''input box should have right order x_min, y_min, x_max, y_max'''
    dw = 1./size[0]
    dh = 1./size[1]
    
    center_x = (box[0] + box[2]) / 2.0
    center_y = (box[1] + box[3]) / 2.0
    
    w = box[2] - box[0]
    h = box[3] - box[1]
    
    x = center_x * dw
    w = w * dw
    y = center_y * dh
    h = h * dh
    
    return (round(x, 3), round(y, 3), round(w, 3), round(h, 3))
"""
Coordinate conversion example

test_ann = [537.0625, 212.375, 987.0625, 560.8125] -> a list of float or int-type entities
wh = (1920, 1080)

y_out =  coorcvt2yolo(size=wh, box=test_ann)

"""
def coorcvt2raw(size, box):
    w, h = size
    x_min = box[0] * w - box[2] * w/2
    y_min = box[1] * h - box[3] * h/2
    x_max = box[0] * w + box[2] * w/2
    y_max = box[1] * h + box[3] * h/2
    
    return [[x_min, y_min], [x_max, y_max]]

class YOLO():
    def __init__(self, img_dir = None, ann_dir = None, list_path = None):
        VALID_IMAGE_FORMAT = ['jpg', 'png', 'jpeg', 'tiff']
        self.img_pathes = []
        self.label_pathes = glob(os.path.join(ann_dir, "*.txt"))
        
        for form in VALID_IMAGE_FORMAT:
            self.img_pathes += [glob(os.path.join(img_dir, "*.{}".format(form)))]
        
        if len(self.img_pathes) == 0:
            raise Exception("There is no images having valid format. \
                            Please check your folder")
        
        if len(self.label_pathes) == 0:
            raise Exception("There is no annotation files having valid format. \
                            Please check your folder")
        """
        As a property of YOLO format, 
        there is no information for matched image data in a txt file.
        So all data should be sorted and image-label pair must have same name.
        """    
        
        self.img_pathes.sort() 
        self.label_pathes.sort()
        """
        self._list.cat_mapping
        self._list.supcat_mapping
        """
        self._list = label_list(list_path = list_path)  
    
    def load_annotation(self, idx : int, encode_img : bool):
        """
        Rule : Image-file's name should be same as label file's name
        and sorted.
        """
        img_name = os.path.basename(self.img_pathes[idx])
        img = Image.open(self.img_pathes[idx])
        width, height = img.size
        
        with open(self.label_pathes[idx], "r") as label_file:
            ann_data = label_file.readlines()
        label_file.close()
        
        shapes = []
        
        for _, ann in enumerate(ann_data):
            cls_id, c_x, c_y, w, h = ann.strip("\n").split(" ")
            bbox = self.coorcvt2raw((width, height), [float(item) for item in [c_x, c_y, w, h]])
            tmp_shape = {"label" : cls_id,
                         "points" : bbox,
                         "group_id" : None,
                         "shape_type" : "rectangle",
                         "flags" : {}
                         }
            
            shapes.append(tmp_shape)
        
        LABELME_FORMAT = {"version":"4.5.6", # If labelme is updated, you should change this value
                  "flags":{}, # You can use this value space customly.
                  "shapes":shapes, # Annotation items are in here
                  "imagePath":img_name, # Image filename
                  "imageData":None, # Base64 encoding data 
                  "imageHeight":width,
                  "imageWidth":height
                  }
        
        if encode_img == True:
            img = open(self.img_pathes[idx], 'rb').read()    
            LABELME_FORMAT["imageData"] = base64.b64encode(img).decode("utf-8")
        
        return LABELME_FORMAT

    '''LABELME -> YOLO'''
    """
    데이터를 읽을 때 공통 포맷을 LABELME로 두면, Generate라는 함수를 이용해서 변환할 수 있어서 매우 편하다! 
    """
    def generate(self, img_path, label_path, output_dir):
        
        img_basename = os.path.splitext(os.path.basename(img_path))[0]
        label_basename = os.path.splitext(os.path.basename(label_path))[0]
        
        if img_basename != label_basename :
            raise Exception("Image file and label file are not matched. Please check the file names")
        
        with open(label_path, "r+") as json_file:
            data = json.load(json_file)
        json_file.close()
        
        img_w, img_h = data["imageWidth"], data["imageHeight"]
        
        yolo_txt = open(os.path.join(output_dir, 
                                     os.path.splitext(os.path.basename(label_path))[0]) + ".txt", "a")
            
        for i in range(len(data["shapes"])):
            tmp_ann = data["shapes"][i]  # dictionary structure
            cls_name = tmp_ann["label"]
            
            if tmp_ann["shape_type"] == "polygon":
                x_min, y_min = np.min(tmp_ann["points"], axis=0)
                x_max, y_max = np.max(tmp_ann["points"], axis=0)
                yolo_coor = coorcvt2yolo((img_w, img_h), [x_min, y_min, x_max, y_max])
            
            elif tmp_ann["shape_type"] == "rectangle":
                x_min, y_min = tmp_ann["points"][0]
                x_max, y_max = tmp_ann["points"][1]
                yolo_coor = coorcvt2yolo((img_w, img_h), [x_min, y_min, x_max, y_max])
            else:
                raise Exception("Invalid shape type. Please check the shape type of this annotation data")
                
            tmp_write = "{} {} {} {} {}\n".format(self._list.cat_mapping(mode=False, cat_name = cls_name), 
                                                  yolo_coor[0], 
                                                  yolo_coor[1], 
                                                  yolo_coor[2], 
                                                  yolo_coor[3])
            yolo_txt.write(tmp_write)
            
        yolo_txt.close()