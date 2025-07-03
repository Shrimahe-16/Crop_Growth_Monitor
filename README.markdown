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
- **Weather Data Integration**: ESP32 fetches real-time and forecasted weather data from OpenWeatherMap API, enabling informed irrigation decisions.

## Hardware Components
- **STM32 Nucleo-F446RE**: Core microcontroller for sensor data acquisition and actuator control.
- **ESP32 NodeMCU**: Fetches real-time weather data via Wi-Fi and communicates with STM32 via UART.
- **DHT11 Sensor**: Measures temperature and humidity.
- **Soil Moisture Sensor**: Monitors soil moisture levels (ADC1 Channel 0).
- **LDR Sensor**: Measures light intensity (ADC2 Channel 1).
- **Water Pump**: Controlled via MOSFET for automated irrigation.
- **Power Supply**: Powers all components.

## Software Dependencies
- **Embedded C**: For STM32 programming (using STM32CubeMX and Keil uVision).
- **Arduino Framework**: For ESP32 programming (using Arduino IDE or PlatformIO).
- **Python 3.x**: For GUI and vegetation index analysis.
- **Python Libraries**:
  - `customtkinter`: For the GUI.
  - `matplotlib`: For plotting sensor data and vegetation indices.
  - `numpy`, `pandas`, `PIL`: For image processing and data analysis.
  - `pyserial`: For serial communication with the STM32.
- **OpenWeatherMap API**: For weather data integration (requires an API key).
- **ESP32 Libraries**:
  - `WiFi.h`: For Wi-Fi connectivity.
  - `HTTPClient.h`: For HTTP requests to OpenWeatherMap API.
  - `ArduinoJson.h`: For parsing JSON responses from the API.

## Repository Structure
```
Crop-Growth-Monitoring-System/
├── main.c                        # STM32 firmware for sensor interfacing and control
├── WeatherData_ESP32.ino         # ESP32 firmware for fetching and sending weather data
├── Combined_Analysis_NDVI_NIR.py # Combined NDVI and VARI analysis script
├── NDVI.py                       # NDVI computation and analysis
├── VARI.py                       # VARI computation and analysis
├── dataLogger.py                 # GUI for sensor data visualization and analysis
├── RGB_Images/                   # Directory for RGB images
├── NIR_Images/                   # Directory for NIR images
├── vari_outputs_date/            # Directory for VARI output images
├── ndvi_outputs_date/            # Directory for NDVI output images
├── ndvi_analysis_date.csv        # NDVI analysis results
├── vari_analysis_date.csv        # VARI analysis results
└── README.md                     # Project documentation
```

## Setup Instructions
### Hardware Setup
1. **Connect Sensors and Actuators**:
   - DHT11 to GPIOA Pin 4 (STM32).
   - Soil Moisture Sensor to ADC1 Channel 0 (STM32).
   - LDR Sensor to ADC2 Channel 1 (STM32).
   - Water Pump to GPIOB Pin 0 (via MOSFET, STM32).
   - ESP32 to GPIOC Pin 1 (STM32) for UART communication.
   - ESP32 GPIO 16 (RX), GPIO 17 (TX) for Serial2 communication, and GPIO 0, 2, 4 for RGB LED indicators.
2. **Power Supply**: Ensure all components are powered appropriately.
3. **Program STM32**: Use STM32CubeMX to configure peripherals and Keil uVision to compile and flash `main.c` to the STM32 Nucleo-F446RE.
4. **Program ESP32**: Use Arduino IDE or PlatformIO to compile and flash `ESP32_Code.ino` to the ESP32 NodeMCU. Update Wi-Fi credentials (`ssid`, `password`) and OpenWeatherMap API key (`apiKey`) in the code.

### Software Setup
1. **Install Python Dependencies**:
   ```bash
   pip install customtkinter matplotlib numpy pandas pillow pyserial
   ```
2. **Install ESP32 Dependencies**:
   - Install the ESP32 board support in Arduino IDE or PlatformIO.
   - Install required libraries: `WiFi.h`, `HTTPClient.h`, and `ArduinoJson.h` via the Arduino Library Manager.
3. **Configure OpenWeatherMap API**:
   - Obtain an API key from [OpenWeatherMap](https://openweathermap.org/appid).
   - Update `ESP32_Code.ino` with the API key and Wi-Fi credentials.
4. **Directory Setup**:
   - Create `RGB_Images` and `NIR_Images` folders for image inputs.
   - Ensure write permissions for `vari_outputs_date`, `ndvi_outputs_date`, and CSV files.

### Running the Application
1. **Start the STM32 and ESP32**:
   - Power on the hardware setup and ensure the STM32 is running the `main.c` firmware.
   - Ensure the ESP32 is running the `ESP32_Code.ino` firmware and connected to Wi-Fi (indicated by green LED).
2. **Launch the GUI**:
   ```bash
   python dataLogger.py
   ```
3. **Connect to STM32**:
   - Select the appropriate COM port in the GUI.
   - Click "Connect" to start receiving sensor data.
4. **Perform Vegetation Analysis**:
   - Input paths to RGB and NIR images in the GUI.
   - Click "Analyze" to compute NDVI and VARI and view results.
5. **Weather Data Integration**:
   - The ESP32 fetches current and forecasted weather data when triggered by STM32 (PC1 pin HIGH).
   - Weather data (temperature, humidity, rain status) is sent to the STM32 via UART and displayed in the GUI.

## ESP32 Weather Integration
The `ESP32_Code.ino` script enables the ESP32 to:
- Connect to Wi-Fi using provided credentials.
- Fetch current weather (temperature, humidity, condition) and tomorrow's forecast (average temperature, humidity, condition) from the OpenWeatherMap API.
- Communicate with the STM32 via UART (Serial2, RX=GPIO16, TX=GPIO17).
- Use RGB LEDs to indicate status:
  - Red: Wi-Fi disconnected.
  - Green: Wi-Fi connected.
  - Orange: Successful weather data transmission.
  - Blue: HTTP or JSON parsing error.
- Send a compact key-value message to the STM32 when triggered, e.g., `Now=No_rain,Temp=25.5,Humidity=60,Tom=Rain,Temp=24.0,Humidity=65`.

## Usage
- **Dashboard Tab**: Displays real-time sensor data (temperature, humidity, soil moisture, light) using animated gauges, weather status (from ESP32), and irrigation status.
- **History Tab**: Plots historical sensor data for trend analysis.
- **Raw Data Tab**: Shows raw serial data from the STM32, including weather data from the ESP32.
- **Vegetation Analysis**: Upload RGB and NIR images to compute NDVI and VARI, view heatmaps, and get health insights.

## Results 
- The system accurately monitors environmental parameters and controls irrigation based on soil moisture (<40%) and weather conditions (from ESP32).
- NDVI values >0.6 and VARI values >0.5 indicate healthy vegetation.
- The GUI provides intuitive visualization and insights for crop management, enhanced by real-time weather data from the ESP32.

![alt text](image.png) ![alt text](<Screenshot 2025-07-01 231636.png>) ![alt text](<Screenshot 2025-07-01 231801.png>)


## References
- Chen, H., Yang, Y., et al. (2022). *Design of Crop Growth Environment Monitoring System and部分 Crop Growth Environment Prediction Model*. 2nd Asia-Pacific Conference on Communication, Technology and Computer Science.
- Adafruit Industries. (n.d.). *DHT11, DHT22 and AM2300 Sensors*. [Link](https://www.adafruit.com/product/2300)
- STMicroelectronics. (2024). *STM32F446RE Datasheet*. [Link](https://www.st.com/en/microcontrollers-microprocessors/stm32f446re.html)
- NASA. (n.d.). *Normalized Difference Vegetation Index (NDVI)*. [Link](https://earthobservatory.nasa.gov/Features/MeasuringVegetation/measuring_vegetation_2.php)
- Huete, A. (1988). *A soil-adjusted vegetation index (SAVI)*. Remote Sensing of Environment, 25(3), 295-309.
- OpenWeatherMap API Documentation. [Link](https://openweathermap.org/appid)
