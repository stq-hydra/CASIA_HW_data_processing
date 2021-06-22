import cv2, copy, math
import numpy as np

def shift_left(points, min_x, min_y, max_x, max_y):
    for point in points:
        if point[0] == -1:
            continue
        point[0] -= min_x
        point[1] -= min_y
    max_x -= min_x
    max_y -= min_y
    return max_x, max_y, points

def pts_shift_top(pts):
    # pts [[x1,y1],[x2,y2],[x3,y3],...,[xn,yn]]
    new_pts = copy.deepcopy(pts)
    shift_y = np.array(new_pts).min(axis=0)[1]
    for pt in new_pts:
        pt[1] -= shift_y
    return new_pts, shift_y

def get_points_box_simple(points, get_shift=False):
    max_x = 0
    max_y = 0
    min_x, min_y = 9999, 9999
    ## all shift left
    for point in points:
        if point[0] == -1:
            continue
        if point[0] < min_x:
            min_x = point[0]
        if point[1] < min_y:
            min_y = point[1]

        if point[0] > max_x:
            max_x = point[0]
        if point[1] > max_y:
            max_y = point[1]

    for point in points:
        if point[0] == -1:
            continue
        point[0] -= min_x
        point[1] -= min_y

    max_x -= min_x
    max_y -= min_y
    if get_shift == True:
        return max_x, max_y, points, min_x, min_y
    return max_x, max_y, points

def get_points_box(points, shift=True, get_shift_h=False):
    max_x = max_y = 0
    min_x, min_y = 999999, 999999
    ## all shift left
    for point in points:
        if point[0] == -1:
            continue

        if point[0] < min_x:
            min_x = point[0]
        if point[1] < min_y:
            min_y = point[1]

        if point[0] > max_x:
            max_x = point[0]
        if point[1] > max_y:
            max_y = point[1]

    if shift:
        max_x, max_y, points = shift_left(points, min_x, min_y, max_x, max_y)
    max_x += 1
    max_y += 1
    if get_shift_h:
        return max_x, max_y, points, min_y
    return max_x, max_y, points

def pts_shift_top(pts):
    # pts [[x1,y1],[x2,y2],[x3,y3],...,[xn,yn]]
    new_pts = copy.deepcopy(pts)
    shift_y = np.array(new_pts).min(axis=0)[1]
    for pt in new_pts:
        pt[1] -= shift_y
    return new_pts, shift_y


def point_filter(points):
    new_points = []
    temp_points = []
    for i in range(len(points)):
        if i != len(points) - 1 and points[i] == points[i + 1]:
            continue
        else:
            temp_points.append(points[i])
    i = 0
    if temp_points[1][0] == -1:  # 过滤第一个点就是第一个笔画的情况
        i = 2
    while True:
        if i == len(temp_points):
            break
        # if i + 1 == len(temp_points) - 1 or i == len(temp_points):
        #     break
        if temp_points[i][0] == -1 and i + 2 >= len(temp_points) - 2:
            new_points.append(temp_points[i])
            break
        if temp_points[i][0] == -1 and temp_points[i + 2][0] == -1:
            i += 2
            continue  ###20200724
        else:
            new_points.append(temp_points[i])
        i += 1
    return new_points


def Nrotation_angle_get_coor_coordinates(point, center, angle):
    src_x, src_y = point
    center_x, center_y = center
    radian = math.radians(angle)
    dest_x = round((src_x - center_x) * math.cos(radian) + (src_y - center_y) * math.sin(radian) + center_x)
    dest_y = round((src_y - center_y) * math.cos(radian) - (src_x - center_x) * math.sin(radian) + center_y)
    return [int(dest_x), int(dest_y)]

def show_char_img(per_char_point_list, index=1):
    img = np.zeros((1000, 1000), np.uint8)  # 创建黑底图像
    # pos_xy = point_filter(per_char_point_list)
    pos_xy = per_char_point_list
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
        cv2.line(img, (little_X_point, little_Y_point), (large_X_point, large_Y_point), 255, 2)
    img = img[:max_y + 1, : max_x + 1]
    print(img.shape)
    # cv2.imshow('1', img)
    # cv2.waitKey(1)
    cv2.imwrite('E:/img/code_test/'+str(index)+'.png', img)

def show_line_img(line_point_list, index=1, get_img=True):
    per_char_point_list = []
    for line in line_point_list:
        per_char_point_list += line
    img = np.zeros((1000, 4000), np.uint8)  # 创建黑底图像
    pos_xy = per_char_point_list
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
        cv2.line(img, (little_X_point, little_Y_point), (large_X_point, large_Y_point), 255, 2)
    img = img[:max_y + 1, : max_x + 1]
    print(img.shape)
    # cv2.imshow('1', img)
    # cv2.waitKey(1)
    cv2.imwrite('E:/img/code_test/line_'+str(index)+'.png', img)
    if get_img:
        return img

def get_char_box(char_points):
    # 输入字符点集，得到左上角xy坐标以及右下角xy坐标
    char_points = list(filter(lambda x:x[0]!=-1, char_points))
    min_xy = np.array(char_points).min(axis=0)
    max_xy = np.array(char_points).max(axis=0)
    return min_xy[0], min_xy[1], max_xy[0], max_xy[1]

def get_line_box(line_chars_points):
    # 输入一行list，每个元素是字符集 e.g. line_chars_points = [char1,char2,char3...], 其中char1 = [[x1,y1],[x2,y2],...[-1,0]]
    min_x = 999999 ; min_y = 999999
    max_x = 0 ; max_y = 0
    for char_points in line_chars_points:
        if char_points == []:
            print('该字符为空！')
            continue
        x1, y1, x2, y2 = get_char_box(char_points)
        min_x = x1 if x1 < min_x else min_x
        min_y = y1 if y1 < min_y else min_y
        max_x = x2 if x2 > max_x else max_x
        max_y = y2 if y2 > max_y else max_y
    return min_x, min_y, max_x, max_y


def page_chars_list_resize_h_and_merge_lines(page_chars_list, resize_h=128, padding_h=0, padding_w=0, line_gap=6):
    add_shift_w = padding_w # 第一行先加用户自己设置的 padding_w 偏移量
    for line_chars_points in page_chars_list:
        min_x, min_y, max_x, max_y = get_line_box(line_chars_points)
        # 将所有点移到左上角 min_y就是最小的h，所以往上移min_y个像素，同理min_x左移
        for line_points in line_chars_points:
            for char_points in line_points:
                if char_points[0] != -1:
                    char_points[0] -= min_x
                    char_points[1] -= min_y
        # resize h
        origin_h = max_y - min_y
        h_scale = float(origin_h) / (resize_h - padding_h*2)
        for char_points_i, char_points in enumerate(line_chars_points):
            for point_index, point in enumerate(char_points):
                if point[0] != -1:
                    point[0] = int(point[0] / h_scale + 0.5)
                    point[1] = int(point[1] / h_scale + 0.5) + padding_h
                    char_points[point_index] = point
            line_chars_points[char_points_i] = point_filter(char_points) # 去掉重复点

        # 合并操作
        for char_points in line_chars_points:
            for char_point in char_points:
                if char_point[0] != -1:
                    char_point[0] += add_shift_w
        min_x, min_y, max_x, max_y = get_line_box(line_chars_points)
        # print(min_x)
        add_shift_w += (max_x - min_x) + padding_w
        # print(add_shift_w)
    page_merge_lines_list = []
    for line_chars_list in page_chars_list:
        page_merge_lines_list += line_chars_list
    return page_merge_lines_list


def split_page_merge_lines_to_chunks(page_merge_lines_list, label_list, chunk_size_w, padding_w=0):
    merge_label = ''
    for label in label_list:
        merge_label += label
    new_label_list = []

    label_num_list = []
    # 求出每一个字符的最大x轴
    max_x_list = [0]
    for char_list in page_merge_lines_list:
        if char_list == []:
            continue
        max_x = np.array(list(filter(lambda x:x[0]!=-1, char_list))).max(axis=0)[0]
        max_x_list.append(max_x)
    start_i =0
    start_x = max_x_list[0]
    chunk_size_w -= padding_w
    for i, max_x in enumerate(max_x_list):
        if max_x - start_x > chunk_size_w:
            # label_num_list.append([start_i + 1, i])
            # new_label_list.append(merge_label[start_i:i])
            temp_max_x = np.array(list(filter(lambda x: x[0] != -1, page_merge_lines_list[i-1]))).max(axis=0)[0]
            temp_min_x = np.array(list(filter(lambda x: x[0] != -1, page_merge_lines_list[i-1]))).min(axis=0)[0]
            char_w = temp_max_x - temp_min_x
            start_i = i-1
            start_x = max_x_list[i] - char_w - padding_w
            continue
            # print("出现错误！！！")
            # raise NotImplementedError("出现错误！！！")
        if i == len(max_x_list) - 1:
            label_num_list.append([start_i + 1, i])
            new_label_list.append(merge_label[start_i:i])
            continue
        if max_x - start_x <= chunk_size_w and max_x_list[i+1] - start_x > chunk_size_w:
            label_num_list.append([start_i+1, i])
            new_label_list.append(merge_label[start_i:i])
            start_i = i
            start_x = max_x_list[i]
    return label_num_list, new_label_list

def draw_chunk_img_line(args, chunk_points):
    chunk_size = args.chunk_size
    per_char_point_list = []
    for line in chunk_points:
        per_char_point_list += line
    img = np.zeros(chunk_size, np.uint8)  # 创建黑底图像
    pos_xy = per_char_point_list
    max_x, max_y, pos_xy = get_points_box(pos_xy)
    add_h = (chunk_size[0] - max_y) // 2
    if (chunk_size[1] - max_x) // 2 <= args.padding_w*2:
        add_w = (chunk_size[1] - max_x) // 2
    else:
        add_w = args.padding_w
    for point in pos_xy:
        if point[0] != -1:
            point[0] += add_w
            point[1] += add_h
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
        cv2.line(img, (little_X_point, little_Y_point), (large_X_point, large_Y_point), 255, 2)
    # img = img[:max_y + 1, : max_x + 1]
    # print(img.shape)
    # cv2.imwrite('E:/img/code_test/line.png', img)
    return img
