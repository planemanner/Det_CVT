#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 17:20:30 2021

@author: hmc
"""

import os 
import base64
import json
import numpy as np
from tqdm import tqdm
from pycocotools.coco import COCO as _COCO
import datetime
from glob import glob
import cv2
from utils import label_list

with open("./labelme_sample.json", "r+") as f:
    data = json.load(f)
f.close()

sample = data["shapes"]

def area_of_polygon(polygon):
    polygon = np.array(polygon).astype(int)
    return cv2.contourArea(polygon)

def find_all_img_anns(coco):
    
    img_id_list = []
    ann_list = []
    
    for img_info in coco['images']:
        img_id_list.append(img_info['id'])
        ann_list.append([])
    
    print("START LOADING annotation data")
    
    for ann in tqdm(coco['annotations']):
        index = img_id_list.index(ann['image_id'])
        ann_list[index].append(ann)
    
    return coco['images'], ann_list

class COCO():
    def __init__(self, img_dir = None, ann_path = None, list_path = None):
        """
        Arguments Description
        Label_list -> coco category look-up table (dictionary format)
        
        COCO FORMAT STRUCTURE
        info
         - description : What data ?
         - url : where do you get this data ?
         - version : The version of annotation data
         - year : The year of generating annotation data
         - contributor : contributor's name
         - data_created : date
        images (list)
         - license : I don't know what it means exactly.
         - file_name : image filename
         - coco_url : MSCOCO TEAM'S Website. (Indicating an image on the website)
         - height : The height of an image
         - width : The width of an image
         - flickr_url : COCO data is generated by using flickr app. 
         So, in here, the url of flickr exists.
         - id : image id. it is unique.
        licenses
         - url : indicate an institute's url having copyright of this data.
         - id : Maybe... institute's id ?
         - name : The institute's name
        annotations (list)
         when iscrowd : 1
         - segmentation 
           - counts : uncompressed RLE format annotation data
           - size : uncompressed RLE format annotation data
           Please check https://github.com/cocodataset/cocoapi/issues/135
         when iscrowd : 0
         - segmentation
           - N-dimensional polygon's coordinates like x_1, y_1 ... x_N, y_N
         - area : Region of the segmentation polygon.
         - iscrowd : crowd target or not.
         - image_id : literally same 
         - bbox : literally same
         - category_id : literally same
         - id : ??
        categories (list)
         - supercategory : High level concept category
         - id : Category number
         - category : Concrete category
         example, sup_cat : Furniture
                  cat : Chair
        """
        
        self.img_dir = img_dir
        self.COCO = _COCO(ann_path)
        self.image_ids = self.COCO.getImgIds()
        self._list = label_list(list_path = list_path)
    
    def load_image_info(self, img_idx):
        """
        image_info is dictionary having following structure
        
        {'license': 3,
         'file_name': 'COCO_val2014_000000391895.jpg',
         'coco_url': 'http://images.cocodataset.org/val2014/COCO_val2014_000000391895.jpg',
         'height': 360,
         'width': 640,
         'date_captured': '2013-11-14 11:18:45',
         'flickr_url': 'http://farm9.staticflickr.com/8186/8119368305_4e622c8349_z.jpg',
         'id': 391895
         }
        
        """
        image_info = self.COCO.loadImgs(self.image_ids[img_idx])[0]
        
        return image_info
    
    def load_annotation(self, image_index: int, encode_img: bool):
        
        image_info = self.load_image_info(img_idx=image_index)
        annotations_ids = self.COCO.getAnnIds(imgIds=self.image_ids[image_index], iscrowd=False)
        ann_data = self.coco.loadAnns(annotations_ids)
        # Partial annotation data based on an image id
        shapes = []
        
        for item_id, item in enumerate(ann_data):
            # bbox : x_min, y_min, width, height
            x_min, y_min, width, height = item['bbox']
            tmp_shape = {"label": self._list.cat_mapping(True, cat_id=str(item['category_id'])),
                         "points": [[x_min, y_min],[x_min+width, y_min + height]],
                         "group_id": None,
                         "shape_type": "rectangle",
                         "flags": {}
                         }

            shapes.append(tmp_shape)
            
        LABELME_FORMAT = {"version":"4.5.6", # If labelme is updated, you should change this value
                  "flags":{}, # You can use this value space customly.
                  "shapes":shapes, # Annotation items are in here
                  "imagePath":image_info['file_name'], # Image filename
                  "imageData":None, # Base64 encoding data 
                  "imageHeight":image_info['height'],
                  "imageWidth":image_info['width']
                  }
        
        if encode_img == True:
            img = open(os.path.join(self.img_dir, image_info['file_name']), 'rb').read()    
            LABELME_FORMAT["imageData"] = base64.b64encode(img).decode("utf-8")
        
        return LABELME_FORMAT
    
    def generate(self, img_dir, label_dir, output_path):
        VALID_IMAGE_FORMAT = ['jpg', 'png', 'jpeg', 'tiff']
        img_list = []
        ann_list = glob(os.path.join(label_dir, '*.json'))
        amount_of_ann = len(ann_list)
        
        for form in VALID_IMAGE_FORMAT:
            img_list += [glob(os.path.join(img_dir, "*.{}".format(form)))]
        
        if len(img_list) == 0:
            raise Exception("There is no valid images. Please check the image folder")
        
        if len(ann_list) == 0:
            raise Exception("There is no annotation files. Please check the annotation folder")
                    
        now = datetime.datetime.now()

        data = dict(
            info=dict(
                description = "What kind of dataset?",
                version="v1.0",
                year=now.year,
                contributor="LEE KANG IL, AIRLAB",
                date_created=now.strftime("%Y-%m-%d %H:%M:%S.%f")
                ),
            images=[],
            annotations=[],
            categories = self._list.COCO_LIKE_MAP
            )
        
        for image_id, label_path in enumerate(ann_list):
            with open(os.path.join(label_dir, label_path), 'r+') as f:
                label_data = json.load(f)
            f.close()
            
            data["images"].append(
                dict(
                    file_name = label_data["imagePath"],
                    height = label_data["imageHeight"],
                    width = label_data["imageWidth"], 
                    id = image_id,
                    )
                )
            
            for label_id in range(len(label_data["shapes"])):
                label_data[label_id]['label']
                if label_data[label_id]['shape_type'] == 'rectangle':
                    (x_min, y_min), (x_max, y_max) = label_data[label_id]['points']
                    bbox = [x_min, y_min, x_max-x_min, y_max-y_min]
                    area = bbox[2] * bbox[3]
                    
                elif label_data[label_id]['shape_type'] == 'polygon':
                    polygon_pts = label_data[label_id]['points']
                    area = area_of_polygon(polygon_pts)
                    bbox = polygon_pts
                    
                data["annotations"].append(
                    dict(
                        segmentation = [],
                        area = area,
                        iscrowd = 0,
                        image_id = image_id,
                        bbox = bbox, # x_min, y_min, w, h
                        category_id = self._list.cat_mapping(False, 
                                                             cat_name = label_data[label_id]['label']),
                        id = str(image_id).zfill(len(str(amount_of_ann))) + str(label_id).zfill(3)
                        ))
                """
                If you don't want to set specific super cat. and etc, please set sup cat as None
                and the others are properly dealt.
                """
                
        with open(output_path, 'w') as out_file:
            json.dump(data, out_file, indent=4)
