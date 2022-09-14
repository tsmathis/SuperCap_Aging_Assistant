import pandas as pd
import matplotlib.pyplot as plt

from aging_methods import calc_cap_IR_drop, calc_Qirr, plot_data
from eis import *


def main():

    # aging_data = pd.read_csv("4-19-04-oYP-29-138-ACN-Et4NBF4(2)220506_003_6.csv")
    eis = pd.read_table(
        r"E:\CIRIMAT_data\transfer_3833898_files_5c453f1e\av vieill\19-04-22-SW2elec-9mm-oYP50F-S1-29x2-124 et 139µm -ACN 15M Et4NBF4_06_PEIS_C02.txt"
    )
    # # data = calc_cap_IR_drop(aging_data)
    # # plot_data(data)

    # qirr = calc_Qirr(aging_data)

    # plt.scatter(*zip(*qirr.items()))

    # plt.show()

    calc_eis_cap(eis)
    nyquist_plots(eis, 1)
    plot_caps_vs_freq(eis, 2)
    plot_img_cap_vs_freq(eis, 3)

    plt.show()


if __name__ == "__main__":
    main()
