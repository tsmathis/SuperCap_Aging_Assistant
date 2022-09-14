import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def calc_eis_cap(df):
    df["C''"] = df["Re(Z)/Ohm"] / (df["freq/Hz"] * df["|Z|/Ohm"] ** 2)
    df["C'"] = df["-Im(Z)/Ohm"] / (df["freq/Hz"] * df["|Z|/Ohm"] ** 2)


def nyquist_plots(df, num, area):
    if not area:
        plt.figure(num)
        plt.plot(df["Re(Z)/Ohm"], df["-Im(Z)/Ohm"], "-o")


def plot_caps_vs_freq(df, num, area, label="", color="tab:red"):
    plt.figure(num)
    plt.plot(
        df["freq/Hz"],
        df["C'"] / area,
        marker="o",
        color=color,
        label=("C'' " + label),
    )
    plt.plot(
        df["freq/Hz"],
        df["C''"] / area,
        marker="s",
        color=color,
        markerfacecolor="white",
        label=("C' " + label),
    )
    plt.xscale("log")
    plt.xlabel("Freq. (Hz)")
    plt.ylabel("F/cm$^2$")
    plt.legend()


def plot_img_cap_vs_freq(df, num, area, label=""):
    plt.figure(num)
    plt.plot(df["Re(Z)/Ohm"], df["C''"] / area, "-o", label=label)
    plt.xlabel("Re(Z) ($\Omega$)")
    plt.ylabel("F/cm$^2$")
    plt.legend()
