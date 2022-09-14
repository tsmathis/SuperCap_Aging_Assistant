import numpy as np
import matplotlib.pyplot as plt

from collections import Counter


def resample_time(time_series):
    """"""
    resampled_series = []
    counter = dict(sorted(Counter(time_series).items()))
    for num in counter:
        resampled_series.extend(np.linspace(start=num, stop=num + 1, num=counter[num]))
    return resampled_series


def calc_cap_IR_drop(df, mass, area):
    """"""
    cycles_to_process = df.query("CycleNo % 6 == 0").reset_index(drop=True)
    cycles_to_process["Fixed_time"] = resample_time(cycles_to_process["TestTime/Sec"])

    cycle_num = cycles_to_process["CycleNo"].unique()
    data_dict = {cycle: {} for cycle in cycle_num}

    for cycle in cycle_num:
        current_zero_val = (
            cycles_to_process.query("CycleNo == @cycle")["Current/mA"].iloc[0] / 1000
        )

        data_dict[cycle]["Charge_time"] = cycles_to_process.query(
            "CycleNo == @cycle & StepStatus == 'CCC'"
        )["Fixed_time"]
        data_dict[cycle]["Charge_voltage"] = cycles_to_process.query(
            "CycleNo == @cycle & StepStatus == 'CCC'"
        )["Voltage/V"]

        data_dict[cycle]["Discharge_time"] = cycles_to_process.query(
            "CycleNo == @cycle & StepStatus == 'CCD'"
        )["Fixed_time"]
        data_dict[cycle]["Discharge_voltage"] = cycles_to_process.query(
            "CycleNo == @cycle & StepStatus == 'CCD'"
        )["Voltage/V"]

        data_dict[cycle]["IR drop"] = (
            area
            * (
                data_dict[cycle]["Charge_voltage"].iloc[-1]
                - data_dict[cycle]["Discharge_voltage"].iloc[0]
            )
            / (current_zero_val)
        )

        charge_m, charge_b = np.polyfit(
            x=data_dict[cycle]["Charge_time"],
            y=data_dict[cycle]["Charge_voltage"],
            deg=1,
        )
        dis_m, dis_b = np.polyfit(
            x=data_dict[cycle]["Discharge_time"],
            y=data_dict[cycle]["Discharge_voltage"],
            deg=1,
        )

        data_dict[cycle]["Charge_slope/intercept"] = (charge_m, charge_b)
        data_dict[cycle]["Discharge_slope/intercept"] = (dis_m, dis_b)
        data_dict[cycle]["Charge_cap"] = 2 * (1 / charge_m) * current_zero_val
        data_dict[cycle]["Discharge_cap"] = (2 * (-1 / dis_m) * current_zero_val) / mass

    return data_dict


def plot_first_and_last_cycle(data_dict, num):
    keys = list(data_dict.keys())
    first, last = keys[0], keys[-1]

    charge_time_first = (
        data_dict[first]["Charge_time"] - data_dict[first]["Charge_time"].iloc[0]
    )
    discharge_time_first = (
        data_dict[first]["Discharge_time"] - data_dict[first]["Charge_time"].iloc[0]
    )
    charge_time_last = (
        data_dict[last]["Charge_time"] - data_dict[last]["Charge_time"].iloc[0]
    )
    discharge_time_last = (
        data_dict[last]["Discharge_time"] - data_dict[last]["Charge_time"].iloc[0]
    )

    plt.figure(num)
    plt.plot(
        charge_time_first,
        data_dict[first]["Charge_voltage"],
        "-o",
        color="tab:red",
        markevery=0.01,
        label="Before first aging cycle",
    )
    plt.plot(
        discharge_time_first,
        data_dict[first]["Discharge_voltage"],
        "-o",
        color="k",
        markevery=0.01,
    )
    plt.plot(
        charge_time_last,
        data_dict[last]["Charge_voltage"],
        "-o",
        color="tab:red",
        markevery=0.01,
        markerfacecolor="white",
        label="After aging",
    )
    plt.plot(
        discharge_time_last,
        data_dict[last]["Discharge_voltage"],
        "-o",
        color="k",
        markevery=0.01,
        markerfacecolor="white",
    )
    plt.xlabel("Time (s)")
    plt.ylabel("Potential (V)")
    plt.legend()


def calc_Qirr(df):

    floating_data = df.query("StepStatus == 'CVC'")
    cycles = floating_data["CycleNo"].unique()
    qirr_dict = {}

    for idx, cycle in enumerate(cycles):
        qirr_dict[idx + 1] = abs(
            np.trapz(
                y=floating_data.query("CycleNo == @cycle")["Current/mA"][::10],
                x=resample_time(
                    floating_data.query("CycleNo == @cycle")["TestTime/Sec"][::10]
                ),
            )
            / 3600
        )

    return qirr_dict


# need to get mean of last 100 pts of floating period (in uA)
def get_leakage_current(df):
    pass


def cap_decrease():
    pass


def resist_increase():
    pass


def plot_IR_drop_cap_fade(data, num):

    x = []
    y_IR = []
    y_cap = []
    for cycle in data:
        x.append(cycle / 6)
        y_IR.append(data[cycle]["IR drop"])
        y_cap.append(data[cycle]["Discharge_cap"])

    fig, ax = plt.subplots(num)
    fig.canvas.manager.set_window_title("Capacitance Fade/IR Drop")
    ax2 = ax.twinx()
    ax.plot(x, y_cap, "-o", color="tab:red")
    ax.spines["left"].set_color("tab:red")
    ax.tick_params(axis="y", colors="tab:red")
    ax.yaxis.label.set_color("tab:red")
    ax2.plot(x, y_IR, "-o", color="tab:blue", alpha=0.7)
    ax2.spines["right"].set_color("tab:blue")
    ax2.tick_params(axis="y", colors="tab:blue")
    ax2.yaxis.label.set_color("tab:blue")
    ax.set_xlabel("Aging Cycle #")
    ax.set_ylabel("Capacitance (F/g)")
    ax2.set_ylabel("IR Drop ($\Omega$.cm$^2$)", rotation=270, va="bottom")
    fig.tight_layout()
