import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt

SCREEN_SIZE = [600, 450]
cord_x = 37.622504
cord_y = 55.75
z = 12


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.getImage()

    def keyPressEvent(self, event):
        global z
        if event.key() == Qt.Key_PageUp:
            if z < 19:
                z += 1

                self.getImage()

        if event.key() == Qt.Key_PageDown:
            if z > 2:
                z -= 1

                self.getImage()

    def getImage(self):
        global z
        map_request = f"http://static-maps.yandex.ru/1.x/?l=map&ll={cord_x},{cord_y}&z={z}"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)
        self.image.repaint()



    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        ## Изображение
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())