import sys, os, subprocess
import matplotlib
import time
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QAction,
    QFileDialog,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QWidget,
    QFrame,
    QLineEdit,
)


class SecondWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.label = QLabel("New Window")
        layout.addWidget(self.label)

        self.container = QWidget()
        self.container.setLayout(layout)
        self.setCentralWidget(self.container)


class MainWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super(MainWindow, self).__init__(parent)
        self.data_window = SecondWindow()

        self.setWindowTitle("Test GUI layout")
        self.resize(1200, 677)

        self.page_layout = QVBoxLayout()

        entry_boxes = QWidget()
        entry_layout = QFormLayout()
        entry_boxes.setLayout(entry_layout)
        mass_entry = QLineEdit()
        area_entry = QLineEdit()
        entry_layout.addRow("Enter electrode mass:", mass_entry)
        entry_layout.addRow("Enter electrode area:", area_entry)
        self.page_layout.addWidget(entry_boxes)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setLineWidth(3)
        self.page_layout.addWidget(div)

        aging_wid = QWidget()
        aging_layout = QVBoxLayout()
        aging_wid.setLayout(aging_layout)
        aging_files_button = QPushButton("Add aging data...")
        aging_files_button.setFixedHeight(41)
        aging_files_button.setFixedWidth(200)
        message = QLabel("Aging Files Here")
        aging_layout.addWidget(message)
        aging_layout.addWidget(aging_files_button)
        self.page_layout.addWidget(aging_wid)

        div2 = QFrame()
        div2.setFrameShape(QFrame.HLine)
        div2.setLineWidth(3)
        self.page_layout.addWidget(div2)

        cvs = QWidget()
        cvs_layout = QVBoxLayout()
        labels = QHBoxLayout()
        label_b = QLabel("CVs before aging")
        label_a = QLabel("CVs after aging")
        labels.addWidget(label_b)
        labels.addWidget(label_a)
        buttons = QHBoxLayout()

        five_before = QPushButton("5 mV/s")
        p_5_before = QPushButton("0.5 mV/s")
        buttons.addWidget(five_before)
        buttons.addWidget(p_5_before)

        five_after = QPushButton("5 mV/s")
        p_5_after = QPushButton("0.5 mV/s")
        buttons.addWidget(five_after)
        buttons.addWidget(p_5_after)

        cvs_layout.addLayout(labels)
        cvs_layout.addLayout(buttons)
        cvs.setLayout(cvs_layout)

        self.page_layout.addWidget(cvs)

        div3 = QFrame()
        div3.setFrameShape(QFrame.HLine)
        div3.setLineWidth(3)
        self.page_layout.addWidget(div3)

        eis = QWidget()
        eis_layout = QHBoxLayout()
        eis_before = QVBoxLayout()
        eis_after = QVBoxLayout()
        eis_layout.addLayout(eis_before)
        eis_layout.addLayout(eis_after)
        eis.setLayout(eis_layout)

        eis_label_b = QLabel("EIS before aging")
        ocv_b = QPushButton("OCV EIS")
        p5_b = QPushButton("0.5 V EIS")
        one_b = QPushButton("1 V EIS")

        eis_before.addWidget(eis_label_b)
        eis_before.addWidget(ocv_b)
        eis_before.addWidget(p5_b)
        eis_before.addWidget(one_b)

        eis_label_a = QLabel("EIS after aging")
        ocv_a = QPushButton("OCV EIS")
        p5_a = QPushButton("0.5 V EIS")
        one_a = QPushButton("1 V EIS")

        eis_after.addWidget(eis_label_a)
        eis_after.addWidget(ocv_a)
        eis_after.addWidget(p5_a)
        eis_after.addWidget(one_a)
        self.page_layout.addWidget(eis)

        div4 = QFrame()
        div4.setFrameShape(QFrame.HLine)
        div4.setLineWidth(3)
        self.page_layout.addWidget(div4)

        process = QPushButton("Process data")
        process.setStyleSheet("background-color: #007AFF")
        process.clicked.connect(self.show_data_window)
        self.page_layout.addWidget(process)

        container = QWidget()
        container.setLayout(self.page_layout)
        self.setCentralWidget(container)

    def show_data_window(self):
        self.close()
        time.sleep(1)
        self.data_window.showMaximized()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    app.exec_()


if __name__ == "__main__":
    main()
