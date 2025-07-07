import streamlit as st
import pandas as pd
from analyzer import CarLogAnalyzer

st.set_page_config(page_title="Car Log Analyzer", layout="wide")

st.title("Car Log Analyzer")
st.markdown("Upload your CSV log file and visualize your car's performance data.")

uploaded_file = st.file_uploader("Upload CSV file", type="csv")

if uploaded_file:
    try:
        data = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
        st.success("✅ File loaded successfully.")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()

    analyzer = CarLogAnalyzer(data)

    # 📊 Data Overview
    st.header("📊 Data Overview")

    st.subheader("Preview Data")
    num_rows = st.slider("Number of rows to preview:", 5, min(500, len(data)), 10)
    st.dataframe(data.head(num_rows))

    st.subheader("Top Significant Events")
    important_metric = st.selectbox(
        "Select metric to sort by:",
        [col for col in data.columns if data[col].dtype != 'O'],
        index=0
    )
    top_n = st.slider("How many top events to show?", 1, 50, 10)
    st.dataframe(data.sort_values(by=important_metric, ascending=False).head(top_n))

    st.sidebar.header("Plot Options")

    plot_type = st.sidebar.selectbox(
        "Choose plot type",
        [
            "Sensor over Time",
            "Estimated Horsepower",
            "Boost vs RPM"
        ]
    )

    highlight_events = st.sidebar.checkbox("Highlight significant events?", value=False)

    if highlight_events:
        # Pick top 3 events for the selected metric
        events_df = data.sort_values(by=important_metric, ascending=False).head(3)
        events = []
        for _, row in events_df.iterrows():
            events.append({"time": row["Time (sec)"], "label": f"{important_metric}: {row[important_metric]:.1f}"})
    else:
        events = None

    if plot_type == "Sensor over Time":
        sensor = st.sidebar.selectbox("Select sensor", data.columns)
        if st.sidebar.button("Generate Plot"):
            try:
                buf = analyzer.plot_sensor(sensor, events)
                st.image(buf, caption=f"{sensor} over Time")
            except Exception as e:
                st.error(str(e))

    elif plot_type == "Estimated Horsepower":
        if st.sidebar.button("Generate HP Estimate Plot"):
            try:
                buf = analyzer.estimate_horsepower()
                st.image(buf, caption="Estimated HP vs RPM")
                st.download_button(
                    label="Download data with HP (CSV)",
                    data=analyzer.data.to_csv(index=False).encode(),
                    file_name="data_with_hp.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(str(e))

    elif plot_type == "Boost vs RPM":
        window_length = st.sidebar.slider("Smoothing Window", 5, 101, 51, step=2)
        polyorder = st.sidebar.slider("Polynomial Order", 1, 5, 3)
        if st.sidebar.button("Generate Boost vs RPM Plot"):
            try:
                buf = analyzer.plot_boost_vs_rpm(window_length, polyorder)
                st.image(buf, caption="Boost vs RPM (smoothed)")
            except Exception as e:
                st.error(str(e))

