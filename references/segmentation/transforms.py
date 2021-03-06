# -*- coding: utf-8 -*-

'''
Transformation for semantic segmentation
'''

import random
import numpy as np
import torch
from PIL import Image
from torchvision.transforms import transforms
from torchvision.transforms import functional as F


def pad_if_smaller(img, size, fill=0):
    min_size = min(img.size)
    if min_size < size:
        ow, oh = img.size
        padh = size - oh if oh < size else 0
        padw = size - ow if ow < size else 0
        img = F.pad(img, (0, 0, padw, padh), fill=fill)
    return img


class Compose(transforms.Compose):
    def __init__(self, transforms):
        super(Compose, self).__init__(transforms)

    def __call__(self, image, target):
        for t in self.transforms:
            image, target = t(image, target)
        return image, target


class RandomResize(object):
    def __init__(self, min_size, max_size=None):
        self.min_size = min_size
        if max_size is None:
            max_size = min_size
        self.max_size = max_size

    def __call__(self, image, target):
        if self.min_size == self.max_size:
            size = self.min_size
        else:
            size = random.randint(self.min_size, self.max_size)
        image = F.resize(image, (size, size))
        target = F.resize(target, (size, size), interpolation=Image.NEAREST)
        return image, target

    def __repr__(self):
        return f"{self.__class__.__name__}(min_size={self.min_size}, max_size={self.max_size})"


class RandomHorizontalFlip(object):
    def __init__(self, prob):
        self.prob = prob

    def __call__(self, image, target):
        if random.random() < self.prob:
            height, width = image.size
            image = F.hflip(image)
            # Flip the segmentation
            target = F.hflip(target)

        return image, target

    def __repr__(self):
        return f"{self.__class__.__name__}(p={self.prob})"


class RandomCrop(object):
    def __init__(self, size):
        self.size = size

    def __call__(self, image, target):
        image = pad_if_smaller(image, self.size)
        target = pad_if_smaller(target, self.size, fill=255)
        crop_params = transforms.RandomCrop.get_params(image, (self.size, self.size))
        image = F.crop(image, *crop_params)
        target = F.crop(target, *crop_params)
        return image, target

    def __repr__(self):
        return f"{self.__class__.__name__}(size={self.size})"


class ToTensor(transforms.ToTensor):
    def __call__(self, img, target):

        img = super(ToTensor, self).__call__(img)
        target = torch.as_tensor(np.array(target), dtype=torch.int64)

        return img, target


class SampleTransform(object):
    def __init__(self, transform):
        self.transform = transform

    def __call__(self, image, target):
        image = self.transform.__call__(image)
        return image, target

    def __repr__(self):
        return self.transform.__repr__()
