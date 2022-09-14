import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def cv_cap_current_density(df, rate, mass):
    last_cycle = df["cycle number"].unique()[-1]
    potential = capacitance = df.query("`cycle number` == @last_cycle")["Ewe/V"]
    capacitance = df.query("`cycle number` == @last_cycle")["<I>/mA"] / (mass * rate)
    current_density = df.query("`cycle number` == @last_cycle")["<I>/mA"] / (mass)
    return potential, capacitance, current_density


def calc_capacitance(df, rate, mass):
    last_cycle = df["cycle number"].unique()[-1]


cv1 = pd.read_table(
    r"test_data\cvs_before_aging\19-04-22-SW2elec-9mm-oYP50F-S1-29x2-124 et 139µm -ACN 15M Et4NBF4_02_CV_C02.txt"
)
cv2 = pd.read_table(
    r"test_data\cvs_after_aging\apV19-04-22-9mm-oYP50F-S1-29x2-124 139µm -ACN Et4NBF4_02_CV_C02.txt"
)


p1, cap1, current1 = cv_cap_current_density(cv1, rate=5, mass=0.0029)
p2, cap2, current2 = cv_cap_current_density(cv2, rate=5, mass=0.0029)

plt.plot(p1, cap1)
plt.plot(p2, cap2)
plt.show()
