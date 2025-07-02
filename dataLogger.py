import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
import serial.tools.list_ports
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import numpy as np
import pandas as pd
import os
from datetime import datetime
import time
from Combined_Analysis_NDVI_NIR import combined_ndvi_vari_analysis

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

DARK_BG = "#021403"
DARK_CARD = "#354735"
ACCENT_GREEN = "#4caf50"
ACCENT_YELLOW = "#ffc107"
ACCENT_RED = "#4f0c0c"
ACCENT_BLUE = "#2196f3"
TEXT_WHITE = "#ffffff"
GRADIENT_CARD = "#2a3a31"

class AnimatedCircularGauge(tk.Canvas):
    def __init__(self, parent, size=200, min_value=0, max_value=100, label="", unit="", **kwargs):
        super().__init__(parent, width=size, height=size, bg=DARK_BG, highlightthickness=0, **kwargs)
        self.size = size
        self.min_value = min_value
        self.max_value = max_value
        self.label = label
        self.unit = unit
        self.value = min_value
        self.target_value = min_value
        self.animation_speed = 0.1
        # Colors
        self.bg_color = DARK_CARD
        self.fg_color = ACCENT_GREEN
        self.text_color = TEXT_WHITE

        self.after(10, self.animate_value)

    def set_value(self, value):
        self.target_value = max(self.min_value, min(self.max_value, value))

    def animate_value(self):
        if abs(self.value - self.target_value) > 0.1:
            self.value += (self.target_value - self.value) * self.animation_speed
            self.redraw()
        elif self.value != self.target_value:
            self.value = self.target_value
            self.redraw()

        self.after(16, self.animate_value)

    def redraw(self):
        self.delete("all")

        center_x = self.size // 2
        center_y = self.size // 2
        radius = min(center_x, center_y) - 15

        self.create_oval(center_x - radius, center_y - radius,
                         center_x + radius, center_y + radius,
                         outline='#2a3a31', width=15, fill=self.bg_color)

        start_angle = 90
        extent = -270 * (self.value - self.min_value) / (self.max_value - self.min_value)

        for i in range(15):
            offset = i
            self.create_arc(center_x - radius + offset, center_y - radius + offset,
                            center_x + radius - offset, center_y + radius - offset,
                            start=start_angle, extent=extent,
                            outline=self.fg_color, width=1, style="arc")

        value_text = f"{int(self.value) if self.value.is_integer() else round(self.value, 1)}"
        self.create_text(center_x, center_y - 15,
                         text=value_text, fill=self.text_color,
                         font=('Arial', 24, 'bold'))

        self.create_text(center_x, center_y + 15,
                         text=self.unit, fill=self.text_color,
                         font=('Arial', 14))

        self.create_text(center_x, center_y + radius - 10,
                         text=self.label, fill=self.text_color,
                         font=('Arial', 12, 'bold'))


class VegetationAnalysisGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🌱 Crop Growth Monitoring System")

        try:
            self.iconbitmap("plant_icon.ico")
        except:
            pass

        # Initialize variables
        self.serial_connection = None
        self.serial_thread = None
        self.running = True
        self.sensor_data = {
            "temperature": 0.0,
            "humidity": 0.0,
            "moisture": 0.0,
            "light": 0.0,
            "temp_status": "❌",
            "moisture_status": "❌",
            "light_status": "❌",
            "weather": "unknown",
            "motor": "OFF"
        }
        self.sensor_history = pd.DataFrame(columns=["timestamp", "temperature", "humidity",
                                                    "moisture", "light"])
        self.analysis_canvas = None
        self.go_back_button = None
        self.inference_frame = None
        self.analysis_container = None
        self.buttons_frame = None
        self.background_label = None  # For background image

        self.configure(fg_color=DARK_BG)
        self.setup_ui()
        self.state('zoomed')
        self.toggle_zoomed()

        self.bind("<Escape>", self.toggle_zoomed)
        self.bind("<Configure>", self.resize_background)  # Resize background on window resize

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def resize_background(self, event=None):
        if self.background_label and os.path.exists(self.bg_image_path):
            # Get current window size
            win_width = self.winfo_width()
            win_height = self.winfo_height()

            # Load and resize image
            try:
                image = Image.open(self.bg_image_path)
                image = image.resize((win_width, win_height), Image.Resampling.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(image)
                self.background_label.configure(image=self.bg_image)
            except Exception as e:
                print(f"Error loading background image: {e}")

    def toggle_zoomed(self, event=None):
        if self.state() == 'zoomed':
            self.state('normal')
            self.geometry("1200x800")
        else:
            self.state('zoomed')
        self.resize_background()
        return "break"

    def setup_ui(self):
        # Configure grid layout - 2 columns, 3 rows
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)  # For title
        self.grid_rowconfigure(1, weight=0)  # For buttons
        self.grid_rowconfigure(2, weight=1)  # For main content

        # Add title
        title_label = ctk.CTkLabel(
            self,
            text="Crop Growth Monitoring System",
            font=("Helvetica", 24, "bold"),
            text_color=ACCENT_GREEN
        )
        title_label.grid(row=1, column=0, columnspan=2, padx=75, pady=(10,0), sticky="w")

        self.exit_button = ctk.CTkButton(
            self,
            text="Exit",
            command=self.on_closing,
            fg_color=ACCENT_RED,
            hover_color="#b71c1c",
            width=100
        )
        self.exit_button.grid(row=1, column=1, sticky="ne", padx=(5, 10), pady=5)

        # Create frames with proper expansion
        self.left_frame = ctk.CTkFrame(self, fg_color=DARK_BG)
        self.left_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(1, weight=1)

        self.center_frame = ctk.CTkFrame(self, fg_color=DARK_BG)
        self.center_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        self.center_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(1, weight=1)
        # Setup UI components
        self.create_serial_controls()
        self.create_sensor_display()
        self.create_analysis_display()

        self.update_sensor_display()

    def create_serial_controls(self):
        serial_frame = ctk.CTkFrame(self.left_frame, fg_color=DARK_CARD)
        serial_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        title_frame = ctk.CTkFrame(serial_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(title_frame, text="🌐 Device Connection", font=("Arial", 14, "bold")).pack(side="top")

        port_label = ctk.CTkLabel(serial_frame, text="COM Port:")
        port_label.pack(pady=(0, 5))

        self.port_combobox = ctk.CTkComboBox(serial_frame, values=self.get_serial_ports())
        self.port_combobox.pack(fill="x", pady=5)

        self.connect_button = ctk.CTkButton(
            serial_frame,
            text="Connect",
            command=self.toggle_serial_connection,
            fg_color="#029606",
            hover_color="#005703"
        )
        self.connect_button.pack(fill="x", pady=3)

        self.status_label = ctk.CTkLabel(serial_frame, text="Status: Disconnected", text_color=ACCENT_RED)
        self.status_label.pack(pady=3)

    def create_sensor_display(self):
        sensor_frame = ctk.CTkFrame(self.left_frame, fg_color=DARK_BG)
        sensor_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        sensor_frame.grid_columnconfigure(0, weight=1)

        tabview = ctk.CTkTabview(sensor_frame, fg_color=DARK_CARD, segmented_button_fg_color=DARK_BG,
                                 segmented_button_selected_color="#2c4f2b",
                                 segmented_button_selected_hover_color="#405e3f",
                                 segmented_button_unselected_hover_color="#405e3f")
        tabview.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        current_tab = tabview.add("🌡️Dashboard")
        self.create_dashboard_tab(current_tab)

        history_tab = tabview.add(" 📈 History ")
        self.create_history_charts_tab(history_tab)

        raw_tab = tabview.add(" 📋 Raw Data ")
        self.create_raw_data_tab(raw_tab)

    def create_dashboard_tab(self, parent):
        dashboard_frame = ctk.CTkFrame(parent, fg_color=DARK_CARD)
        dashboard_frame.pack(fill="both", expand=True, padx=5, pady=10)

        status_frame = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
        status_frame.pack(fill="x", padx=5, pady=5)

        weather_card = ctk.CTkFrame(status_frame, fg_color=DARK_BG, corner_radius=10)
        weather_card.pack(side="left", fill="both", expand=True, padx=5)

        weather_header = ctk.CTkFrame(weather_card, fg_color="transparent")
        weather_header.pack(fill="x", pady=(5, 0))
        ctk.CTkLabel(weather_header, text="☀️ WEATHER", font=("Arial", 13, "bold")).pack(side="top")

        self.weather_label = ctk.CTkLabel(weather_card, text="Sunny", font=("Times New Roman", 15, "bold"),
                                          text_color=ACCENT_YELLOW)
        self.weather_label.pack(pady=5)

        motor_card = ctk.CTkFrame(status_frame, fg_color=DARK_BG, corner_radius=10)
        motor_card.pack(side="left", fill="both", expand=True, padx=5)

        motor_header = ctk.CTkFrame(motor_card, fg_color="transparent")
        motor_header.pack(fill="x", pady=(5, 0))
        ctk.CTkLabel(motor_header, text="🚰 IRRIGATION", font=("Arial", 12, "bold")).pack(side="top")

        self.motor_label = ctk.CTkLabel(motor_card, text="OFF", font=("Arial", 16),
                                        text_color="#eb5d36")
        self.motor_label.pack(pady=5)

        gauge_frame = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
        gauge_frame.pack(fill="both", expand=True, padx=5, pady=5)

        gauge_frame.grid_columnconfigure(0, weight=1)
        gauge_frame.grid_columnconfigure(1, weight=1)
        gauge_frame.grid_rowconfigure(0, weight=1)
        gauge_frame.grid_rowconfigure(1, weight=1)

        temp_card = ctk.CTkFrame(gauge_frame, fg_color=DARK_BG, corner_radius=10)
        temp_card.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(temp_card, text="Temperature", font=("Times New Roman", 14, "bold")).pack(pady=(5, 0))
        self.temp_gauge = AnimatedCircularGauge(temp_card, size=180, min_value=0, max_value=50,
                                                label="", unit="°C")
        self.temp_gauge.pack(pady=5)
        self.temp_gauge.fg_color = ACCENT_BLUE

        humid_card = ctk.CTkFrame(gauge_frame, fg_color=DARK_BG, corner_radius=10)
        humid_card.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(humid_card, text="Humidity", font=("Times New Roman", 14, "bold")).pack(pady=(5, 0))
        self.humid_gauge = AnimatedCircularGauge(humid_card, size=180, min_value=0, max_value=100,
                                                 label="", unit="%")
        self.humid_gauge.pack(pady=5)
        self.humid_gauge.fg_color = "#00bcd4"

        moist_card = ctk.CTkFrame(gauge_frame, fg_color=DARK_BG, corner_radius=10)
        moist_card.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(moist_card, text="Soil Moisture", font=("Times New Roman", 14, "bold")).pack(pady=(5, 0))
        self.moist_gauge = AnimatedCircularGauge(moist_card, size=180, min_value=0, max_value=100,
                                                 label="", unit="%")
        self.moist_gauge.pack(pady=5)
        self.moist_gauge.fg_color = ACCENT_GREEN

        light_card = ctk.CTkFrame(gauge_frame, fg_color=DARK_BG, corner_radius=10)
        light_card.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(light_card, text="Light Level", font=("Times New Roman", 14, "bold")).pack(pady=(5, 0))
        self.light_gauge = AnimatedCircularGauge(light_card, size=180, min_value=0, max_value=100,
                                                 label="", unit="%")
        self.light_gauge.pack(pady=5)
        self.light_gauge.fg_color = ACCENT_YELLOW

    def create_history_charts_tab(self, parent):
        chart_frame = ctk.CTkFrame(parent, fg_color="#000000")
        chart_frame.pack(fill="both", expand=True, padx=10, pady=5)

        plt.style.use('dark_background')
        self.fig, self.axs = plt.subplots(2, 2, figsize=(8, 6), facecolor=DARK_BG)
        self.fig.tight_layout(pad=3.0)

        for ax in self.axs.flatten():
            ax.set_facecolor("#000000")
            ax.grid(color='#2a3a31')

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.update_history_charts()

    def create_raw_data_tab(self, parent):
        self.raw_data_text = ctk.CTkTextbox(
            parent,
            wrap="word",
            fg_color=DARK_BG,
            text_color=TEXT_WHITE,
            font=("Consolas", 12)
        )
        self.raw_data_text.pack(fill="both", expand=True, padx=5, pady=10)
        self.raw_data_text.insert("0.0", "Waiting for data...\n")

    def browse_rgb(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.rgb_entry.delete(0, "end")
            self.rgb_entry.insert(0, file_path)

    def browse_nir(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.nir_entry.delete(0, "end")
            self.nir_entry.insert(0, file_path)

    def create_analysis_display(self):
        # Analysis display frame
        analysis_frame = ctk.CTkFrame(self.center_frame, fg_color=DARK_BG)
        analysis_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        analysis_frame.grid_columnconfigure(0, weight=1)
        analysis_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(analysis_frame, text="🌿 Vegetation Index Analysis",
                     font=("Arial", 16, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        input_frame = ctk.CTkFrame(analysis_frame, fg_color=DARK_CARD)
        input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=0)

        # RGB image path input
        ctk.CTkLabel(input_frame, text="RGB Image Path:").grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))
        self.rgb_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter RGB image path")
        self.rgb_entry.grid(row=1, column=0, sticky="ew", padx=(10, 5), pady=5)
        rgb_browse_button = ctk.CTkButton(input_frame, text="Browse", command=self.browse_rgb,
                                          fg_color=ACCENT_BLUE, hover_color="#1976d2")
        rgb_browse_button.grid(row=1, column=1, padx=(0, 10), pady=5)

        # NIR image path input
        ctk.CTkLabel(input_frame, text="NIR Image Path:").grid(row=2, column=0, sticky="w", padx=10, pady=(5, 0))
        self.nir_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter NIR image path")
        self.nir_entry.grid(row=3, column=0, sticky="ew", padx=(10, 5), pady=5)
        nir_browse_button = ctk.CTkButton(input_frame, text="Browse", command=self.browse_nir,
                                          fg_color=ACCENT_BLUE, hover_color="#1976d2")
        nir_browse_button.grid(row=3, column=1, padx=(0, 10), pady=5)

        # Analyze button
        self.analyze_button = ctk.CTkButton(
            input_frame,
            text="Analyze",
            command=self.run_analysis,
            fg_color=ACCENT_GREEN,
            hover_color="#3d8b40"
        )
        self.analyze_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Plot display area
        self.plot_frame = ctk.CTkFrame(analysis_frame, fg_color=DARK_BG)
        self.plot_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=1)

        # Placeholder label
        self.plot_label = ctk.CTkLabel(
            self.plot_frame,
            text="No analysis results available",
            fg_color=DARK_CARD,
            corner_radius=10
        )
        self.plot_label.pack(fill="both", expand=True, padx=10, pady=10)

    def load_inference_data(self, rgb_path):
        # Load inference data from ndvi_analysis_date.csv
        csv_path = r"S:\RVCE\4th_sem\MCP\PBL\Display\ndvi_analysis_date.csv"
        base_name = os.path.splitext(os.path.basename(rgb_path))[0]

        try:
            df = pd.read_csv(csv_path)
            # Find the row matching the RGB image
            row = df[df['RGB Image'].str.contains(base_name, case=False, na=False)]
            if not row.empty:
                stats = row.iloc[-1]
                # Prepare inference data as a list of tuples: (label, value, color)
                inference_data = [
                    ("📅 DateTime", stats['DateTime'], TEXT_WHITE),
                    ("🖼️ Image", stats['RGB Image'], TEXT_WHITE),
                    ("📈 Mean NDVI", f"{stats['Mean NDVI']:.3f}",
                     ACCENT_GREEN if stats['Mean NDVI'] > 0.6 else ACCENT_YELLOW if stats[
                                                                                        'Mean NDVI'] > 0.3 else ACCENT_RED),
                    ("🌱 Healthy", f"{stats['Healthy (%)']:.2f}%",
                     ACCENT_GREEN if stats['Healthy (%)'] > 50 else ACCENT_YELLOW if stats[
                                                                                         'Healthy (%)'] > 20 else ACCENT_RED),
                    ("🌿 Moderate", f"{stats['Moderate (%)']:.2f}%", ACCENT_YELLOW),
                    ("🍂 Sparse", f"{stats['Sparse (%)']:.2f}%", ACCENT_RED),
                    ("🏜️ Non-Vegetated", f"{stats['Non-Vegetated (%)']:.2f}%", ACCENT_RED)
                ]
                # Interpretation with dynamic color-coding
                interpretation = []
                if stats['Mean NDVI'] > 0.6:
                    interpretation.append(
                        ("🌟 Healthy Vegetation: Mean NDVI > 0.6 indicates robust plant health.", ACCENT_GREEN))
                elif stats['Mean NDVI'] > 0.3:
                    interpretation.append(
                        ("⚠️ Moderate Health: Mean NDVI between 0.3-0.6 suggests variable plant vigor.", ACCENT_YELLOW))
                else:
                    interpretation.append(
                        ("🚨 Low Health: Mean NDVI < 0.3 indicates potential stress or sparse vegetation.", ACCENT_RED))

                if stats['Healthy (%)'] > 50:
                    interpretation.append(("✅ Good Crop Health: Over 50% healthy vegetation detected.", ACCENT_GREEN))
                else:
                    interpretation.append(
                        ("⚠️ Monitor Crop: Healthy vegetation below 50%, consider irrigation or nutrient checks.",
                         ACCENT_YELLOW))

                if stats['Sparse (%)'] + stats['Non-Vegetated (%)'] > 30:
                    interpretation.append(
                        ("⚠️ Stress Detected: High sparse/non-vegetated areas (>30%) suggest drought or soil issues.",
                         ACCENT_RED))
                else:
                    interpretation.append(
                        ("🌿 Stable Conditions: Low sparse/non-vegetated areas indicate stable soil health.",
                         ACCENT_GREEN))

                return inference_data, interpretation
            else:
                return [(f"No analysis data found for {base_name}", "", ACCENT_RED)], []
        except Exception as e:
            return [(f"Error loading inference: {str(e)}", "", ACCENT_RED)], []

    def run_analysis(self):
        # Get image paths from entry fields
        rgb_path = self.rgb_entry.get()
        nir_path = self.nir_entry.get()

        if not rgb_path or not nir_path:
            self.plot_label.configure(text="Please enter both RGB and NIR image paths")
            return

        # Clear previous plot, buttons, and inference if exist
        if self.analysis_canvas:
            self.analysis_canvas.get_tk_widget().destroy()
            self.analysis_canvas = None
        if self.go_back_button:
            self.go_back_button.destroy()
            self.go_back_button = None
        if self.buttons_frame:
            self.buttons_frame.destroy()
            self.buttons_frame = None
        if self.inference_frame:
            self.inference_frame.destroy()
            self.inference_frame = None
        if self.analysis_container:
            self.analysis_container.destroy()
            self.analysis_container = None

        # Hide left column and expand right column
        self.left_frame.grid_remove()
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Create buttons frame at root level for Go Back button
        self.buttons_frame = ctk.CTkFrame(self, fg_color=DARK_BG)
        self.buttons_frame.grid(row=1, column=1, sticky="ne", padx=(110, 5), pady=5)

        # Add Go Back button
        self.go_back_button = ctk.CTkButton(
            self.buttons_frame,
            text="Go Back",
            command=self.restore_dashboard,
            fg_color=ACCENT_RED,
            hover_color="#b71c1c",
            width=100
        )
        self.go_back_button.pack(side="left", padx=5)

        # Create a new frame to hold plot and inference
        self.analysis_container = ctk.CTkFrame(self.center_frame, fg_color=DARK_BG)
        self.analysis_container.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.analysis_container.grid_columnconfigure(0, weight=7)  # Plot (70%)
        self.analysis_container.grid_columnconfigure(1, weight=3)  # Inference (30%)
        self.analysis_container.grid_rowconfigure(0, weight=1)

        # Recreate plot_frame in the container
        self.plot_frame = ctk.CTkFrame(self.analysis_container, fg_color=DARK_BG)
        self.plot_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=1)

        # Create inference frame
        self.inference_frame = ctk.CTkFrame(self.analysis_container, fg_color=GRADIENT_CARD,
                                            corner_radius=10, border_width=2, border_color=ACCENT_GREEN)
        self.inference_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.inference_frame.grid_columnconfigure(0, weight=1)
        self.inference_frame.grid_rowconfigure(2, weight=1)

        # Run analysis
        try:
            # Call combined analysis function
            plt.style.use('dark_background')
            fig = combined_ndvi_vari_analysis(rgb_path, nir_path)
            if fig is None:
                self.plot_label.configure(text="Analysis failed: Check console for details")
                self.restore_dashboard()
                return

            # Embed the plot in the GUI
            self.analysis_canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            self.analysis_canvas.get_tk_widget().pack(fill="both", expand=True)
            self.plot_label.pack_forget()  # Hide placeholder
            self.analysis_canvas.draw()

            # Display inference
            inference_data, interpretation = self.load_inference_data(rgb_path)

            # Inference title
            ctk.CTkLabel(
                self.inference_frame,
                text="🌿 Vegetation Insights",
                font=("Arial", 18, "bold"),
                text_color=ACCENT_GREEN
            ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

            # Statistics section
            stats_frame = ctk.CTkFrame(self.inference_frame, fg_color=GRADIENT_CARD,
                                       corner_radius=8, border_width=1, border_color=ACCENT_YELLOW)
            stats_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
            stats_frame.grid_columnconfigure((0, 1), weight=1)

            ctk.CTkLabel(
                stats_frame,
                text="📊 Statistics",
                font=("Arial", 14, "bold"),
                text_color=ACCENT_YELLOW
            ).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")

            for i, (label, value, color) in enumerate(inference_data, start=1):
                ctk.CTkLabel(
                    stats_frame,
                    text=label,
                    font=("Arial", 12, "bold"),
                    text_color=TEXT_WHITE,
                    anchor="w"
                ).grid(row=i, column=0, padx=(5, 2), pady=2, sticky="w")
                ctk.CTkLabel(
                    stats_frame,
                    text=value,
                    font=("Arial", 12),
                    text_color=color,
                    anchor="w"
                ).grid(row=i, column=1, padx=(2, 5), pady=2, sticky="w")

            # Interpretation section
            interp_frame = ctk.CTkFrame(self.inference_frame, fg_color=GRADIENT_CARD,
                                        corner_radius=8, border_width=1, border_color=ACCENT_YELLOW)
            interp_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
            interp_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                interp_frame,
                text="🔍 Interpretation",
                font=("Arial", 14, "bold"),
                text_color=ACCENT_YELLOW
            ).grid(row=0, column=0, padx=5, pady=5, sticky="w")

            for i, (text, color) in enumerate(interpretation, start=1):
                ctk.CTkLabel(
                    interp_frame,
                    text=text,
                    font=("Arial", 12),
                    text_color=color,
                    anchor="w",
                    wraplength=350
                ).grid(row=i, column=0, padx=5, pady=2, sticky="w")

        except Exception as e:
            self.plot_label.configure(text=f"Error: {str(e)}")
            print(f"Analysis error: {str(e)}")
            self.restore_dashboard()

    def restore_dashboard(self):
        # Clear existing plot, buttons, and inference
        if self.analysis_canvas:
            self.analysis_canvas.get_tk_widget().destroy()
            self.analysis_canvas = None
        if self.go_back_button:
            self.go_back_button.destroy()
            self.go_back_button = None
        if self.buttons_frame:
            self.buttons_frame.destroy()
            self.buttons_frame = None
        if self.inference_frame:
            self.inference_frame.destroy()
            self.inference_frame = None
        if self.analysis_container:
            self.analysis_container.destroy()
            self.analysis_container = None

        # Restore original plot_frame in analysis_frame
        self.plot_frame = ctk.CTkFrame(self.center_frame, fg_color=DARK_BG)
        self.plot_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=1)

        # Restore placeholder label
        self.plot_label = ctk.CTkLabel(
            self.plot_frame,
            text="No analysis results available",
            fg_color=DARK_CARD,
            corner_radius=10
        )
        self.plot_label.pack(fill="both", expand=True, padx=10, pady=10)

        # Restore left column and reset grid weights
        self.left_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def toggle_serial_connection(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.disconnect_serial()
        else:
            self.connect_serial()

    def connect_serial(self):
        port = self.port_combobox.get()
        if not port:
            self.status_label.configure(text="Status: No port selected", text_color=ACCENT_RED)
            return

        try:
            self.serial_connection = serial.Serial(
                port=port,
                baudrate=115200,
                timeout=1
            )
            self.status_label.configure(text=f"Status: Connected to {port}", text_color=ACCENT_GREEN)
            self.connect_button.configure(text="Disconnect", fg_color=ACCENT_RED, hover_color="#b71c1c")

            self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.serial_thread.start()

        except serial.SerialException as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color=ACCENT_RED)

    def disconnect_serial(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.serial_connection = None
        self.status_label.configure(text="Status: Disconnected", text_color=ACCENT_RED)
        self.connect_button.configure(text="Connect", fg_color=ACCENT_GREEN, hover_color="#3d8b40")

    def read_serial_data(self):
        while self.running and self.serial_connection and self.serial_connection.is_open:
            try:
                line = self.serial_connection.readline().decode('utf-8').strip()
                if line:
                    self.process_serial_data(line)
            except (serial.SerialException, UnicodeDecodeError):
                break
            time.sleep(0.1)

    def process_serial_data(self, data):
        self.raw_data_text.insert("end", f"{datetime.now().strftime('%H:%M:%S')} - {data}\n")
        self.raw_data_text.see("end")

        try:
            parts = [p.strip() for p in data.split(';') if p.strip()]
            for part in parts:
                if '=' in part:
                    key, value = part.split('=', 1)
                    key = key.strip().lower()

                    if key in self.sensor_data:
                        if key in ["temperature", "humidity", "moisture", "light"]:
                            self.sensor_data[key] = float(value) if '.' in value else int(value)
                        elif key in ["temp_status", "moisture_status", "light_status"]:
                            self.sensor_data[key] = "✅" if int(value) == 1 else "❌"
                        elif key == "motor":
                            self.sensor_data[key] = value
                        elif key == "weather":
                            weather_value = value
                            if "Rain_now" in weather_value:
                                self.sensor_data["weather"] = "🌧️ Raining Now"
                            elif "No_rain" in weather_value:
                                self.sensor_data["weather"] = "☀️ Sunny / No Rain"
                            elif "Rain_tomorrow" in weather_value:
                                self.sensor_data["weather"] = "🌧️ Rain expected tomorrow"
                            elif "Rain_now_tomorrow" in weather_value:
                                self.sensor_data["weather"] = "🌧️ Raining Now.\n 🌧️ Rain expected tomorrow"
                            else:
                                self.sensor_data["weather"] = "🌤️ Unknown"

            timestamp = datetime.now()
            new_row = {
                "timestamp": timestamp,
                "temperature": self.sensor_data["temperature"],
                "humidity": self.sensor_data["humidity"],
                "moisture": self.sensor_data["moisture"],
                "light": self.sensor_data["light"]
            }
            self.sensor_history = pd.concat([self.sensor_history, pd.DataFrame([new_row])], ignore_index=True)

            if len(self.sensor_history) > 100:
                self.sensor_history = self.sensor_history.iloc[-100:]

            self.update_sensor_display()

        except Exception as e:
            print(f"Error processing data: {e}")

    def update_sensor_display(self):
        self.temp_gauge.set_value(self.sensor_data["temperature"])
        self.humid_gauge.set_value(self.sensor_data["humidity"])
        self.moist_gauge.set_value(self.sensor_data["moisture"])
        self.light_gauge.set_value(self.sensor_data["light"])

        self.weather_label.configure(text=self.sensor_data["weather"])

        motor_status = self.sensor_data["motor"]
        self.motor_label.configure(text=motor_status)
        if motor_status.upper() == "ON":
            self.motor_label.configure(text_color=ACCENT_GREEN)
        else:
            self.motor_label.configure(text_color=ACCENT_RED)

        self.update_history_charts()

    def update_history_charts(self):
        if not self.sensor_history.empty:
            for ax in self.axs.flatten():
                ax.clear()

            self.axs[0, 0].plot(self.sensor_history["timestamp"], self.sensor_history["temperature"],
                                color=ACCENT_BLUE, linewidth=2)
            self.axs[0, 0].set_title("Temperature (°C)", color=TEXT_WHITE)
            self.axs[0, 0].grid(True, color='#2a3a31')

            self.axs[0, 1].plot(self.sensor_history["timestamp"], self.sensor_history["humidity"],
                                color="#00bcd4", linewidth=2)
            self.axs[0, 1].set_title("Humidity (%)", color=TEXT_WHITE)
            self.axs[0, 1].grid(True, color='#2a3a31')

            self.axs[1, 0].plot(self.sensor_history["timestamp"], self.sensor_history["moisture"],
                                color=ACCENT_GREEN, linewidth=2)
            self.axs[1, 0].set_title("Soil Moisture (%)", color=TEXT_WHITE)
            self.axs[1, 0].grid(True, color='#2a3a31')

            self.axs[1, 1].plot(self.sensor_history["timestamp"], self.sensor_history["light"],
                                color=ACCENT_YELLOW, linewidth=2)
            self.axs[1, 1].set_title("Light Level (%)", color=TEXT_WHITE)
            self.axs[1, 1].grid(True, color='#2a3a31')

            for ax in self.axs.flatten():
                ax.tick_params(colors=TEXT_WHITE)
                plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

            self.fig.tight_layout()
            self.canvas.draw()

    def on_closing(self):
        self.running = False
        self.disconnect_serial()
        self.quit()  # Stop the Tkinter event loop
        self.destroy()  # Destroy the window


if __name__ == "__main__":
    app = VegetationAnalysisGUI()
    app.mainloop()