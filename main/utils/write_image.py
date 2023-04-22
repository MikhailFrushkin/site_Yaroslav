from PIL import Image, ImageDraw, ImageFont
import numpy as np


def write_images_art(img, text1, text2):
    # Открываем изображение
    image = img
    width, height = image.size

    # Создаем объект ImageDraw
    draw = ImageDraw.Draw(image)

    # Задаем шрифт для надписей
    font = ImageFont.truetype("arial.ttf", 24)

    # Добавляем надпись в правый верхний угол
    bbox1 = draw.textbbox((0, 0), text1, font=font)
    x1 = width - bbox1[2] - 5
    y1 = 5
    draw.text((x1, y1), text1, font=font, fill="black")

    # Добавляем надпись в левый нижний угол
    bbox2 = draw.textbbox((0, 0), text2, font=font)
    x2 = 5
    y2 = height - bbox2[3] - 5
    draw.text((x2, y2), text2, font=font, fill="black")
    return image





