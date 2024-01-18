# do the object refinement
# including clustering
# and eliminating low quality clusters

# avaliable "policies" that can be selected for usage:
# 1. for an image of three persons and two dogs 
# 2. insert person and insert dog 
# 3. build a relation database (one single map)
#    person -> dog
#    dog    -> person
#    person -> bike
#    bike   -> person
#    ...
# 4. in that sense, we can also insert dog or bike, if that's an image of three persons
# 5. sort the object images and somehow pick the top qualities

#可选择使用的可用“策略”：
# 1.三个人和两只狗的照片
# 2.插入人和插入狗
# 3.建立关系数据库（一张地图）
#人->狗
#狗->人
#人->自行车
#自行车->人
#    ...
# 4.从这个意义上说，如果是三个人的图像，我们也可以插入狗或自行车
# 5.对对象图像进行排序，并以某种方式选择最佳质量
#from imagecluster import calc as ic
#from imagecluster import postproc as pp
import sys
import os, random
import itertools
from PIL import Image
import imagehash
# No use
def clustering(pool_path, cluster_path, label):
    ias = ic.image_arrays(pool_path, size=(224,224))
    model = ic.get_model()
    fps = ic.fingerprints(ias, model)
    
    fps = ic.pca(fps, n_components=0.95)
    clusters = ic.cluster(fps, sim=0.5)
    pp.make_links(clusters, cluster_path + '/' + label)



def small_images_remover(base):
    # just iterate every pool of objects and remove low quality 
    # just sort by size and shave small images.
    # 只需迭代每个对象池并删除低质量的对象
    # 只需按大小排序并删除小图像。
    def size(l):
        return os.path.getsize(l)
    obj_list = {}
    for path, _, files in os.walk(base):
        for name in files:
            label = name.split("_")[0]
            l = os.path.join(path, name)
            if label in obj_list:
                obj_list[label].append((l, size(l)))
            else:
                obj_list[label] = [(l, size(l))]
    
    P = 0.9
    # 2019-07-15
    # seems that we will need to increase the number from 0.7 -->　0.9
    # we remove 90% of object instances 
    for _, v in obj_list.items():
        if (len(v) < 6):
            continue
        else:
            v.sort(key=lambda n: n[1]) 
            n = int(len(v) * P)
            for i in range(n):
                os.system("mv " + v[i][0] + " " + v[i][0]+"_drop")
 



# let's build a database for task 3
def build_db(base):
    m = {}
    for path, subdirs, files in os.walk(base):
        for name in files:
            if "object.log" in name:
                l = os.path.join(path, name)
                with open(l) as f:
                    lines = f.readlines()
                    nl = []
                    for l in lines:
                        n = l.split(',')[0][2:-1]
                        if " " in n:
                            n = n.replace(" ", "-")
                        nl.append(n)
                    for i, j in itertools.product(nl, nl):
                        if i != j:
                            m[i] = j
    return m


def build_object_hashdb(base):
    hash_m = {}
    for path, subdirs, files in os.walk(base):
        for name in files:
            if ".png" in name:
                l = os.path.join(path, name)
                hash_m[name] = compute_image_hash(l)
    # print(hash_m)
    return hash_m

def compute_image_hash(i):
    hash = imagehash.average_hash(Image.open(i))
    return hash
# 上面是初始化函数


# randomly select one from top ten high quality images?
def one_from_top_N(label, image):
    # pick top ten good images from a pool? How to?
    # check whether it has over ten files 
    N = 10
    t = [name for name in os.listdir(base_object + label + "/") if name.endswith(".png")]
    n = len(t)
    if n > N:
        files = []
        for i in range(N):
            files.append(random.choice(os.listdir(base_object + label + "/")))
        return random.sample(files, 1)[0]
    else:
        return random.sample(t, 1)[0]

def hamming(a, b):
    return bin(a^b).count('1')

def one_with_close_hash(label, image):
    # select one image with the closest hash value of objects of the same label on the image
    # 选择一张图像,其中图像上相同标签的对象的哈希值最接近
    iid = image.split(".")[0]
    image_label_hash_list = []
    all_label_hash_map = {}
    for k, v in hash_m.items():
        # print (k, v, iid, label)
        # 从hashdb中获取对应标签下目标的哈希值
        if iid in k and label in k:
            # 当前图像下label标签对应的目标
            image_label_hash_list.append(v)
        if label in k and k.endswith(".png"):
            # note that for this, we put every possible 
            # object instances, including the original objects into the set, 
            # AS LONG AS it is large enough.
            # 所有标签为label的目标
            all_label_hash_map[k] = v
    a1 = []
    if len(image_label_hash_list) == 0: # all_label_hash_map随机选一个目标
        # this is possible, suppose we decide to insert a dog for a image of only human beings 
        # just randomly select one 
        return random.choice(list(all_label_hash_map.keys()))
    else: # 在all_label_hash_map选取hash值相似的图像插入
        for a in image_label_hash_list:
            # print ("hash value", a)
            a1.append(int(str(a), 16))
        average_hash = int(sum(a1) / len(image_label_hash_list)) # 计算image的label标签的评价hash值
        min_distance = 999999
        min_label = None
        for k, v in all_label_hash_map.items():
            # print ("check other hash", v)
            distance = hamming(int(str(v), 16), average_hash)
            if distance < min_distance:
                # print ("find one minimal ", v, distance, ah)
                min_distance = distance
                min_label = k
        assert min_label 

        return min_label


base_image = ""
base_object = ""
m = {}
hash_m = {}
def init(i, o):
    # target_dir = "../object_pool/" : i
    # image_dir = "../image_pool/" : o
    global m
    global hash_m
    global base_image
    global base_object
    base_image = o
    base_object = i
    # base = "../image_pool/"
    # FIXME
    # small_images_remover(base_object)
    m = build_db(base_image) # {'person': 'bicycle', 'kite': 'tie', 'tennis-racket': 'person', 'giraffe': 'person',...}
    hash_m = build_object_hashdb(base_object) # 统计object_pool中每个图片的hash值
    print(m)

def get_labels(image):
    with open(base_image + image.split(".")[0] + "/object.log") as f:
        lines = f.readlines()
        nl = []
        for n in lines:
            n1 = n.split(',')[0][2:-1]
            n1 = n1.replace(" ", "-")
            nl.append(n1)
        s = set(nl)
        ss = set()

        for s1 in s:
            if s1 in m:
                # note that this is possible such that m does not have s1 as a key
                # for instance, an image contains objects of the same label
                t = m[s1]
                if t not in s:
                    ss.add(t)

    # nl: a list of all the objects in the image 
    # ss: a set of correlated object labels (the element of ss is not in s)
    return (nl, ss)

# the input is an image 
# output: a set of objects used for insertion.
# note that given an image of N objects
# we will need to iterate for 10 * N synthetic images 
# in that sense, we shouldn't generate too many object files for each object.
# maybe it's like this:
# suppose we have N objects in the input image,
# then we prepare N objects as well for use.

# 输入是一个图像
# 输出：用于插入的一组对象。
# 注意，给定N个对象的图像
# 我们需要迭代10*N个合成图像
# 从这个意义上说，我们不应该为每个对象生成太多的对象文件。
# 也许是这样的：
# 假设我们在输入图像中有N个对象，
# 那么我们也准备N个对象以供使用。
import random
def process(image):
    # clustering("../object_pool/" + label, "../object_clusters/" + label, label)
    (nl, ss) = get_labels(image) # 获取图像所有的标签和一组相关对象标签的集合(从db中提取)
    N = len(nl)
    print(nl, ss)
    # then let's prepare N labels as well
    # candidates = random.sample(nl + list(s1), N) # 选出N个要插入的对象标签 (插入的对象包含db相关联的标签)
    # FIXME
    # so that might give us a easier time, considering that 
    # we can find object instances of identical label in the background image.

    # candidates = random.sample(nl + list(ss), N)  # 选出N个要插入的对象标签 (插入的对象包含db相关联的标签)
    candidates = random.sample(nl, N) # 选出N个要插入的对象标签 (插入的对象都是图像中的标签)

    res = []
    # for an image of N objects, we select N objects close to existing cases for the usage.
    for cl in candidates:
        # res.append(one_from_top_N(cl, image))
        res.append(one_with_close_hash(cl, image)) # 选择图像上具有相同标签的对象的哈希值最接近的一个图像
    return res
