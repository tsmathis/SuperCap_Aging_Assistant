import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from collections import Counter
from itertools import accumulate

cycle_match = "(?i)Cycle"
status_match = "(?i)StepStatus|Step-State"


class AgingData:
    def __init__(self, mass, area) -> None:
        self.mass = mass
        self.area = area

    def read_data(self, file_name):
        self.df = pd.read_csv(file_name)
        self.cycle_col = str([col for col in self.df if re.search(cycle_match, col)][0])
        self.status_col = [col for col in self.df if re.search(status_match, col)][0]

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
        cycles_to_process = self.df.query(
            "`{0}` % 6 == 0".format(self.cycle_col)
        ).reset_index(drop=True)
        cycles_to_process["Fixed_time"] = self.resample_time(
            cycles_to_process["TestTime/Sec"]
        )

        cycle_num = cycles_to_process[self.cycle_col].unique()
        self.data_dict = {cycle: {} for cycle in cycle_num}

        for cycle in cycle_num:
            current_zero_val = (
                cycles_to_process.query("`{0}` == @cycle".format(self.cycle_col))[
                    "Current/uA"
                ].iloc[0]
                / 1000000
            )

            self.data_dict[cycle]["Charge_time"] = cycles_to_process.query(
                "`{0}` == @cycle & `{1}` == 'CCC'".format(
                    self.cycle_col, self.status_col
                )
            )["Fixed_time"]
            self.data_dict[cycle]["Charge_voltage"] = cycles_to_process.query(
                "`{0}` == @cycle & `{1}` == 'CCC'".format(
                    self.cycle_col, self.status_col
                )
            )["Voltage/V"]

            self.data_dict[cycle]["Discharge_time"] = cycles_to_process.query(
                "`{0}` == @cycle & `{1}` == 'CCD'".format(
                    self.cycle_col, self.status_col
                )
            )["Fixed_time"]
            self.data_dict[cycle]["Discharge_voltage"] = cycles_to_process.query(
                "`{0}` == @cycle & `{1}` == 'CCD'".format(
                    self.cycle_col, self.status_col
                )
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

    def calc_Qirr(self):
        floating_data = self.df.query("`{0}` == 'CVC'".format(self.status_col))
        cycles = floating_data[self.cycle_col].unique()
        self.qirr_dict = {}

        for idx, cycle in enumerate(cycles):
            self.qirr_dict[idx + 1] = abs(
                np.mean(
                    floating_data.query("`{0}` == @cycle".format(self.cycle_col))[
                        "Current/uA"
                    ][::10]
                    * self.resample_time(
                        floating_data.query("`{0}` == @cycle".format(self.cycle_col))[
                            "TestTime/Sec"
                        ][::10]
                    )
                )
                / 3.6e6
            )

        self.total_qirr = list(accumulate(self.qirr_dict.values()))

    def get_leakage_current(self):
        floating_data = self.df.query("`{0}` == 'CVC'".format(self.status_col))
        cycles = floating_data[self.cycle_col].unique()
        self.leakage_current = [
            round(
                np.mean(
                    floating_data.query("`{0}` == @cycle".format(self.cycle_col))[
                        "Current/uA"
                    ][-100:]
                ),
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

    def prep_data(self):
        self.aging_cycles = [cycle / 6 for cycle in self.data_dict]
        self.IR_drop = [self.data_dict[cycle]["IR drop"] for cycle in self.data_dict]
        self.discharge_cap = [
            self.data_dict[cycle]["Discharge_cap"] for cycle in self.data_dict
        ]
        self.charge_cap = [
            self.data_dict[cycle]["Charge_cap"] for cycle in self.data_dict
        ]

    def plot_IR_drop_cap_fade_vs_cycle(self, axis, axis_labels=None):
        ax2 = axis.twinx()

        axis.plot(self.aging_cycles, self.discharge_cap, "-o", color="tab:red")
        axis.spines["left"].set_color("tab:red")
        axis.tick_params(axis="y", colors="tab:red")
        axis.yaxis.label.set_color("tab:red")

        ax2.plot(self.aging_cycles, self.IR_drop, "-o", color="tab:blue")
        ax2.spines["right"].set_color("tab:blue")
        ax2.tick_params(axis="y", colors="tab:blue")
        ax2.yaxis.label.set_color("tab:blue")

        axis.set_xlabel("Aging Cycle #")
        axis.set_ylabel("Capacitance (F/g)")
        ax2.set_ylabel("IR Drop ($\Omega$.cm$^2$)", rotation=270, va="bottom")
        if axis_labels:
            ax2.get_yaxis().set_visible(False)

    def plot_IR_drop_cap_fade_vs_qirr(self, axis, axis_labels=None):
        x = self.total_qirr
        ax2 = axis.twinx()

        axis.plot(x, self.discharge_cap, "-o", color="tab:red")
        axis.spines["left"].set_color("tab:red")
        axis.tick_params(axis="y", colors="tab:red")
        axis.yaxis.label.set_color("tab:red")

        ax2.plot(x, self.IR_drop, "-o", color="tab:blue")
        ax2.spines["right"].set_color("tab:blue")
        ax2.tick_params(axis="y", colors="tab:blue")
        ax2.yaxis.label.set_color("tab:blue")

        axis.set_xlabel("Qirr (mAh)")
        axis.set_ylabel("Capacitance (F/g)")
        ax2.set_ylabel("IR Drop ($\Omega$.cm$^2$)", rotation=270, va="bottom")
        if axis_labels:
            ax2.get_yaxis().set_visible(False)

    def plot_first_and_last_cycle(self, axis, legend=None):
        keys = list(self.data_dict.keys())
        self.first, self.last = keys[0], keys[-1]

        self.charge_time_first = (
            self.data_dict[self.first]["Charge_time"]
            - self.data_dict[self.first]["Charge_time"].iloc[0]
        )
        self.discharge_time_first = (
            self.data_dict[self.first]["Discharge_time"]
            - self.data_dict[self.first]["Charge_time"].iloc[0]
        )
        self.charge_time_last = (
            self.data_dict[self.last]["Charge_time"]
            - self.data_dict[self.last]["Charge_time"].iloc[0]
        )
        self.discharge_time_last = (
            self.data_dict[self.last]["Discharge_time"]
            - self.data_dict[self.last]["Charge_time"].iloc[0]
        )

        axis.plot(
            self.charge_time_first,
            self.data_dict[self.first]["Charge_voltage"],
            "-o",
            color="tab:red",
            markevery=0.01,
            label="Before first aging cycle",
        )
        axis.plot(
            self.discharge_time_first,
            self.data_dict[self.first]["Discharge_voltage"],
            "-o",
            color="k",
            markevery=0.01,
        )
        axis.plot(
            self.charge_time_last,
            self.data_dict[self.last]["Charge_voltage"],
            "-o",
            color="tab:red",
            markevery=0.01,
            markerfacecolor="white",
            label="After aging",
        )
        axis.plot(
            self.discharge_time_last,
            self.data_dict[self.last]["Discharge_voltage"],
            "-o",
            color="k",
            markevery=0.01,
            markerfacecolor="white",
        )
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("Potential (V)")
        if legend:
            axis.legend()

    def prep_export(self):
        self.ccd_curves = pd.DataFrame(
            {
                "First cycle charge time (s)": self.charge_time_first,
                "First cycle charge voltage (V)": self.data_dict[self.first][
                    "Charge_voltage"
                ],
                "First cycle discharge time (s)": self.discharge_time_first,
                "First cycle discharge voltage (V)": self.data_dict[self.first][
                    "Discharge_voltage"
                ],
                "Last cycle charge time (s)": self.charge_time_last,
                "Last cycle charge voltage (V)": self.data_dict[self.last][
                    "Charge_voltage"
                ],
                "Last cycle discharge time (s)": self.discharge_time_last,
                "Last cycle discharge voltage (V)": self.data_dict[self.last][
                    "Discharge_voltage"
                ],
            }
        )

        self.ccd_curves = self.ccd_curves.apply(lambda x: pd.Series(x.dropna().values))

        self.aging_df = pd.DataFrame(
            {
                "Aging Cycles": self.aging_cycles,
                "Qirr (mAh)": [val for val in self.qirr_dict.values()],
                "Qirr total (mAh)": self.total_qirr,
                "Discharge Capacitance (F/g)": self.discharge_cap,
                "Discharge cap decrease (%)": self.cap_decrease,
                "Charge Capacitance (F/g)": self.charge_cap,
                "IR drop (Ohm * cm2)": self.IR_drop,
                "IR drop increase (%)": self.resist_increase,
                "Leakage Current uA": self.leakage_current,
            }
        )
