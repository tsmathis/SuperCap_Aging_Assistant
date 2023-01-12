import sys, os, traceback, textwrap, inspect

from data_processing_funcs import process_data
from data_window_ui import DataWindow
from src.spinner_widget import QtWaitingSpinner

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
    QMessageBox,
    QFileDialog,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFormLayout,
    QStackedLayout,
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


def exception_handler(error, window_title):
    dlg = QMessageBox()
    dlg.setWindowTitle(window_title)
    dlg.setText(textwrap.dedent(error))
    dlg.setIcon(QMessageBox.Warning)
    dlg.setStandardButtons(QMessageBox.Ok)
    button = dlg.exec_()
    return


class EmptyFileIO(Exception):
    pass


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str, str)
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
            if (
                not aging_data
                and not cvs_before
                and not cvs_after
                and not eis_before
                and not eis_after
            ):
                raise EmptyFileIO

        except ValueError:
            err_msg = """
            Please ensure values are entered for both the electrode mass (in g) and the electrode area (in cm<sup>2</sup>)
            """
            self.signals.error.emit(err_msg, "Mass/Area Input Error")

        except IndexError:
            err_msg = """
            The "Aging Data" file did not contain the expected columns. Please double check that your data file contains the expected columns. 
            
            Consult the documentation to view the complete list of expected columns. 
            """
            self.signals.error.emit(err_msg, "File parsing error")

        except KeyError as exc:
            filename, lineno, funcname, text = traceback.extract_tb(exc.__traceback__)[
                2
            ]

            frames = inspect.trace()
            argvalues = inspect.getargvalues(frames[2][0])

            if "eis" in funcname:
                err = "EIS"
            elif "cv" in funcname:
                err = "cyclic voltammogram"
            elif "aging" in funcname:
                err = "aging"

            err_msg = f"""
            An error occurred when processing the {err} data using one of the following files:

            "{next(iter(argvalues[3].values()))}"

            The file was missing the following expected column: "{exc}"

            Please ensure the correct files are loaded in the {err} section. If this error persists, double check that your data files contain the columns you expect.
            """

            self.signals.error.emit(err_msg, "File Parsing Error")

        except EmptyFileIO:
            self.signals.error.emit("No files loaded", "Empty File Input")

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

        main_page = QWidget()
        main_page.setLayout(self.page_layout)

        stack = QWidget()
        self.stack_layout = QStackedLayout()
        self.stack_layout.setStackingMode(QStackedLayout.StackAll)
        stack.setLayout(self.stack_layout)

        self.stack_layout.addWidget(main_page)

        self.spinner = QtWaitingSpinner(self, True, True, Qt.ApplicationModal)
        self.stack_layout.addWidget(self.spinner)

        self.setCentralWidget(stack)
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

    def show_data_window(self):
        self.stack_layout.setCurrentIndex(1)
        self.spinner.start()
        worker = Worker(dialog=self)
        worker.signals.result.connect(self.set_data)
        worker.signals.finished.connect(self.finish_processing)
        worker.signals.error.connect(self.process_error)
        self.threadpool.start(worker)

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

    def process_error(self, error, title):
        self.spinner.stop()
        exception_handler(
            error=error,
            window_title=title,
        )


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(os.path.join(basedir, "supercap_aging.ico")))

    window = FileWindow()
    window.show()

    app.exec_()


if __name__ == "__main__":
    main()
