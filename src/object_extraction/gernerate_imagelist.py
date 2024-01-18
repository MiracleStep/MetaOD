import os

with open("imagelist.txt", "w") as f:
    list = os.listdir("../images/test2017")
    for i in list:
        split = i.split(".")
        f.write(split[0]+".jpg\n")
