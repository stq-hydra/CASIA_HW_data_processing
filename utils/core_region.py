import numpy as np
from utils.operation_points import get_points_box_simple, pts_shift_top

def core_region_resize(h, core_percentage, line_points, y1, y2):
    core_h =  int(h * core_percentage) # 26
    if core_h % 2 != 0: # 必须是偶数
        core_h -= 2

    up_bottom_h = (h - core_h) / 2
    box_w, box_h, line_points, min_x, min_y = get_points_box_simple(line_points, get_shift=True)
    y1 = int(y1 - min_y)
    y2 = int(y2 - min_y)
    h_scale_core = float(y2 - y1) / (core_h)
    h_scale_up = y1 / up_bottom_h
    h_scale_bottom = y2 / up_bottom_h
    for point_index, point in enumerate(line_points):
        if point[0] == -1:
            continue
        if point[1] < y1 and point[1] > 0:
            point[1] = int(point[1] / h_scale_up + 0.5)
        elif point[1] >= y1 and point[1] <= y2:
            point[1] = int((point[1] - y1) / h_scale_core + 0.5 + up_bottom_h)
        elif point[1] > y2:
            point[1] = int((point[1] - y2) / h_scale_bottom + 0.5 + up_bottom_h + core_h)
        line_points[point_index] = point
    for point_index, point in enumerate(line_points):
        if point[0] != -1:
            point[0] = int(point[0] / h_scale_core + 0.5)
        line_points[point_index] = point
    return line_points

def core_region_estimation(line_points, core_percentage):
    half_core_percentage = core_percentage/2
    if len(line_points) == 3:
        raise ValueError('点集不能小于3')
    pts, shift_y = pts_shift_top(line_points) #点击移到顶部方便缩放
    pts_h = np.array(pts).max(axis=0)[1] + 1
    pts_y_axis_count = [0] * pts_h
    P                = [0] * pts_h
    PK               = [0] * pts_h
    for pt in pts:
        pts_y_axis_count[pt[1]] += 1
    pts_num = len(pts)
    sum_tmp_PK = 0
    find_center_flag = True
    for pts_i in range(pts_h):
        P[pts_i] = pts_y_axis_count[pts_i] / pts_num   #每个灰度级出现的概率
        PK[pts_i] = sum_tmp_PK + P[pts_i]    #概率累计和
        if find_center_flag and PK[pts_i] > 0.5:
            center = pts_i
            find_center_flag = False
        sum_tmp_PK = PK[pts_i]

    #上界
    for i in range(center):
        if PK[i] > 0.5 - half_core_percentage:
            y1 = i - 1 + shift_y
            break
    #下界
    for i in reversed(range(pts_h)):
        if PK[i] < 0.5 + half_core_percentage:
            y2 = i + 1 + shift_y
            break
    return y1, y2