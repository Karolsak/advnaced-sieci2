"""
Advanced DC Series Motor Simulator - Web Application
Flask backend with REST API for motor simulation

Features:
- Example 29.32 solver
- Real-time motor simulation
- Multi-physics modeling
- Economic analysis
- RESTful API endpoints
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
import json
import uuid
from datetime import datetime
import threading
import time

app = Flask(__name__)
app.secret_key = 'dc-motor-simulator-secret-key-2024'
CORS(app)

# Store active simulations
simulations = {}

class MotorSimulation:
    """Motor simulation engine"""

    def __init__(self, sim_id):
        self.sim_id = sim_id
        self.is_running = False
        self.current_time = 0
        self.dt = 0.01  # Time step

        # Motor parameters
        self.params = {
            'V_supply': 460.0,
            'R_armature': 0.5,
            'L_armature': 0.05,
            'J_inertia': 0.5,
            'B_friction': 0.01,
            'k_torque': 0.05,
            'k_emf': 0.05,
            'T_load': 100.0,
            'efficiency': 0.85,
            'power_cost': 0.12,
            'ambient_temp': 25.0,
            'thermal_resistance': 2.0,
            'thermal_capacitance': 1000.0,
            'max_temp': 155.0,
        }

        # Control parameters
        self.control_params = {
            'method': 'Open Loop',
            'kp': 1.0,
            'ki': 0.5,
            'setpoint': 1500.0,
            'duty_cycle': 0.8,
            'pwm_freq': 1000.0,
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

        # History
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

        self.solver_type = 'RK45'
        self.max_history = 500

    def update_params(self, params):
        """Update motor parameters"""
        self.params.update(params)

    def update_control_params(self, params):
        """Update control parameters"""
        self.control_params.update(params)

    def reset(self):
        """Reset simulation"""
        self.is_running = False
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

    def motor_dynamics(self, t, y):
        """Motor differential equations"""
        Ia = y[0]
        omega = y[1]
        T_motor = y[2]

        V = self.params['V_supply']
        Ra = self.params['R_armature']
        La = self.params['L_armature']
        J = self.params['J_inertia']
        B = self.params['B_friction']
        T_load = self.params['T_load']

        # Apply control
        V_applied = self.apply_control(V, Ia, omega)

        # Electrical equation
        k_e_eff = self.params['k_emf'] * (1 + 0.01 * Ia)
        Eb = k_e_eff * Ia * omega

        # Temperature effect on resistance
        temp_coefficient = 0.004
        Ra_temp = Ra * (1 + temp_coefficient * (T_motor - 25))

        dIa_dt = (V_applied - Eb - Ia * Ra_temp) / La

        # Mechanical equation
        k_t_eff = self.params['k_torque'] * (1 + 0.01 * Ia)
        T_electromag = k_t_eff * Ia * Ia

        domega_dt = (T_electromag - T_load - B * omega) / J

        # Thermal equation
        P_copper = Ia**2 * Ra_temp
        P_iron = 0.01 * omega**2
        P_mech = B * omega**2
        P_stray = 0.005 * V_applied * Ia

        P_total_loss = P_copper + P_iron + P_mech + P_stray

        C_th = self.params['thermal_capacitance']
        R_th = self.params['thermal_resistance']
        T_amb = self.params['ambient_temp']

        dT_dt = (P_total_loss - (T_motor - T_amb) / R_th) / C_th

        return [dIa_dt, domega_dt, dT_dt]

    def apply_control(self, V_nominal, Ia, omega):
        """Apply control strategy"""
        method = self.control_params['method']

        if method == 'PI Speed Control':
            speed_rpm = omega * 60 / (2 * np.pi)
            setpoint = self.control_params['setpoint']
            error = setpoint - speed_rpm

            Kp = self.control_params['kp']
            Ki = self.control_params['ki']

            V_control = V_nominal + Kp * error
            return np.clip(V_control, 0, V_nominal * 1.5)

        elif method == 'Field Weakening':
            if omega > 100:
                field_reduction = 100 / omega
                return V_nominal * np.clip(field_reduction, 0.5, 1.0)
            return V_nominal

        elif method in ['Chopper Control', 'PWM Control']:
            duty = self.control_params['duty_cycle']
            return V_nominal * duty

        return V_nominal

    def step(self):
        """Perform one simulation step"""
        t_start = self.current_time
        t_end = self.current_time + self.dt

        y0 = [
            self.state['current'],
            self.state['speed'],
            self.state['temperature']
        ]

        if self.solver_type == 'RK45':
            sol = solve_ivp(
                self.motor_dynamics,
                [t_start, t_end],
                y0,
                method='RK45',
                dense_output=True
            )
            y_new = sol.y[:, -1]
        else:  # Euler
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
        self.history['speed'].append(self.state['speed'] * 60 / (2 * np.pi))  # Convert to RPM
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

        # Limit history
        if len(self.history['time']) > self.max_history:
            for key in self.history:
                self.history[key] = self.history[key][-self.max_history:]

    def calculate_motor_quantities(self):
        """Calculate motor performance quantities"""
        Ia = self.state['current']
        omega = self.state['speed']
        T_motor_temp = self.state['temperature']

        V = self.params['V_supply']
        Ra = self.params['R_armature']
        B = self.params['B_friction']

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

    def get_state(self):
        """Get current state and recent history"""
        return {
            'state': self.state,
            'history': {
                'time': self.history['time'][-100:],
                'current': self.history['current'][-100:],
                'speed': self.history['speed'][-100:],
                'torque': self.history['torque'][-100:],
                'temperature': self.history['temperature'][-100:],
                'power_in': self.history['power_in'][-100:],
                'power_out': self.history['power_out'][-100:],
                'efficiency': self.history['efficiency'][-100:],
            },
            'time': self.current_time,
            'is_running': self.is_running
        }

# Routes

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/create_simulation', methods=['POST'])
def create_simulation():
    """Create new simulation instance"""
    sim_id = str(uuid.uuid4())
    simulations[sim_id] = MotorSimulation(sim_id)
    return jsonify({'sim_id': sim_id})

@app.route('/api/update_params', methods=['POST'])
def update_params():
    """Update motor parameters"""
    data = request.json
    sim_id = data.get('sim_id')
    params = data.get('params', {})

    if sim_id not in simulations:
        return jsonify({'error': 'Simulation not found'}), 404

    simulations[sim_id].update_params(params)
    return jsonify({'status': 'success'})

@app.route('/api/update_control', methods=['POST'])
def update_control():
    """Update control parameters"""
    data = request.json
    sim_id = data.get('sim_id')
    params = data.get('params', {})

    if sim_id not in simulations:
        return jsonify({'error': 'Simulation not found'}), 404

    simulations[sim_id].update_control_params(params)
    return jsonify({'status': 'success'})

@app.route('/api/start', methods=['POST'])
def start_simulation():
    """Start simulation"""
    data = request.json
    sim_id = data.get('sim_id')

    if sim_id not in simulations:
        return jsonify({'error': 'Simulation not found'}), 404

    simulations[sim_id].is_running = True
    return jsonify({'status': 'started'})

@app.route('/api/stop', methods=['POST'])
def stop_simulation():
    """Stop simulation"""
    data = request.json
    sim_id = data.get('sim_id')

    if sim_id not in simulations:
        return jsonify({'error': 'Simulation not found'}), 404

    simulations[sim_id].is_running = False
    return jsonify({'status': 'stopped'})

@app.route('/api/reset', methods=['POST'])
def reset_simulation():
    """Reset simulation"""
    data = request.json
    sim_id = data.get('sim_id')

    if sim_id not in simulations:
        return jsonify({'error': 'Simulation not found'}), 404

    simulations[sim_id].reset()
    return jsonify({'status': 'reset'})

@app.route('/api/step', methods=['POST'])
def step_simulation():
    """Perform simulation step"""
    data = request.json
    sim_id = data.get('sim_id')

    if sim_id not in simulations:
        return jsonify({'error': 'Simulation not found'}), 404

    sim = simulations[sim_id]
    if sim.is_running:
        sim.step()

    return jsonify(sim.get_state())

@app.route('/api/solve_example', methods=['POST'])
def solve_example():
    """Solve Example 29.32"""
    try:
        # Given data
        I = np.array([20, 30, 40, 50])
        T = np.array([128.8, 230.5, 349.8, 446.2])
        V = 460.0
        Ra = 0.5

        # Logarithmic fit
        log_I = np.log(I)
        log_T = np.log(T)
        coeffs = np.polyfit(log_I, log_T, 1)
        n = coeffs[0]
        log_k = coeffs[1]
        k_torque = np.exp(log_k)

        # Calculate back-EMF
        Eb = V - I * Ra

        # Calculate speeds
        N_base = Eb / I
        k_speed = 1000.0 / N_base[0]
        N_rpm = N_base * k_speed

        # Extended range
        I_extended = np.linspace(10, 60, 100)
        T_extended = k_torque * I_extended**n
        Eb_extended = V - I_extended * Ra
        N_base_extended = Eb_extended / I_extended
        N_extended = N_base_extended * k_speed

        # Results
        results = {
            'test_data': {
                'current': I.tolist(),
                'torque': T.tolist(),
                'speed': N_rpm.tolist(),
                'back_emf': Eb.tolist(),
            },
            'extended_data': {
                'current': I_extended.tolist(),
                'torque': T_extended.tolist(),
                'speed': N_extended.tolist(),
            },
            'coefficients': {
                'k_torque': float(k_torque),
                'n': float(n),
            },
            'analysis': {
                'max_torque': float(T_extended.max()),
                'min_speed': float(N_extended.min()),
                'max_speed': float(N_extended.max()),
            }
        }

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calculate_economics', methods=['POST'])
def calculate_economics():
    """Calculate economic analysis"""
    try:
        data = request.json
        sim_id = data.get('sim_id')
        power_cost = data.get('power_cost', 0.12)
        operating_hours = data.get('operating_hours', 8760)
        maintenance_cost = data.get('maintenance_cost', 500)

        if sim_id not in simulations:
            return jsonify({'error': 'Simulation not found'}), 404

        sim = simulations[sim_id]

        if len(sim.history['power_in']) == 0:
            return jsonify({'error': 'No simulation data available'}), 400

        # Calculate averages
        avg_power_in = np.mean(sim.history['power_in']) / 1000  # kW
        avg_power_out = np.mean(sim.history['power_out']) / 1000  # kW
        avg_efficiency = np.mean(sim.history['efficiency'])

        # Calculate costs
        annual_energy = avg_power_in * operating_hours
        annual_energy_cost = annual_energy * power_cost
        total_annual_cost = annual_energy_cost + maintenance_cost

        # Losses
        annual_energy_loss = (avg_power_in - avg_power_out) * operating_hours
        annual_loss_cost = annual_energy_loss * power_cost

        # 10-year projection
        total_10yr_cost = total_annual_cost * 10
        total_10yr_energy = annual_energy * 10

        # CO2
        co2_factor = 0.5
        annual_co2 = annual_energy * co2_factor

        # Loss breakdown
        avg_copper = np.mean(sim.history['copper_loss'][-100:]) if sim.history['copper_loss'] else 0
        avg_iron = np.mean(sim.history['iron_loss'][-100:]) if sim.history['iron_loss'] else 0
        avg_mech = np.mean(sim.history['mech_loss'][-100:]) if sim.history['mech_loss'] else 0
        avg_stray = np.mean(sim.history['stray_loss'][-100:]) if sim.history['stray_loss'] else 0

        total_loss = avg_copper + avg_iron + avg_mech + avg_stray

        if total_loss > 0:
            copper_pct = (avg_copper / total_loss) * 100
            iron_pct = (avg_iron / total_loss) * 100
            mech_pct = (avg_mech / total_loss) * 100
            stray_pct = (avg_stray / total_loss) * 100
        else:
            copper_pct = iron_pct = mech_pct = stray_pct = 0

        results = {
            'operating': {
                'avg_power_in': avg_power_in,
                'avg_power_out': avg_power_out,
                'avg_efficiency': avg_efficiency,
                'operating_hours': operating_hours,
            },
            'annual': {
                'energy': annual_energy,
                'energy_cost': annual_energy_cost,
                'maintenance_cost': maintenance_cost,
                'total_cost': total_annual_cost,
                'energy_loss': annual_energy_loss,
                'loss_cost': annual_loss_cost,
            },
            'projection': {
                'total_energy': total_10yr_energy,
                'total_cost': total_10yr_cost,
            },
            'environmental': {
                'annual_co2': annual_co2,
                'total_co2': annual_co2 * 10,
            },
            'loss_breakdown': {
                'copper': copper_pct,
                'iron': iron_pct,
                'mechanical': mech_pct,
                'stray': stray_pct,
            }
        }

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_losses', methods=['POST'])
def get_losses():
    """Get detailed loss data"""
    data = request.json
    sim_id = data.get('sim_id')

    if sim_id not in simulations:
        return jsonify({'error': 'Simulation not found'}), 404

    sim = simulations[sim_id]

    return jsonify({
        'time': sim.history['time'][-100:],
        'copper_loss': sim.history['copper_loss'][-100:],
        'iron_loss': sim.history['iron_loss'][-100:],
        'mech_loss': sim.history['mech_loss'][-100:],
        'stray_loss': sim.history['stray_loss'][-100:],
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
