import os

def mkdir(path):
    path = path.strip().rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        print(path + ' 创建成功')
        return True
    else:
        print(path + ' 目录已存在')
        return False

def bytes2int(x):
    result = 0
    for index, byte in enumerate(x):
        result = result + int(byte << (index * 8))
    return result