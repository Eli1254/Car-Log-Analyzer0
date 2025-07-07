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
    show_complex_statistics,
)

st.set_page_config(page_title="Car Log Analyzer", layout="wide")

st.title("🚘 Car Log Analyzer")
st.markdown("""
Welcome to the **Car Log Analyzer** — a tool for enthusiasts and tuners to explore, visualize,  
and better understand your car's datalog CSV files.  
Upload your log file and start exploring trends, anomalies, and estimated performance.  
""")

# Upload CSV file
uploaded_file = st.file_uploader("📁 Upload your datalog CSV file here:", type=["csv"])

if uploaded_file:
    data = load_data(uploaded_file)

    if data is not None:
        # Data Preview Row Slider
        max_rows = st.slider(
            "🔍 Number of rows to preview in data overview:",
            min_value=5,
            max_value=100,
            value=20,
            step=5
        )

        st.header("📊 Data Overview")
        show_data_overview(data, max_rows=max_rows)

        st.sidebar.header("Smoothing Settings")
        smoothing_preset = st.sidebar.selectbox(
            "Smoothing Preset",
            ["Light Smooth", "Medium Smooth", "Heavy Smooth", "Custom"],
            index=1
        )

        if smoothing_preset == "Light Smooth":
            window_length = 21
            poly_order = 2
        elif smoothing_preset == "Medium Smooth":
            window_length = 51
            poly_order = 3
        elif smoothing_preset == "Heavy Smooth":
            window_length = 101
            poly_order = 2
        elif smoothing_preset == "Custom":
            window_length = st.sidebar.slider("Window Length", min_value=5, max_value=201, step=2, value=51)
            poly_order = st.sidebar.slider("Polynomial Order", min_value=1, max_value=5, value=3)
        else:
            window_length = 51
            poly_order = 3

        st.sidebar.subheader("Options")
        highlight_events = st.sidebar.checkbox("Highlight Significant Events?", value=False)
        important_metric = st.sidebar.selectbox(
            "Metric to Highlight (if enabled):",
            [col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])],
            index=0
        )

        st.header("📈 Visualizations")

        tabs = st.tabs([
            "Sensor over Time",
            "3D Timing Table",
            "Boost vs RPM",
            "Torque vs RPM",
            "Boost vs Torque",
            "Estimated HP",
            "Statistics"
        ])

        with tabs[0]:
            st.subheader("Sensor Data over Time")
            sensor = st.selectbox("Select sensor to plot:", data.columns)
            plot_sensor_data(data, sensor, highlight_events, important_metric)

        with tabs[1]:
            st.subheader("3D Timing Table")
            plot_3d_timing_table(data)

        with tabs[2]:
            st.subheader("Boost vs RPM (Smoothed Trend)")
            plot_boost_vs_rpm(data, window_length, poly_order)

        with tabs[3]:
            st.subheader("Torque vs RPM (Smoothed Trend)")
            plot_torque_vs_rpm(data, window_length, poly_order)

        with tabs[4]:
            st.subheader("Boost vs Torque (Smoothed Trend)")
            plot_boost_vs_torque(data, window_length, poly_order)

        with tabs[5]:
            st.subheader("Estimated Horsepower vs RPM")
            estimate_horsepower(data)

        with tabs[6]:
            st.subheader("Complex Statistics")
            show_complex_statistics(data)
else:
    st.info("⬆️ Please upload a datalog CSV file to get started.")


