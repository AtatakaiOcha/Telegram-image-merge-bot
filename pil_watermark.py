# -*- coding: utf-8 -*-
from PIL import Image
import os


watermark_default = os.getcwd() + "\\watermark_images\\default.jpg"


def merge_watermark(photo, crd, user_id):
    watermark = os.getcwd() + f"\\watermark_images\\{user_id}.jpg"
    img = Image.open(photo)
    if os.path.exists(os.getcwd() + f"\\watermark_images\\{user_id}.jpg"):
        watermark_image = Image.open(watermark)
        img.paste(watermark_image, (crd[0], crd[1]))
    else:
        watermark_image = Image.open(watermark_default)
        img.paste(watermark_image, (crd[0], crd[1]))
    img.save(photo)
