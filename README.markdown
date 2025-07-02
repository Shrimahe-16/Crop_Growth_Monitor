# Crop Growth Monitoring System

## Overview
The **Crop Growth Monitoring System** is an IoT-based solution designed to enhance precision agriculture by automating the monitoring and management of crop growth conditions. This project integrates real-time environmental sensing, weather forecasting, and vegetation health analysis to optimize irrigation and improve crop yields. The system is built using an STM32 Nucleo-F446RE microcontroller, ESP32 for internet connectivity, and Python-based GUI for data visualization and analysis.

This project was developed as part of the **Microcontroller and Programming** course (EI243AI) at RV College of Engineering, Bengaluru, during the academic year 2024-25.

## Features
- **Real-Time Environmental Monitoring**: Tracks temperature, humidity, soil moisture, and light intensity using sensors like DHT11, soil moisture sensor, and LDR.
- **Automated Irrigation Control**: Activates a water pump based on soil moisture levels and weather forecasts retrieved via the OpenWeatherMap API.
- **Vegetation Health Analysis**: Computes **NDVI** (Normalized Difference Vegetation Index) and **VARI** (Visible Atmospherically Resistant Index) to assess plant health using RGB and NIR images.
- **Graphical User Interface**: A Python-based GUI built with `customtkinter` displays real-time sensor data, historical trends, and vegetation analysis results.
- **Data Logging and Communication**: Sensor data is transmitted via UART for remote monitoring and stored in CSV files for analysis.

## Hardware Components
- **STM32 Nucleo-F446RE**: Core microcontroller for sensor data acquisition and actuator control.
- **ESP32 NodeMCU**: Fetches real-time weather data via Wi-Fi.
- **DHT11 Sensor**: Measures temperature and humidity.
- **Soil Moisture Sensor**: Monitors soil moisture levels (ADC1 Channel 0).
- **LDR Sensor**: Measures light intensity (ADC2 Channel 1).
- **Water Pump**: Controlled via MOSFET for automated irrigation.
- **Power Supply**: Powers all components.

## Software Dependencies
- **Embedded C**: For STM32 programming (using STM32CubeMX and Keil uVision).
- **Python 3.x**: For GUI and vegetation index analysis.
- **Python Libraries**:
  - `customtkinter`: For the GUI.
  - `matplotlib`: For plotting sensor data and vegetation indices.
  - `numpy`, `pandas`, `PIL`: For image processing and data analysis.
  - `pyserial`: For serial communication with the STM32.
- **OpenWeatherMap API**: For weather data integration (requires an API key).

## Repository Structure
```
Crop-Growth-Monitoring-System/
├── main.c                    # STM32 firmware for sensor interfacing and control
├── Combined_Analysis_NDVI_NIR.py # Combined NDVI and VARI analysis script
├── NDVI.py                   # NDVI computation and analysis
├── VARI.py                   # VARI computation and analysis
├── display_final.py           # GUI for sensor data visualization and analysis
├── RGB_Images/               # Directory for RGB images
├── NIR_Images/               # Directory for NIR images
├── vari_outputs_date/        # Directory for VARI output images
├── ndvi_outputs_date/        # Directory for NDVI output images
├── ndvi_analysis_date.csv    # NDVI analysis results
├── vari_analysis_date.csv    # VARI analysis results
└── README.md                 # Project documentation
```

## Setup Instructions
### Hardware Setup
1. **Connect Sensors and Actuators**:
   - DHT11 to GPIOA Pin 4.
   - Soil Moisture Sensor to ADC1 Channel 0.
   - LDR Sensor to ADC2 Channel 1.
   - Water Pump to GPIOB Pin 0 (via MOSFET).
   - ESP32 to GPIOC Pin 1 for weather data communication.
2. **Power Supply**: Ensure all components are powered appropriately.
3. **Program STM32**: Use STM32CubeMX to configure peripherals and Keil uVision to compile and flash `main.c` to the STM32 Nucleo-F446RE.

### Software Setup
1. **Install Python Dependencies**:
   ```bash
   pip install customtkinter matplotlib numpy pandas pillow pyserial
   ```
2. **Configure OpenWeatherMap API**:
   - Obtain an API key from [OpenWeatherMap](https://openweathermap.org/appid).
   - Update the ESP32 firmware (not included in this repository) to include the API key and Wi-Fi credentials.
3. **Directory Setup**:
   - Create `RGB_Images` and `NIR_Images` folders for image inputs.
   - Ensure write permissions for `vari_outputs_date`, `ndvi_outputs_date`, and CSV files.

### Running the Application
1. **Start the STM32**: Power on the hardware setup and ensure the STM32 is running the `main.c` firmware.
2. **Launch the GUI**:
   ```bash
   python display_final.py
   ```
3. **Connect to STM32**:
   - Select the appropriate COM port in the GUI.
   - Click "Connect" to start receiving sensor data.
4. **Perform Vegetation Analysis**:
   - Input paths to RGB and NIR images in the GUI.
   - Click "Analyze" to compute NDVI and VARI and view results.

## Usage
- **Dashboard Tab**: Displays real-time sensor data (temperature, humidity, soil moisture, light) using animated gauges, weather status, and irrigation status.
- **History Tab**: Plots historical sensor data for trend analysis.
- **Raw Data Tab**: Shows raw serial data from the STM32.
- **Vegetation Analysis**: Upload RGB and NIR images to compute NDVI and VARI, view heatmaps, and get health insights.

## Results
- The system accurately monitors environmental parameters and controls irrigation based on soil moisture (<40%) and weather conditions.
- NDVI values >0.6 and VARI values >0.5 indicate healthy vegetation.
- The GUI provides intuitive visualization and insights for crop management.

## Future Enhancements
- Add soil pH sensing for nutrient monitoring.
- Implement wireless communication (Wi-Fi/Bluetooth) for remote access.
- Develop a mobile/web dashboard for live data visualization.
- Integrate cloud storage for data logging and predictive analytics.
- Optimize energy consumption with low-power modes.

## References
- Chen, H., Yang, Y., et al. (2022). *Design of Crop Growth Environment Monitoring System and Research on Crop Growth Environment Prediction Model*. 2nd Asia-Pacific Conference on Communication, Technology and Computer Science.
- Adafruit Industries. (n.d.). *DHT11, DHT22 and AM2300 Sensors*. [Link](https://www.adafruit.com/product/2300)
- STMicroelectronics. (2024). *STM32F446RE Datasheet*. [Link](https://www.st.com/en/microcontrollers-microprocessors/stm32f446re.html)
- NASA. (n.d.). *Normalized Difference Vegetation Index (NDVI)*. [Link](https://earthobservatory.nasa.gov/Features/MeasuringVegetation/measuring_vegetation_2.php)
- Huete, A. (1988). *A soil-adjusted vegetation index (SAVI)*. Remote Sensing of Environment, 25(3), 295-309.
- OpenWeatherMap API Documentation. [Link](https://openweathermap.org/appid)

## Contributors
- **Sathvik Madagi** (IRV23EC133)
- **Shreevathsa Kuthethoor** (IRV23EC140)
- **Shridattha M Hebbar** (IRV23EC143)

## License
This project is licensed under the MIT License.