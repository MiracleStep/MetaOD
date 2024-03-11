import os
import shutil
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


clean()