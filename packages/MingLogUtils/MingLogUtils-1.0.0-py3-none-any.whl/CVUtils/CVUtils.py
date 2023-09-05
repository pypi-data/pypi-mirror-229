import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import aiofiles, asyncio
from scipy import ndimage
import json
import random
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

def show_image(image, mode="bgr"):
    """
    定义展示图片函数，默认展示BGR通道，适配CV2
    主要用于在jupyter notebook中嵌入图像使用
    配合%matplitlib inline使用效果更好
        image: cv2读取的图片数据
        mode: 展示图像的格式，支持"bgr"（默认）, "rgb", "gray"三种格式
    """
    if mode == 'bgr':
        plt.imshow(image[:, :, ::-1])
    elif mode == "gray":
        plt.imshow(image, cmap='gray')
    else:
        plt.imshow(image)
    plt.axis('off')
    plt.show()
    
def read_image(filename):
    """
    定义读取中文路径图片的函数
        filename: 图片路径
    """
    return cv2.imdecode(np.fromfile(filename, dtype=np.uint8), -1)

def resize2gray(image, new_shape):
    """
    定义尺寸统一函数，并将图片转化为灰度图像
        image: 原始BGR格式图像
        new_shape: 统一的尺寸大小
    """
    image = cv2.resize(image, new_shape)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def cv2AddChineseText(img, text, position, textColor=(0, 255, 0), textSize=30, stroke_width=2):
    """
    用于在图片中增加中文文字
        img: 图片数组
        text: 添加的文本内容
        position: 添加文本的位置坐标
        textColor: 文字颜色
        textSize: 文字大小
        stroke_width: 文字粗细
    """
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        "simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text(position, text, textColor, font=fontStyle, stroke_width=stroke_width)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

async def _copy_one_file(file_path, output_path):
    file_name = file_path.split('\\')[-1]
    output_path = output_path + '\\' + file_name
    async with aiofiles.open(file_path, 'rb') as f, aiofiles.open(output_path, 'wb') as g:
        bytes = await f.read()
        await g.write(bytes)

async def _copy_allfile(all_filepath, output_path):
    tasks = []
    for file_path in all_filepath:
        tasks.append(asyncio.create_task(_copy_one_file(file_path, output_path)))
    await asyncio.wait(tasks)

def copy_files(all_filepath, output_path):
    """
    使用协程拷贝文件
        all_filepath: 所有图片路径列表
        output_path: 将路径中的图片拷贝到的路径
    """
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(_copy_allfile(all_filepath, output_path))

def split_rectangle_image_from_imageArray(ori_image, left_top_point, right_bottom_point):
    """
    切分出矩形区域图像
        ori_image: 原始图像Array数组
        left_top_point: 左上角坐标
        right_bottom_point: 右下角坐标
    """
    result_image = ori_image[int(left_top_point[1]): int(right_bottom_point[1]), int(left_top_point[0]):int(right_bottom_point[0]),  :]
    return result_image

def image_correction(img):
    """
    图像校正
        img: 原始图像（ndarray格式）
        Return: 校正后的图像（ndarray格式）
    """
    # 二值化
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # 边缘检测
    edges = cv2.Canny(gray, 50, 150, apertureSize = 3)
    # 霍夫变换
    lines = cv2.HoughLines(edges,1,np.pi/180,0)
    for rho,theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
    t = float(y2-y1)/(x2-x1)
    # 得到角度后
    rotate_angle = np.degrees(np.arctan(t))
    if rotate_angle > 45:
        rotate_angle = -90 + rotate_angle
    elif rotate_angle < -45:
        rotate_angle = 90 + rotate_angle
    # 图像根据角度进行校正
    rotate_img = ndimage.rotate(img, rotate_angle)
    return rotate_img


def get_plate_dict():
    with open(ROOT + '/files/Province.txt', 'r', encoding='utf-8') as f, open(ROOT + '/files/WordAndNum.txt', 'r', encoding='utf-8') as g:
        province_dict = json.load(f)
        wn_dict = json.load(g)
    province_dict_T = {j:str(i).upper() for i,j in province_dict.items()}
    wn_dict_T = {j:str(i).upper() for i,j in wn_dict.items()}
    return province_dict_T, wn_dict_T

def Num2Plate(plate_nums):
    """
    车牌还原
        plate_nums：车牌对应的列表数值编号
    """
    province_dict_T, wn_dict_T = get_plate_dict()
    LicensePlateNum = ''
    for i, plate_num in enumerate(plate_nums):
        if i == 0:
            LicensePlateNum += province_dict_T[plate_num]
        else:
            LicensePlateNum += wn_dict_T[plate_num]
    return LicensePlateNum

def save_list2txt(list_, output_file):
    """
    将列表内容按行存储到文件中
        list_：列表
        output_file：按行存储的文件路径
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for i in list_:
            f.writelines(i + '\n')

def train_test_split2txt(filenames, test_size=0.2, output_dir=None):
    """
    将列表中的内容进行训练集测试集切分
        filenames: 文件名构成的列表
        test_size: 测试集比例
        output_dir: 输出文件存储的文件夹，默认是None表示不存储切分结果
    """
    # 获取切分索引
    split_index = int(len(filenames) * (1 - test_size))
    random.shuffle(filenames)
    train_filenames = filenames[:split_index]
    test_filenames = filenames[split_index:]
    # 如果给定输出文件夹则存储到输出文件夹，否则返回切分结果
    if output_dir:
        # 支持当文件夹不存在时创建文件夹，但是仅支持单层文件夹
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        save_list2txt(train_filenames, os.path.join(output_dir, 'train.txt'))
        save_list2txt(test_filenames, os.path.join(output_dir, 'test.txt'))
        return
    return train_filenames, test_filenames
    