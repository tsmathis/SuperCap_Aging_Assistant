import pandas as pd
import matplotlib.pyplot as plt

from aging_methods import (
    calc_cap_IR_drop,
    calc_Qirr,
    plot_IR_drop_cap_fade,
    plot_first_and_last_cycle,
)
from cvs import cv_cap_current_density
from eis import calc_eis_cap, plot_caps_vs_freq, plot_img_cap_vs_freq

aging_data = pd.read_csv(r"test_data\4-19-04-oYP-29-138-ACN-Et4NBF4(2)220506_003_6.csv")
# cvs
five_before = pd.read_table(
    r"test_data\cvs_before_aging\19-04-22-SW2elec-9mm-oYP50F-S1-29x2-124 et 139µm -ACN 15M Et4NBF4_02_CV_C02.txt"
)
five_after = pd.read_table(
    r"test_data\cvs_after_aging\apV19-04-22-9mm-oYP50F-S1-29x2-124 139µm -ACN Et4NBF4_02_CV_C02.txt"
)
p_5_before = pd.read_table(
    r"test_data\cvs_before_aging\19-04-22-SW2elec-9mm-oYP50F-S1-29x2-124 et 139µm -ACN 15M Et4NBF4_03_CV_C02.txt"
)
p_5_after = pd.read_table(
    r"test_data\cvs_after_aging\apV19-04-22-9mm-oYP50F-S1-29x2-124 139µm -ACN Et4NBF4_03_CV_C02.txt"
)
# eis
ocv_before = pd.read_table(
    r"test_data\eis_before_aging\19-04-22-SW2elec-9mm-oYP50F-S1-29x2-124 et 139µm -ACN 15M Et4NBF4_04_PEIS_C02.txt"
)
p_5_volt_eis_before = pd.read_table(
    r"test_data\eis_before_aging\19-04-22-SW2elec-9mm-oYP50F-S1-29x2-124 et 139µm -ACN 15M Et4NBF4_06_PEIS_C02.txt"
)
one_volt_eis_before = pd.read_table(
    r"test_data\eis_before_aging\19-04-22-SW2elec-9mm-oYP50F-S1-29x2-124 et 139µm -ACN 15M Et4NBF4_08_PEIS_C02.txt"
)

ocv_after = pd.read_table(
    r"test_data\eis_after_aging\apV19-04-22-9mm-oYP50F-S1-29x2-124 139µm -ACN Et4NBF4_04_PEIS_C02.txt"
)
p_5_volt_eis_after = pd.read_table(
    r"test_data\eis_after_aging\apV19-04-22-9mm-oYP50F-S1-29x2-124 139µm -ACN Et4NBF4_06_PEIS_C02.txt"
)
one_volt_eis_after = pd.read_table(
    r"test_data\eis_after_aging\apV19-04-22-9mm-oYP50F-S1-29x2-124 139µm -ACN Et4NBF4_08_PEIS_C02.txt"
)

cvs_before = [five_before, p_5_before]
cvs_after = [five_after, p_5_after]
rates = [5, 0.5]
cvs_labels_b = ["5 mV/s before aging", "0.5 mV/s before aging"]
cvs_labels_a = ["5 mV/s after aging", "0.5 mV/s after aging"]

eis_before = [ocv_before, p_5_volt_eis_before, one_volt_eis_before]
eis_after = [ocv_after, p_5_volt_eis_after, one_volt_eis_after]

eis_labels_before = ["OCV before aging", "0.5V before aging", "1V before aging"]
eis_labels_after = ["OCV after aging", "0.5V after aging", "1V after aging"]


def main():
    idx = 1
    area = 0.502
    mass = 0.0029

    age = calc_cap_IR_drop(aging_data, mass=0.0029, area=0.502)
    plot_IR_drop_cap_fade(age, num=idx)
    idx += 1

    plot_first_and_last_cycle(age, num=idx)
    idx += 1

    for cv_b, cv_a, rate, label_b, label_a in zip(
        cvs_before, cvs_after, rates, cvs_labels_b, cvs_labels_a
    ):
        p_b, cap_b, density_b = cv_cap_current_density(cv_b, rate=rate, mass=mass)
        p_a, cap_a, density_a = cv_cap_current_density(cv_a, rate=rate, mass=mass)
        plt.figure(idx)
        plt.plot(p_b, cap_b, label=label_b)
        plt.plot(p_a, cap_a, label=label_a)
        plt.xlabel("Potential (V)")
        plt.ylabel("Capacitance (F/g)")
        plt.legend()
        idx += 1

    idx += 2

    for eis_b, eis_a, label_b, label_a in zip(
        eis_before, eis_after, eis_labels_before, eis_labels_after
    ):
        calc_eis_cap(eis_b)
        calc_eis_cap(eis_a)
        plot_caps_vs_freq(eis_b, num=idx, area=0.502, label=label_b)
        plot_caps_vs_freq(eis_a, num=idx, area=0.502, label=label_a, color="k")
        idx += 1

    for eis_b, label_b in zip(eis_before, eis_labels_before):
        plot_img_cap_vs_freq(eis_b, num=idx, area=0.502, label=label_b)
    idx += 1

    for eis_a, label_a in zip(eis_after, eis_labels_after):
        plot_img_cap_vs_freq(eis_a, num=idx, area=0.502, label=label_a)
    idx += 1

    plt.show()


if __name__ == "__main__":
    main()
