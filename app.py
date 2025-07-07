import streamlit as st
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

# Upload primary datalog CSV
file1 = st.file_uploader("Upload your primary datalog CSV", type=["csv"])
data1 = load_data(file1) if file1 else None

# Upload second datalog CSV for comparison (optional)
file2 = st.file_uploader("Upload second datalog CSV for comparison (optional)", type=["csv"])
data2 = load_data(file2) if file2 else None

if data1 is not None:

    st.sidebar.header("Vehicle Parameters for Performance Estimates")
    vehicle_weight_lbs = st.sidebar.number_input("Vehicle Weight (lbs)", min_value=1500, max_value=6000, value=3200, step=50)
    altitude_ft = st.sidebar.number_input("Altitude (ft)", min_value=0, max_value=15000, value=5500, step=100)

    st.sidebar.markdown("---")
    st.sidebar.write("**Use this section to adjust filters (optional):**")
    rpm_min, rpm_max = st.sidebar.slider("RPM Range", 0, 9000, (1500, 7000), step=100)
    thr_min, thr_max = st.sidebar.slider("Throttle Position (%) Range", 0, 100, (0, 100))
    load_min, load_max = st.sidebar.slider("Calculated Load (g/rev) Range", 0.0, 2.0, (0.0, 2.0), step=0.01)

    # Detect throttle and load columns (approximate)
    throttle_col = None
    load_col = None
    for col in data1.columns:
        if "throttle" in col.lower():
            throttle_col = col
            break
    for col in data1.columns:
        if "load" in col.lower():
            load_col = col
            break

    # Filter data
    data1_filtered = data1[
        (data1['RPM (RPM)'] >= rpm_min) & (data1['RPM (RPM)'] <= rpm_max)
    ]
    if throttle_col:
        data1_filtered = data1_filtered[
            (data1_filtered[throttle_col] >= thr_min) & (data1_filtered[throttle_col] <= thr_max)
        ]
    if load_col:
        data1_filtered = data1_filtered[
            (data1_filtered[load_col] >= load_min) & (data1_filtered[load_col] <= load_max)
        ]

    st.header("Data Overview & Stats")
    show_data_overview(data1_filtered)

    st.header("Performance Estimates & Graphs")

    max_hp = estimate_horsepower(data1_filtered)

    if max_hp:
        est_0_60 = estimate_zero_to_sixty(max_hp, vehicle_weight_lbs, altitude_ft)
        est_qtr_mile = estimate_quarter_mile(max_hp, vehicle_weight_lbs, altitude_ft)

    st.header("Sensor Plots with Highlights")

    plot_sensor_data(data1_filtered, sensor="Boost (psi)", highlight_events=True, metric="Req Torque (Nm)")
    plot_boost_vs_rpm(data1_filtered)
    plot_torque_vs_rpm(data1_filtered)
    plot_boost_vs_torque(data1_filtered)

    st.header("Ignition Timing and Knock / AFR Analysis")

    plot_3d_timing_table(data1_filtered)
    plot_timing_heatmap(data1_filtered)
    plot_knock_afr(data1_filtered)

    if data2 is not None:
        st.header("Log Comparison")
        plot_compare_logs(data1_filtered, data2)

else:
    st.info("Please upload at least one datalog CSV file to begin analysis.")


