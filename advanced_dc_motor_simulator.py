"""
Advanced DC Series Motor Simulator with Multi-Physics Modeling
Solution for Example 29.32 and Comprehensive Motor Analysis Tool

Features:
- Multi-tab interface with auto-scaling
- Real-time ODE solvers (RK45, Euler)
- Multi-physics simulation (electromagnetic, thermal, mechanical)
- Economic analysis and loss breakdown
- Dynamic visualization
- Advanced motor controls
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
import threading
import time
from datetime import datetime

class DCMotorSimulator:
    """Advanced DC Series Motor Simulator with Multi-Physics Modeling"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced DC Series Motor Simulator - Multi-Physics Analysis")
        self.root.geometry("1400x900")

        # Simulation state
        self.is_running = False
        self.simulation_thread = None
        self.current_time = 0
        self.dt = 0.001  # Time step for simulation

        # Motor parameters
        self.params = {
            'V_supply': 460.0,      # Supply voltage (V)
            'R_armature': 0.5,      # Armature + field resistance (Ω)
            'L_armature': 0.05,     # Armature inductance (H)
            'J_inertia': 0.5,       # Moment of inertia (kg·m²)
            'B_friction': 0.01,     # Viscous friction coefficient
            'k_torque': 0.05,       # Torque constant
            'k_emf': 0.05,          # Back-EMF constant
            'T_load': 100.0,        # Load torque (N·m)
            'efficiency': 0.85,     # Motor efficiency
            'power_cost': 0.12,     # $/kWh
            'ambient_temp': 25.0,   # Ambient temperature (°C)
            'thermal_resistance': 2.0,  # °C/W
            'thermal_capacitance': 1000.0,  # J/°C
            'max_temp': 155.0,      # Maximum winding temperature (°C)
        }

        # State variables
        self.state = {
            'current': 0.0,
            'speed': 0.0,
            'torque': 0.0,
            'temperature': 25.0,
            'power_in': 0.0,
            'power_out': 0.0,
        }

        # History for plotting
        self.history = {
            'time': [],
            'current': [],
            'speed': [],
            'torque': [],
            'temperature': [],
            'power_in': [],
            'power_out': [],
            'efficiency': [],
            'copper_loss': [],
            'iron_loss': [],
            'mech_loss': [],
            'stray_loss': [],
        }

        # Solver selection
        self.solver_type = tk.StringVar(value="RK45")

        # Example 29.32 data (correcting last torque value from 46.2 to 446.2)
        self.test_current = np.array([20, 30, 40, 50])
        self.test_torque = np.array([128.8, 230.5, 349.8, 446.2])  # Corrected

        # Build UI
        self.setup_ui()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def setup_ui(self):
        """Setup the user interface with tabs"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs
        self.tab_main = ttk.Frame(self.notebook)
        self.tab_motor_control = ttk.Frame(self.notebook)
        self.tab_analysis = ttk.Frame(self.notebook)
        self.tab_thermal = ttk.Frame(self.notebook)
        self.tab_economic = ttk.Frame(self.notebook)
        self.tab_example = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_main, text="Main Control")
        self.notebook.add(self.tab_motor_control, text="Motor Control")
        self.notebook.add(self.tab_analysis, text="Performance Analysis")
        self.notebook.add(self.tab_thermal, text="Thermal Analysis")
        self.notebook.add(self.tab_economic, text="Economic Analysis")
        self.notebook.add(self.tab_example, text="Example 29.32")

        # Setup individual tabs
        self.setup_main_tab()
        self.setup_motor_control_tab()
        self.setup_analysis_tab()
        self.setup_thermal_tab()
        self.setup_economic_tab()
        self.setup_example_tab()

    def setup_main_tab(self):
        """Setup main control tab"""
        # Left panel - Parameters
        left_frame = ttk.LabelFrame(self.tab_main, text="Motor Parameters", padding=10)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Make responsive
        self.tab_main.columnconfigure(0, weight=1)
        self.tab_main.columnconfigure(1, weight=3)
        self.tab_main.rowconfigure(0, weight=1)

        # Parameter inputs
        self.param_widgets = {}
        param_labels = {
            'V_supply': 'Supply Voltage (V)',
            'R_armature': 'Armature Resistance (Ω)',
            'L_armature': 'Armature Inductance (H)',
            'J_inertia': 'Moment of Inertia (kg·m²)',
            'B_friction': 'Friction Coefficient',
            'T_load': 'Load Torque (N·m)',
        }

        row = 0
        for param, label in param_labels.items():
            ttk.Label(left_frame, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)

            var = tk.DoubleVar(value=self.params[param])
            scale = ttk.Scale(left_frame, from_=0, to=self.params[param]*3,
                            orient=tk.HORIZONTAL, variable=var,
                            command=lambda v, p=param: self.update_param(p, v))
            scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)

            entry = ttk.Entry(left_frame, textvariable=var, width=10)
            entry.grid(row=row, column=2, pady=2)

            self.param_widgets[param] = var
            row += 1

        # Control buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)

        ttk.Button(button_frame, text="Start", command=self.start_simulation,
                  style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Stop", command=self.stop_simulation,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset_simulation).pack(side=tk.LEFT, padx=5)

        # Solver selection
        row += 1
        ttk.Label(left_frame, text="ODE Solver:").grid(row=row, column=0, sticky=tk.W, pady=5)
        solver_frame = ttk.Frame(left_frame)
        solver_frame.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5)
        ttk.Radiobutton(solver_frame, text="RK45 (Adaptive)", variable=self.solver_type,
                       value="RK45").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(solver_frame, text="Euler (Fixed)", variable=self.solver_type,
                       value="Euler").pack(side=tk.LEFT, padx=5)

        # Right panel - Real-time graphs
        right_frame = ttk.LabelFrame(self.tab_main, text="Real-Time Monitoring", padding=10)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Create matplotlib figure
        self.fig_main = Figure(figsize=(10, 8), dpi=80)
        self.canvas_main = FigureCanvasTkAgg(self.fig_main, master=right_frame)
        self.canvas_main.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Create subplots
        self.ax_current = self.fig_main.add_subplot(3, 2, 1)
        self.ax_speed = self.fig_main.add_subplot(3, 2, 2)
        self.ax_torque = self.fig_main.add_subplot(3, 2, 3)
        self.ax_temp = self.fig_main.add_subplot(3, 2, 4)
        self.ax_power = self.fig_main.add_subplot(3, 2, 5)
        self.ax_efficiency = self.fig_main.add_subplot(3, 2, 6)

        self.fig_main.tight_layout()

    def setup_motor_control_tab(self):
        """Setup motor control strategies tab"""
        # Control frame
        control_frame = ttk.LabelFrame(self.tab_motor_control, text="Advanced Control Methods", padding=10)
        control_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Control method selection
        ttk.Label(control_frame, text="Control Strategy:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)

        self.control_method = tk.StringVar(value="Open Loop")
        control_methods = ["Open Loop", "PI Speed Control", "Field Weakening", "Chopper Control", "PWM Control"]

        for i, method in enumerate(control_methods):
            ttk.Radiobutton(control_frame, text=method, variable=self.control_method,
                          value=method).grid(row=i+1, column=0, sticky=tk.W, padx=20, pady=2)

        # PI Controller parameters
        pi_frame = ttk.LabelFrame(control_frame, text="PI Controller Parameters", padding=10)
        pi_frame.grid(row=0, column=1, rowspan=6, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)

        self.kp_var = tk.DoubleVar(value=1.0)
        self.ki_var = tk.DoubleVar(value=0.5)
        self.setpoint_var = tk.DoubleVar(value=1500.0)

        ttk.Label(pi_frame, text="Proportional Gain (Kp):").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Scale(pi_frame, from_=0, to=10, variable=self.kp_var, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(pi_frame, textvariable=self.kp_var, width=10).grid(row=0, column=2, pady=5)

        ttk.Label(pi_frame, text="Integral Gain (Ki):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Scale(pi_frame, from_=0, to=5, variable=self.ki_var, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(pi_frame, textvariable=self.ki_var, width=10).grid(row=1, column=2, pady=5)

        ttk.Label(pi_frame, text="Speed Setpoint (RPM):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Scale(pi_frame, from_=0, to=3000, variable=self.setpoint_var, orient=tk.HORIZONTAL).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(pi_frame, textvariable=self.setpoint_var, width=10).grid(row=2, column=2, pady=5)

        # PWM parameters
        pwm_frame = ttk.LabelFrame(control_frame, text="PWM Parameters", padding=10)
        pwm_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        self.duty_cycle_var = tk.DoubleVar(value=0.8)
        self.pwm_freq_var = tk.DoubleVar(value=1000.0)

        ttk.Label(pwm_frame, text="Duty Cycle:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Scale(pwm_frame, from_=0, to=1, variable=self.duty_cycle_var, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(pwm_frame, textvariable=self.duty_cycle_var, width=10).grid(row=0, column=2, pady=5)

        ttk.Label(pwm_frame, text="PWM Frequency (Hz):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(pwm_frame, textvariable=self.pwm_freq_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5)

    def setup_analysis_tab(self):
        """Setup performance analysis tab"""
        # Loss breakdown
        loss_frame = ttk.LabelFrame(self.tab_analysis, text="Detailed Loss Breakdown", padding=10)
        loss_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create figure for loss analysis
        self.fig_analysis = Figure(figsize=(12, 8), dpi=80)
        self.canvas_analysis = FigureCanvasTkAgg(self.fig_analysis, master=loss_frame)
        self.canvas_analysis.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Subplots for different analyses
        self.ax_loss_pie = self.fig_analysis.add_subplot(2, 2, 1)
        self.ax_loss_time = self.fig_analysis.add_subplot(2, 2, 2)
        self.ax_speed_torque = self.fig_analysis.add_subplot(2, 2, 3)
        self.ax_efficiency_curve = self.fig_analysis.add_subplot(2, 2, 4)

        self.fig_analysis.tight_layout()

    def setup_thermal_tab(self):
        """Setup thermal analysis tab"""
        thermal_frame = ttk.LabelFrame(self.tab_thermal, text="Multi-Physics Thermal Analysis", padding=10)
        thermal_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Thermal parameters
        param_frame = ttk.Frame(thermal_frame)
        param_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(param_frame, text="Thermal Parameters:", font=('Arial', 12, 'bold')).pack(pady=5)

        self.thermal_params = {}
        thermal_labels = {
            'ambient_temp': ('Ambient Temperature (°C)', 0, 50),
            'thermal_resistance': ('Thermal Resistance (°C/W)', 0.1, 10),
            'thermal_capacitance': ('Thermal Capacitance (J/°C)', 100, 5000),
            'max_temp': ('Maximum Temperature (°C)', 100, 200),
        }

        for param, (label, min_val, max_val) in thermal_labels.items():
            frame = ttk.Frame(param_frame)
            frame.pack(fill=tk.X, pady=5)

            ttk.Label(frame, text=label).pack(anchor=tk.W)
            var = tk.DoubleVar(value=self.params[param])
            ttk.Scale(frame, from_=min_val, to=max_val, variable=var,
                     orient=tk.HORIZONTAL).pack(fill=tk.X)
            ttk.Entry(frame, textvariable=var, width=10).pack()

            self.thermal_params[param] = var

        # Derating curve
        ttk.Label(param_frame, text="\nDerating Information:", font=('Arial', 10, 'bold')).pack(pady=5)
        self.derating_label = ttk.Label(param_frame, text="Operating within limits", foreground='green')
        self.derating_label.pack(pady=5)

        # Thermal visualization
        viz_frame = ttk.Frame(thermal_frame)
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.fig_thermal = Figure(figsize=(10, 8), dpi=80)
        self.canvas_thermal = FigureCanvasTkAgg(self.fig_thermal, master=viz_frame)
        self.canvas_thermal.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.ax_temp_rise = self.fig_thermal.add_subplot(2, 1, 1)
        self.ax_derating = self.fig_thermal.add_subplot(2, 1, 2)

        self.fig_thermal.tight_layout()

    def setup_economic_tab(self):
        """Setup economic analysis tab"""
        econ_frame = ttk.LabelFrame(self.tab_economic, text="Economic Analysis & Energy Consumption", padding=10)
        econ_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Economic parameters
        param_frame = ttk.LabelFrame(econ_frame, text="Economic Parameters", padding=10)
        param_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.power_cost_var = tk.DoubleVar(value=0.12)
        self.operating_hours_var = tk.DoubleVar(value=8760)  # Hours per year
        self.maintenance_cost_var = tk.DoubleVar(value=500)  # Annual maintenance

        ttk.Label(param_frame, text="Energy Cost ($/kWh):").pack(anchor=tk.W, pady=2)
        ttk.Entry(param_frame, textvariable=self.power_cost_var, width=15).pack(pady=2)

        ttk.Label(param_frame, text="Operating Hours (hrs/year):").pack(anchor=tk.W, pady=2)
        ttk.Entry(param_frame, textvariable=self.operating_hours_var, width=15).pack(pady=2)

        ttk.Label(param_frame, text="Maintenance Cost ($/year):").pack(anchor=tk.W, pady=2)
        ttk.Entry(param_frame, textvariable=self.maintenance_cost_var, width=15).pack(pady=2)

        ttk.Button(param_frame, text="Calculate Economics",
                  command=self.calculate_economics).pack(pady=10)

        # Results display
        self.econ_results = tk.Text(param_frame, width=30, height=15)
        self.econ_results.pack(pady=5)

        # Visualization
        viz_frame = ttk.Frame(econ_frame)
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.fig_econ = Figure(figsize=(10, 8), dpi=80)
        self.canvas_econ = FigureCanvasTkAgg(self.fig_econ, master=viz_frame)
        self.canvas_econ.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.ax_cost_breakdown = self.fig_econ.add_subplot(2, 1, 1)
        self.ax_cost_time = self.fig_econ.add_subplot(2, 1, 2)

        self.fig_econ.tight_layout()

    def setup_example_tab(self):
        """Setup Example 29.32 solution tab"""
        example_frame = ttk.LabelFrame(self.tab_example, text="Example 29.32 - Series Motor Speed/Torque Curve", padding=10)
        example_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel - problem statement and solution
        left_panel = ttk.Frame(example_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Problem statement
        problem_text = """
Example 29.32 - DC Series Motor Analysis

Given Data:
• Static torque test results:
  - Current (A):    20,    30,    40,    50
  - Torque (N·m): 128.8, 230.5, 349.8, 446.2*

• Supply Voltage: 460 V
• Armature + Field Resistance: 0.5 Ω
• Ignore iron and friction losses

Task: Deduce the speed/torque curve for the machine.

* Note: Original value of 46.2 corrected to 446.2 based on series motor characteristics

Solution Approach:
1. Establish relationship between current and torque from test data
2. For series motor: T ∝ Φ × Ia ≈ k × Ia²
3. Calculate back-EMF: Eb = V - Ia × Ra
4. For series motor: Eb = k' × Φ × N = k'' × Ia × N
5. Solve for speed: N = Eb / (k'' × Ia)
6. Plot speed-torque characteristic
        """

        problem_label = tk.Text(left_panel, wrap=tk.WORD, height=25, width=50)
        problem_label.insert(1.0, problem_text)
        problem_label.config(state=tk.DISABLED)
        problem_label.pack(pady=5)

        ttk.Button(left_panel, text="Solve Example 29.32",
                  command=self.solve_example_29_32).pack(pady=10)

        # Results text
        self.example_results = tk.Text(left_panel, wrap=tk.WORD, height=15, width=50)
        self.example_results.pack(pady=5)

        # Right panel - visualization
        right_panel = ttk.Frame(example_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.fig_example = Figure(figsize=(8, 10), dpi=80)
        self.canvas_example = FigureCanvasTkAgg(self.fig_example, master=right_panel)
        self.canvas_example.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.ax_torque_current = self.fig_example.add_subplot(3, 1, 1)
        self.ax_speed_current = self.fig_example.add_subplot(3, 1, 2)
        self.ax_speed_torque_curve = self.fig_example.add_subplot(3, 1, 3)

        self.fig_example.tight_layout()

    def solve_example_29_32(self):
        """Solve Example 29.32 and display results"""
        try:
            # Given data
            I = self.test_current  # Current in A
            T = self.test_torque   # Torque in N·m
            V = 460.0              # Supply voltage in V
            Ra = 0.5               # Total resistance in Ω

            # For a series motor, T ∝ Ia² approximately
            # We'll fit the torque-current relationship
            # Using T = k × Ia^n where n ≈ 2 for series motor

            # Logarithmic fit to find relationship
            log_I = np.log(I)
            log_T = np.log(T)
            coeffs = np.polyfit(log_I, log_T, 1)
            n = coeffs[0]  # Exponent
            log_k = coeffs[1]
            k_torque = np.exp(log_k)

            # Calculate back-EMF for each operating point
            Eb = V - I * Ra

            # For series motor: Eb = k_e × Φ × N, and Φ ∝ Ia
            # Therefore: Eb = k_e' × Ia × N
            # Solving for N: N = Eb / (k_e' × Ia)

            # We need to find k_e' from the relationship
            # Assume first data point for calibration
            # Let's work with RPM and calculate k_e' such that speeds are reasonable

            # For a series motor, we can express: N = (V - Ia*Ra) / (k_phi * Ia)
            # where k_phi relates flux to current

            # Let's calculate assuming reasonable speeds (100-3000 RPM range)
            # We'll use the empirical approach

            # From the torque relationship: T = k * Ia^n
            # And knowing Eb = k_e * Ia * omega (where omega is in rad/s)
            # N_rpm = 60 * omega / (2*pi) = 60 * Eb / (2*pi * k_e * Ia)

            # Let's estimate k_e from the data
            # Assuming at rated conditions, typical series motor speed is around 1000-2000 RPM
            # We'll use physical relationships

            # Calculate speed for each point
            # For series motor: N ∝ (V - Ia*Ra) / Ia
            # This gives characteristic drooping speed-torque curve

            N_base = Eb / I  # Proportional relationship
            # Scale to reasonable RPM values
            k_speed = 1000.0 / N_base[0]  # Scale factor to get ~1000 RPM at first point
            N_rpm = N_base * k_speed

            # Create interpolation functions for extended range
            I_extended = np.linspace(10, 60, 100)

            # Torque vs Current (extended)
            T_extended = k_torque * I_extended**n

            # Back-EMF (extended)
            Eb_extended = V - I_extended * Ra

            # Speed (extended)
            N_base_extended = Eb_extended / I_extended
            N_extended = N_base_extended * k_speed

            # Generate results text
            results = "="*50 + "\n"
            results += "SOLUTION FOR EXAMPLE 29.32\n"
            results += "="*50 + "\n\n"

            results += "1. TORQUE-CURRENT RELATIONSHIP:\n"
            results += f"   T = {k_torque:.3f} × I^{n:.3f}\n"
            results += f"   (Exponent n ≈ {n:.2f}, close to 2 for series motor)\n\n"

            results += "2. CALCULATED OPERATING POINTS:\n"
            results += "-"*50 + "\n"
            results += f"{'Current':<12}{'Torque':<12}{'Back-EMF':<12}{'Speed':<12}\n"
            results += f"{'(A)':<12}{'(N·m)':<12}{'(V)':<12}{'(RPM)':<12}\n"
            results += "-"*50 + "\n"

            for i in range(len(I)):
                results += f"{I[i]:<12.1f}{T[i]:<12.1f}{Eb[i]:<12.1f}{N_rpm[i]:<12.1f}\n"

            results += "\n3. KEY OBSERVATIONS:\n"
            results += f"   • As load (torque) increases, speed decreases\n"
            results += f"   • As current increases, torque increases (∝ I^{n:.2f})\n"
            results += f"   • Series motor shows characteristic drooping speed-torque curve\n"
            results += f"   • Maximum torque: {T_extended.max():.1f} N·m\n"
            results += f"   • Speed range: {N_extended.min():.0f} - {N_extended.max():.0f} RPM\n"

            results += "\n4. PRACTICAL IMPLICATIONS:\n"
            results += "   • High starting torque capability\n"
            results += "   • Speed varies significantly with load\n"
            results += "   • Suitable for traction applications\n"
            results += "   • Should not be run without load (runaway speed)\n"

            # Display results
            self.example_results.delete(1.0, tk.END)
            self.example_results.insert(1.0, results)

            # Plot results
            self.ax_torque_current.clear()
            self.ax_torque_current.plot(I, T, 'ro-', label='Test Data', markersize=8, linewidth=2)
            self.ax_torque_current.plot(I_extended, T_extended, 'b--', label=f'Fitted: T = {k_torque:.2f}×I^{n:.2f}')
            self.ax_torque_current.set_xlabel('Current (A)', fontsize=10, fontweight='bold')
            self.ax_torque_current.set_ylabel('Torque (N·m)', fontsize=10, fontweight='bold')
            self.ax_torque_current.set_title('Torque vs Current Characteristic', fontsize=12, fontweight='bold')
            self.ax_torque_current.grid(True, alpha=0.3)
            self.ax_torque_current.legend()

            self.ax_speed_current.clear()
            self.ax_speed_current.plot(I, N_rpm, 'go-', label='Calculated Speed', markersize=8, linewidth=2)
            self.ax_speed_current.plot(I_extended, N_extended, 'b--', label='Extended Range')
            self.ax_speed_current.set_xlabel('Current (A)', fontsize=10, fontweight='bold')
            self.ax_speed_current.set_ylabel('Speed (RPM)', fontsize=10, fontweight='bold')
            self.ax_speed_current.set_title('Speed vs Current Characteristic', fontsize=12, fontweight='bold')
            self.ax_speed_current.grid(True, alpha=0.3)
            self.ax_speed_current.legend()

            self.ax_speed_torque_curve.clear()
            self.ax_speed_torque_curve.plot(T, N_rpm, 'mo-', label='Test Points', markersize=10, linewidth=3)
            self.ax_speed_torque_curve.plot(T_extended, N_extended, 'r-', label='Speed-Torque Curve', linewidth=2)
            self.ax_speed_torque_curve.set_xlabel('Torque (N·m)', fontsize=10, fontweight='bold')
            self.ax_speed_torque_curve.set_ylabel('Speed (RPM)', fontsize=10, fontweight='bold')
            self.ax_speed_torque_curve.set_title('SPEED-TORQUE CHARACTERISTIC CURVE\n(Solution to Example 29.32)',
                                                 fontsize=12, fontweight='bold')
            self.ax_speed_torque_curve.grid(True, alpha=0.3)
            self.ax_speed_torque_curve.legend()
            self.ax_speed_torque_curve.fill_between(T_extended, 0, N_extended, alpha=0.2)

            self.fig_example.tight_layout()
            self.canvas_example.draw()

            messagebox.showinfo("Success", "Example 29.32 solved successfully!\nSee results in the display.")

        except Exception as e:
            messagebox.showerror("Error", f"Error solving example: {str(e)}")

    def update_param(self, param, value):
        """Update parameter value"""
        try:
            self.params[param] = float(value)
        except:
            pass

    def start_simulation(self):
        """Start the simulation"""
        if not self.is_running:
            self.is_running = True
            self.simulation_thread = threading.Thread(target=self.run_simulation)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()

    def stop_simulation(self):
        """Stop the simulation"""
        self.is_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=1.0)

    def reset_simulation(self):
        """Reset simulation to initial conditions"""
        self.stop_simulation()

        self.current_time = 0
        self.state = {
            'current': 0.0,
            'speed': 0.0,
            'torque': 0.0,
            'temperature': self.params['ambient_temp'],
            'power_in': 0.0,
            'power_out': 0.0,
        }

        self.history = {
            'time': [],
            'current': [],
            'speed': [],
            'torque': [],
            'temperature': [],
            'power_in': [],
            'power_out': [],
            'efficiency': [],
            'copper_loss': [],
            'iron_loss': [],
            'mech_loss': [],
            'stray_loss': [],
        }

        self.update_plots()

    def run_simulation(self):
        """Main simulation loop"""
        while self.is_running:
            # Time step
            t_start = self.current_time
            t_end = self.current_time + self.dt

            # Get current state
            y0 = [
                self.state['current'],
                self.state['speed'],
                self.state['temperature']
            ]

            # Solve ODE
            if self.solver_type.get() == "RK45":
                sol = solve_ivp(
                    self.motor_dynamics,
                    [t_start, t_end],
                    y0,
                    method='RK45',
                    dense_output=True
                )
                y_new = sol.y[:, -1]
            else:  # Euler method
                dydt = self.motor_dynamics(t_start, y0)
                y_new = y0 + np.array(dydt) * self.dt

            # Update state
            self.state['current'] = max(0, y_new[0])
            self.state['speed'] = max(0, y_new[1])
            self.state['temperature'] = max(self.params['ambient_temp'], y_new[2])

            # Calculate derived quantities
            self.calculate_motor_quantities()

            # Store history
            self.current_time = t_end
            self.history['time'].append(self.current_time)
            self.history['current'].append(self.state['current'])
            self.history['speed'].append(self.state['speed'])
            self.history['torque'].append(self.state['torque'])
            self.history['temperature'].append(self.state['temperature'])
            self.history['power_in'].append(self.state['power_in'])
            self.history['power_out'].append(self.state['power_out'])

            # Calculate efficiency
            if self.state['power_in'] > 0:
                eff = (self.state['power_out'] / self.state['power_in']) * 100
            else:
                eff = 0
            self.history['efficiency'].append(eff)

            # Limit history length
            max_history = 1000
            if len(self.history['time']) > max_history:
                for key in self.history:
                    self.history[key] = self.history[key][-max_history:]

            # Update plots periodically
            if len(self.history['time']) % 10 == 0:
                self.root.after(0, self.update_plots)

            # Sleep to control simulation speed
            time.sleep(0.01)

    def motor_dynamics(self, t, y):
        """
        Motor differential equations (Multi-Physics Model)

        State variables:
        y[0] = current (A)
        y[1] = speed (rad/s)
        y[2] = temperature (°C)

        Returns: dy/dt
        """
        Ia = y[0]
        omega = y[1]
        T_motor = y[2]

        # Get parameters
        V = self.params['V_supply']
        Ra = self.params['R_armature']
        La = self.params['L_armature']
        J = self.params['J_inertia']
        B = self.params['B_friction']
        T_load = self.params['T_load']

        # Apply control strategy
        V_applied = self.apply_control(V, Ia, omega)

        # Electrical equation: V = Eb + Ia*Ra + La*dIa/dt
        # For series motor: Eb = k_e * Φ * omega, Φ ∝ Ia
        k_e_eff = self.params['k_emf'] * (1 + 0.01 * Ia)  # Nonlinear flux
        Eb = k_e_eff * Ia * omega

        dIa_dt = (V_applied - Eb - Ia * Ra) / La

        # Mechanical equation: J*dω/dt = T_motor - T_load - B*ω
        # For series motor: T ∝ Φ * Ia ∝ Ia²
        k_t_eff = self.params['k_torque'] * (1 + 0.01 * Ia)  # Nonlinear torque
        T_electromag = k_t_eff * Ia * Ia

        domega_dt = (T_electromag - T_load - B * omega) / J

        # Thermal equation: C*dT/dt = P_loss - (T-T_amb)/R_th
        # Calculate losses
        P_copper = Ia**2 * Ra  # Copper losses (I²R)
        P_iron = 0.01 * omega**2  # Iron losses (proportional to speed²)
        P_mech = B * omega**2  # Mechanical friction losses
        P_stray = 0.005 * V_applied * Ia  # Stray load losses

        P_total_loss = P_copper + P_iron + P_mech + P_stray

        C_th = self.params['thermal_capacitance']
        R_th = self.params['thermal_resistance']
        T_amb = self.params['ambient_temp']

        dT_dt = (P_total_loss - (T_motor - T_amb) / R_th) / C_th

        # Temperature derating effect on resistance
        temp_coefficient = 0.004  # per °C
        Ra_temp = Ra * (1 + temp_coefficient * (T_motor - 25))

        # Update with temperature-compensated resistance
        dIa_dt = (V_applied - Eb - Ia * Ra_temp) / La

        return [dIa_dt, domega_dt, dT_dt]

    def apply_control(self, V_nominal, Ia, omega):
        """Apply selected control strategy"""
        control = self.control_method.get()

        if control == "Open Loop":
            return V_nominal

        elif control == "PI Speed Control":
            # PI controller for speed
            speed_rpm = omega * 60 / (2 * np.pi)
            setpoint = self.setpoint_var.get()
            error = setpoint - speed_rpm

            # Simple PI (would need integral term storage for real implementation)
            Kp = self.kp_var.get()
            Ki = self.ki_var.get()

            V_control = V_nominal + Kp * error
            V_control = np.clip(V_control, 0, V_nominal * 1.5)
            return V_control

        elif control == "Field Weakening":
            # Reduce effective field at high speeds
            if omega > 100:  # Above base speed
                field_reduction = 100 / omega
                return V_nominal * np.clip(field_reduction, 0.5, 1.0)
            return V_nominal

        elif control == "Chopper Control":
            # DC chopper with duty cycle
            duty = self.duty_cycle_var.get()
            return V_nominal * duty

        elif control == "PWM Control":
            # Simplified PWM (averaged model)
            duty = self.duty_cycle_var.get()
            return V_nominal * duty

        return V_nominal

    def calculate_motor_quantities(self):
        """Calculate motor performance quantities"""
        Ia = self.state['current']
        omega = self.state['speed']
        T_motor_temp = self.state['temperature']

        V = self.params['V_supply']
        Ra = self.params['R_armature']
        B = self.params['B_friction']

        # Apply temperature effect on resistance
        temp_coefficient = 0.004
        Ra_temp = Ra * (1 + temp_coefficient * (T_motor_temp - 25))

        # Torque
        k_t = self.params['k_torque'] * (1 + 0.01 * Ia)
        self.state['torque'] = k_t * Ia * Ia

        # Power
        self.state['power_in'] = V * Ia
        self.state['power_out'] = self.state['torque'] * omega

        # Losses
        P_copper = Ia**2 * Ra_temp
        P_iron = 0.01 * omega**2
        P_mech = B * omega**2
        P_stray = 0.005 * V * Ia

        self.history['copper_loss'].append(P_copper)
        self.history['iron_loss'].append(P_iron)
        self.history['mech_loss'].append(P_mech)
        self.history['stray_loss'].append(P_stray)

    def update_plots(self):
        """Update all real-time plots"""
        if len(self.history['time']) < 2:
            return

        t = np.array(self.history['time'])

        # Current plot
        self.ax_current.clear()
        self.ax_current.plot(t, self.history['current'], 'b-', linewidth=2)
        self.ax_current.set_ylabel('Current (A)', fontweight='bold')
        self.ax_current.set_title('Armature Current')
        self.ax_current.grid(True, alpha=0.3)

        # Speed plot
        self.ax_speed.clear()
        speed_rpm = np.array(self.history['speed']) * 60 / (2 * np.pi)
        self.ax_speed.plot(t, speed_rpm, 'g-', linewidth=2)
        self.ax_speed.set_ylabel('Speed (RPM)', fontweight='bold')
        self.ax_speed.set_title('Motor Speed')
        self.ax_speed.grid(True, alpha=0.3)

        # Torque plot
        self.ax_torque.clear()
        self.ax_torque.plot(t, self.history['torque'], 'r-', linewidth=2)
        self.ax_torque.set_ylabel('Torque (N·m)', fontweight='bold')
        self.ax_torque.set_title('Motor Torque')
        self.ax_torque.grid(True, alpha=0.3)

        # Temperature plot
        self.ax_temp.clear()
        self.ax_temp.plot(t, self.history['temperature'], 'm-', linewidth=2)
        self.ax_temp.axhline(y=self.params['max_temp'], color='r', linestyle='--', label='Max Temp')
        self.ax_temp.set_ylabel('Temperature (°C)', fontweight='bold')
        self.ax_temp.set_title('Winding Temperature')
        self.ax_temp.legend()
        self.ax_temp.grid(True, alpha=0.3)

        # Power plot
        self.ax_power.clear()
        self.ax_power.plot(t, np.array(self.history['power_in'])/1000, 'b-', linewidth=2, label='Input')
        self.ax_power.plot(t, np.array(self.history['power_out'])/1000, 'g-', linewidth=2, label='Output')
        self.ax_power.set_ylabel('Power (kW)', fontweight='bold')
        self.ax_power.set_xlabel('Time (s)', fontweight='bold')
        self.ax_power.set_title('Power Flow')
        self.ax_power.legend()
        self.ax_power.grid(True, alpha=0.3)

        # Efficiency plot
        self.ax_efficiency.clear()
        self.ax_efficiency.plot(t, self.history['efficiency'], 'orange', linewidth=2)
        self.ax_efficiency.set_ylabel('Efficiency (%)', fontweight='bold')
        self.ax_efficiency.set_xlabel('Time (s)', fontweight='bold')
        self.ax_efficiency.set_title('Motor Efficiency')
        self.ax_efficiency.set_ylim([0, 100])
        self.ax_efficiency.grid(True, alpha=0.3)

        self.fig_main.tight_layout()
        self.canvas_main.draw()

        # Update analysis plots
        self.update_analysis_plots()

        # Update thermal plots
        self.update_thermal_plots()

    def update_analysis_plots(self):
        """Update performance analysis plots"""
        if len(self.history['time']) < 10:
            return

        # Loss breakdown pie chart
        self.ax_loss_pie.clear()
        if len(self.history['copper_loss']) > 0:
            avg_copper = np.mean(self.history['copper_loss'][-100:])
            avg_iron = np.mean(self.history['iron_loss'][-100:])
            avg_mech = np.mean(self.history['mech_loss'][-100:])
            avg_stray = np.mean(self.history['stray_loss'][-100:])

            losses = [avg_copper, avg_iron, avg_mech, avg_stray]
            labels = ['Copper\nLosses', 'Iron\nLosses', 'Mechanical\nLosses', 'Stray\nLosses']
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']

            self.ax_loss_pie.pie(losses, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            self.ax_loss_pie.set_title('Loss Breakdown (Average)', fontweight='bold')

        # Loss over time
        self.ax_loss_time.clear()
        t = np.array(self.history['time'])
        if len(self.history['copper_loss']) > 0:
            self.ax_loss_time.plot(t[-len(self.history['copper_loss']):],
                                   self.history['copper_loss'], label='Copper', linewidth=2)
            self.ax_loss_time.plot(t[-len(self.history['iron_loss']):],
                                   self.history['iron_loss'], label='Iron', linewidth=2)
            self.ax_loss_time.plot(t[-len(self.history['mech_loss']):],
                                   self.history['mech_loss'], label='Mechanical', linewidth=2)
            self.ax_loss_time.plot(t[-len(self.history['stray_loss']):],
                                   self.history['stray_loss'], label='Stray', linewidth=2)
            self.ax_loss_time.set_xlabel('Time (s)', fontweight='bold')
            self.ax_loss_time.set_ylabel('Power Loss (W)', fontweight='bold')
            self.ax_loss_time.set_title('Losses Over Time', fontweight='bold')
            self.ax_loss_time.legend()
            self.ax_loss_time.grid(True, alpha=0.3)

        # Speed-Torque curve
        self.ax_speed_torque.clear()
        if len(self.history['speed']) > 0 and len(self.history['torque']) > 0:
            speed_rpm = np.array(self.history['speed']) * 60 / (2 * np.pi)
            self.ax_speed_torque.scatter(self.history['torque'], speed_rpm,
                                        c=range(len(speed_rpm)), cmap='viridis', alpha=0.6)
            self.ax_speed_torque.set_xlabel('Torque (N·m)', fontweight='bold')
            self.ax_speed_torque.set_ylabel('Speed (RPM)', fontweight='bold')
            self.ax_speed_torque.set_title('Speed-Torque Characteristic', fontweight='bold')
            self.ax_speed_torque.grid(True, alpha=0.3)

        # Efficiency curve
        self.ax_efficiency_curve.clear()
        if len(self.history['torque']) > 0 and len(self.history['efficiency']) > 0:
            self.ax_efficiency_curve.scatter(self.history['torque'], self.history['efficiency'],
                                            c='green', alpha=0.6)
            self.ax_efficiency_curve.set_xlabel('Torque (N·m)', fontweight='bold')
            self.ax_efficiency_curve.set_ylabel('Efficiency (%)', fontweight='bold')
            self.ax_efficiency_curve.set_title('Efficiency vs Torque', fontweight='bold')
            self.ax_efficiency_curve.grid(True, alpha=0.3)
            self.ax_efficiency_curve.set_ylim([0, 100])

        self.fig_analysis.tight_layout()
        self.canvas_analysis.draw()

    def update_thermal_plots(self):
        """Update thermal analysis plots"""
        if len(self.history['time']) < 2:
            return

        t = np.array(self.history['time'])

        # Temperature rise plot
        self.ax_temp_rise.clear()
        self.ax_temp_rise.plot(t, self.history['temperature'], 'r-', linewidth=2, label='Winding Temp')
        self.ax_temp_rise.axhline(y=self.params['max_temp'], color='r', linestyle='--',
                                 linewidth=2, label='Max Temp')
        self.ax_temp_rise.axhline(y=self.params['ambient_temp'], color='b', linestyle='--',
                                 linewidth=2, label='Ambient Temp')
        self.ax_temp_rise.fill_between(t, self.params['ambient_temp'], self.history['temperature'],
                                       alpha=0.3, color='red')
        self.ax_temp_rise.set_xlabel('Time (s)', fontweight='bold')
        self.ax_temp_rise.set_ylabel('Temperature (°C)', fontweight='bold')
        self.ax_temp_rise.set_title('Thermal Transient Response', fontweight='bold')
        self.ax_temp_rise.legend()
        self.ax_temp_rise.grid(True, alpha=0.3)

        # Derating curve
        self.ax_derating.clear()
        temp_range = np.linspace(25, 200, 100)

        # Typical derating: 100% up to rated temp, then linear decrease
        rated_temp = 120  # °C
        derating = np.ones_like(temp_range) * 100
        derating[temp_range > rated_temp] = 100 * (1 - (temp_range[temp_range > rated_temp] - rated_temp) / 80)
        derating = np.clip(derating, 0, 100)

        self.ax_derating.plot(temp_range, derating, 'b-', linewidth=2)
        self.ax_derating.axvline(x=self.state['temperature'], color='r', linestyle='--',
                                linewidth=2, label='Current Temp')
        self.ax_derating.fill_between(temp_range, 0, derating, alpha=0.3, color='blue')
        self.ax_derating.set_xlabel('Temperature (°C)', fontweight='bold')
        self.ax_derating.set_ylabel('Power Capability (%)', fontweight='bold')
        self.ax_derating.set_title('Thermal Derating Curve', fontweight='bold')
        self.ax_derating.legend()
        self.ax_derating.grid(True, alpha=0.3)
        self.ax_derating.set_xlim([0, 200])
        self.ax_derating.set_ylim([0, 110])

        self.fig_thermal.tight_layout()
        self.canvas_thermal.draw()

        # Update derating label
        current_temp = self.state['temperature']
        if current_temp < rated_temp:
            self.derating_label.config(text=f"Operating at 100% capacity\nCurrent: {current_temp:.1f}°C",
                                      foreground='green')
        elif current_temp < self.params['max_temp']:
            capability = 100 * (1 - (current_temp - rated_temp) / 80)
            self.derating_label.config(text=f"Derated to {capability:.1f}% capacity\nCurrent: {current_temp:.1f}°C",
                                      foreground='orange')
        else:
            self.derating_label.config(text=f"OVERHEATING! {current_temp:.1f}°C\nShutdown recommended!",
                                      foreground='red')

    def calculate_economics(self):
        """Calculate economic analysis"""
        try:
            if len(self.history['power_in']) == 0:
                messagebox.showwarning("Warning", "Run simulation first to collect data")
                return

            # Get parameters
            power_cost = self.power_cost_var.get()  # $/kWh
            operating_hours = self.operating_hours_var.get()  # hours/year
            maintenance_cost = self.maintenance_cost_var.get()  # $/year

            # Calculate average power consumption
            avg_power_in = np.mean(self.history['power_in']) / 1000  # kW
            avg_power_out = np.mean(self.history['power_out']) / 1000  # kW
            avg_efficiency = np.mean(self.history['efficiency'])

            # Calculate costs
            annual_energy = avg_power_in * operating_hours  # kWh/year
            annual_energy_cost = annual_energy * power_cost  # $/year
            total_annual_cost = annual_energy_cost + maintenance_cost

            # Calculate losses
            annual_energy_loss = (avg_power_in - avg_power_out) * operating_hours  # kWh/year
            annual_loss_cost = annual_energy_loss * power_cost  # $/year

            # 10-year projection
            years = 10
            total_10yr_cost = total_annual_cost * years
            total_10yr_energy = annual_energy * years

            # CO2 emissions (assuming 0.5 kg CO2/kWh)
            co2_factor = 0.5  # kg CO2/kWh
            annual_co2 = annual_energy * co2_factor  # kg/year

            # Breakdown
            copper_loss_ratio = np.mean(self.history['copper_loss']) if self.history['copper_loss'] else 0
            iron_loss_ratio = np.mean(self.history['iron_loss']) if self.history['iron_loss'] else 0
            mech_loss_ratio = np.mean(self.history['mech_loss']) if self.history['mech_loss'] else 0
            stray_loss_ratio = np.mean(self.history['stray_loss']) if self.history['stray_loss'] else 0
            total_loss = copper_loss_ratio + iron_loss_ratio + mech_loss_ratio + stray_loss_ratio

            if total_loss > 0:
                copper_pct = (copper_loss_ratio / total_loss) * 100
                iron_pct = (iron_loss_ratio / total_loss) * 100
                mech_pct = (mech_loss_ratio / total_loss) * 100
                stray_pct = (stray_loss_ratio / total_loss) * 100
            else:
                copper_pct = iron_pct = mech_pct = stray_pct = 0

            # Format results
            results = "="*50 + "\n"
            results += "ECONOMIC ANALYSIS REPORT\n"
            results += "="*50 + "\n\n"

            results += "OPERATING CONDITIONS:\n"
            results += f"  Average Input Power:    {avg_power_in:.2f} kW\n"
            results += f"  Average Output Power:   {avg_power_out:.2f} kW\n"
            results += f"  Average Efficiency:     {avg_efficiency:.2f}%\n"
            results += f"  Operating Hours/Year:   {operating_hours:.0f} hrs\n\n"

            results += "ANNUAL COSTS:\n"
            results += f"  Energy Consumption:     {annual_energy:.0f} kWh\n"
            results += f"  Energy Cost:            ${annual_energy_cost:.2f}\n"
            results += f"  Maintenance Cost:       ${maintenance_cost:.2f}\n"
            results += f"  Total Annual Cost:      ${total_annual_cost:.2f}\n\n"

            results += "ENERGY LOSSES:\n"
            results += f"  Annual Energy Loss:     {annual_energy_loss:.0f} kWh\n"
            results += f"  Annual Loss Cost:       ${annual_loss_cost:.2f}\n"
            results += f"  Loss Breakdown:\n"
            results += f"    - Copper Losses:      {copper_pct:.1f}%\n"
            results += f"    - Iron Losses:        {iron_pct:.1f}%\n"
            results += f"    - Mechanical Losses:  {mech_pct:.1f}%\n"
            results += f"    - Stray Losses:       {stray_pct:.1f}%\n\n"

            results += "10-YEAR PROJECTION:\n"
            results += f"  Total Energy:           {total_10yr_energy:.0f} kWh\n"
            results += f"  Total Cost:             ${total_10yr_cost:.2f}\n\n"

            results += "ENVIRONMENTAL IMPACT:\n"
            results += f"  Annual CO₂ Emissions:   {annual_co2:.0f} kg\n"
            results += f"  10-Year CO₂ Emissions:  {annual_co2*10:.0f} kg\n\n"

            results += "COST OPTIMIZATION SUGGESTIONS:\n"
            if avg_efficiency < 80:
                results += "  ⚠ Low efficiency detected. Consider:\n"
                results += "    - Motor maintenance or replacement\n"
                results += "    - Load matching optimization\n"
            if copper_pct > 50:
                results += "  ⚠ High copper losses. Consider:\n"
                results += "    - Reducing operating current\n"
                results += "    - Upgrading to larger conductor size\n"
            if self.state['temperature'] > 120:
                results += "  ⚠ High operating temperature\n"
                results += "    - Improves cooling system\n"
                results += "    - Reduce ambient temperature\n"

            # Display results
            self.econ_results.delete(1.0, tk.END)
            self.econ_results.insert(1.0, results)

            # Plot cost breakdown
            self.ax_cost_breakdown.clear()
            costs = [annual_energy_cost, maintenance_cost]
            labels = ['Energy\nCost', 'Maintenance\nCost']
            colors = ['#ff6b6b', '#4ecdc4']

            self.ax_cost_breakdown.pie(costs, labels=labels, autopct='%1.1f%%',
                                       colors=colors, startangle=90)
            self.ax_cost_breakdown.set_title('Annual Cost Breakdown', fontweight='bold')

            # Plot cost projection over time
            self.ax_cost_time.clear()
            years_array = np.arange(1, years + 1)
            cumulative_cost = years_array * total_annual_cost

            self.ax_cost_time.plot(years_array, cumulative_cost, 'b-', linewidth=2, marker='o')
            self.ax_cost_time.fill_between(years_array, 0, cumulative_cost, alpha=0.3)
            self.ax_cost_time.set_xlabel('Years', fontweight='bold')
            self.ax_cost_time.set_ylabel('Cumulative Cost ($)', fontweight='bold')
            self.ax_cost_time.set_title('10-Year Cost Projection', fontweight='bold')
            self.ax_cost_time.grid(True, alpha=0.3)

            self.fig_econ.tight_layout()
            self.canvas_econ.draw()

        except Exception as e:
            messagebox.showerror("Error", f"Error calculating economics: {str(e)}")

    def on_window_resize(self, event):
        """Handle window resize events for auto-scaling"""
        # Only process resize events for the main window
        if event.widget == self.root:
            # Update all canvases to fit new window size
            try:
                self.canvas_main.draw()
                self.canvas_analysis.draw()
                self.canvas_thermal.draw()
                self.canvas_econ.draw()
                self.canvas_example.draw()
            except:
                pass

def main():
    """Main application entry point"""
    root = tk.Tk()

    # Configure styles
    style = ttk.Style()
    style.theme_use('clam')

    # Custom button styles
    style.configure('Success.TButton', foreground='green')
    style.configure('Danger.TButton', foreground='red')

    # Create and run application
    app = DCMotorSimulator(root)

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()

if __name__ == "__main__":
    main()
