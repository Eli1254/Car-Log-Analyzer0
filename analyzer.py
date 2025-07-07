import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import streamlit as st

def load_data(file):
    try:
        data = pd.read_csv(file, encoding='ISO-8859-1')
        st.success("✅ Data loaded successfully.")
        return data
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        return None

def show_data_overview(data, max_rows=20):
    if data is None or data.empty:
        st.warning("⚠️ No data to preview.")
        return
    st.write("### Data Preview")
    st.dataframe(data.head(max_rows))
    st.write(f"Showing {min(max_rows,len(data))} rows out of {len(data)} total")
    st.write(f"Shape: {data.shape}")
    st.write("Columns:", list(data.columns))
    missing = data.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        st.write("### Missing Values")
        st.dataframe(missing)
    else:
        st.write("✅ No missing values detected.")

def check_required_columns(data, required_cols, context=""):
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        st.warning(f"⚠️ Missing required columns for {context}: {', '.join(missing)}")
        return False
    return True

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
    except:
        return series

def plot_sensor_data(data, sensor, highlight_events=False, metric=None, custom_events=None):
    if data is None or sensor not in data.columns or 'Time (sec)' not in data.columns:
        st.warning("⚠️ Sensor or time data missing.")
        return
    time = data['Time (sec)']
    plt.figure(figsize=(12, 5))
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
    if custom_events:
        for event in custom_events:
            if 0 <= event['time'] <= time.max():
                plt.axvline(x=event['time'], color='purple', linestyle=':')
                plt.text(event['time'], data[sensor].min(), event['label'], rotation=90, verticalalignment='bottom', color='purple')
            else:
                st.warning(f"⚠️ Custom event time {event['time']} out of data range.")
    st.pyplot(plt)

def plot_3d_timing_table(data):
    required_cols = ['RPM (RPM)', 'Calculated Load (g/rev)', 'Ignition Timing (°)']
    if not check_required_columns(data, required_cols, "3D Timing Table"):
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
    if not check_required_columns(data, ['RPM (RPM)', 'Boost (psi)'], "Boost vs RPM"):
        return
    boost_smoothed = _safe_savgol_filter(data['Boost (psi)'], window_length, poly_order)
    plt.figure(figsize=(12, 5))
    plt.plot(data['RPM (RPM)'], boost_smoothed, label="Boost (Smoothed)", color='blue')
    plt.xlabel("RPM")
    plt.ylabel("Boost (psi)")
    plt.title("Boost (psi) vs RPM (Smoothed)")
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

def plot_torque_vs_rpm(data, window_length=51, poly_order=3):
    if not check_required_columns(data, ['RPM (RPM)', 'Req Torque (Nm)'], "Torque vs RPM"):
        return
    torque_smoothed = _safe_savgol_filter(data['Req Torque (Nm)'], window_length, poly_order)
    plt.figure(figsize=(12, 5))
    plt.plot(data['RPM (RPM)'], torque_smoothed, label="Torque (Smoothed)", color='orange')
    plt.xlabel("RPM")
    plt.ylabel("Torque (Nm)")
    plt.title("Torque (Nm) vs RPM (Smoothed)")
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

def plot_boost_vs_torque(data, window_length=51, poly_order=3):
    if not check_required_columns(data, ['Boost (psi)', 'Req Torque (Nm)'], "Boost vs Torque"):
        return
    boost_smoothed = _safe_savgol_filter(data['Boost (psi)'], window_length, poly_order)
    torque_smoothed = _safe_savgol_filter(data['Req Torque (Nm)'], window_length, poly_order)
    plt.figure(figsize=(12, 5))
    plt.plot(boost_smoothed, torque_smoothed, label="Boost vs Torque (Smoothed)", color='purple')
    plt.xlabel("Boost (psi)")
    plt.ylabel("Torque (Nm)")
    plt.title("Boost (psi) vs Torque (Nm) (Smoothed)")
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

def estimate_horsepower(data):
    if not check_required_columns(data, ['RPM (RPM)', 'Req Torque (Nm)'], "Horsepower Estimation"):
        return None
    rpm = data['RPM (RPM)']
    torque_nm = data['Req Torque (Nm)']
    torque_lbft = torque_nm * 0.73756
    hp = (torque_lbft * rpm) / 5252
    max_hp = hp.max()
    plt.figure(figsize=(12, 5))
    plt.plot(rpm, hp, label="Estimated HP", color='green')
    plt.xlabel("RPM")
    plt.ylabel("Estimated Horsepower")
    plt.title("Estimated Horsepower vs RPM")
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)
    return max_hp

def estimate_zero_to_sixty(max_hp, weight_lbs, altitude_ft, drivetrain, cylinders):
    # Power loss from altitude ~3% per 1000 ft
    power_at_alt = max_hp * (1 - 0.03 * (altitude_ft / 1000))
    power_at_alt = max(power_at_alt, 1)  # Avoid division by zero or negative power

    weight_power_ratio = weight_lbs / power_at_alt

    # Drivetrain factor: AWD < RWD < FWD in acceleration times (AWD best traction)
    drivetrain_factors = {
        'FWD': 1.10,
        'RWD': 1.00,
        'AWD': 0.88
    }
    drivetrain_factor = drivetrain_factors.get(drivetrain, 1.0)

    # Cylinder factor: fewer cylinders often means less torque/power delivery smoothness
    cylinder_factor = 1 + (8 - cylinders) * 0.03  # 8 cylinders is baseline (factor=1), downscale for fewer

    base_time = 0.023 * (weight_power_ratio ** 1.12)  # base formula from before

    zero_to_sixty = base_time * drivetrain_factor * cylinder_factor

    # Clamp realistic lower limit based on drivetrain, e.g. 3s for AWD and 3.5 for others for this car class
    min_time = 2.7 if drivetrain == "AWD" else 3.3
    zero_to_sixty = max(zero_to_sixty, min_time)

    st.write(f"Estimated 0-60 mph (sec): **{zero_to_sixty:.2f}** (adjusted for weight, altitude, drivetrain & cylinders)")
    return zero_to_sixty

def estimate_quarter_mile(max_hp, weight_lbs, altitude_ft):
    power_at_alt = max_hp * (1 - 0.03 * (altitude_ft / 1000))
    power_at_alt = max(power_at_alt, 1)
    weight_power_ratio = weight_lbs / power_at_alt

    quarter_mile_time = 5.9 * weight_power_ratio ** 0.36
    quarter_mile_time = max(quarter_mile_time, 9.5)
    st.write(f"Estimated 1/4 Mile ET (sec): **{quarter_mile_time:.2f}** (adjusted for weight & altitude)")
    return quarter_mile_time

def plot_knock_afr(data):
    knock_cols = [col for col in data.columns if "knock" in col.lower()]
    afr_cols = [col for col in data.columns if "afr" in col.lower()]
    if not knock_cols or not afr_cols:
        st.warning("⚠️ No knock or AFR columns found.")
        return
    fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    time = data['Time (sec)']
    for col in knock_cols:
        axs[0].plot(time, data[col], label=col)
    axs[0].set_title("Knock Sensor Data")
    axs[0].set_ylabel("Knock")
    axs[0].grid(True)
    axs[0].legend()
    threshold = 1.0
    high_knock = data[knock_cols[0]] > threshold
    if high_knock.any():
        axs[0].scatter(time[high_knock], data[knock_cols[0]][high_knock], color='red', label="Knock > Threshold")
    for col in afr_cols:
        axs[1].plot(time, data[col], label=col)
    axs[1].set_title("Air-Fuel Ratio (AFR)")
    axs[1].set_xlabel("Time (sec)")
    axs[1].set_ylabel("AFR")
    axs[1].grid(True)
    axs[1].legend()
    st.pyplot(fig)

def plot_timing_heatmap(data):
    required_cols = ['RPM (RPM)', 'Calculated Load (g/rev)', 'Ignition Timing (°)']
    if not check_required_columns(data, required_cols, "Ignition Timing Heatmap"):
        return
    try:
        pivot_table = data.pivot_table(index='RPM (RPM)', columns='Calculated Load (g/rev)', values='Ignition Timing (°)', aggfunc='mean')
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_table, cmap="viridis", cbar_kws={'label': 'Ignition Timing (°)'})
        plt.title("Ignition Timing Heatmap (RPM vs Load)")
        plt.xlabel("Load (g/rev)")
        plt.ylabel("RPM")
        st.pyplot(plt)
    except Exception as e:
        st.warning(f"⚠️ Error generating heatmap: {e}")

def plot_compare_logs(data1, data2):
    if data1 is None or data2 is None:
        st.warning("⚠️ Both logs are required for comparison.")
        return
    sensors = [col for col in data1.columns if pd.api.types.is_numeric_dtype(data1[col])]
    if not sensors:
        st.warning("⚠️ No numeric sensors found for comparison.")
        return
    selected_sensor = st.selectbox("Select sensor to compare:", sensors)
    plt.figure(figsize=(12, 5))
    try:
        plt.plot(data1['Time (sec)'], data1[selected_sensor], label="Log 1")
        plt.plot(data2['Time (sec)'], data2[selected_sensor], label="Log 2", alpha=0.7)
        plt.xlabel("Time (sec)")
        plt.ylabel(selected_sensor)
        plt.title(f"Comparison of {selected_sensor}")
        plt.legend()
        plt.grid(True)
        st.pyplot(plt)
    except Exception as e:
        st.warning(f"⚠️ Error plotting comparison: {e}")
