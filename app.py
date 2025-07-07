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
    plot_knock_afr,
    plot_timing_heatmap,
    export_plot_png,
    filter_data,
    plot_compare_logs,
    calc_wheel_hp_torque,
    estimate_quarter_mile,
)

st.set_page_config(page_title="Car Log Analyzer", layout="wide")

st.title("🚘 Car Log Analyzer Plus")
st.markdown("""
Welcome to the **Car Log Analyzer Plus** — enhanced for tuners and enthusiasts.
Upload your datalog CSV(s) and explore detailed analyses, filtering, event marking, and export capabilities.
""")

# Upload one or two files for comparison
uploaded_file_1 = st.file_uploader("📁 Upload your primary datalog CSV file:", type=["csv"], key="file1")
uploaded_file_2 = st.file_uploader("📁 (Optional) Upload a second CSV to compare:", type=["csv"], key="file2")

if uploaded_file_1:
    data1 = load_data(uploaded_file_1)
    data2 = load_data(uploaded_file_2) if uploaded_file_2 else None

    if data1 is None or (uploaded_file_2 and data2 is None):
        st.error("Failed to load one or both files.")
    else:
        # Controls for filtering data
        st.sidebar.header("Data Filtering")
        rpm_min, rpm_max = st.sidebar.slider("RPM Range", int(data1['RPM (RPM)'].min()), int(data1['RPM (RPM)'].max()), (int(data1['RPM (RPM)'].min()), int(data1['RPM (RPM)'].max())))
        throttle_col = None
        for col in data1.columns:
            if 'throttle' in col.lower():
                throttle_col = col
                break
        if throttle_col:
            thr_min, thr_max = st.sidebar.slider(f"{throttle_col} Range (%)", float(data1[throttle_col].min()), float(data1[throttle_col].max()), (float(data1[throttle_col].min()), float(data1[throttle_col].max())))
        else:
            thr_min, thr_max = None, None

        load_col = None
        for col in data1.columns:
            if 'load' in col.lower():
                load_col = col
                break
        if load_col:
            load_min, load_max = st.sidebar.slider(f"{load_col} Range", float(data1[load_col].min()), float(data1[load_col].max()), (float(data1[load_col].min()), float(data1[load_col].max())))
        else:
            load_min, load_max = None, None

        data1_filtered = filter_data(data1, rpm_min, rpm_max, thr_min, thr_max, load_min, load_max, throttle_col, load_col)
        data2_filtered = filter_data(data2, rpm_min, rpm_max, thr_min, thr_max, load_min, load_max, throttle_col, load_col) if data2 is not None else None

        # Smoothing controls
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
        else:
            window_length = st.sidebar.slider("Window Length", min_value=5, max_value=201, step=2, value=51)
            poly_order = st.sidebar.slider("Polynomial Order", min_value=1, max_value=5, value=3)

        # Highlight event options
        st.sidebar.header("Event Markers")
        highlight_events = st.sidebar.checkbox("Highlight Significant Events?", value=False)
        important_metric = None
        if highlight_events:
            important_metric = st.sidebar.selectbox(
                "Metric to Highlight (if enabled):",
                [col for col in data1.columns if pd.api.types.is_numeric_dtype(data1[col])],
                index=0
            )
        # Custom events input
        st.sidebar.subheader("Custom Events")
        custom_events = []
        event_count = st.sidebar.number_input("Number of custom events", min_value=0, max_value=10, value=0, step=1)
        for i in range(event_count):
            t = st.sidebar.number_input(f"Event {i+1} time (sec)", min_value=0.0, max_value=float(data1['Time (sec)'].max()), value=0.0)
            label = st.sidebar.text_input(f"Event {i+1} label", value="")
            if label.strip() != "":
                custom_events.append({'time': t, 'label': label.strip()})

        # Data preview slider on main page
        max_rows = st.slider(
            "🔍 Number of rows to preview in data overview:",
            min_value=5,
            max_value=100,
            value=20,
            step=5
        )

        st.header("📊 Data Overview - Primary Log")
        show_data_overview(data1_filtered, max_rows=max_rows)

        if data2_filtered is not None:
            st.header("📊 Data Overview - Secondary Log")
            show_data_overview(data2_filtered, max_rows=max_rows)

        st.header("📈 Visualizations")
        tabs = st.tabs([
            "Sensor over Time",
            "3D Timing Table",
            "Boost vs RPM",
            "Torque vs RPM",
            "Boost vs Torque",
            "Estimated HP",
            "Knock & AFR Analysis",
            "Ignition Timing Heatmap",
            "Compare Logs",
            "Quarter Mile Estimation",
            "Statistics",
            "Export"
        ])

        with tabs[0]:
            st.subheader("Sensor Data over Time")
            sensor = st.selectbox("Select sensor to plot:", data1.columns)
            plot_sensor_data(data1_filtered, sensor, highlight_events, important_metric, custom_events)

        with tabs[1]:
            st.subheader("3D Timing Table")
            plot_3d_timing_table(data1_filtered)

        with tabs[2]:
            st.subheader("Boost vs RPM (Smoothed Trend)")
            plot_boost_vs_rpm(data1_filtered, window_length, poly_order)

        with tabs[3]:
            st.subheader("Torque vs RPM (Smoothed Trend)")
            plot_torque_vs_rpm(data1_filtered, window_length, poly_order)

        with tabs[4]:
            st.subheader("Boost vs Torque (Smoothed Trend)")
            plot_boost_vs_torque(data1_filtered, window_length, poly_order)

        with tabs[5]:
            st.subheader("Estimated Horsepower vs RPM")
            estimate_horsepower(data1_filtered)

        with tabs[6]:
            st.subheader("Knock & AFR Analysis")
            plot_knock_afr(data1_filtered)

        with tabs[7]:
            st.subheader("Ignition Timing Heatmap")
            plot_timing_heatmap(data1_filtered)

        with tabs[8]:
            if data2_filtered is not None:
                st.subheader("Compare Logs Overlay")
                plot_compare_logs(data1_filtered, data2_filtered)
            else:
                st.info("Upload a second log to enable comparison.")

        with tabs[9]:
            st.subheader("Quarter Mile Estimation")
            estimate_quarter_mile(data1_filtered)

        with tabs[10]:
            st.subheader("Complex Statistics")
            show_complex_statistics(data1_filtered)

        with tabs[11]:
            st.subheader("Export Plots")
            export_plot_png()

else:
    st.info("⬆️ Please upload at least one datalog CSV file to get started.")

