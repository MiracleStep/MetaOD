import os 
import sys

# python3 Step0_object_detection.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=images/dog.jpg # python3 Step1_extract_object.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=images/dog.jpg # python3 Step2_save_into_seperate.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=images/dog.jpg 
# 对数据集进行分割
lines = []
with open("../scripts/imagelist.txt") as f:
    lines = f.readlines()

for n in lines[0:300]:
    n = n.strip()
    print("asa")
    print(os.system("which python"))
    os.system("python Step0_object_detection.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=../images/test2017/" + n +  ".jpg")
    os.system("python Step1_extract_object.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=../images/test2017/" + n +  ".jpg")
    os.system("python Step2_save_into_seperate.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=../images/test2017/" + n + ".jpg")
# 
# n = sys.argv[1].strip()
# os.system("python Step0_object_detection.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=../../../../coco_test_2017/test2017/" + n)
# os.system("python Step1_extract_object.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=../../../../coco_test_2017/test2017/" + n)
# os.system("python Step2_save_into_seperate.py --trained_model=yolact_darknet53_54_800000.pth --score_threshold=0.3 --top_k=100 --image=../../../../coco_test_2017/test2017/" + n)
