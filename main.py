import sys, os, subprocess
import textwrap
from collections import deque

from aging_methods import AgingData
from eis import Eis
from cvs import CVs
from data_export import export_data

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QApplication,
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
    QMessageBox,
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

    def __init__(self, idx=None, parent=None):
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
    def __init__(self, aging_data, cvs_before, cvs_after, eis_before, eis_after):
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

        window_queue = deque(maxlen=12)

        for i in range(12):
            fig = MplCanvas()
            fig_toolbar = NavigationToolbar(fig, self)
            window = QWidget()
            window_layout = QVBoxLayout()
            window.setLayout(window_layout)
            window_layout.addWidget(fig_toolbar)
            window_layout.addWidget(fig)
            self.stacklayout.addWidget(window)
            window_queue.append(fig)

        widget_slot_queue = deque(maxlen=12)

        for i in range(12):
            button = ClickableWidget(idx=i)
            button.clicked.connect(self.change_activate_view)
            button.setMaximumSize(150, 150)
            button.setMinimumSize(50, 50)
            if i % 2 == 0:
                button_layout.addWidget(button, int(i / 2), 0, 1, 1)
            else:
                button_layout.addWidget(button, int(i / 2), 1, 1, 1)
            widget_slot_queue.append(button)

        export = QPushButton("Export Data")
        export.setStyleSheet("background-color: #007AFF")
        export.clicked.connect(self.get_export_location)
        button_layout.addWidget(export, 7, 0, 1, 2)

        pagelayout.addWidget(stack)
        pagelayout.addWidget(buttons)

        if aging_data:
            btn = widget_slot_queue.popleft()
            aging_data.plot_IR_drop_cap_fade_vs_cycle(axis=btn.axes)
            fig = window_queue.popleft()
            aging_data.plot_IR_drop_cap_fade_vs_cycle(axis=fig.axes)

            btn2 = widget_slot_queue.popleft()
            aging_data.plot_IR_drop_cap_fade_vs_qirr(axis=btn2.axes)
            fig2 = window_queue.popleft()
            aging_data.plot_IR_drop_cap_fade_vs_qirr(axis=fig2.axes)

            btn3 = widget_slot_queue.popleft()
            aging_data.plot_first_and_last_cycle(axis=btn3.axes)
            fig3 = window_queue.popleft()
            aging_data.plot_first_and_last_cycle(axis=fig3.axes, legend=1)

        if cvs_before and cvs_after:
            for keyb, keya in zip(cvs_before, cvs_after):
                btn = widget_slot_queue.popleft()
                cvs_before[keyb].plot_cv_cap_current_density(axis=btn.axes)
                cvs_after[keya].plot_cv_cap_current_density(axis=btn.axes)

                fig = window_queue.popleft()
                cvs_before[keyb].plot_cv_cap_current_density(
                    label="before aging", axis=fig.axes
                )
                cvs_after[keya].plot_cv_cap_current_density(
                    label="after aging", axis=fig.axes
                )

        if eis_before and eis_after:
            labels = ["OCV", "0.5 V", "1.0 V"]
            for keyb, keya, label in zip(eis_before, eis_after, labels):
                btn = widget_slot_queue.popleft()
                eis_before[keyb].plot_caps_vs_freq(axis=btn.axes)
                eis_after[keya].plot_caps_vs_freq(axis=btn.axes, color="k")

                fig = window_queue.popleft()
                eis_before[keyb].plot_caps_vs_freq(
                    label=f"{label} before aging", axis=fig.axes
                )
                eis_after[keya].plot_caps_vs_freq(
                    label=f"{label} after aging", color="k", axis=fig.axes
                )

        if eis_before:
            btn = widget_slot_queue.popleft()
            fig = window_queue.popleft()

            for key, label in zip(eis_before, labels):
                eis_before[key].nyquist_plots(figure=btn.fig, axis=btn.axes)
                eis_before[key].nyquist_plots(
                    label=f"{label} before aging", figure=fig.fig, axis=fig.axes
                )

            btn = widget_slot_queue.popleft()
            fig = window_queue.popleft()

            for key, label in zip(eis_before, labels):
                eis_before[key].plot_img_cap_vs_real_Z(axis=btn.axes)
                eis_before[key].plot_img_cap_vs_real_Z(
                    label=f"{label} before aging", axis=fig.axes
                )

        if eis_after:
            btn = widget_slot_queue.popleft()
            fig = window_queue.popleft()

            for key, label in zip(eis_after, labels):
                eis_after[key].nyquist_plots(figure=btn.fig, axis=btn.axes)
                eis_after[key].nyquist_plots(
                    label=f"{label} after aging", figure=fig.fig, axis=fig.axes
                )

            btn = widget_slot_queue.popleft()
            fig = window_queue.popleft()

            for key, label in zip(eis_after, labels):
                eis_after[key].plot_img_cap_vs_real_Z(axis=btn.axes)
                eis_after[key].plot_img_cap_vs_real_Z(
                    label=f"{label} after aging", axis=fig.axes
                )

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    def change_activate_view(self, clicked):
        self.stacklayout.setCurrentIndex(clicked)

    #  need to implement fully
    def get_export_location(self):
        dialog = QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "", directory="")
        if not folder_path:
            return
        if folder_path:
            if os.path.exists(folder_path + "/"):
                write_confirmed = QMessageBox.question(
                    self,
                    "Overwrite file?",
                    (
                        textwrap.dedent(
                            f"""\
                                The files:  already exist.
                                Are you sure you want to overwrite them?"""
                        )
                    ),
                )
                if write_confirmed == QMessageBox.No:
                    return
            else:
                write_confirmed = True

        if write_confirmed:
            export_data(destination=folder_path + "/")


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

    def calc_aging_data(self, file, mass, area):
        if len(file) == 0:
            return None
        aging = AgingData(mass=mass, area=area)
        aging.read_data(file)
        aging.calc_cap_IR_drop()
        aging.calc_Qirr()
        return aging

    def calc_cv_data_before_aging(self, file_list, mass):
        rates = [5, 0.5]
        cvs_before = {}
        for idx, cv in enumerate(file_list):
            if len(cv) == 0:
                continue
            cvs_before[rates[idx]] = CVs(rate=rates[idx], mass=mass)
            cvs_before[rates[idx]].read_data(cv)
        return cvs_before

    def calc_cv_data_after_aging(self, file_list, mass):
        rates = [5, 0.5]
        cvs_after = {}
        for idx, cv in enumerate(file_list):
            if len(cv) == 0:
                continue
            cvs_after[rates[idx]] = CVs(rate=rates[idx], mass=mass)
            cvs_after[rates[idx]].read_data(cv)
        return cvs_after

    def calc_eis_data_before_aging(self, file_list, area):
        labels = ["OCV", "0.5 V", "1.0 V"]
        eis_before = {}
        for idx, eis in enumerate(file_list):
            if len(eis) == 0:
                continue
            eis_before[labels[idx]] = Eis(area=area)
            eis_before[labels[idx]].read_data(eis)
            eis_before[labels[idx]].calc_eis_cap()
        return eis_before

    def calc_eis_data_after_aging(self, file_list, area):
        labels = ["OCV", "0.5 V", "1.0 V"]
        eis_after = {}
        for idx, eis in enumerate(file_list):
            if len(eis) == 0:
                continue
            eis_after[labels[idx]] = Eis(area=area)
            eis_after[labels[idx]].read_data(eis)
            eis_after[labels[idx]].calc_eis_cap()
        return eis_after

    def show_data_window(self):
        mass = float(self.mass_entry.text())
        area = float(self.area_entry.text())

        aging_file = self.aging_data_display.text()

        cvs_before_files = [
            self.cvs_five_before_display.text(),
            self.cvs_p_5_before_display.text(),
        ]
        cvs_after_files = [
            self.cvs_five_after_display.text(),
            self.cvs_p_5_after_display.text(),
        ]

        eis_before_files = [
            self.eis_ocv_before_display.text(),
            self.eis_p_5V_before_display.text(),
            self.eis_one_V_before_display.text(),
        ]
        eis_after_files = [
            self.eis_ocv_after_display.text(),
            self.eis_p_5V_after_display.text(),
            self.eis_one_V_after_display.text(),
        ]

        self.data_window = SecondWindow(
            aging_data=self.calc_aging_data(file=aging_file, mass=mass, area=area),
            cvs_before=self.calc_cv_data_before_aging(
                file_list=cvs_before_files, mass=mass
            ),
            cvs_after=self.calc_cv_data_after_aging(
                file_list=cvs_after_files, mass=mass
            ),
            eis_before=self.calc_eis_data_before_aging(
                file_list=eis_before_files, area=area
            ),
            eis_after=self.calc_eis_data_after_aging(
                file_list=eis_after_files, area=area
            ),
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
