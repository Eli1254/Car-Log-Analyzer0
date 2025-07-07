import streamlit as st
import pandas as pd

from analyzer import (
    load_data,
    plot_sensor_data,
    show_complex_statistics,
    filter_by_time_range,
    plot_boost_vs_rpm,
    plot_torque_vs_rpm,
    plot_boost_vs_torque,
    estimate_horsepower_from_torque,
    plot_3d_timing_table,
    plot_with_events,
    estimate_quarter_mile,
    estimate_0_60_time
)

st.set_page_config(page_title="Car Log Analyzer", layout="wide")

st.title("🚗 Car Log Analyzer")
st.markdown("""
Welcome to **Car Log Analyzer** — a powerful yet easy-to-use tool for automotive enthusiasts and tuners!  
Upload one or two log files (`.csv`) to explore your car’s performance metrics, visualize data, and estimate key times.
""")

# --- Sidebar: user inputs
st.sidebar.header("Settings")
vehicle_weight = st.sidebar.number_input("Vehicle Weight (lbs)", 1000, 10000, 3000, 50)
altitude = st.sidebar.number_input("Altitude (ft)", 0, 15000, 0, 100)

smoothing_window = st.sidebar.slider("Smoothing Window Length", min_value=5, max_value=101, step=2, value=51)
poly_order = st.sidebar.slider("Smoothing Polynomial Order", min_value=1, max_value=5, value=3)

rows_preview = st.sidebar.slider("Rows to preview", min_value=5, max_value=50, value=10)

# --- File upload(s)
st.subheader("Upload Log File(s)")
uploaded_file1 = st.file_uploader("Upload your primary log CSV", type=["csv"], key="file1")
uploaded_file2 = st.file_uploader("Optional: upload second log for comparison", type=["csv"], key="file2")

data1 = load_data(uploaded_file1) if uploaded_file1 else None
data2 = load_data(uploaded_file2) if uploaded_file2 else None

if data1 is None:
    st.info("👆 Please upload at least one log file to get started.")
    st.stop()

# --- Data preview
st.subheader("📊 Data Preview")
st.write("Primary Log Data:")
st.dataframe(data1.head(rows_preview))

if data2 is not None:
    st.write("Comparison Log Data:")
    st.dataframe(data2.head(rows_preview))

# --- Mode selector
analysis_mode = st.selectbox(
    "Select Analysis Mode:",
    [
        "Sensor Data Visualization",
        "3D Timing Table",
        "Boost vs RPM",
        "Torque vs RPM",
        "Boost vs Torque",
        "Estimate Horsepower",
        "Estimate 1/4 Mile ET",
        "Estimate 0-60 mph",
        "Complex Statistics",
        "Filter by Time Range",
        "Plot Sensor Data with Event Markers",
        "Compare Two Logs"
    ]
)

# --- Perform selected analysis
if analysis_mode == "Sensor Data Visualization":
    sensor = st.selectbox("Select sensor", data1.columns)
    plot_sensor_data(data1, sensor)

elif analysis_mode == "3D Timing Table":
    plot_3d_timing_table(data1)

elif analysis_mode == "Boost vs RPM":
    plot_boost_vs_rpm(data1, smoothing_window, poly_order)

elif analysis_mode == "Torque vs RPM":
    plot_torque_vs_rpm(data1, smoothing_window, poly_order)

elif analysis_mode == "Boost vs Torque":
    plot_boost_vs_torque(data1, smoothing_window, poly_order)

elif analysis_mode == "Estimate Horsepower":
    data1 = estimate_horsepower_from_torque(data1)
    if "Estimated Horsepower" in data1.columns:
        st.write(data1[["RPM (RPM)", "Estimated Horsepower"]].head())

elif analysis_mode == "Estimate 1/4 Mile ET":
    if "Estimated Horsepower" not in data1.columns:
        st.warning("Please run 'Estimate Horsepower' first.")
    else:
        estimate_quarter_mile(data1, vehicle_weight, altitude)

elif analysis_mode == "Estimate 0-60 mph":
    if "Estimated Horsepower" not in data1.columns:
        st.warning("Please run 'Estimate Horsepower' first.")
    else:
        estimate_0_60_time(data1, vehicle_weight, altitude)

elif analysis_mode == "Complex Statistics":
    show_complex_statistics(data1)

elif analysis_mode == "Filter by Time Range":
    start = st.number_input("Start Time (sec):", value=0.0)
    end = st.number_input("End Time (sec):", value=float(data1['Time (sec)'].max()))
    filtered = filter_by_time_range(data1, start, end)
    st.dataframe(filtered.head(rows_preview))

elif analysis_mode == "Plot Sensor Data with Event Markers":
    sensor = st.selectbox("Select sensor", data1.columns)
    events = [
        {'time': 50, 'label': 'Max RPM'},
        {'time': 100, 'label': 'Overheating'}
    ]
    plot_with_events(data1, sensor, events)

elif analysis_mode == "Compare Two Logs":
    if data2 is None:
        st.warning("Please upload a second log file.")
    else:
        sensor = st.selectbox("Select sensor to compare", data1.columns)
        st.line_chart(pd.DataFrame({
            "Log 1": data1[sensor],
            "Log 2": data2[sensor]
        }))
