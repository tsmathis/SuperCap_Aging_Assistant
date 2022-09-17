import sys, os, subprocess
import matplotlib
import time
import numpy as np

from eis import Eis

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
from PyQt5.QtWidgets import (
    QApplication,
    QAction,
    QFileDialog,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QGridLayout,
    QFormLayout,
    QWidget,
    QFrame,
    QLineEdit,
)

test_eis = Eis(area=0.502)
test_eis.read_data(
    r"test_data\eis_before_aging\19-04-22-SW2elec-9mm-oYP50F-S1-29x2-124 et 139µm -ACN 15M Et4NBF4_04_PEIS_C02.txt"
)
test_eis.calc_eis_cap()


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig = Figure(dpi=150, constrained_layout=True)
        self.axes = self.fig.add_subplot()
        super().__init__(self.fig)


class ClickableWidget(MplCanvas):
    clicked = pyqtSignal(int)

    def __init__(self, idx, parent=None):
        self.fig = Figure(dpi=100)
        self.axes = self.fig.add_subplot()
        super().__init__(self.fig)
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)
        self.index = idx
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if isinstance(obj, MplCanvas) and event.type() == QEvent.MouseButtonPress:
            self.clicked.emit(self.index)
        return QWidget.eventFilter(self, obj, event)


class SecondWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        pagelayout = QHBoxLayout()
        button_layout = QGridLayout()
        self.stacklayout = QStackedLayout()

        buttons = QWidget()
        stack = QWidget()
        stack.setMinimumSize(400, 400)
        stack.setLayout(self.stacklayout)
        buttons.setLayout(button_layout)
        buttons.setFixedWidth(350)

        for i in range(6):
            row = QWidget()
            row.setMaximumSize(150, 150)
            row.setMinimumSize(50, 50)
            button_layout.addWidget(row, i, 1, 1, 1)

        pagelayout.addWidget(stack)
        pagelayout.addWidget(buttons)

        btn = ClickableWidget(idx=0)
        test_eis.nyquist_plots(figure=btn.fig, axis=btn.axes)
        btn.setMaximumSize(150, 150)
        btn.clicked.connect(self.change_activate_view)
        button_layout.addWidget(btn, 0, 0, 1, 1)

        fig = MplCanvas()
        fig_toolbar = NavigationToolbar(fig, self)
        test_eis.nyquist_plots(label="OCV", figure=fig.fig, axis=fig.axes)
        window = QWidget()
        window_layout = QVBoxLayout()
        window.setLayout(window_layout)
        window_layout.addWidget(fig_toolbar)
        window_layout.addWidget(fig)
        self.stacklayout.addWidget(window)

        btn2 = ClickableWidget(idx=1)
        test_eis.plot_caps_vs_freq(axis=btn2.axes)
        btn2.setMaximumSize(150, 150)
        btn2.clicked.connect(self.change_activate_view)
        button_layout.addWidget(btn2, 0, 1, 1, 1)

        fig2 = MplCanvas()
        fig_toolbar = NavigationToolbar(fig2, self)
        test_eis.plot_caps_vs_freq(label="OCV", axis=fig2.axes)
        window = QWidget()
        window_layout = QVBoxLayout()
        window.setLayout(window_layout)
        window_layout.addWidget(fig_toolbar)
        window_layout.addWidget(fig2)
        self.stacklayout.addWidget(window)

        btn3 = ClickableWidget(idx=2)
        test_eis.plot_img_cap_vs_real_Z(axis=btn3.axes)
        btn3.setMaximumSize(150, 150)
        btn3.clicked.connect(self.change_activate_view)
        button_layout.addWidget(btn3, 1, 0, 1, 1)

        fig3 = MplCanvas()
        fig_toolbar = NavigationToolbar(fig3, self)
        test_eis.plot_img_cap_vs_real_Z(label="OCV", axis=fig3.axes)
        window = QWidget()
        window_layout = QVBoxLayout()
        window.setLayout(window_layout)
        window_layout.addWidget(fig_toolbar)
        window_layout.addWidget(fig3)
        self.stacklayout.addWidget(window)

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    def change_activate_view(self, clicked):
        self.stacklayout.setCurrentIndex(clicked)


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
