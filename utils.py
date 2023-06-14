"""Некоторые полезные функции"""

import json
import easygui
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

from config import e2E, e2r, e2R, DEBUG, STAT_FILE_NAME, MAX_SPEED
from char_map import get_all_pixels, get_coords


def log(*args):
    """Так же, как print, но только если DEBUG == True"""
    if DEBUG:
        print(*args)


def match(key, target, mod):
    """Совпадает ли нажатая клавиша с целевой буквой"""
    if key == target:
        return True
    if key not in e2E:
        return False
    if ('shift' in mod) ^ ('capslock' in mod):
        # capitalized
        return target in (e2R[key], e2E[key])
    # lower
    return target in (key, e2r[key])


def calculateSpeed(lettersNumber, time):
    """Вычисление скорости ввода"""
    return 60 * lettersNumber / time


def readFromJson():
    """Чтение статистики из файла"""
    file = open(STAT_FILE_NAME, 'r')
    data = json.load(file)
    file.close()
    return data


def sendToJson(data):
    """Запись новой статистики в файл"""
    file = open(STAT_FILE_NAME, 'w')
    json.dump(data, file)
    file.close()


def formSpeed(speed):
    """Округление результата"""
    if speed < MAX_SPEED:
        return str(round(speed, 1))
    return '>' + str(MAX_SPEED)


def getFrequencies(contents):
    """частота нажатий определенных клавиш"""
    heatmapData = np.asarray([[0] * 57] * 21)

    for char in contents:
        coords = get_coords(char)
        if coords:
            for coord in coords:
                x, y = coord
                heatmapData[x][y] += contents[char]

    total = np.sum(heatmapData)
    if total != 0:
        heatmapData = heatmapData / total

    for pixel in get_all_pixels(((18, 18), (19, 34))):
        x, y = pixel
        heatmapData[x][y] *= 0.3

    return heatmapData[::-1]


def blendAndShow(contents):
    """Тепловая карта ошибочных нажатий"""
    heatmapData = getFrequencies(contents)
    img = mpimg.imread('keyboard.png')

    plt.clf()
    plt.xticks([])
    plt.yticks([])
    plt.axis('off')

    plt.imshow(heatmapData, interpolation='lanczos', zorder=1,
               cmap='viridis', alpha=0.8)
    plt.imshow(img, extent=(0, 57, 0, 21))
    plt.show()


def getTextFromChosenFile():
    """Загрузка текста для набора из текстового файла"""
    file_name = easygui.fileopenbox()
    if file_name is None:
        return None
    file = open(file_name, 'r')
    text = file.read()
    file.close()
    return text


def mostMissButtons():
    """Самые ошибочные кнопки"""
    data = readFromJson()
    if 'wrongLetters' in data:
        heatmap = [(-c, l) for (l, c) in data['wrongLetters'].items()]
        heatmap.sort()
        return ' '.join([str(x[1]) for x in heatmap][:5])
    return 'No statistics yet'

def showHeatmap(instance):
    """Создание тепловой карты ошибок"""
    data = readFromJson()
    blendAndShow(data['wrongLetters'])
