# -*- coding: utf-8 -*-
# @Time    : 2020/12/12 11:10
# @FileName: utils.py
# @Function: 各种整合的操作
# @Email ：yfwu2020@qq.com

from __future__ import division
import cv2, os
import numpy as np
from struct import unpack
from utils.operation_points import get_points_box, point_filter

def bytes2float(byte_list):
    assert len(byte_list) == 4
    byte_array = bytearray(byte_list)
    python_float = unpack('<f', byte_array)[0]
    return python_float

def resize2myH(points, my_h):
    max_x, max_y, points = get_points_box(points)
    scale = max_y / my_h
    if scale == 0:
        print(' ')
    for i, point in enumerate(points):
        points[i][0] = int(points[i][0] // scale)
        points[i][1] = int(points[i][1] // scale)
    return points

def resize2myW(points, targetW=32):
    max_x, max_y, points = get_points_box(points)
    scale = max_x / targetW
    for i, point in enumerate(points):
        points[i][0] = int(points[i][0] // scale)
        points[i][1] = int(points[i][1] // scale)
    return points

def strQ2B(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:  # 全角空格直接转换
            inside_code = 32
        elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += chr(inside_code)
    return rstring


def strB2Q(ustring):
    """半角转全角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 32:  # 半角空格直接转化
            inside_code = 12288
        elif inside_code >= 32 and inside_code <= 126:  # 半角字符（除空格）根据关系转化
            inside_code += 65248

        rstring += chr(inside_code)
    return rstring


##获得所有文件夹名称
def get_dir_name(dir):
    directory_list = os.listdir(dir)
    del_file = []
    for directory in directory_list:
        if os.path.isfile(os.path.join(dir, directory)):
            del_file.append(directory)
    for file in del_file:
        directory_list.remove(file)
    return directory_list


def draw_img_from_points_split_with_minus1_0(pos_xy, show_points=False):
    img = np.zeros((1000, 4000, 3), np.uint8)  # 创建黑底图像
    img.fill(255)  # 填白
    pos_xy = point_filter(pos_xy)
    max_x, max_y, pos_xy = get_points_box(pos_xy)
    line_points = pos_xy
    first_point = True
    for X_index in range(len(line_points)):
        if line_points[X_index][0] == -1:
            first_point = True
            continue
        if first_point is True:  # 去掉第一点
            first_point = False
            continue
        little_X_point = line_points[X_index - 1][0]
        large_X_point = line_points[X_index][0]
        little_Y_point = line_points[X_index - 1][1]
        large_Y_point = line_points[X_index][1]
        # cv2.line(img, (little_X_point, little_Y_point), (large_X_point, large_Y_point), (0, 0, 0), 2)
    if show_points:
        for X_index in range(len(line_points)):
            if line_points[X_index][0] == -1:
                continue
            # img[line_points[X_index][1]][line_points[X_index][0]] = [255,0,0]
            cv2.circle(img, (line_points[X_index][0], line_points[X_index][1]), 1, (0, 0, 255), 2)
        img = img[:max_y + 1, : max_x + 1]
    print(img.shape)
    cv2.imshow('1', img)
    cv2.waitKey(1)


