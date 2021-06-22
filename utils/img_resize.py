# -*- coding: utf-8 -*-
# @Time    : 2021/1/28 12:32
# @FileName    : img_resize.py
# @Email   : yfwu2020@qq.com

import cv2
from utils.operation_points import get_points_box

def img_resize(img, resize_h=32, mode='keep_ratio', interpolation=cv2.INTER_CUBIC):
    if mode != 'keep_ratio':
        raise KeyError("当前不支持{}模式".format(mode))
    img = img.astype("uint8")
    h = img.shape[0]
    aim_scale = resize_h / h
    img = cv2.resize(img, (0, 0), fx=aim_scale, fy=aim_scale, interpolation=interpolation)
    return img

def line_points_resize(line_points, resize_h=32, mode='keep_ratio'):
    if mode != 'keep_ratio':
        raise KeyError("当前不支持{}模式".format(mode))
    box_w, box_h, line_points = get_points_box(line_points)
    h_scale = float(box_h) / (resize_h - 0)
    for point_index, point in enumerate(line_points):
        if point[0] == -1:
            continue
        point[0] = int(point[0] / h_scale) # + 0.5)
        point[1] = int(point[1] / h_scale) # + 0.5)
        line_points[point_index] = point
    max_x, max_y, _ = get_points_box(line_points, shift=False)
    return line_points, max_x