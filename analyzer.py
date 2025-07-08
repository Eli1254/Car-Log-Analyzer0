import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter
import seaborn as sns
import streamlit as st
import io

def load_data(file):
    try:
        return pd.read_csv(file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def show_data_overview(data, max_rows=20):
    st.subheader("Data Preview")
    st.dataframe(data.head(max_rows))
    st.write(f"Shape: {data.shape}")
    st.write("Columns:", list(data.columns))
    st.subheader("Descriptive Statistics")
    st.dataframe(data.describe())

def plot_sensor_data(data, sensor):
    plt.figure()
    plt.plot(data['Time (sec)'], data[sensor])
    plt.xlabel("Time (sec)")
    plt.ylabel(sensor)
    plt.title(f"{sensor} over Time")
    st.pyplot(plt)

def plot_3d_timing_table(data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(
        data['RPM (RPM)'],
        data['Calculated Load (g/rev)'],
        data['Ignition Timing (°)'],
        c=data['Ignition Timing (°)'],
        cmap='viridis'
    )
    ax.set_xlabel("RPM")
    ax.set_ylabel("Load (g/rev)")
    ax.set_zlabel("Ignition Timing (°)")
    st.pyplot(fig)

def plot_boost_vs_rpm(data, window_length=51, poly_order=3):
    rpm = data['RPM (RPM)']
    boost = savgol_filter(data['Boost (psi)'], window_length, poly_order)
    plt.figure()
    plt.plot(rpm, boost)
    plt.xlabel("RPM")
    plt.ylabel("Boost (psi)")
    plt.title("Boost vs RPM (Smoothed)")
    st.pyplot(plt)

def plot_torque_vs_rpm(data, window_length=51, poly_order=3):
    rpm = data['RPM (RPM)']
    torque = savgol_filter(data['Req Torque (Nm)'], window_length, poly_order)
    plt.figure()
    plt.plot(rpm, torque)
    plt.xlabel("RPM")
    plt.ylabel("Torque (Nm)")
    plt.title("Torque vs RPM (Smoothed)")
    st.pyplot(plt)

def estimate_horsepower(data):
    rpm = data['RPM (RPM)']
    torque_nm = data['Req Torque (Nm)']
    torque_lbft = torque_nm * 0.73756
    hp = (torque_lbft * rpm) / 5252
    data['Estimated Horsepower'] = hp
    plt.figure()
    plt.plot(rpm, hp)
    plt.xlabel("RPM")
    plt.ylabel("Horsepower")
    plt.title("Estimated Horsepower")
    st.pyplot(plt)
    return data

def estimate_zero_to_sixty(weight, altitude, max_hp):
    alt_factor = 1 + (altitude / 10000) * 0.1
    t_0_60 = 5.5 * ((weight / max_hp) ** 0.5) * alt_factor
    return t_0_60

def estimate_quarter_mile(weight, altitude, max_hp):
    alt_factor = 1 + (altitude / 10000) * 0.1
    et_1_4 = 5.825 * ((weight / max_hp) ** (1/3)) * alt_factor
    return et_1_4

def plot_knock_afr(data):
    knock_cols = [c for c in data.columns if "knock" in c.lower()]
    afr_cols = [c for c in data.columns if "afr" in c.lower()]
    if not knock_cols or not afr_cols:
        st.warning("No knock or AFR data found.")
        return

    fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    time = data['Time (sec)']
    for col in knock_cols:
        axs[0].plot(time, data[col], label=col)
    axs[0].set_title("Knock")
    axs[0].legend()
    for col in afr_cols:
        axs[1].plot(time, data[col], label=col)
    axs[1].set_title("AFR")
    axs[1].legend()
    st.pyplot(fig)

def plot_timing_heatmap(data):
    pivot = data.pivot_table(index='RPM (RPM)', columns='Calculated Load (g/rev)', values='Ignition Timing (°)', aggfunc='mean')
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot, cmap="viridis")
    plt.title("Ignition Timing Heatmap")
    st.pyplot(plt)

def export_plot_png():
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    st.download_button("Download Plot as PNG", buf, file_name="plot.png", mime="image/png")

def plot_compare_logs(data1, data2, sensor):
    plt.figure()
    plt.plot(data1['Time (sec)'], data1[sensor], label="Log 1")
    plt.plot(data2['Time (sec)'], data2[sensor], label="Log 2", alpha=0.7)
    plt.title(f"{sensor} Comparison")
    plt.legend()
    st.pyplot(plt)
