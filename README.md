Crop Growth Monitoring System

Overview

The Crop Growth Monitoring System is an IoT-based solution designed to enhance precision agriculture by automating the monitoring and management of crop growth conditions. This project integrates real-time environmental sensing, weather forecasting, and vegetation health analysis to optimize irrigation and improve crop yields. The system is built using an STM32 Nucleo-F446RE microcontroller, ESP32 for internet connectivity, and Python-based GUI for data visualization and analysis.

This project was developed as part of the Microcontroller and Programming course (EI243AI) at RV College of Engineering, Bengaluru, during the academic year 2024-25.

Features





Real-Time Environmental Monitoring: Tracks temperature, humidity, soil moisture, and light intensity using sensors like DHT11, soil moisture sensor, and LDR.



Automated Irrigation Control: Activates a water pump based on soil moisture levels and weather forecasts retrieved via the OpenWeatherMap API.



Vegetation Health Analysis: Computes NDVI (Normalized Difference Vegetation Index) and VARI (Visible Atmospherically Resistant Index) to assess plant health using RGB and NIR images.



Graphical User Interface: A Python-based GUI built with customtkinter displays real-time sensor data, historical trends, and vegetation analysis results.



Data Logging and Communication: Sensor data is transmitted via UART for remote monitoring and stored in CSV files for analysis.

Hardware Components





STM32 Nucleo-F446RE: Core microcontroller for sensor data acquisition and actuator control.



ESP32 NodeMCU: Fetches real-time weather data via Wi-Fi.



DHT11 Sensor: Measures temperature and humidity.



Soil Moisture Sensor: Monitors soil moisture levels (ADC1 Channel 0).



LDR Sensor: Measures light intensity (ADC2 Channel 1).



Water Pump: Controlled via MOSFET for automated irrigation.



Power Supply: Powers all components.

Software Dependencies





Embedded C: For STM32 programming (using STM32CubeMX and Keil uVision).



Python 3.x: For GUI and vegetation index analysis.



Python Libraries:





customtkinter: For the GUI.



matplotlib: For plotting sensor data and vegetation indices.



numpy, pandas, PIL: For image processing and data analysis.



pyserial: For serial communication with the STM32.



OpenWeatherMap API: For weather data integration (requires an API key).