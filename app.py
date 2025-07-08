import streamlit as st
import pandas as pd
from analyzer import (
    load_data,
    show_data_overview,
    plot_sensor_data,
    plot_3d_timing_table,
    plot_boost_vs_rpm,
    plot_torque_vs_rpm,
    plot_boost_vs_torque,
    estimate_horsepower,
    estimate_zero_to_sixty,
    estimate_quarter_mile,
    plot_knock_afr,
    plot_timing_heatmap,
    plot_compare_logs,
)

st.set_page_config(page_title="Car Log Analyzer", layout="wide")

st.title("🚗 Car Log Analyzer")

file1 = st.file_uploader("Upload your primary datalog CSV", type=["csv"])
file2 = st.file_uploader("Upload second datalog CSV for comparison (optional)", type=["csv"])

data1 = load_data(file1) if file1 else None
data2 = load_data(file2) if file2 else None

if data1 is not None:

    st.sidebar.header("Vehicle & Data Filters")

    weight = st.sidebar.number_input("Vehicle Weight (lbs)", min_value=1500, max_value=6000, value=3200, step=50)
    altitude = st.sidebar.number_input("Altitude (ft)", min_value=0, max_value=15000, value=7300, step=100)

    drivetrain = st.sidebar.selectbox("Drivetrain", options=["AWD", "RWD", "FWD"], index=0)
    cylinders = st.sidebar.slider("Number of Cylinders", min_value=3, max_value=12, value=4, step=1)

    st.sidebar.markdown("---")

    # Data overview rows slider
    max_rows = len(data1)
    preview_rows = st.sidebar.slider("Rows to show in Data Overview", min_value=5, max_value=max_rows, value=min(20, max_rows), step=5)

    rpm_min, rpm_max = st.sidebar.slider("RPM Range", int(data1['RPM (RPM)'].min()), int(data1['RPM (RPM)'].max()), (int(data1['RPM (RPM)'].min()), int(data1['RPM (RPM)'].max())), step=100)
    throttle_col = next((c for c in data1.columns if "throttle" in c.lower()), None)
    load_col = next((c for c in data1.columns if "load" in c.lower()), None)
    
    if throttle_col:
        thr_min, thr_max = st.sidebar.slider(f"{throttle_col} Range", float(data1[throttle_col].min()), float(data1[throttle_col].max()), (float(data1[throttle_col].min()), float(data1[throttle_col].max())))
    else:
        thr_min, thr_max = None, None
    if load_col:
        load_min, load_max = st.sidebar.slider(f"{load_col} Range", float(data1[load_col].min()), float(data1[load_col].max()), (float(data1[load_col].min()), float(data1[load_col].max())))
    else:
        load_min, load_max = None, None

    # Filter data
    data1_filtered = data1[
        (data1['RPM (RPM)'] >= rpm_min) & (data1['RPM (RPM)'] <= rpm_max)
    ]
    if throttle_col and thr_min is not None and thr_max is not None:
        data1_filtered = data1_filtered[(data1_filtered[throttle_col] >= thr_min) & (data1_filtered[throttle_col] <= thr_max)]
    if load_col and load_min is not None and load_max is not None:
        data1_filtered = data1_filtered[(data1_filtered[load_col] >= load_min) & (data1_filtered[load_col] <= load_max)]

    if data2 is not None:
        data2_filtered = data2[
            (data2['RPM (RPM)'] >= rpm_min) & (data2['RPM (RPM)'] <= rpm_max)
        ]
        if throttle_col and thr_min is not None and thr_max is not None:
            data2_filtered = data2_filtered[(data2_filtered[throttle_col] >= thr_min) & (data2_filtered[throttle_col] <= thr_max)]
        if load_col and load_min is not None and load_max is not None:
            data2_filtered = data2_filtered[(data2_filtered[load_col] >= load_min) & (data2_filtered[load_col] <= load_max)]
    else:
        data2_filtered = None

    st.sidebar.markdown("---")
    st.sidebar.header("Select Visualizations to Display")
    options = st.sidebar.multiselect(
        "Choose graphs and analyses:",
        [
            "Data Overview",
            "Sensor Data Over Time",
            "3D Timing Table",
            "Boost vs RPM",
            "Torque vs RPM",
            "Boost vs Torque",
            "Estimated Horsepower",
            "0-60 Estimate",
            "1/4 Mile Estimate",
            "Knock & AFR Analysis",
            "Ignition Timing Heatmap",
            "Log Comparison",
        ],
        default=["Data Overview", "Estimated Horsepower"]
    )

    if "Data Overview" in options:
        st.header("Data Overview")
        show_data_overview(data1_filtered, max_rows=preview_rows)

    if "Sensor Data Over Time" in options:
        st.header("Sensor Data Over Time")
        # Allow user to pick sensor from numeric columns
        numeric_cols = [col for col in data1_filtered.columns if pd.api.types.is_numeric_dtype(data1_filtered[col])]
        sensor = st.selectbox("Select sensor to plot", numeric_cols)
        highlight = st.checkbox("Highlight top 3 peaks in sensor", value=False)
        metric = None
        if highlight:
            metric = st.selectbox("Select metric to highlight peaks", numeric_cols, index=0)
        plot_sensor_data(data1_filtered, sensor, highlight_events=highlight, metric=metric)

    if "3D Timing Table" in options:
        st.header("3D Timing Table")
        plot_3d_timing_table(data1_filtered)

    if "Boost vs RPM" in options:
        st.header("Boost vs RPM")
        plot_boost_vs_rpm(data1_filtered)

    if "Torque vs RPM" in options:
        st.header("Torque vs RPM")
        plot_torque_vs_rpm(data1_filtered)

    if "Boost vs Torque" in options:
        st.header("Boost vs Torque")
        plot_boost_vs_torque(data1_filtered)

    max_hp = None
    if "Estimated Horsepower" in options or "0-60 Estimate" in options or "1/4 Mile Estimate" in options:
        max_hp = estimate_horsepower(data1_filtered)

    if "0-60 Estimate" in options and max_hp is not None:
        st.header("0-60 mph Estimate")
        estimate_zero_to_sixty(max_hp, weight, altitude, drivetrain, cylinders)

    if "1/4 Mile Estimate" in options and max_hp is not None:
        st.header("1/4 Mile Estimate")
        estimate_quarter_mile(max_hp, weight, altitude)

    if "Knock & AFR Analysis" in options:
        st.header("Knock & AFR Analysis")
        plot_knock_afr(data1_filtered)

    if "Ignition Timing Heatmap" in options:
        st.header("Ignition Timing Heatmap")
        plot_timing_heatmap(data1_filtered)

    if "Log Comparison" in options and data2_filtered is not None:
        st.header("Log Comparison")
        plot_compare_logs(data1_filtered, data2_filtered)

else:
    st.info("Please upload at least one datalog CSV file to start analysis.")
