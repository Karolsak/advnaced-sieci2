#!/usr/bin/env python3
"""
DC Motor Simulator with Dynamic Visualization
Solves three DC motor problems with real-time ODE simulation
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.integrate import solve_ivp
import math


class DCMotorSimulator:
    """Main application for DC motor simulation"""

    def __init__(self, root):
        self.root = root
        self.root.title("DC Motor Simulator - Dynamic Analysis")
        self.root.geometry("1400x900")

        # Make window resizable
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Create tabs for each problem
        self.create_shunt_motor_tab()
        self.create_series_motor_speed_tab()
        self.create_series_motor_torque_tab()

        # Bind resize event
        self.root.bind('<Configure>', self.on_resize)

    def on_resize(self, event):
        """Handle window resize events"""
        # Update all canvases
        try:
            if hasattr(self, 'canvas1'):
                self.canvas1.draw_idle()
            if hasattr(self, 'canvas2'):
                self.canvas2.draw_idle()
            if hasattr(self, 'canvas3'):
                self.canvas3.draw_idle()
        except:
            pass

    def create_shunt_motor_tab(self):
        """Problem 1: 230-V DC Shunt Motor"""
        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="Problem 1: Shunt Motor")

        # Configure grid
        tab1.rowconfigure(1, weight=1)
        tab1.columnconfigure(1, weight=1)

        # Left panel for controls
        control_frame = ttk.LabelFrame(tab1, text="Motor Parameters", padding=10)
        control_frame.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=5, pady=5)

        # Parameters with sliders
        self.shunt_params = {}

        params = [
            ("Voltage (V)", "voltage", 230, 100, 400),
            ("Input Power (kW)", "power", 11, 1, 50),
            ("No-load Current (A)", "i0", 5, 1, 20),
            ("No-load Speed (rpm)", "n0", 1150, 500, 2000),
            ("Armature Resistance (Ω)", "ra", 0.5, 0.1, 2.0),
            ("Field Resistance (Ω)", "rf", 110, 50, 500),
            ("Simulation Time (s)", "sim_time", 5, 1, 20),
        ]

        for i, (label, key, default, min_val, max_val) in enumerate(params):
            ttk.Label(control_frame, text=label).grid(row=i, column=0, sticky='w', pady=5)

            var = tk.DoubleVar(value=default)
            self.shunt_params[key] = var

            slider = ttk.Scale(control_frame, from_=min_val, to=max_val,
                             variable=var, orient='horizontal', length=200,
                             command=lambda v, k=key: self.update_shunt_motor())
            slider.grid(row=i, column=1, padx=5, pady=5)

            entry = ttk.Entry(control_frame, textvariable=var, width=10)
            entry.grid(row=i, column=2, padx=5, pady=5)
            entry.bind('<Return>', lambda e: self.update_shunt_motor())

        # ODE Solver selection
        ttk.Label(control_frame, text="ODE Solver:").grid(row=len(params), column=0, sticky='w', pady=5)
        self.shunt_solver = tk.StringVar(value="RK45")
        solver_combo = ttk.Combobox(control_frame, textvariable=self.shunt_solver,
                                    values=["RK45", "Euler"], state='readonly', width=18)
        solver_combo.grid(row=len(params), column=1, columnspan=2, sticky='w', padx=5, pady=5)
        solver_combo.bind('<<ComboboxSelected>>', lambda e: self.update_shunt_motor())

        # Calculate button
        calc_btn = ttk.Button(control_frame, text="Calculate & Simulate",
                            command=self.update_shunt_motor)
        calc_btn.grid(row=len(params)+1, column=0, columnspan=3, pady=10)

        # Results display
        results_frame = ttk.LabelFrame(control_frame, text="Results", padding=10)
        results_frame.grid(row=len(params)+2, column=0, columnspan=3, sticky='ew', pady=5)

        self.shunt_results = tk.Text(results_frame, height=12, width=35, font=('Courier', 9))
        self.shunt_results.pack()

        # Right panel for graphs
        graph_frame = ttk.Frame(tab1)
        graph_frame.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=5, pady=5)
        graph_frame.rowconfigure(0, weight=1)
        graph_frame.columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.fig1 = Figure(figsize=(10, 8))
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=graph_frame)
        self.canvas1.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Initial calculation
        self.update_shunt_motor()

    def shunt_motor_dynamics(self, t, y, V, Ra, Rf, Kt, J, B):
        """ODE system for shunt motor dynamics"""
        omega = y[0]  # Angular velocity
        Ia = y[1]     # Armature current

        # Field current (constant for shunt motor)
        If = V / Rf

        # Back EMF
        Eb = Kt * omega * If

        # Armature current derivative
        La = 0.1  # Armature inductance (assumed)
        dIa_dt = (V - Eb - Ia * Ra) / La

        # Torque
        T = Kt * If * Ia

        # Angular acceleration
        domega_dt = (T - B * omega) / J

        return [domega_dt, dIa_dt]

    def euler_method(self, f, t_span, y0, t_eval):
        """Simple Euler method for ODE solving"""
        t0, tf = t_span
        dt = t_eval[1] - t_eval[0]
        n = len(t_eval)

        y = np.zeros((len(y0), n))
        y[:, 0] = y0

        for i in range(1, n):
            dydt = f(t_eval[i-1], y[:, i-1])
            y[:, i] = y[:, i-1] + np.array(dydt) * dt

        return t_eval, y

    def update_shunt_motor(self, *args):
        """Calculate and update shunt motor results"""
        try:
            # Get parameters
            V = self.shunt_params['voltage'].get()
            P_input = self.shunt_params['power'].get() * 1000  # Convert to W
            I0 = self.shunt_params['i0'].get()
            N0 = self.shunt_params['n0'].get()
            Ra = self.shunt_params['ra'].get()
            Rf = self.shunt_params['rf'].get()
            sim_time = self.shunt_params['sim_time'].get()

            # Calculations
            # Field current
            If = V / Rf

            # Input current
            I = P_input / V

            # Armature current at load
            Ia = I - If

            # Armature current at no-load
            Ia0 = I0 - If

            # Back EMF at no-load
            Eb0 = V - Ia0 * Ra

            # Back EMF at load
            Eb = V - Ia * Ra

            # Speed at load
            N = N0 * (Eb / Eb0)

            # Angular velocity
            omega = 2 * np.pi * N / 60  # rad/s

            # (a) Torque developed
            T = (Eb * Ia) / omega  # N.m

            # (b) Efficiency
            # Copper losses
            Cu_loss_arm = Ia**2 * Ra
            Cu_loss_field = If**2 * Rf

            # No-load losses (approximated from no-load input)
            P_no_load = V * I0
            Iron_friction_loss = P_no_load - Ia0**2 * Ra - If**2 * Rf

            # Total losses
            Total_loss = Cu_loss_arm + Cu_loss_field + Iron_friction_loss

            # Output power
            P_output = P_input - Total_loss

            # Efficiency
            efficiency = (P_output / P_input) * 100

            # (c) Speed is already calculated as N

            # Display results
            results_text = f"""
SHUNT MOTOR ANALYSIS
{'='*32}

Input Parameters:
  Voltage: {V} V
  Input Power: {P_input/1000:.2f} kW
  Input Current: {I:.2f} A
  Field Current: {If:.2f} A
  Armature Current: {Ia:.2f} A

Calculated Results:
  (a) Torque Developed: {T:.2f} N.m
  (b) Efficiency: {efficiency:.2f} %
  (c) Speed at Load: {N:.2f} rpm

Additional Info:
  Back EMF: {Eb:.2f} V
  Armature Loss: {Cu_loss_arm:.2f} W
  Field Loss: {Cu_loss_field:.2f} W
  Core & Friction: {Iron_friction_loss:.2f} W
  Output Power: {P_output/1000:.2f} kW
"""

            self.shunt_results.delete(1.0, tk.END)
            self.shunt_results.insert(1.0, results_text)

            # Dynamic simulation
            J = 0.05  # Moment of inertia (kg.m^2)
            B = 0.01  # Friction coefficient
            Kt = Eb0 / (2 * np.pi * N0 / 60)  # Torque constant

            # Initial conditions
            y0 = [0, 0]  # [omega, Ia]
            t_span = [0, sim_time]
            t_eval = np.linspace(0, sim_time, 500)

            # Solve ODE
            if self.shunt_solver.get() == "RK45":
                sol = solve_ivp(
                    lambda t, y: self.shunt_motor_dynamics(t, y, V, Ra, Rf, Kt, J, B),
                    t_span, y0, t_eval=t_eval, method='RK45'
                )
                t = sol.t
                omega_sim = sol.y[0]
                Ia_sim = sol.y[1]
            else:  # Euler
                t, y = self.euler_method(
                    lambda t, y: self.shunt_motor_dynamics(t, y, V, Ra, Rf, Kt, J, B),
                    t_span, y0, t_eval
                )
                omega_sim = y[0]
                Ia_sim = y[1]

            # Convert to rpm and calculate other quantities
            speed_sim = omega_sim * 60 / (2 * np.pi)
            torque_sim = Kt * (V / Rf) * Ia_sim
            power_sim = torque_sim * omega_sim / 1000  # kW

            # Plot results
            self.fig1.clear()

            ax1 = self.fig1.add_subplot(2, 2, 1)
            ax1.plot(t, speed_sim, 'b-', linewidth=2)
            ax1.axhline(y=N, color='r', linestyle='--', label=f'Steady State: {N:.1f} rpm')
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Speed (rpm)')
            ax1.set_title('Speed vs Time')
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            ax2 = self.fig1.add_subplot(2, 2, 2)
            ax2.plot(t, Ia_sim, 'g-', linewidth=2)
            ax2.axhline(y=Ia, color='r', linestyle='--', label=f'Steady State: {Ia:.1f} A')
            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Armature Current (A)')
            ax2.set_title('Armature Current vs Time')
            ax2.grid(True, alpha=0.3)
            ax2.legend()

            ax3 = self.fig1.add_subplot(2, 2, 3)
            ax3.plot(t, torque_sim, 'm-', linewidth=2)
            ax3.axhline(y=T, color='r', linestyle='--', label=f'Steady State: {T:.1f} N.m')
            ax3.set_xlabel('Time (s)')
            ax3.set_ylabel('Torque (N.m)')
            ax3.set_title('Torque vs Time')
            ax3.grid(True, alpha=0.3)
            ax3.legend()

            ax4 = self.fig1.add_subplot(2, 2, 4)
            ax4.plot(t, power_sim, 'c-', linewidth=2)
            ax4.axhline(y=P_output/1000, color='r', linestyle='--', label=f'Steady State: {P_output/1000:.1f} kW')
            ax4.set_xlabel('Time (s)')
            ax4.set_ylabel('Output Power (kW)')
            ax4.set_title('Output Power vs Time')
            ax4.grid(True, alpha=0.3)
            ax4.legend()

            self.fig1.tight_layout()
            self.canvas1.draw()

        except Exception as e:
            self.shunt_results.delete(1.0, tk.END)
            self.shunt_results.insert(1.0, f"Error in calculation:\n{str(e)}")

    def create_series_motor_speed_tab(self):
        """Problem 2: Series Motor Speed Calculation"""
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="Problem 2: Series Motor Speed")

        # Configure grid
        tab2.rowconfigure(1, weight=1)
        tab2.columnconfigure(1, weight=1)

        # Left panel for controls
        control_frame = ttk.LabelFrame(tab2, text="Motor Parameters", padding=10)
        control_frame.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=5, pady=5)

        # Parameters with sliders
        self.series_params = {}

        params = [
            ("Voltage (V)", "voltage", 250, 100, 400),
            ("Power Rating (kW)", "power", 18.65, 5, 50),
            ("Armature Resistance (Ω)", "ra", 0.1, 0.01, 0.5),
            ("Field Resistance (Ω)", "rf", 0.05, 0.01, 0.3),
            ("Brush Voltage Drop (V)", "vb", 3, 0, 10),
            ("Current I1 (A)", "i1", 80, 20, 200),
            ("Speed at I1 (rpm)", "n1", 600, 100, 1500),
            ("Current I2 (A)", "i2", 100, 20, 200),
            ("Simulation Time (s)", "sim_time", 10, 1, 30),
        ]

        for i, (label, key, default, min_val, max_val) in enumerate(params):
            ttk.Label(control_frame, text=label).grid(row=i, column=0, sticky='w', pady=5)

            var = tk.DoubleVar(value=default)
            self.series_params[key] = var

            slider = ttk.Scale(control_frame, from_=min_val, to=max_val,
                             variable=var, orient='horizontal', length=200,
                             command=lambda v: self.update_series_motor_speed())
            slider.grid(row=i, column=1, padx=5, pady=5)

            entry = ttk.Entry(control_frame, textvariable=var, width=10)
            entry.grid(row=i, column=2, padx=5, pady=5)
            entry.bind('<Return>', lambda e: self.update_series_motor_speed())

        # ODE Solver selection
        ttk.Label(control_frame, text="ODE Solver:").grid(row=len(params), column=0, sticky='w', pady=5)
        self.series_solver = tk.StringVar(value="RK45")
        solver_combo = ttk.Combobox(control_frame, textvariable=self.series_solver,
                                    values=["RK45", "Euler"], state='readonly', width=18)
        solver_combo.grid(row=len(params), column=1, columnspan=2, sticky='w', padx=5, pady=5)
        solver_combo.bind('<<ComboboxSelected>>', lambda e: self.update_series_motor_speed())

        # Calculate button
        calc_btn = ttk.Button(control_frame, text="Calculate & Simulate",
                            command=self.update_series_motor_speed)
        calc_btn.grid(row=len(params)+1, column=0, columnspan=3, pady=10)

        # Results display
        results_frame = ttk.LabelFrame(control_frame, text="Results", padding=10)
        results_frame.grid(row=len(params)+2, column=0, columnspan=3, sticky='ew', pady=5)

        self.series_results = tk.Text(results_frame, height=12, width=35, font=('Courier', 9))
        self.series_results.pack()

        # Right panel for graphs
        graph_frame = ttk.Frame(tab2)
        graph_frame.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=5, pady=5)
        graph_frame.rowconfigure(0, weight=1)
        graph_frame.columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.fig2 = Figure(figsize=(10, 8))
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=graph_frame)
        self.canvas2.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Initial calculation
        self.update_series_motor_speed()

    def series_motor_dynamics(self, t, y, V, Ra, Rf, Vb, I_target, J, B):
        """ODE system for series motor dynamics"""
        omega = y[0]  # Angular velocity
        Ia = y[1]     # Armature current

        # For series motor, field current = armature current
        If = Ia

        # Flux proportional to current (assuming linear magnetic circuit)
        phi = 0.01 * If  # Flux constant

        # Back EMF
        Eb = phi * omega

        # Armature current derivative
        La = 0.2  # Armature inductance (assumed)
        Lf = 0.1  # Field inductance (assumed)
        L_total = La + Lf

        # Applied voltage equation
        dIa_dt = (V - Eb - Ia * (Ra + Rf) - Vb) / L_total

        # Torque (proportional to flux and current)
        T = phi * Ia

        # Angular acceleration
        domega_dt = (T - B * omega) / J

        return [domega_dt, dIa_dt]

    def update_series_motor_speed(self, *args):
        """Calculate and update series motor speed results"""
        try:
            # Get parameters
            V = self.series_params['voltage'].get()
            Ra = self.series_params['ra'].get()
            Rf = self.series_params['rf'].get()
            Vb = self.series_params['vb'].get()
            I1 = self.series_params['i1'].get()
            N1 = self.series_params['n1'].get()
            I2 = self.series_params['i2'].get()
            sim_time = self.series_params['sim_time'].get()

            # For series motor: N ∝ (V - Ia*Ra - If*Rf - Vb) / φ
            # and φ ∝ I (in unsaturated region)
            # Therefore: N ∝ (V - I*(Ra+Rf) - Vb) / I

            # At condition 1
            Eb1 = V - I1 * (Ra + Rf) - Vb

            # At condition 2
            Eb2 = V - I2 * (Ra + Rf) - Vb

            # Speed relationship for series motor
            # N2/N1 = (Eb2/Eb1) * (I1/I2)
            N2 = N1 * (Eb2 / Eb1) * (I1 / I2)

            # Calculate torques
            # T ∝ φ * I ∝ I^2 (for series motor)
            T1 = (Eb1 * I1) / (2 * np.pi * N1 / 60)
            T2 = (Eb2 * I2) / (2 * np.pi * N2 / 60)

            # Power calculations
            P_out1 = Eb1 * I1 / 1000  # kW
            P_out2 = Eb2 * I2 / 1000  # kW

            # Display results
            results_text = f"""
SERIES MOTOR SPEED ANALYSIS
{'='*32}

Input Parameters:
  Voltage: {V} V
  Ra + Rf: {Ra + Rf} Ω
  Brush Drop: {Vb} V

Condition 1:
  Current: {I1} A
  Speed: {N1} rpm
  Back EMF: {Eb1:.2f} V
  Torque: {T1:.2f} N.m
  Power: {P_out1:.2f} kW

Condition 2:
  Current: {I2} A
  Calculated Speed: {N2:.2f} rpm
  Back EMF: {Eb2:.2f} V
  Torque: {T2:.2f} N.m
  Power: {P_out2:.2f} kW

Speed Ratio: {N2/N1:.3f}
Torque Ratio: {T2/T1:.3f}
"""

            self.series_results.delete(1.0, tk.END)
            self.series_results.insert(1.0, results_text)

            # Dynamic simulation for both operating points
            J = 0.08  # Moment of inertia
            B = 0.02  # Friction coefficient

            # Simulate transition from condition 1 to condition 2
            t_eval = np.linspace(0, sim_time, 500)

            # Initial conditions at steady state 1
            omega1 = 2 * np.pi * N1 / 60
            y0 = [omega1, I1]

            # Intermediate time arrays
            t_half = sim_time / 2
            t_eval1 = np.linspace(0, t_half, 250)
            t_eval2 = np.linspace(t_half, sim_time, 250)

            # Solve for condition 1
            if self.series_solver.get() == "RK45":
                sol1 = solve_ivp(
                    lambda t, y: self.series_motor_dynamics(t, y, V, Ra, Rf, Vb, I1, J, B),
                    [0, t_half], y0, t_eval=t_eval1, method='RK45'
                )
                omega_sim1 = sol1.y[0]
                Ia_sim1 = sol1.y[1]

                # Solve for condition 2 (starting from end of condition 1)
                y0_2 = [sol1.y[0][-1], I2]
                sol2 = solve_ivp(
                    lambda t, y: self.series_motor_dynamics(t, y, V, Ra, Rf, Vb, I2, J, B),
                    [t_half, sim_time], y0_2, t_eval=t_eval2, method='RK45'
                )
                omega_sim2 = sol2.y[0]
                Ia_sim2 = sol2.y[1]
            else:  # Euler
                t1, y1 = self.euler_method(
                    lambda t, y: self.series_motor_dynamics(t, y, V, Ra, Rf, Vb, I1, J, B),
                    [0, t_half], y0, t_eval1
                )
                omega_sim1 = y1[0]
                Ia_sim1 = y1[1]

                y0_2 = [omega_sim1[-1], I2]
                t2, y2 = self.euler_method(
                    lambda t, y: self.series_motor_dynamics(t, y, V, Ra, Rf, Vb, I2, J, B),
                    [t_half, sim_time], y0_2, t_eval2
                )
                omega_sim2 = y2[0]
                Ia_sim2 = y2[1]

            # Combine results
            t_combined = np.concatenate([t_eval1, t_eval2])
            omega_combined = np.concatenate([omega_sim1, omega_sim2])
            Ia_combined = np.concatenate([Ia_sim1, Ia_sim2])

            # Convert to rpm and calculate other quantities
            speed_combined = omega_combined * 60 / (2 * np.pi)
            phi_combined = 0.01 * Ia_combined
            torque_combined = phi_combined * Ia_combined
            power_combined = torque_combined * omega_combined / 1000  # kW

            # Plot results
            self.fig2.clear()

            ax1 = self.fig2.add_subplot(2, 2, 1)
            ax1.plot(t_combined, speed_combined, 'b-', linewidth=2)
            ax1.axhline(y=N1, color='g', linestyle='--', alpha=0.7, label=f'N1: {N1:.1f} rpm')
            ax1.axhline(y=N2, color='r', linestyle='--', alpha=0.7, label=f'N2: {N2:.1f} rpm')
            ax1.axvline(x=t_half, color='k', linestyle=':', alpha=0.5, label='Load Change')
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Speed (rpm)')
            ax1.set_title('Speed vs Time (Load Change)')
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            ax2 = self.fig2.add_subplot(2, 2, 2)
            ax2.plot(t_combined, Ia_combined, 'g-', linewidth=2)
            ax2.axhline(y=I1, color='g', linestyle='--', alpha=0.7, label=f'I1: {I1:.1f} A')
            ax2.axhline(y=I2, color='r', linestyle='--', alpha=0.7, label=f'I2: {I2:.1f} A')
            ax2.axvline(x=t_half, color='k', linestyle=':', alpha=0.5, label='Load Change')
            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Armature Current (A)')
            ax2.set_title('Current vs Time')
            ax2.grid(True, alpha=0.3)
            ax2.legend()

            ax3 = self.fig2.add_subplot(2, 2, 3)
            ax3.plot(t_combined, torque_combined, 'm-', linewidth=2)
            ax3.axhline(y=T1, color='g', linestyle='--', alpha=0.7, label=f'T1: {T1:.1f} N.m')
            ax3.axhline(y=T2, color='r', linestyle='--', alpha=0.7, label=f'T2: {T2:.1f} N.m')
            ax3.axvline(x=t_half, color='k', linestyle=':', alpha=0.5, label='Load Change')
            ax3.set_xlabel('Time (s)')
            ax3.set_ylabel('Torque (N.m)')
            ax3.set_title('Torque vs Time')
            ax3.grid(True, alpha=0.3)
            ax3.legend()

            ax4 = self.fig2.add_subplot(2, 2, 4)
            # Speed-Current characteristic
            current_range = np.linspace(20, 150, 100)
            Eb_range = V - current_range * (Ra + Rf) - Vb
            speed_range = N1 * (Eb_range / Eb1) * (I1 / current_range)
            ax4.plot(current_range, speed_range, 'c-', linewidth=2, label='Characteristic')
            ax4.plot(I1, N1, 'go', markersize=10, label=f'Point 1: ({I1}A, {N1}rpm)')
            ax4.plot(I2, N2, 'ro', markersize=10, label=f'Point 2: ({I2}A, {N2:.1f}rpm)')
            ax4.set_xlabel('Current (A)')
            ax4.set_ylabel('Speed (rpm)')
            ax4.set_title('Speed-Current Characteristic')
            ax4.grid(True, alpha=0.3)
            ax4.legend()

            self.fig2.tight_layout()
            self.canvas2.draw()

        except Exception as e:
            self.series_results.delete(1.0, tk.END)
            self.series_results.insert(1.0, f"Error in calculation:\n{str(e)}")

    def create_series_motor_torque_tab(self):
        """Problem 3: Series Motor Torque-Speed Relationship"""
        tab3 = ttk.Frame(self.notebook)
        self.notebook.add(tab3, text="Problem 3: Series Motor Torque")

        # Configure grid
        tab3.rowconfigure(1, weight=1)
        tab3.columnconfigure(1, weight=1)

        # Left panel for controls
        control_frame = ttk.LabelFrame(tab3, text="Motor Parameters", padding=10)
        control_frame.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=5, pady=5)

        # Parameters with sliders
        self.torque_params = {}

        params = [
            ("Voltage (V)", "voltage", 220, 100, 400),
            ("Initial Speed (rpm)", "n1", 800, 200, 2000),
            ("Initial Current (A)", "i1", 100, 20, 200),
            ("Torque Ratio (T2/T1)", "torque_ratio", 0.5, 0.1, 1.0),
            ("Total Resistance (Ω)", "r_total", 0.2, 0.05, 1.0),
            ("Simulation Time (s)", "sim_time", 10, 1, 30),
        ]

        for i, (label, key, default, min_val, max_val) in enumerate(params):
            ttk.Label(control_frame, text=label).grid(row=i, column=0, sticky='w', pady=5)

            var = tk.DoubleVar(value=default)
            self.torque_params[key] = var

            slider = ttk.Scale(control_frame, from_=min_val, to=max_val,
                             variable=var, orient='horizontal', length=200,
                             command=lambda v: self.update_series_motor_torque())
            slider.grid(row=i, column=1, padx=5, pady=5)

            entry = ttk.Entry(control_frame, textvariable=var, width=10)
            entry.grid(row=i, column=2, padx=5, pady=5)
            entry.bind('<Return>', lambda e: self.update_series_motor_torque())

        # ODE Solver selection
        ttk.Label(control_frame, text="ODE Solver:").grid(row=len(params), column=0, sticky='w', pady=5)
        self.torque_solver = tk.StringVar(value="RK45")
        solver_combo = ttk.Combobox(control_frame, textvariable=self.torque_solver,
                                    values=["RK45", "Euler"], state='readonly', width=18)
        solver_combo.grid(row=len(params), column=1, columnspan=2, sticky='w', padx=5, pady=5)
        solver_combo.bind('<<ComboboxSelected>>', lambda e: self.update_series_motor_torque())

        # Calculate button
        calc_btn = ttk.Button(control_frame, text="Calculate & Simulate",
                            command=self.update_series_motor_torque)
        calc_btn.grid(row=len(params)+1, column=0, columnspan=3, pady=10)

        # Results display
        results_frame = ttk.LabelFrame(control_frame, text="Results", padding=10)
        results_frame.grid(row=len(params)+2, column=0, columnspan=3, sticky='ew', pady=5)

        self.torque_results = tk.Text(results_frame, height=12, width=35, font=('Courier', 9))
        self.torque_results.pack()

        # Right panel for graphs
        graph_frame = ttk.Frame(tab3)
        graph_frame.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=5, pady=5)
        graph_frame.rowconfigure(0, weight=1)
        graph_frame.columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.fig3 = Figure(figsize=(10, 8))
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=graph_frame)
        self.canvas3.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Initial calculation
        self.update_series_motor_torque()

    def update_series_motor_torque(self, *args):
        """Calculate and update series motor torque-speed results"""
        try:
            # Get parameters
            V = self.torque_params['voltage'].get()
            N1 = self.torque_params['n1'].get()
            I1 = self.torque_params['i1'].get()
            torque_ratio = self.torque_params['torque_ratio'].get()
            R_total = self.torque_params['r_total'].get()
            sim_time = self.torque_params['sim_time'].get()

            # For series motor: T ∝ φ * I ∝ I^2
            # T2/T1 = (I2/I1)^2
            # I2 = I1 * sqrt(T2/T1)
            I2 = I1 * np.sqrt(torque_ratio)

            # Back EMF at condition 1
            Eb1 = V - I1 * R_total

            # Back EMF at condition 2
            Eb2 = V - I2 * R_total

            # Speed relationship: N ∝ Eb / φ ∝ Eb / I
            # N2/N1 = (Eb2/Eb1) * (I1/I2)
            N2 = N1 * (Eb2 / Eb1) * (I1 / I2)

            # Calculate torques (proportional to I^2)
            omega1 = 2 * np.pi * N1 / 60
            omega2 = 2 * np.pi * N2 / 60

            T1 = (Eb1 * I1) / omega1
            T2 = T1 * torque_ratio

            # Power calculations
            P1 = Eb1 * I1 / 1000  # kW
            P2 = Eb2 * I2 / 1000  # kW

            # Display results
            results_text = f"""
SERIES MOTOR TORQUE ANALYSIS
{'='*32}

Input Parameters:
  Voltage: {V} V
  Total Resistance: {R_total} Ω
  Torque Ratio: {torque_ratio}

Initial Condition:
  Speed: {N1} rpm
  Current: {I1} A
  Back EMF: {Eb1:.2f} V
  Torque: {T1:.2f} N.m
  Power: {P1:.2f} kW

At Half Torque:
  Speed: {N2:.2f} rpm
  Current: {I2:.2f} A
  Back EMF: {Eb2:.2f} V
  Torque: {T2:.2f} N.m
  Power: {P2:.2f} kW

Speed Increase: {((N2-N1)/N1)*100:.2f}%
Current Reduction: {((I1-I2)/I1)*100:.2f}%
"""

            self.torque_results.delete(1.0, tk.END)
            self.torque_results.insert(1.0, results_text)

            # Dynamic simulation
            J = 0.1  # Moment of inertia
            B = 0.015  # Friction coefficient

            # Create time array
            t_eval = np.linspace(0, sim_time, 500)
            t_half = sim_time / 2
            t_eval1 = np.linspace(0, t_half, 250)
            t_eval2 = np.linspace(t_half, sim_time, 250)

            # Initial conditions at steady state 1
            y0 = [omega1, I1]

            # Solve for condition 1
            if self.torque_solver.get() == "RK45":
                sol1 = solve_ivp(
                    lambda t, y: self.series_motor_dynamics(t, y, V, R_total*0.6, R_total*0.4, 0, I1, J, B),
                    [0, t_half], y0, t_eval=t_eval1, method='RK45'
                )
                omega_sim1 = sol1.y[0]
                Ia_sim1 = sol1.y[1]

                # Reduce torque at t_half (simulate load reduction)
                y0_2 = [sol1.y[0][-1], I2]
                sol2 = solve_ivp(
                    lambda t, y: self.series_motor_dynamics(t, y, V, R_total*0.6, R_total*0.4, 0, I2, J, B),
                    [t_half, sim_time], y0_2, t_eval=t_eval2, method='RK45'
                )
                omega_sim2 = sol2.y[0]
                Ia_sim2 = sol2.y[1]
            else:  # Euler
                t1, y1 = self.euler_method(
                    lambda t, y: self.series_motor_dynamics(t, y, V, R_total*0.6, R_total*0.4, 0, I1, J, B),
                    [0, t_half], y0, t_eval1
                )
                omega_sim1 = y1[0]
                Ia_sim1 = y1[1]

                y0_2 = [omega_sim1[-1], I2]
                t2, y2 = self.euler_method(
                    lambda t, y: self.series_motor_dynamics(t, y, V, R_total*0.6, R_total*0.4, 0, I2, J, B),
                    [t_half, sim_time], y0_2, t_eval2
                )
                omega_sim2 = y2[0]
                Ia_sim2 = y2[1]

            # Combine results
            t_combined = np.concatenate([t_eval1, t_eval2])
            omega_combined = np.concatenate([omega_sim1, omega_sim2])
            Ia_combined = np.concatenate([Ia_sim1, Ia_sim2])

            # Convert and calculate
            speed_combined = omega_combined * 60 / (2 * np.pi)
            phi_combined = 0.01 * Ia_combined
            torque_combined = phi_combined * Ia_combined
            power_combined = torque_combined * omega_combined / 1000  # kW

            # Plot results
            self.fig3.clear()

            ax1 = self.fig3.add_subplot(2, 2, 1)
            ax1.plot(t_combined, speed_combined, 'b-', linewidth=2)
            ax1.axhline(y=N1, color='g', linestyle='--', alpha=0.7, label=f'N1: {N1:.1f} rpm')
            ax1.axhline(y=N2, color='r', linestyle='--', alpha=0.7, label=f'N2: {N2:.1f} rpm')
            ax1.axvline(x=t_half, color='k', linestyle=':', alpha=0.5, label='Torque Reduction')
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Speed (rpm)')
            ax1.set_title('Speed Response to Torque Reduction')
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            ax2 = self.fig3.add_subplot(2, 2, 2)
            ax2.plot(t_combined, Ia_combined, 'g-', linewidth=2)
            ax2.axhline(y=I1, color='g', linestyle='--', alpha=0.7, label=f'I1: {I1:.1f} A')
            ax2.axhline(y=I2, color='r', linestyle='--', alpha=0.7, label=f'I2: {I2:.1f} A')
            ax2.axvline(x=t_half, color='k', linestyle=':', alpha=0.5, label='Torque Reduction')
            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Current (A)')
            ax2.set_title('Current vs Time')
            ax2.grid(True, alpha=0.3)
            ax2.legend()

            ax3 = self.fig3.add_subplot(2, 2, 3)
            ax3.plot(t_combined, torque_combined, 'm-', linewidth=2)
            ax3.axhline(y=T1, color='g', linestyle='--', alpha=0.7, label=f'T1: {T1:.1f} N.m')
            ax3.axhline(y=T2, color='r', linestyle='--', alpha=0.7, label=f'T2: {T2:.1f} N.m')
            ax3.axvline(x=t_half, color='k', linestyle=':', alpha=0.5, label='Torque Reduction')
            ax3.set_xlabel('Time (s)')
            ax3.set_ylabel('Torque (N.m)')
            ax3.set_title('Torque vs Time')
            ax3.grid(True, alpha=0.3)
            ax3.legend()

            ax4 = self.fig3.add_subplot(2, 2, 4)
            # Torque-Speed characteristic
            current_range = np.linspace(20, 150, 100)
            Eb_range = V - current_range * R_total
            speed_range = N1 * (Eb_range / Eb1) * (I1 / current_range)
            torque_range = (current_range / I1)**2 * T1
            ax4.plot(speed_range, torque_range, 'c-', linewidth=2, label='Characteristic')
            ax4.plot(N1, T1, 'go', markersize=10, label=f'Point 1: ({N1}rpm, {T1:.1f}N.m)')
            ax4.plot(N2, T2, 'ro', markersize=10, label=f'Point 2: ({N2:.1f}rpm, {T2:.1f}N.m)')
            ax4.set_xlabel('Speed (rpm)')
            ax4.set_ylabel('Torque (N.m)')
            ax4.set_title('Torque-Speed Characteristic')
            ax4.grid(True, alpha=0.3)
            ax4.legend()

            self.fig3.tight_layout()
            self.canvas3.draw()

        except Exception as e:
            self.torque_results.delete(1.0, tk.END)
            self.torque_results.insert(1.0, f"Error in calculation:\n{str(e)}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = DCMotorSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
