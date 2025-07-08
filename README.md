# Car Log Analyzer Plus - User Manual

Welcome to **Car Log Analyzer Plus**, a Streamlit web app designed for automotive enthusiasts and tuners to analyze vehicle datalogs with ease.

---

## Getting Started

1. **Upload your datalog CSV** file using the upload control on the main page.
2. Optionally upload a **second CSV** to compare two logs side-by-side.
3. Use the **sidebar filters** to narrow your data by RPM, throttle position, and load.
4. Select a **smoothing preset** or customize smoothing parameters for smoother graphs.
5. Add **custom event markers** to annotate key moments in your data.

---

## Features

### Data Overview
- Preview your data with adjustable number of rows.
- Quickly check for missing values.

### Visualizations
- Plot sensor data over time with optional event markers.
- 3D Ignition timing tables.
- Boost vs RPM, Torque vs RPM, Boost vs Torque graphs with smoothing.
- Estimated horsepower calculation from requested torque.
- Knock and AFR data analysis with event highlights.
- Ignition timing heatmap showing RPM vs load.
- Side-by-side comparison of two logs.


### Export
- Download the last displayed plot as a PNG image.

---

## Notes

- Ensure your CSV contains columns like `Time (sec)`, `RPM (RPM)`, `Boost (psi)`, `Req Torque (Nm)`, `Ignition Timing (°)`, `Calculated Load (g/rev)`, and knock/AFR sensors for full functionality.
- Smoothing presets help clean noisy data but can be fine-tuned.
- Use event markers to highlight significant data points or moments in the log.
- Some features require specific columns; the app will warn if missing.

---

## Getting Help

- If you encounter errors or missing data warnings, check your CSV file formatting and column names.
- Feel free to raise issues or suggest improvements on the GitHub repo.

---

## License

This project is licensed under a **restrictive license**. Please see `LICENSE.txt` for details.

---

Enjoy analyzing your car's logs!

---

*Beta Version (Tested for subaru but may work with other vehicles using csvs files through COBB or Open Source software).*

*Horsepower estimation is a very ball-park estimate based on rough calculations and requires the parameters: Time (sec), RPM (RPM), and Req Torque (Nm) to function properly.*
