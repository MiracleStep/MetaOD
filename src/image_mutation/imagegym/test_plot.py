from PIL import Image, ImageDraw

def draw_detection_box(image_path, box_coordinates, output_path):
    # 打开图像
    image = Image.open(image_path)

    # 创建Draw对象
    draw = ImageDraw.Draw(image)

    # 从输入的坐标中解包左上角和右下角坐标
    x1, y1, x2, y2 = box_coordinates

    # 画矩形框
    draw.rectangle([x1, y1, x2, y2], outline="red", width=2)

    # 保存或显示图像
    image.save(output_path)
    # image.show()  # 如果你想在默认图像查看器中显示图像

# 输入图片路径
image_path = "../000000003469.jpg"

# 输入目标检测框的左上角和右下角坐标
box_coordinates = (284, 639,0,419) #((300, 608), (449, 621)))

# 输出图片路径
output_path = "output.png"

# 调用函数画目标检测框
draw_detection_box(image_path, box_coordinates, output_path)
