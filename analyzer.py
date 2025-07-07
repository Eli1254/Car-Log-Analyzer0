import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter
from mpl_toolkits.mplot3d import Axes3D
import streamlit as st
import seaborn as sns

def load_data(file) -> pd.DataFrame:
    try:
        return pd.read_csv(file, encoding='ISO-8859-1')
    except UnicodeDecodeError:
        return pd.read_csv(file, encoding='utf-8', errors='replace')


def plot_sensor_data(data, sensor_name):
    if sensor_name not in data.columns:
        st.warning(f"Sensor {sensor_name} not found.")
        return

    st.line_chart(data[sensor_name])


def show_complex_statistics(data):
    numeric = data.select_dtypes(include=np.number)
    desc = numeric.describe().T
    desc["variance"] = numeric.var()
    desc["skewness"] = numeric.skew()
    st.write(desc)

    st.subheader("Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(8,6))
    sns.heatmap(numeric.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    st.pyplot(fig)


def filter_by_time_range(data, start, end):
    return data[(data['Time (sec)'] >= start) & (data['Time (sec)'] <= end)]


def plot_boost_vs_rpm(data):
    if 'RPM (RPM)' not in data.columns or 'Boost (psi)' not in data.columns:
        st.warning("Required columns missing.")
        return

    boost = savgol_filter(data['Boost (psi)'], 51, 3)
    fig, ax = plt.subplots()
    ax.plot(data['RPM (RPM)'], boost, label="Boost (psi)")
    ax.set_xlabel("RPM")
    ax.set_ylabel("Boost (psi)")
    ax.grid()
    st.pyplot(fig)


def plot_torque_vs_rpm(data):
    if 'RPM (RPM)' not in data.columns or 'Req Torque (Nm)' not in data.columns:
        st.warning("Required columns missing.")
        return

    torque = savgol_filter(data['Req Torque (Nm)'], 51, 3)
    fig, ax = plt.subplots()
    ax.plot(data['RPM (RPM)'], torque, label="Torque (Nm)")
    ax.set_xlabel("RPM")
    ax.set_ylabel("Torque (Nm)")
    ax.grid()
    st.pyplot(fig)


def plot_boost_vs_torque(data):
    if 'Boost (psi)' not in data.columns or 'Req Torque (Nm)' not in data.columns:
        st.warning("Required columns missing.")
        return

    boost = savgol_filter(data['Boost (psi)'], 51, 3)
    torque = savgol_filter(data['Req Torque (Nm)'], 51, 3)

    fig, ax = plt.subplots()
    ax.plot(boost, torque, label="Boost vs Torque")
    ax.set_xlabel("Boost (psi)")
    ax.set_ylabel("Torque (Nm)")
    ax.grid()
    st.pyplot(fig)


def estimate_horsepower_from_torque(data):
    if 'Req Torque (Nm)' not in data.columns or 'RPM (RPM)' not in data.columns:
        st.warning("Required columns missing.")
        return data

    torque_lbft = data['Req Torque (Nm)'] * 0.73756
    data['Estimated Horsepower'] = (torque_lbft * data['RPM (RPM)']) / 5252

    fig, ax = plt.subplots()
    ax.plot(data['RPM (RPM)'], data['Estimated Horsepower'], label="Estimated HP")
    ax.set_xlabel("RPM")
    ax.set_ylabel("Horsepower")
    ax.grid()
    st.pyplot(fig)

    return data


def plot_3d_timing_table(data):
    if not all(c in data.columns for c in ['RPM (RPM)', 'Calculated Load (g/rev)', 'Ignition Timing (°)']):
        st.warning("Required columns missing.")
        return

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(
        data['RPM (RPM)'],
        data['Calculated Load (g/rev)'],
        data['Ignition Timing (°)'],
        c=data['Ignition Timing (°)'],
        cmap='viridis'
    )
    fig.colorbar(sc, label="Ignition Timing")
    ax.set_xlabel("RPM")
    ax.set_ylabel("Load (g/rev)")
    ax.set_zlabel("Timing (°)")
    st.pyplot(fig)


def plot_with_events(data, sensor_name, events):
    if sensor_name not in data.columns:
        st.warning(f"Sensor {sensor_name} not found.")
        return

    fig, ax = plt.subplots()
    ax.plot(data['Time (sec)'], data[sensor_name], label=sensor_name)

    for event in events:
        ax.axvline(event['time'], color='red', linestyle='--')
        ax.text(event['time'], ax.get_ylim()[0], event['label'], rotation=90, color='red')

    ax.set_xlabel("Time (sec)")
    ax.set_ylabel(sensor_name)
    st.pyplot(fig)


def adjust_hp_for_altitude(hp, altitude_ft):
    correction_factor = 1 - (0.03 * altitude_ft / 1000)
    correction_factor = max(correction_factor, 0.5)
    return hp * correction_factor


def estimate_quarter_mile(data, vehicle_weight, altitude):
    if 'Estimated Horsepower' not in data.columns:
        st.warning("Run horsepower estimation first.")
        return

    max_hp = data['Estimated Horsepower'].max()
    corrected_hp = adjust_hp_for_altitude(max_hp, altitude)
    et = 6.29 * (vehicle_weight / corrected_hp) ** (1/3)

    st.write(f"**Estimated 1/4 Mile ET: {et:.2f} seconds**")


def estimate_0_60_time(data, vehicle_weight, altitude, drivetrain_loss_pct=15):
    if 'Estimated Horsepower' not in data.columns:
        st.warning("Run horsepower estimation first.")
        return

    max_hp = data['Estimated Horsepower'].max()
    corrected_hp = adjust_hp_for_altitude(max_hp, altitude)
    wheel_hp = corrected_hp * (1 - drivetrain_loss_pct / 100)
    zero_to_sixty = (5.825 * vehicle_weight) / wheel_hp

    st.write(f"**Estimated 0-60 mph Time: {zero_to_sixty:.2f} seconds**")

