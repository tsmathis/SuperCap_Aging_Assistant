import pandas as pd
import matplotlib.pyplot as plt


class Eis:
    def __init__(self, area) -> None:
        self.area = area

    def read_data(self, file_name):
        self.df = pd.read_table(file_name)

    def calc_eis_cap(self):
        # Convert Hz to rad/s
        self.df["C''"] = self.df["Re(Z)/Ohm"] / (
            self.df["freq/Hz"] * 6.28 * self.df["|Z|/Ohm"] ** 2
        )
        self.df["C'"] = self.df["-Im(Z)/Ohm"] / (
            self.df["freq/Hz"] * 6.28 * self.df["|Z|/Ohm"] ** 2
        )

    def prep_export(self):
        self.eis_df = pd.DataFrame(
            {
                "Freq (Hz)": self.df["freq/Hz"],
                "Freq (rad/s)": self.df["freq/Hz"] * 6.28,
                "Re(Z)/Ohm": self.df["Re(Z)/Ohm"],
                "-Im(Z)/Ohm": self.df["-Im(Z)/Ohm"],
                "C'' (F)": self.df["C''"],
                "C' (F)": self.df["C'"],
                "C'' (F/cm^2)": self.df["C''"] / self.area,
                "C' (F/cm^2)": self.df["C'"] / self.area,
            }
        )

    def nyquist_plots(self, figure, axis, color, marker, axis_labels=None, label=None):
        x = self.df["Re(Z)/Ohm"] * self.area
        y = self.df["-Im(Z)/Ohm"] * self.area
        min_x, min_y = min(x), min(y)
        max_val = max(max(x), max(y))

        base = axis
        base.plot(x, y, marker=marker, color=color, label=label)
        base.set_xlim(min_x * 0.95, max_val * 1.1)
        base.set_ylim(min_y * 0.95, max_val * 1.1)
        base.set_xlabel("Re(Z) ($\Omega$.cm$^2$)")
        base.set_ylabel("-Im(Z) ($\Omega$.cm$^2$)")
        if label:
            base.legend()

        if len(figure.axes) > 1:
            figure.axes[1].plot(x, y, marker=marker, color=color)
        else:
            figure.add_axes([0.55, 0.2, 0.3, 0.3])
            figure.axes[1].plot(x, y, marker=marker, color=color)
            figure.axes[1].set_xlim(min_x * 0.95, max_val * 0.05)
            figure.axes[1].set_ylim(min_y * 0.95, max_val * 0.05)
            if axis_labels:
                figure.axes[1].get_xaxis().set_visible(False)
                figure.axes[1].get_yaxis().set_visible(False)

        def enter_axes(event):
            if not event.inaxes:
                return
            if event.inaxes == figure.axes[1]:
                base.set_navigate(False)
            elif event.inaxes == base:
                base.set_navigate(True)

        figure.canvas.mpl_connect("axes_enter_event", enter_axes)

    def plot_caps_vs_freq(self, axis, label="", color="tab:red"):
        axis.plot(
            self.df["freq/Hz"],
            self.df["C'"] / self.area,
            marker="o",
            color=color,
            label=("C'' " + label),
        )
        axis.plot(
            self.df["freq/Hz"],
            self.df["C''"] / self.area,
            marker="s",
            color=color,
            markerfacecolor="white",
            label=("C' " + label),
        )
        axis.set_xscale("log")
        axis.set_xlabel("Freq. (Hz)")
        axis.set_ylabel("F/cm$^2$")
        if len(label) > 1:
            axis.legend()

    def plot_img_cap_vs_real_Z(self, axis, marker, color, label=None):
        axis.plot(
            self.df["Re(Z)/Ohm"],
            self.df["C''"] / self.area,
            marker=marker,
            color=color,
            label=label,
        )
        axis.set_xlabel("Re(Z) ($\Omega$)")
        axis.set_ylabel("C'' (F/cm$^2$)")
        if label:
            axis.legend()
