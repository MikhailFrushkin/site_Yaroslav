import os
import subprocess


def convert_xcf_to_png(xcf_file_path):
    gimp_path = r"C:\Program Files\GIMP 2\bin\gimp-2.10.exe"

    # путь к исходному файлу
    input_file = xcf_file_path

    # получение имени файла без расширения
    file_name = os.path.splitext(os.path.basename(input_file))[0]

    # путь к файлу результата
    output_file = os.path.join(os.path.dirname(input_file), f"{file_name}_2.png")
    print(output_file)

    # команда для конвертации изображения в GIMP

    command = [
        gimp_path,
        '-i',  # запускать без интерактивного режима
        '-b', '(gimp-file-load RUN-NONINTERACTIVE "{}" "{}")'.format(input_file.replace('\\', '/'),
                                                                     input_file.replace('\\', '/')),
        # загрузить исходный файл
        '-b',
        r'(gimp-file-save RUN-NONINTERACTIVE 1 "{}" {})'.format(
            '(gimp-image-get-active-drawable (car (gimp-image-list)))',
            output_file.replace('\\', '/'),
            0.9,  # compression level
            1,  # save background transparency
            0,  # save color space information
        ),
        '-b',
        '(gimp-quit 0)'
    ]
    process = subprocess.Popen(command)


if __name__ == '__main__':
    convert_xcf_to_png(r'C:\Users\site_Yaroslav\main\files\SKZ-5NEW-NABORxPLYAZH37\SKZ-5NEW-NABORxPLYAZH37.xcf')
