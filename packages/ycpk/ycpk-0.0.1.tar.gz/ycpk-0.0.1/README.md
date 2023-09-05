<!--
 * @Author: wind windzu1@gmail.com
 * @Date: 2023-09-01 14:23:18
 * @LastEditors: wind windzu1@gmail.com
 * @LastEditTime: 2023-09-01 17:49:36
 * @Description: 
 * Copyright (c) 2023 by windzu, All Rights Reserved. 
-->
# YCPK

yun chuang perception kit

本项目是一个工具集合，包含了感知一些常用的工具，如相机标定，数据集转换，数据集切片，gif生成等

| Tools           | Description                                                          |
| --------------- |:--------------------------------------------------------------------:|
| gif generator   | generate gif from image or point cloud                               |
| data slice      | slice data to nuscenes format                                                 |
| voc2coco        | convert standard voc format dataset to coco format                   |
| ros visualizer  | convert the common message format of ros to marker for visualization |



## Install

```bash
pip3 install ycpk
```
> Note : 如果想使用开发版，可以通过源码安装
```bash
git clone http://szlan.yczx.tech:1024/perception/ycpk.git
cd ycpk
pip3 install -e .
```

## Simple Usage
> 下面是一些简单的使用介绍，更多高级用法请参考其[文档](https://ycpk.readthedocs.io/en/latest/)

```bash
ycpk [tools_name] [args]
```

### 数据切片
> 本功能需要熟悉`config.yaml`的编写规则，请参考[文档](https://ycpk.readthedocs.io/en/latest/data_slice.html)

本功能负责将采集到的数据包切片，并按照一个的格式保存，切片时候会对数据的时间同步检查，切片后的数据集可以用于训练，也可以用于标注
```bash
ycpk slice ./config.yaml
```
### gif生成

> All folders under this path will be traversed. If a folder contains images or point cloud files, a gif will be generated with the name of the folder and stored in its parent directory

* path：Want to traverse the root path of the generated gif

```bash
ycpk gif . # generator gif from specify path
```

### voc2coco

* path：The path where the standard voc format data set is located
  
  ```bash
  path
  ├── Annotations
  ├── coco
  ├── ImageSets
  ├── JPEGImages
  └── labels.txt
  ```

* labels.txt ：The labels.txt file must be included, and its content is the name of the category, which is used to map from class name to label id when converting to coco
  
  ```txt
  class_name_0
  class_name_1
  class_name_2
  ...
  ```

```bash
ycpk v2c . # convert voc to coco
```
### 相机内参标定

```bash
ycpk calib_camera --camera_model fisheye --size 11x8 --square 0.045 --image_dir ./images
```

### 森云相机内参读取