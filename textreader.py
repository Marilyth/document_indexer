import pytesseract
from PIL import ImageGrab, Image, ImageDraw, ImageFilter
import PIL
import requests
import os
import subprocess
import sys
import math
import cv2
import numpy as np

def open_image(path: str):
    return Image.open(path)

def process_image(image: Image.Image, relative_box: tuple = None, use_contour_inversion = False) -> Image.Image:
    """
    relative_box in this format (relative_left, relative_top, relative_width, relative_height).
    focus_colour is an rgb tuple of the colour of your text to focus on. It will be converted to black, anything else to white.
    focus_distance_dropoff is the maximum distance in RGB space between focus_colour and the pixel before being replaced by white.
    """
    bbox = image.getbbox()
    crop_box = bbox if relative_box is None else (bbox[0] + (bbox[2] - bbox[0]) * (1 - relative_box[0]), 
                                                  bbox[1] + (bbox[-1] - bbox[1]) * (1 - relative_box[1]), 
                                                  (bbox[0] + (bbox[2] - bbox[0]) * (1 - relative_box[0])) + (bbox[2] - bbox[0]) * relative_box[2], 
                                                  (bbox[1] + (bbox[-1] - bbox[1]) * (1 - relative_box[1])) + (bbox[-1] - bbox[1]) * relative_box[-1])
    cropped_image = image.crop(crop_box)
    cropped_image = cropped_image.convert("L")

    img = np.asarray(cropped_image, dtype="uint8")
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 5)

    if use_contour_inversion:
        h, w = img.shape[:2]
        mask = np.zeros((h + 2, w + 2), np.uint8)
        for i in range(0, w, 5):
            cv2.floodFill(img, mask, (i, 0), 0)

    cropped_image = Image.fromarray(img)

    draw = ImageDraw.Draw(image)
    draw.rectangle(crop_box, outline="black")
    image.save("selection_showcase.png")

    cropped_image = cropped_image.filter(ImageFilter.SHARPEN)
    cropped_image = cropped_image.convert("L")
    cropped_image.save("ai_image_input.png")

    return cropped_image

def read_image_text(image: Image.Image, psm: int = 3, oem: int = 3, user_words: list = None) -> str:
    """
    relative_box in this format (relative_left, relative_top, relative_width, relative_height).
    focus_colour is an rgb tuple of the colour of your text to focus on. It will be converted to black, anything else to white.
    focus_distance_dropoff is the maximum distance in RGB space between focus_colour and the pixel before being replaced by white.
    """
    if user_words:
        with open("user_words.txt", "w") as f:
            f.write("\n".join(user_words))
        config = f"--oem {oem} --psm {psm} --user-words \"{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_words.txt')}\""
    else:
        config = f"--oem {oem} --psm {psm}"

    try:
        return pytesseract.image_to_string(image, config=config)
    except pytesseract.TesseractNotFoundError as e:
        print(e)
        download_tesseract()
        return pytesseract.image_to_string(image, config=config)
