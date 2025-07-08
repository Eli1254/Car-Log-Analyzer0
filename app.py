import streamlit as st
import pandas as pd
from analyzer import *

st.set_page_config(page_title="Car Log Analyzer", layout="wide")

st.title("Car Log Analyzer")

uploaded_file_1 = st.file_uploader("Upload primary log CSV", type=["csv"])
uploaded_file_2 = st.file_uploader("Upload secondary log CSV (optional)", type=["csv"])

if uploaded_file_1:
    data1 = load_data(uploaded_file_1)
    data2 = load_data(uploaded_file_2) if uploaded_file_2 else None

    if data1 is not None:
        weight = st.sidebar.number_input("Vehicle weight (lbs)", 1000, 6000, 3200)
        altitude = st.sidebar.number_input("Altitude (ft)", 0, 15000, 7300)

        st.sidebar.header("Smoothing")
        preset = st.sidebar.selectbox("Preset", ["Light", "Medium", "Heavy", "Custom"], index=1)
        if preset == "Light":
            wl, po = 21, 2
        elif preset == "Medium":
            wl, po = 51, 3
        elif preset == "Heavy":
            wl, po = 101, 2
        else:
            wl = st.sidebar.slider("Window Length", 5, 201, 51, 2)
            po = st.sidebar.slider("Poly Order", 1, 5, 3)

        tabs = st.tabs([
            "Data Overview", "Sensor Over Time", "3D Timing Table",
            "Boost vs RPM", "Torque vs RPM", "Estimated Horsepower",
            "0-60 & ¼‑mile", "Knock & AFR", "Timing Heatmap",
            "Compare Logs", "Export Plot"
        ])

        with tabs[0]:
            max_rows = st.slider(
                "Rows to display in data preview",
                min_value=5,
                max_value=int(min(100, data1.shape[0])),
                value=20,
                step=5
            )
            show_data_overview(data1, max_rows)

        with tabs[1]:
            sensor = st.selectbox("Sensor", data1.columns)
            plot_sensor_data(data1, sensor)

        with tabs[2]:
            plot_3d_timing_table(data1)

        with tabs[3]:
            plot_boost_vs_rpm(data1, wl, po)

        with tabs[4]:
            plot_torque_vs_rpm(data1, wl, po)

        with tabs[5]:
            data1 = estimate_horsepower(data1)

        with tabs[6]:
            if 'Estimated Horsepower' not in data1.columns:
                data1 = estimate_horsepower(data1)
            max_hp = data1['Estimated Horsepower'].max()
            t_0_60 = estimate_zero_to_sixty(weight, altitude, max_hp)
            et_1_4 = estimate_quarter_mile(weight, altitude, max_hp)
            st.metric("0–60 mph", f"{t_0_60:.2f} sec")
            st.metric("¼‑mile ET", f"{et_1_4:.2f} sec")

        with tabs[7]:
            plot_knock_afr(data1)

        with tabs[8]:
            plot_timing_heatmap(data1)

        with tabs[9]:
            if data2 is not None:
                sensor_cmp = st.selectbox("Sensor to compare", data1.columns)
                plot_compare_logs(data1, data2, sensor_cmp)
            else:
                st.info("Upload a secondary log to enable comparison.")

        with tabs[10]:
            export_plot_png()
    else:
        st.error("Failed to load primary log.")
else:
    st.info("Upload a CSV to start.")
