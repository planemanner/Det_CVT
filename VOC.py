#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 09:41:08 2021

@author: hmc
"""

import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element, ElementTree, SubElement
import json
import os
import numpy as np
from xml.etree.ElementTree import dump
import base64
from utils import label_list
from glob import glob
# Indentation function for XML format
def indent(elem, level=0): 
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
            
class VOC():
    def __init__(self, img_dir = None, ann_dir = None, list_path = None):
        """
        ann_dir : The root path of annotation data
        """
        self.ann_list = glob(os.path.join(ann_dir, "*.xml"))
        self.img_dir = img_dir
        self._list = label_list(list_path = list_path)
        
        if len(self.ann_list) == 0:
            raise Exception("Please check annotation directory path. This root path has 0-length")
        
    def load_annotation(self, idx : int, encode_img : bool):
        """
        Intermediate data load format : LABELME
        LABELME use utf-8 format decoded image for GUI
        So, if you want to change some label data by using labelme you should set encode_img as True.
        """
        xml = open(self.ann_list[idx], 'r')
        tree = et.parse(xml)
        root = tree.getroot()
        
        all_objects = root.findall("object")
        
        shapes = []
        
        for i in range(len(all_objects)):
            bbox = all_objects[i].find("bndbox")
            x_min = bbox.find("xmin").text
            y_min = bbox.find("ymin").text
            x_max = bbox.find("xmax").text
            y_max = bbox.find("ymax").text
            
            tmp_shape = {"label" : all_objects[i].find("name").text,
                         "points" : [[x_min, y_min],[x_max, y_max]],
                         "group_id" : "None",
                         "shape_type" : "rectangle",
                         "flags" : {}
                         }
            shapes.append(tmp_shape)
            
        LABELME_FORMAT = {"version":"4.5.6", # If labelme is updated, you should change this value
                          "flags":{}, # You can use this value space customly.
                          "shapes":shapes, # Annotation items are in here
                          "imagePath":root.find("filename").text, # Image filename
                          "imageData":None, # Base64 encoding data 
                          "imageHeight":int(root.find("size").find("height").text),
                          "imageWidth":int(root.find("size").find("width").text)
                          }
        
        if encode_img == True:
            img = open(os.path.join(self.img_dir, root.find("filename")),'rb').read()    
            LABELME_FORMAT["imageData"] = base64.b64encode(img).decode("utf-8")
        
        return LABELME_FORMAT
            
    def generate(self, src_path : str, target_dir : str, database_name = None):
        """
        source_path : Path of raw data (Labelme format)
        target_path : Path to be saved
        
        Flow
        1. Load raw data 
        2. Make xml data structure
        """
        # Load raw data (labelme format)
        with open(src_path, "r+") as json_file:
            data = json.load(json_file)
        
        json_file.close()
        
        xml_annotation = Element("annotation") # Root head
        
        SubElement(xml_annotation, "filename").text = data["imagePath"]
        
        xml_source = SubElement(xml_annotation, "source")
        SubElement(xml_source, "database").text = database_name
        

        xml_size = SubElement(xml_annotation, "size")
        SubElement(xml_size, "width").text = str(data["imageWidth"])
        SubElement(xml_size, "height").text = str(data["imageHeight"])
        SubElement(xml_size, "depth").text = str(3)
        
        SubElement(xml_annotation, "segmented")
        
        for i in range(len(data["shapes"])):

            tmp_ann = data["shapes"][i]
            
            xml_object = SubElement(xml_annotation, "object")
            
            SubElement(xml_object, "name").text = tmp_ann["label"]
            SubElement(xml_object, "pose").text = ""
            SubElement(xml_object, "truncated").text = str(1)
            SubElement(xml_object, "difficult").text = str(0)
            
            xml_object_bndbox = SubElement(xml_object, "bndbox")
            xml_object_bndbox_xmin = SubElement(xml_object_bndbox, "xmin")
            xml_object_bndbox_ymin = SubElement(xml_object_bndbox, "ymin")
            xml_object_bndbox_xmax = SubElement(xml_object_bndbox, "xmax")
            xml_object_bndbox_ymax = SubElement(xml_object_bndbox, "ymax")
            
            if tmp_ann["shape_type"] == 'polygon':
                x_min, y_min = map(str, map(int, np.min(tmp_ann["points"], axis=0)))
                x_max, y_max = map(str, map(int, np.max(tmp_ann["points"], axis=0)))
                
                xml_object_bndbox_xmin.text = x_min
                xml_object_bndbox_ymin.text = y_min
                xml_object_bndbox_xmax.text = x_max
                xml_object_bndbox_ymax.text = y_max
                
            elif tmp_ann["shape_type"] == 'rectangle':
                xml_object_bndbox_xmin.text = str(int(tmp_ann["points"][0][0]))
                xml_object_bndbox_ymin.text = str(int(tmp_ann["points"][0][1]))
                xml_object_bndbox_xmax.text = str(int(tmp_ann["points"][1][0]))
                xml_object_bndbox_ymax.text = str(int(tmp_ann["points"][1][1]))
            
            else:
                raise Exception("Invalid annotation exist in raw data")
                
        indent(xml_annotation)
        dump(xml_annotation)
        
        ElementTree(xml_annotation).write(
            os.path.join(target_dir, 
                         os.path.splitext(os.path.basename(src_path))[0]) + '.xml')