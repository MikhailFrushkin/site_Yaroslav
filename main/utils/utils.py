import os

import pandas as pd

from main.settings import BASE_DIR
import glob


def search_folder(name):
    '''поиск папки по названию артикула'''
    for root, dirs, files in os.walk(os.path.join(BASE_DIR, 'files')):
        if name in dirs:
            return os.path.join(root, name)
    return None
