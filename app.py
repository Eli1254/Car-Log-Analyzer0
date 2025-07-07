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
    estimate_0_60_time,
)

st.set_page_config(page_title="Car Log Analyzer", layout="wide")

st.title("🚗 Car Log Analyzer")
st.markdown("""
Analyze and visualize your car's performance logs.  
Upload a `.csv` log file and explore a variety of graphs, statistics, and performance estimates.
""")

# Upload file
uploaded_file = st.file_uploader("Upload your car log CSV", type=["csv"])

data = None
if uploaded_file:
    data = load_data(uploaded_file)

if data is not None:
    st.subheader("📊 Data Preview")
    preview_rows = st.slider(
        "Select number of rows to preview:",
        min_value=5, max_value=min(len(data), 100), value=10, step=5
    )
    st.dataframe(data.head(preview_rows))

    # Sidebar for inputs
    st.sidebar.header("Vehicle & Environment Inputs")

    vehicle_weight = st.sidebar.number_input(
        "Vehicle Weight (lbs)",
        min_value=1000, max_value=10000, value=3000, step=10,
        help="Weight of your car including driver."
    )

    altitude = st.sidebar.number_input(
        "Altitude (feet)",
        min_value=0, max_value=15000, value=0, step=100,
        help="Approximate elevation above sea level."
    )

    # User actions
    st.subheader("📈 Visualization & Analysis")

    option = st.selectbox(
        "Choose an analysis option:",
        [
            "Sensor Data Visualization",
            "3D Timing Table",
            "Boost vs RPM",
            "Torque vs RPM",
            "Boost vs Required Torque",
            "Estimate Horsepower",
            "Show Complex Statistics",
            "Filter Data by Time Range",
            "Plot Sensor Data with Event Markers",
            "Estimate 1/4 Mile ET",
            "Estimate 0-60 mph Time",
        ]
    )

    if option == "Sensor Data Visualization":
        sensor_name = st.selectbox("Select sensor to visualize", data.columns)
        plot_sensor_data(data, sensor_name)

    elif option == "3D Timing Table":
        plot_3d_timing_table(data)

    elif option == "Boost vs RPM":
        plot_boost_vs_rpm(data)

    elif option == "Torque vs RPM":
        plot_torque_vs_rpm(data)

    elif option == "Boost vs Required Torque":
        plot_boost_vs_torque(data)

    elif option == "Estimate Horsepower":
        data = estimate_horsepower_from_torque(data)
        if 'Estimated Horsepower' in data.columns:
            st.dataframe(data[['RPM (RPM)', 'Estimated Horsepower']].head())

    elif option == "Show Complex Statistics":
        show_complex_statistics(data)

    elif option == "Filter Data by Time Range":
        start_time = st.number_input("Start Time (sec):", value=0.0)
        end_time = st.number_input("End Time (sec):", value=float(data['Time (sec)'].max()))
        filtered_data = filter_by_time_range(data, start_time, end_time)
        st.dataframe(filtered_data)

    elif option == "Plot Sensor Data with Event Markers":
        sensor_name = st.selectbox("Select sensor for event markers", data.columns)
        events = [
            {'time': 50, 'label': 'Max RPM'},
            {'time': 100, 'label': 'Overheating'}
        ]
        plot_with_events(data, sensor_name, events)

    elif option == "Estimate 1/4 Mile ET":
        estimate_quarter_mile(data, vehicle_weight, altitude)

    elif option == "Estimate 0-60 mph Time":
        estimate_0_60_time(data, vehicle_weight, altitude)

else:
    st.info("👆 Please upload a CSV file to get started.")

