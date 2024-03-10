import numpy as np
import tensorflow as tf
from PIL import ImageDraw, ImageFont, Image
from yolo import YOLO
from utils.utils import cvtColor, preprocess_input, resize_image

gpus = tf.config.experimental.list_physical_devices(device_type='GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)


class localize_YOLO(YOLO):
    # ---------------------------------------------------#
    #   检测图片
    # ---------------------------------------------------#
    def detect_image(self, image):
        # ---------------------------------------------------------#
        #   在这里将图像转换成RGB图像，防止灰度图在预测时报错。
        #   代码仅仅支持RGB图像的预测，所有其它类型的图像都会转化成RGB
        # ---------------------------------------------------------#
        image = cvtColor(image)
        # ---------------------------------------------------------#
        #   给图像增加灰条，实现不失真的resize
        #   也可以直接resize进行识别
        # ---------------------------------------------------------#
        image_data = resize_image(image, (self.input_shape[1], self.input_shape[0]), self.letterbox_image)
        # ---------------------------------------------------------#
        #   添加上batch_size维度，并进行归一化
        # ---------------------------------------------------------#
        image_data = np.expand_dims(preprocess_input(np.array(image_data, dtype='float32')), 0)

        # ---------------------------------------------------------#
        #   将图像输入网络当中进行预测！
        # ---------------------------------------------------------#
        input_image_shape = np.expand_dims(np.array([image.size[1], image.size[0]], dtype='float32'), 0)

        out_boxes, out_scores, out_classes = self.get_pred(image_data, input_image_shape)

        print('Found {} boxes for {}'.format(len(out_boxes), 'img'))
        # ---------------------------------------------------------#
        #   设置字体与边框厚度
        # ---------------------------------------------------------#
        # font = ImageFont.truetype(font='model_data/simhei.ttf',
        #                           size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32'))
        thickness = int(max((image.size[0] + image.size[1]) // np.mean(self.input_shape), 1))

        res = []
        for i, c in list(enumerate(out_classes)):
            predicted_class = self.class_names[int(c)]
            box = out_boxes[i]
            score = out_scores[i]

            top, left, bottom, right = box
            # 处理越界问题
            top = max(0, np.floor(top).astype('int32'))  # 左上角：y
            left = max(0, np.floor(left).astype('int32'))  # 左上角：x
            bottom = min(image.size[1], np.floor(bottom).astype('int32'))  # 右下角: y
            right = min(image.size[0], np.floor(right).astype('int32'))  # 右下角: x

            res.append((predicted_class.replace(" ", "_"), float(score) * 100,
                        ((left, right), (top, bottom))))  # box = ((x0, x1), (y0, y1))

            label = '{} {:.2f}'.format(predicted_class, score)
            draw = ImageDraw.Draw(image)
            # label_size = draw.textsize(label, font)
            label_size = draw.textsize(label)
            # label_size = draw.textbbox((0, 0), label, font)
            label = label.encode('utf-8')
            print(label, top, left, bottom, right)

            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])

            for i in range(thickness):  # 画厚度
                draw.rectangle([left + i, top + i, right - i, bottom - i], outline=self.colors[c])
            draw.rectangle([tuple(text_origin), tuple(text_origin + label_size)], fill=self.colors[c])
            draw.text(text_origin, str(label, 'UTF-8'), fill=(0, 0, 0))
            # del draw
        return image, res


yolo = localize_YOLO()

def localize_objects(path):
    image = Image.open(path)
    # if path == "../images/test2017/000000003469.jpg":
    #     return list([('person', 78.37519645690918, ((284, 639), (0, 419))),
    #                 ('tvmonitor', 90.7253086566925, ((0, 239), (64, 276))),
    #                 ('remote', 88.13422918319702, ((297, 360), (56, 165))),
    #                 ('remote', 70.9669291973114, ((271, 314), (330, 369)))])
    image, res = yolo.detect_image(image)
    # localize_objects("./kite.jpg")[('Bicycle_wheel', 94.234306, ((302, 424), (503, 620))), ('Bicycle_wheel', 93.37022, ((483, 603), (483, 603))), ('Bicycle', 89.73106, ((303, 608), (425, 619))), ('Picture_frame', 71.71168, ((756, 927), (106, 203)))]
    # image_with_box.show()

    # print(res)
    """[('person', 78.37519645690918, ((284, 639), (0, 419))),
                    ('tvmonitor', 90.7253086566925, ((0, 239), (64, 276))),
                    ('remote', 88.13422918319702, ((297, 360), (56, 165))),
                    ('remote', 70.9669291973114, ((271, 314), (330, 369)))])"""
    return res
# "../images/test2017/000000003469.jpg"
if __name__ == '__main__':
    image = Image.open("../new_0.png")
    image, res = yolo.detect_image(image)
    image2, _ = yolo.detect_image(Image.open("../000000003469.jpg"))
    image.show()
    image2.show()
    # yolo = YOLO()
    # image = Image.open("./kite.jpg")
    # results = yolo.detect_image(image, crop=False, count=False)
    # results.show()
