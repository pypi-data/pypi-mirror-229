import cv2
import numpy as np
import os
import dill

from typing import Callable
from collections import defaultdict


def cal_diff(image1, image2):
    image_and = cv2.bitwise_xor(image1, image2)
    return 1 - (np.sum(image_and) / 2500 / 255)

def get_edge(x, interval):
    edges = [x[0]]
    for i in range(len(x) - 1):
        if x[i + 1] - x[i] > interval:
            edges.extend([x[i], x[i + 1]])

    edges.append(x[-1])
    return edges

def split(binary, length=None, interval=None):
    pixels = np.where(binary > 0)
    x = sorted(list(set(pixels[1])))

    if length is not None:
        interval = 1
        while len(edges := get_edge(x, interval)) > length * 2:
            interval += 1
    elif interval is not None:
        edges = get_edge(x, interval)
    else:
        raise RuntimeError

    char_list = []
    for i in range(len(edges) // 2):
        char_img = binary[:, edges[i * 2]:edges[i * 2 + 1] + 1]
        char_pixels = np.where(char_img > 0)
        y = sorted(list(set(char_pixels[0])))
        char_img = char_img[min(y):max(y) + 1, :]
        char_img = cv2.resize(char_img, (50, 50))
        char_list.append(char_img)

    return (char_list, interval) if length is not None else char_list



def show_image(image):
    cv2.imshow('Show', image)
    cv2.waitKey(0)


class QQOcr:
    model = {'data': defaultdict(list), 'function': None}
    dataset = None
    binary_function = None

    def set_binary(self, function: Callable):
        """设置二值化方法"""
        self.binary_function = function

    def load_dataset(self, dir_path: str):
        """加载数据集"""
        assert os.path.isdir(dir_path)

        images = [(cv2.imread(os.path.join(dir_path, filename)), filename)
                  for filename in os.listdir(dir_path)
                  if not filename.endswith('.txt')]

        with open(os.path.join(dir_path, 'label.txt'), 'r') as file:
            labels = {filename: value
                      for line in file.readlines()
                      for (filename, value) in [line.strip().split('\t')]}

        self.dataset = [(image, labels[filename]) for image, filename in images]

    def learn(self, equalization=True):
        """学习数据集并生成模型"""
        assert self.dataset is not None

        if self.binary_function is not None:
            max_interval = 0
            for image, label in self.dataset:
                binary = self.binary_function(image)
                char_list, interval = split(binary, length=len(label))
                max_interval = max(interval, max_interval)
                for char_image, char in zip(char_list, label):
                    self.model['data'][char].append(char_image)
            self.model['interval'] = max_interval
        else:
            raise RuntimeError('The binary_function cannot both be None.')

        if equalization:
            for char in self.model['data'].keys():
                canvas = np.zeros((50, 50), np.uint64)
                for image in self.model['data'][char]:
                    canvas += image

                canvas = np.floor_divide(canvas, len(self.model['data'][char]))
                canvas = np.uint8(canvas)
                self.model['data'][char] = canvas
        else:
            raise RuntimeError('Equalization cannot be False for this qqocr version.')

    def save_model(self, path: str):
        """保存模型"""
        assert path.endswith('.qmodel')

        self.model['function'] = self.binary_function
        with open(path, 'wb') as file:
            dill.dump(self.model, file)

    def load_model(self, path: str):
        """加载模型"""
        assert path.endswith('.qmodel')

        with open(path, 'rb') as file:
            self.model = dill.load(file)

    def predict(self, image):
        """通过已加载的模型预测图片文本"""
        binary = self.model['function'](image)
        interval = self.model['interval']
        char_list = split(binary, interval=interval)
        predict_list = []
        for char_image in char_list:
            predict_char, max_score = '', 0
            for char in self.model['data'].keys():
                templ = self.model['data'][char]
                score = cal_diff(char_image, templ)
                if score > max_score:
                    predict_char, max_score = char, score
            predict_list.append(predict_char)
        return ''.join(predict_list)





