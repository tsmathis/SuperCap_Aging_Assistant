import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class CVs:
    def __init__(self, rate, mass) -> None:
        self.rate = rate
        self.mass = mass

    def read_data(self, file_name):
        self.df = pd.read_table(file_name)
        self.last_cycle = self.df["cycle number"].unique()[-1]

    def plot_cv_cap_current_density(self, axis, label=None):
        self.potential = self.df.query("`cycle number` == @self.last_cycle")["Ewe/V"]
        self.capacitance = self.df.query("`cycle number` == @self.last_cycle")[
            "<I>/mA"
        ] / (self.mass * self.rate)
        self.current_density = self.df.query("`cycle number` == @self.last_cycle")[
            "<I>/mA"
        ] / (self.mass)

        axis.plot(self.potential, self.capacitance, label=f"{self.rate} mV/s {label}")
        axis.set_xlabel("Potential (V)")
        axis.set_ylabel("Specific Capacitance (F/g)")
        if label:
            axis.legend()

    def calc_capacitance(self):
        pass
