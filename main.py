import sys, os

from data_processing_funcs import process_data
from data_window_ui import DataWindow
from spinner_widget import QtWaitingSpinner

from PyQt5.QtCore import (
    Qt,
    QThreadPool,
    QRunnable,
    QObject,
    pyqtSignal,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
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

basedir = os.path.dirname(__file__)

try:
    from ctypes import windll

    myappid = "supercap_aging.tylersmathis"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object, object, object, object, object)


class Worker(QRunnable):
    def __init__(self, dialog):
        super(Worker, self).__init__()
        self.signals = WorkerSignals()
        self.w = dialog

    def run(self):
        try:
            aging_data, cvs_before, cvs_after, eis_before, eis_after = process_data(
                mass_entry=self.w.mass_entry.text(),
                area_entry=self.w.area_entry.text(),
                aging_data_display=self.w.aging_data_display.text(),
                cvs_five_before_display=self.w.cvs_five_before_display.text(),
                cvs_p_5_before_display=self.w.cvs_p_5_before_display.text(),
                cvs_five_after_display=self.w.cvs_five_after_display.text(),
                cvs_p_5_after_display=self.w.cvs_p_5_after_display.text(),
                eis_ocv_before_display=self.w.eis_ocv_before_display.text(),
                eis_p_5V_before_display=self.w.eis_p_5V_before_display.text(),
                eis_one_V_before_display=self.w.eis_one_V_before_display.text(),
                eis_ocv_after_display=self.w.eis_ocv_after_display.text(),
                eis_p_5V_after_display=self.w.eis_p_5V_after_display.text(),
                eis_one_V_after_display=self.w.eis_one_V_after_display.text(),
            )
        except:
            pass
        else:
            self.signals.result.emit(
                aging_data, cvs_before, cvs_after, eis_before, eis_after
            )
            self.signals.finished.emit()


class FileWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super(FileWindow, self).__init__(parent)

        self.setWindowTitle("SuperCap Aging: Data Import")
        self.setMaximumWidth(1200)
        self.page_layout = QVBoxLayout()

        self.spinner = QtWaitingSpinner(self, True, True, Qt.ApplicationModal)
        self.page_layout.addWidget(self.spinner)

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

        self.threadpool = QThreadPool()

    def get_csv_files(self, widget):
        filters = "Comma Separated Values (*.csv)"
        filename, _ = QFileDialog.getOpenFileName(
            filter=filters,
        )
        widget.setText(filename)

    def get_txt_files(self, widget):
        filters = "Text files (*.txt)"
        filename, _ = QFileDialog.getOpenFileName(
            filter=filters,
        )
        widget.setText(filename)

    def set_data(self, aging_data, cvs_before, cvs_after, eis_before, eis_after):
        self.data_window = DataWindow(
            aging_data=aging_data,
            cvs_before=cvs_before,
            cvs_after=cvs_after,
            eis_before=eis_before,
            eis_after=eis_after,
        )
        self.data_window.showMaximized()

    def finish_processing(self):
        self.close()
        self.spinner.stop()

    def show_data_window(self):
        self.spinner.start()
        worker = Worker(dialog=self)

        worker.signals.result.connect(self.set_data)
        worker.signals.finished.connect(self.finish_processing)
        self.threadpool.start(worker)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(os.path.join(basedir, "supercap_aging.ico")))

    window = FileWindow()
    window.show()

    app.exec_()


if __name__ == "__main__":
    main()
