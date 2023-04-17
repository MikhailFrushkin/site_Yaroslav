import os
import cv2
import hashlib
import pandas as pd
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from main.settings import BASE_DIR
import glob

from read_excel.models import GroupedOrders


def search_folder(name):
    '''поиск папки по названию артикула'''
    for root, dirs, files in os.walk(os.path.join(BASE_DIR, 'files')):
        if name in dirs:
            return os.path.join(root, name)
    return None


def split_image(filename, dir_name):
    icon_dir = dir_name
    image = cv2.imread(filename)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_image, 240, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    scale_px_mm = 5  # 10 пикселей на 1 мм
    os.makedirs(icon_dir, exist_ok=True)
    count = 1
    size = None
    folder_name = 'Значки по отдельности'

    if not os.path.exists(os.path.join(icon_dir, folder_name)):
        os.makedirs(os.path.join(icon_dir, folder_name))
        print("Папка", folder_name, "была успешно создана в директории", icon_dir)
        for i in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])

            diameter_px = max(w, h)
            diameter_mm = diameter_px / scale_px_mm
            if 150 > diameter_mm > 100:
                print(diameter_mm)
                size = 37
                icon = image[y:y + h, x:x + w]
                cv2.imwrite(f"{icon_dir}/Значки по отдельности/{count}.png", icon)
                count += 1
            elif 600 > diameter_mm > 200:
                size = 56
                print(f'большие значки {diameter_mm}')
                if w > h:  # vertical rectangle
                    # split image into 3 equal parts vertically
                    h1 = h // 3
                    h2 = h1 * 2
                    icon1 = image[y:y + h, x:x + w // 3]
                    icon2 = image[y:y + h, x + w // 3:x + w // 3 * 2]
                    icon3 = image[y:y + h, x + w // 3 * 2:x + w]
                    cv2.imwrite(f"{icon_dir}/Значки по отдельности/{count}.png", icon1)
                    count += 1
                    cv2.imwrite(f"{icon_dir}/Значки по отдельности/{count}.png", icon2)
                    count += 1
                    cv2.imwrite(f"{icon_dir}/Значки по отдельности/{count}.png", icon3)
                    count += 1
        try:
            prod = GroupedOrders.objects.filter(path_files=dir_name).first()
            prod.size = size
            prod.save()
        except Exception as ex:
            print(ex)
    else:
        print("Папка", folder_name, "уже существует в директории", icon_dir)


def unique_images_function(directory):
    hashes = {}
    unique_images = []
    folder_name = 'Значки по отдельности'
    out_dir = os.path.join(directory, folder_name)
    # Задаем порог для SSIM
    ssim_threshold = 0.80
    folder_name2 = 'Уникальные значки'
    if not os.path.exists(os.path.join(out_dir, folder_name2)):
        os.makedirs(os.path.join(out_dir, folder_name2))
        print("Папка", folder_name2, "была успешно создана в директории", out_dir)
        # Проходимся по каждому изображению
        for i in range(1, len(os.listdir(out_dir)) + 1):
            # Открываем изображение и вычисляем его хеш
            try:
                with Image.open(f'{out_dir}/{i}.png') as img:
                    hash = hashlib.md5(img.tobytes()).hexdigest()
                    if hash in hashes:
                        continue
                    unique = True
                    for j in range(1, i):
                        img1 = cv2.imread(f'{out_dir}/{i}.png')
                        img2 = cv2.imread(f'{out_dir}/{j}.png')
                        gray_img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
                        gray_img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
                        h1, w1 = gray_img1.shape
                        h2, w2 = gray_img2.shape
                        # Если изображения имеют разные размеры, изменить размер одного или обоих изображений
                        if h1 != h2 or w1 != w2:
                            # Найти наибольший размер
                            min_h, min_w = max(h1, h2), max(w1, w2)
                            gray_img1 = cv2.resize(gray_img1, (min_w, min_h))
                            gray_img2 = cv2.resize(gray_img2, (min_w, min_h))
                        similarity_score = ssim(gray_img1, gray_img2)
                        if similarity_score > ssim_threshold:
                            unique = False
                            break
                    if unique:
                        hashes[hash] = i
                        unique_images.append(img)
            except Exception as ex:
                print(ex)
                continue
        for i, img in enumerate(unique_images):
            img.save(f'{os.path.join(out_dir, folder_name2)}/{i + 1}.png')
            print(i + 1)
        prod = GroupedOrders.objects.get(path_files=directory)
        prod.quantity = len(unique_images)
        prod.save()
    else:
        print("Папка", folder_name2, "уже существует в директории", out_dir)


def add_images(queryset):
    A4_WIDTH = 2480
    A4_HEIGHT = 3508
    dict_sizes_images = {
        25: (35, 20),
        37: (48, 20),
        44: (53, 16),
        56: (66, 12)
    }
    ICON_SIZE = int((dict_sizes_images[queryset.first().size][0] / 25.4) * 300)
    size_images_param = dict_sizes_images[queryset.first().size]
    COUNT_PER_PAGE = size_images_param[1]
    if size_images_param[1] == 20:
        ICONS_PER_ROW = 4
        ICONS_PER_COL = 5
    elif size_images_param[1] == 12:
        ICONS_PER_ROW = 3
        ICONS_PER_COL = 4
    for product in queryset:
        num = product.total_num
        path_images = f'{product.path_files}/Значки по отдельности/Уникальные значки/'
        files = glob.glob(path_images + '/*.png')
        print(files)
        print(f'Количество значков в папке: {len(files)}')
        print(f'Количество значков  в общем на {num} заказов: {len(files) * num}')
        all_images = len(files) * num
        num_page = len(files) * num // COUNT_PER_PAGE
        if len(files) * num % COUNT_PER_PAGE > 0:
            num_page += 1
        print(f'Количество листов: {num_page}')
        for page in range(num_page):
            result_image = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), (255, 255, 255))
            for i in range(0, ICONS_PER_ROW * ICONS_PER_COL, len(files)):
                if i > COUNT_PER_PAGE or all_images == 0:
                    break
                try:
                    for file in files:
                        if all_images == 0:
                            break
                        icon_image = Image.open(file).convert('RGBA')
                        background = Image.new('RGBA', icon_image.size, (255, 255, 255, 255))
                        alpha_composite = Image.alpha_composite(background, icon_image)
                        icon_image = alpha_composite.crop(alpha_composite.getbbox())
                        icon_image = icon_image.resize((ICON_SIZE, ICON_SIZE))
                        # Вычисляем координаты для размещения изображения на листе A4
                        row = i // ICONS_PER_ROW
                        col = i % ICONS_PER_ROW
                        x = col * ICON_SIZE + (A4_WIDTH - ICON_SIZE * ICONS_PER_ROW) // 2
                        y = row * ICON_SIZE + (A4_HEIGHT - ICON_SIZE * ICONS_PER_COL) // 2
                        # Размещаем изображение на листе A4
                        result_image.paste(icon_image, (x, y))
                        i += 1
                        all_images -= 1
                except Exception as ex:
                    print(ex)
            result_image.save(f'result_{product.name_product}_{page + 1}.png')


def distribute_images(queryset):
    group1 = ['img1_1', 'img1_2', 'img1_3', 'img1_4']
    group2 = ['img2_1', 'img2_2', 'img2_3', 'img2_4', 'img2_5', 'img2_6', 'img2_7', 'img2_8']

    groups = [group1, group1,
              group2, group2,
              ]

    groups = sorted(groups, key=lambda x: -len(x))
    total_length = sum(len(group) for group in groups)
    print(total_length)
    result = []
    i = 0
    while len(groups) > 0:
        j = 1
        new_group = []
        new_group.extend(groups[i])
        while j < len(groups) or len(new_group) == 20:
            try:
                group = groups[j]
            except Exception as ex:
                print(ex)
                break
            len_collect = len(new_group) + len(group)
            if len_collect <= 20:
                new_group.extend(group)
                groups.pop(j)
            else:
                j += 1
            if len(new_group) == 20:
                break
        groups.pop(i)
        result.append(new_group)
    for row in result:
        print(len(row), row)

if __name__ == '__main__':
    dict_images = {
        'набор1': {
            'количество в наборе': 4,
            'количество наборов': 3
        },
        'набор2': {
            'количество в наборе': 8,
            'количество наборов': 4
        },
        'набор3': {
            'количество в наборе': 1,
            'количество наборов': 30
        },
        'набор4': {
            'количество в наборе': 20,
            'количество наборов': 3
        },
    }
    distribute_images(dict_images)
