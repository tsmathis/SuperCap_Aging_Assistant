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


# need to implement
def get_first_and_last_cycle(df):
    pass


def calc_cap_IR_drop(df, mass=0.0029, area=0.502):
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


def plot_data(data):
    fig1 = plt.figure("CCD curves")
    for cycle in data:
        m, b = data[cycle]["Discharge_slope/intercept"]
        m2, b2 = data[cycle]["Charge_slope/intercept"]
        plt.scatter(
            data[cycle]["Charge_time"],
            data[cycle]["Charge_voltage"],
            color="tab:orange",
            alpha=0.4,
        )
        plt.scatter(
            data[cycle]["Discharge_time"],
            data[cycle]["Discharge_voltage"],
            color="tab:blue",
            alpha=0.4,
        )
        plt.plot(
            data[cycle]["Discharge_time"],
            data[cycle]["Discharge_time"] * m + b,
            color="tab:red",
        )
        plt.plot(
            data[cycle]["Charge_time"],
            data[cycle]["Charge_time"] * m2 + b2,
            color="tab:red",
        )
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")

    fig2 = plt.figure("IR Drop")
    x_IR = []
    y_IR = []
    for cycle in data:
        x_IR.append(cycle / 6)
        y_IR.append(data[cycle]["IR drop"])

    plt.plot(x_IR, y_IR, "-o", color="tab:blue")
    plt.xlabel("Cycle #")
    plt.ylabel("IR Drop ($\Omega$)")

    fig3 = plt.figure("Capacitance")
    x = []
    y = []
    for cycle in data:
        x.append(cycle / 6)
        y.append(data[cycle]["Discharge_cap"])
    plt.plot(x, y, "-o", color="tab:red")
    plt.xlabel("Cycle #")
    plt.ylabel("Discharge_Capacitance (mF)")

    plt.show()
