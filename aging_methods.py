import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from collections import Counter
from itertools import accumulate


class AgingData:
    def __init__(self, mass, area) -> None:
        self.mass = mass
        self.area = area

    def read_data(self, file_name):
        self.df = pd.read_csv(file_name)

    def resample_time(self, time_series):
        """"""
        resampled_series = []
        counter = dict(sorted(Counter(time_series).items()))
        for num in counter:
            resampled_series.extend(
                np.linspace(start=num, stop=num + 1, num=counter[num])
            )
        return resampled_series

    def calc_cap_IR_drop(self):
        """"""
        cycles_to_process = self.df.query("CycleNo % 6 == 0").reset_index(drop=True)
        cycles_to_process["Fixed_time"] = self.resample_time(
            cycles_to_process["TestTime/Sec"]
        )

        cycle_num = cycles_to_process["CycleNo"].unique()
        self.data_dict = {cycle: {} for cycle in cycle_num}

        for cycle in cycle_num:
            current_zero_val = (
                cycles_to_process.query("CycleNo == @cycle")["Current/mA"].iloc[0]
                / 1000
            )

            self.data_dict[cycle]["Charge_time"] = cycles_to_process.query(
                "CycleNo == @cycle & StepStatus == 'CCC'"
            )["Fixed_time"]
            self.data_dict[cycle]["Charge_voltage"] = cycles_to_process.query(
                "CycleNo == @cycle & StepStatus == 'CCC'"
            )["Voltage/V"]

            self.data_dict[cycle]["Discharge_time"] = cycles_to_process.query(
                "CycleNo == @cycle & StepStatus == 'CCD'"
            )["Fixed_time"]
            self.data_dict[cycle]["Discharge_voltage"] = cycles_to_process.query(
                "CycleNo == @cycle & StepStatus == 'CCD'"
            )["Voltage/V"]

            self.data_dict[cycle]["IR drop"] = (
                self.area
                * (
                    self.data_dict[cycle]["Charge_voltage"].iloc[-1]
                    - self.data_dict[cycle]["Discharge_voltage"].iloc[0]
                )
                / (current_zero_val)
            )

            charge_m, charge_b = np.polyfit(
                x=self.data_dict[cycle]["Charge_time"],
                y=self.data_dict[cycle]["Charge_voltage"],
                deg=1,
            )
            dis_m, dis_b = np.polyfit(
                x=self.data_dict[cycle]["Discharge_time"],
                y=self.data_dict[cycle]["Discharge_voltage"],
                deg=1,
            )

            self.data_dict[cycle]["Charge_slope/intercept"] = (charge_m, charge_b)
            self.data_dict[cycle]["Discharge_slope/intercept"] = (dis_m, dis_b)
            self.data_dict[cycle]["Charge_cap"] = 2 * (1 / charge_m) * current_zero_val
            self.data_dict[cycle]["Discharge_cap"] = (
                2 * (-1 / dis_m) * current_zero_val
            ) / self.mass

    def plot_first_and_last_cycle(self, axis):
        keys = list(self.data_dict.keys())
        first, last = keys[0], keys[-1]

        charge_time_first = (
            self.data_dict[first]["Charge_time"]
            - self.data_dict[first]["Charge_time"].iloc[0]
        )
        discharge_time_first = (
            self.data_dict[first]["Discharge_time"]
            - self.data_dict[first]["Charge_time"].iloc[0]
        )
        charge_time_last = (
            self.data_dict[last]["Charge_time"]
            - self.data_dict[last]["Charge_time"].iloc[0]
        )
        discharge_time_last = (
            self.data_dict[last]["Discharge_time"]
            - self.data_dict[last]["Charge_time"].iloc[0]
        )

        axis.plot(
            charge_time_first,
            self.data_dict[first]["Charge_voltage"],
            "-o",
            color="tab:red",
            markevery=0.01,
            label="Before first aging cycle",
        )
        axis.plot(
            discharge_time_first,
            self.data_dict[first]["Discharge_voltage"],
            "-o",
            color="k",
            markevery=0.01,
        )
        axis.plot(
            charge_time_last,
            self.data_dict[last]["Charge_voltage"],
            "-o",
            color="tab:red",
            markevery=0.01,
            markerfacecolor="white",
            label="After aging",
        )
        axis.plot(
            discharge_time_last,
            self.data_dict[last]["Discharge_voltage"],
            "-o",
            color="k",
            markevery=0.01,
            markerfacecolor="white",
        )
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("Potential (V)")
        axis.legend()

    def calc_Qirr(self):
        floating_data = self.df.query("StepStatus == 'CVC'")
        cycles = floating_data["CycleNo"].unique()
        self.qirr_dict = {}

        for idx, cycle in enumerate(cycles):
            self.qirr_dict[idx + 1] = abs(
                np.mean(
                    floating_data.query("CycleNo == @cycle")["Current/mA"][::10]
                    * self.resample_time(
                        floating_data.query("CycleNo == @cycle")["TestTime/Sec"][::10]
                    )
                )
                / 3600
            )

        self.total_qirr = list(accumulate(self.qirr_dict.values()))

    def get_leakage_current(self):
        floating_data = self.df.query("StepStatus == 'CVC'")
        cycles = floating_data["CycleNo"].unique()
        self.leakage_current = [
            round(
                np.mean(floating_data.query("CycleNo == @cycle")["Current/mA"][-100:])
                * 1000,
                2,
            )
            for cycle in cycles
        ]

    def get_cap_decrease(self):
        first = self.data_dict[next(iter(self.data_dict))]["Discharge_cap"]
        self.cap_decrease = [
            round((self.data_dict[key]["Discharge_cap"] / first) * 100, 1)
            for key in self.data_dict
        ]

    def get_resist_increase(self):
        first = self.data_dict[next(iter(self.data_dict))]["IR drop"]
        self.resist_increase = [
            round(((self.data_dict[key]["IR drop"] - first) / first) * 100, 1)
            for key in self.data_dict
        ]

    def plot_IR_drop_cap_fade(self, axis):
        x = []
        y_IR = []
        y_cap = []
        for cycle in self.data_dict:
            x.append(cycle / 6)
            y_IR.append(self.data_dict[cycle]["IR drop"])
            y_cap.append(self.data_dict[cycle]["Discharge_cap"])

        ax2 = axis.twinx()
        axis.plot(x, y_cap, "-o", color="tab:red")
        axis.spines["left"].set_color("tab:red")
        axis.tick_params(axis="y", colors="tab:red")
        axis.yaxis.label.set_color("tab:red")
        ax2.plot(x, y_IR, "-o", color="tab:blue")
        ax2.spines["right"].set_color("tab:blue")
        ax2.tick_params(axis="y", colors="tab:blue")
        ax2.yaxis.label.set_color("tab:blue")
        axis.set_xlabel("Aging Cycle #")
        axis.set_ylabel("Capacitance (F/g)")
        ax2.set_ylabel("IR Drop ($\Omega$.cm$^2$)", rotation=270, va="bottom")
        # figure.tight_layout()
