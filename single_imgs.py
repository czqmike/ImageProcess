# -*- coding: utf-8 -*-
'''
Author: czqmike
Date: 2021-09-08 16:31:59
LastEditTime: 2021-10-12 16:29:21
LastEditors: czqmike
Description: 
    脚本功能：将`source_dir`下的图片去重
    source: https://www.jianshu.com/p/c87f6f69d51f
Example:
    python single_imgs.py -s G:\path_to_dir
'''

import cv2
import numpy as np
import argparse
import os
import collections
import time
from rich.progress import Progress

## 解决cv2.imread()中文路径读取报错问题
def cv_imread(file_path): 
    cv_img = cv2.imdecode(np.fromfile(file_path,dtype=np.uint8), 0) 
    return cv_img 

def flat_gen(x):
    def iselement(e):
        return not(isinstance(e, collections.Iterable) and not isinstance(e, str))
    for el in x:
        if iselement(el):
            yield el
        else:
            yield from flat_gen(el)   

def pHash(imgfile):
    # 加载并调整图片为32x32灰度图片
    img = cv_imread(imgfile)
    img = cv2.resize(img, (32, 32), interpolation=cv2.INTER_CUBIC)

    # 创建二维列表
    h, w = img.shape[:2]
    vis0 = np.zeros((h, w), np.float32)
    vis0[:h, :w] = img  # 填充数据

    # 二维Dct变换
    vis1 = cv2.dct(cv2.dct(vis0))
    # 拿到左上角的8 * 8
    vis1 = vis1[0:8, 0:8]

    # 把二维list变成一维list
    img_list = list(flat_gen(vis1.tolist()))

    # 计算均值
    avg = sum(img_list) * 1. / len(img_list)
    avg_list = ['0' if i < avg else '1' for i in img_list]

    # 得到哈希值 (一个16进制字符串，如：`0000fdcefeeeeede`，表示64位hash值)
    return ''.join(['%x' % int(''.join(avg_list[x:x + 4]), 2) for x in range(0, 8 * 8, 4)])

## 计算图像的laplacian响应的方差值用以去除模糊图片，经过简单测试，个人认为 <40 的图片可认为是模糊的
## source: https://blog.csdn.net/WZZ18191171661/article/details/96602043
def variance_of_laplacian(image):
	return cv2.Laplacian(image, cv2.CV_64F).var()

parser = argparse.ArgumentParser()
parser.add_argument("--source_dir", "-s", required=True, default=r"G:\path_to_dir", help="path to source image dir")
parse_res = parser.parse_args()
source_dir = parse_res.source_dir

cnt = 0
for root, dirs, files in os.walk(source_dir):
    for _ in files:
        cnt += 1

t = time.time()
S = set()
deleted_files = []
with Progress() as progress:
    task = progress.add_task("[cyan]singling images:", total=cnt)
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            img = os.path.join(root, file)
            try:
                img_hash = pHash(img)
                # print(img + " " + img_hash)
                if img_hash in S:
                    os.remove(img) # 有一位(16进制)不一样则删除，也就是说这里hamming distance为1-4
                    # [注] 如果想使用任意长度的hamming distance而非4的话，可以参考这篇文章 http://www.lanceyan.com/tech/arch/simhash_hamming_distance_similarity2-html.html
                    deleted_files.append(img)
                else:
                    S.add(img_hash)
            except Exception as e:
                print(e.args)
            finally:
                progress.update(task, advance=1)

with open('deleted_files.txt', 'w') as f:
    for file in deleted_files:
        f.write(file + '\n')

print("Before single: {} pics".format(cnt))
print("After single:  {} pics".format(len(S)) ) 
print("Unrepeated rate: {:.2f}%".format( (len(S) * 100. / (cnt + 1e-6)) ))
print("Total time: {} secs".format(time.time() - t))

# for root, dirs, files in os.walk(source_dir):
#     for file in files:
#         img_path = os.path.join(root, file)
#         vra = variance_of_laplacian(cv_imread(img_path))
#         if vra < 40:
#             print(img_path + ' ' + str(vra) )
