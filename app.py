import streamlit as st
import pandas as pd
from analyzer import (
    load_data, show_data_overview, plot_sensor_data, plot_3d_timing_table,
    plot_boost_vs_rpm, plot_torque_vs_rpm, estimate_horsepower,
    show_complex_statistics, estimate_quarter_mile, estimate_0_60
)

st.set_page_config(page_title="Car Log Analyzer Plus", layout="wide")

st.title("🚘 Car Log Analyzer Plus")
st.markdown("""
Welcome to the **Car Log Analyzer Plus** — enhanced for tuners and enthusiasts.
Upload your datalog CSV(s) and explore detailed analyses, filtering, event marking, and export capabilities.
""")

vehicle_weight = st.sidebar.number_input("Vehicle Weight (lbs)", 1000, 6000, 3000, 50)
altitude = st.sidebar.number_input("Altitude (ft)", 0, 15000, 0, 100)

uploaded_file = st.file_uploader("📁 Upload your datalog CSV:", type=["csv"])

if uploaded_file:
    data = load_data(uploaded_file)
    if data is not None:
        max_rows = st.slider("Rows to preview:", 5, 100, 20, 5)
        st.header("📊 Data Overview")
        show_data_overview(data, max_rows=max_rows)

        st.header("📈 Visualizations")
        tabs = st.tabs([
            "Sensor over Time", "3D Timing Table", "Boost vs RPM",
            "Torque vs RPM", "Horsepower", "0–60 & 1/4 Mile", "Stats"
        ])

        with tabs[0]:
            sensor = st.selectbox("Sensor to plot:", data.columns)
            plot_sensor_data(data, sensor)

        with tabs[1]:
            plot_3d_timing_table(data)

        with tabs[2]:
            plot_boost_vs_rpm(data)

        with tabs[3]:
            plot_torque_vs_rpm(data)

        with tabs[4]:
            estimate_horsepower(data)

        with tabs[5]:
            estimate_0_60(data, vehicle_weight, altitude)
            estimate_quarter_mile(data, vehicle_weight, altitude)

        with tabs[6]:
            show_complex_statistics(data)

else:
    st.info("⬆️ Upload a file to begin.")
