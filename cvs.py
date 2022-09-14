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
