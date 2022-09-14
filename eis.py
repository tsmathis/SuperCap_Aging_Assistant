import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def calc_eis_cap(df):
    df["C''"] = df["Re(Z)/Ohm"] / (df["freq/Hz"] * df["|Z|/Ohm"] ** 2)
    df["C'"] = df["-Im(Z)/Ohm"] / (df["freq/Hz"] * df["|Z|/Ohm"] ** 2)


def nyquist_plots(df, num, area=None):
    if not area:
        plt.figure(num)
        plt.plot(df["Re(Z)/Ohm"], df["-Im(Z)/Ohm"], "-o")


def plot_caps_vs_freq(df, num, area=None, label="", markers="o", color="tab:red"):
    if not area:
        plt.figure(num)
        plt.plot(
            df["freq/Hz"], df["C'"], marker=markers, color=color, label=("C'' " + label)
        )
        plt.plot(
            df["freq/Hz"],
            df["C''"],
            marker=markers,
            color=color,
            markerfacecolor="none",
            label=("C' " + label),
        )
        plt.legend()
        plt.xscale("log")


def plot_img_cap_vs_freq(df, num, area=None):
    if not area:
        plt.figure(num)
        plt.plot(df["Re(Z)/Ohm"], df["C''"], "-o")
