# DetectionCVT
  - Version 1.0
  - Annotated data converter for Detection task
  - Available conversion
    - COCO <-> VOC
    - VOC <-> YOLO
    - YOLO <-> COCO
    - COCO, VOC, YOLO <-> LABELME
  - Dependency
    - python 3.7
    - pyqt5, numpy, PIL, labelme, opencv-python, pycocotools, tqdm
  - Prerequired
    You need to make label list by using make_label_list.py. Detail description will be updated
      
      **Content of Example**
  
      | supercategory number | supercategory name | category number | category name | 
      |:---:|:---:|:---:|:---:|
      |0|furniture|0|chair|
      |0|furniture|1|bed|
      |1|fruits|2|apple|
      |2|cosmetic|3|lipstick|
 - To do
   - Update overall codes reflecting all feedback
 - Updated feature
   - make_label_list.py provides a GUI to make yaml file having category list.

[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fplanemanner&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
