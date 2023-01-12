from aging_methods import AgingData
from eis import Eis
from cvs import CVs


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


def calc_cv_data(file_list, mass):
    rates = [5, 0.5]
    cv_data = {}
    for idx, cv in enumerate(file_list):
        if len(cv) == 0:
            continue
        cv_data[rates[idx]] = CVs(rate=rates[idx], mass=mass)
        cv_data[rates[idx]].read_prep_data(cv)
        cv_data[rates[idx]].calc_capacitance()
        cv_data[rates[idx]].prep_export()
    return cv_data


def calc_eis_data(file_list, area):
    labels = ["OCV", "0.5 V", "1.0 V"]
    eis_data = {}
    for idx, eis in enumerate(file_list):
        if len(eis) == 0:
            continue
        eis_data[labels[idx]] = Eis(area=area)
        eis_data[labels[idx]].read_data(eis)
        eis_data[labels[idx]].calc_eis_cap()
        eis_data[labels[idx]].prep_export()
    return eis_data


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

    mass = float(mass_entry)
    area = float(area_entry)

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

    aging_data = calc_aging_data(file=aging_file, mass=mass, area=area)
    cvs_before = calc_cv_data(file_list=cvs_before_files, mass=mass)
    cvs_after = calc_cv_data(file_list=cvs_after_files, mass=mass)
    eis_before = calc_eis_data(file_list=eis_before_files, area=area)
    eis_after = calc_eis_data(file_list=eis_after_files, area=area)

    return aging_data, cvs_before, cvs_after, eis_before, eis_after
