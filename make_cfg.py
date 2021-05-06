#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 11:00:15 2021

@author: hmc
"""
import yaml
import argparse
import os
"""
Python dictionary data serialization sample code

** Code 1 **
fruits = {'fruits':['blueberry', 'apple', 'orange']}

print(serialized_fruits)

** Output 1 **
fruits:
- blueberry
- apple
- orange

** Code 2 **

fruits = {'fruits':['blueberry', {'apple':['green', 'red']}, 'orange']}
serialized_fruits = yaml.dump(fruits)

** Output 2 **

fruits:
- blueberry
- apple:
  - green
  - red
- orange

self.cfg = {
            "task" : None,
            "source_form" : None,
            "target_form" : None,
            "img_dir" : None,
            "ann_dir" : None,
            "category_list" : None,
            "super_category_list" : None,
            "output_dir" : None
            }

"""

parser = argparse.ArgumentParser(description="Set the configurations for converter")
parser.add_argument("--task", type=str, default='det',
                    choices=['det', 'seg'],
                    help="Detection, Semantic_Segmentation...")
parser.add_argument("--src_form", type=str, default=None,
                    choices=['COCO', 'VOC', 'YOLO', 'LABELME'],
                    help="What is the source labeling data format ?")
parser.add_argument("--tgt_form", type=str, default=None,
                    choices=['COCO', 'VOC', 'YOLO', 'LABELME'],
                    help="What is the target labeling data format ?")
parser.add_argument("--img_dir", type=str, default=None, help="Where are the images ?")
parser.add_argument("--ann_dir", type=str, default=None,
                    help="Where are the annotation data ?")
parser.add_argument("--cat_list", type=str, default=None,
                    help="Where is the label list txt file ?")
parser.add_argument("--output_dir", type=str, default=None,
                    help="Where do you want to save the converted data?")
parser.add_argument("--coco_ann_name", type=str, default="train",
                    help="What is the name of coco json file?")
parser.add_argument("--yaml_dir", type=str, default='./', help="Where do you want to save this configuration file ?")
parser.add_argument("--img_enc", type=bool, default=False)
args = parser.parse_args()

cvt_cfg = {'cvt_cfg': [
            {'task': args.task},
            {'src_form': args.src_form},
            {'tgt_form': args.tgt_form},
            {'img_dir': args.img_dir},
            {'ann_dir': args.ann_dir},
            {'cat_list': args.cat_list},
            {'output_dir': args.output_dir},
            {'COCO_ANN_NAME': args.coco_ann_name},
            {'img_enc': args.img_enc}]}

with open(os.path.join(args.yaml_dir, 'cvt_cfg.yaml'), "w") as f:
    yaml.dump(cvt_cfg, f)

f.close()


























