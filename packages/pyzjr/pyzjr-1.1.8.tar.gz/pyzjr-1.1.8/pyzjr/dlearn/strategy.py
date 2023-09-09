import numpy as np
from PIL import Image
import torch
from thop import clever_format, profile
from torchsummary import summary
import random
from pyzjr.video import Timer

from pyzjr.utils import gpu

def cvtColor(image):
    """转化为RGB格式"""
    if len(np.shape(image)) == 3 and np.shape(image)[2] == 3:
        return image
    else:
        img = image.convert('RGB')
        return img

def show_config(**kwargs):
    """显示配置"""
    print('Configurations:')
    print('-' * 70)
    print('|%25s | %40s|' % ('keys', 'values'))
    print('-' * 70)
    for key, value in kwargs.items():
        print('|%25s | %40s|' % (str(key), str(value)))
    print('-' * 70)

def normalize_image(image):
    """
    将图像归一化到 [0, 1] 的范围
    :param image: 输入的图像
    :return: 归一化后的图像
    """
    normalized_image = image / 255
    return normalized_image

def resizepad_image(image, size, frame=True):
    """
    将调整图像大小并进行灰度填充
    :param image: 输入图像, PIL Image 对象
    :param size: 目标尺寸，形如 (width, height)
    :param frame: 是否进行不失真的resize
    :return: 调整大小后的图像，PIL Image 对象
    """
    iw, ih = image.size
    w, h = size
    if frame:
        scale = min(w/iw, h/ih)
        nw = int(iw*scale)
        nh = int(ih*scale)

        image = image.resize((nw,nh), Image.BICUBIC)
        new_image = Image.new('RGB', size, (128,128,128))
        new_image.paste(image, ((w-nw)//2, (h-nh)//2))
        return new_image, nw, nh
    else:
        new_image = image.resize((w, h), Image.BICUBIC)
        return new_image

def seed_torch(seed=11):
    """
    :param seed:设置随机种子以确保实验的可重现性
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def summarys(input_shape, model):
    """
    打印模型的摘要信息，并计算模型的总浮点运算量和总参数数量
    :param input_shape:
    :param model:要进行计算的模型
    """
    device = gpu()
    models = model.to(device)
    summary(models, (3, input_shape[0], input_shape[1]))

    dummy_input = torch.randn(1, 3, input_shape[0], input_shape[1]).to(device)
    flops, params = profile(models.to(device), (dummy_input, ), verbose=False)
    flops = flops * 2
    flops, params = clever_format([flops, params], "%.3f")
    print('Total GFLOPS: %s' % (flops))
    print('Total params: %s' % (params))


class Runtests:
    """用于测量运行时间"""
    def __init__(self, description='Done'):
        self.description = description

    def __enter__(self):
        self.timer = Timer()
        return self

    def __exit__(self, *args):
        print(f'{self.description}: {self.timer.stop():.5f} sec')