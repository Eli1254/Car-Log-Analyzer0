import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import streamlit as st
import io

def load_data(file):
    try:
        data = pd.read_csv(file, encoding='ISO-8859-1')
        st.success("✅ Data loaded successfully.")
        return data
    except FileNotFoundError:
        st.error("❌ File not found.")
        return None
    except UnicodeDecodeError:
        st.error("❌ File encoding error.")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return None

def check_required_columns(data, required_cols, context=""):
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        st.warning(f"⚠️ Missing columns for {context}: {', '.join(missing)}")
        return False
    return True

def show_data_overview(data, max_rows=20):
    if data is None or data.empty:
        st.warning("⚠️ No data to preview.")
        return
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

def _safe_savgol_filter(series, window_length=51, poly_order=3):
    try:
        length = len(series)
        if length < 5:
            return series
        wl = min(window_length, length if length % 2 != 0 else length - 1)
        if wl < poly_order + 2:
            wl = poly_order + 2 if (poly_order + 2) % 2 != 0 else poly_order + 3
        if wl > length:
            wl = length if length % 2 != 0 else length - 1
        return savgol_filter(series, window_length=wl, polyorder=poly_order)
    except Exception:
        return series

def plot_sensor_data(data, sensor, highlight_events=False, metric=None, custom_events=None):
    if data is None or sensor not in data.columns or 'Time (sec)' not in data.columns:
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
            plt.text(row['Time (sec)'], data[sensor].min(), f"{metric}: {row[metric]:.1f}", rotation=90, color='red')

    if custom_events:
        for event in custom_events:
            if 0 <= event['time'] <= time.max():
                plt.axvline(x=event['time'], color='purple', linestyle=':')
                plt.text(event['time'], data[sensor].min(), event['label'], rotation=90, color='purple')

    st.pyplot(plt)

def plot_3d_timing_table(data):
    if not check_required_columns(data, ['RPM (RPM)', 'Calculated Load (g/rev)', 'Ignition Timing (°)'], "3D Timing Table"):
        return
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(
        data['RPM (RPM)'], data['Calculated Load (g/rev)'], data['Ignition Timing (°)'],
        c=data['Ignition Timing (°)'], cmap='viridis'
    )
    fig.colorbar(scatter, label="Timing (°)")
    ax.set_xlabel("RPM")
    ax.set_ylabel("Load (g/rev)")
    ax.set_zlabel("Timing (°)")
    ax.set_title("3D Timing Table")
    st.pyplot(fig)

def plot_boost_vs_rpm(data, window_length=51, poly_order=3):
    if not check_required_columns(data, ['RPM (RPM)', 'Boost (psi)'], "Boost vs RPM"):
        return
    boost_smoothed = _safe_savgol_filter(data['Boost (psi)'], window_length, poly_order)
    plt.figure(figsize=(12, 6))
    plt.plot(data['RPM (RPM)'], boost_smoothed, label="Boost (Smoothed)", color='blue')
    plt.xlabel("RPM")
    plt.ylabel("Boost (psi)")
    plt.title("Boost vs RPM")
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

def plot_torque_vs_rpm(data, window_length=51, poly_order=3):
    if not check_required_columns(data, ['RPM (RPM)', 'Req Torque (Nm)'], "Torque vs RPM"):
        return
    torque_smoothed = _safe_savgol_filter(data['Req Torque (Nm)'], window_length, poly_order)
    plt.figure(figsize=(12, 6))
    plt.plot(data['RPM (RPM)'], torque_smoothed, label="Torque (Smoothed)", color='orange')
    plt.xlabel("RPM")
    plt.ylabel("Torque (Nm)")
    plt.title("Torque vs RPM")
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

def estimate_horsepower(data):
    if not check_required_columns(data, ['RPM (RPM)', 'Req Torque (Nm)'], "Horsepower Estimation"):
        return
    rpm = data['RPM (RPM)']
    torque_lbft = data['Req Torque (Nm)'] * 0.73756
    hp = (torque_lbft * rpm) / 5252
    data['Estimated Horsepower'] = hp
    plt.figure(figsize=(12, 6))
    plt.plot(rpm, hp, label="Estimated HP", color='green')
    plt.xlabel("RPM")
    plt.ylabel("Horsepower")
    plt.title("Estimated Horsepower vs RPM")
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

def estimate_quarter_mile(data, weight, altitude):
    if 'Estimated Horsepower' not in data.columns:
        st.warning("⚠️ Run HP estimation first.")
        return
    max_hp = data['Estimated Horsepower'].max()
    correction = max(0.5, 1 - 0.03 * (altitude / 1000))
    corrected_hp = max_hp * correction
    et = 6.29 * (weight / corrected_hp) ** (1/3)
    st.write(f"Estimated 1/4 Mile: **{et:.2f} sec**")

def estimate_0_60(data, weight, altitude, drivetrain_loss_pct=15):
    if data is None:
        st.warning("⚠️ No data for 0-60 estimate.")
        return

    if 'Estimated Horsepower' not in data.columns:
        st.warning("⚠️ Run horsepower estimation first.")
        return

    max_hp = data['Estimated Horsepower'].max()
    correction = max(0.5, 1 - 0.03 * (altitude / 1000))
    corrected_hp = max_hp * correction
    wheel_hp = corrected_hp * (1 - drivetrain_loss_pct / 100)

    # Use physics-based formula for 0-60 time (approx)
    # t_0_60 = k * (weight / wheel_hp), k ~ 5.825 (empirical)
    t_0_60 = 5.825 * weight / wheel_hp
    st.write(f"Estimated 0–60 mph Time: **{t_0_60:.2f} seconds** (weight={weight} lbs, corrected HP={corrected_hp:.1f})")


def show_complex_statistics(data):
    st.write("### Descriptive Stats")
    st.dataframe(data.describe())
    st.write("### Correlation Matrix")
    st.dataframe(data.corr())
