import pandas as pd
import matplotlib.pyplot as plt

from aging_methods import (
    calc_cap_IR_drop,
    calc_Qirr,
    plot_IR_drop_cap_fade,
    plot_first_and_last_cycle,
    get_leakage_current,
    cap_decrease,
    resist_increase,
)
from cvs import cv_cap_current_density
from eis import calc_eis_cap, plot_caps_vs_freq, plot_img_cap_vs_freq

aging_data = pd.read_csv(r"test_data\4-19-04-oYP-29-138-ACN-Et4NBF4(2)220506_003_6.csv")


def main():
    area = 0.502
    mass = 0.0029

    d = calc_cap_IR_drop(aging_data, mass, area)
    print(resist_increase(d))


if __name__ == "__main__":
    main()
