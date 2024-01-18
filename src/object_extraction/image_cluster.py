# move images out of the folder 

# labels for clustering

# 根据标签和分割的目标构建目标池(object_pool)和图像池(image_pool)
from os import walk

import os
import sys

def build_folder(base, labels):
    for label in labels:
        os.system("mkdir -p " + base + "/" + label)


def label_collector(base):
    s = set()
    for (dirpath, dirnames, filenames) in walk(base):
        image_name = dirpath.split("/")[-1]
        for fn in filenames:
            if ".png" in fn:
                # wine_cup_1.png
                t = fn.split("_")[:-1]
                label = "_".join(t) # 标签名
                if " " in label:
                    label = label.replace(" ", "-")
                    os.system("mv " + dirpath + "/" + fn.replace(" ", "\ ") + " " + dirpath + "/" + fn.replace(" ", "-"))
                s.add(label)
    return s


def build_pool(base, pooldir):
    labels = label_collector(base) # 收集Step2_save_into_seperate文件夹内的标签。
    build_folder(pooldir, labels) # 在pool文件夹中创建标签名命名的文件夹

    # 拷贝Step2_save_into_seperate到pool文件夹(按标签拷贝)
    print(labels)
    for label in labels:
        for (dirpath, dirnames, filenames) in walk(base):
            image_name = dirpath.split("/")[-1]
            for fn in filenames:
                if label in fn:
                    idx = fn.split("_")[-1].split(".")[0]
                    newname = label + "_" + image_name + "_" + idx + ".png"
                    os.system("cp " + dirpath + "/" + fn + " " + pooldir + "/" + label + "/" + newname)
                    


if __name__ == "__main__":
    build_pool(sys.argv[1], sys.argv[2])
    # build_pool("result/Step2_save_into_seperate/", "result/pool/")
