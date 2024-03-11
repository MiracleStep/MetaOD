# this file acts like the gym of OpenAL 
# to set up our environment, 
# we need one initial image and one object image 
# then it paste the object image over the background 
# with (x,y) provided by agent 
import os
import numpy as np
import sys
# ����ļ����ڽ���ͼ���ʼ���Ͳ���
from PIL import Image, ImageOps


def init(bg, ob):
    save_base_path(bg)
    save_object_path(ob)


def save_base_path(bg):
    with open("./background_path.txt", 'w') as f:
        f.write(bg)


def save_object_path(ob):
    with open("./object_path.txt", 'w') as f:
        f.write(ob)


def object_image_path():
    with open("./object_path.txt", 'r') as f:
        l = f.readlines()[0]
    return l


def background_image_path():
    with open("./background_path.txt", 'r') as f:
        l = f.readlines()[0]
    return l

# ����idx����ͼ���Ψһ·��
def synthesized_imagepath(idx):
    base = "./new_"
    path = base + str(idx) + ".png"
    return path


# ���ú���insert_image()���в���
def mutate(x, y, idx):
    # paste ob over bg and synthesize a new image
    return insert_image(x, y, idx)

# Ŀ��ͼ����뵽����ͼ����
def insert_image(x, y, idx):
    obj_img = Image.open(object_image_path(), 'r')
    # obj_img.thumbnail(size, Image.ANTIALIAS)
    bg_img = Image.open(background_image_path())

    bg_img.paste(obj_img.convert('RGBA'), (x, y), mask=obj_img.convert('RGBA'))
    new_path = synthesized_imagepath(idx) # ����ͼ�񱣴��·��
    bg_img.save(new_path)

    return new_path

# Ŀ��ͼ����뵽����ͼ�����������浽�ļ�����
def insert_image_and_save(x, y, idx):
    output_dir = "../insert_saved_image"
    os.makedirs(output_dir, exist_ok=True)
    obj_img = Image.open(object_image_path(), 'r')
    bg_img = Image.open(background_image_path())

    bg_img.paste(obj_img.convert('RGBA'), (x, y), mask=obj_img.convert('RGBA'))
    new_path = os.path.basename(background_image_path())
    new_path = new_path.split(".")[0]
    bg_img.save(os.path.join(output_dir, new_path + "_" + str(idx) + ".jpg"))
    return new_path
