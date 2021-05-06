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
    - ~~label list txt file. [Example](https://github.hmckmc.co.kr/kangil-lee/DetectionCVT/blob/master/label_list.txt)~~
    - label list yaml file.
      - Use make label list file [Code](https://github.hmckmc.co.kr/kangil-lee/DetectionCVT/blob/master/make_label_list.py)
      
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
