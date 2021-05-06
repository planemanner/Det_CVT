#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 09:40:00 2021

@author: hmc
"""
from converter import converter
import argparse

if __name__=="__main__":
    parser = argparse.ArgumentParser("Convert your data~!!")
    parser.add_argument("--yaml_path", type=str, default=None, required=True)
    args = parser.parse_args()
    _cvt = converter(args.yaml_path)
    _cvt.conversion()