import os
from subprocess import run


def convert(file, name_file='new'):
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
        f'"{os.path.join(folder, f"{name_file}.png")}" f"{name_file}.png")',
        '-b',
        '(gimp-quit 0)'
    ]

    run(gimp_command, shell=False)
    print(f'{os.path.join(folder, f"{name_file}.png")}')
    return f'{os.path.join(folder, f"{name_file}.png")}'


if __name__ == '__main__':
    convert('SKZ-5NEW-NABORxPLYAZH37.xcf')
