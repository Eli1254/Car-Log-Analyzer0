# analyzer.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from mpl_toolkits.mplot3d import Axes3D
from io import BytesIO


class CarLogAnalyzer:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def plot_sensor(self, sensor: str) -> BytesIO:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(self.data['Time (sec)'], self.data[sensor], label=sensor)
        ax.set_xlabel("Time (sec)")
        ax.set_ylabel(sensor)
        ax.set_title(f"{sensor} over Time")
        ax.grid()
        ax.legend()
        return self._fig_to_buf(fig)

    def estimate_horsepower(self) -> BytesIO:
        rpm_col = 'RPM (RPM)'
        torque_col = 'Req Torque (Nm)'

        if rpm_col not in self.data.columns or torque_col not in self.data.columns:
            raise ValueError("Required columns for HP estimation are missing")

        torque_lbft = self.data[torque_col] * 0.73756
        rpm = self.data[rpm_col]
        hp = (torque_lbft * rpm) / 5252
        self.data['Estimated HP'] = hp

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(rpm, hp, label='Estimated HP', color='green')
        ax.set_xlabel("RPM")
        ax.set_ylabel("Estimated HP")
        ax.set_title("Estimated Horsepower vs RPM")
        ax.grid()
        ax.legend()
        return self._fig_to_buf(fig)

    def plot_boost_vs_rpm(self, window_length=51, polyorder=3) -> BytesIO:
        rpm_col = 'RPM (RPM)'
        boost_col = 'Boost (psi)'

        if rpm_col not in self.data.columns or boost_col not in self.data.columns:
            raise ValueError("Required columns for Boost vs RPM are missing")

        rpm = self.data[rpm_col]
        boost = self.data[boost_col]
        smooth_boost = savgol_filter(boost, window_length, polyorder)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(rpm, smooth_boost, label='Boost (smoothed)', color='blue')
        ax.set_xlabel("RPM")
        ax.set_ylabel("Boost (psi)")
        ax.set_title("Boost vs RPM")
        ax.grid()
        ax.legend()
        return self._fig_to_buf(fig)

    def _fig_to_buf(self, fig) -> BytesIO:
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf
