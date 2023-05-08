from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea,QApplication,
                             QHBoxLayout, QGroupBox, QGridLayout, QVBoxLayout, QMainWindow, QFrame, QListWidget,)
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, uic, QtGui
import sys

from pondFrame import PondFrame


class PondDashboard(QMainWindow):

    def __init__(self,connected_pond):
        super().__init__()
        self.connected_ponds = connected_pond
        self.label = QLabel(self)
        self.list_widget = QListWidget(self)
        self.update_dashboard()
        self.initUI()

    def update_dashboard(self):
        # self.connected_ponds = connected_ponds
        temp = self.connected_ponds.values()
        self.list_widget.clear()
        for items in temp:
            
            self.list_widget.addItem(str(items))

    def initUI(self):

        self.scroll = (QScrollArea())
        self.widget = QWidget()
        self.vbox = (QVBoxLayout())
        self.grid = QGridLayout()


        font = self.label.font()
        font.setPointSize(20)
        font.setBold(True)
        self.label.setFont(font)
        self.connectLabel = QLabel()
        self.connectLabel.setText("Connected Ponds:")
        self.connectLabel.setFont(font)


        self.vbox.addWidget(self.connectLabel)
        self.vbox.addWidget(self.list_widget)
        self.vbox.addLayout(self.grid)
        self.widget.setLayout(self.vbox)
       


        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(0, 20, 800, 200)
        self.setWindowTitle('Pond Dashboard')
        self.show()

        return
    
    def update(self):
        pass