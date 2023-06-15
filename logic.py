"""Модуль с логической частью приложения"""

from collections import defaultdict
import time

from utils import log, match, calculateSpeed, readFromJson, sendToJson, \
    getTextFromChosenFile
from gui import KeyboardTrainApp, KeyboardListener


class KeyboardTrainer:
    """Главный класс"""

    def __init__(self):
        """Создание и загрузка приложения"""
        self.app = KeyboardTrainApp(self)
        self.app.run()
        self.keyboardInput = None

    def newInput(self, instance):
        """Ввод введенного текста в поле"""
        log('Новый текст')
        insertedText = self.app.TextInputWidget.text
        log('inserted text:', insertedText)

        if len(insertedText) == 0:
            return

        self.keyboardInput = KeyboardInput(insertedText,
                                           self.app, self.endInput)
        self.app.newPhrase(self.keyboardInput, insertedText)

    def endInput(self, textLen, totalClicks, inputTime, wrongLetters):
        """сохранение текущей статистики в файл и показ меню со статистикой"""
        nowSpeed = calculateSpeed(textLen, inputTime)
        nowMistakes = totalClicks - textLen

        data = readFromJson()
        if 'totalClicks' in data and data['totalClicks'] != 0:
            data['averageSpeed'] *= data['totalClicks']
            data['averageSpeed'] += totalClicks * nowSpeed
            data['totalClicks'] += totalClicks
            data['averageSpeed'] /= data['totalClicks']
            newWrongLetters = defaultdict(int)
            for letter in data['wrongLetters']:
                newWrongLetters[letter] = data['wrongLetters'][letter]
            for letter in wrongLetters:
                newWrongLetters[letter] += wrongLetters[letter]
            data['wrongLetters'] = newWrongLetters
        else:
            data['averageSpeed'] = nowSpeed
            data['totalClicks'] = totalClicks
            data['wrongLetters'] = wrongLetters
        sendToJson(data)

        log('Ты ввел этот текст')
        log('Скорость ввода:', nowSpeed)
        log('Время', round(inputTime, 1))
        log('Ошибки', nowMistakes)
        log('Средняя скорость:', data['averageSpeed'])

        self.keyboardInput = None
        self.app.endMenu(nowSpeed, nowMistakes, data['averageSpeed'])

    def interupt(self, instance):
        """Прерывание ввода"""
        self.keyboardInput.interupt()

    def reset(self, instance):
        """Удаление всей статистики"""
        sendToJson({})
        self.endInput(0, 0, 10, {})

    def loadText(self, instance):
        """Окно для выбора файла для ввода"""
        log('load text')
        text = getTextFromChosenFile()
        if not text is None:
            self.app.insertText(text)


class KeyboardInput:
    """Получение входных данных"""
    letterNumber = 0
    startTime = 0
    totalClicks = 0
    needToUnbind = False
    wrongLetters = defaultdict(int)

    def __init__(self, text, app, endFunc):
        """Чтение клавиатуры программой"""
        self.text = text
        self.app = app
        self.endFunc = endFunc
        self.listener = KeyboardListener(self.onKeyDown)

    def onKeyDown(self, keycode, text, modifiers):
        """Сброс статистики"""
        log('The key', keycode, 'have been pressed')
        log(' - modifiers are %r' % modifiers)
        if self.needToUnbind:
            return True

        if self.startTime == 0:
            self.startTime = time.time()

        if keycode[1] == 'enter':
            text = '\n'
        if keycode[1] == 'tab':
            text = '\t'

        if len(keycode[1]) == 1 or keycode[1] == 'spacebar' or \
                keycode[1] == 'tab' or keycode[1] == 'enter':
            self.totalClicks += 1

        if match(text, self.text[self.letterNumber], modifiers):
            log('Правильная буква!!!')
            self.letterNumber += 1
            self.app.addLetter(self.letterNumber, self.text)
        else:
            log('Неверная буква:', text,
                'Мне нужна:', (self.text[self.letterNumber],))
            self.wrongLetters[self.text[self.letterNumber]] += 1

        if len(self.text) == self.letterNumber:
            self.endInput()
            return True
        return False

    def interupt(self):
        """отвязка клавиатуры"""
        self.needToUnbind = True
        self.endInput()

    def endInput(self):
        """функция окончания ввода"""
        endTime = time.time()
        self.endFunc(self.letterNumber, self.totalClicks,
                     endTime - self.startTime, self.wrongLetters)
