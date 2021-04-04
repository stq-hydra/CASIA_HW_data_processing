# CASIA 手写中文数据处理
CASIA-HWDB1-2、CASIA-OLHWDB1-2、ICDAR2013联机脱机等中文手写数据处理

## 开始
### ①CASIA-OLHWDB1
把transformCASIA-OLHWDB1.x.py文件中的：<br/>
> save_dir 换成 你要保存生成的图片的位置<br/>
version_dir 换成 原始二进制文件(*.POT)对应路径
<br/>

其他选项比如()：<br/>
> size_mode 		=> 可选[basic | resize]。其中basic : 保持原始大小 ; resize : 缩放点集<br/>
resize_hw 			=> 要将图片缩放成多大默认96X96，如果size_mode='basic'则这个不生效<br/>
background_color 	=> 255 白底黑字；0 黑底白字<br/>
border 				=> 四周留空白的像素个数<br/>

然后执行命令
```
python transformCASIA_OLHWDB1.py
```


## TODO
单字生成：
- [ ] CASIA-HWDB1
- [ ] CASIA-HWDB2
- [X] CASIA-OLHWDB1
- [ ] CASIA-OLHWDB2
- [ ] ICDAR2013-offline
- [ ] ICDAR2013-online

文本行生成：
- [ ] CASIA-HWDB2
- [ ] CASIA-OLHWDB2
- [ ] ICDAR2013-offline
- [ ] ICDAR2013-online

<br/>

- [ ] 速度优化

数据来源：
[CASIA Online and Offline Chinese Handwriting Databases](http://www.nlpr.ia.ac.cn/databases/handwriting/Home.html)