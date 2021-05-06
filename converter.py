#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 11:03:32 2021

@author: hmc

Prevalantly used datasets

MSCOCO
VOC 2012
VOC 2017

Preliminary Features
- annotation validity check
- 
YOLO
def __init__(self, img_dir, label_dir, list_path):
VOC
def __init__(self, img_dir = None, ann_dir = None, list_path = None):
COCO
def __init__(self, img_dir = None, ann_path = None, list_path = None):
"""
from VOC import VOC
from YOLO import YOLO
from COCO import COCO
import yaml
import os
import json
from glob import glob

class converter():
    def __init__(self, cfg_path):
        """
        Available format list
          - Labelme
            Labelme annotation file format -> a list of json files
          - COCO
            COCO annotation file format -> a json file
          - VOC
            x_min, y_min, x_max, y_max
            VOC annotation file format -> a list of xml files
          - YOLO
            Image size ratio-based representation
            (center_x, center_y, w, h)
            YOLO annotation file format -> a list of txt files
        
        cfg structure:
            [{'task': 'det'},
             {'src_form': None},
             {'tgt_form': None},
             {'img_dir': None},
             {'ann_dir': None},
             {'cat_list': None},
             {'supcat_list': None},
             {'output_dir': None}]
        """
        self.cfg = None
        self.set_cfg(yaml_path=cfg_path)
        if os.path.isfile("./tmp_directory"):
            os.mkdir("./tmp_directory")

    def set_cfg(self, yaml_path : str):
        """
        Description
        Step.1 : Read yaml script from local folder
          - You need to set regular format for this converter
          - If improper variables are used, raise an exception and 
          inform to user what should be modified.
          
        Step.2 : set configuration parameters
        """
        if os.path.splitext(yaml_path)[-1] != '.yaml':
            raise Exception("Invalid configuration file format. Please check whether the format is .yaml or not")
            
        with open(yaml_path, 'r') as _f:
            cfg = yaml.load(_f, Loader=yaml.FullLoader)['cvt_cfg']
        _f.close()
        
        self.cfg = cfg
        
    def conversion(self):
        """
        How to decide what formats are used ? -> src_form, tgt_form 
        function name space
        To_YOLO
        To_COCO
        To_VOC
        To_LABELME
        """
        self.tmp_clear()
        
        VAL_FORMAT = ["YOLO", "COCO", "VOC", "LABELME"]
        
        if self.cfg["src_form"] not in VAL_FORMAT:
            raise Exception("Please give a valid source format") 
            
        if self.cfg["tgt_form"] == "YOLO":
            self.To_YOLO()
        elif self.cfg["tgt_form"] == "COCO":
            self.To_COCO()
        elif self.cfg["tgt_form"] == "VOC":
            self.To_VOC()
        elif self.cfg["tgt_form"] == "LABELME":
            self.To_LABELME()
        else:
            raise Exception("Please give a valid target format")
            
    def tmp_ann(self, ann_data, tmp_path):
        tmp_json = open(tmp_path, 'w')
        json.dump(ann_data, tmp_json, indent=4)
        tmp_json.close()
    
    def tmp_clear(self):
        """
        This function clean up the temporary directory.
        """
        tmp_ann_list = glob(os.path.join('./tmp_directory', '*.json'))
        
        for ann_path in tmp_ann_list:
            os.remove(ann_path)
    
    def To_YOLO(self):
        _YOLO = YOLO(list_path=self.cfg['cat_list'])
        if self.cfg["src_form"] == "COCO":
            _COCO = COCO(img_dir=self.cfg['img_dir'],
                         ann_path=os.path.join(self.cfg['ann_dir'], self.cfg['COCO_ANN_NAME'] + '.json'),
                         list_path=self.cfg['cat_list'])
            
            num_imgs = len(_COCO.image_ids)

            for i in range(num_imgs):
                ann_data = _COCO.load_annotation(i, False)
                tmp_path = './tmp_directory/{}.json'.format(os.path.basename(
                    os.path.splitext(ann_data["imagePath"])[0]))
                self.tmp_ann(ann_data, tmp_path)
                
                _YOLO.generate(img_path=ann_data["imagePath"],
                               label_path=tmp_path,
                               output_dir=self.cfg['output_dir'])
                
        elif self.cfg["src_form"] == "VOC":
            _VOC = VOC(img_dir = self.cfg["img_dir"],
                       ann_dir = self.cfg["ann_dir"], 
                       list_path = self.cfg["cat_list"])
            
            num_imgs = len(_VOC.ann_list)
            
            for i in range(num_imgs):
                ann_data = _VOC.load_annotation(idx=i, encode_img=self.cfg["img_enc"])
                tmp_path = './tmp_directory/{}.json'.format(os.path.basename(
                    os.path.splitext(ann_data["imagePath"])[0]))
                self.tmp_ann(ann_data, tmp_path)
                
                _YOLO.generate(img_path=ann_data["imagePath"],
                               label_path=tmp_path,
                               output_dir=self.cfg['output_dir'])

        elif self.cfg["src_form"] == "LABELME":
            
            ann_list = glob(os.path.join(self.cfg["ann_dir"], "*.json"))
            
            for ann_idx, ann_path in enumerate(ann_list):
                _YOLO.generate(img_path=os.path.splitext(os.path.basename(ann_path))[0],
                               label_path=ann_path,
                               output_dir=self.cfg["output_dir"])
            
    def To_COCO(self):
        _COCO = COCO(list_path=self.cfg["cat_list"])
        if self.cfg["src_form"] == "YOLO":
            _YOLO = YOLO(img_dir=self.cfg["img_dir"], ann_dir=self.cfg["ann_dir"], list_path=self.cfg["cat_list"])
            
            for idx in range(len(_YOLO.label_pathes)):
                ann_data = _YOLO.load_annotation(idx=idx, encode_img=self.cfg["img_enc"])
                tmp_path = './tmp_directory/{}.json'.format(os.path.basename(
                    os.path.splitext(ann_data["imagePath"])[0]))
                self.tmp_ann(ann_data, tmp_path)

            _COCO.generate(img_dir=self.cfg["img_dir"],
                           label_dir="./tmp_directory",
                           output_path=os.path.join(self.cfg["output_dir"], "COCO_FORM.json"))
            
        elif self.cfg["src_form"] == "VOC":
            
            _VOC = VOC(img_dir=self.cfg["img_dir"],
                       ann_dir=self.cfg["ann_dir"],
                       list_path=self.cfg["cat_list"])
            
            num_imgs = len(_VOC.ann_list)
            
            for i in range(num_imgs):
                ann_data = _VOC.load_annotation(idx=i, encode_img=self.cfg["img_enc"])
                tmp_path = './tmp_directory/{}.json'.format(os.path.basename(
                    os.path.splitext(ann_data["imagePath"])[0]))
                self.tmp_ann(ann_data, tmp_path)

            _COCO.generate(img_dir=self.cfg["img_dir"],
                           label_dir="./tmp_directory",
                           output_path=os.path.join(self.cfg["output_dir"], "COCO_FORM.json"))
            
        elif self.cfg["src_form"] == "LABELME":
            _COCO.generate(img_dir=self.cfg["img_dir"],
                           label_dir=self.cfg["ann_dir"],
                           output_path=os.path.join(self.cfg["output_dir"], "COCO_FORM.json"))
            
    def To_VOC(self):
        _VOC = VOC(list_path=self.cfg["cat_list"])
        if self.cfg["src_form"] == "COCO":
            _COCO = COCO(img_dir=self.cfg['img_dir'],
                         ann_path=os.path.join(self.cfg['ann_dir'], self.cfg['COCO_ANN_NAME'] + '.json'),
                         list_path=self.cfg['cat_list'])
            num_imgs = len(_COCO.image_ids)
            
            for idx in range(num_imgs):
                ann_data = _COCO.load_annotation(image_index=idx, encode_img=self.cfg["img_enc"])
                tmp_path = './tmp_directory/{}.json'.format(os.path.basename(
                    os.path.splitext(ann_data["imagePath"])[0]))
                self.tmp_ann(ann_data, tmp_path)
                _VOC.generate(src_path=tmp_path, target_dir=self.cfg["output_dir"]) # Done !
                
        elif self.cfg["src_form"] == "YOLO":
            _YOLO = YOLO(img_dir=self.cfg["img_dir"], ann_dir=self.cfg["ann_dir"], list_path=self.cfg["cat_list"])
            
            for idx in range(len(_YOLO.label_pathes)):
                ann_data = _YOLO.load_annotation(idx = idx, encode_img=self.cfg['img_enc'])
                tmp_path = './tmp_directory/{}.json'.format(os.path.basename(
                    os.path.splitext(ann_data["imagePath"])[0]))
                self.tmp_ann(ann_data, tmp_path)
                _VOC.generate(src_path=tmp_path, target_dir=self.cfg["output_dir"]) # Done !
                
        elif self.cfg["src_form"] == "LABELME":
            _VOC = VOC(list_path=self.cfg["cat_list"])
            ann_list = os.path.join(self.cfg["ann_dir"], "*.json")
            
            for idx, ann_path in enumerate(ann_list):
                _VOC.generate(src_path=ann_path, target_dir=self.cfg["output_dir"]) # Done !
            
    def To_LABELME(self):
        if self.cfg["src_form"] == "COCO":
            _COCO = COCO(img_dir=self.cfg['img_dir'],
                         ann_path=os.path.join(self.cfg['ann_dir'], self.cfg['COCO_ANN_NAME'] + '.json'),
                         list_path=self.cfg['cat_list'])
            num_imgs = len(_COCO.image_ids)
            
            for idx in range(num_imgs):
                ann_data = _COCO.load_annotation(image_index=idx, encode_img=self.cfg['img_enc'])
                tmp_path = '{}/{}.json'.format(self.cfg["output_dir"], os.path.basename(
                    os.path.splitext(ann_data["imagePath"])[0]))
                self.tmp_ann(ann_data, tmp_path)
            
        elif self.cfg["src_form"] == "VOC":
            
            _VOC = VOC(img_dir=self.cfg["img_dir"],
                       ann_dir=self.cfg["ann_dir"],
                       list_path=self.cfg["cat_list"])
            
            num_imgs = len(_VOC.ann_list)
            
            for i in range(num_imgs):
                ann_data = _VOC.load_annotation(idx=i, encode_img=False)
                tmp_path = '{}/{}.json'.format(self.cfg["output_dir"], os.path.basename(
                    os.path.splitext(ann_data["imagePath"])[0]))
                self.tmp_ann(ann_data, tmp_path)
                
        elif self.cfg["src_form"] == "YOLO":
            _YOLO = YOLO(img_dir=self.cfg["img_dir"], ann_dir = self.cfg["ann_dir"], list_path = self.cfg["cat_list"])
            
            for idx in range(len(_YOLO.label_pathes)):
                ann_data = _YOLO.load_annotation(idx=idx, encode_img=self.cfg['img_enc'])
                tmp_path = '{}/{}.json'.format(self.cfg["output_dir"], os.path.basename(
                    os.path.splitext(ann_data["imagePath"])[0]))
                self.tmp_ann(ann_data, tmp_path)
    
        
        


