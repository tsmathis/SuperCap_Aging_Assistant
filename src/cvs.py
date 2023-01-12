import pandas as pd
import numpy as np


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

    def plot_cv_cap_current_density(self, axis, color, label=None):
        axis.plot(
            self.potential,
            self.capacitance,
            color=color,
            label=f"{self.rate} mV/s {label}",
        )
        axis.set_xlabel("Potential (V)")
        axis.set_ylabel("Specific Capacitance (F/g)")
        if label:
            axis.legend()

    def calc_capacitance(self):
        window = max(self.potential) - min(self.potential)

        self.discharge_current = self.df.query(
            "`cycle number` == @self.last_cycle & `<I>/mA` < 0"
        )["<I>/mA"]

        self.charge_current = self.df.query(
            "`cycle number` == @self.last_cycle & `<I>/mA` > 0"
        )["<I>/mA"]

        self.discharge_potential = self.df.query(
            "`cycle number` == @self.last_cycle & `<I>/mA` < 0"
        )["Ewe/V"].sort_values()

        self.charge_potential = self.df.query(
            "`cycle number` == @self.last_cycle & `<I>/mA` > 0"
        )["Ewe/V"].sort_values()

        self.discharge_capacitance = (
            2
            * abs(np.trapz(self.discharge_current, self.discharge_potential))
            / (self.rate * window)
        )
        self.charge_capacitance = (
            2
            * np.trapz(self.charge_current, self.charge_potential)
            / (self.rate * window)
        )

        self.specific_discharge = self.discharge_capacitance / self.mass
        self.specific_charge = self.charge_capacitance / self.mass

    def prep_export(self):
        self.cvs_df = pd.DataFrame(
            {
                "Potential (V)": round(self.potential, 5),
                "Current (mA)": round(self.current, 5),
                "Capacitance for plotting (F/g)": round(self.capacitance, 5),
                "Current Density (A/g)": round(self.current_density, 5),
                "Discharge Capacitance (F)": round(self.discharge_capacitance, 5),
                "Charge Capacitance (F)": round(self.charge_capacitance, 5),
                "Discharge Capacitance (F/g)": round(self.specific_discharge, 5),
                "Charge Capacitance (F/g)": round(self.specific_charge, 5),
                "Coulombic Effciency (%)": round(
                    self.discharge_capacitance / self.charge_capacitance * 100, 5
                ),
            }
        )
