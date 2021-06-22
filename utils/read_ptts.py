import cv2, math, os, numpy as np
from utils.core_region import core_region_resize, core_region_estimation
from utils.operation_file import bytes2int
from utils.operation_points import get_points_box, point_filter, Nrotation_angle_get_coor_coordinates, show_char_img, page_chars_list_resize_h_and_merge_lines, split_page_merge_lines_to_chunks, draw_chunk_img_line


def read_ptts_to_img_line(args, ptts_file_path, train_or_test='Train_Ptts'):
    # 注意：这里 train set 去掉了error code，但test set没有
    img_line_list = []
    label_list = []
    ucX = []
    ucY = []
    aX = []
    aY = []
    CharStrokeIndex = []
    stroke2PointNumber = []  # 存储各个笔画的点数（第i笔有多少个点）
    point_count_list = []
    error_character = False
    max_width = []

    # line
    line_aX = []
    line_points = []
    LineStrokeIndex = []
    with open(ptts_file_path, 'rb') as f:
        SizeOfheader = bytes2int(np.fromfile(f, dtype='uint8', count=4))
        FormatCode = np.fromfile(f, dtype='uint8', count=8)
        illustration_length = SizeOfheader - 54
        illustration = np.fromfile(f, dtype='uint8', count=illustration_length)
        # illustration_str = str(bytes(illustration).decode('gbk'))
        CodeType = np.fromfile(f, dtype='uint8', count=20)
        # CodeType_str = str(bytes(CodeType).decode('gbk'))
        CodeLength = bytes2int(np.fromfile(f, dtype='uint8', count=2))
        DataType = np.fromfile(f, dtype='uint8', count=20)
        # DataType_str = str(bytes(DataType).decode('gbk'))
        SampleLength = bytes2int(np.fromfile(f, dtype='uint8', count=4))
        PageIndex = bytes2int(np.fromfile(f, dtype='uint8', count=4))
        StrokeNumber = bytes2int(np.fromfile(f, dtype='uint8', count=4))  # 总的笔画数
        for stroke_index in range(StrokeNumber):
            PointNumber = bytes2int(np.fromfile(f, dtype='short', count=1))  # 这个笔画一共有几个点
            stroke2PointNumber.append(PointNumber)  # 存储每笔对应有几个点
            for point_index in range(PointNumber):
                temp_X = bytes2int(np.fromfile(f, dtype='ushort', count=1))
                temp_Y = bytes2int(np.fromfile(f, dtype='ushort', count=1))
                ucX.append(temp_X)
                ucY.append(temp_Y)
        point_count_sum = 0
        point_count_list.append(0)
        for point_count_i in range(len(stroke2PointNumber)):
            point_count_list.append(point_count_sum + stroke2PointNumber[point_count_i])
            point_count_sum += stroke2PointNumber[point_count_i]
        LineNumber = bytes2int(np.fromfile(f, dtype='ushort', count=1))  # 一共有几行
        for line_index in range(LineNumber):
            LineStrokeNumber = bytes2int(np.fromfile(f, dtype='ushort', count=1))  # 一行有几个笔画
            for line_stroke_index in range(LineStrokeNumber):
                LineStrokeIndex.append(bytes2int(np.fromfile(f, dtype='ushort', count=1)))
            LineCharNumber = bytes2int(np.fromfile(f, dtype='ushort', count=1))  # 一行几个字符
            del line_points[:]
            if args.fix_size:
                img_line = np.zeros((args.SAVE_HEIGHT, args.fix_w), np.uint8)  # 创建黑底图像 984 2121 4311
            else:
                img_line = np.zeros((args.SAVE_HEIGHT, args.SAVE_HEIGHT * 35), np.uint8)  # 创建黑底图像 984 2121 4311
            line_rgb = (255, 255, 255)
            if args.bgColor_white:
                img_line.fill(255)  # 填白
                line_rgb = (0,0,0)
            line_label = ''
            for line_char_index in range(LineCharNumber):
                del aX[:]
                del aY[:]
                del CharStrokeIndex[:]
                TagCode = np.fromfile(f, dtype='uint8', count=CodeLength)
                # TagCode = TagCode[::-1]
                if TagCode[0] == 255 and TagCode[1] == 255:
                    error_character = True
                    # print('character error code')
                    args.error_character_num += 1
                    if args.error_character_num % 10 == 0:
                        print(args.error_character_num)
                else:
                    label = str(bytes(TagCode).decode('gbk'))[0].encode('utf8').decode('utf8')
                    line_label += label
                CharStrokeNumber = bytes2int(np.fromfile(f, dtype='ushort', count=1))  # 这个字的笔画数
                for ii in range(CharStrokeNumber):
                    CharStrokeIndex.append(bytes2int(np.fromfile(f, dtype='ushort', count=1)))
                ###画图
                for char_stroke_index in CharStrokeIndex:
                    temp_point_number = stroke2PointNumber[char_stroke_index]
                    for X_index in range(temp_point_number):
                        aX.append(ucX[point_count_list[char_stroke_index] + 1 + X_index - 1])
                        aY.append(ucY[point_count_list[char_stroke_index] + 1 + X_index - 1])
                if error_character == True and train_or_test == 'Train_Ptts':
                    error_character = False
                    print('continue')
                    continue

                aX_count = 0
                for char_stroke_index in CharStrokeIndex:
                    temp_point_number = stroke2PointNumber[char_stroke_index]
                    for X_index in range(temp_point_number):
                        line_points.append([aX[aX_count + X_index], aY[aX_count + X_index]])
                    aX_count += temp_point_number
                    line_points.append([-1, 0])
            if not args.DEBUG:  # debug下不进行拟合等操作
                # huber 线性拟合
                if args.rectify_flag:
                    temp_line_aX = []
                    temp_line_aY = []
                    for point_i in line_points:
                        if point_i[0] != -1:
                            temp_line_aX.append(point_i[0])
                            temp_line_aY.append(point_i[1])
                    # print(max(line_aX))
                    temp_max_width = max(temp_line_aX) - min(temp_line_aX)
                    temp_max_height = max(temp_line_aY) - min(temp_line_aY)
                    # print(temp_max_width, temp_max_height)
                    # 记录并去掉-1,0
                    stroke_stop_index_list = []  # 记录所有-1,0 的位置
                    for stroke_stop_i, line_point in enumerate(line_points):
                        if line_point == [-1, 0]:
                            stroke_stop_index_list.append(stroke_stop_i)
                    line_points = list(filter(lambda x: x != [-1, 0], line_points))
                    if temp_max_width / temp_max_height >= 3:  # 宽度为高度的3倍以上才拟合
                        line_points = np.array(line_points)  # loc 必须为矩阵形式，且表示[x,y]坐标
                        [vx, vy, x, y] = cv2.fitLine(line_points, cv2.DIST_HUBER, 0, 0.01, 0.01)
                        k = vy / vx
                        b = y - k * x
                        angle = math.degrees(math.atan(k))
                        # print('倾斜角 = ' + str(angle))
                        lefty = int(((0 - x) * vy / vx) + y)
                        line_points = line_points.tolist()
                        for point_index, point_i in enumerate(line_points):
                            line_points[point_index] = Nrotation_angle_get_coor_coordinates(point_i, [0, lefty], angle)
                    if args.core_region_flag:  # 核心区域估计
                        y1, y2 = core_region_estimation(line_points, args.core_percentage)
                    # else:
                    #     if args.core_region_flag:  # 核心区域估计
                    #         y1, y2 = core_region_estimation(line_points, args.core_percentage)
                    # 恢复
                    for stroke_stop_i in stroke_stop_index_list:
                        line_points.insert(stroke_stop_i, [-1, 0])
                if args.core_region_flag:
                    # core region缩放到 26
                    line_points = core_region_resize(args.SAVE_HEIGHT, args.core_percentage, line_points, y1, y2)
                else:
                    # draw img_line use line_aX
                    box_w, box_h, line_points = get_points_box(line_points)
                    h_scale = float(box_h) / (args.SAVE_HEIGHT - args.padding_h*2)
                    if args.fix_size:
                        w_scale = float(box_w) / (args.fix_w - 2)
                        if w_scale > h_scale:
                            for point_index, point in enumerate(line_points):
                                if point[0] == -1:
                                    continue
                                point[0] = point[0] / w_scale
                                point[1] = point[1] / w_scale
                                point[0] = int(point[0] + 0.5)
                                point[1] = int(point[1] + 0.5)
                                line_points[point_index] = point
                            _, max_h, _ = get_points_box(line_points, shift=False)
                            if max_h >= 1:
                                add_y = (args.SAVE_HEIGHT - max_h) // 2
                                for point_index, point in enumerate(line_points):
                                    point[1] = point[1] + add_y
                                    line_points[point_index] = point
                        else:
                            for point_index, point in enumerate(line_points):
                                if point[0] == -1:
                                    continue
                                point[0] = point[0] / h_scale
                                point[1] = point[1] / h_scale
                                point[0] = int(point[0] + 0.5)
                                point[1] = int(point[1] + 0.5)
                                line_points[point_index] = point
                    else:
                        for point_index, point in enumerate(line_points):
                            if point[0] == -1:
                                continue
                            point[0] = point[0] / h_scale
                            point[1] = point[1] / h_scale
                            point[0] = int(point[0] + 0.5)
                            point[1] = int(point[1] + 0.5)
                            line_points[point_index] = point

                # 过滤相邻重复点和只有一个点的情况
                line_points = point_filter(line_points)
                
                for line_point in line_points:
                    if line_point[0] != -1:
                        line_point[0] += args.padding_w
                        line_point[1] += args.padding_h
                first_point = True

                # Path Signature
                pass

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
                    cv2.line(img_line, (little_X_point, little_Y_point), (large_X_point, large_Y_point),
                             line_rgb, args.pen_thickness)

                del line_aX[:]
                for point_i in line_points:
                    if point_i[0] != -1:
                        line_aX.append(point_i[0])
                # print(max(line_aX))
                max_width.append(max(line_aX))
                try:
                    if not args.fix_size:
                        img_line = img_line[:, : max(line_aX) + 1 + args.padding_w]
                except:
                    raise OSError
                img_line_list.append(img_line)
            label_list.append(line_label)
    return img_line_list, label_list


def read_ptts_to_img_line_chunks_by_page_semantic(args, ptts_file_path, train_or_test='Train_Ptts'):
    # 一些初始化操作
    chunk_size = args.chunk_size
    # 核心操作部分
    img_list = []
    page_chars_list, label_list = get_ptts_page_lines_chars(args, ptts_file_path, train_or_test) # 放回所有字符和label
    page_merge_lines_list = page_chars_list_resize_h_and_merge_lines(page_chars_list, resize_h=chunk_size[0], padding_h=args.padding_h, padding_w=args.padding_w)
    chunks_list, new_label_list = split_page_merge_lines_to_chunks(page_merge_lines_list, label_list, chunk_size_w=chunk_size[1], padding_w=args.padding_w)
    for chunk_range in chunks_list:
        chunk_points = page_merge_lines_list[chunk_range[0]-1:chunk_range[1]]
        img = draw_chunk_img_line(args, chunk_points)
        img_list.append(img)
    return img_list, new_label_list

def get_ptts_page_lines_chars(args, ptts_file_path, train_or_test='Train_Ptts'):
    # 输入一个PTTS，根据自己设定的大小分割成N个文本行图片
    # 注意：train set 去掉了error code，但test set没有
    label_list = []
    ucX = []
    ucY = []
    aX = []
    aY = []
    CharStrokeIndex = []
    stroke2PointNumber = []  # 存储各个笔画的点数（第i笔有多少个点）
    point_count_list = []
    error_character = False
    # line
    line_aX = []
    line_points = []
    LineStrokeIndex = []
    with open(ptts_file_path, 'rb') as f:
        SizeOfheader = bytes2int(np.fromfile(f, dtype='uint8', count=4))
        FormatCode = np.fromfile(f, dtype='uint8', count=8)
        illustration_length = SizeOfheader - 54
        illustration = np.fromfile(f, dtype='uint8', count=illustration_length)
        # illustration_str = str(bytes(illustration).decode('gbk'))
        CodeType = np.fromfile(f, dtype='uint8', count=20)
        # CodeType_str = str(bytes(CodeType).decode('gbk'))
        CodeLength = bytes2int(np.fromfile(f, dtype='uint8', count=2))
        DataType = np.fromfile(f, dtype='uint8', count=20)
        # DataType_str = str(bytes(DataType).decode('gbk'))
        SampleLength = bytes2int(np.fromfile(f, dtype='int', count=1))
        PageIndex = bytes2int(np.fromfile(f, dtype='int', count=1))
        StrokeNumber = bytes2int(np.fromfile(f, dtype='int', count=1))  # 总的笔画数
        for stroke_index in range(StrokeNumber):
            PointNumber = bytes2int(np.fromfile(f, dtype='short', count=1))  # 这个笔画一共有几个点
            stroke2PointNumber.append(PointNumber)  # 存储每笔对应有几个点
            for point_index in range(PointNumber):
                temp_X = bytes2int(np.fromfile(f, dtype='ushort', count=1))
                temp_Y = bytes2int(np.fromfile(f, dtype='ushort', count=1))
                ucX.append(temp_X)
                ucY.append(temp_Y)
        point_count_sum = 0
        point_count_list.append(0)
        for point_count_i in range(len(stroke2PointNumber)):
            point_count_list.append(point_count_sum + stroke2PointNumber[point_count_i])
            point_count_sum += stroke2PointNumber[point_count_i]
        LineNumber = bytes2int(np.fromfile(f, dtype='ushort', count=1))  # 一共有几行
        page_chars_list = []
        for line_index in range(LineNumber):
            LineStrokeNumber = bytes2int(np.fromfile(f, dtype='ushort', count=1))  # 一行有几个笔画
            for line_stroke_index in range(LineStrokeNumber):
                LineStrokeIndex.append(bytes2int(np.fromfile(f, dtype='ushort', count=1)))
            LineCharNumber = bytes2int(np.fromfile(f, dtype='ushort', count=1))  # 一行几个字符
            del line_points[:]
            line_label = ''
            line_chars_list = []
            for line_char_index in range(LineCharNumber):
                del aX[:]
                del aY[:]
                del CharStrokeIndex[:]
                TagCode = np.fromfile(f, dtype='uint8', count=CodeLength)
                # TagCode = TagCode[::-1]
                if TagCode[0] == 255 and TagCode[1] == 255:
                    error_character = True
                    print('character error code')
                else:
                    label = str(bytes(TagCode).decode('gbk'))[0].encode('utf8').decode('utf8')
                    line_label += label
                CharStrokeNumber = bytes2int(np.fromfile(f, dtype='ushort', count=1))  # 这个字的笔画数
                for ii in range(CharStrokeNumber):
                    CharStrokeIndex.append(bytes2int(np.fromfile(f, dtype='ushort', count=1)))

                if error_character == True and train_or_test == 'Train_Ptts':
                    error_character = False
                    print('continue')
                    continue

                ###画图
                per_char_point_list = []    # 每个字符的点集
                for char_stroke_index in CharStrokeIndex:
                    temp_point_number = stroke2PointNumber[char_stroke_index]
                    for X_index in range(temp_point_number):
                        temp_X = ucX[point_count_list[char_stroke_index] + 1 + X_index - 1]
                        temp_Y = ucY[point_count_list[char_stroke_index] + 1 + X_index - 1]
                        aX.append(temp_X)
                        aY.append(temp_Y)
                        per_char_point_list.append([temp_X, temp_Y])
                    per_char_point_list.append([-1,0])
                # show_char_img(per_char_point_list, line_char_index)
                if len(per_char_point_list) != 0:
                    line_chars_list.append(per_char_point_list)

            label_list.append(line_label)
            page_chars_list.append(line_chars_list)
    return page_chars_list, label_list