import os
from subprocess import run


def convert(file):
    print(file)
    filename = file
    folder = os.path.dirname(os.path.abspath(file))
    print(folder)
    gimp_path = '/usr/bin/gimp'
    # Конвертируем файл в формат .png
    gimp_command = [
        gimp_path,
        '-i',
        '-b',
        f'(gimp-file-load RUN-NONINTERACTIVE "{filename}" "{filename}")',
        '-b',
        f'(gimp-file-save RUN-NONINTERACTIVE 1 (car (gimp-image-merge-visible-layers (aref (cadr (gimp-image-list)) 0) 0)) '
        f'"{os.path.join(folder, "new.png")}" "new.png")',
        '-b',
        '(gimp-quit 0)'
    ]

    run(gimp_command, shell=False)
    return f'{os.path.join(folder, "new.png")}'


if __name__ == '__main__':
    convert('SKZ-5NEW-NABORxPLYAZH37.xcf')
