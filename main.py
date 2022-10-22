import sys, os, textwrap

from aging_methods import AgingData
from eis import Eis
from cvs import CVs
from data_window_ui import DataWindow
from spinner_widget import QtWaitingSpinner

from PyQt5.QtCore import (
    Qt,
    QThreadPool,
    QRunnable,
    QMetaObject,
    pyqtSlot,
    Q_ARG,
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
    QMessageBox,
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


class Worker(QRunnable):
    def __init__(self, func, dialog):
        super(Worker, self).__init__()
        self.func = func
        self.w = dialog

    def run(self):
        self.func()
        QMetaObject.invokeMethod(
            self.w,
            "set_data",
            Qt.QueuedConnection,
            Q_ARG(object, self.w),
        )


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

    def calc_aging_data(self, file, mass, area):
        if len(file) == 0:
            return None
        aging = AgingData(mass=mass, area=area)
        aging.read_data(file)
        aging.calc_cap_IR_drop()
        aging.calc_Qirr()
        aging.get_leakage_current()
        aging.get_cap_decrease()
        aging.get_resist_increase()
        return aging

    def calc_cv_data_before_aging(self, file_list, mass):
        rates = [5, 0.5]
        cvs_before = {}
        for idx, cv in enumerate(file_list):
            if len(cv) == 0:
                continue
            cvs_before[rates[idx]] = CVs(rate=rates[idx], mass=mass)
            cvs_before[rates[idx]].read_prep_data(cv)
            cvs_before[rates[idx]].calc_capacitance()
            cvs_before[rates[idx]].prep_export()
        return cvs_before

    def calc_cv_data_after_aging(self, file_list, mass):
        rates = [5, 0.5]
        cvs_after = {}
        for idx, cv in enumerate(file_list):
            if len(cv) == 0:
                continue
            cvs_after[rates[idx]] = CVs(rate=rates[idx], mass=mass)
            cvs_after[rates[idx]].read_prep_data(cv)
            cvs_after[rates[idx]].calc_capacitance()
            cvs_after[rates[idx]].prep_export()
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
            eis_before[labels[idx]].prep_export()
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
            eis_after[labels[idx]].prep_export()
        return eis_after

    def process_data(self):
        try:
            mass = float(self.mass_entry.text())
        except ValueError:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("No mass input")
            dlg.setText(
                textwrap.dedent(
                    """\
                    Please enter a value for the electrode mass (in g).
                    """
                )
            )
            dlg.setIcon(QMessageBox.Warning)
            dlg.setStandardButtons(QMessageBox.Ok)
            button = dlg.exec_()
            return
        try:
            area = float(self.area_entry.text())
        except ValueError:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("No area input")
            dlg.setText(
                textwrap.dedent(
                    """\
                    Please enter a value for the electrode area (in cm<sup>2</sup>).
                    """
                )
            )
            dlg.setIcon(QMessageBox.Warning)
            dlg.setStandardButtons(QMessageBox.Ok)
            button = dlg.exec_()
            return

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

        try:
            self.aging_data = self.calc_aging_data(
                file=aging_file, mass=mass, area=area
            )
        except KeyError:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("File Error for Aging Data")
            dlg.setText(
                textwrap.dedent(
                    """\
                    The file loaded for "Aging Data" does not contain the correct data headers.
                    Check to ensure the file is correct.
                    """
                )
            )
            dlg.setIcon(QMessageBox.Warning)
            dlg.setStandardButtons(QMessageBox.Ok)
            button = dlg.exec_()
            return

        try:
            self.cvs_before = self.calc_cv_data_before_aging(
                file_list=cvs_before_files, mass=mass
            )
        except KeyError:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("File Error for CVs Before Aging Data")
            dlg.setText(
                textwrap.dedent(
                    """\
                    One, or both, files loaded for "CVs Before Aging" does not contain the correct data headers.
                    Check to ensure the files are correct.
                    """
                )
            )
            dlg.setIcon(QMessageBox.Warning)
            dlg.setStandardButtons(QMessageBox.Ok)
            button = dlg.exec_()
            return

        try:
            self.cvs_after = self.calc_cv_data_after_aging(
                file_list=cvs_after_files, mass=mass
            )
        except KeyError:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("File Error for CVs After Aging Data")
            dlg.setText(
                textwrap.dedent(
                    """\
                    One, or both, files loaded for "CVs After Aging" does not contain the correct data headers.
                    Check to ensure the files are correct.
                    """
                )
            )
            dlg.setIcon(QMessageBox.Warning)
            dlg.setStandardButtons(QMessageBox.Ok)
            button = dlg.exec_()
            return

        try:
            self.eis_before = self.calc_eis_data_before_aging(
                file_list=eis_before_files, area=area
            )
        except KeyError:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("File Error for EIS Before Aging Data")
            dlg.setText(
                textwrap.dedent(
                    """\
                    One, or multiple, files loaded for "EIS Before Aging" does not contain the correct data headers.
                    Check to ensure the files are correct.
                    """
                )
            )
            dlg.setIcon(QMessageBox.Warning)
            dlg.setStandardButtons(QMessageBox.Ok)
            button = dlg.exec_()
            return

        try:
            self.eis_after = self.calc_eis_data_after_aging(
                file_list=eis_after_files, area=area
            )
        except KeyError:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("File Error for EIS After Aging Data")
            dlg.setText(
                textwrap.dedent(
                    """\
                    One, or multiple, files loaded for "EIS After Aging" does not contain the correct data headers.
                    Check to ensure the files are correct.
                    """
                )
            )
            dlg.setIcon(QMessageBox.Warning)
            dlg.setStandardButtons(QMessageBox.Ok)
            button = dlg.exec_()
            return

        try:
            if (
                not self.aging_data
                and not self.cvs_before
                and not self.cvs_after
                and not self.eis_before
                and not self.eis_after
            ):
                raise Exception
        except Exception:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("No files loaded!")
            dlg.setText(
                textwrap.dedent(
                    """\
                    No files were input for processing.
                    At least one of the sections for "Aging Data", "CVs",
                    or "EIS" must be filled in to continue. 
                    """
                )
            )
            dlg.setIcon(QMessageBox.Warning)
            dlg.setStandardButtons(QMessageBox.Ok)
            button = dlg.exec_()
            return

    def show_data_window(self):
        self.spinner.start()
        worker = Worker(func=self.process_data, dialog=self)
        QThreadPool.globalInstance().start(worker)

    @pyqtSlot(object)
    def set_data(self, window):
        self.data_window = DataWindow(
            aging_data=window.aging_data,
            cvs_before=window.cvs_before,
            cvs_after=window.cvs_after,
            eis_before=window.eis_before,
            eis_after=window.eis_after,
        )
        self.data_window.showMaximized()
        self.close()
        self.spinner.stop()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(os.path.join(basedir, "supercap_aging.ico")))

    window = FileWindow()
    window.show()

    app.exec_()


if __name__ == "__main__":
    main()
