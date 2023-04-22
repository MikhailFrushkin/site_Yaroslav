import glob
import hashlib
import os

import PyPDF2
import cv2
from PIL import Image
from loguru import logger
from skimage.metrics import structural_similarity as ssim

from main.settings import BASE_DIR
from read_excel.models import GroupedOrders, InfoProd, MyFiles
from utils.convert import convert


def search_folder(name):
    '''поиск папки по названию артикула'''
    for root, dirs, files in os.walk(os.path.join(BASE_DIR, 'files')):
        if name in dirs:
            folder = os.path.join(root, name)
            return os.path.normpath(folder)
    return None


def split_image(filename, dir_name, order):
    icon_dir = dir_name
    os.makedirs(icon_dir, exist_ok=True)
    folder_name = 'Значки по отдельности'
    size = None

    if not os.path.exists(os.path.join(icon_dir, folder_name)):
        os.makedirs(os.path.join(icon_dir, folder_name))
        print("Папка", folder_name, "была успешно создана в директории", icon_dir)
        image = cv2.imread(filename)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray_image, 240, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        scale_px_mm = 5  # 10 пикселей на 1 мм
        count = 1
        flag_56 = True

        for i in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])

            diameter_px = max(w, h)
            diameter_mm = diameter_px / scale_px_mm

            if 140 > diameter_mm > 110:
                print(diameter_mm)
                size = 37
                icon = image[y:y + h, x:x + w]
                cv2.imwrite(f"{icon_dir}/Значки по отдельности/{count}.png", icon)
                count += 1
                flag_56 = False
            elif 600 > diameter_mm > 200 and flag_56:
                print(flag_56)
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
            obj, created = InfoProd.objects.get_or_create(
                code_prod=order['code_prod'],
                size=size)
            prod = GroupedOrders.objects.filter(path_files=dir_name).first()
            prod.size = size
            prod.save()
        except Exception as ex:
            logger.debug(ex)
    else:
        print("Папка", folder_name, "уже существует в директории", icon_dir)
        try:
            obj, created = InfoProd.objects.get_or_create(
                code_prod=order['code_prod'],
                size=size)
            prod = GroupedOrders.objects.filter(path_files=dir_name).first()
            if size:
                prod.size = size
                prod.save()
        except Exception as ex:
            logger.debug(ex)


def unique_images_function(directory, order):
    hashes = {}
    unique_images = []
    folder_name = 'Значки по отдельности'
    out_dir = os.path.join(directory, folder_name)
    # Задаем порог для SSIM
    ssim_threshold = 0.80
    folder_name2 = 'Уникальные значки'
    if not os.path.exists(os.path.join(directory, folder_name2)):
        os.makedirs(os.path.join(directory, folder_name2))
        print("Папка", folder_name2, "была успешно создана в директории", directory)
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
            img.save(f'{os.path.join(directory, folder_name2)}/{i + 1}.png')
            print(i + 1)

        prod = GroupedOrders.objects.get(code_prod=order['code_prod'])
        prod.quantity = len(unique_images)
        prod.save()
        order_info = InfoProd.objects.get(code_prod=order['code_prod'])
        order_info.quantity = len(unique_images)
        order_info.save()
    else:
        print("Папка", folder_name2, "уже существует в директории", out_dir)

        order_info = InfoProd.objects.get(code_prod=order['code_prod'])
        prod = GroupedOrders.objects.get(code_prod=order['code_prod'])
        prod.quantity = order_info.quantity
        prod.save()


def distribute_images(queryset):
    A4_WIDTH = 2480
    A4_HEIGHT = 3508
    dict_sizes_images = {
        25: (35, 20),
        37: (51, 20),
        44: (53, 16),
        56: (70, 12)
    }
    # dict_sizes_images = {
    #     25: (35, 20),
    #     37: (48, 20),
    #     44: (53, 16),
    #     56: (66, 12)
    # }
    size_images_param = dict_sizes_images[queryset.first().size]

    ICON_SIZE = int((dict_sizes_images[queryset.first().size][0] / 25.4) * 300)
    if queryset.first().size == 56:
        GAP_SIZE_PX = 0
    else:
        GAP_SIZE = 1
        GAP_SIZE_PX = int(GAP_SIZE / 25.4 * 300)

    COUNT_PER_PAGE = size_images_param[1]
    if COUNT_PER_PAGE == 20:
        ICONS_PER_ROW = 4
        ICONS_PER_COL = 5
    elif COUNT_PER_PAGE == 12:
        ICONS_PER_ROW = 3
        ICONS_PER_COL = 4
    groups = []
    arts_list_orders = []
    for i, product in enumerate(queryset):
        num = product.total_num
        path_images = f'{product.path_files}/Уникальные значки/'
        files = glob.glob(path_images + '/*.png')
        files = sorted(files, key=lambda x: int(os.path.basename(x).split('.')[0]))
        for _ in range(product.total_num):
            groups.append(files)
        print(f'Артикул: {product.code_prod}')
        print(f'Количество значков в папке: {len(files)}')
        print(f'Количество значков  в общем на {num} заказов: {len(files) * num}')
        print()
    groups = sorted(groups, key=lambda x: -len(x))
    result = []
    i = 0
    while len(groups) > 0:
        j = 1
        new_group = []
        new_group.extend(groups[i])
        arts_list_orders.append(os.path.dirname(os.path.abspath(groups[i][0])))
        while j < len(groups) or len(new_group) == COUNT_PER_PAGE:
            try:
                group = groups[j]
            except Exception as ex:
                print(ex)
                break
            len_collect = len(new_group) + len(group)
            if len_collect <= COUNT_PER_PAGE:
                new_group.extend(group)
                arts_list_orders.append(os.path.dirname(os.path.abspath(group[0])))
                groups.pop(j)
            else:
                j += 1
            if len(new_group) == COUNT_PER_PAGE:
                break
        groups.pop(i)
        result.append(new_group)

    for i in range(len(arts_list_orders)):
        arts_list_orders[i] = arts_list_orders[i].replace("/Уникальные значки", "")

    for num, set_images in enumerate(result):
        result_image = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), (255, 255, 255))
        for i in range(0, ICONS_PER_ROW * ICONS_PER_COL, COUNT_PER_PAGE):
            try:
                for file in set_images:
                    icon_image = Image.open(file).convert('RGBA')
                    background = Image.new('RGBA', icon_image.size, (255, 255, 255, 255))
                    alpha_composite = Image.alpha_composite(background, icon_image)
                    icon_image = alpha_composite.crop(alpha_composite.getbbox())
                    icon_image = icon_image.resize((ICON_SIZE, ICON_SIZE))
                    # Вычисляем координаты для размещения изображения на листе A4
                    row = i // ICONS_PER_ROW
                    col = i % ICONS_PER_ROW
                    x = col * (ICON_SIZE + GAP_SIZE_PX) + (
                            A4_WIDTH - ICON_SIZE * ICONS_PER_ROW - GAP_SIZE_PX * (ICONS_PER_ROW - 1)) // 2
                    y = row * (ICON_SIZE + GAP_SIZE_PX) + (
                            A4_HEIGHT - ICON_SIZE * ICONS_PER_COL - GAP_SIZE_PX * (ICONS_PER_COL - 1)) // 2
                    # Размещаем изображение на листе A4
                    result_image.paste(icon_image, (x, y))
                    i += 1
            except Exception as ex:
                logger.debug(ex)
            image_path = f'{BASE_DIR}/output/{queryset.first().size}/result_{queryset.first().size}_{num + 1}.png'
            result_image.save(image_path)
            MyFiles.objects.create(image=image_path,
                                   name=f'result_{COUNT_PER_PAGE}_{num + 1}.png',
                                   size=queryset.first().size)
    try:
        create_pdf(arts_list_orders, queryset.first().size)
    except Exception as ex:
        logger.debug(ex)
    try:
        create_six_images(arts_list_orders, queryset.first().size)
    except Exception as ex:
        logger.debug(ex)


def create_pdf(arts_list, size):
    pdf_files = []
    merged_pdf = PyPDF2.PdfMerger()
    for i in arts_list:
        files = glob.glob(i + '/*.pdf')
        if len(files) == 0:
            print(f'Не найдено pdf файлов в папке {i}')
        else:
            pdf_files.append(files[0])
    for file_name in pdf_files:
        with open(file_name, 'rb') as pdf_file:
            merged_pdf.append(pdf_file)

    # сохраняем объединенный PDF файл в новый файл
    with open(f'{BASE_DIR}/output/{size}/merged_file.pdf', 'wb') as output:
        merged_pdf.write(output)


def create_six_images(arts_list, size):
    images = []
    full_list_skins = []
    skin_list = set(arts_list)
    for i in arts_list:
        try:
            full_list_skins.append(os.path.join(i, 'Обложка/skin.png'))
        except Exception as ex:
            logger.debug(f'{i} - {ex}')
            continue
    for i in skin_list:
        if not os.path.exists(os.path.join(i, 'Обложка/skin.png')):
            files = glob.glob(i + '/*.xcf')
            if len(files) == 0:
                continue
            else:
                files = sorted(files, key=lambda f: os.path.getsize(f))
                convert(files[0], name_file='skin')

    for i in full_list_skins:
        if os.path.exists(i):
            images.append(i)
    try:
        save_as_pdf(images, size)
    except Exception as ex:
        logger.debug(f'{ex}')


def save_as_pdf(images, size):
    A4_WIDTH = 2480
    A4_HEIGHT = 3508

    SIZE_H = int(A4_HEIGHT / 3) - 40
    SIZE_W = int(A4_WIDTH / 3) - 40
    GAP_SIZE = 1
    GAP_SIZE_PX = int(GAP_SIZE / 25.4 * 300)

    ICONS_PER_ROW = 3
    ICONS_PER_COL = 3
    result_image = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), (255, 255, 255))
    num_page = 1
    for num, set_images in enumerate(images):
        try:
            icon_image = Image.open(set_images).convert('RGBA')
            background = Image.new('RGBA', icon_image.size, (255, 255, 255, 255))
            alpha_composite = Image.alpha_composite(background, icon_image)
            icon_image = alpha_composite.crop(alpha_composite.getbbox())
            icon_image = icon_image.resize((SIZE_W, SIZE_H))
            # Вычисляем координаты для размещения изображения на листе A4
            row = (num % 9) // ICONS_PER_ROW
            col = num % ICONS_PER_ROW
            x = col * (SIZE_W + GAP_SIZE_PX) + (
                    A4_WIDTH - SIZE_W * ICONS_PER_ROW - GAP_SIZE_PX * (ICONS_PER_ROW - 1)) // 2
            y = row * (SIZE_H + GAP_SIZE_PX) + (
                    A4_HEIGHT - SIZE_H * ICONS_PER_COL - GAP_SIZE_PX * (ICONS_PER_COL - 1)) // 2
            # Размещаем изображение на листе A4
            result_image.paste(icon_image, (x, y))
            if (num + 1) % 9 == 0:
                image_path = f'{BASE_DIR}/output/{size}/skin_{num_page}.png'
                result_image.save(image_path)
                result_image = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), (255, 255, 255))
                num_page += 1
        except Exception as ex:
            logger.debug(ex)
    image_path = f'{BASE_DIR}/output/{size}/skin_{num_page}.png'
    result_image.save(image_path)
