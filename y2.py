import os
import sys
from PIL import Image
from io import BytesIO
from PyQt5 import uic
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget
from PyQt5.QtCore import Qt


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('api.ui', self)

        self.cord_x = 37.622504
        self.cord_y = 55.75
        self.z = 16
        self.cord_znach = 0.05
        self.type = 'map'

        self.map.toggled.connect(self.kind_of_map)
        self.sat.toggled.connect(self.kind_of_map)
        self.gibrid.toggled.connect(self.kind_of_map)

        self.OK.clicked.connect(self.getImage)

        self.find_adress.clicked.connect(self.input)

        self.flag = False  # Метка
        self.flag_x = self.cord_x
        self.flag_y = self.cord_y

        self.getImage()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            if self.z < 19:
                self.z += 1
                self.getImage()

        if event.key() == Qt.Key_PageDown:
            if self.z > 2:
                self.z -= 1
                self.getImage()

        if 2 <= self.z <= 4:
            self.cord_znach = 4
        elif 4 <= self.z < 6:
            self.cord_znach = 1
        elif 6 <= self.z <= 8:
            self.cord_znach = 0.5
        elif 8 <= self.z <= 12:
            self.cord_znach = 0.05
        elif 12 <= self.z <= 16:
            self.cord_znach = 0.005
        elif 16 <= self.z <= 19:
            self.cord_znach = 0.0005

        if event.key() == Qt.Key_Left or event.key() == Qt.Key_A:
            if self.cord_x - self.cord_znach > -179:
                self.cord_x -= self.cord_znach
            else:
                self.cord_x = -self.cord_x
                self.cord_x -= self.cord_znach
            self.getImage()

        if event.key() == Qt.Key_Right or event.key() == Qt.Key_D:
            if self.cord_x + self.cord_znach < 179:
                self.cord_x += self.cord_znach
            else:
                self.cord_x = -self.cord_x
                self.cord_x += self.cord_znach
            self.getImage()

        if event.key() == Qt.Key_Down or event.key() == Qt.Key_S:
            if self.cord_y - self.cord_znach >= -69:
                self.cord_y -= self.cord_znach
                self.getImage()

        if event.key() == Qt.Key_Up or event.key() == Qt.Key_W:
            if self.cord_y + self.cord_znach <= 69:
                self.cord_y += self.cord_znach
                self.getImage()

    def getImage(self):
        if self.flag:
            map_request = f"http://static-maps.yandex.ru/1.x/?l={self.type}&ll={self.cord_x},{self.cord_y}&z={self.z}&pt={self.flag_x},{self.flag_y},comma"
        elif not self.flag:
            map_request = f"http://static-maps.yandex.ru/1.x/?l={self.type}&ll={self.cord_x},{self.cord_y}&z={self.z}&l=map"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        if self.type == 'map':
            self.map_file = "map.png"
        else:
            self.map_file = "map.jpg"
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)
        self.image.repaint()

    def kind_of_map(self):
        if self.sender().text() == 'Схема':
            self.type = 'map'
        elif self.sender().text() == 'Спутник':
            self.type = 'sat'
        elif self.sender().text() == 'Гибрид':
            self.type = 'sat,skl'

    def input(self):
        self.flag = True
        self.z = 16
        toponym_to_find = self.adress_input.text()

        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym_to_find,
            "format": "json"}

        response = requests.get(geocoder_api_server, params=geocoder_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Преобразуем ответ в json-объект
        json = response.json()
        # Получаем первый топоним из ответа геокодера.
        toponym = json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]
        # Долгота и широта:
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

        self.cord_x = float(toponym_longitude)
        self.cord_y = float(toponym_lattitude)
        self.flag_x = self.cord_x
        self.flag_y = self.cord_y

        self.getImage()

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        try:
            os.remove('map.png')
            os.remove('map.jpg')
        except Exception:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())