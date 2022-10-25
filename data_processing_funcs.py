import textwrap

from aging_methods import AgingData
from eis import Eis
from cvs import CVs

from PyQt5.QtWidgets import QMessageBox


def calc_aging_data(file, mass, area):
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


def calc_cv_data_before_aging(file_list, mass):
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


def calc_cv_data_after_aging(file_list, mass):
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


def calc_eis_data_before_aging(file_list, area):
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


def calc_eis_data_after_aging(file_list, area):
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


def process_data(
    mass_entry,
    area_entry,
    aging_data_display,
    cvs_five_before_display,
    cvs_p_5_before_display,
    cvs_five_after_display,
    cvs_p_5_after_display,
    eis_ocv_before_display,
    eis_p_5V_before_display,
    eis_one_V_before_display,
    eis_ocv_after_display,
    eis_p_5V_after_display,
    eis_one_V_after_display,
):
    try:
        mass = float(mass_entry)
    except ValueError:
        dlg = QMessageBox()
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
        area = float(area_entry)
    except ValueError:
        dlg = QMessageBox()
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

    aging_file = aging_data_display

    cvs_before_files = [
        cvs_five_before_display,
        cvs_p_5_before_display,
    ]
    cvs_after_files = [cvs_five_after_display, cvs_p_5_after_display]

    eis_before_files = [
        eis_ocv_before_display,
        eis_p_5V_before_display,
        eis_one_V_before_display,
    ]
    eis_after_files = [
        eis_ocv_after_display,
        eis_p_5V_after_display,
        eis_one_V_after_display,
    ]

    try:
        aging_data = calc_aging_data(file=aging_file, mass=mass, area=area)
    except KeyError:
        dlg = QMessageBox()
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
        cvs_before = calc_cv_data_before_aging(file_list=cvs_before_files, mass=mass)
    except KeyError:
        dlg = QMessageBox()
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
        cvs_after = calc_cv_data_after_aging(file_list=cvs_after_files, mass=mass)
    except KeyError:
        dlg = QMessageBox()
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
        eis_before = calc_eis_data_before_aging(file_list=eis_before_files, area=area)
    except KeyError:
        dlg = QMessageBox()
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
        eis_after = calc_eis_data_after_aging(file_list=eis_after_files, area=area)
    except KeyError:
        dlg = QMessageBox()
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
            not aging_data
            and not cvs_before
            and not cvs_after
            and not eis_before
            and not eis_after
        ):
            raise Exception
    except Exception:
        dlg = QMessageBox()
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

    return aging_data, cvs_before, cvs_after, eis_before, eis_after
