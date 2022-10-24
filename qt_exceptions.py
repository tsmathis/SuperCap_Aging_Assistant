import sys, textwrap

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMessageBox


def show_exception_box(
    title,
    error_msg,
):
    """Checks if a QApplication instance is available and shows a messagebox with the specified error"""
    if QApplication.instance() is not None:
        errorbox = QMessageBox()
        errorbox.setWindowTitle(title)
        errorbox.setText(textwrap.dedent(error_msg))
        errorbox.setIcon(QMessageBox.Warning)
        errorbox.setStandardButtons(QMessageBox.Ok)
        button = errorbox.exec_()
        return


class UncaughtHook(QObject):
    _exception_caught = pyqtSignal(object, object)

    def __init__(self):
        super(UncaughtHook, self).__init__()

        # this registers the exception_hook() function as a hook with the Python interpreter
        sys.excepthook = self.exception_hook

        # connect signal to execute the message box function always on main thread
        self._exception_caught.connect(show_exception_box)

    def exception_hook(self, title, error_msg):
        """Function handling uncaught exceptions.
        It is triggered each time an uncaught exception occurs.
        """
        self._exception_caught.emit(title, error_msg)
