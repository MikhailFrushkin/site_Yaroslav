import os
from gimpfu import *


def xcf_to_png(in_file, out_folder):
    # Открыть файл XCF
    image = pdb.gimp_file_load(in_file, in_file)

    # Сохранить как PNG
    basename = os.path.basename(in_file)
    outfile = os.path.splitext(basename)[0] + '.png'
    out_path = os.path.join(out_folder, outfile)
    pdb.gimp_file_save(image, image.active_drawable, out_path, outfile)

    # Освободить память и закрыть изображение
    pdb.gimp_image_delete(image)

# Пример использования
xcf_to_png('/path/to/infile.xcf', '/path/to/outfolder/')