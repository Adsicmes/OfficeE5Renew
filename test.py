import os
from loguru import logger
import cv2
from PIL import Image
import numpy as np


def pic_transform(inp_name, oup_name, r=0, g=0, b=0, bright=1.0, compress_jpg=75):
    """
    目前实现了
        - rgb颜色通道修改
        - 亮度修改
        - 图片压缩
    目前仅支持保存为jpg并压缩
    :param inp_name: 输入图片路径
    :param oup_name: 输出图片路径
    :param r: 颜色通道r
    :param g: 颜色通道g
    :param b: 颜色通道b
    :param bright: 亮度值 在1上下浮动 大于1变亮 小于1变暗
    :param compress_jpg: 压缩率 1-95 95-100会禁用部分jpeg压缩算法，默认为75
    :return:
    """
    img = cv2.imread(inp_name, 1)
    height = img.shape[0]
    width = img.shape[1]
    dst = np.zeros(img.shape, img.dtype)

    # 1.计算三通道灰度平均值
    imgB = img[:, :, 0]
    imgG = img[:, :, 1]
    imgR = img[:, :, 2]

    # 下述3行代码控制白平衡或者冷暖色调，下例中增加了b的分量，会生成冷色调的图像，
    # 如要实现白平衡，则把两个+10都去掉；如要生成暖色调，则增加r的分量即可。
    bAve = cv2.mean(imgB)[0] + b
    gAve = cv2.mean(imgG)[0] + g
    rAve = cv2.mean(imgR)[0] + r
    aveGray = (int)(bAve + gAve + rAve) / 3

    # 2计算每个通道的增益系数
    bCoef = aveGray / bAve
    gCoef = aveGray / gAve
    rCoef = aveGray / rAve

    # 3使用增益系数
    imgB = np.floor((imgB * bCoef))  # 向下取整
    imgG = np.floor((imgG * gCoef))
    imgR = np.floor((imgR * rCoef))

    # 4将数组元素后处理
    for i in range(0, height):
        for j in range(0, width):
            imgb = imgB[i, j]
            imgg = imgG[i, j]
            imgr = imgR[i, j]
            if imgb > 255:
                imgb = 255
            if imgg > 255:
                imgg = 255
            if imgr > 255:
                imgr = 255
            dst[i, j] = (imgb, imgg, imgr)

    # 提升亮度
    dst = np.power(dst, bright)

    cv2.imwrite(oup_name, dst)

    # 压缩
    pil_img = Image.open(oup_name)
    pil_img.save(oup_name, quality=compress_jpg)


def main():
    raw_path = r"C:\Users\abbey\Desktop\raw"
    output_path = r"C:\Users\abbey\Desktop\raw\handled_compressed_12"
    try:
        os.mkdir(output_path)
    except FileExistsError:
        pass

    fns = os.listdir(raw_path)
    length = len(fns)
    file_remove = []
    for fn in fns:
        if not os.path.isfile(os.path.join(raw_path, fn)):
            file_remove.append(fn)
    for fn in file_remove:
        fns.remove(fn)
        length -= 1

    n = 0
    for fn in fns:
        n += 1
        print(n, "/", length)
        pic_transform(os.path.join(raw_path, fn), os.path.join(output_path, fn), r=3, g=3, b=0, bright=1.02,
                      compress_jpg=75)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.exception(e)
