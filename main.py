import sys, os, subprocess
import matplotlib
import time
import numpy as np

from aging_methods import AgingData
from eis import Eis
from cvs import CVs

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

if hasattr(Qt, "AA_EnableHighDpiScaling"):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, "AA_UseHighDpiPixmaps"):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


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
    def __init__(
        self, aging_data, cvs_before, cvs_after, eis_before, eis_after, mass, area
    ):
        super().__init__()
        self.setWindowTitle("SuperCap Aging")
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

        export = QPushButton("Export Data")
        export.setStyleSheet("background-color: #007AFF")
        button_layout.addWidget(export, 6, 0, 1, 2)

        pagelayout.addWidget(stack)
        pagelayout.addWidget(buttons)

        idx = 0

        if aging_data:
            aging = AgingData(mass=mass, area=area)
            aging.read_data(aging_data)
            aging.calc_cap_IR_drop()
            aging.calc_Qirr()

            btn = ClickableWidget(idx=idx)
            aging.plot_IR_drop_cap_fade_vs_cycle(axis=btn.axes)
            btn.setMaximumSize(150, 150)
            btn.clicked.connect(self.change_activate_view)
            button_layout.addWidget(btn, 0, 0, 1, 1)

            fig = MplCanvas()
            fig_toolbar = NavigationToolbar(fig, self)
            aging.plot_IR_drop_cap_fade_vs_cycle(axis=fig.axes)
            window = QWidget()
            window_layout = QVBoxLayout()
            window.setLayout(window_layout)
            window_layout.addWidget(fig_toolbar)
            window_layout.addWidget(fig)
            self.stacklayout.addWidget(window)

            idx += 1

            btn2 = ClickableWidget(idx=idx)
            aging.plot_IR_drop_cap_fade_vs_qirr(axis=btn2.axes)
            btn2.setMaximumSize(150, 150)
            btn2.clicked.connect(self.change_activate_view)
            button_layout.addWidget(btn2, 0, 1, 1, 1)

            fig2 = MplCanvas()
            fig_toolbar = NavigationToolbar(fig2, self)
            aging.plot_IR_drop_cap_fade_vs_qirr(axis=fig2.axes)
            window2 = QWidget()
            window_layout = QVBoxLayout()
            window2.setLayout(window_layout)
            window_layout.addWidget(fig_toolbar)
            window_layout.addWidget(fig2)
            self.stacklayout.addWidget(window2)

            idx += 1

            btn3 = ClickableWidget(idx=idx)
            aging.plot_first_and_last_cycle(axis=btn3.axes)
            btn3.setMaximumSize(150, 150)
            btn3.clicked.connect(self.change_activate_view)
            button_layout.addWidget(btn3, 1, 0, 1, 1)

            fig3 = MplCanvas()
            fig_toolbar = NavigationToolbar(fig3, self)
            aging.plot_first_and_last_cycle(axis=fig3.axes)
            window2 = QWidget()
            window_layout = QVBoxLayout()
            window2.setLayout(window_layout)
            window_layout.addWidget(fig_toolbar)
            window_layout.addWidget(fig3)
            self.stacklayout.addWidget(window2)

            idx += 1

        # if cvs:
        #     for c in cvs:
        #         pass

        labels = ["OCV", "0.5 V", "1.0 V"]
        # btn = ClickableWidget(idx=idx)
        # eis.nyquist_plots(figure=btn.fig, axis=btn.axes)
        # btn.setMaximumSize(150, 150)
        # btn.clicked.connect(self.change_activate_view)
        # button_layout.addWidget(btn, 0, 0, 1, 1)

        # fig = MplCanvas()
        # fig_toolbar = NavigationToolbar(fig, self)
        # eis.nyquist_plots(label="OCV", figure=fig.fig, axis=fig.axes)
        # window = QWidget()
        # window_layout = QVBoxLayout()
        # window.setLayout(window_layout)
        # window_layout.addWidget(fig_toolbar)
        # window_layout.addWidget(fig)
        # self.stacklayout.addWidget(window)

        # idx += 1

        # btn2 = ClickableWidget(idx=idx)
        # eis1.plot_img_cap_vs_real_Z(axis=btn2.axes)
        # btn2.setMaximumSize(150, 150)
        # btn2.clicked.connect(self.change_activate_view)
        # button_layout.addWidget(btn2, 1, 0, 1, 1)

        # fig2 = MplCanvas()
        # fig_toolbar = NavigationToolbar(fig2, self)
        # eis.plot_img_cap_vs_real_Z(label="OCV", axis=fig2.axes)
        # window = QWidget()
        # window_layout = QVBoxLayout()
        # window.setLayout(window_layout)
        # window_layout.addWidget(fig_toolbar)
        # window_layout.addWidget(fig2)
        # self.stacklayout.addWidget(window)
        pairs = [(1, 1), (2, 0), (2, 1)]

        for i, j, label, pair in zip(eis_before, eis_after, labels, pairs):
            eis1 = Eis(area=area)
            eis1.read_data(i)
            eis1.calc_eis_cap()

            eis2 = Eis(area=area)
            eis2.read_data(j)
            eis2.calc_eis_cap()

            btn = ClickableWidget(idx=idx)
            eis1.plot_caps_vs_freq(axis=btn.axes)
            eis2.plot_caps_vs_freq(axis=btn.axes, color="k")
            btn.setMaximumSize(150, 150)
            btn.clicked.connect(self.change_activate_view)
            button_layout.addWidget(btn, pair[0], pair[1], 1, 1)

            fig = MplCanvas()
            fig_toolbar = NavigationToolbar(fig, self)
            eis1.plot_caps_vs_freq(label=f"{label} before aging", axis=fig.axes)
            eis2.plot_caps_vs_freq(
                label=f"{label} after aging", color="k", axis=fig.axes
            )
            window = QWidget()
            window_layout = QVBoxLayout()
            window.setLayout(window_layout)
            window_layout.addWidget(fig_toolbar)
            window_layout.addWidget(fig)
            self.stacklayout.addWidget(window)
            idx += 1

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    def change_activate_view(self, clicked):
        self.stacklayout.setCurrentIndex(clicked)


class MainWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Data Import")
        self.setMaximumWidth(1200)
        self.page_layout = QVBoxLayout()

        entry_boxes = QWidget()
        entry_layout = QFormLayout()
        entry_boxes.setLayout(entry_layout)

        self.mass_entry = QLineEdit()
        self.area_entry = QLineEdit()
        entry_layout.addRow("Enter electrode mass (g):", self.mass_entry)
        entry_layout.addRow("Enter electrode area (cm<sup>2</sup>):", self.area_entry)

        self.mass_entry.setFixedWidth(70)
        self.area_entry.setFixedWidth(70)
        entry_boxes.setFixedHeight(75)
        self.page_layout.addWidget(entry_boxes)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setLineWidth(3)
        self.page_layout.addWidget(div)

        aging_data = QWidget()
        aging_data.setMaximumWidth(600)
        aging_layout = QGridLayout()
        aging_data.setLayout(aging_layout)

        aging_data_label = QLabel("Aging Data:")
        self.aging_data_display = QLineEdit()
        self.aging_data_display.setMinimumWidth(200)
        self.aging_data_display.setReadOnly(True)
        aging_files_input = QPushButton("...")
        aging_files_input.clicked.connect(
            lambda: self.get_csv_files(self.aging_data_display)
        )

        aging_layout.addWidget(aging_data_label, 0, 0, 1, 1)
        aging_layout.addWidget(self.aging_data_display, 0, 1, 1, 1)
        aging_layout.addWidget(aging_files_input, 0, 2, 1, 1)
        aging_data.setFixedHeight(50)
        self.page_layout.addWidget(aging_data)

        div2 = QFrame()
        div2.setFrameShape(QFrame.HLine)
        div2.setLineWidth(3)
        self.page_layout.addWidget(div2)

        cvs = QWidget()
        cvs.setFixedHeight(100)
        cvs_layout = QHBoxLayout()
        cvs.setLayout(cvs_layout)

        cvs_before = QGridLayout()
        cvs_label_before = QLabel("CVs Before Aging:")

        cvs_five_before = QLabel("5 mV/s:")
        self.cvs_five_before_display = QLineEdit()
        self.cvs_five_before_display.setMinimumWidth(200)
        self.cvs_five_before_display.setReadOnly(True)
        cvs_five_before_input = QPushButton("...")
        cvs_five_before_input.clicked.connect(
            lambda: self.get_txt_files(self.cvs_five_before_display)
        )

        cvs_p_5_before = QLabel("0.5 mV/s:")
        self.cvs_p_5_before_display = QLineEdit()
        self.cvs_p_5_before_display.setReadOnly(True)
        cvs_p_5_before_input = QPushButton("...")
        cvs_p_5_before_input.clicked.connect(
            lambda: self.get_txt_files(self.cvs_p_5_before_display)
        )

        cvs_before.addWidget(cvs_label_before, 0, 0, 1, 1)
        cvs_before.addWidget(cvs_five_before, 1, 0, 1, 1)
        cvs_before.addWidget(self.cvs_five_before_display, 1, 1, 1, 1)
        cvs_before.addWidget(cvs_five_before_input, 1, 2, 1, 1)
        cvs_before.addWidget(cvs_p_5_before, 2, 0, 1, 1)
        cvs_before.addWidget(self.cvs_p_5_before_display, 2, 1, 1, 1)
        cvs_before.addWidget(cvs_p_5_before_input, 2, 2, 1, 1)

        cvs_after = QGridLayout()
        cvs_label_after = QLabel("CVs After Aging:")

        cvs_five_after = QLabel("5 mV/s:")
        self.cvs_five_after_display = QLineEdit()
        self.cvs_five_after_display.setMinimumWidth(200)
        self.cvs_five_after_display.setReadOnly(True)
        cvs_five_after_input = QPushButton("...")
        cvs_five_after_input.clicked.connect(
            lambda: self.get_txt_files(self.cvs_five_after_display)
        )

        cvs_p_5_after = QLabel("0.5 mV/s:")
        self.cvs_p_5_after_display = QLineEdit()
        self.cvs_p_5_after_display.setReadOnly(True)
        cvs_p_5_after_input = QPushButton("...")
        cvs_p_5_after_input.clicked.connect(
            lambda: self.get_txt_files(self.cvs_p_5_after_display)
        )

        cvs_after.addWidget(cvs_label_after, 0, 0, 1, 1)
        cvs_after.addWidget(cvs_five_after, 1, 0, 1, 1)
        cvs_after.addWidget(self.cvs_five_after_display, 1, 1, 1, 1)
        cvs_after.addWidget(cvs_five_after_input, 1, 2, 1, 1)
        cvs_after.addWidget(cvs_p_5_after, 2, 0, 1, 1)
        cvs_after.addWidget(self.cvs_p_5_after_display, 2, 1, 1, 1)
        cvs_after.addWidget(cvs_p_5_after_input, 2, 2, 1, 1)

        cvs_layout.addLayout(cvs_before)
        cvs_layout.addLayout(cvs_after)
        self.page_layout.addWidget(cvs)

        div3 = QFrame()
        div3.setFrameShape(QFrame.HLine)
        div3.setLineWidth(3)
        self.page_layout.addWidget(div3)

        eis = QWidget()
        eis.setFixedHeight(130)
        eis_layout = QHBoxLayout()
        eis.setLayout(eis_layout)

        eis_before = QGridLayout()
        eis_label_before = QLabel("EIS Before Aging:")

        eis_ocv_before = QLabel("OCV EIS:")
        self.eis_ocv_before_display = QLineEdit()
        self.eis_ocv_before_display.setReadOnly(True)
        eis_ocv_before_input = QPushButton("...")
        eis_ocv_before_input.clicked.connect(
            lambda: self.get_txt_files(self.eis_ocv_before_display)
        )

        eis_p_5V_before = QLabel("0.5 V EIS:")
        self.eis_p_5V_before_display = QLineEdit()
        self.eis_p_5V_before_display.setReadOnly(True)
        eis_p_5V_before_input = QPushButton("...")
        eis_p_5V_before_input.clicked.connect(
            lambda: self.get_txt_files(self.eis_p_5V_before_display)
        )

        eis_one_V_before = QLabel("1 V EIS:")
        self.eis_one_V_before_display = QLineEdit()
        self.eis_one_V_before_display.setReadOnly(True)
        eis_one_V_before_input = QPushButton("...")
        eis_one_V_before_input.clicked.connect(
            lambda: self.get_txt_files(self.eis_one_V_before_display)
        )

        eis_before.addWidget(eis_label_before, 0, 0, 1, 1)
        eis_before.addWidget(eis_ocv_before, 1, 0, 1, 1)
        eis_before.addWidget(self.eis_ocv_before_display, 1, 1, 1, 1)
        eis_before.addWidget(eis_ocv_before_input, 1, 2, 1, 1)
        eis_before.addWidget(eis_p_5V_before, 2, 0, 1, 1)
        eis_before.addWidget(self.eis_p_5V_before_display, 2, 1, 1, 1)
        eis_before.addWidget(eis_p_5V_before_input, 2, 2, 1, 1)
        eis_before.addWidget(eis_one_V_before, 3, 0, 1, 1)
        eis_before.addWidget(self.eis_one_V_before_display, 3, 1, 1, 1)
        eis_before.addWidget(eis_one_V_before_input, 3, 2, 1, 1)

        eis_after = QGridLayout()
        eis_label_after = QLabel("EIS After Aging:")

        eis_ocv_after = QLabel("OCV EIS:")
        self.eis_ocv_after_display = QLineEdit()
        self.eis_ocv_after_display.setReadOnly(True)
        eis_ocv_after_input = QPushButton("...")
        eis_ocv_after_input.clicked.connect(
            lambda: self.get_txt_files(self.eis_ocv_after_display)
        )

        eis_p_5V_after = QLabel("0.5 V EIS:")
        self.eis_p_5V_after_display = QLineEdit()
        self.eis_p_5V_after_display.setReadOnly(True)
        eis_p_5V_after_input = QPushButton("...")
        eis_p_5V_after_input.clicked.connect(
            lambda: self.get_txt_files(self.eis_p_5V_after_display)
        )

        eis_one_V_after = QLabel("1 V EIS:")
        self.eis_one_V_after_display = QLineEdit()
        self.eis_one_V_after_display.setReadOnly(True)
        eis_one_V_after_input = QPushButton("...")
        eis_one_V_after_input.clicked.connect(
            lambda: self.get_txt_files(self.eis_one_V_after_display)
        )

        eis_after.addWidget(eis_label_after, 0, 0, 1, 1)
        eis_after.addWidget(eis_ocv_after, 1, 0, 1, 1)
        eis_after.addWidget(self.eis_ocv_after_display, 1, 1, 1, 1)
        eis_after.addWidget(eis_ocv_after_input, 1, 2, 1, 1)
        eis_after.addWidget(eis_p_5V_after, 2, 0, 1, 1)
        eis_after.addWidget(self.eis_p_5V_after_display, 2, 1, 1, 1)
        eis_after.addWidget(eis_p_5V_after_input, 2, 2, 1, 1)
        eis_after.addWidget(eis_one_V_after, 3, 0, 1, 1)
        eis_after.addWidget(self.eis_one_V_after_display, 3, 1, 1, 1)
        eis_after.addWidget(eis_one_V_after_input, 3, 2, 1, 1)

        eis_layout.addLayout(eis_before)
        eis_layout.addLayout(eis_after)
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

    def get_csv_files(self, widget):
        filters = "Comma Separated Values (*.csv)"
        filename, _ = QFileDialog.getOpenFileName(filter=filters)
        widget.setText(filename)

    def get_txt_files(self, widget):
        filters = "Text files (*.txt)"
        filename, _ = QFileDialog.getOpenFileName(filter=filters)
        widget.setText(filename)

    def show_data_window(self):
        aging_data = self.aging_data_display.text()
        cvs_before = [
            self.cvs_five_before_display.text(),
            self.cvs_p_5_before_display.text(),
        ]
        cvs_after = [
            self.cvs_five_after_display.text(),
            self.cvs_p_5_after_display.text(),
        ]
        eis_before = [
            self.eis_ocv_before_display.text(),
            self.eis_p_5V_before_display.text(),
            self.eis_one_V_before_display.text(),
        ]
        eis_after = [
            self.eis_ocv_after_display.text(),
            self.eis_p_5V_after_display.text(),
            self.eis_one_V_after_display.text(),
        ]

        self.data_window = SecondWindow(
            aging_data=aging_data,
            cvs_before=cvs_before,
            cvs_after=cvs_after,
            eis_before=eis_before,
            eis_after=eis_after,
            mass=float(self.mass_entry.text()),
            area=float(self.area_entry.text()),
        )

        self.close()
        self.data_window.showMaximized()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    app.exec_()


if __name__ == "__main__":
    main()
