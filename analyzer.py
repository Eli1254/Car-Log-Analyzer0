import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter
from mpl_toolkits.mplot3d import Axes3D
import streamlit as st

def load_data(file):
    try:
        data = pd.read_csv(file, encoding='ISO-8859-1')
        st.success("✅ Data loaded successfully.")
        return data
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None

def show_data_overview(data, max_rows=500):
    st.write("### Data Preview")
    st.dataframe(data.head(max_rows))
    st.write(f"Shape: {data.shape}")
    st.write("Columns:", list(data.columns))

    missing = data.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        st.write("### Missing Values")
        st.dataframe(missing)
    else:
        st.write("✅ No missing values detected.")


def plot_sensor_data(data, sensor, highlight_events=False, metric=None):
    if sensor not in data.columns:
        st.warning(f"Sensor '{sensor}' not found.")
        return

    time = data['Time (sec)']
    plt.figure(figsize=(12, 6))
    plt.plot(time, data[sensor], label=sensor)
    plt.xlabel("Time (sec)")
    plt.ylabel(sensor)
    plt.title(f"{sensor} over Time")
    plt.grid(True)

    if highlight_events and metric in data.columns:
        top_events = data.nlargest(3, metric)
        for _, row in top_events.iterrows():
            plt.axvline(x=row['Time (sec)'], color='red', linestyle='--')
            plt.text(row['Time (sec)'], data[sensor].min(), f"{metric}: {row[metric]:.1f}", rotation=90, verticalalignment='bottom', color='red')

    plt.legend()
    st.pyplot(plt)

def plot_3d_timing_table(data):
    required_cols = ['RPM (RPM)', 'Calculated Load (g/rev)', 'Ignition Timing (°)']
    if not all(col in data.columns for col in required_cols):
        st.warning("Required columns missing for 3D plot.")
        return

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(
        data['RPM (RPM)'],
        data['Calculated Load (g/rev)'],
        data['Ignition Timing (°)'],
        c=data['Ignition Timing (°)'],
        cmap='viridis'
    )
    fig.colorbar(scatter, label="Timing (°)")
    ax.set_xlabel("RPM")
    ax.set_ylabel("Load (g/rev)")
    ax.set_zlabel("Ignition Timing (°)")
    ax.set_title("3D Timing Table")
    st.pyplot(fig)

def plot_boost_vs_rpm(data, window_length=51, poly_order=3):
    required_cols = ['RPM (RPM)', 'Boost (psi)']
    if not all(col in data.columns for col in required_cols):
        st.warning("Required columns missing for Boost vs RPM.")
        return

    boost = savgol_filter(data['Boost (psi)'], window_length=window_length, polyorder=poly_order)
    plt.figure(figsize=(12, 6))
    plt.plot(data['RPM (RPM)'], boost, label="Boost (Smoothed)", color='blue')
    plt.xlabel("RPM")
    plt.ylabel("Boost (psi)")
    plt.title("Boost (psi) vs RPM (Smoothed)")
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

def plot_torque_vs_rpm(data, window_length=51, poly_order=3):
    required_cols = ['RPM (RPM)', 'Req Torque (Nm)']
    if not all(col in data.columns for col in required_cols):
        st.warning("Required columns missing for Torque vs RPM.")
        return

    torque = savgol_filter(data['Req Torque (Nm)'], window_length=window_length, polyorder=poly_order)
    plt.figure(figsize=(12, 6))
    plt.plot(data['RPM (RPM)'], torque, label="Torque (Smoothed)", color='orange')
    plt.xlabel("RPM")
    plt.ylabel("Torque (Nm)")
    plt.title("Torque (Nm) vs RPM (Smoothed)")
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

def plot_boost_vs_torque(data, window_length=51, poly_order=3):
    required_cols = ['Boost (psi)', 'Req Torque (Nm)']
    if not all(col in data.columns for col in required_cols):
        st.warning("Required columns missing for Boost vs Torque.")
        return

    boost = savgol_filter(data['Boost (psi)'], window_length=window_length, polyorder=poly_order)
    torque = savgol_filter(data['Req Torque (Nm)'], window_length=window_length, polyorder=poly_order)
    plt.figure(figsize=(12, 6))
    plt.plot(boost, torque, label="Boost vs Torque (Smoothed)", color='purple')
    plt.xlabel("Boost (psi)")
    plt.ylabel("Torque (Nm)")
    plt.title("Boost (psi) vs Torque (Nm) (Smoothed)")
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

def estimate_horsepower(data):
    required_cols = ['RPM (RPM)', 'Req Torque (Nm)']
    if not all(col in data.columns for col in required_cols):
        st.warning("Required columns missing for HP estimation.")
        return

    rpm = data['RPM (RPM)']
    torque_nm = data['Req Torque (Nm)']
    torque_lbft = torque_nm * 0.73756
    hp = (torque_lbft * rpm) / 5252

    plt.figure(figsize=(12, 6))
    plt.plot(rpm, hp, label="Estimated HP", color='green')
    plt.xlabel("RPM")
    plt.ylabel("Estimated Horsepower")
    plt.title("Estimated Horsepower vs RPM (from Requested Torque)")
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

def show_complex_statistics(data):
    st.write("### Descriptive Statistics")
    st.dataframe(data.describe())
    st.write("### Correlation Matrix")
    st.dataframe(data.corr())


