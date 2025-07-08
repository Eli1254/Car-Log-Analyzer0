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
)

st.set_page_config(page_title="Car Log Analyzer Plus", layout="wide")

st.title("Car Log Analyzer Plus")
st.markdown("""
Upload your datalog CSV(s) and explore detailed analyses, filtering, smoothing, event marking, and export capabilities.
""")

# Upload files
uploaded_file_1 = st.file_uploader("📁 Upload primary datalog CSV", type=["csv"], key="file1")
uploaded_file_2 = st.file_uploader("📁 (Optional) Upload secondary CSV for comparison", type=["csv"], key="file2")

if uploaded_file_1:
    data1 = load_data(uploaded_file_1)
    data2 = load_data(uploaded_file_2) if uploaded_file_2 else None

    if data1 is None or (uploaded_file_2 and data2 is None):
        st.error("Failed to load one or both files.")
    else:
        # --- FILTER SLIDERS ---
        st.sidebar.header("Data Filtering")
        rpm_min, rpm_max = st.sidebar.slider(
            "RPM Range",
            int(data1['RPM (RPM)'].min()), int(data1['RPM (RPM)'].max()),
            (int(data1['RPM (RPM)'].min()), int(data1['RPM (RPM)'].max()))
        )

        throttle_col = next((col for col in data1.columns if 'throttle' in col.lower()), None)
        if throttle_col:
            thr_min, thr_max = st.sidebar.slider(
                f"{throttle_col} Range (%)",
                float(data1[throttle_col].min()), float(data1[throttle_col].max()),
                (float(data1[throttle_col].min()), float(data1[throttle_col].max()))
            )
        else:
            thr_min, thr_max = None, None

        load_col = next((col for col in data1.columns if 'load' in col.lower()), None)
        if load_col:
            load_min, load_max = st.sidebar.slider(
                f"{load_col} Range",
                float(data1[load_col].min()), float(data1[load_col].max()),
                (float(data1[load_col].min()), float(data1[load_col].max()))
            )
        else:
            load_min, load_max = None, None

        data1_filtered = filter_data(data1, rpm_min, rpm_max, thr_min, thr_max, load_min, load_max, throttle_col, load_col)
        data2_filtered = filter_data(data2, rpm_min, rpm_max, thr_min, thr_max, load_min, load_max, throttle_col, load_col) if data2 is not None else None

        # --- SMOOTHING CONTROLS ---
        st.sidebar.header("Smoothing Settings")
        smoothing_preset = st.sidebar.selectbox(
            "Smoothing Preset",
            ["Light Smooth", "Medium Smooth", "Heavy Smooth", "Custom"],
            index=1
        )
        if smoothing_preset == "Light Smooth":
            window_length, poly_order = 21, 2
        elif smoothing_preset == "Medium Smooth":
            window_length, poly_order = 51, 3
        elif smoothing_preset == "Heavy Smooth":
            window_length, poly_order = 101, 2
        else:
            window_length = st.sidebar.slider("Window Length", 5, 201, 51, 2)
            poly_order = st.sidebar.slider("Polynomial Order", 1, 5, 3)

        # --- EVENT MARKERS ---
        st.sidebar.header("Event Markers")
        highlight_events = st.sidebar.checkbox("Highlight Significant Events?", value=False)
        important_metric = None
        if highlight_events:
            important_metric = st.sidebar.selectbox(
                "Metric to Highlight",
                [col for col in data1.columns if pd.api.types.is_numeric_dtype(data1[col])],
                index=0
            )

        st.sidebar.subheader("Custom Events")
        custom_events = []
        event_count = st.sidebar.number_input("Number of custom events", 0, 10, 0, 1)
        for i in range(event_count):
            t = st.sidebar.number_input(f"Event {i+1} time (sec)", 0.0, float(data1['Time (sec)'].max()), 0.0)
            label = st.sidebar.text_input(f"Event {i+1} label", "")
            if label.strip():
                custom_events.append({'time': t, 'label': label.strip()})

        # --- MAIN PAGE ---
        max_rows = st.slider("🔍 Rows to preview", 5, 100, 20, 5)

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
            "Statistics",
            "Export"
        ])

        with tabs[0]:
            st.subheader("Sensor Data over Time")
            sensor = st.selectbox("Select sensor:", data1.columns)
            plot_sensor_data(data1_filtered, sensor, highlight_events, important_metric, custom_events)

        with tabs[1]:
            st.subheader("3D Timing Table")
            plot_3d_timing_table(data1_filtered)

        with tabs[2]:
            st.subheader("Boost vs RPM (Smoothed)")
            plot_boost_vs_rpm(data1_filtered, window_length, poly_order)

        with tabs[3]:
            st.subheader("Torque vs RPM (Smoothed)")
            plot_torque_vs_rpm(data1_filtered, window_length, poly_order)

        with tabs[4]:
            st.subheader("Boost vs Torque (Smoothed)")
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
                st.info("Upload second log to enable comparison.")

        with tabs[9]:
            st.subheader("Complex Statistics")
            show_complex_statistics(data1_filtered)

        with tabs[10]:
            st.subheader("Export Plots")
            export_plot_png()

else:
    st.info("⬆️ Upload at least one datalog CSV to get started.")
