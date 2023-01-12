from collections import deque

from data_export import export_data

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import pyqtSignal, QEvent
from PyQt5.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QGridLayout,
    QWidget,
)


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig = Figure(dpi=150, constrained_layout=True)
        self.axes = self.fig.add_subplot()
        super().__init__(self.fig)


class ClickableWidget(MplCanvas):
    clicked = pyqtSignal(int)

    def __init__(self, idx=None, parent=None):
        self.fig = Figure(dpi=100)
        self.axes = self.fig.add_subplot()
        super().__init__(self.fig)
        self.setMaximumSize(150, 150)
        self.setMinimumSize(50, 50)
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)
        self.index = idx
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if isinstance(obj, MplCanvas) and event.type() == QEvent.MouseButtonPress:
            self.clicked.emit(self.index)
        return QWidget.eventFilter(self, obj, event)


class DataWindow(QMainWindow):
    def __init__(self, aging_data, cvs_before, cvs_after, eis_before, eis_after):
        super().__init__()
        self.setWindowTitle("SuperCap Aging")

        self.aging_data = aging_data
        self.cvs_before = cvs_before
        self.cvs_after = cvs_after
        self.eis_before = eis_before
        self.eis_after = eis_after

        pagelayout = QHBoxLayout()
        button_layout = QGridLayout()
        self.stacklayout = QStackedLayout()

        buttons = QWidget()
        stack = QWidget()
        stack.setMinimumSize(400, 400)
        stack.setLayout(self.stacklayout)
        buttons.setLayout(button_layout)
        buttons.setFixedWidth(350)

        window_queue = deque(maxlen=12)

        for i in range(12):
            fig = MplCanvas()
            fig_toolbar = NavigationToolbar(fig, self)
            window = QWidget()
            window_layout = QVBoxLayout()
            window.setLayout(window_layout)
            window_layout.addWidget(fig_toolbar)
            window_layout.addWidget(fig)
            self.stacklayout.addWidget(window)
            window_queue.append(fig)

        widget_slot_queue = deque(maxlen=12)

        for i in range(12):
            button = ClickableWidget(idx=i)
            button.clicked.connect(self.change_active_view)
            if i % 2 == 0:
                button_layout.addWidget(button, int(i / 2), 0, 1, 1)
            else:
                button_layout.addWidget(button, int(i / 2), 1, 1, 1)
            widget_slot_queue.append(button)

        export = QPushButton("Export Data")
        export.setStyleSheet("background-color: #007AFF")
        export.clicked.connect(self.get_export_location)
        button_layout.addWidget(export, 7, 0, 1, 2)

        pagelayout.addWidget(stack)
        pagelayout.addWidget(buttons)

        if self.aging_data:
            self.aging_data.prep_data()
            btn = widget_slot_queue.popleft()
            self.aging_data.plot_IR_drop_cap_fade_vs_cycle(axis=btn.axes, axis_labels=1)
            fig = window_queue.popleft()
            self.aging_data.plot_IR_drop_cap_fade_vs_cycle(axis=fig.axes)

            btn2 = widget_slot_queue.popleft()
            self.aging_data.plot_IR_drop_cap_fade_vs_qirr(axis=btn2.axes, axis_labels=1)
            fig2 = window_queue.popleft()
            self.aging_data.plot_IR_drop_cap_fade_vs_qirr(axis=fig2.axes)

            btn3 = widget_slot_queue.popleft()
            self.aging_data.plot_first_and_last_cycle(axis=btn3.axes)
            fig3 = window_queue.popleft()
            self.aging_data.plot_first_and_last_cycle(axis=fig3.axes, legend=1)
            self.aging_data.prep_export()

        if self.cvs_before and self.cvs_after:
            for (keyb, keya) in zip(self.cvs_before, self.cvs_after):
                btn = widget_slot_queue.popleft()
                self.cvs_before[keyb].plot_cv_cap_current_density(
                    axis=btn.axes, color="tab:red"
                )
                self.cvs_after[keya].plot_cv_cap_current_density(
                    axis=btn.axes, color="k"
                )

                fig = window_queue.popleft()
                self.cvs_before[keyb].plot_cv_cap_current_density(
                    label="before aging", axis=fig.axes, color="tab:red"
                )
                self.cvs_after[keya].plot_cv_cap_current_density(
                    label="after aging", axis=fig.axes, color="k"
                )

        if self.cvs_before and not self.cvs_after:
            for keyb in self.cvs_before:
                btn = widget_slot_queue.popleft()
                self.cvs_before[keyb].plot_cv_cap_current_density(
                    axis=btn.axes, color="tab:red"
                )

                fig = window_queue.popleft()
                self.cvs_before[keyb].plot_cv_cap_current_density(
                    label="before aging", axis=fig.axes, color="tab:red"
                )

        if self.cvs_after and not self.cvs_before:
            for keya in self.cvs_after:
                btn = widget_slot_queue.popleft()
                self.cvs_after[keya].plot_cv_cap_current_density(
                    axis=btn.axes, color="k"
                )

                fig = window_queue.popleft()
                self.cvs_after[keya].plot_cv_cap_current_density(
                    label="after aging", axis=fig.axes, color="k"
                )

        eis_labels = ["OCV", "0.5 V", "1.0 V"]
        eis_colors = ["black", "tab:red", "tab:blue"]
        if self.eis_before and self.eis_after:
            for keyb, keya, label in zip(self.eis_before, self.eis_after, eis_labels):
                btn = widget_slot_queue.popleft()
                self.eis_before[keyb].plot_caps_vs_freq(axis=btn.axes)
                self.eis_after[keya].plot_caps_vs_freq(axis=btn.axes, color="k")

                fig = window_queue.popleft()
                self.eis_before[keyb].plot_caps_vs_freq(
                    label=f"{label} before aging", axis=fig.axes
                )
                self.eis_after[keya].plot_caps_vs_freq(
                    label=f"{label} after aging", color="k", axis=fig.axes
                )

        if self.eis_before:
            btn = widget_slot_queue.popleft()
            fig = window_queue.popleft()
            for key, label, color in zip(self.eis_before, eis_labels, eis_colors):
                self.eis_before[key].nyquist_plots(
                    figure=btn.fig,
                    axis=btn.axes,
                    marker="o",
                    axis_labels=1,
                    color=color,
                )
                self.eis_before[key].nyquist_plots(
                    label=f"{label} before aging",
                    figure=fig.fig,
                    axis=fig.axes,
                    marker="o",
                    color=color,
                )

            btn = widget_slot_queue.popleft()
            fig = window_queue.popleft()

            for key, label, color in zip(self.eis_before, eis_labels, eis_colors):
                self.eis_before[key].plot_img_cap_vs_real_Z(
                    axis=btn.axes, marker="o", color=color
                )
                self.eis_before[key].plot_img_cap_vs_real_Z(
                    label=f"{label} before aging",
                    axis=fig.axes,
                    marker="o",
                    color=color,
                )

        if self.eis_after:
            btn = widget_slot_queue.popleft()
            fig = window_queue.popleft()
            for key, label, color in zip(self.eis_after, eis_labels, eis_colors):
                self.eis_after[key].nyquist_plots(
                    figure=btn.fig,
                    axis=btn.axes,
                    marker="s",
                    axis_labels=1,
                    color=color,
                )
                self.eis_after[key].nyquist_plots(
                    label=f"{label} after aging",
                    figure=fig.fig,
                    axis=fig.axes,
                    marker="s",
                    color=color,
                )

            btn = widget_slot_queue.popleft()
            fig = window_queue.popleft()

            for key, label, color in zip(self.eis_after, eis_labels, eis_colors):
                self.eis_after[key].plot_img_cap_vs_real_Z(
                    axis=btn.axes, marker="s", color=color
                )
                self.eis_after[key].plot_img_cap_vs_real_Z(
                    label=f"{label} after aging", axis=fig.axes, marker="s", color=color
                )

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    def change_active_view(self, clicked):
        self.stacklayout.setCurrentIndex(clicked)

    def get_export_location(self):
        file_name, filters = QFileDialog.getSaveFileName(self, filter="Excel (*.xlsx)")
        if not file_name:
            return
        export_data(
            file_name=file_name,
            aging_data=self.aging_data,
            cvs_before=self.cvs_before,
            cvs_after=self.cvs_after,
            eis_before=self.eis_before,
            eis_after=self.eis_after,
        )
