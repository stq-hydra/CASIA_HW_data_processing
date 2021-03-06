import os
import numpy as np
import cv2
import time
import copy

start_time = time.time()


def mkdir(path):
    path = path.strip().rstrip("\\")
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + ' 创建成功')
    else:
        print(path + ' 目录已存在')


def bytes2int(x):
    result = 0
    for index, byte in enumerate(x):
        result = result + int(byte << (index * 8))
    return result


save_dir = r'/home/datasets/textGroup/casia/CASIA_OLHWDB1_character_resize32' # 要保存数据的地方
version_dir = r"/home/datasets/textGroup/casia/source/CASIA-OLHWDB"   # 原始二进制文件(*.POT)对应路径 

size_mode = 'resize'  # basic : 保持原始大小 ; resize : 缩放点集
resize_hw = 96  # 把点集缩放到96之间，并生成96*96大小的图片(会padding)。如果图片太大或太小，自行调整笔画粗细(thickness)。

border = 2  # thickness - 1 四周留空白像素
background_color = 255  # 255 白底黑字；0 黑底白字
core_resize_hw = resize_hw - border * 2
thickness = 2  # 笔画粗细

all_class = set()  # 所有类别
path_label_list = []
path_label_list_train = []  # 标准训练集 需要在每个CASIA-OLHWDB1.x文件夹有trainlist.txt
path_label_list_test = []  # 标准测试集 需要在每个CASIA-OLHWDB1.x文件夹有testlist.txt

version_dir_list = os.listdir(version_dir)
for version in version_dir_list:  # CASIA-OLHWDB1.0-1.2
    absolute_version_path = os.path.join(version_dir, version)
    pot_file_names = [files for files in os.listdir(absolute_version_path) if files.endswith('pot')]
    # pot_file_names = [files for files in os.listdir(os.path.join(version_dir, version, "Data_POT")) if files.endswith('pot')]   # 如果你的路径还有一层 Data_POT 文件夹
    mkdir(os.path.join(save_dir, version))
    train_pot_list = []
    test_pot_list = []
    if os.path.exists(absolute_version_path + '/trainlist.txt'):  # 可以不加这行
        with open(absolute_version_path + '/trainlist.txt', 'r', encoding='utf8') as f:
            train_pot_list = f.readlines()
            train_pot_list = [train_pot.replace('\n', '') for train_pot in train_pot_list]
        with open(absolute_version_path + '/testlist.txt', 'r', encoding='utf8') as f:
            test_pot_list = f.readlines()
            test_pot_list = [test_pot.replace('\n', '') for test_pot in test_pot_list]

    for pot_file in pot_file_names:
        with open(os.path.join(version_dir, version, pot_file), 'rb') as f:
            per_people_counter = 1
            writer_index = pot_file.split('.')[0]
            print(os.path.join(version_dir, version, pot_file))
            count = 0
            while True:
                ucX, ucY, pen_down_index = [], [], []
                min_ucX = 100000
                min_ucY = 100000
                if size_mode == 'resize':
                    img = np.zeros((resize_hw, resize_hw), np.uint8)  # 创建黑底图像
                else:
                    img = np.zeros((500, 500), np.uint8)  # 创建黑底图像
                img.fill(background_color)  # 填白
                count += 1
                SampleSize = bytes2int(np.fromfile(f, dtype='ushort', count=1))
                if SampleSize == 0:
                    # print('count = ', count)
                    break
                TagCode = np.fromfile(f, dtype='uint8', count=4)
                TagCode = TagCode[::-1]
                label = str(bytes(TagCode).decode('gbk'))[2].encode('utf8').decode('utf8')
                StrokeNumber = bytes2int(np.fromfile(f, dtype='ushort', count=1))
                for stroke_index in range(StrokeNumber):
                    while True:
                        temp_X = bytes2int(np.fromfile(f, dtype='short', count=1))  # 该点的横坐标
                        temp_Y = bytes2int(np.fromfile(f, dtype='short', count=1))  # 该点的纵坐标
                        if temp_X == -1 and temp_Y == 0:
                            ucX.append(-1)
                            ucY.append(0)
                            break
                        ucX.append(temp_X)
                        ucY.append(temp_Y)
                        if temp_X < min_ucX:
                            min_ucX = temp_X
                        if temp_Y < min_ucY:
                            min_ucY = temp_Y
                CharacterEnd_X = bytes2int(np.fromfile(f, dtype='short', count=1))
                CharacterEnd_Y = bytes2int(np.fromfile(f, dtype='short', count=1))

                per_people_counter += 1
                if len(ucX) == 1 or len(ucX) == 2 and ucX[1] < 0:
                    continue
                ucX = [X - min_ucX for X in ucX]
                ucY = [Y - min_ucY for Y in ucY]
                if size_mode == 'resize':  # 处理点坐标范围在 core_resize_hw 以内
                    ratio = max(ucX) / core_resize_hw if max(ucX) > max(ucY) else max(ucY) / core_resize_hw
                    ucX = [int(X / ratio - 0.5) for X in ucX]  # 这里笔画间标志(-1,0)会变得更小，但不影响结果
                    ucY = [int(Y / ratio - 0.5) for Y in ucY]
                elif size_mode != 'basic':
                    print('没有这个处理方式！可选 [ basic | resize ]')
                    raise KeyError()

                ### 绘字
                first_point = True
                for X_index, temp_ucX in enumerate(ucX):
                    # if ucX[X_index] == -1 and ucY[X_index] == 0:
                    if ucX[X_index] < 0:
                        pen_down_index.append(X_index)
                        first_point = True
                        continue
                    if first_point is False:
                        little_X_point = ucX[X_index - 1]
                        large_X_point = ucX[X_index]
                        little_Y_point = ucY[X_index - 1]
                        large_Y_point = ucY[X_index]
                        cv2.line(img, (little_X_point, little_Y_point), (large_X_point, large_Y_point),
                                 255 - background_color, thickness)
                    else:
                        first_point = False
                index_count = 0
                for index in pen_down_index:
                    del ucX[index - index_count]
                    del ucY[index - index_count]
                    index_count += 1

                img_relative_path = version + '/' + writer_index + '_' + str(per_people_counter).rjust(4, '0') + '.png'
                save_absolute_path = save_dir + '/' + img_relative_path

                save_img = copy.deepcopy(img[min(ucY):max(ucY) + 1, min(ucX): max(ucX) + 1])
                if size_mode == 'resize':
                    h, w = save_img.shape
                    pad_top = (resize_hw - h) // 2
                    pad_left = (resize_hw - w) // 2
                    img.fill(background_color)
                    img[pad_top:pad_top + h, pad_left:pad_left + w] = save_img
                    save_img = img

                # print(save_absolute_path)

                # 准备写入txt文件作为label
                txt_append = img_relative_path + ' ' + label + '\n'
                path_label_list.append(txt_append)
                if writer_index in train_pot_list:
                    path_label_list_train.append(txt_append)
                    all_class.add(label)  # 更新总类别
                elif writer_index in test_pot_list:
                    path_label_list_test.append(txt_append)
                    all_class.add(label)  # 更新总类别

                try:
                    cv2.imencode('.png', save_img)[1].tofile(save_absolute_path)
                except:
                    print(min(ucX), max(ucX), min(ucY), max(ucY))
                    raise OSError

with open(save_dir + '/OLHWDB1.txt', 'w', encoding='utf8') as f:
    f.writelines(path_label_list)
with open(save_dir + '/OLHWDB1_train.txt', 'w', encoding='utf8') as f:
    f.writelines(path_label_list_train)
with open(save_dir + '/OLHWDB1_test.txt', 'w', encoding='utf8') as f:
    f.writelines(path_label_list_test)

print('总样本数 =', len(path_label_list))
print('训练集数 =', len(path_label_list_train))
print('测试集数 =', len(path_label_list_test))
print('总类别数 =', len(all_class))  # 7356
print()


total_time = time.time() - start_time
m, s = divmod(total_time, 60)
h, m = divmod(m, 60)
print("用时：%02d小时:%02d分:%02d秒" % (h, m, s))
