# the empirical evidence we would like to show for the evaluation.
import sys

sys.path.append('imagegym')
from imagegym.env import ENV
import os
from PIL import Image
import math


# 统计背景图像上被插入目标的区域 return # [(delta_box, 中心点，宽， 高),..]
def collect_regions_of_objects(boxs):
    # return a list of boxes
    a = []
    for box in boxs:
        w = abs(box[0][1] - box[0][0])
        h = abs(box[1][1] - box[1][0])
        delta_box = math.sqrt(h ** 2 + w ** 2) / 2
        mid = (int(box[0][0] + w / 2), int(box[1][0] + h / 2))
        a.append((delta_box, mid, w, h))  # [(delta_box, 中心点，宽， 高),..]

    # print (boxs)
    # print (a)
    return a


# 进行目标插入，插入后进行预测，返回是否检测出错误。win表示检测出错误
def insert_object_images(x, y, idx):
    r = env.do_insert(x, y, idx)
    if r == "win":
        # print ("win!!")
        return 1  # 检测出模型错误
    else:
        return 0  # 模型没有检测出错误
        # return 1


# 进行目标插入，插入后不进行预测，保存图像
def only_insert_object_images(x, y, idx):
    env.do_insert_and_save(x, y, idx)


from random import randint
import random


# x1 = target_obj_x + 2 * 0.5 * inserted_obj_x
# y1 = target_obj_y + 2 * 0.5 * inserted_obj_y
# x2 = target_obj_x + 2 * inserted_obj_x
# y2 = target_obj_y + 2 * inserted_obj_y
# 获取引导插入坐标
def get_guided_insertion_location(arr):
    def compute_distance(target_obj_x, target_obj_y, inserted_obj_x,
                         inserted_obj_y):  # 计算距离：blue region：x1蓝色框内框的宽度  x2蓝色框外框宽度...
        x1 = target_obj_x + inserted_obj_x
        y1 = target_obj_y + inserted_obj_y
        x2 = target_obj_x + 2 * inserted_obj_x
        y2 = target_obj_y + 2 * inserted_obj_y
        # print ("compute distance", x1, y1, x2, y2)
        return (x1, y1, x2, y2)  #

    def sampling(x1, y1, x2, y2):  # 采样：计算距离背景图像上被插入对象的距离
        x = 0.0
        y = 0.0
        while (x == 0.0 and y == 0.0):
            x = random.uniform(0, 1) * x2
            y = random.uniform(0, 1) * y2

        if (x < x1 and y < y1):
            xpower = math.ceil((math.log(x1) - math.log(x)) / math.log(x2 / x1))
            ypower = math.ceil((math.log(y1) - math.log(y)) / math.log(y2 / y1))
            power = min(xpower, ypower)
            x *= math.pow(x2 / x1, power)
            y *= math.pow(y2 / y1, power)

        r = randint(0, 4)
        if ((r & 1) != 0):
            x = -x
        if ((r & 2) != 0):
            y = -y

        return (int(x), int(y))

    def aux():
        # print ("I am here", arr, env.label0)
        #        print (random.choice([a for a in zip(env.label0, range(0, len(env.label0))) if a[0] == label]))
        #        print (zip(env.label0, range(0, len(env.label0))))
        tt = []
        for a in zip(env.label0, range(0, len(env.label0))):
            if a[0].replace("_", '-').lower() == label:
                tt.append(a)
        obj_idx = random.choice(tt)[1]  # 从背景图像中随机选择一个和插入对象相同标签的对象
        assert len(tt) != 0
        # print ([a for a in zip(env.label0, range(0, len(env.label0))) if a[0].lower() == label])
        # obj_idx = randint(0, len(arr)-1)
        x = arr[obj_idx][2]  # 背景图像对应对象的宽和高。
        y = arr[obj_idx][3]

        # 计算蓝色框宽高：blue region：x1蓝色框内框的宽度  x2蓝色框外框宽度...  t = (x1, y1, x2, y2) -> (内框宽，内框高，外框宽，外框高)
        t = compute_distance(x, y, obj_width, obj_height)  # 传入背景图像待插入对象的宽高，x, y。 传入插入目标的宽高，obj_width，obj_height。
        # print ("what we want", t, obj_width, obj_height)

        x, y = sampling(t[0] / 2, t[1] / 2, t[2] / 2, t[3] / 2)  # 采样：计算距离背景图像上被插入对象的距离
        # print ("random number", x, y)
        # compensate 
        x1 = x + arr[obj_idx][1][0]  # x + 背景图像被插入对象中心点x
        y1 = y + arr[obj_idx][1][1]
        # print ("random coordinator", x1, y1)
        return (x1, y1)

    c = 0
    while True:
        x1, y1 = aux()  # 计算插入目标的坐标(在背景图像上被插入对象的附近，随机生成一个坐标)
        print("find a location: ", x1, y1, "then check: ")
        r1 = env.check_overlapping(x1, y1, "")  # 检查插入位置是否与其他对象重叠。True为重叠，False为不重叠
        r2 = env.check_boundary(x1, y1)  # 检查插入位置是否越界：True表示没有越界，False为越界了
        c += 1
        if c == 20:
            print("Reached maximum number of times!")
            return None
        if r1 == False and r2 == True:
            # all set
            print("good insertion")
            return x1, y1
        else:
            print("bad insertion, overlapping:", r1, " not out of boundary:", r2)
            continue
            # return x1, y1


def delta_insertion(win, cl, c):
    # 增量调试插入
    # we need to move to XX.
    def average(x1, y1, x2, y2):
        return int((x1 + x2) / 2), int((y1 + y2) / 2)

    def close(mx, my, x1, y1):
        # compute the distance; 
        # if it is just too close, then terminate
        d = math.sqrt((x1 - mx) ** 2 + (y1 - my) ** 2)
        return d < base_delta_obj / 6

    def percentage(x1, y1, xc, yc, x2, y2):
        # x1 y1: starting point 
        # xc yc: centroid 
        # x2 y2: termination point
        d1 = math.sqrt((x1 - xc) ** 2 + (y1 - yc) ** 2)
        d2 = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        print("[LOG] percentage ", d2 / d1)

    def check_valid_location(x1, y1):
        r1 = env.check_overlapping(x1, y1, "")
        r2 = env.check_boundary(x1, y1)
        if r1 == False and r2 == True:
            # all set
            return True
        else:
            # print ("bad insertion", r1, r2)
            return False

    x0 = win[0]
    y0 = win[1]
    xc = cl[0]
    yc = cl[1]
    x2, y2 = xc, yc
    x1, y1 = x0, y0
    print("start to delta debugging", x1, y1, x2, y2)
    idx = 0
    while True:
        idx += 1
        if check_valid_location(x2, y2) == False:
            print("overlapping at ", x2, y2)
            r = 0
        else:
            # do it only if it is not overlapping
            r = insert_object_images(x2, y2, idx)
        if r == 1:
            x1, y1 = x2, y2
            if close(xc, yc, x1, y1):
                break
            x2, y2 = average(xc, yc, x1, y1)
        else:
            x2, y2 = average(x1, y1, x2, y2)
            if close(x1, y1, x2, y2):
                break

    print("finished at", x1, y1)
    insert_object_images(x1, y1, idx)
    percentage(x0, y0, xc, yc, x1, y1)
    os.system("cp new_" + str(idx) + ".png " + "new_final_" + str(c) + ".png")
    return x1, y1


def insert_loc(boxs):
    # let's compute cendroid first.
    arr = []
    for box in boxs:
        h = (box[0][0] + box[0][1]) / 2
        w = (box[1][0] + box[1][1]) / 2
        arr.append((h, w))

    def centeroidnp(v, label):
        length = 0
        sum_x = 0
        sum_y = 0
        # for v1 in v:
        for i in range(0, len(v)):
            # if True:
            # only do it when it has the same label
            # print (env.label0[i], label)
            if env.label0[i].replace("_", "-").lower() == label:
                v1 = v[i]
                # print ("take this one", label, v1)
                sum_x += v1[0]
                sum_y += v1[1]
                length += 1
        print("centroid", int(sum_x / length), int(sum_y / length))
        return int(sum_x / length), int(sum_y / length)

    return centeroidnp(arr, label)


def process():
    _ = env.reset()
    a = collect_regions_of_objects(
        env.object_boxes)  # 统计背景图像上目标检测box的：[(delta_box, 中心点，宽， 高),..] [(delta_box, 中心点，宽， 高),..]
    win_list = []
    # FIXME
    bound = len(a) * 10  # 对于具有 N 个现有对象的每个背景图像 i，我们执行 10 × N 引导或随机插入。（这里只有引导插入）
    c = 1
    if bound == 0:
        # too bad
        return
    print("START TO PROCESS, PROCESS NUMS:", bound)
    while True:
        print()
        bound -= 1
        if bound == 0:  # 超过 10 x N 个了
            break
        # paper中引导插入：从背景图像中随机选择一个与插入对象标签相同的现有对象，并在其附近进行插入。
        t = get_guided_insertion_location(a)  # 引导插入：得到一个没有覆盖其他目标并且没有越界的插入的中心点坐标 t = (x, y)
        if t == None:
            continue
        else:
            x, y = t
        # 找到一个插入坐标
        print("insert object images location:" + str(x) + " " + str(y))

        # 只进行目标插入，并保存图像
        #FIXME
        only_insert_object_images(x, y, c)
        c += 1
        continue

        # 目标插入后进行预测并检测结果
        if insert_object_images(x, y, 0) == 1:  # 执行目标插入，插入坐标为x,y，新生成的保存路径：./new_idx.png，并对目标插入后的图像进行目标检测。并检查检测结果。
            # 如果检测结果中模型出错，就cp为new_start_str(c).png图像，并把出错的插入坐标保存到win_list列表中。
            # find one
            print("find one!  insertion location: " + str(x), str(y), "save file: " + "new_start_" + str(c) + ".png")
            os.system("cp new_0.png new_start_" + str(c) + ".png")
            c += 1
            win_list.append((x, y))
            # break
        else:
            print("no error!  insertion location: ", x, y)

    print("WINLIST", len(win_list))

    cl = insert_loc(env.object_boxes)
    print("centroid ", cl)
    # 后续增量调试提高图像多样性，未看。
    c = 1
    for win in win_list:
        mw = delta_insertion(win, cl, c)
        print("finish with : ", mw, win)
        c += 1


bg = ""
ob = ""
env = None
im = None
input_height = None
input_width = None
obj_height = None
obj_width = None
base_delta_obj = None
label = None

from PIL import Image


def do_resize(w, l, n):
    img = Image.open(n)
    new_img = img.resize((int(w), int(l)))
    new_img.save(n, "PNG", optimize=True)


def check_label_consistency():  # 远程服务器检测bg背景图片标签中是否存在插入对象的label标签
    # this is possible!
    # note that YOLO and the remote object detection system may have 
    # inconsistent detection results 
    for a in zip(env.label0, range(0, len(env.label0))):
        if a[0].replace("_", '-').lower() == label:
            return True
    return False


def main(n, obj, width, length, c):
    global bg  # 背景图像
    global ob  # 插入目标
    global env  # ENV(bg, ob, True)
    global im  # Image.open(bg)
    global input_height  # bg的高和宽
    global input_width
    global obj_height  # ob的高和宽
    global obj_width
    global base_delta_obj  # 基本增量调试参数
    global label  # 插入目标的标签
    # n : 背景图像
    # obj: 插入的object
    #  resize width, length of obj
    # c：计数
    bg = "../images/val2017/" + n
    label = obj.split("_")[0]

    ob = "../object_pool/" + label + "/" + obj
    os.system("cp " + ob + " obj_" + str(c) + ".png")
    print("random test image: ", n, "object", ob)
    # resize obj.png
    do_resize(width, length, "obj_" + str(c) + ".png")  # 调整目标图片宽高
    # return
    ob = "./obj_" + str(c) + ".png"
    env = ENV(bg, ob, True)  # 初始化
    im = Image.open(bg)
    input_height, input_width = im.size
    im = Image.open(ob)
    obj_height, obj_width = im.size
    base_delta_obj = math.sqrt(obj_height ** 2 + obj_width ** 2)
    if (check_label_consistency() == False):  # 远程服务器检测bg背景图片标签中存在插入对象的label标签
        # 不存在，直接skip
        print("[LOG] inconsistent YOLO and remote service results; so we can skip this round " + label)
        return
    # 插入对象的标签在背景图像上必须存在
    process()  # 进行引导插入并统计出错的结果、进行增量调试插入
    os.system("mkdir " + n + "-" + obj)
    # it is possible that no "new_*" files are produced because we didn't find anything
    os.system("mv new_final_* " + n + "-" + obj)
    os.system("mv new_start_* " + n + "-" + obj)
    os.system("mv obj_" + str(c) + ".png " + n + '-' + obj)


# main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

if __name__ == '__main__':  # 测试用
    # main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    main("000000000139.jpg", "chair_000000039405_36.png", 61, 88, 1)
