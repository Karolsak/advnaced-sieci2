"""
Advanced 3-Phase Induction Motor Simulator with Multi-Physics Analysis
Includes: Auto-transformer starter calculations, Dynamic simulation,
Thermal analysis, Economic analysis, and Advanced controls
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.integrate import solve_ivp, odeint
import threading
import time
from datetime import datetime

class InductionMotorSimulator:
    """
    Advanced Induction Motor Simulator with Multi-Physics Modeling
    """

    def __init__(self):
        # Motor parameters (default values from the problem)
        self.V_rated = 400.0  # Rated voltage (V) - Line voltage
        self.V_phase = self.V_rated / np.sqrt(3)  # Phase voltage
        self.I_fl = 30.0  # Full load current (A)
        self.slip_fl = 0.04  # Full load slip
        self.Z_standstill = 1.54  # Standstill impedance per phase (Ω)
        self.I_max_line = 75.0  # Maximum starting current from line (A)
        self.f = 50.0  # Frequency (Hz)
        self.poles = 4  # Number of poles
        self.rated_power = 15000.0  # Rated power (W) - 15 kW

        # Derived parameters
        self.omega_s = 2 * np.pi * self.f  # Synchronous angular frequency
        self.n_s = 120 * self.f / self.poles  # Synchronous speed (rpm)

        # Motor equivalent circuit parameters
        self.R1 = 0.5  # Stator resistance (Ω)
        self.R2 = 0.6  # Rotor resistance (Ω)
        self.X1 = 1.0  # Stator leakage reactance (Ω)
        self.X2 = 1.0  # Rotor leakage reactance (Ω)
        self.Xm = 50.0  # Magnetizing reactance (Ω)

        # Mechanical parameters
        self.J = 0.5  # Moment of inertia (kg·m²)
        self.B = 0.01  # Friction coefficient (N·m·s)

        # Thermal parameters
        self.thermal_resistance = 2.0  # °C/W
        self.thermal_capacitance = 500.0  # J/°C
        self.ambient_temp = 25.0  # °C
        self.max_temp = 155.0  # Maximum winding temperature (°C)

        # Economic parameters
        self.electricity_cost = 0.12  # $/kWh
        self.motor_cost = 2000.0  # Initial cost ($)
        self.maintenance_cost_annual = 200.0  # $/year

        # Simulation parameters
        self.dt = 0.001  # Time step (s)
        self.simulation_time = 10.0  # Total simulation time (s)
        self.solver_method = 'RK45'  # ODE solver method

        # State variables
        self.is_running = False
        self.current_time = 0.0
        self.omega_m = 0.0  # Mechanical angular velocity
        self.theta_m = 0.0  # Mechanical angle
        self.temperature = self.ambient_temp

        # Data storage
        self.time_data = []
        self.speed_data = []
        self.torque_data = []
        self.current_data = []
        self.power_data = []
        self.efficiency_data = []
        self.temp_data = []
        self.loss_data = {'copper': [], 'iron': [], 'mechanical': [], 'stray': []}

        # Control parameters
        self.load_torque = 50.0  # Load torque (N·m)
        self.voltage_control = 1.0  # Voltage control factor (0-1)
        self.frequency_control = 1.0  # Frequency control factor (0-1)

        # Auto-transformer starter results
        self.auto_transformer_tapping = 0.0
        self.starting_torque_ratio = 0.0

    def calculate_auto_transformer_starter(self):
        """
        Calculate auto-transformer tapping and starting torque ratio
        """
        # Calculate starting current at full voltage
        V_phase = self.V_rated / np.sqrt(3)
        I_st_full = V_phase / self.Z_standstill
        I_st_line_full = np.sqrt(3) * I_st_full  # Line current at starting

        # For auto-transformer: I_line = α² * I_motor
        # Where α is the tapping ratio
        # I_motor at reduced voltage = α * I_st_full
        # I_line = α² * I_st_full (per phase)
        # Line current = √3 * α² * I_st_full

        # We need: √3 * α² * I_st_full = I_max_line
        alpha_squared = self.I_max_line / (np.sqrt(3) * I_st_full)
        alpha = np.sqrt(alpha_squared)

        self.auto_transformer_tapping = alpha * 100  # Convert to percentage

        # Calculate torques
        # Starting torque at full voltage
        T_st_full = 3 * (V_phase**2) * self.R2 / (self.omega_s * self.Z_standstill**2)

        # Starting torque at reduced voltage (proportional to V²)
        T_st_reduced = alpha**2 * T_st_full

        # Full load torque
        # At full load: slip = slip_fl
        Z_fl = np.sqrt((self.R1 + self.R2/self.slip_fl)**2 + (self.X1 + self.X2)**2)
        I_fl_calc = V_phase / Z_fl
        T_fl = 3 * I_fl_calc**2 * (self.R2/self.slip_fl) / self.omega_s

        self.starting_torque_ratio = T_st_reduced / T_fl

        return alpha * 100, self.starting_torque_ratio

    def motor_dynamics_ode(self, t, y, V_applied, f_applied, T_load):
        """
        Differential equations for motor dynamics
        y = [i_d, i_q, psi_d, psi_q, omega_m, theta_m, T_temp]
        """
        i_d, i_q, psi_d, psi_q, omega_m, theta_m, T_temp = y

        # Electrical angular velocity
        omega_e = 2 * np.pi * f_applied

        # Slip
        omega_r = omega_m * (self.poles / 2)
        slip_omega = omega_e - omega_r

        # Voltage in dq frame (RMS to peak conversion)
        V_d = V_applied * np.sqrt(2) * np.cos(omega_e * t)
        V_q = V_applied * np.sqrt(2) * np.sin(omega_e * t)

        # Electrical equations (simplified dq model)
        L_s = self.X1 / omega_e + self.Xm / omega_e
        L_r = self.X2 / omega_e + self.Xm / omega_e
        L_m = self.Xm / omega_e

        # Flux linkage derivatives
        dpsi_d = V_d - self.R1 * i_d + omega_e * psi_q
        dpsi_q = V_q - self.R1 * i_q - omega_e * psi_d

        # Current derivatives (simplified)
        di_d = (dpsi_d - L_m * (dpsi_d)) / L_s
        di_q = (dpsi_q - L_m * (dpsi_q)) / L_s

        # Electromagnetic torque (RMS values)
        I_rms = np.sqrt(i_d**2 + i_q**2) / np.sqrt(2)
        slip_current = abs(slip_omega) / omega_e if omega_e > 0 else 1.0
        slip_current = max(0.001, min(1.0, slip_current))

        T_em = 3 * I_rms**2 * self.R2 / (slip_current * omega_e) if omega_e > 0 else 0

        # Mechanical equation
        domega_m = (T_em - T_load - self.B * omega_m) / self.J
        dtheta_m = omega_m

        # Thermal equation
        # Total losses
        P_copper = 3 * I_rms**2 * (self.R1 + self.R2)
        P_iron = 0.02 * V_applied**2  # Simplified iron loss
        P_mechanical = self.B * omega_m**2
        P_total_loss = P_copper + P_iron + P_mechanical

        # Temperature dynamics
        dT_temp = (P_total_loss - (T_temp - self.ambient_temp) / self.thermal_resistance) / self.thermal_capacitance

        return [di_d, di_q, dpsi_d, dpsi_q, domega_m, dtheta_m, dT_temp]

    def simplified_motor_ode(self, t, y):
        """
        Simplified motor dynamics for faster simulation
        y = [omega_m, theta_m, temperature]
        """
        omega_m, theta_m, temperature = y

        # Applied voltage and frequency
        V_applied = self.voltage_control * self.V_phase
        f_applied = self.frequency_control * self.f
        omega_e = 2 * np.pi * f_applied

        # Slip
        omega_r = omega_m * (self.poles / 2)
        slip = (omega_e - omega_r) / omega_e if omega_e > 0 else 1.0
        slip = max(0.001, min(1.0, slip))

        # Equivalent impedance
        R_eq = self.R1 + self.R2 / slip
        X_eq = self.X1 + self.X2
        Z_eq = np.sqrt(R_eq**2 + X_eq**2)

        # Current (RMS)
        I_rms = V_applied / Z_eq

        # Electromagnetic torque
        T_em = 3 * I_rms**2 * (self.R2 / slip) / omega_e if omega_e > 0 else 0

        # Mechanical dynamics
        domega_m = (T_em - self.load_torque - self.B * omega_m) / self.J
        dtheta_m = omega_m

        # Losses
        P_copper_stator = 3 * I_rms**2 * self.R1
        P_copper_rotor = 3 * I_rms**2 * self.R2
        P_iron = 0.02 * V_applied**2
        P_mechanical = self.B * omega_m**2
        P_stray = 0.01 * (P_copper_stator + P_copper_rotor)

        P_total_loss = P_copper_stator + P_copper_rotor + P_iron + P_mechanical + P_stray

        # Thermal dynamics
        dtemperature = (P_total_loss - (temperature - self.ambient_temp) / self.thermal_resistance) / self.thermal_capacitance

        return [domega_m, dtheta_m, dtemperature]

    def calculate_performance_at_time(self, t, y):
        """Calculate detailed performance metrics"""
        omega_m, theta_m, temperature = y

        # Applied voltage and frequency
        V_applied = self.voltage_control * self.V_phase
        f_applied = self.frequency_control * self.f
        omega_e = 2 * np.pi * f_applied

        # Slip
        omega_r = omega_m * (self.poles / 2)
        slip = (omega_e - omega_r) / omega_e if omega_e > 0 else 1.0
        slip = max(0.001, min(1.0, slip))

        # Equivalent impedance
        R_eq = self.R1 + self.R2 / slip
        X_eq = self.X1 + self.X2
        Z_eq = np.sqrt(R_eq**2 + X_eq**2)

        # Current (RMS)
        I_rms = V_applied / Z_eq

        # Electromagnetic torque
        T_em = 3 * I_rms**2 * (self.R2 / slip) / omega_e if omega_e > 0 else 0

        # Speed in RPM
        n_rpm = omega_m * 60 / (2 * np.pi)

        # Power
        P_in = 3 * V_applied * I_rms * np.cos(np.arctan(X_eq / R_eq))
        P_out = T_em * omega_m

        # Losses breakdown
        P_copper_stator = 3 * I_rms**2 * self.R1
        P_copper_rotor = 3 * I_rms**2 * self.R2
        P_iron = 0.02 * V_applied**2
        P_mechanical = self.B * omega_m**2
        P_stray = 0.01 * (P_copper_stator + P_copper_rotor)

        # Efficiency
        efficiency = (P_out / P_in * 100) if P_in > 0 else 0

        return {
            'speed_rpm': n_rpm,
            'torque': T_em,
            'current': I_rms * np.sqrt(3),  # Line current
            'power_in': P_in,
            'power_out': P_out,
            'efficiency': efficiency,
            'temperature': temperature,
            'losses': {
                'copper_stator': P_copper_stator,
                'copper_rotor': P_copper_rotor,
                'iron': P_iron,
                'mechanical': P_mechanical,
                'stray': P_stray
            }
        }

    def run_simulation(self, progress_callback=None):
        """Run dynamic simulation"""
        # Initial conditions [omega_m, theta_m, temperature]
        y0 = [0.0, 0.0, self.ambient_temp]

        # Time span
        t_span = (0, self.simulation_time)
        t_eval = np.linspace(0, self.simulation_time, int(self.simulation_time / self.dt))

        # Clear previous data
        self.time_data = []
        self.speed_data = []
        self.torque_data = []
        self.current_data = []
        self.power_data = []
        self.efficiency_data = []
        self.temp_data = []
        self.loss_data = {'copper': [], 'iron': [], 'mechanical': [], 'stray': []}

        # Solve ODE
        if self.solver_method == 'RK45':
            sol = solve_ivp(self.simplified_motor_ode, t_span, y0, method='RK45',
                          t_eval=t_eval, max_step=self.dt)
            t_result = sol.t
            y_result = sol.y.T
        elif self.solver_method == 'Euler':
            # Manual Euler integration
            t_result = t_eval
            y_result = np.zeros((len(t_eval), 3))
            y_result[0] = y0

            for i in range(1, len(t_eval)):
                dt = t_eval[i] - t_eval[i-1]
                dydt = self.simplified_motor_ode(t_eval[i-1], y_result[i-1])
                y_result[i] = y_result[i-1] + np.array(dydt) * dt

                if progress_callback and i % 100 == 0:
                    progress_callback(i / len(t_eval) * 100)
        else:
            # Use odeint as fallback
            t_result = t_eval
            y_result = odeint(lambda y, t: self.simplified_motor_ode(t, y), y0, t_eval)

        # Process results
        for i, (t, y) in enumerate(zip(t_result, y_result)):
            perf = self.calculate_performance_at_time(t, y)

            self.time_data.append(t)
            self.speed_data.append(perf['speed_rpm'])
            self.torque_data.append(perf['torque'])
            self.current_data.append(perf['current'])
            self.power_data.append(perf['power_out'] / 1000)  # kW
            self.efficiency_data.append(perf['efficiency'])
            self.temp_data.append(perf['temperature'])

            total_copper = perf['losses']['copper_stator'] + perf['losses']['copper_rotor']
            self.loss_data['copper'].append(total_copper)
            self.loss_data['iron'].append(perf['losses']['iron'])
            self.loss_data['mechanical'].append(perf['losses']['mechanical'])
            self.loss_data['stray'].append(perf['losses']['stray'])

        return t_result, y_result


class MotorSimulatorGUI:
    """
    Advanced Tkinter GUI for Induction Motor Simulator
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced 3-Phase Induction Motor Simulator - Multi-Physics Analysis")
        self.root.geometry("1400x900")

        # Initialize simulator
        self.simulator = InductionMotorSimulator()

        # Simulation control
        self.is_simulating = False
        self.simulation_thread = None

        # Configure grid weights for auto-scaling
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Create tabs
        self.create_main_tab()
        self.create_starter_calculation_tab()
        self.create_simulation_tab()
        self.create_multiphysics_tab()
        self.create_advanced_controls_tab()
        self.create_economic_analysis_tab()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky='ew')

    def create_main_tab(self):
        """Create main menu and parameter input tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Main Menu & Parameters")

        # Configure grid
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Title
        title_frame = ttk.LabelFrame(tab, text="Motor Parameters Input", padding=10)
        title_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        # Parameter inputs
        params_frame = ttk.Frame(title_frame)
        params_frame.pack(fill='both', expand=True)

        row = 0
        # Voltage
        ttk.Label(params_frame, text="Rated Voltage (V):").grid(row=row, column=0, sticky='w', pady=2)
        self.voltage_entry = ttk.Entry(params_frame, width=15)
        self.voltage_entry.insert(0, str(self.simulator.V_rated))
        self.voltage_entry.grid(row=row, column=1, padx=5, pady=2)

        # Frequency
        ttk.Label(params_frame, text="Frequency (Hz):").grid(row=row, column=2, sticky='w', pady=2)
        self.freq_entry = ttk.Entry(params_frame, width=15)
        self.freq_entry.insert(0, str(self.simulator.f))
        self.freq_entry.grid(row=row, column=3, padx=5, pady=2)

        row += 1
        # Full load current
        ttk.Label(params_frame, text="Full Load Current (A):").grid(row=row, column=0, sticky='w', pady=2)
        self.fl_current_entry = ttk.Entry(params_frame, width=15)
        self.fl_current_entry.insert(0, str(self.simulator.I_fl))
        self.fl_current_entry.grid(row=row, column=1, padx=5, pady=2)

        # Full load slip
        ttk.Label(params_frame, text="Full Load Slip:").grid(row=row, column=2, sticky='w', pady=2)
        self.fl_slip_entry = ttk.Entry(params_frame, width=15)
        self.fl_slip_entry.insert(0, str(self.simulator.slip_fl))
        self.fl_slip_entry.grid(row=row, column=3, padx=5, pady=2)

        row += 1
        # Standstill impedance
        ttk.Label(params_frame, text="Standstill Impedance (Ω):").grid(row=row, column=0, sticky='w', pady=2)
        self.z_standstill_entry = ttk.Entry(params_frame, width=15)
        self.z_standstill_entry.insert(0, str(self.simulator.Z_standstill))
        self.z_standstill_entry.grid(row=row, column=1, padx=5, pady=2)

        # Max starting current
        ttk.Label(params_frame, text="Max Starting Current (A):").grid(row=row, column=2, sticky='w', pady=2)
        self.max_current_entry = ttk.Entry(params_frame, width=15)
        self.max_current_entry.insert(0, str(self.simulator.I_max_line))
        self.max_current_entry.grid(row=row, column=3, padx=5, pady=2)

        row += 1
        # Number of poles
        ttk.Label(params_frame, text="Number of Poles:").grid(row=row, column=0, sticky='w', pady=2)
        self.poles_entry = ttk.Entry(params_frame, width=15)
        self.poles_entry.insert(0, str(self.simulator.poles))
        self.poles_entry.grid(row=row, column=1, padx=5, pady=2)

        # Rated power
        ttk.Label(params_frame, text="Rated Power (W):").grid(row=row, column=2, sticky='w', pady=2)
        self.power_entry = ttk.Entry(params_frame, width=15)
        self.power_entry.insert(0, str(self.simulator.rated_power))
        self.power_entry.grid(row=row, column=3, padx=5, pady=2)

        row += 1
        ttk.Separator(params_frame, orient='horizontal').grid(row=row, column=0, columnspan=4, sticky='ew', pady=10)

        row += 1
        # Equivalent circuit parameters
        ttk.Label(params_frame, text="Stator Resistance R1 (Ω):").grid(row=row, column=0, sticky='w', pady=2)
        self.r1_entry = ttk.Entry(params_frame, width=15)
        self.r1_entry.insert(0, str(self.simulator.R1))
        self.r1_entry.grid(row=row, column=1, padx=5, pady=2)

        ttk.Label(params_frame, text="Rotor Resistance R2 (Ω):").grid(row=row, column=2, sticky='w', pady=2)
        self.r2_entry = ttk.Entry(params_frame, width=15)
        self.r2_entry.insert(0, str(self.simulator.R2))
        self.r2_entry.grid(row=row, column=3, padx=5, pady=2)

        row += 1
        ttk.Label(params_frame, text="Stator Reactance X1 (Ω):").grid(row=row, column=0, sticky='w', pady=2)
        self.x1_entry = ttk.Entry(params_frame, width=15)
        self.x1_entry.insert(0, str(self.simulator.X1))
        self.x1_entry.grid(row=row, column=1, padx=5, pady=2)

        ttk.Label(params_frame, text="Rotor Reactance X2 (Ω):").grid(row=row, column=2, sticky='w', pady=2)
        self.x2_entry = ttk.Entry(params_frame, width=15)
        self.x2_entry.insert(0, str(self.simulator.X2))
        self.x2_entry.grid(row=row, column=3, padx=5, pady=2)

        row += 1
        ttk.Label(params_frame, text="Magnetizing Reactance Xm (Ω):").grid(row=row, column=0, sticky='w', pady=2)
        self.xm_entry = ttk.Entry(params_frame, width=15)
        self.xm_entry.insert(0, str(self.simulator.Xm))
        self.xm_entry.grid(row=row, column=1, padx=5, pady=2)

        # Update button
        ttk.Button(params_frame, text="Update Parameters", command=self.update_parameters).grid(
            row=row, column=3, padx=5, pady=10)

        # Information panel
        info_frame = ttk.LabelFrame(tab, text="Motor Information", padding=10)
        info_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)

        self.info_text = scrolledtext.ScrolledText(info_frame, height=20, width=80, wrap=tk.WORD)
        self.info_text.pack(fill='both', expand=True)

        self.display_motor_info()

    def create_starter_calculation_tab(self):
        """Create auto-transformer starter calculation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Auto-Transformer Starter")

        # Configure grid
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Input frame
        input_frame = ttk.LabelFrame(tab, text="Starter Calculation", padding=10)
        input_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        ttk.Button(input_frame, text="Calculate Auto-Transformer Tapping",
                  command=self.calculate_starter, width=30).pack(pady=10)

        # Results frame
        results_frame = ttk.LabelFrame(tab, text="Results", padding=10)
        results_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)

        self.starter_results_text = scrolledtext.ScrolledText(results_frame, height=25, wrap=tk.WORD)
        self.starter_results_text.pack(fill='both', expand=True)

    def create_simulation_tab(self):
        """Create dynamic simulation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Dynamic Simulation")

        # Configure grid
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Control frame
        control_frame = ttk.LabelFrame(tab, text="Simulation Controls", padding=10)
        control_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        # Simulation parameters
        params_frame = ttk.Frame(control_frame)
        params_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(params_frame, text="Simulation Time (s):").grid(row=0, column=0, sticky='w', pady=2)
        self.sim_time_entry = ttk.Entry(params_frame, width=10)
        self.sim_time_entry.insert(0, str(self.simulator.simulation_time))
        self.sim_time_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(params_frame, text="Load Torque (N·m):").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.load_torque_entry = ttk.Entry(params_frame, width=10)
        self.load_torque_entry.insert(0, str(self.simulator.load_torque))
        self.load_torque_entry.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(params_frame, text="Solver Method:").grid(row=0, column=4, sticky='w', pady=2, padx=(20, 0))
        self.solver_combo = ttk.Combobox(params_frame, values=['RK45', 'Euler', 'LSODA'], width=10)
        self.solver_combo.set(self.simulator.solver_method)
        self.solver_combo.grid(row=0, column=5, padx=5, pady=2)

        # Control sliders
        sliders_frame = ttk.Frame(control_frame)
        sliders_frame.pack(fill='x', padx=5, pady=10)

        ttk.Label(sliders_frame, text="Voltage Control (0-100%):").grid(row=0, column=0, sticky='w', pady=5)
        self.voltage_scale = ttk.Scale(sliders_frame, from_=0, to=100, orient='horizontal', length=200,
                                      command=self.update_voltage_control)
        self.voltage_scale.set(100)
        self.voltage_scale.grid(row=0, column=1, padx=5, pady=5)
        self.voltage_label = ttk.Label(sliders_frame, text="100%")
        self.voltage_label.grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(sliders_frame, text="Frequency Control (0-100%):").grid(row=1, column=0, sticky='w', pady=5)
        self.freq_scale = ttk.Scale(sliders_frame, from_=0, to=100, orient='horizontal', length=200,
                                   command=self.update_freq_control)
        self.freq_scale.set(100)
        self.freq_scale.grid(row=1, column=1, padx=5, pady=5)
        self.freq_label = ttk.Label(sliders_frame, text="100%")
        self.freq_label.grid(row=1, column=2, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill='x', padx=5, pady=5)

        self.start_btn = ttk.Button(button_frame, text="Start Simulation", command=self.start_simulation)
        self.start_btn.pack(side='left', padx=5)

        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_simulation, state='disabled')
        self.stop_btn.pack(side='left', padx=5)

        self.reset_btn = ttk.Button(button_frame, text="Reset", command=self.reset_simulation)
        self.reset_btn.pack(side='left', padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(control_frame, mode='determinate', length=400)
        self.progress.pack(fill='x', padx=5, pady=5)

        # Visualization frame
        viz_frame = ttk.LabelFrame(tab, text="Dynamic Visualization", padding=5)
        viz_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        viz_frame.grid_rowconfigure(0, weight=1)
        viz_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.sim_fig = Figure(figsize=(12, 8), dpi=100)
        self.sim_canvas = FigureCanvasTkAgg(self.sim_fig, master=viz_frame)
        self.sim_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Create subplots
        self.ax_speed = self.sim_fig.add_subplot(3, 2, 1)
        self.ax_torque = self.sim_fig.add_subplot(3, 2, 2)
        self.ax_current = self.sim_fig.add_subplot(3, 2, 3)
        self.ax_power = self.sim_fig.add_subplot(3, 2, 4)
        self.ax_efficiency = self.sim_fig.add_subplot(3, 2, 5)
        self.ax_temp = self.sim_fig.add_subplot(3, 2, 6)

        self.sim_fig.tight_layout(pad=2.0)

    def create_multiphysics_tab(self):
        """Create multi-physics analysis tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Multi-Physics Analysis")

        # Configure grid
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Info frame
        info_frame = ttk.LabelFrame(tab, text="Multi-Physics Modeling", padding=10)
        info_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        info_text = """
        This simulator includes coupled electromagnetic-thermal-mechanical models:

        • Electromagnetic Model: Calculates torque, current, and flux based on voltage and frequency
        • Thermal Model: Solves heat transfer equations considering all loss components
        • Mechanical Model: Simulates shaft dynamics with inertia and friction
        • Loss Analysis: Separates copper, iron, mechanical friction, and stray load losses
        """
        ttk.Label(info_frame, text=info_text, justify='left').pack(anchor='w')

        # Visualization frame
        viz_frame = ttk.LabelFrame(tab, text="Loss Breakdown & Thermal Analysis", padding=5)
        viz_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        viz_frame.grid_rowconfigure(0, weight=1)
        viz_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.mp_fig = Figure(figsize=(12, 8), dpi=100)
        self.mp_canvas = FigureCanvasTkAgg(self.mp_fig, master=viz_frame)
        self.mp_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Create subplots
        self.ax_losses = self.mp_fig.add_subplot(2, 2, 1)
        self.ax_thermal = self.mp_fig.add_subplot(2, 2, 2)
        self.ax_loss_pie = self.mp_fig.add_subplot(2, 2, 3)
        self.ax_stress = self.mp_fig.add_subplot(2, 2, 4)

        self.mp_fig.tight_layout(pad=2.0)

        # Update button
        ttk.Button(tab, text="Update Multi-Physics Analysis",
                  command=self.update_multiphysics_plots).grid(row=2, column=0, pady=10)

    def create_advanced_controls_tab(self):
        """Create advanced controls and thermal derating tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Advanced Controls")

        # Configure grid
        tab.grid_rowconfigure(2, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # V/f Control
        vf_frame = ttk.LabelFrame(tab, text="V/f Control", padding=10)
        vf_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        ttk.Label(vf_frame, text="Variable Voltage Variable Frequency (V/f) Control").pack(anchor='w', pady=5)

        vf_controls = ttk.Frame(vf_frame)
        vf_controls.pack(fill='x', pady=5)

        ttk.Label(vf_controls, text="Target Speed (RPM):").grid(row=0, column=0, sticky='w', pady=2)
        self.target_speed_entry = ttk.Entry(vf_controls, width=15)
        self.target_speed_entry.insert(0, "1450")
        self.target_speed_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Button(vf_controls, text="Apply V/f Control", command=self.apply_vf_control).grid(
            row=0, column=2, padx=10, pady=2)

        # Thermal derating
        thermal_frame = ttk.LabelFrame(tab, text="Thermal Derating", padding=10)
        thermal_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=5)

        ttk.Label(thermal_frame, text="Automatic load reduction based on temperature").pack(anchor='w', pady=5)

        thermal_controls = ttk.Frame(thermal_frame)
        thermal_controls.pack(fill='x', pady=5)

        ttk.Label(thermal_controls, text="Max Temperature (°C):").grid(row=0, column=0, sticky='w', pady=2)
        self.max_temp_entry = ttk.Entry(thermal_controls, width=15)
        self.max_temp_entry.insert(0, str(self.simulator.max_temp))
        self.max_temp_entry.grid(row=0, column=1, padx=5, pady=2)

        self.thermal_derating_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(thermal_controls, text="Enable Thermal Derating",
                       variable=self.thermal_derating_var).grid(row=0, column=2, padx=10, pady=2)

        # Power consumption monitoring
        power_frame = ttk.LabelFrame(tab, text="Power Consumption Monitoring", padding=10)
        power_frame.grid(row=2, column=0, sticky='nsew', padx=10, pady=5)
        power_frame.grid_rowconfigure(0, weight=1)
        power_frame.grid_columnconfigure(0, weight=1)

        self.power_text = scrolledtext.ScrolledText(power_frame, height=15, wrap=tk.WORD)
        self.power_text.grid(row=0, column=0, sticky='nsew')

    def create_economic_analysis_tab(self):
        """Create economic analysis tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Economic Analysis")

        # Configure grid
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Input frame
        input_frame = ttk.LabelFrame(tab, text="Economic Parameters", padding=10)
        input_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        params = ttk.Frame(input_frame)
        params.pack(fill='x', pady=5)

        ttk.Label(params, text="Electricity Cost ($/kWh):").grid(row=0, column=0, sticky='w', pady=2)
        self.elec_cost_entry = ttk.Entry(params, width=15)
        self.elec_cost_entry.insert(0, str(self.simulator.electricity_cost))
        self.elec_cost_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(params, text="Motor Initial Cost ($):").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.motor_cost_entry = ttk.Entry(params, width=15)
        self.motor_cost_entry.insert(0, str(self.simulator.motor_cost))
        self.motor_cost_entry.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(params, text="Annual Maintenance ($):").grid(row=1, column=0, sticky='w', pady=2)
        self.maint_cost_entry = ttk.Entry(params, width=15)
        self.maint_cost_entry.insert(0, str(self.simulator.maintenance_cost_annual))
        self.maint_cost_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(params, text="Operating Hours/Year:").grid(row=1, column=2, sticky='w', pady=2, padx=(20, 0))
        self.op_hours_entry = ttk.Entry(params, width=15)
        self.op_hours_entry.insert(0, "4000")
        self.op_hours_entry.grid(row=1, column=3, padx=5, pady=2)

        ttk.Button(input_frame, text="Calculate Economic Analysis",
                  command=self.calculate_economics).pack(pady=10)

        # Results frame
        results_frame = ttk.LabelFrame(tab, text="Economic Analysis Results", padding=10)
        results_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        self.econ_text = scrolledtext.ScrolledText(results_frame, height=20, wrap=tk.WORD)
        self.econ_text.grid(row=0, column=0, sticky='nsew')

    def update_parameters(self):
        """Update simulator parameters from GUI inputs"""
        try:
            self.simulator.V_rated = float(self.voltage_entry.get())
            self.simulator.V_phase = self.simulator.V_rated / np.sqrt(3)
            self.simulator.f = float(self.freq_entry.get())
            self.simulator.I_fl = float(self.fl_current_entry.get())
            self.simulator.slip_fl = float(self.fl_slip_entry.get())
            self.simulator.Z_standstill = float(self.z_standstill_entry.get())
            self.simulator.I_max_line = float(self.max_current_entry.get())
            self.simulator.poles = int(self.poles_entry.get())
            self.simulator.rated_power = float(self.power_entry.get())

            self.simulator.R1 = float(self.r1_entry.get())
            self.simulator.R2 = float(self.r2_entry.get())
            self.simulator.X1 = float(self.x1_entry.get())
            self.simulator.X2 = float(self.x2_entry.get())
            self.simulator.Xm = float(self.xm_entry.get())

            # Recalculate derived parameters
            self.simulator.omega_s = 2 * np.pi * self.simulator.f
            self.simulator.n_s = 120 * self.simulator.f / self.simulator.poles

            self.display_motor_info()
            self.status_bar.config(text="Parameters updated successfully")
            messagebox.showinfo("Success", "Motor parameters updated successfully!")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid parameter value: {str(e)}")

    def display_motor_info(self):
        """Display motor information"""
        self.info_text.delete(1.0, tk.END)

        info = f"""
╔══════════════════════════════════════════════════════════════════════╗
║         ADVANCED 3-PHASE INDUCTION MOTOR SIMULATOR                   ║
║              Multi-Physics Analysis System                           ║
╚══════════════════════════════════════════════════════════════════════╝

ELECTRICAL PARAMETERS:
─────────────────────────────────────────────────────────────────────
  Rated Voltage (Line):          {self.simulator.V_rated:.2f} V
  Phase Voltage:                 {self.simulator.V_phase:.2f} V
  Frequency:                     {self.simulator.f:.2f} Hz
  Full Load Current:             {self.simulator.I_fl:.2f} A
  Full Load Slip:                {self.simulator.slip_fl:.4f} ({self.simulator.slip_fl*100:.2f}%)
  Standstill Impedance:          {self.simulator.Z_standstill:.4f} Ω
  Maximum Starting Current:      {self.simulator.I_max_line:.2f} A
  Number of Poles:               {self.simulator.poles}
  Rated Power:                   {self.simulator.rated_power/1000:.2f} kW

EQUIVALENT CIRCUIT PARAMETERS:
─────────────────────────────────────────────────────────────────────
  Stator Resistance (R1):        {self.simulator.R1:.4f} Ω
  Rotor Resistance (R2):         {self.simulator.R2:.4f} Ω
  Stator Reactance (X1):         {self.simulator.X1:.4f} Ω
  Rotor Reactance (X2):          {self.simulator.X2:.4f} Ω
  Magnetizing Reactance (Xm):    {self.simulator.Xm:.4f} Ω

MECHANICAL PARAMETERS:
─────────────────────────────────────────────────────────────────────
  Synchronous Speed:             {self.simulator.n_s:.2f} RPM
  Angular Frequency:             {self.simulator.omega_s:.2f} rad/s
  Moment of Inertia:             {self.simulator.J:.4f} kg·m²
  Friction Coefficient:          {self.simulator.B:.6f} N·m·s

THERMAL PARAMETERS:
─────────────────────────────────────────────────────────────────────
  Thermal Resistance:            {self.simulator.thermal_resistance:.2f} °C/W
  Thermal Capacitance:           {self.simulator.thermal_capacitance:.2f} J/°C
  Ambient Temperature:           {self.simulator.ambient_temp:.2f} °C
  Maximum Temperature:           {self.simulator.max_temp:.2f} °C

SIMULATION FEATURES:
─────────────────────────────────────────────────────────────────────
  ✓ Auto-transformer Starter Calculations
  ✓ Dynamic ODE Simulation (RK45, Euler, LSODA)
  ✓ Multi-Physics Modeling (Electromagnetic-Thermal-Mechanical)
  ✓ Real-time Loss Analysis (Copper, Iron, Mechanical, Stray)
  ✓ V/f Speed Control
  ✓ Thermal Derating
  ✓ Economic Analysis
  ✓ Advanced Visualization

╔══════════════════════════════════════════════════════════════════════╗
║  This simulator solves coupled differential equations for accurate   ║
║  prediction of motor behavior under various operating conditions.    ║
╚══════════════════════════════════════════════════════════════════════╝
        """

        self.info_text.insert(1.0, info)

    def calculate_starter(self):
        """Calculate auto-transformer starter tapping"""
        self.update_parameters()

        tapping, torque_ratio = self.simulator.calculate_auto_transformer_starter()

        # Display detailed results
        self.starter_results_text.delete(1.0, tk.END)

        results = f"""
╔══════════════════════════════════════════════════════════════════════╗
║           AUTO-TRANSFORMER STARTER CALCULATION RESULTS               ║
╚══════════════════════════════════════════════════════════════════════╝

PROBLEM STATEMENT:
─────────────────────────────────────────────────────────────────────
A {self.simulator.V_rated}V 3-phase squirrel cage induction motor has:
  • Full load slip: {self.simulator.slip_fl*100:.2f}%
  • Standstill impedance: {self.simulator.Z_standstill:.4f} Ω
  • Full load current: {self.simulator.I_fl:.2f} A
  • Maximum starting current allowed: {self.simulator.I_max_line:.2f} A

Find: Auto-transformer tapping and starting torque ratio

SOLUTION:
─────────────────────────────────────────────────────────────────────

Step 1: Calculate Starting Current at Full Voltage
───────────────────────────────────────────────────
  Phase Voltage: V_ph = {self.simulator.V_rated}/√3 = {self.simulator.V_phase:.2f} V

  Starting current per phase:
  I_st = V_ph / Z_st = {self.simulator.V_phase:.2f} / {self.simulator.Z_standstill:.4f}
       = {self.simulator.V_phase/self.simulator.Z_standstill:.2f} A

  Line starting current:
  I_st_line = √3 × I_st = √3 × {self.simulator.V_phase/self.simulator.Z_standstill:.2f}
            = {np.sqrt(3) * self.simulator.V_phase/self.simulator.Z_standstill:.2f} A

Step 2: Calculate Auto-transformer Tapping
───────────────────────────────────────────────────
  For auto-transformer starter:
    • Voltage applied to motor: V_motor = α × V_rated
    • Current from motor: I_motor = α × I_st
    • Current from line: I_line = α² × I_st

  Required condition:
    √3 × α² × I_st = I_max_line
    √3 × α² × {self.simulator.V_phase/self.simulator.Z_standstill:.2f} = {self.simulator.I_max_line:.2f}

  Solving for α:
    α² = {self.simulator.I_max_line:.2f} / (√3 × {self.simulator.V_phase/self.simulator.Z_standstill:.2f})
    α² = {self.simulator.I_max_line / (np.sqrt(3) * self.simulator.V_phase/self.simulator.Z_standstill):.4f}
    α = {tapping/100:.4f}

Step 3: Calculate Starting Torque Ratio
───────────────────────────────────────────────────
  Torque is proportional to voltage squared:
    T_st ∝ V²

  Starting torque at reduced voltage:
    T_st_reduced = α² × T_st_full
                 = {(tapping/100)**2:.4f} × T_st_full

  Ratio to full load torque:
    T_st_reduced / T_fl = {torque_ratio:.4f}

═══════════════════════════════════════════════════════════════════════

FINAL RESULTS:
═══════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                 │
  │  AUTO-TRANSFORMER TAPPING:        {tapping:.2f}%                    │
  │                                                                 │
  │  STARTING TORQUE RATIO:           {torque_ratio:.4f}                 │
  │  (in terms of full load torque)                                 │
  │                                                                 │
  └─────────────────────────────────────────────────────────────────┘

INTERPRETATION:
─────────────────────────────────────────────────────────────────────
  • The auto-transformer should be tapped at {tapping:.2f}% of rated voltage
  • This limits the starting current to {self.simulator.I_max_line:.2f} A (line current)
  • The available starting torque is {torque_ratio:.2f} times the full load torque

  Voltage applied to motor: {tapping:.2f}% × {self.simulator.V_rated}V = {tapping/100 * self.simulator.V_rated:.2f} V

PRACTICAL CONSIDERATIONS:
─────────────────────────────────────────────────────────────────────
  • Standard tappings: 40%, 50%, 60%, 65%, 70%, 75%, 80%
  • Recommended tapping: {min([40, 50, 60, 65, 70, 75, 80], key=lambda x: abs(x-tapping)):.0f}% (closest standard)
  • Ensure starting torque exceeds load torque requirement
  • Auto-transformer reduces both current and torque by factor of α²

═══════════════════════════════════════════════════════════════════════
        """

        self.starter_results_text.insert(1.0, results)
        self.status_bar.config(text=f"Auto-transformer tapping calculated: {tapping:.2f}%")

    def update_voltage_control(self, value):
        """Update voltage control slider"""
        self.voltage_label.config(text=f"{float(value):.1f}%")
        self.simulator.voltage_control = float(value) / 100.0

    def update_freq_control(self, value):
        """Update frequency control slider"""
        self.freq_label.config(text=f"{float(value):.1f}%")
        self.simulator.frequency_control = float(value) / 100.0

    def start_simulation(self):
        """Start dynamic simulation"""
        if self.is_simulating:
            messagebox.showwarning("Warning", "Simulation already running!")
            return

        try:
            # Update parameters
            self.simulator.simulation_time = float(self.sim_time_entry.get())
            self.simulator.load_torque = float(self.load_torque_entry.get())
            self.simulator.solver_method = self.solver_combo.get()

            # Update button states
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.is_simulating = True

            # Reset progress
            self.progress['value'] = 0

            # Run simulation in separate thread
            self.simulation_thread = threading.Thread(target=self.run_simulation_thread)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid simulation parameter: {str(e)}")
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.is_simulating = False

    def run_simulation_thread(self):
        """Run simulation in separate thread"""
        try:
            self.status_bar.config(text="Running simulation...")

            # Run simulation
            self.simulator.run_simulation(progress_callback=self.update_progress)

            # Update plots
            self.root.after(0, self.update_simulation_plots)
            self.root.after(0, self.update_multiphysics_plots)
            self.root.after(0, self.update_power_consumption)

            self.status_bar.config(text="Simulation completed successfully")

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Simulation error: {str(e)}"))
            self.status_bar.config(text="Simulation failed")

        finally:
            self.is_simulating = False
            self.root.after(0, lambda: self.start_btn.config(state='normal'))
            self.root.after(0, lambda: self.stop_btn.config(state='disabled'))
            self.root.after(0, lambda: self.progress.config(value=100))

    def update_progress(self, value):
        """Update progress bar"""
        self.root.after(0, lambda: self.progress.config(value=value))

    def stop_simulation(self):
        """Stop simulation"""
        self.is_simulating = False
        self.status_bar.config(text="Simulation stopped by user")

    def reset_simulation(self):
        """Reset simulation"""
        self.is_simulating = False
        self.progress['value'] = 0
        self.voltage_scale.set(100)
        self.freq_scale.set(100)
        self.simulator.voltage_control = 1.0
        self.simulator.frequency_control = 1.0

        # Clear plots
        for ax in [self.ax_speed, self.ax_torque, self.ax_current,
                   self.ax_power, self.ax_efficiency, self.ax_temp]:
            ax.clear()
        self.sim_canvas.draw()

        self.status_bar.config(text="Simulation reset")

    def update_simulation_plots(self):
        """Update simulation plots"""
        if not self.simulator.time_data:
            return

        # Clear all axes
        for ax in [self.ax_speed, self.ax_torque, self.ax_current,
                   self.ax_power, self.ax_efficiency, self.ax_temp]:
            ax.clear()

        # Speed plot
        self.ax_speed.plot(self.simulator.time_data, self.simulator.speed_data, 'b-', linewidth=2)
        self.ax_speed.axhline(y=self.simulator.n_s, color='r', linestyle='--', label='Sync Speed')
        self.ax_speed.set_xlabel('Time (s)')
        self.ax_speed.set_ylabel('Speed (RPM)')
        self.ax_speed.set_title('Motor Speed vs Time')
        self.ax_speed.grid(True, alpha=0.3)
        self.ax_speed.legend()

        # Torque plot
        self.ax_torque.plot(self.simulator.time_data, self.simulator.torque_data, 'g-', linewidth=2)
        self.ax_torque.axhline(y=self.simulator.load_torque, color='r', linestyle='--', label='Load Torque')
        self.ax_torque.set_xlabel('Time (s)')
        self.ax_torque.set_ylabel('Torque (N·m)')
        self.ax_torque.set_title('Electromagnetic Torque vs Time')
        self.ax_torque.grid(True, alpha=0.3)
        self.ax_torque.legend()

        # Current plot
        self.ax_current.plot(self.simulator.time_data, self.simulator.current_data, 'r-', linewidth=2)
        self.ax_current.axhline(y=self.simulator.I_fl, color='b', linestyle='--', label='FL Current')
        self.ax_current.set_xlabel('Time (s)')
        self.ax_current.set_ylabel('Current (A)')
        self.ax_current.set_title('Line Current vs Time')
        self.ax_current.grid(True, alpha=0.3)
        self.ax_current.legend()

        # Power plot
        self.ax_power.plot(self.simulator.time_data, self.simulator.power_data, 'm-', linewidth=2)
        self.ax_power.set_xlabel('Time (s)')
        self.ax_power.set_ylabel('Power (kW)')
        self.ax_power.set_title('Output Power vs Time')
        self.ax_power.grid(True, alpha=0.3)

        # Efficiency plot
        self.ax_efficiency.plot(self.simulator.time_data, self.simulator.efficiency_data, 'c-', linewidth=2)
        self.ax_efficiency.set_xlabel('Time (s)')
        self.ax_efficiency.set_ylabel('Efficiency (%)')
        self.ax_efficiency.set_title('Efficiency vs Time')
        self.ax_efficiency.grid(True, alpha=0.3)

        # Temperature plot
        self.ax_temp.plot(self.simulator.time_data, self.simulator.temp_data, 'orange', linewidth=2)
        self.ax_temp.axhline(y=self.simulator.max_temp, color='r', linestyle='--', label='Max Temp')
        self.ax_temp.axhline(y=self.simulator.ambient_temp, color='b', linestyle='--', label='Ambient')
        self.ax_temp.set_xlabel('Time (s)')
        self.ax_temp.set_ylabel('Temperature (°C)')
        self.ax_temp.set_title('Winding Temperature vs Time')
        self.ax_temp.grid(True, alpha=0.3)
        self.ax_temp.legend()

        self.sim_fig.tight_layout(pad=2.0)
        self.sim_canvas.draw()

    def update_multiphysics_plots(self):
        """Update multi-physics analysis plots"""
        if not self.simulator.time_data:
            return

        # Clear all axes
        for ax in [self.ax_losses, self.ax_thermal, self.ax_loss_pie, self.ax_stress]:
            ax.clear()

        # Loss breakdown over time
        self.ax_losses.plot(self.simulator.time_data, self.simulator.loss_data['copper'],
                           label='Copper Loss', linewidth=2)
        self.ax_losses.plot(self.simulator.time_data, self.simulator.loss_data['iron'],
                           label='Iron Loss', linewidth=2)
        self.ax_losses.plot(self.simulator.time_data, self.simulator.loss_data['mechanical'],
                           label='Mechanical Loss', linewidth=2)
        self.ax_losses.plot(self.simulator.time_data, self.simulator.loss_data['stray'],
                           label='Stray Load Loss', linewidth=2)
        self.ax_losses.set_xlabel('Time (s)')
        self.ax_losses.set_ylabel('Loss (W)')
        self.ax_losses.set_title('Detailed Loss Breakdown vs Time')
        self.ax_losses.legend()
        self.ax_losses.grid(True, alpha=0.3)

        # Thermal profile
        self.ax_thermal.plot(self.simulator.time_data, self.simulator.temp_data,
                            'r-', linewidth=2, label='Winding Temp')
        self.ax_thermal.axhline(y=self.simulator.max_temp, color='orange',
                               linestyle='--', linewidth=2, label='Max Temp Limit')
        self.ax_thermal.fill_between(self.simulator.time_data, self.simulator.ambient_temp,
                                     self.simulator.temp_data, alpha=0.3)
        self.ax_thermal.set_xlabel('Time (s)')
        self.ax_thermal.set_ylabel('Temperature (°C)')
        self.ax_thermal.set_title('Thermal Analysis - Temperature Rise')
        self.ax_thermal.legend()
        self.ax_thermal.grid(True, alpha=0.3)

        # Loss pie chart (at final time)
        if len(self.simulator.loss_data['copper']) > 0:
            final_losses = [
                self.simulator.loss_data['copper'][-1],
                self.simulator.loss_data['iron'][-1],
                self.simulator.loss_data['mechanical'][-1],
                self.simulator.loss_data['stray'][-1]
            ]
            labels = ['Copper\nLoss', 'Iron\nLoss', 'Mechanical\nLoss', 'Stray\nLoss']
            colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#ffa07a']

            self.ax_loss_pie.pie(final_losses, labels=labels, autopct='%1.1f%%',
                                colors=colors, startangle=90)
            self.ax_loss_pie.set_title('Loss Distribution at Steady State')

        # Mechanical stress (torque vs speed)
        self.ax_stress.plot(self.simulator.speed_data, self.simulator.torque_data,
                           'b-', linewidth=2)
        self.ax_stress.set_xlabel('Speed (RPM)')
        self.ax_stress.set_ylabel('Torque (N·m)')
        self.ax_stress.set_title('Mechanical Stress Analysis - Torque vs Speed')
        self.ax_stress.grid(True, alpha=0.3)

        self.mp_fig.tight_layout(pad=2.0)
        self.mp_canvas.draw()

    def apply_vf_control(self):
        """Apply V/f control"""
        try:
            target_speed = float(self.target_speed_entry.get())

            # Calculate required frequency
            # n = 120*f/p * (1-s)
            # For approximate calculation, assume small slip
            required_freq = target_speed * self.simulator.poles / 120
            freq_ratio = required_freq / self.simulator.f

            # Update controls
            self.freq_scale.set(freq_ratio * 100)
            self.voltage_scale.set(freq_ratio * 100)  # Maintain V/f ratio

            self.simulator.frequency_control = freq_ratio
            self.simulator.voltage_control = freq_ratio

            messagebox.showinfo("V/f Control",
                              f"V/f control applied:\nFrequency: {freq_ratio*100:.1f}%\nVoltage: {freq_ratio*100:.1f}%")

        except ValueError:
            messagebox.showerror("Error", "Invalid target speed value")

    def update_power_consumption(self):
        """Update power consumption monitoring"""
        if not self.simulator.time_data:
            return

        self.power_text.delete(1.0, tk.END)

        # Calculate statistics
        avg_power = np.mean(self.simulator.power_data)
        max_power = np.max(self.simulator.power_data)
        avg_current = np.mean(self.simulator.current_data)
        max_current = np.max(self.simulator.current_data)
        avg_efficiency = np.mean(self.simulator.efficiency_data)
        final_temp = self.simulator.temp_data[-1]

        # Calculate energy consumption
        energy_kwh = np.trapz(self.simulator.power_data, self.simulator.time_data) / 3600  # kWh

        # Calculate total losses
        total_copper_loss = np.mean(self.simulator.loss_data['copper'])
        total_iron_loss = np.mean(self.simulator.loss_data['iron'])
        total_mech_loss = np.mean(self.simulator.loss_data['mechanical'])
        total_stray_loss = np.mean(self.simulator.loss_data['stray'])
        total_loss = total_copper_loss + total_iron_loss + total_mech_loss + total_stray_loss

        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║              POWER CONSUMPTION MONITORING REPORT                     ║
╚══════════════════════════════════════════════════════════════════════╝

SIMULATION PERIOD: {self.simulator.simulation_time:.2f} seconds

POWER STATISTICS:
─────────────────────────────────────────────────────────────────────
  Average Output Power:          {avg_power:.2f} kW
  Maximum Output Power:          {max_power:.2f} kW
  Energy Consumed:               {energy_kwh:.4f} kWh

CURRENT STATISTICS:
─────────────────────────────────────────────────────────────────────
  Average Line Current:          {avg_current:.2f} A
  Maximum Line Current:          {max_current:.2f} A
  Rated Current:                 {self.simulator.I_fl:.2f} A
  Current Overload:              {(max_current/self.simulator.I_fl - 1)*100:.1f}%

EFFICIENCY ANALYSIS:
─────────────────────────────────────────────────────────────────────
  Average Efficiency:            {avg_efficiency:.2f}%

LOSS BREAKDOWN (Average):
─────────────────────────────────────────────────────────────────────
  Copper Losses (I²R):           {total_copper_loss:.2f} W ({total_copper_loss/total_loss*100:.1f}%)
  Iron Losses (Core):            {total_iron_loss:.2f} W ({total_iron_loss/total_loss*100:.1f}%)
  Mechanical Losses:             {total_mech_loss:.2f} W ({total_mech_loss/total_loss*100:.1f}%)
  Stray Load Losses:             {total_stray_loss:.2f} W ({total_stray_loss/total_loss*100:.1f}%)
  ─────────────────────────────────────────────────────────────────
  Total Losses:                  {total_loss:.2f} W

THERMAL STATUS:
─────────────────────────────────────────────────────────────────────
  Final Winding Temperature:     {final_temp:.2f} °C
  Temperature Rise:              {final_temp - self.simulator.ambient_temp:.2f} °C
  Maximum Allowed:               {self.simulator.max_temp:.2f} °C
  Thermal Margin:                {self.simulator.max_temp - final_temp:.2f} °C
  Status:                        {'⚠ WARNING' if final_temp > self.simulator.max_temp else '✓ NORMAL'}

OPERATING COST ESTIMATE:
─────────────────────────────────────────────────────────────────────
  Electricity Rate:              ${self.simulator.electricity_cost:.4f}/kWh
  Cost for this simulation:      ${energy_kwh * self.simulator.electricity_cost:.6f}

  Projected Annual Cost (4000 hrs @ avg load):
    Energy Cost:                 ${avg_power * 4000 * self.simulator.electricity_cost:.2f}/year

═══════════════════════════════════════════════════════════════════════
        """

        self.power_text.insert(1.0, report)

    def calculate_economics(self):
        """Calculate economic analysis"""
        try:
            elec_cost = float(self.elec_cost_entry.get())
            motor_cost = float(self.motor_cost_entry.get())
            maint_cost = float(self.maint_cost_entry.get())
            op_hours = float(self.op_hours_entry.get())

            self.simulator.electricity_cost = elec_cost
            self.simulator.motor_cost = motor_cost
            self.simulator.maintenance_cost_annual = maint_cost

            # Calculate economics
            if not self.simulator.power_data:
                messagebox.showwarning("Warning", "Please run simulation first!")
                return

            avg_power = np.mean(self.simulator.power_data)
            avg_efficiency = np.mean(self.simulator.efficiency_data)

            # Annual energy consumption
            annual_energy = avg_power * op_hours  # kWh

            # Annual electricity cost
            annual_elec_cost = annual_energy * elec_cost

            # Total annual operating cost
            total_annual_cost = annual_elec_cost + maint_cost

            # Lifecycle cost (assume 15 years)
            lifecycle_years = 15
            lifecycle_cost = motor_cost + total_annual_cost * lifecycle_years

            # Calculate payback for efficiency improvement
            # Compare with a motor of 2% lower efficiency
            lower_eff = avg_efficiency - 2
            power_at_lower_eff = avg_power * (avg_efficiency / lower_eff)
            annual_energy_lower = power_at_lower_eff * op_hours
            annual_savings = (annual_energy_lower - annual_energy) * elec_cost

            # Assume high-efficiency motor costs 10% more
            extra_cost = motor_cost * 0.10
            payback_years = extra_cost / annual_savings if annual_savings > 0 else float('inf')

            self.econ_text.delete(1.0, tk.END)

            report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    ECONOMIC ANALYSIS REPORT                          ║
╚══════════════════════════════════════════════════════════════════════╝

INPUT PARAMETERS:
─────────────────────────────────────────────────────────────────────
  Motor Initial Cost:            ${motor_cost:,.2f}
  Electricity Rate:              ${elec_cost:.4f}/kWh
  Annual Maintenance Cost:       ${maint_cost:,.2f}
  Operating Hours per Year:      {op_hours:,.0f} hours

OPERATING PERFORMANCE:
─────────────────────────────────────────────────────────────────────
  Average Output Power:          {avg_power:.2f} kW
  Average Efficiency:            {avg_efficiency:.2f}%
  Load Factor:                   {avg_power/(self.simulator.rated_power/1000)*100:.1f}%

ANNUAL COSTS:
─────────────────────────────────────────────────────────────────────
  Annual Energy Consumption:     {annual_energy:,.2f} kWh
  Annual Electricity Cost:       ${annual_elec_cost:,.2f}
  Annual Maintenance Cost:       ${maint_cost:,.2f}
  ─────────────────────────────────────────────────────────────────
  Total Annual Operating Cost:   ${total_annual_cost:,.2f}

LIFECYCLE COST ANALYSIS ({lifecycle_years} years):
─────────────────────────────────────────────────────────────────────
  Initial Investment:            ${motor_cost:,.2f}
  Cumulative Operating Costs:    ${total_annual_cost * lifecycle_years:,.2f}
  ─────────────────────────────────────────────────────────────────
  Total Lifecycle Cost:          ${lifecycle_cost:,.2f}

  Average Cost per Year:         ${lifecycle_cost/lifecycle_years:,.2f}
  Average Cost per kWh:          ${lifecycle_cost/(annual_energy*lifecycle_years):.4f}

EFFICIENCY IMPROVEMENT ANALYSIS:
─────────────────────────────────────────────────────────────────────
  Current Efficiency:            {avg_efficiency:.2f}%
  Standard Motor Efficiency:     {lower_eff:.2f}%

  Annual Energy Savings:         {annual_energy_lower - annual_energy:,.2f} kWh
  Annual Cost Savings:           ${annual_savings:,.2f}

  Extra Cost of High-Eff Motor:  ${extra_cost:,.2f}
  Simple Payback Period:         {payback_years:.2f} years

  {lifecycle_years}-Year Savings:           ${annual_savings * lifecycle_years:,.2f}
  ROI over {lifecycle_years} years:         {(annual_savings * lifecycle_years - extra_cost)/extra_cost*100:.1f}%

ENVIRONMENTAL IMPACT:
─────────────────────────────────────────────────────────────────────
  Annual CO₂ Emissions:          {annual_energy * 0.5:.2f} kg
  (assuming 0.5 kg CO₂/kWh)

  Lifetime CO₂ Emissions:        {annual_energy * 0.5 * lifecycle_years / 1000:.2f} tons

RECOMMENDATIONS:
─────────────────────────────────────────────────────────────────────
  • {'✓' if avg_efficiency > 90 else '⚠'} Efficiency: {'Excellent' if avg_efficiency > 90 else 'Consider upgrade'}
  • {'✓' if payback_years < 3 else '⚠'} Payback: {'Good investment' if payback_years < 3 else 'Moderate return'}
  • {'✓' if annual_elec_cost < motor_cost else '⚠'} Operating cost is {'less' if annual_elec_cost < motor_cost else 'greater'} than initial cost

COST BREAKDOWN PERCENTAGE:
─────────────────────────────────────────────────────────────────────
  Initial Cost:                  {motor_cost/lifecycle_cost*100:.1f}%
  Energy Costs:                  {annual_elec_cost*lifecycle_years/lifecycle_cost*100:.1f}%
  Maintenance Costs:             {maint_cost*lifecycle_years/lifecycle_cost*100:.1f}%

═══════════════════════════════════════════════════════════════════════

NOTE: This analysis is based on simulation results. Actual costs may vary
      based on load patterns, voltage variations, and operating conditions.

═══════════════════════════════════════════════════════════════════════
            """

            self.econ_text.insert(1.0, report)
            self.status_bar.config(text="Economic analysis completed")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid economic parameter: {str(e)}")

    def on_window_resize(self, event):
        """Handle window resize event for auto-scaling"""
        # Only update if the event is from the main window
        if event.widget == self.root:
            # The grid configuration already handles auto-scaling
            # This method can be used for additional resize logic if needed
            pass


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = MotorSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
