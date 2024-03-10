# this is the whole workflow three modules

import os
import shutil
import sys
sys.path.append('../')
import object_refinement.refinement_process as RP
import os.path
from os import walk



class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

# 删除和创建文件夹
def clean():
    print("clean")
    # os.system("rm -rf ../object_extraction/result/*")
    # os.system("rm -rf ../image_pool/")
    # os.system("rm -rf ../object_pool/")
    try:
        shutil.rmtree("../object_extraction/result/", ignore_errors=True)
        shutil.rmtree("../image_pool/", ignore_errors=True)
        shutil.rmtree("../object_pool/", ignore_errors=True)

        os.mkdir("../image_pool/")
        os.mkdir("../object_pool/")
        os.mkdir("../object_extraction/result")
        os.mkdir("../object_extraction/result/Step0_object_detection")
        os.mkdir("../object_extraction/result/Step1_extract_object")
        os.mkdir("../object_extraction/result/Step2_save_into_seperate")
        os.mkdir("../object_extraction/result/pool")
    except :
        print("")

# 进行对象分割，提取分割目标到目标池(object_pool)
def process_object_extraction(images):
    # extract objects and save into pools 
    # let's randomly select N 
    # images from the COCO pool
    with cd("../object_extraction/"):
        for i in images:
            pass
            # os.system("python image_disection.py " + i) # 进行分割图像

        # 生成目标池和图像池
        os.system("python image_cluster.py result/Step2_save_into_seperate/ result/pool/")
        os.system("mv result/pool/* ../object_pool/")
        os.system("mv result/Step2_save_into_seperate/* ../image_pool/")

# 初始化目标改良/细化
def init_object_refinement():
    # refinement; clustering and so on
    # basically even if we skip this one, we still can 
    # proceed the following steps, right?
    target_dir = "../object_pool/"
    image_dir = "../image_pool/"
    RP.init(target_dir, image_dir)


def valid_image(i):
    # ../image_pool/000000313994/obj
    i1 = i.split(".")[0]
    return os.path.isfile("../image_pool/" + i1 + "/object.log")


def process_object_refinement(i):
    return RP.process(i)


def get_obj_list(obj_name, i, c):
    print (obj_name, i, c)
    # the baseline approach is to extract all the objects with 
    # the same label, after the clustering with set of the same label
    # ../obj_pool/label/
    obj_name = obj_name.replace(" ", "-")
    with cd("../object_pool/" + obj_name):
        # ideally, we have several clusters right here, 
        # and we try all objects within the same cluster with obj_name

        # 1. find the object within a cluster 
        r = None
        for (dirpath, dirnames, filenames) in walk("."):
            for f in filenames:
                if (i + "_" + str(c)) in f:
                    # OK, we are in the right cluster
                    target_dir = dirpath
                    r = os.listdir(target_dir)
                    break
        assert r
        return r


def resize(label, lines):
    # input: label:要插入对象的标签 lines: 图像所有的标签数据
    c = 0
    xs = 0
    ys = 0
    for l in lines:
        if label.replace("-", " ") in l:
            items = l.strip().split(",")
            x1 = int(items[2])
            x2 = int(items[3])
            y1 = int(items[4])
            y2 = int(items[5][:-1])
            xs += abs(x2-x1)
            ys += abs(y2-y1)
            c += 1

    if (c == 0): # 图像没有要插入对象的标签：计算所有图像目标宽高的平均值
        # just take the average
        return resize("", lines)
    else: # 图像有要插入对象的标签：计算标签目标的宽高的平均值
        return (int(xs/c), int(ys/c))


def process_object_insertion(i, objects):
    # insert objects into the image, and also do a delta debugging style augmentation
    # 在图像中插入对象，并执行增量调试样式增强图像多样性
    with cd("../image_mutation"):
        i1 = i.split(".")[0]
        # let's first select one image
        # image_pool/ + i +
        p = "../image_pool/" + i1 + "/object.log"
        if os.path.isfile(p) == False:
            # well maybe it is because no object is detected.
            print ("[LOG] NO OBJECT IS DETECTED")
            return

        lines = [] # ["('person', 1, 278, 640, 0, 418)\n", ...]
        with open(p) as f:
            lines = f.readlines()
        c = 1
        for o in objects: # 选取一个插入目标
            label = o.split("_")[0]
            x, y = resize(label, lines) # 计算插入目标resize的宽高：根据标签计算，如果标签没有插入目标的标签，则计算标签所有对象的平均值。
            print("python3 image_insertion.py " + i.strip() + " " + o + " " + str(x) + " " + str(y) + " " + str(c))
            os.system("python3 image_insertion.py " + i.strip() + " " + o + " " + str(x) + " " + str(y) + " " + str(c)) # 执行图像目标插入
            c += 1
            #break




def process():
    # clean()

    # the image list contains randomly selected N images 
    # from the COCO test 2017 data set 
    with open("imagelist.txt") as f:
        images = f.readlines()
    # 进行目标分割并生成目标池和图像池
    process_object_extraction(images)
    return
    # 初始化对象细化和选择-建立数据库和哈希数据库、删除低分辨率或碎片图像。
    init_object_refinement()

    for i in images:
        # 验证当前图像是提取到object_pool：如果为false可能是：当前图像没进行目标分割 or 目标分割结果为0
        if valid_image(i) == False:
            continue
        # 对象细化和选择-选择
        objects = process_object_refinement(i)
        print(objects) # for example: ['tv_000000003469_1.png', 'person_000000003469_2.png', 'remote_000000000188_2.png', 'person_000000003469_2.png']
        # why set()? because there can exist redundant labels
        process_object_insertion(i, set(objects)) # 在图像中插入对象
        break

# process()
#
if __name__ == '__main__': # 测试用
    with open("imagelist.txt") as f:
        images = f.readlines()
    # 初始化对象细化和选择-建立数据库和哈希数据库、删除低分辨率或碎片图像。
    init_object_refinement()
    for i in images:
        # 验证当前图像是提取到object_pool：如果为false可能是：当前图像没进行目标分割 or 目标分割结果为0
        if valid_image(i) == False:
            continue
        # 对象细化和选择-选择
        objects = process_object_refinement(i)
        print(objects) # for example: ['tv_000000003469_1.png', 'person_000000003469_2.png', 'remote_000000000188_2.png', 'person_000000003469_2.png']
        # why set()? because there can exist redundant labels
        process_object_insertion(i, set(objects))
        break