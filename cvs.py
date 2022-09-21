import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class CVs:
    def __init__(self, rate, mass) -> None:
        self.rate = rate
        self.mass = mass

    def read_prep_data(self, file_name):
        self.df = pd.read_table(file_name)
        self.last_cycle = self.df["cycle number"].unique()[-1]
        self.potential = self.df.query("`cycle number` == @self.last_cycle")["Ewe/V"]
        self.current = self.df.query("`cycle number` == @self.last_cycle")["<I>/mA"]
        self.capacitance = self.current / (self.mass * self.rate)
        self.current_density = self.current / (self.mass)

    def plot_cv_cap_current_density(self, axis, label=None):
        axis.plot(self.potential, self.capacitance, label=f"{self.rate} mV/s {label}")
        axis.set_xlabel("Potential (V)")
        axis.set_ylabel("Specific Capacitance (F/g)")
        if label:
            axis.legend()

    def calc_capacitance(self):
        pass

    def prep_export(self):
        self.cvs_df = pd.DataFrame(
            {
                "Potential (V)": self.potential,
                "Current (mA)": self.current,
                "Capacitance for plotting (F/g)": self.capacitance,
                "Current Density (A/g)": self.current_density,
            }
        )
