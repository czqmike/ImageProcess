'''
Author: czqmike
Date: 2021-09-06 14:35:24
LastEditTime: 2021-09-18 13:00:21
LastEditors: czqmike
Description: 
    脚本功能：筛选出尺寸大于size*size, 物理大小大于storage kb的，
    并且图片后缀为`jpg, jpeg, png`的图片，将其按照原有文件夹结构另存为`path_to_saved_dir`
Example:
    python filter_imgs.py -i G:\path_to_dir -o G:\path_to_dir
'''
import os
import argparse
from PIL import Image
import shutil
from rich.progress import Progress


## Return file size (kbs)
def get_storage(path: str):
    if not os.path.exists(path):
        return 0
    return os.path.getsize(path) / 1024

def is_size_ok(path: str, size: float):
    if not os.path.exists(path):
        return False
    img = Image.open(path)
    return img.size[0] > size and img.size[1] > size

def is_type_ok(path: str, ends_with: list):
    if not os.path.exists(path):
        return False
    return os.path.split(path)[-1].split('.')[-1].lower() in ends_with

parser = argparse.ArgumentParser()
parser.add_argument("--path_to_imgs", "-i", required=True, default=r" G:\path_to_dir", help="path to source image dir")
parser.add_argument("--path_to_saving_dir", "-o", required=True, default=r" G:\path_to_dir", help="path of saving dir, different with `path_to_imgs`")
parser.add_argument("--size", required=False, type=float, default=400., help="pixel of min size of images")
parser.add_argument("--storage", required=False, type=float, default=30., help="min storage of kbs of saving images")
parser.add_argument("--image_types", required=False, type=list, default=['png', 'jpg', 'jpeg'], help="types of images")
parse_res = parser.parse_args()

source_dir = parse_res.path_to_imgs
saving_dir = parse_res.path_to_saving_dir
size = parse_res.size
storage = parse_res.storage
ends_with = parse_res.image_types
source_name = source_dir.split(os.path.sep)[-1]

cnt = 0
for root, dirs, files in os.walk(source_dir):
    for _ in files:
        cnt += 1

cp_cnt = 0
with Progress() as progress:
    task = progress.add_task("[cyan]copying...", total=cnt)
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            d = os.path.join(root, file)
            try:
                if is_type_ok(d, ends_with) and get_storage(d) > storage and is_size_ok(d, size):
                    sd = d.replace(source_dir, saving_dir)
                    p = os.path.split(sd)[0]
                    if not os.path.exists(p):
                        os.makedirs(p)
                    shutil.copy(d, sd)
                    cp_cnt += 1
            except Exception as e:
                print("[Error]", e.args)
            finally:
                progress.update(task, advance=1)

print("Progress finished, copied {} files.".format(cp_cnt))
