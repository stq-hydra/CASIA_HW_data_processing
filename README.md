# <center>CASIA 手写中文数据处理</center>

CASIA-HWDB1-2、CASIA-OLHWDB1-2、ICDAR2013联机脱机等中文手写数据处理

## 单字生成
### ①CASIA-OLHWDB1

---
把**transformCASIA-OLHWDB1.py**文件中：<br/>


`save_dir`：换成 你要保存生成的图片的位置<br/>
`version_dir`：换成 原始二进制文件(*.POT)对应路径

<br/>
其他选项比如：<br/>

* `size_mode`：可选[basic | resize]。其中basic : 保持原始大小 ; resize : 缩放点集


* `resize_hw`：要将图片缩放成多大，默认96X96，如果size_mode='basic'则这个不生效<br/>


* `background_color`：255 白底黑字；0 黑底白字<br/>


* `border`：四周留空白的像素个数<br/>

<br/>

然后执行命令
```
python transformCASIA-OLHWDB1.py
```

## 文本行生成
### ①CASIA-OLHWDB2 （默认linux版本，windows版本看55行，改改就行）


---
在**transformCASIA-OLHWDB2.py**文件中：<br/>
修改22行为：原始PTTS二进制文件 <br/>
修改23行为：生成的图片要存储的路径 <br/>

--rectify_flag 这里默认True，即huber线性拟合后进行矫正<br/> 


然后执行命令
```
python transformCASIA-OLHWDB2.py
```

<br/>

```
文件夹结构：
 CASIA-OLHWDB2       (总共：52220张文本行， 训练集41710张，测试集10510张)
 ├----CASIA-OLHWDB2.0     (20573张文本行)   (001-P16.ptts => 420-P20.ptts)
 │    ├--Train_Ptts                                                       (336 writers)
 │    └--Test_Ptts                                                        (84  writers)
 ├----CASIA-OLHWDB2.1     (17282张文本行)
 │    ├--Train_Ptts                       (1001-P16.ptts => 1240-P20.ptts, 240 writers)
 │    └--Test_Ptts                        (1241-P16.ptts => 1300-P20.ptts, 60  writers)
 └----CASIA-OLHWDB2.2     (14365张文本行)
      ├--Train_Ptts                       (501-P14.ptts  => 740-P18.ptts,  239 writers, 缺第671位writer)
      └--Test_Ptts                        (741-P14.ptts  => 800-P18.ptts,  60  writers)
          └--XXX.ptts
```

内容比较多，如果有错请指正。图片的核心区域估计仅供参考，应该还能再改改。

<br/> 

## 常用类别 classes

- [X] HWDB2_2703.py		(CASAI-HWDB2文本行的训练集总字符类别)
- [X] HWDB2_7373.py
- [X] OLHWDB12_7356.py	(CASAI-OLHWDB1单字的训练集总字符类别)
- [X] OLHWDB12_7366.py	(CASAI-OLHWDB1单字、CASAI-OLHWDB2文本行的训练集总字符类别)
- [X] OLHWDB2_2650.py   (CASAI-OLHWDB2文本行的训练集总字符类别)



---

## TODO
单字生成：
- [ ] CASIA-HWDB1
- [ ] CASIA-HWDB2
- [X] CASIA-OLHWDB1
- [ ] CASIA-OLHWDB2

文本行生成：
- [ ] CASIA-HWDB2
- [X] CASIA-OLHWDB2      	包括拟合后矫正、核心区域估计(core estimate)、~~path signature~~
- [ ] ICDAR2013-offline  	包括拟合后矫正
- [ ] ICDAR2013-online	 	包括拟合后矫正、core estimate


<br/>

- [ ] 速度优化

数据来源：
[CASIA Online and Offline Chinese Handwriting Databases](http://www.nlpr.ia.ac.cn/databases/handwriting/Home.html)