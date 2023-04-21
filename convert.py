import os
from subprocess import run


def convert(file):
    filename = file
    folder = os.path.dirname(os.path.abspath('SKZ-5NEW-NABORxPLYAZH37.xcf'))
    print(folder)
    gimp_path = r"C:\Program Files\GIMP 2\bin\gimp-2.10.exe"
    # Конвертируем файл в формат .png
    gimp_command = [
        gimp_path,
        '-i',
        '-b',
        f'(gimp-file-load RUN-NONINTERACTIVE "{filename}" "{filename}")',
        '-b',
        f'(gimp-file-save RUN-NONINTERACTIVE 1 (car (gimp-image-merge-visible-layers (aref (cadr (gimp-image-list)) 0) 0)) '
        f'"{os.path.join("C:/Users/site_Yaroslav/", "new.png")}" "new.png")',
        '-b',
        '(gimp-quit 0)'
    ]


    run(gimp_command, shell=True)


if __name__ == '__main__':
    convert('C:/Users/site_Yaroslav/SKZ-5NEW-NABORxPLYAZH37.xcf')

